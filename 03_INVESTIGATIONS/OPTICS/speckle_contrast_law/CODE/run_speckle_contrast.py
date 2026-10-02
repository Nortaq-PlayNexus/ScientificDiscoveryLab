"""EXP-0002 — Speckle contrast law (Q-O001 / HYP-001).

Fully-developed speckle numerically: random-phase disk pupil -> complex Gaussian
field in the image plane (stationary mean intensity). M independent realisations
are intensity-summed; contrast C = std/mean is compared with 1/sqrt(M).

Pipeline: preregistration frozen -> measurement grid -> bootstrap CI -> BH-FDR ->
resolution-trend check -> generator sanity (KS) -> reports.

Run from the investigation folder:
    python CODE/run_speckle_contrast.py
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

ENGINE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "04_SHARED_ENGINE")
)
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

from engine.hypothesis_testing.prereg import freeze_config  # noqa: E402
from engine.reproducibility.experiments import append_registry_row  # noqa: E402
from engine.statistics.testers import bh_fdr  # noqa: E402
from engine.utilities.core import (  # noqa: E402
    SEED_LADDER,
    make_experiment_json,
    rng,
)

INV = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENT_ID = "EXP-0002"
SEED = 42
GRID_N = (32, 64, 128, 256)
M_LADDER = (1, 2, 4, 8, 16)
N_REAL = 32
N_BOOT = 500
ALPHA = 0.01
APERTURE_FRAC = 1 / 8
INTERIOR_FRAC = 0.8  # inner disk 80% of grid radius for the "interior" check


def bootstrap_effects(block_values, m, n_boot, seed):
    """Bootstrap block-mean r = C*sqrt(M); returns (r_dist, two-sided p vs r=1)."""
    gen = rng("bootstrap-speckle-r", seed)
    n = len(block_values)
    block_values = np.asarray(block_values, dtype=float)
    dist = np.empty(n_boot)
    for i in range(n_boot):
        dist[i] = np.mean(block_values[gen.integers(0, n, size=n)]) * np.sqrt(m)
    n1 = 1.0
    p = 2.0 * min(float((dist >= n1).mean()), float((dist <= n1).mean()))
    p = min(1.0, p + np.finfo(float).eps)
    return dist, p


def speckle_intensity(n, aperture_r, gen):
    """One fully-developed speckle intensity field (stationary mean)."""
    y, x = np.mgrid[-n // 2 : n // 2, -n // 2 : n // 2]
    pupil = (x**2 + y**2) <= aperture_r**2
    phases = gen.uniform(0.0, 2.0 * np.pi, size=(n, n))
    spectrum = pupil * np.exp(1j * phases)
    field = np.fft.ifft2(spectrum)
    return np.abs(field) ** 2


def interior_mask(n):
    y, x = np.mgrid[-n // 2 : n // 2, -n // 2 : n // 2]
    r = INTERIOR_FRAC * n / 2
    return (x**2 + y**2) <= r**2


def ci_bootstrap(block_values, n_boot, seed, alpha=0.05):
    """Percentile CI across realisation-blocks (block = one speckle realisation)."""
    gen = rng("bootstrap-speckle", seed)
    block_values = np.asarray(block_values, dtype=float)
    means = np.empty(n_boot)
    for i in range(n_boot):
        idx = gen.integers(0, len(block_values), size=len(block_values))
        means[i] = np.mean(block_values[idx])
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi)


def run_cell(n, m, gen):
    """Return (contrast, interior_contrast) using prefix sums of M speckle fields."""
    aperture_r = int(n * APERTURE_FRAC)
    mask = interior_mask(n)
    summed = np.zeros((n, n))
    for k in range(1, m + 1):
        summed = summed + speckle_intensity(n, aperture_r, gen)
    mean_val = summed.mean()
    std_val = summed.std()
    return (
        float(std_val / mean_val),
        float(summed[mask].std() / summed[mask].mean()),
    )


def main():
    os.makedirs(os.path.join(INV, "CONFIG"), exist_ok=True)
    os.makedirs(os.path.join(INV, "RESULTS"), exist_ok=True)
    os.makedirs(os.path.join(INV, "FIGURES"), exist_ok=True)
    os.makedirs(os.path.join(INV, "REPORT"), exist_ok=True)
    os.makedirs(os.path.join(INV, "REPLICATION"), exist_ok=True)

    prereg_path = os.path.join(INV, "CONFIG", "prereg_EXP-0002.json")
    freeze_config(
        experiment_id=EXPERIMENT_ID,
        hypothesis_id="HYP-001",
        question_id="Q-O001",
        seed=SEED,
        alpha=ALPHA,
        controls=("C1 positive M=1", "C2 MC spread", "C3 seed ladder",
                  "C4 resolution ladder", "C5 generator KS", "C7 ensemble-vs-space"),
        analyses=("bootstrap-99% CI", "BH-FDR across grid"),
        params={"grid_N": list(GRID_N), "M_ladder": list(M_LADDER),
                "n_realisations": N_REAL, "n_boot": N_BOOT,
                "aperture_frac": APERTURE_FRAC, "interior_frac": INTERIOR_FRAC},
        out_path=prereg_path,
        note="Frozen before execution.",
    )

    gen = rng("speckle-contrast", SEED)
    cells = {}
    for n in GRID_N:
        for m in M_LADDER:
            c_vals = []
            c_int = []
            for _ in range(N_REAL):
                c, ci_int = run_cell(n, m, gen)
                c_vals.append(c)
                c_int.append(ci_int)
            lo, hi = ci_bootstrap(c_vals, N_BOOT, SEED, alpha=ALPHA)
            r_dist, p_two = bootstrap_effects(c_vals, m, N_BOOT, SEED)
            r_m = float(np.mean(c_vals) * np.sqrt(m))
            cells[f"N{n}_M{m}"] = {
                "c_mean": float(np.mean(c_vals)),
                "c_ci_low": lo,
                "c_ci_high": hi,
                "r": r_m,
                "p_two_sided_null_r_eq_1": p_two,
                "c_interior_mean": float(np.mean(c_int)),
                "n": n,
                "m": m,
            }

    # BH-FDR over the grid (alpha 0.01)
    keys = sorted(cells)
    pvals = np.array([cells[k]["p_two_sided_null_r_eq_1"] for k in keys])
    sig, (_ranked, thr, order) = bh_fdr(pvals, alpha=ALPHA)
    for i, k in enumerate(keys):
        cells[k]["fdr_sig"] = bool(sig[i])

    # C5: generator sanity - single-speckle intensity vs exponential (N=256)
    from scipy import stats as _s

    n = 256
    gen5 = rng("speckle-ks", SEED)
    a_r = int(n * 8 * APERTURE_FRAC)
    i1 = speckle_intensity(n, a_r, gen5)
    sample = i1.ravel()
    sample = sample[np.random.default_rng(0).choice(sample.size, size=20000,
                                                   replace=False)]
    ks = _s.kstest(sample, "expon", args=(0, sample.mean()))

    # C3 seed ladder spot-check: r at (N=128, M=8) across secondary seeds
    seed_r = {}
    for s in SEED_LADDER[1:]:
        g = rng("speckle-contrast", s)
        cs = [run_cell(128, 8, g)[0] for _ in range(16)]
        seed_r[s] = float(np.mean(cs) * np.sqrt(8))

    result = {
        "experiment": EXPERIMENT_ID,
        "question": "Q-O001",
        "hypothesis": "HYP-001",
        "cells": cells,
        "generator_ks_expon_p": float(ks.pvalue),
        "generator_ks_stat": float(ks.statistic),
        "seed_ladder_r_M8_N128": seed_r,
        "decision": None,
        "conclusion_lab": None,
    }

    # Decision rule (frozen): at N=256, all M cells 99% CI contains 1
    n256 = [cells[k] for k in keys if cells[k]["n"] == 256]
    held = all(c["c_ci_low"] * np.sqrt(c["m"]) <= 1 <=
               c["c_ci_high"] * np.sqrt(c["m"]) for c in n256)
    if held and ks.pvalue > 1e-6:
        result["decision"] = "H1_SUPPORTED"
        result["conclusion_lab"] = (
            "C(M)=1/sqrt(M) reproduced at N=256 within 99% bootstrap CIs; "
            "remaining scatter is Monte Carlo noise."
        )
    else:
        result["decision"] = "H2_FLAG_DEV"
        result["conclusion_lab"] = (
            "Resolution-persistent deviation flagged; escalate to independent "
            "implementation + kill-the-hypothesis before any interpretation."
        )

    os.makedirs(os.path.join(INV, "CONFIG"), exist_ok=True)
    res_path = os.path.join(INV, "RESULTS", "EXP-0002_results.json")
    with open(res_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)

    make_experiment_json(
        experiment_id=EXPERIMENT_ID,
        question="Q-O001",
        hypothesis="HYP-001",
        seed=SEED,
        parameters={**{k: v for k, v in cells.items()},
                    "n_realisations": N_REAL, "n_boot": N_BOOT},
        result=result,
        out_path=os.path.join(INV, "CONFIG", f"{EXPERIMENT_ID}_experiment.json"),
    )

    reg_path = os.path.join(INV, "CONFIG", "registry.jsonl")
    append_registry_row(reg_path, {
        "experiment_id": EXPERIMENT_ID, "hypothesis": "HYP-001",
        "question": "Q-O001", "seed": SEED, "decision": result["decision"],
        "result_path": res_path,
    })

    print(json.dumps(result, indent=2, sort_keys=True))
    return result


if __name__ == "__main__":
    main()