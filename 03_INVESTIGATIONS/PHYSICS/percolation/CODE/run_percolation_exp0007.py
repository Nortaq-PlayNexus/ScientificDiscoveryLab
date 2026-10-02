"""EXP-0007 — Extended bond_wrap Monte Carlo at L=32,48,64,96,128,192.

Follow-up to EXP-0005 (diagnostic) and EXP-0006 (never executed).
Extends bond_wrap to L=96,128,192 to test whether the L48->L64
non-monotonicity (p50: 0.49859->0.49748->0.50036) is a finite-size
artifact or persists. Combined with EXP-0005 bond_wrap at L=32,48,64
this gives 6 sizes for FSS (>=4 requirement met).

Methodology identical to EXP-0005: torus horizontal wrap on Lx(2L) strip,
toroidal rows, pure-Python union-find.

Independent seeds for NEW sizes (L=96,128,192 use seeds 101,202,303;
L=32,48,64 use EXP-0005 seed 42 to preserve the frozen measurement).
p-grid and fitting frozen from EXP-0005.

Reads parameters from CONFIG/prereg_EXP-0007.json (frozen before execution).
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
ENGINE = os.path.join(LAB, "04_SHARED_ENGINE")
sys.path.insert(0, ENGINE)
sys.path.insert(0, os.path.join(ENGINE, ".."))

from engine.utilities.core import rng, sha256_text, make_experiment_json  # noqa: E402
from engine.reproducibility.experiments import append_registry_row  # noqa: E402

QUESTION_ID = "Q-P004"
HYPOTHESIS_ID = "HYP-004"
EXP_ID = "EXP-0007"
PREREG_PATH = os.path.join(os.path.dirname(ROOT), "CONFIG", "prereg_EXP-0007.json")
EXP0005_RESULTS = os.path.join(ROOT, "RESULTS", "EXP-0005_results.json")

from scipy import stats as sstats  # noqa: E402
from scipy import optimize as sopt  # noqa: E402


def canonical_p(p: float) -> str:
    return f"{p:.17g}"


def cell_label(system: str, L: int, p: float) -> str:
    return f"perc-bond-wrap-exp0007:L{L}:p{canonical_p(p)}"


def interp_p50(ps, W):
    ps = np.asarray(ps, dtype=float)
    W = np.asarray(W, dtype=float)
    below = W < 0.5
    above = W > 0.5
    if not below.any() or not above.any():
        raise ValueError("p50 not bracketed")
    i = int(np.flatnonzero(below)[-1])
    j = int(np.flatnonzero(above)[0])
    if i >= j:
        raise ValueError("p50 grid ordering issue")
    p0, p1 = ps[i], ps[j]
    w0, w1 = W[i], W[j]
    return float(p0 + (0.5 - w0) * (p1 - p0) / (w1 - w0))


def _ufind_bond_wrap_cell(L: int, p: float, n_real: int, seed: int) -> dict:
    gen = rng(cell_label("bond_wrap", L, p), seed)
    total = n_real * 2 * L * L
    u = gen.random(total)
    S = 2 * L
    parent = list(range(L * S))
    size = [1] * (L * S)

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    k = 0
    for t in range(n_real):
        h = u[t * 2 * L * L:(t + 1) * 2 * L * L] < p
        hb = h[:L * L].reshape(L, L)
        vb = h[L * L:].reshape(L, L)
        parent[:] = list(range(L * S))
        size[:] = [1] * (L * S)
        idx = 0
        for r in range(L):
            base = r * S
            for c in range(S - 1):
                if hb[r, c % L]:
                    a, b = base + c, base + c + 1
                    ra, sna = find(a), find(b)
                    if ra != sna:
                        if size[ra] < size[sna]:
                            ra, sna = sna, ra
                        parent[sna] = ra
                        size[ra] += size[sna]
                idx += 1
        for r in range(L):
            rn = (r + 1) % L
            base = r * S
            for c in range(S):
                if vb[r, c % L]:
                    a, b = base + c, rn * S + c
                    ra, sna = find(a), find(b)
                    if ra != sna:
                        if size[ra] < size[sna]:
                            ra, sna = sna, ra
                        parent[sna] = ra
                        size[ra] += size[sna]
        wrapped = False
        for r in range(L):
            base = r * S
            for c in range(L):
                if find(base + c) == find(base + c + L):
                    wrapped = True
                    break
            if wrapped:
                break
        if wrapped:
            k += 1
    return {"k": k, "n": n_real}


def load_prereg_params(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def p_grids_for(system: str, L: int, params) -> list:
    cfg = params["parameters"]["systems"][system]
    return list(np.arange(0.38, 0.64, 0.02))


def run_cell(system: str, L: int, p: float, n_real: int, seed: int) -> dict:
    assert system == "bond_wrap"
    return _ufind_bond_wrap_cell(L, p, n_real, seed)


def bootstrap_p50(ps, ks, ns, draws=500, seed=42):
    gen = rng("perc-boot-exp0007", seed)
    ws = np.asarray(ks, dtype=float) / np.asarray(ns, dtype=float)
    ps = np.asarray(ps, dtype=float)
    out = []
    for _ in range(draws):
        kb = gen.binomial(np.asarray(ns, dtype=np.int64), ws)
        wb = kb / np.asarray(ns, dtype=float)
        try:
            out.append(interp_p50(ps, wb))
        except ValueError:
            continue
    if len(out) < 2:
        raise RuntimeError("bootstrap too degenerate")
    out = np.asarray(out)
    return float(out.mean()), float(out.std(ddof=1) if len(out) > 1 else 0.0), out


def fss_fit(Ls, p50s, ses, model="primary"):
    Ls = np.asarray(Ls, dtype=float)
    y = np.asarray(p50s, dtype=float)
    se = np.asarray(ses, dtype=float)
    if model == "primary":
        x = Ls ** (-3.0 / 4.0)
    elif model == "alt1":
        x = Ls ** (-1.0 / 1.35)
    else:
        x = np.log(Ls)
    w = 1.0 / se
    A = np.vstack([np.ones_like(x), x]).T
    W = np.diag(w)
    coef, *_ = np.linalg.lstsq(W @ A, W @ y, rcond=None)
    a, b = coef
    resid = y - (a + b * x)
    chi2 = float(np.sum((resid * w) ** 2))
    df = len(Ls) - 2
    chi2_red = chi2 / df if df > 0 else None
    cov = np.linalg.inv(A.T @ (W @ A))
    se_a = float(np.sqrt(cov[0, 0])) if len(Ls) > 2 else None
    return {"a": float(a), "se_a": se_a, "b": float(b), "chi2_red": chi2_red, "L_used": [int(li) for li in Ls], "model": model}


def fit_probit_width(ps, ks, ns, s0=0.05):
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

    res = sopt.minimize(nll, [mu0, np.log(s0)], method="L-BFGS-B", bounds=[(None, None), (-10, 10)])
    mu, s = res.x[0], float(np.exp(res.x[1]))
    return mu, s


def main():
    params = load_prereg_params(PREREG_PATH)
    sys_params = params["parameters"]
    tols = sys_params["tolerances"]

    # ---- Load EXP-0005 frozen bond_wrap cells for L=32,48,64 ----
    with open(EXP0005_RESULTS, encoding="utf-8") as fh:
        exp0005 = json.load(fh)
    exp0005_cells = exp0005["cells"]["bond_wrap"]
    frozen_Ls = {32, 48, 64}

    # ---- Run NEW cells at L=96,128,192 with independent seeds ----
    new_cells = []
    cfg = sys_params["systems"]["bond_wrap"]
    n_real_map = cfg["n_real"]
    seed_map = cfg["seed"]
    for L in cfg["L_list"]:
        if L in frozen_Ls:
            continue
        grid = p_grids_for("bond_wrap", L, params)
        n_real = int(n_real_map[str(L)])
        seed = int(seed_map[str(L)])
        for p in grid:
            pres = run_cell("bond_wrap", L, p, n_real, seed)
            new_cells.append({
                "system": "bond_wrap", "L": int(L), "p": float(p),
                "seed": seed, "n": pres["n"], "k": int(pres["k"]),
            })

    # ---- Combine frozen + new cells ----
    all_cells = {"bond_wrap": exp0005_cells + new_cells}

    # ---- Per-L p50, SE, width for ALL L ----
    Ls_all = sorted(set(c["L"] for c in all_cells["bond_wrap"]))
    p50_by_L = {}
    width_by_L = {}
    se_by_L = {}
    p50_ml_by_L = {}

    for L in Ls_all:
        Lcells = [c for c in all_cells["bond_wrap"] if c["L"] == L]
        ps = [c["p"] for c in Lcells]
        ks = [c["k"] for c in Lcells]
        ns = [c["n"] for c in Lcells]
        p50, se, boot = bootstrap_p50(ps, ks, ns, draws=500, seed=42)
        p50_ml, width_mle = fit_probit_width(ps, ks, ns, s0=0.05)
        p50_ml10, width_robust = fit_probit_width(ps, ks, ns, s0=0.10)
        p50_by_L[L] = p50
        se_by_L[L] = se
        width_by_L[L] = width_robust  # primary: sigma0=0.10 (robust)
        p50_ml_by_L[L] = {"s0_005": p50_ml, "s0_010": p50_ml10, "width_s0_005": width_mle, "width_s0_010": width_robust}

    # ---- FSS fits (multiple models) ----
    fss_models = {}
    for model_name, model_label in [("primary", "p50(L)=a+b*L^(-3/4)"), ("alt1", "p50(L)=a+b*L^(-1/nu), nu~1.35"), ("alt2", "log(p50)=c+d*log(L)")]:
        Ls_fit = [L for L in Ls_all if L in [32, 48, 64, 96, 128, 192]]
        p50s = [p50_by_L[L] for L in Ls_fit]
        ses = [se_by_L[L] for L in Ls_fit]
        fss_models[model_name] = fss_fit(Ls_fit, p50s, ses, model=model_name)

    # Primary model = primary FSS
    primary_fit = fss_models["primary"]

    # ---- Non-monotonicity test ----
    # EXP-0005 showed: L=32:0.49859, L=48:0.49748, L=64:0.50036 (non-monotonic)
    p50_series = {L: p50_by_L[L] for L in Ls_all}
    p50_vals = [p50_by_L[L] for L in Ls_all]
    # Check for local minima: p(L-1) > p(L) < p(L+1)
    local_minima = []
    for i in range(1, len(Ls_all) - 1):
        if p50_vals[i - 1] > p50_vals[i] and p50_vals[i] < p50_vals[i + 1]:
            local_minima.append({"L": Ls_all[i], "p50": p50_vals[i]})

    # ---- C4: scale stability (drop L in {32,48}) ----
    c4_Ls = [L for L in Ls_all if L not in [32, 48]]
    c4_p50s = [p50_by_L[L] for L in c4_Ls]
    c4_ses = [se_by_L[L] for L in c4_Ls]
    c4_fit = fss_fit(c4_Ls, c4_p50s, c4_ses, model="primary")
    c4_shift = abs(c4_fit["a"] - primary_fit["a"])

    # ---- C1 determinism (L=64, p=0.5, seed=42 from EXP-0005 frozen) ----
    c1_cell_cfg = sys_params["c1_cell"]
    c1_cfg = (c1_cell_cfg["L"], c1_cell_cfg["p"], c1_cell_cfg["seed"])
    c1_n = int(cfg["n_real"]["64"])
    r1 = run_cell("bond_wrap", c1_cfg[0], c1_cfg[1], c1_n, c1_cfg[2])
    r2 = run_cell("bond_wrap", c1_cfg[0], c1_cfg[1], c1_n, c1_cfg[2])
    c1 = {"cell": c1_cfg, "first": {"k": r1["k"], "n": r1["n"]}, "second": {"k": r2["k"], "n": r2["n"]}, "pass": r1["k"] == r2["k"]}

    # ---- C6 seed ladder (L=64, bond_wrap) ----
    c6_seed_data = []
    c6_p50s = {}
    c6_ses = {}
    sd = sys_params["seed_ladder_c6"]
    L6 = int(sd["L"])
    n6 = int(cfg["n_real"]["64"])
    grid6 = p_grids_for("bond_wrap", L6, params)
    for s in [42] + [int(x) for x in sd["extra_seeds"]]:
        k6 = [run_cell("bond_wrap", L6, p, n6, s)["k"] for p in grid6]
        ns6 = [n6] * len(grid6)
        p6, s6, _ = bootstrap_p50(grid6, k6, ns6, draws=200, seed=42)
        c6_p50s[str(s)] = p6
        c6_ses[str(s)] = s6
    max_dev = max(abs(c6_p50s[str(s)] - c6_p50s["42"]) for s in c6_p50s)
    joint_tol = 3.0 * np.hypot(c6_ses["42"], max(c6_ses.values()))
    c6 = {"L": L6, "seeds": [int(s) for s in c6_p50s], "primary_seed": 42, "primary_p50": c6_p50s["42"], "primary_se": c6_ses["42"], "p50_by_seed": c6_p50s, "se_by_seed": c6_ses, "max_abs_dev": float(max_dev), "joint_tolerance": float(joint_tol), "pass": max_dev < float(joint_tol)}

    # ---- C8 width-route ----
    logsL = np.log(np.asarray(Ls_all, dtype=float))
    widths = np.array([width_by_L[L] for L in Ls_all])
    logs = np.log(widths)
    slope, *_ = np.polyfit(logsL, logs, 1)
    inv_nu_width = float(-slope)
    nu_gate = sys_params["diagnostics"]["nu_gate"]
    c8 = {"inv_nu_width": inv_nu_width, "nu": float(1.0 / max(inv_nu_width, 1e-9)), "gate": [float(nu_gate[0]), float(nu_gate[1])], "pass": float(nu_gate[0]) <= inv_nu_width <= float(nu_gate[1])}

    # ---- Estimator comparison: s0=0.05 vs s0=0.10 ----
    width_s0_005 = []
    width_s0_010 = []
    for L in Ls_all:
        Lcells = [c for c in all_cells["bond_wrap"] if c["L"] == L]
        ps = [c["p"] for c in Lcells]
        ks = [c["k"] for c in Lcells]
        ns = [c["n"] for c in Lcells]
        _, w005 = fit_probit_width(ps, ks, ns, s0=0.05)
        _, w010 = fit_probit_width(ps, ks, ns, s0=0.10)
        width_s0_005.append(w005)
        width_s0_010.append(w010)
    width_s0_ratio = float(np.mean(np.array(width_s0_010) / np.array(width_s0_005)))
    c8_comparison = {"s0_005_widths": width_s0_005, "s0_010_widths": width_s0_010, "mean_ratio": width_s0_ratio, "note": "s0=0.10 primary; s0=0.05 comparison recorded per EXP-0006 proposal"}

    # ---- Decision ----
    anchors = {"bond_wrap": 0.5}
    ds = {s: abs(primary_fit["a"] - anchors[s]) for s in anchors}
    chi2_ok = (primary_fit["chi2_red"] or 0.0) < tols["chi2_red_gate"]
    gates = {"d_bond_wrap": ds["bond_wrap"], "tol_pc": tols["tol_pc"], "c1": c1["pass"], "c6": c6["pass"], "c4": c4_shift < tols["tol_c4_shift"], "c8": c8["pass"], "chi2_red_ok": chi2_ok, "FG": {"bond_wrap": primary_fit["chi2_red"]}, "in_tol": ds["bond_wrap"] <= tols["tol_pc"]}
    proc_broken = (not chi2_ok) or (not c1["pass"]) or (not c6["pass"]) or (not gates["c4"]) or (not c8["pass"])
    if proc_broken:
        decision = "INCONCLUSIVE"
        reason = "procedure suspect (fit-goodness / C1 / C6 / C4 / C8)"
    elif ds["bond_wrap"] <= tols["tol_pc"]:
        decision = "H0_SUPPORTED"
        reason = "all thresholds within 0.01 of anchor"
    else:
        decision = "ABNORMAL"
        reason = "gate(s) green but threshold outside tolerance"

    conclusion = ("Bond torus-wrap percolation p_c = 1/2 reproduced within tolerance through a controlled pipeline." if decision == "H0_SUPPORTED" else reason)

    results = {
        "experiment": EXP_ID, "question": QUESTION_ID, "hypothesis": HYPOTHESIS_ID,
        "decision": decision, "reason": reason, "conclusion_lab": conclusion,
        "prereg_sha256": sha256_text(open(PREREG_PATH, encoding="utf-8").read()),
        "p50": p50_series, "p50_with_meta": p50_ml_by_L,
        "se": se_by_L, "width": width_by_L, "fss": fss_models,
        "primary_fss": primary_fit, "non_monotonicity": {"p50_by_L": p50_series, "local_minima": local_minima, "L48_L64_from_EXP0005": {"L48": 0.4974828844043641, "L64": 0.5003630768139604, "delta": 0.5003630768139604 - 0.4974828844043641}, "test_question": "does the L48->L64 non-monotonicity continue at L=96,128,192?"},
        "c1": c1, "c6": c6, "c4": {"drop": [32, 48], "refit_a": c4_fit["a"], "full_a": primary_fit["a"], "shift": c4_shift, "pass": c4_shift < tols["tol_c4_shift"]},
        "c8": c8, "c8_comparison": c8_comparison,
        "gates": gates, "cells": all_cells,
        "data_sources": {"L_32_48_64": "EXP-0005 frozen (CODE/RESULTS/EXP-0005_results.json)", "L_96_128_192": "new runs, seeds 101/202/303"},
    }

    base = os.path.join(ROOT, "RESULTS")
    os.makedirs(base, exist_ok=True)
    res_path = os.path.join(base, f"{EXP_ID}_results.json")
    with open(res_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    exp_json = make_experiment_json(EXP_ID, QUESTION_ID, HYPOTHESIS_ID, 42, sys_params, results, out_path=os.path.join(ROOT, "CONFIG", f"{EXP_ID}_experiment.json"), extra={"prereg_path": f"CONFIG/prereg_{EXP_ID}.json"})
    append_registry_row(os.path.join(ROOT, "CONFIG", "registry.jsonl"), {"experiment_id": EXP_ID, "question": QUESTION_ID, "hypothesis": HYPOTHESIS_ID, "seed": 42, "decision": decision, "result_path": res_path})

    print(f"DECISION: {decision}  ({reason})")
    print(f"bond_wrap a={primary_fit['a']:.5f}  |d|={ds['bond_wrap']:.5f}")
    print(f"chi2_red={primary_fit['chi2_red']:.4f}  C1={c1['pass']}  C6={c6['pass']}  C4={c4_shift:.6f}  C8_1/nu={inv_nu_width:.4f}")
    print(f"p50 by L: {p50_series}")
    print(f"local minima: {local_minima}")
    print(f"L48->L64 delta from EXP-0005: {0.5003630768139604 - 0.4974828844043641:.6f}")
    print(f"Results -> {res_path}")


if __name__ == "__main__":
    main()
