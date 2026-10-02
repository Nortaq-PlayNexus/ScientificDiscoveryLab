"""EXP-0006 read-only result separation (post-execution analysis).

Builds CODE/RESULTS/EXP-0006_summary.json from the frozen EXP-0006_results.json
with the structure required by DIAGNOSTICS/EXP-0006_proposal.md:

  primary_results       -> all gate decisions (C1-C7, FG, in_tol), p_c estimates
                           with SEs, FSS fits (a, b, chi2_red) per system.
  estimator_diagnostics -> C8 width-route at multiple sigma0 (0.05 comparison +
                           0.10 primary), width scales per L, linear-WLS ratios,
                           convergence flags.

No new Monte Carlo. Deterministic from frozen cells. Frozen EXP-0006 results
and registry rows are NOT modified.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy import stats as sstats
from scipy import optimize as sopt
from scipy import ndimage as snd

ROOT = os.path.dirname(os.path.abspath(__file__))
INVESTIGATION = os.path.abspath(os.path.join(ROOT, ".."))
RESULTS_DIR = os.path.join(ROOT, "RESULTS")
RAW = os.path.join(RESULTS_DIR, "EXP-0006_results.json")
OUT = os.path.join(RESULTS_DIR, "EXP-0006_summary.json")


def interp_p50(ps, W):
    ps = np.asarray(ps, dtype=float)
    W = np.asarray(W, dtype=float)
    below = W < 0.5
    above = W > 0.5
    if not below.any() or not above.any():
        raise ValueError("p50 not bracketed")
    i = int(np.flatnonzero(below)[-1])
    j = int(np.flatnonzero(above)[0])
    p0, p1 = ps[i], ps[j]
    w0, w1 = W[i], W[j]
    return float(p0 + (0.5 - w0) * (p1 - p0) / (w1 - w0))


def fit_width_mle(ps, ks, ns, s0):
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
    return float(res.x[0]), float(np.exp(res.x[1])), bool(res.success)


def fit_width_wls(ps, ks, ns):
    """Closed-form linear-WLS probit: W approx Phi((p-mu)/s), invert then WLS."""
    ps = np.asarray(ps, dtype=float)
    k = np.asarray(ks, dtype=np.int64)
    n = np.asarray(ns, dtype=np.int64)
    W = np.clip(k / n, 1e-6, 1.0 - 1e-6)
    z = sstats.norm.ppf(W)
    se_w = np.sqrt(np.clip(W * (1.0 - W) / n, 1e-9, None))
    se_z = se_w / np.maximum(sstats.norm.pdf(z), 1e-9)
    A = np.vstack([np.ones_like(ps), ps]).T
    Wm = np.diag(1.0 / se_z)
    coef, *_ = np.linalg.lstsq(Wm @ A, Wm @ z, rcond=None)
    mu = -coef[0] / coef[1]
    s = 1.0 / coef[1]
    return float(mu), float(s)


def widths_per_L(results, system, s0):
    out = {}
    for L in sorted({c["L"] for c in results["cells"][system]}):
        cells = [c for c in results["cells"][system] if c["L"] == L]
        ps = [c["p"] for c in cells]
        if system == "bond_wrap":
            ks = [c["k"] for c in cells]
        else:
            ks = [c["k_v"] for c in cells]
        ns = [c["n"] for c in cells]
        mu_mle, s_mle, conv = fit_width_mle(ps, ks, ns, s0)
        mu_wls, s_wls = fit_width_wls(ps, ks, ns)
        out[str(L)] = {
            "width_mle_s0": s_mle, "width_wls": s_wls, "ratio_mle_wls": s_mle / s_wls,
            "mu_mle": mu_mle, "mu_wls": mu_wls, "converged": conv,
        }
    return out


def inv_nu_from(widths):
    Ls = sorted(int(k) for k in widths)
    logs = np.log(np.array([widths[str(L)]["width_mle_s0"] for L in Ls], dtype=float))
    slope, *_ = np.polyfit(np.log(Ls), logs, 1)
    return float(-slope)


def main():
    results = json.load(open(RAW, encoding="utf-8"))

    c7_path = os.path.join(INVESTIGATION, "REPLICATION",
                           "C7_exp0006_report.json")
    if os.path.exists(c7_path):
        c7 = json.load(open(c7_path, encoding="utf-8"))["pass"]
    else:
        c7 = None

    primary = {}
    for system in ["bond_span", "bond_wrap", "site_span"]:
        primary[system] = {
            "fss": results["fss"][system],
            "p50": results["p50"][system],
        }
    primary["gates"] = dict(results["gates"])
    primary["gates"]["c7"] = c7
    primary["c1"] = results["c1"]
    primary["c2"] = results["c2"]
    primary["c4"] = results["c4"]
    primary["c6"] = results["c6"]
    primary["c7"] = {"pass": c7,
                     "report": "REPLICATION/C7_exp0006_report.json",
                     "note": "pure-Python union-find re-implementation on identical streams"}
    primary["decision"] = results["decision"]
    primary["reason"] = results["reason"]
    primary["corroboration"] = results["corroboration"]

    w05 = widths_per_L(results, "bond_span", 0.05)
    w10 = widths_per_L(results, "bond_span", 0.10)
    w05_wrap = widths_per_L(results, "bond_wrap", 0.10)
    w05_site = widths_per_L(results, "site_span", 0.10)

    diag = {
        "estimator_note": results.get("experiment", ""),
        "width_route": {
            "primary_s0": 0.10,
            "comparison_s0": 0.05,
            "bond_span": {
                "s0_005": w05, "s0_010": w10,
                "inv_nu_s0_005": inv_nu_from(w05),
                "inv_nu_s0_010": inv_nu_from(w10),
                "gate": [0.6, 0.9],
            },
            "bond_wrap_reference_s0_010": w05_wrap,
            "site_span_reference_s0_010": w05_site,
        },
        "grid_resolution": {
            "bond_span_L256_step": 0.004, "bond_span_L512_step": 0.004,
            "note": "fine grid (0.004) is ~1.6x the physical width (0.0065/0.0039) at L=256/512; "
                    "resolves the transition, unlike EXP-0005 coarse 0.02 grid.",
        },
    }

    summary = {
        "experiment": "EXP-0006",
        "question": "Q-P004",
        "hypothesis": "HYP-004",
        "prereg_sha256": results["prereg_sha256"],
        "prereg_path": "CONFIG/prereg_EXP-0006.json",
        "raw_results_path": "CODE/RESULTS/EXP-0006_results.json",
        "primary_results": primary,
        "estimator_diagnostics": diag,
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    print("Wrote", OUT)
    print("C8 primary (s0=0.10): 1/nu = %.4f (gate [0.6,0.9])" % diag["width_route"]["bond_span"]["inv_nu_s0_010"])
    print("C8 comparison (s0=0.05): 1/nu = %.4f" % diag["width_route"]["bond_span"]["inv_nu_s0_005"])
    print("C7 pass:", c7)


if __name__ == "__main__":
    main()