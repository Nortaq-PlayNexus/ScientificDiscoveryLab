"""Q-P006 runner — precision study of 2D percolation exponents.
L in {512, 1024, 2048}, 2000 bootstrap draws each.
Reuses perc_engine and run_exp0009.py functions where possible."""
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
                             fit_tau_histogram)

# Re-derive PC and SEED from Q-P006 prereg (not Q-P005)
CONFIG = os.path.join(QDIR, "CONFIG")
PREC = json.load(open(os.path.join(CONFIG, "prereg_EXP-0009P.json"), encoding="utf-8"))
PC = {"seed": PREC["seed"], "p_canon_token": PREC["p_canon_token"],
      "parameters": PREC["parameters"], "decision_rule": PREC["decision_rule"]}
SEED = PREC["seed"]

CONFIG = os.path.join(QDIR, "CONFIG")
PREC = json.load(open(os.path.join(CONFIG, "prereg_EXP-0009P.json"), encoding="utf-8"))
BS = PREC["parameters"]["bootstrap_label"]
L_LIST = PREC["parameters"]["L_list"]
N_REAL = {int(k): int(v) for k, v in PREC["parameters"]["n_real"].items()}
BS_DRAWS = PREC["parameters"]["bootstrap_draws"]
TAU_RANGE = PREC["parameters"]["tau_fit_range"]
TAU_L = PREC["parameters"]["tau_L"]

EXP_ID = PREC["experiment_id"]


def cell_label_p(L, kind, seed):
    return PREC["rng_label_pattern"].replace("<L>", str(L)).replace("<pcanon>", PREC["p_canon_token"]).replace("<kind>", kind)


def main():
    t_start = time.time()
    cells = {}
    for L in L_LIST:
        n = N_REAL[L]
        path = os.path.join(QDIR, "CODE", "RESULTS", f"_cells_L{L}_n{n}.npz")
        if os.path.exists(path):
            z = np.load(path, allow_pickle=True)
            cells[L] = {"L": L, "N": int(z["N"]), "n": n, "k_v": int(z["k_v"]),
                          "P_span": float(z["P_span"]), "masses": z["masses"],
                          "chis": z["chis"], "pinfs": z["pinfs"], "sizes": list(z["sizes"])}
        else:
            cells[L] = run_exponent_cell(L, n, SEED)
            save_cell(L, n, cells[L])
        print(f"[Q-P006] L={L} n={n} done (P_span={cells[L]['P_span']:.4f}, {time.time()-t_start:.0f}s)", flush=True)

    logx = np.log(np.asarray(L_LIST, dtype=float))
    mmat = [cells[L]["masses"] for L in L_LIST]
    cmat = [cells[L]["chis"] for L in L_LIST]
    pmat = [cells[L]["pinfs"] for L in L_LIST]

    Df = bootstrap_slope(logx, mmat, BS_DRAWS, BS + "-df", SEED)
    Gf = bootstrap_slope(logx, cmat, BS_DRAWS, BS + "-gn", SEED)
    Bf = -bootstrap_slope(logx, pmat, BS_DRAWS, BS + "-bn", SEED)

    Df_m, Df_se = float(Df.mean()), float(Df.std(ddof=1))
    Gf_m, Gf_se = float(Gf.mean()), float(Gf.std(ddof=1))
    Bf_m, Bf_se = float(Bf.mean()), float(Bf.std(ddof=1))
    print(f"[Q-P006] Df={Df_m:.5f}+-{Df_se:.5f} Gn={Gf_m:.5f}+-{Gf_se:.5f} Bn={Bf_m:.5f}+-{Bf_se:.5f}", flush=True)

    tL = TAU_L
    tsizes = [ss[1:] for ss in cells[tL]["sizes"]]
    tc = fit_tau_cumulative(tsizes, TAU_RANGE[0], TAU_RANGE[1], BS + "-tau", SEED)
    tau_m = tc["tau_cum"]

    inv_nu_draws = None
    wres = {}
    for Lk in [256, 512, 1024]:
        pass

    results = {
        "experiment": EXP_ID, "L_list": L_LIST, "n_real": N_REAL,
        "bootstrap_draws": BS_DRAWS,
        "exponents": {
            "Df": {"mean": Df_m, "se": Df_se, "expected": 91/48, "tol": 0.015},
            "gamma_nu": {"mean": Gf_m, "se": Gf_se, "expected": 43/24, "tol": 0.03},
            "beta_nu": {"mean": Bf_m, "se": Bf_se, "expected": 5/48, "tol": 0.015},
            "tau": {"mean": tau_m, "se": tc.get("boot_se", 0), "expected": 187/91, "tol": 0.05},
        },
        "tau_cumulative_se": tc.get("boot_se", 0),
        "tau_cum_chi2_red": tc.get("chi2_red", None),
        "elapsed": time.time() - t_start,
    }

    os.makedirs(os.path.join(QDIR, "CODE", "RESULTS"), exist_ok=True)
    out = os.path.join(QDIR, "CODE", "RESULTS", f"{EXP_ID}_results.json")
    with open(out, "w") as f: json.dump(results, f, indent=2)
    print(f"[Q-P006] DONE in {time.time()-t_start:.0f}s. Saved: {out}", flush=True)


if __name__ == "__main__":
    main()
