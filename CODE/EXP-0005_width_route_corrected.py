"""EXP-0005 CORRECTED width-route validation (diagnostic).
Reproduces the frozen run's width-route (C8) using the SAME frozen
cell counts but with the corrected estimator starting sigma
(s0=0.10 instead of the frozen s0=0.05), avoiding a degenerate
sigma->0 basin. Deterministic: no new MC, no frozen file written.
Outputs a self-contained result JSON clearly labeled as diagnostic.
"""
import json, os
import numpy as np
from scipy import stats as _stt
from scipy import optimize as _opt

base = r"C:\Users\natha\ScientificDiscoveryLab"
R = json.load(open(os.path.join(base, "03_INVESTIGATIONS", "PHYSICS", "percolation",
                                "CODE", "RESULTS", "EXP-0005_results.json"), encoding="utf-8"))
cells = R["cells"]
fc = R["p50"]
PRE = os.path.join(base, "03_INVESTIGATIONS", "PHYSICS", "percolation", "CONFIG",
                   "prereg_EXP-0005.json")

def interp_p50(ps, W):
    ps = np.asarray(ps, float); W = np.asarray(W, float)
    below = W < 0.5; above = W > 0.5
    i = int(np.flatnonzero(below)[-1]); j = int(np.flatnonzero(above)[0])
    return float(ps[i] + (0.5 - W[i]) * (ps[j] - ps[i]) / (W[j] - W[i]))

def fit_probit_width(ps, ks, ns, s0=0.05):
    ps = np.asarray(ps, float); k = np.asarray(ks, int); n = np.asarray(ns, int)
    W = k / n
    mu0 = interp_p50(ps, W)
    def nll(theta):
        mu, logs = theta
        s = np.exp(logs)
        z = (ps - mu) / s
        P = _stt.norm.cdf(z); P = np.clip(P, 1e-12, 1 - 1e-12)
        return -float(np.sum(k * np.log(P) + (n - k) * np.log(1.0 - P)))
    res = _opt.minimize(nll, [mu0, np.log(s0)], method="L-BFGS-B",
                        bounds=[(None, None), (-10, 10)])
    return float(res.x[0]), float(np.exp(res.x[1])), float(res.fun)

def by_L(cells, sys):
    d = {}
    for c in cells[sys]:
        d.setdefault(c["L"], []).append(c)
    return {L: sorted(cs, key=lambda c: c["p"]) for L, cs in d.items()}

out = {
    "experiment": "EXP-0005",
    "kind": "DIAGNOSTIC — width-route corrected estimator (NOT a re-run of the frozen EXP-0005)",
    "diagnostic_for": "C8 (width-route 1/nu) and estimator degeneracy",
    "frozen_results_path": os.path.join("CODE", "RESULTS", "EXP-0005_results.json"),
    "methodology_differs_from_frozen": True,
    "frozen_estimator": {"width_fn": "fit_probit_width (L-BFGS-B) starting s0=0.05",
                          "in_code_lines": "286-296 of CODE/run_percolation.py"},
    "corrected_estimator": {"width_fn": "fit_probit_width (L-BFGS-B) starting s0=0.10",
                            "rationale": "avoids sigma->0 degenerate basin on monotone-ordered cell data"},
    "data": "recomputed from the SAME frozen cells (no new MC); frozen RESULTS/registry NOT modified",
    "per_L": {},
    "C8": {},
    "comparison_to_frozen": {},
}

BL = {sys: by_L(cells, sys) for sys in ("bond_span", "bond_wrap", "site_span")}
for sys, BLsys in BL.items():
    for L in sorted(BLsys):
        cs = BLsys[L]
        ps = np.array([c["p"] for c in cs])
        kv = np.array([c["k"] if "k" in c and "k_v" not in c else c["k_v"] for c in cs])
        n = np.array([c["n"] for c in cs])
        mu_a, s_a, nll_a = fit_probit_width(ps, kv, n, s0=0.05)
        mu_b, s_b, nll_b = fit_probit_width(ps, kv, n, s0=0.10)
        out["per_L"][f"{sys}:L{L}"] = {
            "n_cells": len(cs), "grid_step": float(np.median(np.diff(ps))),
            "MLE_s0=0.05": {"mu": mu_a, "width": s_a, "nll": nll_a},
            "MLE_s0=0.10": {"mu": mu_b, "width": s_b, "nll": nll_b},
        }

# C8 across bond_span
for key, s0 in (("MLE_s0=0.05 (FROZEN)", 0.05), ("MLE_s0=0.10 (CORRECTED)", 0.10)):
    Ls = sorted(int(L) for L in BL["bond_span"])
    ws = [fit_probit_width(np.array([c["p"] for c in BL["bond_span"][L]]),
                            np.array([c["k_v"] for c in BL["bond_span"][L]]),
                            np.array([c["n"] for c in BL["bond_span"][L]]), s0=s0)[1] for L in Ls]
    slope = np.polyfit(np.log(np.array(Ls, float)), np.log(np.array(ws, float)), 1)[0]
    out["C8"][key] = {"Ls": Ls, "widths": ws, "inv_nu": float(-slope),
                       "nu": float(1.0 / max(-slope, 1e-9)),
                       "gate": [0.6, 0.9], "pass": bool(0.6 <= -slope <= 0.9)}

out["comparison_to_frozen"] = {
    "frozen_C8_inv_nu": R["c8"]["inv_nu_width"],
    "frozen_C8_pass": R["c8"]["pass"],
    "frozen_FG": {s: R["fss"][s]["chi2_red"] for s in ("bond_span", "bond_wrap", "site_span")},
    "corrected_C8_inv_nu": out["C8"]["MLE_s0=0.10 (CORRECTED)"]["inv_nu"],
    "corrected_C8_pass": out["C8"]["MLE_s0=0.10 (CORRECTED)"]["pass"],
}

res_path = os.path.join(base, "03_INVESTIGATIONS", "PHYSICS", "percolation",
                        "CODE", "RESULTS", "EXP-0005_width_route_corrected.json")
with open(res_path, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, sort_keys=True)
print("wrote", res_path)
print("frozen C8 inv_nu =", out["comparison_to_frozen"]["frozen_C8_inv_nu"],
      "pass =", out["comparison_to_frozen"]["frozen_C8_pass"])
print("corrected C8 inv_nu =", out["comparison_to_frozen"]["corrected_C8_inv_nu"],
      "pass =", out["comparison_to_frozen"]["corrected_C8_pass"])
