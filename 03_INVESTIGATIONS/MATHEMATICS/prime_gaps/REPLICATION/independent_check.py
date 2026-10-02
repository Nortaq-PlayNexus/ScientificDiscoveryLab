"""C7 — independent implementation for EXP-0008 (Q-M002).

This file is a SEPARATE implementation path from CODE/run_prime_gaps.py:
- Prime source: pure-Python segmented sieve (not the numpy bool-array sieve).
- Binning: equal-width bins over [0, 10] for its own GOF (different scheme
  than the primary's exponential-quantile bins).
- Statistics entry point: scipy.stats.chisquare + scipy.stats.kstest.

Per the frozen prereg, the independent implementation must (i) use a
different binning scheme and (ii) match the primary's chi2/KS vectors
within the recorded tolerance. Because the equal-width chi2 differs from
the exponential-quantile chi2 by construction, this checker reports TWO
things:
  1. `equal_width_gof` — its own independent chi2 GOF whose per-block
     BH-FDR verdict must match the primary's G1 verdict, and
  2. a same-binning vector (`vector_match`) — chi2/KS computed on the
     prereg exponential-quantile edges, which must match the primary's
     chi2/KS within 1e-9 (tabulated tolerance tol_c7_vector_match).

This resolves the documented prereg contradiction; see
state/EXP-0008_decisions.md. The frozen prereg file is NOT modified.
"""
from __future__ import annotations

import bisect
import json
import math
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np
from scipy import stats as sp_stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "04_SHARED_ENGINE"))
from engine.utilities.core import rng, version_info, machine_info

HERE = os.path.dirname(os.path.abspath(__file__))
INVESTIGATION = os.path.dirname(HERE)
PREREG = os.path.join(INVESTIGATION, "CONFIG", "prereg_EXP-0008.json")
REPORT_PATH = os.path.join(HERE, "C7_exp0008_report.json")
INDEPENDENT_RNG_LABEL = "exp0008/c7/independent"


def load_prereg(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def segmented_sieve(N):
    """Pure-Python segmented sieve -> sorted list of primes up to N."""
    limit = int(N ** 0.5) + 1
    base = [True] * (limit + 1)
    base[0:2] = [False, False]
    for i in range(2, int(limit ** 0.5) + 1):
        if base[i]:
            for j in range(i * i, limit + 1, i):
                base[j] = False
    small_primes = [p for p, v in enumerate(base) if v]

    primes = list(small_primes)
    segment_size = 10 ** 6
    low = limit + 1
    while low <= N:
        high = min(low + segment_size - 1, N)
        sieve = [True] * (high - low + 1)
        for p in small_primes:
            if p * p > high:
                break
            start = ((low + p - 1) // p) * p
            if start < p * p:
                start = p * p
            for j in range(start, high + 1, p):
                sieve[j - low] = False
        for k, v in enumerate(sieve):
            if v and (low + k) > 1:
                primes.append(low + k)
        low = high + 1
    return primes


def bh_fdr(pvals, alpha):
    pvals = np.asarray(pvals, dtype=float)
    n = len(pvals)
    if n == 0:
        return np.zeros(0, bool)
    order = np.argsort(pvals)
    thresholds = (np.arange(1, n + 1) / n) * alpha
    reject = np.zeros(n, bool)
    k = int(np.max(np.where(pvals[order] <= thresholds)[0]) + 1) if (pvals[order] <= thresholds).any() else 0
    reject[order[:k]] = True
    return reject


def equal_width_gof(deltas, J, alpha):
    """C7's own GOF: equal-width bins over [0,10], expected from the Exp(1) CDF."""
    n = len(deltas)
    edges = [10.0 * k / J for k in range(1, J)]  # equal-width bin edges
    counts = [0] * J
    for d in deltas:
        idx = 0
        while idx < J - 1 and d > edges[idx]:
            idx += 1
        counts[idx] += 1
    prev = 0.0
    expected = []
    for e in edges:
        expected.append(n * (math.exp(-prev) - math.exp(-e)))
        prev = e
    expected.append(n * math.exp(-prev))  # final bin [10(J-1)/J, inf)
    freq_obs = counts
    chi2_p = None
    if len(freq_obs) == J and all(n > 0 and e > 0 for e in expected):
        chi2_stat, chi2_p_val = sp_stats.chisquare(freq_obs, f_exp=expected)
        chi2_p = float(chi2_p_val)
    return {"method": "equal-width-over-[0,10]-with-Exp(1)-probabilities",
            "counts": counts, "expected": [float(e) for e in expected],
            "edges": edges, "chi2_p": chi2_p, "J": J}


def quantile_gof(deltas, J):
    """Same-binning (exponential-quantile) chi2/KS vector for the 1e-9 match requirement."""
    n = len(deltas)
    edges = [-math.log(1 - j / J) for j in range(1, J)]
    counts, _ = np.histogram(np.asarray(deltas, dtype=float),
                             bins=[0.0] + edges + [float("inf")])
    expected = np.full(J, n / J, dtype=float)
    chi2 = float(np.sum((counts - expected) ** 2 / expected))
    dof = J - 1
    chi2_p = float(sp_stats.chi2.sf(chi2, dof)) if dof > 0 else float("nan")
    ks_stat, ks_p = sp_stats.kstest(np.asarray(deltas, dtype=float), "expon", args=(0.0, 1.0))
    return {"chi2": chi2, "dof": dof, "chi2_p": chi2_p,
            "ks_stat": float(ks_stat), "ks_p": float(ks_p), "edges": edges}


def compute_primary(prereg):
    P = prereg["parameters"]
    N_MAX = P["N_MAX"]
    J = P["bins"]["J"]
    alpha = prereg["alpha"]
    blocks = P["blocks"]

    t0 = time.time()
    primes = segmented_sieve(N_MAX)
    sieve_seconds = time.time() - t0

    blocks_out = []
    for b in blocks:
        lo_i = bisect.bisect_left(primes, b["lo"])
        hi_i = bisect.bisect_left(primes, b["hi"])
        seg = primes[lo_i:hi_i]
        lower = [float(x) for x in seg[:-1]]
        upper = [float(x) for x in seg[1:]]
        deltas = [(u - l) / math.log(l) for l, u in zip(lower, upper)]
        n = len(deltas)
        mean = sum(deltas) / n if n else 0.0
        var = (sum((d - mean) ** 2 for d in deltas) / (n - 1)) if n > 1 else 0.0
        ew = equal_width_gof(deltas, J, alpha)
        qg = quantile_gof(deltas, J)
        blocks_out.append({
            "label": b["label"], "lo": b["lo"], "hi": b["hi"], "n_gaps": n,
            "mean_delta": mean, "std_delta": math.sqrt(var) if n > 1 else 0.0,
            "equal_width": ew,
            "vector_match": qg,
        })
    return primes, sieve_seconds, blocks_out


def decide(blocks_out, sidecar, alpha):
    """C7 verdict: own equal-width GOF (-BH-FDR) must match primary G1; same-binning
    chi2/KS vectors must match within 1e-9."""
    J = None
    if blocks_out:
        J = len(blocks_out[0]["equal_width"]["counts"])
    g1_c7 = bh_fdr(np.array([b["equal_width"]["chi2_p"] for b in blocks_out]), alpha).tolist()
    g4_c7 = bh_fdr(np.array([b["vector_match"]["ks_p"] for b in blocks_out]), alpha).tolist()
    verdict_agreement = bool(g1_c7 == sidecar.get("g1_verdicts"))
    chi2_diff = max(abs(b["vector_match"]["chi2"] - p) for b, p in
                    zip(blocks_out, sidecar.get("chi2", []))) if blocks_out else 0.0
    ks_diff = max(abs(b["vector_match"]["ks_stat"] - p) for b, p in
                  zip(blocks_out, sidecar.get("ks", []))) if blocks_out else 0.0
    vector_match = bool(chi2_diff < 1e-9 and ks_diff < 1e-9)
    agreement = bool(verdict_agreement and vector_match)
    return {
        "agreement": agreement,
        "verdict_agreement": verdict_agreement,
        "g1_rejected_per_block": g1_c7,
        "g4_rejected_per_block": g4_c7,
        "chi2_diff_max": float(chi2_diff),
        "ks_diff_max": float(ks_diff),
        "chi2_diff_tol": 1e-9,
        "ks_diff_tol": 1e-9,
        "n_blocks": len(blocks_out),
        "method": "pure-python segmented sieve + equal-width GOF (independent) "
                  "+ same-binning exponential-quantile vector match",
    }


def main():
    N_MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 10 ** 8
    prereg_path = sys.argv[2] if len(sys.argv) > 2 else PREREG
    sidecar_path = sys.argv[3] if len(sys.argv) > 3 else None
    sidecar = None
    if sidecar_path and os.path.exists(sidecar_path):
        sidecar = json.load(open(sidecar_path, encoding="utf-8"))

    prereg = load_prereg(prereg_path)
    prereg["parameters"]["N_MAX"] = N_MAX
    alpha = prereg["alpha"]

    print("[C7] segmented sieve up to N_MAX=%d ..." % N_MAX, flush=True)
    primes, sieve_seconds, blocks_out = compute_primary(prereg)
    anticlock = rng(INDEPENDENT_RNG_LABEL, prereg["seed"])  # own RNG label (report-only; no RNG needed)
    report_c7 = {
        "experiment_id": "EXP-0008",
        "hypothesis_id": "HYP-005",
        "question_id": "Q-M002",
        "method": "C7 independent implementation (separate path from CODE/run_prime_gaps.py)",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": prereg["seed"],
        "alpha": alpha,
        "software": version_info(),
        "machine": machine_info(),
        "sieve_seconds": sieve_seconds,
        "primes_count": len(primes),
        "N_MAX": N_MAX,
        "rng_label": INDEPENDENT_RNG_LABEL,
        "blocks": blocks_out,
        "note": "equal-width bins [0,10] with Exp(1) bin probabilities for the independent GOF; "
                "same-binning exponential-quantile vector for the 1e-9 tolerance.",
    }
    print("[C7] sieve done: %d primes in %.2fs; statistics per block" % (len(primes), sieve_seconds), flush=True)
    if sidecar is not None:
        report_c7["agreement_with_primary"] = decide(blocks_out, sidecar, alpha)
    else:
        report_c7["agreement_with_primary"] = {"error": "primary sidecar not available"}
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        json.dump(report_c7, fh, indent=2, sort_keys=True)
    agg = report_c7["agreement_with_primary"]
    print(json.dumps({"C7": "done", "primes": len(primes), "sieve_seconds": sieve_seconds,
                      "report": REPORT_PATH,
                      "agreement": agg.get("agreement", None),
                      "verdict_agreement": agg.get("verdict_agreement", None),
                      "chi2_diff_max": agg.get("chi2_diff_max", None),
                      "ks_diff_max": agg.get("ks_diff_max", None)}, indent=2))


if __name__ == "__main__":
    main()