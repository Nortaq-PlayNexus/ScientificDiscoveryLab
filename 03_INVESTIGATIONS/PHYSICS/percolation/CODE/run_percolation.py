"""EXP-0005 - Percolation thresholds (Q-P004 / HYP-004).

Controlled Monte Carlo reproduction of square-lattice percolation thresholds:
  - bond_span (PRIMARY): vertical spanning on open L x L (scipy.ndimage batched,
    expanded-site encoding for bond percolation);
  - bond_wrap (SECONDARY): torus horizontal wrap on the universal-cover strip with
    toroidal rows (pure-Python union-find);
  - site_span (calibration anchor): vertical spanning on open L x L site
    percolation (scipy.ndimage batched).

Decision rule, grids, tolerances, fits: CONFIG/prereg_EXP-0005.json (frozen).
Every stream: G_LAB rng(label, seed) with label "perc-<system>:L<L>:p<canonical>",
one gen.random(block) per cell so REAPPLICATION/independent_check.py can reproduce
the identical draws. Emulates EXP-0004's transparent flow.
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

from engine.utilities.core import rng, seed_value, sha256_text  # noqa: E402
from engine.reproducibility.experiments import append_registry_row  # noqa: E402
from engine.utilities.core import make_experiment_json  # noqa: E402

QUESTION_ID = "Q-P004"
HYPOTHESIS_ID = "HYP-004"
EXP_ID = "EXP-0005"
PREREG_PATH = os.path.join(os.path.dirname(ROOT), "CONFIG", "prereg_EXP-0005.json")

from scipy import ndimage as snd  # noqa: E402
from scipy import stats as sstats  # noqa: E402
from scipy import optimize as sopt  # noqa: E402


def canonical_p(p: float) -> str:
    return f"{p:.17g}"


def cell_label(system: str, L: int, p: float) -> str:
    return f"perc-{system}:L{L}:p{canonical_p(p)}"


def interp_p50(ps, W):
    """Root of W(p)=0.5 by linear interpolation of bracketing points."""
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


# ----------------------------------------------------------------------------
# Estimator 1: scipy.ndimage batched spanning (open BC), bond via site-encoding
# ----------------------------------------------------------------------------

def _batch_ndarray_cell(system: str, L: int, p: float, n_real: int, seed: int, chunk: int = 32):
    """Generate and count vertical (+horizontal) spanning across n_real layers.

    bond: sites pixelated onto a (2L-1)x(2L-1) image (odd-odd pixels background),
          sites fixed open, bonds drawn U<p. site: LxL bool image of open sites.
    Returns dict(k_v, k_h, n).
    """
    gen = rng(cell_label(system, L, p), seed)
    if system == "site_span":
        W = L
        total = n_real * (L * L)
    else:  # bond_span
        W = 2 * L - 1
        total = n_real * 2 * L * (L - 1)  # h-edges L*(L-1) + v-edges L*(L-1)
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
            # layout: per layer interleaved [h_edges(L*(L-1)); v_edges(L*(L-1))]
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


# ----------------------------------------------------------------------------
# Estimator 2: pure-Python torus wrap on the universal-cover strip (toroidal rows)
# ----------------------------------------------------------------------------

def _ufind_bond_wrap_cell(L: int, p: float, n_real: int, seed: int) -> dict:
    """Horizontal wrap on the Lx(2L) strip (columns L..2L-1 = periodicates of 0..L-1),
    rows toroidal (L-1 -> 0). Break model exactly the torus bond config."""
    gen = rng(cell_label("bond_wrap", L, p), seed)
    total = n_real * 2 * L * L  # h-states L*L, v-states L*L
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
        # horizontal edges c=0..2L-2 ; state (r, c % L)
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
        # vertical edges, row-wrap
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
        # wrap check: find(r,c) == find(r,c+L) for any c<L
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


# ----------------------------------------------------------------------------
# Monte Carlo: full cell grids
# ----------------------------------------------------------------------------

def load_prereg_params(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def p_grids_for(system: str, L: int, params) -> list:
    cfg = params["parameters"]["systems"][system]
    if system == "bond_wrap":
        return list(np.arange(0.38, 0.64, 0.02))
    if system == "site_span":
        centre = cfg["anchor"]
        step = 0.015
        return [centre + step * k for k in range(-3, 4)]
    ranges = cfg["p_probe_lo_hi"]
    if system == "bond_span" and L <= 128:
        lo, hi, st = ranges["_"]
    else:
        lo, hi, st = ranges["large"]
    return list(np.arange(lo, hi + 0.5 * st, st))


def run_cell(system: str, L: int, p: float, n_real: int, seed: int) -> dict:
    if system == "bond_wrap":
        return _ufind_bond_wrap_cell(L, p, n_real, seed)
    return _batch_ndarray_cell(system, L, p, n_real, seed, chunk=32)


# ----------------------------------------------------------------------------
# Fitting
# ----------------------------------------------------------------------------

def bootstrap_p50(ps, ks, ns, draws=500, seed=42):
    gen = rng("perc-boot", seed)
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
    """WLS p50(L) = a + b L^(-3/4). Returns (a, se_a, b, chi2_red, L_used)."""
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
    # se of a via covariance
    cov = np.linalg.inv(A.T @ (W @ A))
    se_a = float(np.sqrt(cov[0, 0])) if len(Ls) > 2 else None
    return {"a": float(a), "se_a": se_a, "b": float(b), "chi2_red": chi2_red, "L_used": [int(li) for li in Ls]}


def fit_probit_width(ps, ks, ns):
    ps = np.asarray(ps, dtype=float)
    k = np.asarray(ks, dtype=np.int64)
    n = np.asarray(ns, dtype=np.int64)
    W = k / n
    try:
        mu0 = interp_p50(ps, W)
    except ValueError:
        mu0 = float(np.median(ps))
    s0 = 0.05

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


# ----------------------------------------------------------------------------
# Planning checks (run before the frozen run; throwaway, not reported as results)
# ----------------------------------------------------------------------------

def planning_checks():
    checks = []
    # 2x2 torus, all bonds open -> wrap True
    k = _ufind_bond_wrap_cell(2, 1.0, 1, 42)
    checks.append(("wrap_2x2_all_open_true", k["k"] == 1))
    # 2x2 torus, no bonds -> wrap False
    k0 = _ufind_bond_wrap_cell(2, 0.0, 1, 42)
    checks.append(("wrap_2x2_none_false", k0["k"] == 0))
    # site_span L=4 p=0 -> no span; p=1 -> span
    c0 = _batch_ndarray_cell("site_span", 4, 0.0, 8, 42)
    c1 = _batch_ndarray_cell("site_span", 4, 1.0, 8, 42)
    checks.append(("site_p0_none", c0["k_v"] == 0))
    checks.append(("site_p1_all", c1["k_v"] == c1["n"]))
    # bond_span L=4 p=0 -> no span, p=1 -> all span (flood connects everything)
    b0 = _batch_ndarray_cell("bond_span", 4, 0.0, 8, 42)
    b1 = _batch_ndarray_cell("bond_span", 4, 1.0, 8, 42)
    checks.append(("bond_p0_none", b0["k_v"] == 0))
    checks.append(("bond_p1_all", b1["k_v"] == b1["n"]))
    bad = [name for name, ok in checks if not ok]
    return {"passed": not bad, "checks": dict(checks), "failures": bad}


def main():
    params = load_prereg_params(PREREG_PATH)
    sys_params = params["parameters"]
    tols = sys_params["tolerances"]

    pc = planning_checks()
    if not pc["passed"]:
        print("PLANNING CHECKS FAILED:", pc)
        sys.exit(1)
    print("Planning checks: OK")

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
                if system == "bond_wrap":
                    row.update({"k": int(pres["k"])})
                elif system == "site_span":
                    row.update({"k_v": int(pres["k_v"]), "k_h": int(pres["k_h"])})
                else:
                    row.update({"k_v": int(pres["k_v"]), "k_h": int(pres["k_h"])})
                cells[system].append(row)
            # whittle down to per-L p50
            Lcells = [c for c in cells[system] if c["L"] == L]
            ps = [c["p"] for c in Lcells]
            if system == "bond_wrap":
                ks = [c["k"] for c in Lcells]
            else:
                ks = [c["k_v"] for c in Lcells]
            ns = [c["n"] for c in Lcells]
            p50, se, boot = bootstrap_p50(ps, ks, ns, draws=500, seed=42)
            mu_ml, s_ml = fit_probit_width(ps, ks, ns)
            fit_cells[system][str(L)] = {
                "p50": p50, "se": se, "p50_ml": float(mu_ml), "width": float(s_ml),
            }
            print(f"  {system} L={L}: p50={p50:.5f} +- {se:.5f}  width={s_ml:.5f}")

    # ---- C1 determinism (bond_span L=64 p=0.50 seed=42; n_real from frozen L=64) ----
    c1_cfg = dict(sys_params["c1_cell"])
    c1_n = int(sys_params["systems"]["bond_span"]["n_real"]["64"])
    c1_cfg["n_real"] = c1_n
    r1 = run_cell(**c1_cfg)
    r2 = run_cell(**c1_cfg)
    c1 = {"cell": c1_cfg,
          "first": {"k_v": r1["k_v"], "k_h": r1["k_h"]},
          "second": {"k_v": r2["k_v"], "k_h": r2["k_h"]},
          "pass": r1["k_v"] == r2["k_v"] and r1["k_h"] == r2["k_h"]}

# ---- C6 seed ladder (bond_span L=64) ----
    c6_cfg = sys_params["seed_ladder_c6"]
    L6 = int(c6_cfg["L"])
    n6 = int(sys_params["systems"]["bond_span"]["n_real"][str(L6)])
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
    for system in ["bond_span", "bond_wrap", "site_span"]:
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
    pair = abs(fss_out["bond_span"]["a"] - fss_out["bond_wrap"]["a"])
    c2 = {"span_a": fss_out["bond_span"]["a"], "wrap_a": fss_out["bond_wrap"]["a"],
          "pair_diff": pair, "pass": pair < tols["tol_estimator_pair"]}

    # ---- C8 width-route exponent ----
    Ls = sorted(int(L) for L in fit_cells["bond_span"])
    widths = [fit_cells["bond_span"][str(L)]["width"] for L in Ls]
    logsL = np.log(np.asarray(Ls, dtype=float))
    logs = np.log(np.asarray(widths, dtype=float))
    slope, *_ = np.polyfit(logsL, logs, 1)
    inv_nu = float(-slope)
    nu_gate = sys_params["diagnostics"]["nu_gate"]
    c8 = {"inv_nu_width": inv_nu, "nu": float(1.0 / max(inv_nu, 1e-9)),
          "gate": [float(nu_gate[0]), float(nu_gate[1])],
          "pass": float(nu_gate[0]) <= inv_nu <= float(nu_gate[1])}

    # ---- gates / decision ----
    anchors = {"bond_span": sys_params["systems"]["bond_span"]["anchor"],
               "bond_wrap": sys_params["systems"]["bond_wrap"]["anchor"],
               "site_span": sys_params["systems"]["site_span"]["anchor"]}
    ds = {s: abs(fss_out[s]["a"] - anchors[s]) for s in anchors}
    chi2_ok = all((fss_out[s]["chi2_red"] or 0.0) < tols["chi2_red_gate"] for s in anchors)
    gates = {
        "d_bond_span": ds["bond_span"], "d_bond_wrap": ds["bond_wrap"],
        "d_site_span": ds["site_span"],
        "tol_pc": tols["tol_pc"],
        "c1": c1["pass"], "c2": c2["pass"], "c4": c4["pass"], "c8": c8["pass"],
        "chi2_red_ok": chi2_ok,
        "FG": {"bond_span": fss_out["bond_span"]["chi2_red"],
               "bond_wrap": fss_out["bond_wrap"]["chi2_red"],
               "site_span": fss_out["site_span"]["chi2_red"]},
    }
    in_tol = all(dx <= tols["tol_pc"] for dx in [gates["d_bond_span"], gates["d_bond_wrap"], gates["d_site_span"]])
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

    # ---- corroboration: horizontal spanning p50 at L=512 ----
    L512 = 512
    hcells = [c for c in cells["bond_span"] if c["L"] == L512]
    p50_h, se_h, _ = bootstrap_p50([c["p"] for c in hcells],
                                   [c["k_h"] for c in hcells],
                                   [c["n"] for c in hcells], draws=200, seed=42)
    corr = {"horizontal_span_p50_L512": p50_h, "se": se_h,
            "within_0.02": bool(abs(p50_h - 0.5) <= 0.02),
            "note": "independent estimator corroboration only; NOT a gate"}

    conclusion = ("Bond square-lattice percolation p_c = 1/2 (and site p_c ~= "
                  "0.59274605) reproduced within tolerance through a controlled "
                  "pipeline." if decision == "H0_SUPPORTED" else reason)

    results = {
        "experiment": EXP_ID,
        "question": QUESTION_ID,
        "hypothesis": HYPOTHESIS_ID,
        "decision": decision,
        "reason": reason,
        "conclusion_lab": conclusion,
        "prereg_sha256": sha256_text(open(PREREG_PATH, encoding="utf-8").read()),
        "planning_checks": pc,
        "cells": cells,
        "p50": fit_cells,
        "fss": fss_out,
        "c1": c1, "c2": c2, "c4": c4, "c6": c6, "c8": c8, "gates": gates,
        "corroboration": corr,
    }

    # ---- persistence ----
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
    print(f"bond_span a={fss_out['bond_span']['a']:.5f} +- {fss_out['bond_span']['se_a'] or float('nan'):.5f}  "
          f"|d|= {ds['bond_span']:.5f}")
    print(f"bond_wrap a={fss_out['bond_wrap']['a']:.5f}  |d|= {ds['bond_wrap']:.5f}")
    print(f"site_span a={fss_out['site_span']['a']:.5f}  |d|= {ds['site_span']:.5f}")
    print(f"C4 shift={shift:.5f}  C2 pair_diff={pair:.5f}  1/nu={inv_nu:.4f}")
    print("Results ->", res_path)


if __name__ == "__main__":
    main()