"""Q-P008 runner — 3D site percolation critical exponents at p_c ≈ 0.3116."""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
QDIR = os.path.dirname(HERE)
PHYSICS = os.path.dirname(QDIR)
PERC = os.path.join(PHYSICS, "percolation")
ENGINE = os.path.join(PERC, "ENGINE")
if ENGINE not in sys.path: sys.path.insert(0, ENGINE)

import perc_engine as pe

QP005_CODE = os.path.join(PERC, "Q-P005_exponents", "CODE")
if QP005_CODE not in sys.path: sys.path.insert(0, QP005_CODE)
from run_exp0009 import bootstrap_slope, fit_tau_cumulative

PREC_PATHS = [
    os.path.join(QDIR, "CONFIG", "prereg_EXP-0013.json"),
    os.path.join(QDIR, "CONFIG", "prereg_EXP-0011.json"),
]
FORCE_PILOT = os.environ.get("QP008_PILOT", "").lower() in ("1", "true", "yes")
PREC = None
for pp in PREC_PATHS:
    if os.path.exists(pp):
        PREC = json.load(open(pp, encoding="utf-8"))
        break
if PREC is None:
    raise FileNotFoundError("No prereg found")
if FORCE_PILOT:
    pilot_path = os.path.join(QDIR, "CONFIG", "prereg_EXP-0011.json")
    if os.path.exists(pilot_path):
        PREC = json.load(open(pilot_path, encoding="utf-8"))
        print("[Q-P008] PILOT MODE: using EXP-0011 config", flush=True)
SEED = PREC["seed"]
P_C = PREC["parameters"]["p_c"]
L_LIST = PREC["parameters"]["L_list"]
N_REAL = {int(k): int(v) for k, v in PREC["parameters"]["n_real"].items()}
BS_DRAWS = PREC["parameters"]["bootstrap_draws"]
EXP_ID = PREC["experiment_id"]
PCAN = PREC["p_canon_token"]

WIDTH_GRID = PREC["parameters"]["width_grid"]
WIDTH_L_LIST = PREC["parameters"]["width_L_list"]


def cell_label(L, kind, seed):
    return PREC["rng_label_pattern"].replace("<L>", str(L)).replace("<pcanon>", PCAN).replace("<kind>", kind)


def width_curve_L(L, p_grid, n_each, seed_base):
    src, dst, N = pe.cubic_lattice_3d(L)
    ws = []
    for i, p in enumerate(p_grid):
        seed_i = seed_base + i * 31
        lab = cell_label(L, "width", seed_i)
        o = pe.run_span_cell_edges(src, dst, N, L, p, max(4, n_each // 10), seed_i, lab,
                                   semantics="site", want_stats=True)
        P_span = o["k_v"] / o["n"]
        ws.append(P_span)
    return np.array(ws)


def measure_p_c_width(L, seed_base):
    key = f"L{L}"
    if key not in WIDTH_GRID:
        print(f"  WARNING: no width_grid entry for {key}", flush=True)
        return None, 0
    grid_info = WIDTH_GRID[key]
    lo, hi, step = grid_info["grid"]
    n_each = grid_info["n_each"]
    n_pts = int(round((hi - lo) / step)) + 1
    p_grid = np.linspace(lo, hi, n_pts)
    ws = width_curve_L(L, p_grid, n_each, seed_base)
    try:
        i_below = int(np.flatnonzero(ws < 0.5)[-1])
        i_above = int(np.flatnonzero(ws >= 0.5)[0])
        p0, p1 = p_grid[i_below], p_grid[i_above]
        w0, w1 = ws[i_below], ws[i_above]
        p_c = float(p0 + (0.5 - w0) * (p1 - p0) / (w1 - w0))
        return p_c, n_pts
    except (IndexError, ValueError):
        i_closest = int(np.argmin(np.abs(ws - 0.5)))
        return float(p_grid[i_closest]), n_pts


def main():
    t_start = time.time()
    print("[Q-P008] 3D site percolation critical exponents", flush=True)
    print(f"[Q-P008] p_c_canon = {P_C:.7f}", flush=True)
    print(f"[Q-P008] L_list = {L_LIST}", flush=True)

    print("[Q-P008] Phase 1: Width curves + p_c at each L", flush=True)
    p_c_measures = {}
    p_c_sig = {}
    for L in L_LIST:
        print(f"  L={L}: measuring width curve...", flush=True)
        p_c, n_pts = measure_p_c_width(L, SEED + L * 1000)
        if p_c is not None:
            p_c_measures[L] = p_c
            print(f"  L={L}: p_c = {p_c:.8f}", flush=True)
        else:
            print(f"  L={L}: FAILED to find crossing", flush=True)

    if len(p_c_measures) >= 2:
        Ls_arr = np.array(list(p_c_measures.keys()), dtype=float)
        pcs_arr = np.array(list(p_c_measures.values()))
        inv_L = 1.0 / Ls_arr
        slope, intercept = np.polyfit(inv_L, pcs_arr, 1)
        p_c_inf = float(intercept)
        print(f"  p_c(L->inf) = {p_c_inf:.8f}", flush=True)
    elif len(p_c_measures) == 1:
        p_c_inf = list(p_c_measures.values())[0]
        print(f"  p_c(L->inf) ≈ {p_c_inf:.8f} (single L, no extrapolation)", flush=True)
    else:
        p_c_inf = P_C
        print(f"  p_c(L->inf) = {P_C:.8f} (using canon, all measurements failed)", flush=True)

    phase1 = {
        "width_curves": {str(Lk): {"p_c": p_c_measures.get(Lk, None)} for Lk in L_LIST},
        "p_c_extrapolation": {
            "method": "linear_fit_1_over_L",
            "p_c_inf": p_c_inf,
            "p_c_ziff": P_C,
            "abs_dev": abs(p_c_inf - P_C) if len(p_c_measures) >= 2 else None,
        },
    }

    print("[Q-P008] Phase 2: Exponent measurement at p_c", flush=True)
    P_C_REF = P_C
    p_c_note = "width curves at L in {8,16,24} converge slowly from above; using canon p_c for exponent measurement"
    print("  Using p_c = " + str(P_C_REF) + " (canon; width curves diagnostic only)", flush=True)

    cells = {}
    for L in L_LIST:
        n = N_REAL[L]
        src, dst, N = pe.cubic_lattice_3d(L)
        print(f"  L={L} n={n}: running cells at p_c={P_C_REF:.12f}", flush=True)

        masses_list, chis_list, pinfs_list, sizes_list = [], [], [], []
        for i in range(n):
            seed_i = SEED + i * 13 + L * 37
            lab = cell_label(L, "exp", seed_i)
            o = pe.run_span_cell_edges(src, dst, N, L, P_C_REF, 1, seed_i, lab,
                                       semantics="site",
                                       want_largest_mass=True,
                                       want_stats=True,
                                       want_cluster_sizes=True)
            m_arr = np.asarray(o["masses"], dtype=np.float64)
            cl_sizes = o.get("cluster_sizes", [])
            c_arr = np.array([float((np.asarray(ss, dtype=np.float64)**2).sum() / np.asarray(ss, dtype=np.float64).sum()) if len(ss) > 0 else 0.0 for ss in cl_sizes])
            p_arr = m_arr / float(N)
            masses_list.append(m_arr)
            chis_list.append(c_arr)
            pinfs_list.append(p_arr)
            sizes_list.append(cl_sizes)

        masses = np.concatenate(masses_list) if masses_list else np.array([0])
        chis = np.concatenate(chis_list) if chis_list else np.array([0])
        pinfs = np.concatenate(pinfs_list) if pinfs_list else np.array([0])

        cells[L] = {"masses": masses, "chis": chis, "pinfs": pinfs, "sizes": sizes_list}
        print(f"  L={L} done (n_cells={n})", flush=True)

    logx = np.log(np.asarray(L_LIST, dtype=float))
    min_n = min(len(cells[L]["masses"]) for L in L_LIST)
    mmat_a = np.array([cells[L]["masses"][:min_n] for L in L_LIST])
    cmat_a = np.array([cells[L]["chis"][:min_n] for L in L_LIST])
    pmat_a = np.array([cells[L]["pinfs"][:min_n] for L in L_LIST])

    Df = bootstrap_slope(logx, mmat_a, BS_DRAWS, f"{EXP_ID}-df", SEED)
    Gf = bootstrap_slope(logx, cmat_a, BS_DRAWS, f"{EXP_ID}-gn", SEED)
    Bf = -bootstrap_slope(logx, pmat_a, BS_DRAWS, f"{EXP_ID}-bn", SEED)

    Df_m, Df_se = float(Df.mean()), float(Df.std(ddof=1))
    Gf_m, Gf_se = float(Gf.mean()), float(Gf.std(ddof=1))
    Bf_m, Bf_se = float(Bf.mean()), float(Bf.std(ddof=1))

    print(f"[Q-P008] Df={Df_m:.5f}+-{Df_se:.5f} Gn={Gf_m:.5f}+-{Gf_se:.5f} Bn={Bf_m:.5f}+-{Bf_se:.5f}", flush=True)

    tL = 24
    tsizes = [ss[1:] for ss in cells[tL]["sizes"]]
    tc = fit_tau_cumulative(tsizes, 4, 1000, f"{EXP_ID}-tau", SEED)
    tau_m = tc["tau_cum"] if tc is not None else None
    boot_se = tc.get("boot_se", 0) if tc is not None else None
    chi2_red = tc.get("chi2_red", None) if tc is not None else None
    print(f"[Q-P008] tau={'N/A' if tau_m is None else f'{tau_m:.5f}'} (exp 2.19)", flush=True)

    results = {
        "experiment": EXP_ID, "L_list": L_LIST, "n_real": N_REAL,
        "p_c_ziff": P_C, "p_c_refined": p_c_inf,
        "p_c_canon_used": True,
        "p_c_note": p_c_note,
        "p_c_measures": {str(k): v for k, v in p_c_measures.items()},
        "bootstrap_draws": BS_DRAWS,
        "exponents": {
            "Df": {"mean": Df_m, "se": Df_se, "expected": 2.53, "tol": 0.10},
            "gamma_nu": {"mean": Gf_m, "se": Gf_se, "expected": 1.40, "tol": 0.08},
            "beta_nu": {"mean": Bf_m, "se": Bf_se, "expected": 0.41, "tol": 0.05},
        },
        "tau": {"mean": tau_m, "se": boot_se, "expected": 2.19, "tol": 0.10, "fit_range": [4, 1000], "tau_L": tL},
        "tau_cum_chi2_red": chi2_red,
        "elapsed": time.time() - t_start,
    }

    os.makedirs(os.path.join(QDIR, "CODE", "RESULTS"), exist_ok=True)
    out = os.path.join(QDIR, "CODE", "RESULTS", f"{EXP_ID}_results.json")
    with open(out, "w") as f: json.dump(results, f, indent=2)

    combined = {**phase1, "phase2_results": results}
    with open(os.path.join(QDIR, "CODE", "RESULTS", f"{EXP_ID}_combined.json"), "w") as f:
        json.dump(combined, f, indent=2)

    print(f"[Q-P008] DONE in {time.time()-t_start:.0f}s. Saved: {out}", flush=True)


if __name__ == "__main__":
    main()
