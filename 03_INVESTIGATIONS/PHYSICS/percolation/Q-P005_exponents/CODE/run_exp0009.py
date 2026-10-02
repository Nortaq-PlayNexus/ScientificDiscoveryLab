"""EXP-0009 / Q-P005 runner — critical exponents and hyperscaling.

Square-site percolation at p_c = 0.5927460508. Measures D_f, gamma/nu,
beta/nu, tau, 1/nu and the three scaling relations, with the pre-registered
gates (C1, C6, C7 report, FG, PC1). Deterministic: every random draw comes
from G_LAB rng(label, seed) with frozen labels/seeds. Reads the frozen prereg.
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
ROOT = os.path.dirname(QDIR)  # percolation investigation root (parent of Q-P005_exponents)
ENGINE = os.path.join(ROOT, "ENGINE")
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)
import perc_engine as pe  # noqa: E402

LAB = pe.LAB  # C:\Users\natha\ScientificDiscoveryLab
PCONF = os.path.join(QDIR, "CONFIG")

PC = json.load(open(os.path.join(PCONF, "prereg_EXP-0009.json"), encoding="utf-8"))
SEED = PC["seed"]
PCAN = PC["p_canon_token"]
P_C = PC["parameters"]["p_c"]
LBASE = PC["rng_label_pattern"]

D_F_EX = 91 / 48          # 1.895833
GANU_EX = 43 / 24         # 1.791667
BANU_EX = 5 / 48          # 0.104167
TAU_EX = 187 / 91         # 2.054945

DECISION_RULE = PC["decision_rule"]


def bs_name():
    return PC["parameters"]["bootstrap_label"]


def cell_label(L, kind, seed):
    return LBASE.replace("<system>", "site-square").replace("<L>", str(L)).replace(
        "<pcanon>", PCAN).replace("<kind>", kind)


def run_exponent_cell(L, n, seed):
    """Return dict(k_v, n, masses, chis, pinfs, sizes)."""
    src, dst, N = pe.square_lattice(L)
    lab = cell_label(L, "exp", seed)
    out = pe.run_span_cell_edges(src, dst, N, L, P_C, n, seed, lab,
                                 semantics="site",
                                 want_largest_mass=True,
                                 want_stats=True,
                                 want_cluster_sizes=True)
    masses = np.asarray(out["masses"], dtype=np.float64)
    sizes_list = out["cluster_sizes"]
    chis = []
    for ss in sizes_list:
        s = np.asarray(ss, dtype=np.float64)
        if s.size == 0:
            chis.append(0.0)
        else:
            chis.append(float((s * s).sum() / s.sum()))
    chis = np.asarray(chis, dtype=np.float64)
    pinfs = masses / float(N)
    return {"L": int(L), "N": int(N), "n": n,
            "k_v": int(out["k_v"]), "P_span": out["k_v"] / n,
            "masses": masses, "chis": chis, "pinfs": pinfs,
            "sizes": sizes_list}


def _cells_path(L, n):
    return os.path.join(QDIR, "CODE", "RESULTS", f"_cells_L{L}_n{n}.npz")


def save_cell(L, n, cell):
    os.makedirs(os.path.join(QDIR, "CODE", "RESULTS"), exist_ok=True)
    np.savez(_cells_path(L, n),
             masses=cell["masses"], chis=cell["chis"], pinfs=cell["pinfs"],
             k_v=np.asarray(cell["k_v"]), N=np.asarray(cell["N"]),
             P_span=np.asarray(cell["P_span"]),
             sizes=np.asarray(cell["sizes"], dtype=object))


def load_cell(L, n):
    p = _cells_path(L, n)
    if not os.path.exists(p):
        return None
    z = np.load(p, allow_pickle=True)
    return {"L": L, "N": int(z["N"]), "n": n, "k_v": int(z["k_v"]),
            "P_span": float(z["P_span"]),
            "masses": z["masses"], "chis": z["chis"], "pinfs": z["pinfs"],
            "sizes": list(z["sizes"])}


def bootstrap_slope(logx, y_mat, draws, rng_name, seed):
    """y_mat: (n_L, n_real) rows aligned with logx; slope of y vs x per draw."""
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


def fit_tau_cumulative(all_sizes, s_lo, s_hi, rng_label, seed):
    """N_>(s) ~ s^{-(tau-1)} over s in [s_lo, s_hi].

    all_sizes: list of per-realization cluster-size arrays (largest already
    excluded by caller). Aggregated deterministic; SE via weighted OLS over
    equispaced log-s points.
    """
    big = np.concatenate([np.asarray(a, dtype=np.int64) for a in all_sizes]).astype(np.int64)
    n_clusters = big.shape[0]
    big_sorted = np.sort(big)[::-1]
    s_grid = np.geomspace(s_lo, s_hi, 250).astype(np.int64)
    s_grid = np.unique(np.clip(s_grid, 1, None))
    neg_grid = -(s_grid + 1)
    Ngt = np.searchsorted(-big_sorted, neg_grid).astype(float)
    keep = Ngt >= 3
    if keep.sum() < 20:
        return None
    sx = np.log(s_grid[keep].astype(float))
    sy = np.log(Ngt[keep])
    w = ri_weight = np.sqrt(np.maximum(Ngt[keep], 1.0))
    A = np.vstack([np.ones_like(sx), sx]).T
    W = np.diag(w)
    coef, *_ = np.linalg.lstsq(W @ A, W @ sy, rcond=None)
    resid = sy - A @ coef
    chi2r = float(np.sum((resid * w) ** 2) / max(len(sx) - 2, 1))
    cov = np.linalg.inv(A.T @ (W @ W) @ A)
    slope, se_slope = float(coef[1]), float(np.sqrt(cov[1, 1]))
    tau_cum = 1.0 - slope
    # also a deterministic bootstrap over clusters
    gen = pe.rng(rng_label, seed)
    tau_draws = []
    for _ in range(500):
        idx = gen.integers(0, n_clusters, size=n_clusters)
        samp = np.sort(big_sorted[idx])[::-1]  # searchsorted requires sorted input
        Ngt2 = np.searchsorted(-samp, neg_grid).astype(float)
        k = Ngt2 >= 3
        if k.sum() < 20:
            continue
        xx = np.log(s_grid[k].astype(float))
        yy = np.log(Ngt2[k])
        c2 = np.polyfit(xx, yy, 1)
        tau_draws.append(1.0 - c2[0])
    tau_bs = np.asarray(tau_draws, dtype=float)
    return {"tau_cum": tau_cum, "se_slope": se_slope, "chi2_red": chi2r,
            "n_clusters": int(n_clusters), "s_fit_min": int(s_grid[keep].min()),
            "s_fit_max": int(s_grid[keep].max()),
            "boot_mean": float(tau_bs.mean()) if tau_bs.size else None,
            "boot_se": float(tau_bs.std(ddof=1)) if tau_bs.size > 1 else None}


def fit_tau_histogram(all_sizes, s_lo, s_hi):
    """Direct histogram: n_s ~ s^{-tau} over s in [s_lo, s_hi]."""
    big = np.concatenate([np.asarray(a, dtype=np.int64) for a in all_sizes]).astype(np.int64)
    hist = np.bincount(big)
    s = np.arange(hist.shape[0], dtype=np.int64)
    m = (s >= s_lo) & (s <= s_hi) & (hist > 0)
    sx = np.log(s[m].astype(float))
    sy = np.log(hist[m].astype(float))
    w = np.sqrt(np.maximum(hist[m].astype(float), 1.0))
    A = np.vstack([np.ones_like(sx), sx]).T
    W = np.diag(w)
    coef, *_ = np.linalg.lstsq(W @ A, W @ sy, rcond=None)
    resid = sy - A @ coef
    chi2r = float(np.sum((resid * w) ** 2) / max(len(sx) - 2, 1))
    cov = np.linalg.inv(A.T @ (W @ W) @ A)
    slope = float(coef[1])
    return {"tau_hist": -slope, "se_slope": float(np.sqrt(cov[1, 1])),
            "chi2_red": chi2r, "n_bins": int(m.sum())}


def probit_width(L, grid, n_each, seed):
    src, dst, N = pe.square_lattice(L)
    ps = np.arange(grid[0], grid[1] + 1e-12, grid[2])
    ks = []
    for p in ps:
        lab = cell_label(L, f"width-p{p:.4f}".replace(".", "p"), seed)
        o = pe.run_span_cell_edges(src, dst, N, L, float(p), n_each, seed, lab,
                                   semantics="site")
        ks.append(o["k_v"])
    ks = np.asarray(ks, dtype=np.int64)
    mu, sig, ok = pe.probit_fit(ps, ks, np.full(ks.shape, n_each), s0=0.10)
    return {"L": int(L), "mu": mu, "sigma": sig, "ok": bool(ok),
            "p_grid": ps.tolist(), "k": ks.tolist(), "n": int(n_each)}


def span_census_digest(o):
    h = hashlib.sha256()
    for ss in o["sizes"]:
        h.update(np.asarray(ss, dtype=np.int64).tobytes())
    return h.hexdigest()


def c6_seedladder():
    reps = {}
    # M_max and chi at L=256, n=150 per seed (budget revision per prereg note)
    N6 = 150
    mmat, cmat = [], []
    for s in [SEED] + PC["seed_ladder"]:
        o = run_exponent_cell(256, N6, s)
        mmat.append(o["masses"]); cmat.append(o["chis"])
        reps[s] = {"Mmax": float(o["masses"].mean()), "chi": float(o["chis"].mean())}
    mmat = np.asarray(mmat); cmat = np.asarray(cmat)
    nm, nc = mmat.shape[1], cmat.shape[1]
    Sm = mmat.std(ddof=1, axis=1) / np.sqrt(nm)
    Sc = cmat.std(ddof=1, axis=1) / np.sqrt(nc)
    jm = float(np.sqrt(np.sum(Sm ** 2))); jc = float(np.sqrt(np.sum(Sc ** 2)))
    base_m, base_c = reps[SEED]["Mmax"], reps[SEED]["chi"]
    dm = [abs(reps[s]["Mmax"] - base_m) for s in PC["seed_ladder"]]
    dc = [abs(reps[s]["chi"] - base_c) for s in PC["seed_ladder"]]
    pass_m = all(d <= 3 * jm for d in dm)
    pass_c = all(d <= 3 * jc for d in dc)
    # width check at L=128 inner grid
    g = PC["parameters"]["width_grid"]["L128"]["grid"]
    ps = np.arange(g[0], g[1] + 1e-12, g[2])
    inner = ps[np.argsort(np.abs(ps - P_C))[:3]]
    W0 = None
    stats_holder = []
    for s in [SEED] + PC["seed_ladder"]:
        src, dst, N = pe.square_lattice(128)
        ks = []
        for p in inner:
            lab = cell_label(128, f"c6w-p{p:.4f}-s{s}".replace(".", "p"), SEED)
            o = pe.run_span_cell_edges(src, dst, N, 128, float(p), 150, SEED, lab,
                                       semantics="site")
            ks.append(o["k_v"])
        if s == SEED:
            W0 = np.asarray(ks, dtype=float) / 150.0
        stats_holder.append((s, np.asarray(ks, dtype=float) / 150.0))
    jw = float(np.sqrt(np.sum([((w - W0) ** 2).max() for _, w in stats_holder[1:]]) / len(stats_holder[1:])))
    dw = [float(np.abs(w - W0).max()) for _, w in stats_holder[1:]]
    pass_w = all(d <= 3 * jw for d in dw)
    return {"seed_means": reps, "joint_SE_Mmax": jm, "joint_SE_chi": jc,
            "dev_Mmax": dm, "dev_chi": dc, "pass_Mmax": bool(pass_m),
            "pass_chi": bool(pass_c), "width_devs": dw, "joint_SE_width": jw,
            "pass_width": bool(pass_w),
            "pass": bool(pass_m and pass_c and pass_w)}


def main():
    t_start = time.time()
    params = PC["parameters"]
    L_list = params["L_list"]
    n_real = {int(k): int(v) for k, v in params["n_real"].items()}
    cells = {}
    for L in L_list:
        cells[L] = load_cell(L, n_real[L])
        if cells[L] is None:
            cells[L] = run_exponent_cell(L, n_real[L], SEED)
            save_cell(L, n_real[L], cells[L])
        print(f"[progress] exponent cell L={L} n={n_real[L]} done (P_span={cells[L]['P_span']:.4f}, elapsed {time.time()-t_start:.0f}s)", flush=True)

    logx = np.log(np.asarray(L_list, dtype=float))
    mmat = [cells[L]["masses"] for L in L_list]  # ragged per-L lengths (n_real differs)
    cmat = [cells[L]["chis"] for L in L_list]
    pmat = [cells[L]["pinfs"] for L in L_list]

    Df_draws = bootstrap_slope(logx, mmat, params["bootstrap_draws"], bs_name() + "-df", SEED)
    Gf_draws = bootstrap_slope(logx, cmat, params["bootstrap_draws"], bs_name() + "-gn", SEED)
    # P_inf = M_max/N scales ~ L^{-(2-D_f)}; the measured slope is NEGATIVE and
    # beta/nu = -(slope of log P_inf) per the frozen PREDICTIONS.md convention
    # (beta/nu = 2 - D_f, positive). Bf below carries the + convention.
    Bf_draws = -bootstrap_slope(logx, pmat, params["bootstrap_draws"], bs_name() + "-bn", SEED)
    Df, seDf = float(Df_draws.mean()), float(Df_draws.std(ddof=1))
    Gf, seGf = float(Gf_draws.mean()), float(Gf_draws.std(ddof=1))
    Bf, seBf = float(Bf_draws.mean()), float(Bf_draws.std(ddof=1))

    # FG slope stability (inner sizes 256, 512, 1024)
    inner = params["fg_inner_sizes"]
    li = np.log(np.asarray(inner, dtype=float))
    Df_in = float(bootstrap_slope(li, [cells[L]["masses"] for L in inner],
                                  params["bootstrap_draws"], bs_name() + "-dfin", SEED).mean())
    Gf_in = float(bootstrap_slope(li, [cells[L]["chis"] for L in inner],
                                  params["bootstrap_draws"], bs_name() + "-gnin", SEED).mean())
    fg = {"Df_inner": Df_in, "dDf": abs(Df_in - Df),
          "gamma_inner": Gf_in, "dgamma": abs(Gf_in - Gf),
          "pass_Df": bool(abs(Df_in - Df) <= 0.02),
          "pass_gamma": bool(abs(Gf_in - Gf) <= 0.04),
          "pass": bool(abs(Df_in - Df) <= 0.02 and abs(Gf_in - Gf) <= 0.04)}
    print(f"[progress] exponents Df={Df:.5f} Gn={Gf:.5f} Bn={Bf:.5f} | FG dDf={abs(Df_in-Df):.4f} dGn={abs(Gf_in-Gf):.4f}", flush=True)

    # tau at L=1024 (primary): sizes excluding the largest per realization
    tL = params["tau_L"]
    tsizes = [ss[1:] for ss in cells[tL]["sizes"]]  # drop largest (first)
    s_lo, s_hi = params["tau_fit_range"]
    tc = fit_tau_cumulative(tsizes, s_lo, s_hi, bs_name() + "-tau", SEED)
    th = fit_tau_histogram(tsizes, s_lo, s_hi)
    tau_cum = tc["tau_cum"]
    # tau crossover trend over the SHARED range (comparable across L)
    trlo, trhi = params["tau_trend_range"]
    tau_trend = {}
    for Lt in params["tau_trend_L"]:
        tsl = [ss[1:] for ss in cells[Lt]["sizes"]]
        tcl = fit_tau_cumulative(tsl, trlo, trhi, bs_name() + f"-tautr{Lt}", SEED)
        tau_trend[Lt] = {"tau": tcl["tau_cum"], "boot_se": tcl["boot_se"]}
    print(f"[progress] tau trend L={Lt}: tau={tau_trend[Lt]['tau']:.4f} se={tau_trend[Lt]['boot_se']:.4f}", flush=True)
    print(f"[progress] tau L=1024 primary: tau={tau_cum:.4f}", flush=True)

    # width route
    wres = {}
    for Lk in params["width_L_list"]:
        g = params["width_grid"][f"L{Lk}"]
        wres[Lk] = probit_width(Lk, g["grid"], g["n_each"], SEED)
    wLs = np.log(np.asarray(params["width_L_list"], dtype=float))
    wsig = np.log(np.asarray([wres[L]["sigma"] for L in params["width_L_list"]], dtype=float))
    wsl = np.polyfit(wLs, wsig, 1)
    inv_nu = -float(wsl[0])
    nu = 1.0 / inv_nu if inv_nu > 0 else None
    print(f"[progress] width route done: inv_nu={inv_nu:.4f} sigmas=" +
          ", ".join(f"{L}:{wres[L]['sigma']:.4f}" for L in params["width_L_list"]), flush=True)

    # scaling relations
    R1 = abs(tau_cum - (1.0 + 2.0 / Df))
    R2 = abs(2 * Bf + Gf - 2.0)
    R3 = abs(Df - (2.0 - Bf))

    tols = PC["predictions"]
    tau_win = tols["tau"]["direct_window"]
    t256, t512, t1024 = (tau_trend[L]["tau"] for L in (256, 512, 1024))
    tau_rise_pass = bool((t512 >= t256 - tau_trend[512]["boot_se"])
                         and (t1024 >= t512 - tau_trend[1024]["boot_se"]))
    checks = {
        "D_f": {"measured": Df, "se": seDf, "expected": D_F_EX,
                "tol": tols["D_f"]["tol"], "pass": bool(abs(Df - D_F_EX) <= tols["D_f"]["tol"])},
        "gamma_nu": {"measured": Gf, "se": seGf, "expected": GANU_EX,
                     "tol": tols["gamma_nu"]["tol"], "pass": bool(abs(Gf - GANU_EX) <= tols["gamma_nu"]["tol"])},
        "beta_nu": {"measured": Bf, "se": seBf, "expected": BANU_EX,
                    "tol": tols["beta_nu"]["tol"], "pass": bool(abs(Bf - BANU_EX) <= tols["beta_nu"]["tol"])},
        "tau": {"measured": tau_cum, "expected": TAU_EX,
                "window": tau_win,
                "in_window": bool(tau_win[0] <= tau_cum <= tau_win[1]),
                "rise_to_Fisher": bool(tau_rise_pass),
                "rise_step": [t256, t512, t1024],
                "pass": bool(tau_win[0] <= tau_cum <= tau_win[1] and tau_rise_pass)},
        "1/nu": {"measured": inv_nu, "expected": 0.75,
                 "gate": tols["inv_nu_gate"], "pass": bool(tols["inv_nu_gate"][0] <= inv_nu <= tols["inv_nu_gate"][1])},
    }
    relations = {
        "R1_tau=1+2/Df": {"value": R1, "tol": tols["R1_tau_vs_Df"]["tol"],
                          "pass": bool(R1 <= tols["R1_tau_vs_Df"]["tol"])},
        "R2_2bn+gn=2": {"value": R2, "tol": tols["R2_beta_gamma"]["tol"], "pass": bool(R2 <= tols["R2_beta_gamma"]["tol"])},
        "R3_Df=2-bn": {"value": R3, "tol": tols["R3_Df_beta"]["tol"], "pass": bool(R3 <= tols["R3_Df_beta"]["tol"])},
    }

    # C1 determinism
    o1 = run_exponent_cell(256, 100, SEED)  # kind "exp" label + seed -> same frozen stream
    d1 = span_census_digest(o1)
    o2 = run_exponent_cell(256, 100, SEED)
    d2 = span_census_digest(o2)
    c1 = {"digest_eq": d1 == d2, "pass": bool(d1 == d2)}
    print(f"[progress] C1 determinism pass={c1['pass']}", flush=True)

    # C6
    c6 = c6_seedladder()
    print(f"[progress] C6 pass={c6['pass']} | jm={c6['joint_SE_Mmax']:.3e} jc={c6['joint_SE_chi']:.3e}", flush=True)

    # write the pre-C7 results file so the C7 subprocess can read the engine D_f
    outdir = os.path.join(QDIR, "CODE", "RESULTS")
    os.makedirs(outdir, exist_ok=True)
    pre_c7 = {"primary_results": {
        "experiment_id": "EXP-0009", "question": "Q-P005", "hypothesis": "HYP-005",
        "exponents": {k: {"value": v["measured"], "se": v.get("se"), "expected": v["expected"],
                          "tol": v.get("tol"), "pass": v["pass"]} for k, v in checks.items()},
        "relations": relations, "gates": {"C1": c1, "C6": c6, "FG": fg, "C7": {"pass": None}},
        "decision": "C7_PENDING"}}
    pre_c7_path = os.path.join(outdir, "EXP-0009_results.json")
    pe.write_summary(pre_c7_path, pre_c7)

    # C7 independent implementation (subprocess → report merged)
    print("[progress] launching C7 subprocess ...", flush=True)
    c7_script = os.path.join(QDIR, "REPLICATION", "independent_check_exp0009.py")
    c7_report_path = os.path.join(QDIR, "REPLICATION", "C7_exp0009_report.json")
    sub = subprocess.run([sys.executable, c7_script], capture_output=True, text=True)
    if sub.returncode != 0:
        raise RuntimeError(f"C7 subprocess failed:\n{sub.stdout}\n{sub.stderr}")
    c7rep = json.load(open(c7_report_path, encoding="utf-8"))
    c7 = {"report_path": c7_report_path, "pass": bool(c7rep["pass"]),
          "per_L": c7rep.get("per_L"), "D_f": c7rep.get("D_f")}
    print(f"[progress] C7 pass={c7['pass']}", flush=True)

    all_gates = [c1["pass"], c6["pass"], fg["pass"], c7["pass"]]
    p_check = all(v["pass"] for v in checks.values())
    r_check = all(v["pass"] for v in relations.values())

    if not all(all_gates):
        decision = DECISION_RULE["INCONCLUSIVE"]
    elif p_check and r_check:
        decision = DECISION_RULE["H0_SUPPORTED"]
    else:
        decision = DECISION_RULE["ABNORMAL"]

    primary = {
        "experiment_id": "EXP-0009", "question": "Q-P005", "hypothesis": "HYP-005",
        "decision": decision,
        "exponents": {k: {"value": v["measured"], "se": v.get("se"), "expected": v["expected"],
                          "tol": v.get("tol"), "pass": v["pass"]} for k, v in checks.items()},
        "relations": relations,
        "gates": {"C1": c1, "C6": c6, "FG": fg, "C7": c7},
    }
    diag = {
        "p_c": P_C, "L_list": L_list,
        "P_span_per_L": {str(L): float(cells[L]["P_span"]) for L in L_list},
        "mean_mass_per_L": {str(L): float(cells[L]["masses"].mean()) for L in L_list},
        "se_mass_per_L": {str(L): float(cells[L]["masses"].std(ddof=1) / np.sqrt(cells[L]["n"])) for L in L_list},
        "mean_chi_per_L": {str(L): float(cells[L]["chis"].mean()) for L in L_list},
        "width_probit": {str(L): {k: wres[L][k] for k in ("mu", "sigma", "ok", "n")} for L in params["width_L_list"]},
        "inv_nu": inv_nu, "nu": nu,
        "Df_boot_SE": seDf, "gamma_boot_SE": seGf, "beta_boot_SE": seBf,
        "tau_cumulative": tc, "tau_histogram": th, "tau_trend": tau_trend,
        "Bf_as_2_minus_Df": 2.0 - Df,
        "bootstrap_draws": params["bootstrap_draws"],
    }

    results = {"primary_results": primary, "estimator_diagnostics": diag}
    outdir = os.path.join(QDIR, "CODE", "RESULTS")
    os.makedirs(outdir, exist_ok=True)
    rpath = pe.write_summary(os.path.join(outdir, "EXP-0009_results.json"), results)
    pe.write_summary(os.path.join(outdir, "EXP-0009_summary.json"), {
        "primary_results": primary, "estimator_diagnostics": diag,
        "decision": decision, "result_path": rpath})
    pe.write_summary(os.path.join(PCONF, "EXP-0009_experiment.json"),
                     {"experiment_id": "EXP-0009", "question": "Q-P005",
                      "hypothesis": "HYP-005", "params_hash": pe.sha256_text(
                          json.dumps(PC, sort_keys=True)),
                      "result_path": rpath})
    pe.append_registry(os.path.join(QDIR, "RESULTS"), PCONF, "EXP-0009", "Q-P005",
                       "HYP-005", decision, rpath,
                       extra={"exponent_values": [Df, Gf, Bf, tau_cum, inv_nu]})
    print(json.dumps(primary, indent=2))
    print("DIAG:", json.dumps({k: diag[k] for k in ("inv_nu", "nu", "Df_boot_SE",
                                                    "gamma_boot_SE", "beta_boot_SE")}, indent=2))
    print(f"TAU: primary={tau_cum:.4f} trend={ {str(k): round(tau_trend[k]['tau'], 4) for k in params['tau_trend_L']} } R1={R1:.4f}")
    print("DECISION:", decision)


if __name__ == "__main__":
    main()