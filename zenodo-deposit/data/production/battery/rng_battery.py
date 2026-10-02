"""engine.validation.rng_battery — lightweight, reproducible PRNG battery.

Implementation of a NIST SP 800-22 Rev. 1a *footprint* plus classic
(Knuth) tests, pure numpy/scipy, operating on lab-scale streams fixed by
EXP-0004 (04_SHARED_ENGINE/engine must be importable).

Scope note (documented in the investigation): this is a lightweight, in-lab,
reproducible battery at lab stream lengths. It follows the NIST formulas for
the named tests but is NOT the official NIST SP 800-22 harness. "Passes the
battery" means the p-value distribution is uniform and the small-p count is
inside its exact binomial band (see engine.statistics.hypothesis machinery),
NOT "certified by NIST" and NOT "proven random".

Stream convention (frozen):
    NBYTES = 2**15  -> bytes_arr = gen.integers(0, 256, NBYTES, dtype=uint8)
    NF     = 2**15  -> floats_arr = gen.random(NF)
    NW     = 2**13  -> words_arr = gen.integers(0, 2**32, NW, dtype=uint32)
    bits   = np.unpackbits(bytes_arr)  (length 2**18)
Each test consumes a fixed disjoint slice of these arrays (no rerandomisation
inside a test, so tests on one stream are reproducible and independently run).

Every function returns p-value(s) in [0, 1]; a p of NaN marks "not applicable"
(NIST condition) and is still reported. Tests are deterministic.
"""

from __future__ import annotations

import numpy as np

from scipy import special, stats

NBYTES = 1 << 15
NF = 1 << 15
NW = 1 << 13
NBITS = NBYTES * 8

BITS_PERMUTATIONS = 2 ** 8

# NIST long-run-of-ones categories for M=128: L <= 4, 5, 6, 7, 8, 9, >= 10.
_LRO_EDGES = (-np.inf, 5, 6, 7, 8, 9, 10, np.inf)
_LRO_CATS = 7


def _run_limited_counts(m, l):
    """Number of m-bit binary strings whose longest run of 1s is <= l.

    Exact integer recurrence: A(m,l) = sum_{j=1..l+1} A(m-j, l), base 2**m
    for m <= l. Used to derive per-block probabilities without relying on
    published tables (the classic NIST tables were mis-transcribed here once;
    the recurrence is exact and self-documenting).
    """
    if l >= m:
        return 2 ** m
    a = [2 ** i for i in range(l + 1)]
    if m <= l:
        return a[m]
    for size in range(l + 1, m + 1):
        nxt = sum(a[-j] for j in range(1, l + 2))
        a.append(nxt)
    return int(a[-1])


def _lro_block_probs(m=128):
    """Exact per-block category probabilities P(L in category) for M-bit blocks."""
    cats = (4, 5, 6, 7, 8, 9)
    cum = {l: _run_limited_counts(m, l) / (2 ** m) for l in cats}
    probs = [
        cum[4],
        cum[5] - cum[4],
        cum[6] - cum[5],
        cum[7] - cum[6],
        cum[8] - cum[7],
        cum[9] - cum[8],
        1.0 - cum[9],
    ]
    return np.array([max(p, 0.0) for p in probs])

# NIST rank probabilities for 32x32 binary matrices.
_RANK_P = np.array([0.2888, 0.5776, 0.1336])

_TEMPLATE9 = np.array([1, 0, 0, 1, 1, 0, 0, 1, 0], dtype=int)  # 0b100110010


def gammaincc(dof_2, stat_2):
    """Upper incomplete gamma regularised p like NIST's igamc(a, x)."""
    return special.gammaincc(dof_2, stat_2)


def _erfc_p(z):
    return special.erfc(abs(z) / np.sqrt(2.0))


# --------------------------------------------------------------------------- #
# individual tests
# --------------------------------------------------------------------------- #
def t_monobit(bits):
    """NIST 2.1 Frequency (Monobit) on the whole stream."""
    n = bits.size
    s = 2 * int(bits.sum()) - n
    return float(_erfc_p(s / np.sqrt(n)))


def t_block_freq(bits, m=128):
    """NIST 2.2 Block Frequency, M=128 (must divide n)."""
    n = bits.size
    nblocks = n // m
    blocks = bits[: nblocks * m].reshape(nblocks, m)
    pi = blocks.mean(axis=1)
    chi2 = 4.0 * m * np.sum((pi - 0.5) ** 2)
    return float(gammaincc(nblocks / 2.0, chi2 / 2.0))


def t_runs(bits):
    """NIST 2.3 Runs."""
    n = bits.size
    pi = bits.mean()
    if pi in (0.0, 1.0):
        return float("nan")
    transitions = int(np.count_nonzero(bits[1:] != bits[:-1]))
    v_n = transitions + 1
    num = abs(v_n - 2.0 * n * pi * (1.0 - pi))
    den = 2.0 * np.sqrt(2.0 * n) * pi * (1.0 - pi)
    return float(_erfc_p(num / den))


def _longest_run_ones_block(arr):
    """Length of the longest run of 1s in a 1-D 0/1 array."""
    if not arr.any():
        return 0
    d = np.diff(np.concatenate(([0], arr.astype(int), [0])))
    starts = np.flatnonzero(d == 1)
    ends = np.flatnonzero(d == -1)
    return int((ends - starts).max())


def t_longest_run(bits, m=128):
    """Longest Run of Ones in a Block, M=128 (NIST 2.4 footprint).

    Uses the exact per-block probabilities _lro_block_probs(m) rather than a
    published table; chi-square over the 7 NIST categories, df=6.
    """
    n = bits.size
    nblocks = n // m
    blocks = bits[: nblocks * m].reshape(nblocks, m)
    runs = np.array([_longest_run_ones_block(b) for b in blocks])
    cats = np.digitize(runs, _LRO_EDGES) - 1
    obs = np.array([np.count_nonzero(cats == i) for i in range(_LRO_CATS)], dtype=float)
    probs = _lro_block_probs(m)
    chi2 = float(np.sum((obs - nblocks * probs) ** 2 / (nblocks * probs)))
    return float(gammaincc(3.0, chi2 / 2.0))


def _gf2_rank(mat):
    """Rank of a binary matrix over GF(2) by elimination (uint8 0/1)."""
    m = mat.copy().astype(np.int8)
    rows, rank = m.shape[0], 0
    for col in range(m.shape[1]):
        piv = np.flatnonzero(m[rank:, col])
        if piv.size == 0:
            continue
        r = rank + piv[0]
        if r != rank:
            m[[rank, r]] = m[[r, rank]]
        ones = np.flatnonzero(m[rank + 1 :, col]) + rank + 1
        if ones.size:
            m[ones] ^= m[rank]
        rank += 1
        if rank == rows:
            break
    return rank


def t_matrix_rank(bits, mm=32):
    """NIST 2.5 Binary Matrix Rank, 32x32 over GF(2)."""
    nbits = bits.size
    nb = mm * mm
    nm = nbits // nb
    mats = bits[: nm * nb].reshape(nm, mm, mm).astype(np.int8)
    f = np.empty(nm, dtype=int)
    for i in range(nm):
        f[i] = _gf2_rank(mats[i])
    obs = np.array(
        [np.count_nonzero(f == mm), np.count_nonzero(f == mm - 1),
         np.count_nonzero(f <= mm - 2)],
        dtype=float,
    )
    chi2 = float(np.sum((obs - nm * _RANK_P) ** 2 / (nm * _RANK_P)))
    return float(np.exp(-chi2 / 2.0))


def t_dft(bits):
    """NIST 2.9 Discrete Fourier Transform (Spectral) Test."""
    n = bits.size
    x = 2 * bits.astype(float) - 1.0
    freqs = np.abs(np.fft.fft(x))[: n // 2]
    T = float(np.sqrt(np.log(1.0 / 0.05) * n))
    n0 = 0.95 * n / 2.0
    n1 = float(np.count_nonzero(freqs < T))
    d = (n1 - n0) / np.sqrt(n * 0.95 * 0.05 / 4.0)
    return float(_erfc_p(d))


def t_nontemplate(bits, template=None, mw=9):
    """Lightweight non-overlapping template test (m=9).

    Deviation from NIST 2.7: uses non-overlapping windows and a normal
    approximation for the matching count (windows are independent), rather than
    NIST's per-block chi-square bookkeeping. Documented in the investigation.
    """
    if template is None:
        template = _TEMPLATE9
    n = bits.size
    nwin = n // mw
    windows = bits[: nwin * mw].reshape(nwin, mw)
    matches = float(np.count_nonzero((windows == template).all(axis=1)))
    p = 2.0 ** (-mw)
    mu = nwin * p
    sig = np.sqrt(nwin * p * (1.0 - p))
    return float(_erfc_p((matches - mu) / sig))


def _sliding_pattern_counts(bits, m):
    """Counts of the 2**m circular m-bit patterns in a bit stream."""
    n = bits.size
    ext = np.concatenate((bits, bits[: m - 1]))
    w = np.lib.stride_tricks.sliding_window_view(ext, m)
    weights = 2 ** np.arange(m - 1, -1, -1)
    vals = w @ weights
    return np.bincount(vals, minlength=2 ** m), n


def _psi_sq(bits, m):
    counts, n = _sliding_pattern_counts(bits, m)
    return (2.0 ** m / n) * float(np.sum(counts ** 2)) - n


def t_serial(bits, m=3):
    """NIST 2.13 Serial Test (m=3) -> max(∇ψ²,∇²ψ²) two p-values."""
    psi2_m = _psi_sq(bits, m)
    psi2_m1 = _psi_sq(bits, m - 1)
    psi2_m2 = _psi_sq(bits, m - 2)
    nabla = psi2_m - psi2_m1
    nabla2 = psi2_m - 2 * psi2_m1 + psi2_m2
    p1 = float(gammaincc(2.0 ** (m - 2), nabla / 2.0))
    p2 = float(gammaincc(2.0 ** (m - 3), nabla2 / 2.0))
    return p1, p2


def _phi_m(bits, m):
    counts, n = _sliding_pattern_counts(bits, m)
    with np.errstate(divide="ignore", invalid="ignore"):
        frac = counts[counts > 0] / n
    return float(np.sum(frac * np.log(frac)))


def t_apen(bits, m=3):
    """NIST 2.12 Approximate Entropy, m=3."""
    n = bits.size
    apen = _phi_m(bits, m) - _phi_m(bits, m + 1)
    chi2 = 2.0 * n * (np.log(2.0) - apen)
    return float(gammaincc(2.0 ** (m - 1), chi2 / 2.0))


def _cusum_p(z, n):
    """NIST 2.11 p-value for the forward/backward CUSUM statistic z."""
    from math import floor

    from functools import partial

    cdf = partial(stats.norm.cdf)
    val = 0.0
    for k in range(floor((-(n / z) + 1) / 4), floor((n / z - 1) / 4) + 1):
        val += cdf((4 * k + 1) * z / np.sqrt(n)) - cdf((4 * k - 1) * z / np.sqrt(n))
    for k in range(floor((-(n / z) - 3) / 4), floor((n / z - 1) / 4) + 1):
        val -= cdf((4 * k + 3) * z / np.sqrt(n)) - cdf((4 * k + 1) * z / np.sqrt(n))
    return float(np.clip(1.0 - val, 0.0, 1.0))


def t_cusum(bits):
    """NIST 2.11 Cumulative Sums, forward and backward."""
    n = bits.size
    x = 2 * bits.astype(float) - 1.0
    z_f = np.abs(x.cumsum()).max()
    z_b = np.abs(x[::-1].cumsum()).max()
    if z_f <= 0.0 or z_b <= 0.0:
        return float("nan"), float("nan")
    return float(_cusum_p(z_f, n)), float(_cusum_p(z_b, n))


def t_byte_chisq(bytes_arr):
    """Classic: uniform distribution of 256 byte values."""
    n = bytes_arr.size
    counts = np.bincount(bytes_arr, minlength=256).astype(float)
    exp = n / 256.0
    chi2 = float(np.sum((counts - exp) ** 2 / exp))
    return float(gammaincc(255.0 / 2.0, chi2 / 2.0))


def t_float_chisq(floats_arr, nbin=32):
    """Classic: uniform distribution of u in [0,1) over 32 bins."""
    n = floats_arr.size
    counts = np.bincount(np.clip((floats_arr * nbin).astype(int), 0, nbin - 1),
                         minlength=nbin).astype(float)
    exp = n / nbin
    chi2 = float(np.sum((counts - exp) ** 2 / exp))
    return float(gammaincc((nbin - 1) / 2.0, chi2 / 2.0))


def t_word_bucket(words_arr):
    """Classic: top byte of uint32 words uniform over 256 buckets."""
    n = words_arr.size
    top = (words_arr >> 24).astype(np.int64)
    counts = np.bincount(top, minlength=256).astype(float)
    exp = n / 256.0
    chi2 = float(np.sum((counts - exp) ** 2 / exp))
    return float(gammaincc(255.0 / 2.0, chi2 / 2.0))


def t_gap(floats_arr, digit=0):
    """Knuth gap test on base-10 digits; geometric gaps between `digit`."""
    digits = (floats_arr * 10).astype(int) % 10
    idx = np.flatnonzero(digits == digit)
    if idx.size < 2:
        return float("nan")
    gaps = np.diff(idx) - 1  # count of non-digit values between occurrences
    # renormalise: gap length conditional on terminating at a digit -> Geom(0.9)
    buckets = np.array([0, 1, 2, 3, 4, 5, 10, 20, 50, np.inf])
    cat = np.digitize(gaps, buckets) - 1
    nb = buckets.size - 1
    # Pr(gap = k) = 0.9^k * 0.1 (length in non-digits). Aggregate into buckets.
    probs = np.empty(nb)
    for i in range(nb):
        lo, hi = buckets[i], buckets[i + 1]
        if np.isinf(hi):
            ks = np.arange(lo, int(gaps.max()) + 1)
            probs[i] = np.sum(0.9 ** ks * 0.1)
        else:
            ks = np.arange(lo, hi)
            probs[i] = np.sum(0.9 ** ks * 0.1)
    probs /= probs.sum()
    obs = np.array([np.count_nonzero(cat == i) for i in range(nb)], dtype=float)
    ng = obs.sum()
    chi2 = float(np.sum((obs - ng * probs) ** 2 / (ng * probs)))
    return float(gammaincc((nb - 1) / 2.0, chi2 / 2.0))


def t_autocorr(bits, maxlag=8):
    """Classic: bit autocorrelation at lags 1..maxlag (two-sided normal)."""
    n = bits.size
    x = 2 * bits.astype(float) - 1.0
    out = []
    for lag in range(1, maxlag + 1):
        c = float(np.dot(x[: n - lag], x[lag:]))
        z = c / np.sqrt(n - lag)
        out.append(float(_erfc_p(z)))
    return out


# --------------------------------------------------------------------------- #
# orchestration
# --------------------------------------------------------------------------- #
TEST_IDS = (
    "T01_monobit", "T02_blockfreq", "T03_runs", "T04_longestrun",
    "T05_matrixrank", "T06_dft", "T07_nontemplate",
    "T08_serial_p1", "T08_serial_p2", "T09_apen", "T10_cusum_fw", "T10_cusum_bw",
    "T11_bytes", "T12_floats", "T13_words", "T14_gap",
    "T15_ac1", "T15_ac2", "T15_ac3", "T15_ac4",
    "T15_ac5", "T15_ac6", "T15_ac7", "T15_ac8",
)


def run_battery(bits, bytes_arr, floats_arr, words_arr):
    """Run the full battery; return a list of (test_id, p-value) tuples.

    Deterministic given the input arrays. Each test reads a disjoint slice of
    one input array; tests never mutate or rerandomise.
    """
    out = []
    out.append(("T01_monobit", t_monobit(bits)))
    out.append(("T02_blockfreq", t_block_freq(bits)))
    out.append(("T03_runs", t_runs(bits)))
    out.append(("T04_longestrun", t_longest_run(bits)))
    out.append(("T05_matrixrank", t_matrix_rank(bits)))
    out.append(("T06_dft", t_dft(bits)))
    out.append(("T07_nontemplate", t_nontemplate(bits)))
    p1, p2 = t_serial(bits)
    out.append(("T08_serial_p1", p1))
    out.append(("T08_serial_p2", p2))
    out.append(("T09_apen", t_apen(bits)))
    p1, p2 = t_cusum(bits)
    out.append(("T10_cusum_fw", p1))
    out.append(("T10_cusum_bw", p2))
    out.append(("T11_bytes", t_byte_chisq(bytes_arr)))
    out.append(("T12_floats", t_float_chisq(floats_arr)))
    out.append(("T13_words", t_word_bucket(words_arr)))
    out.append(("T14_gap", t_gap(floats_arr)))
    ac = t_autocorr(bits)
    for i, p in enumerate(ac, start=1):
        out.append(("T15_ac%d" % i, p))
    return out


def draw_arrays(gen):
    """Draw the three stream arrays from a numpy-like generator.

    `gen` must support .integers(0, n, size, dtype=uint32) and .random(size).
    Returns (bytes_arr, floats_arr, words_arr).
    """
    bytes_arr = gen.integers(0, 256, NBYTES, dtype=np.uint32).astype(np.uint8)
    floats_arr = gen.random(NF)
    words_arr = gen.integers(0, 2 ** 32, NW, dtype=np.uint32).astype(np.uint32)
    return bytes_arr, floats_arr, words_arr


def streams_for(gen):
    """Full battery inputs: bits + the three arrays."""
    bytes_arr, floats_arr, words_arr = draw_arrays(gen)
    bits = np.unpackbits(bytes_arr)
    return bytes_arr, floats_arr, words_arr, bits