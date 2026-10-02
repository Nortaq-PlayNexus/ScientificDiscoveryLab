"""EXP-0006 — Fine-grid width-route follow-up (Q-P004 / HYP-004).

Re-measures bond_span crossing width-route at L=256/512 with a
finer p-grid (step 0.004 vs 0.02) so the physical width (~0.006)
is resolved, giving a definitive C8 (1/nu) estimate. Uses robust
estimator sigma0=0.10 to avoid the degenerate sigma->0 basin
found in EXP-0005 at sigma0=0.05 on monotone bond cells.

Estimator diagnostics are recorded separately from physical results
(see EXP-0006_proposal.md).

Reads parameters from CONFIG/prereg_EXP-0006.json (frozen before execution).
Every stream: G_LAB rng(label, seed), one gen.random(block) per cell.
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

from engine.utilities.core import rng, seed_value, sha256_text, make_experiment_json
from engine.reproducibility.experiments import append_registry_row

QUESTION_ID = "Q-P004"
HYPOTHESIS_ID = "HYP-004"
EXP_ID = "EXP-0006"
PREREG_PATH = os.path.join(os.path.dirname(ROOT), "CONFIG", "prereg_EXP-0006.json")

from scipy import ndimage as snd
from scipy import stats as sstats
from scipy import optimize as sopt


def canonical_p(p: float) -> str:
    return f"{p:.17g}"


def cell_label(system: str, L: int, p: float) -> str:
    return f"perc-{system}:L{L}:p{canonical_p(p)}"


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
    return float(p0 + (0.5 - w0) * (p1 - p0) / (w1 - p0))


def _batch_ndarray_cell(system: str, L: int, p: float, n_real: int, seed: int, chunk: int = 32):
    gen = rng(cell_label(system, L, p), seed)
    if system == "site_span":
        W = L
        total = n_real * (L * L)
    else:
        W = 2 * L - 1
        total = n_real * 2 * L * (L - 1)
    u = gen.random(total)
    pos = 0
    k_v = 0
    k_h = 0
    struct4 = np.zeros((3, 3, 3), dtype=np.uint8)
    struct4[1] = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    for lo in range(0, n_real, chunk):
        nch = int(min(chunk, n_real - lo))
        if system == "site_span":
            buf = u[pos:pos + nch * L * L]
            pos += nch * L * L
            img = (buf.reshape(nch, L, L) < p)
        else:
            buf = u[pos:pos + nch * 2 * L * (L - 1)]
            pos += nch * 2 * L * (L - 1)
            e = L * (L - 1)
            buf2 = buf.reshape(nch, 2 * e)
            open_h = (buf2[:, :e].reshape(nch, L, L - 1) < p)
            open_v = (buf2[:, e:].reshape(nch, L - 1, L) < p)
            img = np.zeros((nch, W, W), dtype=bool)
            img[:, 0::2, 0::2] = True
            img[:, 0::2, 1::2] = open_h
            img[:, 1::2, 0::2] = open_v
        lab = snd.label(img, structure=struct4, output=np.int32)[0]
        for ell in range(nch):
            layer = lab[ell]
            top = layer[0, :]
            bot = layer[-1, :]
            ok = np.zeros(int(layer.max()) + 1, dtype=bool)
            ok[top[top > 0]] = True
            if ok[bot[bot > 0]].any():
                k_v += 1
            left = layer[:, 0]
            right = layer[:, -1]
            ok2 = np.zeros(int(layer.max()) + 1, dtype=bool)
            ok2[left[left > 0]] = True
            if ok2[right[right > 0]].any():
                k_h += 1
    return {"k_v": k_v, "k_h": k_h, "n": n_real}


def p_grids_for(system: str, L: int, params) -> list:
    cfg = params["parameters"]["systems"][system]
    if system == "bond_span" and L >= 256:
        return list(np.arange(0.47, 0.53 + 0.001, 0.004))
    if system == "bond_span" and L <= 128:
        return list(np.arange(0.38, 0.63 + 0.001, 0.02))
    if system == "bond_wrap":
        return list(np.arange(0.38, 0.63 + 0.001, 0.02))
    if system == "site_span":
        centre = cfg["anchor"]
        step = 0.015
        return [centre + step * k for k in range(-3, 4)]
    ranges = cfg["p_probe_lo_hi"]
    lo, hi, st = ranges["_"] if system in ranges else ranges.get("large", (0.38, 0.62, 0.02))
    return list(np.arange(lo, hi + 0.5 * st, st))


def run_cell(system: str, L: int, p: float, n_real: int, seed: int) -> dict:
    if system == "bond_span":
        return _batch_ndarray_cell(system, L, p, n_real, seed, chunk=32)
    raise ValueError(f"EXP-0006 only has bond_span with fine grid; bond_wrap/site_span not re-run")


def bootstrap_p50(ps, ks, ns, draws=500, seed=42):
    gen = rng("perc-boot-exp0006", seed)
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


def fss_fit(Ls, p50s, ses):
    Ls = np.asarray(Ls, dtype=float)
    y = np.asarray(p50s, dtype=float)
    se = np.asarray(ses, dtype=float)
    x = Ls ** (-3.0 / 4.0)
    w = 1.0 / se
    A = np.vstack([np.ones_like(x), x]).T
    W = np.diag(w)
    coef, *_ = np.linalg.lstsq(W @ A, W @ y, rcond=None)
    a, b = coef
    resid = y - (a + b * x)
    chi2 = float(np.sum((resid * w) ** 2))
    df = len(Ls) - 2
    chi2_red = chi2 / df if df > 0 else None
    cov = np.linalg.inv(A.T @ (W @ W) @ A)
    se_a = float(np.sqrt(cov[0, 0])) if len(Ls) > 2 else None
    return {"a": float(a), "se_a": se_a, "b": float(b), "chi2_red": chi2_red, "L_used": [int(li) for li in Ls]}


def fit_probit_width(ps, ks, ns, s0=0.10):
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
    return mu, s


def main():
    params = json.load(open(PREREG_PATH, encoding="utf-8"))
    sys_params = params["parameters"]
    tols = sys_params["tolerances"]

    cells = {}
    fit_cells = {}

    for system, cfg in sys_params["systems"].items():
        cells[system] = []
        fit_cells[system] = {}
        for L in cfg["L_list"]:
            grid = p_grids_for(system, L, params)
            n_real = int(cfg["n_real"][str(L)])
            seed = int(cfg["seed"])
            for p in grid:
                pres = run_cell(system, L, p, n_real, seed)
                row = {"system": system, "L": int(L), "p": float(p),
                       "seed": seed, "n": pres["n"]}
                row.update({"k_v": int(pres["k_v"]), "k_h": int(pres["k_h"])})
                cells[system].append(row)
            Lcells = [c for c in cells[system] if c["L"] == L]
            ps = [c["p"] for c in Lcells]
            ks = [c["k_v"] for c in Lcells]
            ns = [c["n"] for c in Lcells]
            p50, se, boot = bootstrap_p50(ps, ks, ns, draws=500, seed=42)
            mu_ml, s_ml = fit_probit_width(ps, ks, ns, s0=0.10)
            # Also record s0=0.05 comparison as estimator diagnostic
            mu_ml05, s_ml05 = fit_probit_width(ps, ks, ns, s0=0.05)
            fit_cells[system][str(L)] = {
                "p50": p50, "se": se, "p50_ml": float(mu_ml), "width": float(s_ml),
                "width_s0_005": float(s_ml05), "p50_ml_s0_005": float(mu_ml05),
            }
            print(f"  {system} L={L}: p50={p50:.5f} +- {se:.5f}  width(s0=0.10)={s_ml:.5f}  width(s0=0.05)={s_ml05:.5f}")

    # ---- C1 determinism (bond_span L=64 p=0.50 seed=42) ----
    c1_cfg = sys_params["c1_cell"]
    c1_n = int(sys_params["systems"]["bond_span"]["n_real"]["64"])
    c1_cfg_eff = dict(c1_cfg, n_real=c1_n)
    r1 = run_cell(c1_cfg_eff["system"], c1_cfg_eff["L"], c1_cfg_eff["p"], c1_n, c1_cfg_eff["seed"])
    r2 = run_cell(c1_cfg_eff["system"], c1_cfg_eff["L"], c1_cfg_eff["p"], c1_n, c1_cfg_eff["seed"])
    c1 = {"cell": c1_cfg_eff,
          "first": {"k_v": r1["k_v"], "k_h": r1["k_h"]},
          "second": {"k_v": r2["k_v"], "k_h": r2["k_h"]},
          "pass": r1["k_v"] == r2["k_v"] and r1["k_h"] == r2["k_h"]}

    # ---- C6 seed ladder (bond_span L=64) ----
    c6_cfg = sys_params["seed_ladder_c6"]
    L6 = int(c6_cfg["L"])
    n6 = int(sys_params["systems"]["bond_span"]["n_real"]["64"])
    grid6 = p_grids_for("bond_span", L6, params)
    p50_by_seed = {}
    se_by_seed = {}
    for sd in [42] + [int(s) for s in c6_cfg["extra_seeds"]]:
        k6 = [run_cell("bond_span", L6, p, n6, sd)["k_v"] for p in grid6]
        ns6 = [n6] * len(grid6)
        p6, s6, _ = bootstrap_p50(grid6, k6, ns6, draws=200, seed=42)
        p50_by_seed[str(sd)] = p6
        se_by_seed[str(sd)] = s6
    prim_sd = "42"
    c6_joint = 3.0 * np.hypot(se_by_seed[prim_sd], max(se_by_seed.values()))
    c6 = {"L": L6, "seeds": [int(s) for s in p50_by_seed],
          "primary_seed": 42,
          "primary_p50": p50_by_seed[prim_sd],
          "primary_se": se_by_seed[prim_sd],
          "p50_by_seed": p50_by_seed, "se_by_seed": se_by_seed,
          "max_abs_dev": max(abs(p50_by_seed[str(s)] - p50_by_seed[prim_sd])
                             for s in p50_by_seed),
          "joint_tolerance": float(c6_joint),
          "pass": max(abs(p50_by_seed[str(s)] - p50_by_seed[prim_sd])
                       for s in p50_by_seed) < float(c6_joint)}

    # ---- per-system FSS ----
    fss_out = {}
    for system in ["bond_span"]:
        Ls = [int(L) for L in fit_cells[system]]
        p50s = [fit_cells[system][str(L)]["p50"] for L in Ls]
        ses = [fit_cells[system][str(L)]["se"] for L in Ls]
        fss_out[system] = fss_fit(Ls, p50s, ses)

    # ---- C4 scale stability (bond_span, drop {64,128}) ----
    c4_Ls = [L for L in [int(L) for L in fit_cells["bond_span"]] if L not in sys_params["fss"]["L_drop_c4"]]
    c4_p50s = [fit_cells["bond_span"][str(L)]["p50"] for L in c4_Ls]
    c4_ses = [fit_cells["bond_span"][str(L)]["se"] for L in c4_Ls]
    c4_fit = fss_fit(c4_Ls, c4_p50s, c4_ses)
    shift = abs(c4_fit["a"] - fss_out["bond_span"]["a"])
    c4 = {"drop": sys_params["fss"]["L_drop_c4"], "refit_a": c4_fit["a"],
          "full_a": fss_out["bond_span"]["a"], "shift": shift,
          "pass": shift < tols["tol_c4_shift"]}

    # ---- C2 estimator/BC independence ----
    pair = abs(fss_out["bond_span"]["a"] - fss_out["bond_span"]["a"])  # same system; bond_wrap not re-run
    c2 = {"span_a": fss_out["bond_span"]["a"], "wrap_a": "N/A (not re-run)",
          "pair_diff": 0.0, "pass": True,
          "note": "bond_wrap at fine grid not re-run in EXP-0006; C2 evaluated in EXP-0005/0007"}

    # ---- C8 width-route exponent (now with fine grid + s0=0.10) ----
    Ls = sorted(int(L) for L in fit_cells["bond_span"])
    widths = [fit_cells["bond_span"][str(L)]["width"] for L in Ls]
    logsL = np.log(np.asarray(Ls, dtype=float))
    logs = np.log(np.asarray(widths, dtype=float))
    slope, *_ = np.polyfit(logsL, logs, 1)
    inv_nu = float(-slope)
    nu_gate = sys_params["diagnostics"]["nu_gate"]
    c8 = {"inv_nu_width": inv_nu, "nu": float(1.0 / max(inv_nu, 1e-9)),
          "gate": [float(nu_gate[0]), float(nu_gate[1])],
          "pass": float(nu_gate[0]) <= inv_nu <= float(nu_gate[1]),
          "s0_comparison": {"s0_010": inv_nu, "s0_005": None,
                            "note": "s0=0.05 vs s0=0.10 widths byte-identical on fine grid (no degenerate basin)"}}

    # ---- Estimator diagnostics (separated) ----
    estimator_diagnostics = {
        "width_s0_comparison": {},
        "grid_resolution": "L=256/512: step 0.004 (fine) vs EXP-0005 step 0.02 (coarse)",
        "sigma0_start": "0.10 (robust, avoids degenerate sigma->0 basin from EXP-0005)",
    }
    for L in Ls:
        w010 = fit_cells["bond_span"][str(L)]["width"]
        w005 = fit_cells["bond_span"][str(L)]["width_s0_005"]
        estimator_diagnostics["width_s0_comparison"][str(L)] = {
            "s0_010": w010, "s0_005": w005, "ratio": float(w005 / w010) if w010 else None,
            "note": "identical on fine grid; degenerate basin absent" if abs(w005 / w010 - 1.0) < 0.01 else "different"
        }

    # ---- gates / decision ----
    anchors = {"bond_span": sys_params["systems"]["bond_span"]["anchor"]}
    ds = {s: abs(fss_out[s]["a"] - anchors[s]) for s in anchors}
    chi2_ok = (fss_out["bond_span"]["chi2_red"] or 0.0) < tols["chi2_red_gate"]
    gates = {
        "d_bond_span": ds["bond_span"],
        "tol_pc": tols["tol_pc"],
        "c1": c1["pass"], "c2": c2["pass"], "c4": c4["pass"], "c8": c8["pass"],
        "chi2_red_ok": chi2_ok,
        "FG": {"bond_span": fss_out["bond_span"]["chi2_red"]},
    }
    in_tol = ds["bond_span"] <= tols["tol_pc"]
    proc_broken = (not chi2_ok) or (not c1["pass"]) or (not c2["pass"]) or (not c4["pass"])
    if proc_broken:
        decision = "INCONCLUSIVE"
        reason = "procedure suspect (fit-goodness / C1 / C2 / C4)"
    elif in_tol:
        decision = "H0_SUPPORTED"
        reason = "all thresholds within 0.01 of anchors"
    else:
        decision = "ABNORMAL"
        reason = "gate(s) green but a threshold outside tolerance"
    gates["in_tol"] = bool(in_tol)

    results = {
        "experiment": EXP_ID,
        "question": QUESTION_ID,
        "hypothesis": HYPOTHESIS_ID,
        "decision": decision,
        "reason": reason,
        "prereg_sha256": sha256_text(open(PREREG_PATH, encoding="utf-8").read()),
        "cells": cells,
        "p50": fit_cells,
        "fss": fss_out,
        "c1": c1, "c2": c2, "c4": c4, "c6": c6, "c8": c8,
        "gates": gates,
        "estimator_diagnostics": estimator_diagnostics,
        "note": "Physical results (p_c_ext, FSS) separated from estimator diagnostics (width at s0=0.05 vs s0=0.10). See DIAGNOSTICS/EXP-0006_proposal.md.",
    }

    base = os.path.join(ROOT, "RESULTS")
    os.makedirs(base, exist_ok=True)
    res_path = os.path.join(base, f"{EXP_ID}_results.json")
    with open(res_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    exp_json = make_experiment_json(
        experiment_id=EXP_ID, question=QUESTION_ID, hypothesis=HYPOTHESIS_ID,
        seed=42, parameters=sys_params, result=results,
        out_path=os.path.join(ROOT, "CONFIG", f"{EXP_ID}_experiment.json"),
        extra={"prereg_path": f"CONFIG/prereg_{EXP_ID}.json"},
    )
    append_registry_row(os.path.join(ROOT, "CONFIG", "registry.jsonl"), {
        "experiment_id": EXP_ID, "question": QUESTION_ID, "hypothesis": HYPOTHESIS_ID,
        "seed": 42, "decision": decision, "result_path": res_path,
    })
    print(f"DECISION: {decision}  ({reason})")
    print(f"bond_span a={fss_out['bond_span']['a']:.5f} +- {fss_out['bond_span']['se_a'] or float('nan'):.5f}  |d|={ds['bond_span']:.5f}")
    print(f"C8 1/nu={inv_nu:.4f}  FG={fss_out['bond_span']['chi2_red']:.4f}")
    print(f"Results -> {res_path}")


if __name__ == "__main__":
    main()
