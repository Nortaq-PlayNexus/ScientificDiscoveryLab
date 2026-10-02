"""EXP-0004, C7 - independent battery re-implementation (REPLICATION).

Recomputes five representative test families from the documented formulas only
(FALSIFICATION/planning_checks.md, EXPERIMENT_PLAN.md) on the IDENTICAL streams
the primary battery used, and compares p-values to the primary battery's
recorded results (RESULTS/EXP-0004_results.json).

Deliberately straight-line implementation: explicit loops over the formulas
(multinomial counting via collections instead of numpy vectorisation) to be a
real, distinct implementation of the same statistics.

Run from the investigation folder:
    python REPLICATION/independent_check.py
"""

from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter

import numpy as np

ENGINE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "04_SHARED_ENGINE")
)
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

from engine.statistics.testers import bh_fdr  # noqa: E402
from engine.utilities.core import SEED_LADDER, rng  # noqa: E402
from engine.validation import rng_battery  # noqa: E402

from scipy import special  # noqa: E402

INV = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(INV, "RESULTS", "EXP-0004_results.json")
LAB_LABEL = "Q-I004:cert"
ALPHA = 0.01
TOL = 1e-6
LOG10_TOL = 1e-4


def erfc_p(z):
    return special.erfc(abs(z) / math.sqrt(2.0))


def iMonobit(bits):
    n = len(bits)
    s = sum(2 * int(b) - 1 for b in bits)
    return float(erfc_p(s / math.sqrt(n)))


def iBlockFreq(bits, m=128):
    n = len(bits)
    nb = n // m
    chi2 = 0.0
    for j in range(nb):
        block = bits[j * m:(j + 1) * m]
        pi = sum(block) / m
        chi2 += (pi - 0.5) ** 2
    chi2 *= 4.0 * m
    return float(special.gammaincc(nb / 2.0, chi2 / 2.0))


def iRuns(bits):
    n = len(bits)
    pi = sum(int(b) for b in bits) / n
    if pi in (0.0, 1.0):
        return float("nan")
    v = 1
    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            v += 1
    num = abs(v - 2.0 * n * pi * (1.0 - pi))
    den = 2.0 * math.sqrt(2.0 * n) * pi * (1.0 - pi)
    return float(erfc_p(num / den))


def iByteChisq(data):
    counts = Counter(int(b) for b in data)
    n = len(data)
    exp = n / 256.0
    chi2 = sum((counts.get(k, 0) - exp) ** 2 / exp for k in range(256))
    return float(special.gammaincc(255.0 / 2.0, chi2 / 2.0))


def iFloatChisq(data):
    counts = Counter(int(u * 32) if int(u * 32) < 32 else 31 for u in data)
    n = len(data)
    exp = n / 32.0
    chi2 = sum((counts[k] - exp) ** 2 / exp for k in range(32))
    return float(special.gammaincc(31.0 / 2.0, chi2 / 2.0))


# test ids replicated by this independent implementation
IMPL_TESTS = ("T01_monobit", "T02_blockfreq", "T03_runs", "T11_bytes", "T12_floats")


def main():
    with open(RESULTS_PATH, "r", encoding="utf-8") as fh:
        primary = json.load(fh)

    comparisons = []
    max_logdiff = 0.0
    any_mismatch = False
    for seed in SEED_LADDER:
        gen = rng(LAB_LABEL, seed)
        bytes_arr, floats_arr, words_arr, _ = streams_independent(gen)
        bits = np.unpackbits(bytes_arr)
        indep = {
            "T01_monobit": iMonobit(bits),
            "T02_blockfreq": iBlockFreq(bits),
            "T03_runs": iRuns(bits),
            "T11_bytes": iByteChisq(bytes_arr),
            "T12_floats": iFloatChisq(floats_arr),
        }
        for tid in IMPL_TESTS:
            primary_p = primary["generators"]["G_LAB"][SEED_LADDER.index(seed)][
                "pvals"][tid]
            indep_p = indep[tid]
            diff = abs(primary_p - indep_p)
            logdiff = abs(math.log10(primary_p + 1e-300) -
                          math.log10(indep_p + 1e-300)) if primary_p > 1e-300 else diff
            ok = diff <= TOL or logdiff <= LOG10_TOL
            if not (primary_p == primary_p and indep_p == indep_p):  # nan check
                ok = (primary_p != primary_p) == (indep_p != indep_p)
            max_logdiff = max(max_logdiff, float(logdiff))
            any_mismatch = any_mismatch or not ok
            comparisons.append(
                {
                    "seed": seed,
                    "test": tid,
                    "primary_p": primary_p,
                    "independent_p": indep_p,
                    "abs_diff": float(diff),
                    "log10_diff": float(logdiff),
                    "agree": ok,
                }
            )

    # decision-level agreement: replicate the G_LAB aggregate stat from the
    # independently recomputed subset. We recompute the full per-seed p-multiset
    # by substituting the 5 independently recomputed values into the primary
    # grid (a conservative sensitivity check), then re-run KS + binomial + FDR.
    merged = []
    for idx, seed in enumerate(SEED_LADDER):
        pvals = dict(primary["generators"]["G_LAB"][idx]["pvals"])
        for c in comparisons:
            if c["seed"] == seed and c["test"] in pvals:
                pvals[c["test"]] = c["independent_p"]
        merged.extend(pvals.values())

    from scipy import stats

    from engine.statistics.testers import binomial_band

    n = len(merged)
    ks_p = float(stats.kstest(merged, "uniform").pvalue)
    small = [p for p in merged if p <= ALPHA]
    band = binomial_band(n, p=ALPHA, alpha=0.05)
    sig, _ = bh_fdr(merged, alpha=ALPHA)
    decision_agree = bool(
        ks_p > ALPHA
        and band["lo"] <= len(small) <= band["hi"]
        and band["lo"] <= int(sig.sum()) <= band["hi"]
    )

    out = {
        "experiment": "EXP-0004",
        "check": "C7",
        "reimplemented_tests": list(IMPL_TESTS),
        "seeds": list(SEED_LADDER),
        "comparisons": comparisons,
        "n_comparisons": len(comparisons),
        "all_agree": not any_mismatch,
        "max_log10_diff": max_logdiff,
        "decision_substitution": {
            "ks_p": ks_p,
            "small_p_count": len(small),
            "band": band,
            "fdr_flag_count": int(sig.sum()),
            "decision_unchanged": decision_agree,
        },
    }
    out_path = os.path.join(INV, "REPLICATION", "independent_check.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)

    print(f"C7 independent implementation: all_agree={not any_mismatch} "
          f"over {len(comparisons)} comparisons")
    print(f"  decision unchanged after substitution = {decision_agree}")
    if any_mismatch:
        bad = [c for c in comparisons if not c["agree"]]
        print(f"  MISMATCHES: {[(c['seed'], c['test']) for c in bad]}")
    return out


def streams_independent(gen):
    """INVARIANT mirror of run_rng_cert.make_generator draw sequence.

    Re-derive the exact arrays the primary battery used (same call order and
    sizes), using numpy only as the data holder - statistics come from the
    independent implementations above.
    """
    bytes_arr = np.asarray(
        gen.integers(0, 256, rng_battery.NBYTES, dtype=np.uint32), dtype=np.uint8
    )
    floats_arr = np.asarray(gen.random(rng_battery.NF))
    words_arr = np.asarray(gen.integers(0, 2 ** 32, rng_battery.NW, dtype=np.uint32))
    return bytes_arr, floats_arr, words_arr, None


if __name__ == "__main__":
    main()