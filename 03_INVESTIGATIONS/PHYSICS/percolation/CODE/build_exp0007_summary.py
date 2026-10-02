"""EXP-0007 read-only result separation (post-execution analysis).

Builds CODE/RESULTS/EXP-0007_summary.json from the frozen EXP-0007_results.json
with the same structure used for EXP-0006:

  primary_results       -> all gate decisions (C1, C4, C6, C7, C8, FG, in_tol),
                           p_c estimate per model, FSS fits, non-monotonicity
                           summary, decision.
  estimator_diagnostics -> width-route at sigma0 0.05 vs 0.10, per-L widths,
                           deterministic 1/nu bootstrap (label, seed, n_draws),
                           s0 ratio, fit-convergence note.

No new Monte Carlo. Deterministic from frozen EXP-0007 cells. Frozen results,
prereg and registry rows are NOT modified.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

INVESTIGATION = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.abspath(os.path.join(INVESTIGATION, "..", "..", ".."))
ENGINE = os.path.join(LAB, "04_SHARED_ENGINE")
sys.path.insert(0, ENGINE)
sys.path.insert(0, os.path.join(ENGINE, ".."))
ROOT = INVESTIGATION

from engine.utilities.core import rng, sha256_text  # noqa: E402

RAW = os.path.join(ROOT, "CODE", "RESULTS", "EXP-0007_results.json")
OUT = os.path.join(ROOT, "CODE", "RESULTS", "EXP-0007_summary.json")
PREREG = os.path.join(ROOT, "CONFIG", "prereg_EXP-0007.json")


def interp_p50(ps, W):
    below = np.asarray(W) < 0.5
    above = np.asarray(W) > 0.5
    i = int(np.flatnonzero(below)[-1])
    j = int(np.flatnonzero(above)[0])
    p0, p1 = ps[i], ps[j]
    w0, w1 = W[i], W[j]
    return p0 + (0.5 - w0) * (p1 - p0) / (w1 - w0)


def fit_width(ps, ks, ns, s0=0.10):
    import scipy.optimize as sopt
    import scipy.stats as sstats
    ps = np.asarray(ps, dtype=float)
    k = np.asarray(ks, dtype=np.int64)
    n = np.asarray(ns, dtype=np.int64)
    W = k / n
    try:
        mu0 = interp_p50(ps, W)
    except ValueError:
        mu0 = float(np.median(ps))

    def nll(theta):
        mu, logs = theta
        s = np.exp(logs)
        z = (ps - mu) / s
        P = sstats.norm.cdf(z)
        P = np.clip(P, 1e-12, 1.0 - 1e-12)
        return -float(np.sum(k * np.log(P) + (n - k) * np.log(1.0 - P)))

    res = sopt.minimize(nll, [mu0, np.log(s0)], method="L-BFGS-B",
                        bounds=[(None, None), (-10, 10)])
    mu, s = res.x[0], float(np.exp(res.x[1]))
    return {"converged": bool(res.success), "mu": float(mu), "width": s}


def bootstrap_1nu(results, draws=500, seed=42, label="perc-boot-0007-width"):
    """Deterministic width-route 1/nu bootstrap from frozen per-L count data.

    Per draw: binomial-resample each (L,p) cell at fixed n, refit probit width
    per L (s0=0.10), OLS log(width) vs log(L) slope. Returns point estimate
    (from the frozen widths), bootstrap mean/sd/quantiles.
    """
    gen = rng(label, seed)
    Ls_all = sorted(int(L) for L in results["p50"])
    cells = results["cells"]["bond_wrap"]
    ps = sorted(set(c["p"] for c in cells))
    by_L = {}
    for L in Ls_all:
        rows = [c for c in cells if c["L"] == L]
        by_L[L] = {
            "ps": np.array([r["p"] for r in rows]),
            "ks": np.array([r["k"] for r in rows], dtype=np.int64),
            "ns": np.array([r["n"] for r in rows], dtype=np.int64),
        }

    logsL = np.log(np.asarray(Ls_all, dtype=float))

    def slope_from_widths(widths):
        return float(-np.polyfit(logsL, np.log(np.asarray(widths, dtype=float)), 1)[0])

    widths_point = [results["width"][str(L)] for L in Ls_all]
    inv_nu_point = slope_from_widths(widths_point)

    draws_list = []
    for _ in range(draws):
        W = []
        ok = True
        for L in Ls_all:
            d = by_L[L]
            kb = gen.binomial(d["ns"], d["ks"] / d["ns"].astype(float))
            w = fit_width(d["ps"], kb, d["ns"], s0=0.10)
            if not w["converged"]:
                ok = False
                break
            W.append(w["width"])
        if not ok:
            continue
        draws_list.append(inv_nu_point if len(set(W)) < 2 else slope_from_widths(W))

    draws_arr = np.asarray(draws_list, dtype=float)
    mean = float(draws_arr.mean())
    sd = float(draws_arr.std(ddof=1) if len(draws_arr) > 1 else 0.0)
    q = np.percentile(draws_arr, [2.5, 97.5])
    return {
        "inv_nu_point": inv_nu_point,
        "n_draws": len(draws_arr),
        "label": label, "seed": seed,
        "mean": mean, "sd": sd,
        "ci95": [float(q[0]), float(q[1])],
    }


def main():
    results = json.load(open(RAW, encoding="utf-8"))
    c7_path = os.path.join(ROOT, "REPLICATION", "C7_exp0007_report.json")
    c7 = json.load(open(c7_path, encoding="utf-8")) if os.path.exists(c7_path) else None

    primary = {
        "fss_primary": results["primary_fss"],
        "fss_alt_models": {m: results["fss"][m] for m in ["alt1", "alt2"]},
        "p50_by_L": results["p50"],
        "se_by_L": results["se"],
        "non_monotonicity": {
            "p50_by_L": results["non_monotonicity"]["p50_by_L"],
            "local_minima": results["non_monotonicity"]["local_minima"],
            "L48_L64_delta": results["non_monotonicity"]["L48_L64_from_EXP0005"]["delta"],
            "test_question": results["non_monotonicity"]["test_question"],
            "resolution": (
                "extending to L=96,128,192 gives 6 sizes (>=4 FSS requirement); "
                "remaining local minima at L=48 and L=96 are sub-0.5% wiggles "
                "($\\sim$0.002) far inside the joint SE, and the primary 2-param "
                "FSS now passes FG (chi2_red 2.24 < 4)."
            ),
        },
        "c1": results["c1"],
        "c4": results["c4"],
        "c6": results["c6"],
        "c7": {
            "pass": c7["pass"] if c7 else None,
            "report": "REPLICATION/C7_exp0007_report.json",
            "cells_checked": len(c7["cells"]) if c7 else None,
            "p50_delta_by_L": c7.get("p50_delta_by_L") if c7 else None,
            "note": "independent pure-Python union-find on identical streams; "
                    "preregistered C7 cell bond_wrap L=32 plus new L=96/128/192",
        },
        "c8": results["c8"],
        "fg": results["gates"]["FG"],
        "in_tol": {"d_bond_wrap": results["gates"]["d_bond_wrap"],
                   "tol_pc": results["gates"]["tol_pc"],
                   "pass": results["gates"]["in_tol"]},
        "decision": results["decision"],
        "reason": results["reason"],
    }

    # width-route diagnostics
    Ls_all = sorted(int(L) for L in results["p50"])
    widths_s010 = [results["width"][str(L)] for L in Ls_all]
    widths_s005 = [results["p50_with_meta"][str(L)]["width_s0_005"] for L in Ls_all]
    ratios = [w10 / w05 for w10, w05 in zip(widths_s010, widths_s005)]
    boot = bootstrap_1nu(results)

    diag = {
        "estimator_note": "EXP-0007",
        "width_route": {
            "s0_010_widths_by_L": {str(L): w for L, w in zip(Ls_all, widths_s010)},
            "s0_005_widths_by_L": {str(L): w for L, w in zip(Ls_all, widths_s005)},
            "mean_s0_ratio": float(np.mean(ratios)),
            "inv_nu_s0_010": results["c8"]["inv_nu_width"],
            "inv_nu_gate": results["c8"]["gate"],
            "bootstrap": boot,
            "note": "primary sigma0=0.10 widths; sigma0=0.05 recorded for "
                    "diagnostic separation (identical to ~1e-9).",
        },
        "grid": {
            "p_grid": "arange(0.38,0.64,0.02)",
            "note": "coarse 0.02 grid frozen from EXP-0005 for the wrap system "
                    "(width at L=192 ~0.0077 still ~2.6x grid step; FG now driven "
                    "by resolution of the 6-size FSS rather than small-L kinks).",
        },
    }

    summary = {
        "experiment": "EXP-0007",
        "question": results["question"],
        "hypothesis": results["hypothesis"],
        "prereg_sha256": results["prereg_sha256"],
        "prereg_path": "CONFIG/prereg_EXP-0007.json",
        "raw_results_path": "CODE/RESULTS/EXP-0007_results.json",
        "primary_results": primary,
        "estimator_diagnostics": diag,
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    print("Wrote", OUT)
    print("FG bond_wrap chi2_red = %.4f (gate 4.0)" % results["primary_fss"]["chi2_red"])
    print("1/nu = %.4f  boot mean %.4f sd %.4f CI95 [%.4f, %.4f]"
          % (boot["inv_nu_point"], boot["mean"], boot["sd"], *boot["ci95"]))
    print("C7 pass:", c7["pass"] if c7 else None)
    print("p50 by L:", {str(L): round(v, 5) for L, v in results["p50"].items()})


if __name__ == "__main__":
    main()