"""Q-P007 runner — p_c refinement diagnostic.

Measures p_c via width-curve crossing at L in {512,1024,2048}.
Tests whether p_c accuracy explains Q-P006 exponent deviations.
Also re-measures tau at refined p_c."""
from __future__ import annotations
import json, os, sys, time, hashlib
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

CONFIG = os.path.join(QDIR, "CONFIG")
PREC = json.load(open(os.path.join(CONFIG, "prereg_EXP-0009PC.json"), encoding="utf-8"))
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


def main():
    t_start = time.time()

    # Phase 1: Width curves at each L
    print("[Q-P007] Phase 1: Width curves", flush=True)
    p_c_measures = {}
    wres = {}
    for Lk in PREC["parameters"]["width_L_list"]:
        g = PREC["parameters"]["width_grid"][f"L{Lk}"]
        w = probit_width(Lk, g["grid"], g["n_each"], SEED)
        wres[Lk] = w
        if w["ok"]:
            p_c_measures[Lk] = w["mu"]
            print(f"  L={Lk}: p_c={w['mu']:.6f} +/- {w['sigma']:.6f}", flush=True)

    # Extrapolate p_c -> L->inf
    if len(p_c_measures) >= 2:
        Ls = np.array(list(p_c_measures.keys()), dtype=float)
        pcs = np.array(list(p_c_measures.values()))
        # Linear fit: p_c(L) = p_inf + a/L
        inv_L = 1.0 / Ls
        slope, intercept = np.polyfit(inv_L, pcs, 1)
        p_c_inf = float(intercept)
        print(f"  p_c(L->inf) = {p_c_inf:.8f} (Ziff: {P_C:.8f})", flush=True)
        print(f"  |dev| from Ziff = {abs(p_c_inf - P_C):.8f}", flush=True)
    else:
        p_c_inf = P_C
        print("  Not enough L values for extrapolation, using Ziff value", flush=True)

    # Phase 2: Re-measure exponents at refined p_c (use midpoint if refined is different)
    print("[Q-P007] Phase 2: Exponent measurement at refined p_c", flush=True)
    # Use refined p_c for measurement
    P_C_REF = p_c_inf if abs(p_c_inf - P_C) > 1e-8 else P_C
    print(f"  Using p_c = {P_C_REF:.12f}", flush=True)

    # Need to modify run_exponent_cell to use P_C_REF — but it uses PC["parameters"]["p_c"]
    # Instead, create custom cells
    cells = {}
    for L in L_LIST:
        n = N_REAL[L]
        src, dst, N = pe.square_lattice(L)
        cells[L] = {"L": L, "N": N, "n": n, "k_v": 0, "P_span": 0,
                        "masses": np.array([]), "chis": np.array([]),
                        "pinfs": np.array([]), "sizes": []}
        print(f"  L={L} n={n}: running cells at p_c={P_C_REF:.12f}", flush=True)

        # Run n cells at P_C_REF
        masses_list = []
        chis_list = []
        pinfs_list = []
        sizes_list = []
        for i in range(n):
            seed_i = SEED + i * 7
            lab = cell_label_p(L, "pc-exp", seed_i)
            o = pe.run_span_cell_edges(src, dst, N, L, P_C_REF, 1, seed_i, lab,
                                       semantics="site",
                                       want_largest_mass=True,
                                       want_stats=True,
                                       want_cluster_sizes=True)
            masses_list.append(o["masses"])
            chis_list.append(o["chis"])
            pinfs_list.append(o["pinfs"])
            sizes_list.append(o["sizes"])

        masses = np.concatenate(masses_list) if masses_list else np.array([0])
        chis = np.concatenate(chis_list) if chis_list else np.array([0])
        pinfs = np.concatenate(pinfs_list) if pinfs_list else np.array([0])

        cells[L] = {"L": L, "N": N, "n": n, "k_v": n, "P_span": 1.0,
                        "masses": masses, "chis": chis, "pinfs": pinfs,
                        "sizes": sizes_list}
        print(f"  L={L} done (n_cells={n})", flush=True)

    # Bootstrap exponents
    logx = np.log(np.asarray(L_LIST, dtype=float))
    mmat = [cells[L]["masses"] for L in L_LIST]
    cmat = [cells[L]["chis"] for L in L_LIST]
    pmat = [cells[L]["pinfs"] for L in L_LIST]

    # Need aligned arrays for bootstrap_slope — mmat/cmat/pmat are ragged
    # For Q-P007, use mean per L (simplified)
    # Actually, bootstrap_slope expects per-L arrays with same length
    # Let me resample within each L to match
    min_n = min(len(m) for m in mmat)
    mmat_a = np.array([m[:min_n] for m in mmat])
    cmat_a = np.array([c[:min_n] for c in cmat])
    pmat_a = np.array([p[:min_n] for p in pmat])

    Df = bootstrap_slope(logx, mmat_a, BS_DRAWS, BS + "-df", SEED)
    Gf = bootstrap_slope(logx, cmat_a, BS_DRAWS, BS + "-gn", SEED)
    Bf = -bootstrap_slope(logx, pmat_a, BS_DRAWS, BS + "-bn", SEED)

    Df_m, Df_se = float(Df.mean()), float(Df.std(ddof=1))
    Gf_m, Gf_se = float(Gf.mean()), float(Gf.std(ddof=1))
    Bf_m, Bf_se = float(Bf.mean()), float(Bf.std(ddof=1))

    print(f"[Q-P007] Df={Df_m:.5f}+-{Df_se:.5f} Gn={Gf_m:.5f}+-{Gf_se:.5f} Bn={Bf_m:.5f}+-{Bf_se:.5f}", flush=True)

    # Tau at TAU_L
    tL = TAU_L
    tsizes = [ss[1:] for ss in cells[tL]["sizes"]]
    tc = fit_tau_cumulative(tsizes, TAU_RANGE[0], TAU_RANGE[1], BS + "-tau", SEED)
    tau_m = tc["tau_cum"]
    print(f"[Q-P007] tau={tau_m:.5f} (exp 2.055)", flush=True)

    # Compare with Q-P006 results
    print("\n--- Comparison with Q-P006 (at original p_c) ---", flush=True)
    q006 = {
        "Df": (1.8633, 0.0423), "Gn": (1.7301, 0.0604),
        "Bn": (0.1372, 0.0409), "tau": (1.9753, 0.0048),
    }
    for name, (m6, s6) in q006.items():
        if name == "Df": m_new, s_new = Df_m, Df_se
        elif name == "Gn": m_new, s_new = Gf_m, Gf_se
        elif name == "Bn": m_new, s_new = Bf_m, Bf_se
        else: m_new, s_new = tau_m, tc.get("boot_se", 0)
        delta = m_new - m6
        print(f"  {name}: Q-P006={m6:.5f} -> Q-P007={m_new:.5f} (delta={delta:+.5f})", flush=True)

    results = {
        "experiment": EXP_ID, "L_list": L_LIST, "n_real": N_REAL,
        "p_c_ziff": P_C, "p_c_refined": p_c_inf,
        "p_c_measures": {str(k): v for k, v in p_c_measures.items()},
        "bootstrap_draws": BS_DRAWS,
        "exponents": {
            "Df": {"mean": Df_m, "se": Df_se, "expected": 91/48, "tol": 0.015},
            "gamma_nu": {"mean": Gf_m, "se": Gf_se, "expected": 43/24, "tol": 0.03},
            "beta_nu": {"mean": Bf_m, "se": Bf_se, "expected": 5/48, "tol": 0.015},
            "tau": {"mean": tau_m, "se": tc.get("boot_se", 0), "expected": 187/91, "tol": 0.05},
        },
        "tau_cum_chi2_red": tc.get("chi2_red", None),
        "comparison_with_q006": q006,
        "elapsed": time.time() - t_start,
    }

    os.makedirs(os.path.join(QDIR, "CODE", "RESULTS"), exist_ok=True)
    out = os.path.join(QDIR, "CODE", "RESULTS", f"{EXP_ID}_results.json")
    with open(out, "w") as f: json.dump(results, f, indent=2)
    print(f"[Q-P007] DONE in {time.time()-t_start:.0f}s. Saved: {out}", flush=True)


if __name__ == "__main__":
    main()
