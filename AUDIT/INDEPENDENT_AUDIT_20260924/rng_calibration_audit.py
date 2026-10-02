"""Audit-only multi-seed calibration of the laboratory RNG battery.

The historical EXP-0004 decision pooled 24 p-values per seed and treated the
pool as independent.  This script keeps the battery implementation fixed but
uses 80 fresh seeds per generator, reports each test's marginal calibration,
and quantifies the dependence that invalidates the pooled rule.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

LAB_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(LAB_ROOT / "04_SHARED_ENGINE"))
from engine.utilities.core import rng
from engine.validation.rng_battery import TEST_IDS, run_battery, streams_for

SEEDS = tuple(range(100000, 100080))
ALPHA = 0.01
LAB_LABEL = "audit:rng-calibration"


class MTAdapter:
    def __init__(self, seed):
        self.g = np.random.RandomState(seed)

    def integers(self, low, high, size, dtype=np.uint32):
        if high == 2 ** 32:
            lo = self.g.randint(0, 65536, size).astype(np.uint32)
            hi = self.g.randint(0, 65536, size).astype(np.uint32)
            raw = (hi << np.uint32(16)) | lo
        else:
            raw = self.g.randint(low, high, size)
        return np.asarray(raw, dtype=dtype)

    def random(self, size):
        return np.asarray(self.g.random(size))


def make_gen(name, seed):
    if name == "G_LAB":
        return rng(LAB_LABEL, seed)
    if name == "G_PCG":
        return np.random.default_rng(seed)
    if name == "G_MT":
        return MTAdapter(seed)
    raise ValueError(name)


def exact_band(n, p=ALPHA, coverage=0.95):
    # scipy's interval is the central equal-tail interval used by the lab rule.
    lo, hi = stats.binom.ppf((1 - coverage) / 2, n, p), stats.binom.ppf(
        1 - (1 - coverage) / 2, n, p
    )
    return [int(lo), int(hi)]


def bh_flags(values, alpha=ALPHA):
    p = np.asarray(values, dtype=float)
    order = np.argsort(p)
    m = len(p)
    thresholds = alpha * np.arange(1, m + 1) / m
    passed = p[order] <= thresholds
    out = np.zeros(m, dtype=bool)
    if passed.any():
        kmax = int(np.flatnonzero(passed).max())
        out[order[: kmax + 1]] = True
    return out


def summarize(mat):
    # mat: seeds x tests
    flat = mat.ravel()
    per_test = {}
    for j, tid in enumerate(TEST_IDS):
        vals = mat[:, j]
        finite = vals[np.isfinite(vals)]
        per_test[tid] = {
            "n": int(finite.size),
            "ks_stat": float(stats.kstest(finite, "uniform").statistic) if finite.size else None,
            "ks_p": float(stats.kstest(finite, "uniform").pvalue) if finite.size else None,
            "small_p_count": int(np.sum(finite <= ALPHA)),
            "small_p_fraction": float(np.mean(finite <= ALPHA)) if finite.size else None,
            "min": float(np.min(finite)) if finite.size else None,
            "max": float(np.max(finite)) if finite.size else None,
        }
    corr = np.corrcoef(mat, rowvar=False)
    finite_corr = corr[np.isfinite(corr) & ~np.eye(len(TEST_IDS), dtype=bool)]
    small = int(np.sum(flat <= ALPHA))
    band = exact_band(flat.size)
    fdr = int(bh_flags(flat).sum())
    per_seed_small = np.sum(mat <= ALPHA, axis=1)
    return {
        "n_seeds": int(mat.shape[0]),
        "n_pvalues": int(flat.size),
        "pooled_ks": {
            "stat": float(stats.kstest(flat, "uniform").statistic),
            "p": float(stats.kstest(flat, "uniform").pvalue),
        },
        "pooled_small_p_count": small,
        "pooled_binomial_band_if_independent": band,
        "pooled_bh_flag_count": fdr,
        "per_test": per_test,
        "pvalue_correlation": {
            "mean_abs_offdiag": float(np.mean(np.abs(finite_corr))),
            "max_abs_offdiag": float(np.max(np.abs(finite_corr))),
            "pairs_abs_corr_ge_0_3": int(np.sum((np.abs(corr) >= 0.3) & ~np.eye(len(TEST_IDS), dtype=bool)) // 2),
            "pairs_abs_corr_ge_0_5": int(np.sum((np.abs(corr) >= 0.5) & ~np.eye(len(TEST_IDS), dtype=bool)) // 2),
        },
        "per_seed_small_p_count": {
            "values": [int(x) for x in per_seed_small],
            "mean": float(np.mean(per_seed_small)),
            "sd": float(np.std(per_seed_small, ddof=1)),
            "max": int(np.max(per_seed_small)),
        },
    }


def main():
    t0 = time.time()
    results = {
        "purpose": "Fresh-seed marginal calibration and dependence audit of EXP-0004 battery",
        "method": "Exact historical battery implementation, 80 fresh seeds per generator; "
                  "per-test calibration replaces pooled-p assumption",
        "environment": {"python": sys.version, "platform": platform.platform(),
                         "numpy": np.__version__},
        "seeds": list(SEEDS), "alpha": ALPHA, "test_ids": list(TEST_IDS),
        "generators": {},
    }
    for name in ("G_LAB", "G_PCG", "G_MT"):
        rows = []
        for seed in SEEDS:
            b, f, w, bits = streams_for(make_gen(name, seed))
            vals = dict(run_battery(bits, b, f, w))
            rows.append([float(vals[t]) for t in TEST_IDS])
        mat = np.asarray(rows, dtype=float)
        results["generators"][name] = summarize(mat)
        results["generators"][name]["raw_pvalues"] = mat.tolist()
    results["elapsed_seconds"] = time.time() - t0
    results["interpretation"] = (
        "Marginal per-test calibration is the defensible interpretation of this "
        "battery. The historical pooled KS/binomial/BH decision assumes independence "
        "among p-values from the same stream, but the orchestration reuses the same "
        "bits array for all bit-spectrum tests, so that assumption is false."
    )
    path = Path(__file__).with_name("rng_calibration_results.json")
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({k: {x: v for x, v in d.items() if x != "raw_pvalues"}
                      for k, d in results["generators"].items()}, indent=2))
    print(f"Wrote {path}; elapsed={results['elapsed_seconds']:.1f}s")


if __name__ == "__main__":
    main()
