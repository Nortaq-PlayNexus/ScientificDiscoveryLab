"""EXP-0010 / Q-P005 — D_f at non-power-of-2 lattice sizes.

Lattice-artifact diagnostic for EXP-0009 (ABNORMAL). EXP-0009 measured
D_f = 1.8697 at L in {128,256,512,1024} (ALL power-of-2). This tests
whether the deviation is a lattice-size discretization artifact
(borrowed from coherent-optical-ai-sandbox grid-locking at 256^2):
if D_f recovers to 91/48 at non-power-of-2 sizes, ABNORMAL was an
artifact. Fresh streams; no EXP-0009 cells reused.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
QDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(QDIR)
ENGINE = os.path.join(ROOT, "ENGINE")
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)
import perc_engine as pe  # noqa: E402

LAB = pe.LAB
PCONF = os.path.join(QDIR, "CONFIG")
PC = json.load(open(os.path.join(PCONF, "prereg_EXP-0010.json"), encoding="utf-8"))
SEED = PC["seed"]
P_C = PC["parameters"]["p_c"]
LBASE = PC["rng_label_pattern"]
L_LIST = PC["parameters"]["L_list"]
N_REAL = {int(k): int(v) for k, v in PC["parameters"]["n_real"].items()}
Df_EX = PC["predictions"]["D_f"]["expected"]
Df_TOL = PC["predictions"]["D_f"]["tol"]
BS = PC["parameters"]["bootstrap_label"]
BS_DRAWS = PC["parameters"]["bootstrap_draws"]


def cell_label(L, kind, seed):
    return LBASE.replace("<system>", "site-square").replace("<L>", str(L)).replace(
        "<pcanon>", PC["p_canon_token"]).replace("<kind>", kind)


def run_cell(L, n, seed):
    src, dst, N = pe.square_lattice(L)
    lab = cell_label(L, "exp", seed)
    out = pe.run_span_cell_edges(src, dst, N, L, P_C, n, seed, lab,
                                   semantics="site",
                                   want_largest_mass=True,
                                   want_stats=True,
                                   want_cluster_sizes=True)
    masses = np.asarray(out["masses"], dtype=np.float64)
    sizes_list = out["cluster_sizes"]
    return {"L": int(L), "N": int(N), "n": n,
            "k_v": int(out["k_v"]), "P_span": out["k_v"] / n,
            "masses": masses, "sizes": sizes_list}


def save_cell(L, n, cell):
    p = os.path.join(QDIR, "CODE", "RESULTS", f"_df_nontriv_L{L}_n{n}.npz")
    np.savez(p,
             masses=cell["masses"],
             k_v=np.asarray(cell["k_v"]), N=np.asarray(cell["N"]),
             P_span=np.asarray(cell["P_span"]),
             sizes=np.asarray(cell["sizes"], dtype=object))


def load_cell(L, n):
    p = os.path.join(QDIR, "CODE", "RESULTS", f"_df_nontriv_L{L}_n{n}.npz")
    if not os.path.exists(p):
        return None
    z = np.load(p, allow_pickle=True)
    return {"L": L, "N": int(z["N"]), "n": n, "k_v": int(z["k_v"]),
            "P_span": float(z["P_span"]),
            "masses": z["masses"], "sizes": list(z["sizes"])}


def bootstrap_slope(logx, y_mat, draws, rng_name, seed):
    gen = pe.rng(rng_name, seed)
    nL = len(logx)
    out = np.empty(draws)
    for d in range(draws):
        means = []
        for Ls in range(nL):
            col = y_mat[Ls]
            idx = gen.integers(0, col.shape[0], size=col.shape[0])
            means.append(col[idx].mean())
        out[d] = np.polyfit(logx, np.log(np.asarray(means, dtype=float)), 1)[0]
    return out


def span_census_digest(o):
    h = hashlib.sha256()
    for ss in o["sizes"]:
        h.update(np.asarray(ss, dtype=np.int64).tobytes())
    return h.hexdigest()


def main():
    t_start = time.time()
    cells = {}
    for L in L_LIST:
        cells[L] = load_cell(L, N_REAL[L])
        if cells[L] is None:
            cells[L] = run_cell(L, N_REAL[L], SEED)
            save_cell(L, N_REAL[L], cells[L])
        print(f"[progress] D_f cell L={L} n={N_REAL[L]} done (P_span={cells[L]['P_span']:.4f}, elapsed {time.time()-t_start:.0f}s)", flush=True)

    logx = np.log(np.asarray(L_LIST, dtype=float))
    mmat = [cells[L]["masses"] for L in L_LIST]
    Df_draws = bootstrap_slope(logx, mmat, BS_DRAWS, BS + "-df", SEED)
    Df = float(Df_draws.mean())
    seDf = float(Df_draws.std(ddof=1))
    print(f"[progress] D_f={Df:.6f} (SE={seDf:.6f}, theory={Df_EX}, tol={Df_TOL})", flush=True)

    # C1 determinism at L=253
    o1 = run_cell(253, 100, SEED)
    d1 = span_census_digest(o1)
    o2 = run_cell(253, 100, SEED)
    d2 = span_census_digest(o2)
    c1 = {"digest_eq": d1 == d2, "pass": bool(d1 == d2)}
    print(f"[progress] C1 pass={c1['pass']}", flush=True)

    per_L = {str(L): {"mean_mass": float(cells[L]["masses"].mean()),
                       "se_mass": float(cells[L]["masses"].std(ddof=1) / np.sqrt(cells[L]["n"]))}
             for L in L_LIST}

    c1_pass = c1["pass"]
    df_in_tol = abs(Df - Df_EX) <= Df_TOL
    if not c1_pass:
        decision = "INCONCLUSIVE"
    elif df_in_tol:
        decision = "LATTICE_ARTIFACT"
    else:
        decision = "FINITE_SIZE_CORRECTION"

    primary = {
        "experiment_id": "EXP-0010", "question": "Q-P005", "hypothesis": "HYP-005",
        "decision": decision,
        "D_f": {"measured": Df, "se": seDf, "expected": Df_EX, "tol": Df_TOL,
                "pass": bool(abs(Df - Df_EX) <= Df_TOL), "per_L": per_L},
        "gates": {"C1": c1},
        "test": "D_f at non-power-of-2 L: lattice-artifact vs finite-size correction",
    }
    diag = {"L_list": L_LIST, "p_c": P_C, "theory_Df": Df_EX, "tol": Df_TOL,
            "per_L_mean_mass": {str(L): float(cells[L]["masses"].mean()) for L in L_LIST},
            "P_span_per_L": {str(L): float(cells[L]["P_span"]) for L in L_LIST},
            "D_f_boot_draws": BS_DRAWS}

    outdir = os.path.join(QDIR, "CODE", "RESULTS")
    os.makedirs(outdir, exist_ok=True)
    pe.write_summary(os.path.join(outdir, "EXP-0010_results.json"),
                      {"primary_results": primary, "estimator_diagnostics": diag})
    pe.write_summary(os.path.join(outdir, "EXP-0010_summary.json"), {
        "primary_results": primary, "estimator_diagnostics": diag,
        "decision": decision, "result_path": os.path.join(outdir, "EXP-0010_results.json")})
    pe.append_registry(os.path.join(QDIR, "RESULTS"), PCONF, "EXP-0010", "Q-P005",
                       "HYP-005", decision, os.path.join(outdir, "EXP-0010_results.json"),
                       extra={"Df_measured": Df, "Df_SE": seDf})
    print(json.dumps(primary, indent=2))
    print("Df:", Df, "SE:", seDf, "theory:", Df_EX, "tol:", Df_TOL)
    print("DECISION:", decision)


if __name__ == "__main__":
    main()
