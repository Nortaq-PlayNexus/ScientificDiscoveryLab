"""Q-P007 Phase 2 runner — completes from frozen checkpoint."""
import json, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
QDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(QDIR)
ENGINE = os.path.join(ROOT, "ENGINE")
if ENGINE not in sys.path: sys.path.insert(0, ENGINE)

import perc_engine as pe

QP005_CODE = os.path.join(ROOT, "Q-P005_exponents", "CODE")
if QP005_CODE not in sys.path: sys.path.insert(0, QP005_CODE)
from run_exp0009 import (run_exponent_cell, save_cell, load_cell,
                              bootstrap_slope, fit_tau_cumulative,
                              fit_tau_histogram, probit_width, cell_label)

PREC = json.load(open(os.path.join(QDIR, "CONFIG", "prereg_EXP-0009PC.json"), encoding="utf-8"))
SEED = PREC["seed"]
BS = PREC["parameters"]["bootstrap_label"]
L_LIST = PREC["parameters"]["L_list"]
N_REAL = {int(k): int(v) for k, v in PREC["parameters"]["n_real"].items()}
BS_DRAWS = PREC["parameters"]["bootstrap_draws"]
TAU_RANGE = PREC["parameters"]["tau_fit_range"]
TAU_L = PREC["parameters"]["tau_L"]
P_C = PREC["parameters"]["p_c"]
EXP_ID = PREC["experiment_id"]


def cell_label_p(L, kind, seed):
    return PREC["rng_label_pattern"].replace("<L>", str(L)).replace("<pcanon>", PREC["p_canon_token"]).replace("<kind>", kind)


def cell_npz_path(L):
    return os.path.join(QDIR, "CODE", "RESULTS", f"{EXP_ID}_L{L}_cells.npz")


def save_cell_data(L, masses, chis, pinfs, sizes_list):
    os.makedirs(os.path.join(QDIR, "CODE", "RESULTS"), exist_ok=True)
    sizes_n = [len(s) for s in sizes_list]
    sizes_n_total = [int(np.sum(s)) for s in sizes_list]
    np.savez(cell_npz_path(L),
             masses=masses, chis=chis, pinfs=pinfs,
             sizes_n=np.array(sizes_n, dtype=np.int64),
             sizes_n_total=np.array(sizes_n_total, dtype=np.int64))


def load_cell_data(L):
    p = cell_npz_path(L)
    if not os.path.exists(p):
        return None
    z = np.load(p, allow_pickle=True)
    return {"masses": z["masses"], "chis": z["chis"], "pinfs": z["pinfs"],
            "sizes_n": z["sizes_n"], "sizes_n_total": z["sizes_n_total"]}


def main():
    t_start = time.time()

    p_c_measures = {512: 0.592883, 1024: 0.592673, 2048: 0.592834}
    p_c_sig = {512: 0.004519, 1024: 0.003031, 2048: 0.001828}
    print("[Q-P007] Phase 1 (preserved from run.log):", flush=True)
    for Lk in [512, 1024, 2048]:
        print(f"  L={Lk}: p_c={p_c_measures[Lk]:.6f} +/- {p_c_sig[Lk]:.6f}", flush=True)

    Ls_arr = np.array(list(p_c_measures.keys()), dtype=float)
    pcs_arr = np.array(list(p_c_measures.values()))
    inv_L = 1.0 / Ls_arr
    slope, intercept = np.polyfit(inv_L, pcs_arr, 1)
    p_c_inf = float(intercept)
    print(f"  p_c(L->inf) = {p_c_inf:.8f} (Ziff: {P_C:.8f})", flush=True)
    print(f"  |dev| from Ziff = {abs(p_c_inf - P_C):.8f}", flush=True)

    phase1 = {
        "width_curves": {str(Lk): {"mu": p_c_measures[Lk], "sigma": p_c_sig[Lk]} for Lk in p_c_measures},
        "p_c_extrapolation": {"method": "linear_fit_1_over_L", "p_c_inf": p_c_inf, "p_c_ziff": P_C, "abs_dev": abs(p_c_inf - P_C)},
    }
    os.makedirs(os.path.join(QDIR, "CODE", "RESULTS"), exist_ok=True)
    with open(os.path.join(QDIR, "CODE", "RESULTS", f"{EXP_ID}_phase1.json"), "w") as f:
        json.dump(phase1, f, indent=2)
    print("[Q-P007] Phase 1 results saved.", flush=True)

    print("[Q-P007] Phase 2: Exponent measurement at refined p_c", flush=True)
    P_C_REF = p_c_inf if abs(p_c_inf - P_C) > 1e-8 else P_C
    print(f"  Using p_c = {P_C_REF:.12f}", flush=True)

    cells = {}
    for L in L_LIST:
        cached = load_cell_data(L)
        if cached is not None:
            print(f"  L={L}: loaded from cache", flush=True)
            cells[L] = cached
            continue
        n = N_REAL[L]
        src, dst, N = pe.square_lattice(L)
        print(f"  L={L} n={n}: running cells at p_c={P_C_REF:.12f}", flush=True)

        masses_list, chis_list, pinfs_list, sizes_list = [], [], [], []
        for i in range(n):
            seed_i = SEED + i * 7
            lab = cell_label_p(L, "pc-exp", seed_i)
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

        save_cell_data(L, masses, chis, pinfs, sizes_list)
        cells[L] = {"masses": masses, "chis": chis, "pinfs": pinfs, "sizes": sizes_list}
        print(f"  L={L} done (n_cells={n}), cached", flush=True)

    logx = np.log(np.asarray(L_LIST, dtype=float))
    min_n = min(len(cells[L]["masses"]) for L in L_LIST)
    mmat_a = np.array([cells[L]["masses"][:min_n] for L in L_LIST])
    cmat_a = np.array([cells[L]["chis"][:min_n] for L in L_LIST])
    pmat_a = np.array([cells[L]["pinfs"][:min_n] for L in L_LIST])

    Df = bootstrap_slope(logx, mmat_a, BS_DRAWS, BS + "-df", SEED)
    Gf = bootstrap_slope(logx, cmat_a, BS_DRAWS, BS + "-gn", SEED)
    Bf = -bootstrap_slope(logx, pmat_a, BS_DRAWS, BS + "-bn", SEED)

    Df_m, Df_se = float(Df.mean()), float(Df.std(ddof=1))
    Gf_m, Gf_se = float(Gf.mean()), float(Gf.std(ddof=1))
    Bf_m, Bf_se = float(Bf.mean()), float(Bf.std(ddof=1))

    print(f"[Q-P007] Df={Df_m:.5f}+-{Df_se:.5f} Gn={Gf_m:.5f}+-{Gf_se:.5f} Bn={Bf_m:.5f}+-{Bf_se:.5f}", flush=True)

    tL = TAU_L
    tsizes = [ss[1:] for ss in cells[tL]["sizes"]]
    total_tail = sum(len(s) for s in tsizes)
    print(f"[Q-P007] tau: tL={tL}, total tail clusters={total_tail}", flush=True)
    tc = fit_tau_cumulative(tsizes, TAU_RANGE[0], TAU_RANGE[1], BS + "-tau", SEED)
    tau_m = tc["tau_cum"] if tc is not None else None
    boot_se = tc.get("boot_se", 0) if tc is not None else None
    chi2_red = tc.get("chi2_red", None) if tc is not None else None
    print(f"[Q-P007] tau={'N/A' if tau_m is None else f'{tau_m:.5f}'} (exp 2.055)", flush=True)

    results = {
        "experiment": EXP_ID, "L_list": L_LIST, "n_real": N_REAL,
        "p_c_ziff": P_C, "p_c_refined": p_c_inf,
        "p_c_measures": {str(k): v for k, v in p_c_measures.items()},
        "bootstrap_draws": BS_DRAWS,
        "exponents": {
            "Df": {"mean": Df_m, "se": Df_se, "expected": 91/48, "tol": 0.015},
            "gamma_nu": {"mean": Gf_m, "se": Gf_se, "expected": 43/24, "tol": 0.03},
            "beta_nu": {"mean": Bf_m, "se": Bf_se, "expected": 5/48, "tol": 0.015},
            "tau": {"mean": tau_m, "se": boot_se, "expected": 187/91, "tol": 0.05},
        },
        "tau_cum_chi2_red": chi2_red,
        "tau_raw": {"total_tail_clusters": total_tail, "fit_range": TAU_RANGE, "tau_L": tL},
        "elapsed": time.time() - t_start,
    }

    out = os.path.join(QDIR, "CODE", "RESULTS", f"{EXP_ID}_results.json")
    with open(out, "w") as f: json.dump(results, f, indent=2)

    combined = {**phase1, "phase2_results": results}
    with open(os.path.join(QDIR, "CODE", "RESULTS", f"{EXP_ID}_combined.json"), "w") as f:
        json.dump(combined, f, indent=2)

    print(f"[Q-P007] DONE in {time.time()-t_start:.0f}s. Saved: {out}", flush=True)


if __name__ == "__main__":
    main()
