"""EXP-0008 runner — prime gaps vs Poisson/Gallagher (Q-M002, HYP-005).

Reads every tunable parameter from CONFIG/prereg_EXP-0008.json (the
frozen preregistration). No constant is hardcoded that the prereg
controls. Deterministic: all randomness from
engine.utilities.core.rng(label, seed); primes come from a deterministic
sieve (no RNG).

Prereg-contradiction resolution (documented, does not modify the frozen
prereg): the frozen prereg requires C7 to use "different binning scheme
(equal-width instead of exponential-quantile)" AND "chi2/KS vectors must
match within recorded tolerance" (tol_c7_vector_match = abs diff < 1e-9 on
chi2). Different binning makes the equal-width chi2 numerically different
by construction. Resolution: the C7 checker (i) renders its block-by-block
H0/H1 verdict from its own equal-width GOF (independent method), and
(ii) also reports a same-binning (exponential-quantile, prereg edges)
chi2/KS vector so the tabulated tolerance "abs diff < 1e-9" refers to
identically-binned statistics. C7 passes iff the verdicts match AND the
same-binning vectors match within 1e-9. See state/EXP-0008_decisions.md.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import numpy as np
from scipy import stats as sp_stats

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "04_SHARED_ENGINE"))
from engine.utilities.core import rng, machine_info, version_info, sha256_file

HERE = os.path.dirname(os.path.abspath(__file__))
INVESTIGATION = os.path.dirname(HERE)
PREREG_DEFAULT = os.path.join(INVESTIGATION, "CONFIG", "prereg_EXP-0008.json")
RESULTS_DIR = os.path.join(INVESTIGATION, "RESULTS")
REPLICATION_DIR = os.path.join(INVESTIGATION, "REPLICATION")

# Memory cap for the index matrix inside a bootstrap chunk (bytes). Keeps the
# largest block (B4, ~5.76M gaps) far below available RAM while vectorising.
_BOOTSTRAP_MEM_CAP = 400_000_000


def progress(msg: str) -> None:
    print(f"[EXP-0008] {msg}", flush=True)


def load_prereg(path: str) -> dict:
    pre = json.load(open(path, encoding="utf-8"))
    pre["prereg_sha256"] = sha256_file(path)
    return pre


def bootstrap_means(d, bs, rng, chunk: int | None = None):
    """Memory-stable bootstrap means: bs resamples of len(d)."""
    d = np.asarray(d, dtype=np.float64)
    n = len(d)
    if n == 0:
        return np.full(bs, np.nan, dtype=np.float64)
    if chunk is None:
        chunk = int(min(256, max(1, _BOOTSTRAP_MEM_CAP // (n * 8))))
    means = np.empty(bs, dtype=np.float64)
    for start in range(0, bs, chunk):
        end = min(start + chunk, bs)
        idx = rng.integers(0, n, size=(end - start, n))
        means[start:end] = np.mean(d[idx], axis=1)
    return means


def _c3_bootstrap_for_seed(seed, block_labels, deltas_by_block, bs, rng_label):
    """Bootstrap CI ladder for one seed (module-level so it is importable by spawn workers)."""
    rboot = rng(rng_label, seed)
    verdicts, ci_rows = [], []
    for label, d in zip(block_labels, deltas_by_block):
        resamples = bootstrap_means(d, bs, rboot)
        lo = float(np.percentile(resamples, 2.5))
        hi = float(np.percentile(resamples, 97.5))
        v = bool(lo <= 1.0 <= hi)
        verdicts.append(v)
        ci_rows.append({"block": label, "ci_low": lo, "ci_high": hi, "contains": v})
    return {"seed": int(seed), "overall": bool(all(verdicts)),
            "block_verdicts": verdicts, "ci": ci_rows}


def bh_fdr(pvals, alpha):
    """BH-FDR: boolean mask of rejected hypotheses (ascending-order threshold).

    Corrected: when hypotheses p_(1)..p_(k) all lie under their thresholds, all
    k are rejected (order[:k]). (An earlier indexing bug dropped the last one.)
    """
    pvals = np.asarray(pvals, dtype=float)
    n = len(pvals)
    if n == 0:
        return np.zeros(0, bool)
    order = np.argsort(pvals)
    thresholds = (np.arange(1, n + 1) / n) * alpha
    reject = np.zeros(n, bool)
    k = int(np.max(np.where(pvals[order] <= thresholds)[0]) + 1) if (pvals[order] <= thresholds).any() else 0
    reject[order[:k]] = True
    return reject


def bh_fdr_q(pvals):
    """Per-cell BH q-values (minimum FDR at which each test is rejected)."""
    pvals = np.asarray(pvals, dtype=float)
    n = len(pvals)
    q = np.full(n, np.nan)
    if n == 0:
        return q
    order = np.argsort(pvals)
    steps = pvals[order] * n / np.arange(1, n + 1)
    running = np.minimum.accumulate(steps[::-1])[::-1]
    q[order] = running
    return q


def chi2_gof_block(counts, expected):
    """chi2, dof, chi2_red, p for observed vs expected counts."""
    counts = np.asarray(counts, dtype=float)
    expected = np.asarray(expected, dtype=float)
    nonzero = expected > 0
    chi2 = float(np.sum((counts[nonzero] - expected[nonzero]) ** 2 / expected[nonzero]))
    dof = int(np.sum(nonzero) - 1)
    p = float(sp_stats.chi2.sf(chi2, dof)) if dof > 0 else float("nan")
    return chi2, dof, chi2 / dof if dof > 0 else float("nan"), p


def stats_from_deltas(deltas, J, alpha):
    """Primary + secondary statistics for a 1-D delta array."""
    n = int(len(deltas))
    mean = float(np.mean(deltas))
    std = float(np.std(deltas, ddof=1))
    edges = [-np.log(1 - j / J) for j in range(1, J)]
    counts, _ = np.histogram(deltas, bins=[0.0] + edges + [float("inf")])
    expected = np.full(J, n / J, dtype=float)
    chi2, dof, chi2_red, chi2_p = chi2_gof_block(counts, expected)
    ks_stat, ks_p = sp_stats.kstest(np.asarray(deltas, dtype=float), "expon", args=(0.0, 1.0))
    tail = []
    for t in [1, 2, 3, 4, 5]:
        exp_count = n * float(np.exp(-t))
        obs_count = int(np.sum(np.asarray(deltas) > t))
        se = float(np.sqrt(exp_count * (1 - np.exp(-t)))) if exp_count > 0 else 1.0
        z = (obs_count - exp_count) / se if se > 0 else 0.0
        p_two = float(2 * (1 - sp_stats.norm.cdf(abs(z))))
        tail.append({"t": t, "expected": float(exp_count), "observed": obs_count,
                     "z": float(z), "p": p_two, "fdr_q": None, "sig": None})
    return {
        "n_gaps": n, "mean_delta": mean, "std_delta": std,
        "chi2": chi2, "dof": dof, "chi2_red": chi2_red, "chi2_p": chi2_p,
        "ks_stat": float(ks_stat), "ks_p": float(ks_p),
        "counts": counts.tolist(), "expected": expected.tolist(), "edges": edges,
        "tail": tail, "G1": {"p": chi2_p, "rejected": None}, "G4": {"p": ks_p, "rejected": None},
    }


def run_block_gates(prereg, stats_by_block, deltas_by_block, lower_primes_by_block, alpha):
    """Compute G1..G4, controls C1..C7, and the decision."""
    P = prereg["parameters"]
    bs = P["bootstrap"]["n_draws"]
    bs_label = P["bootstrap"]["rng_label"]
    bs_seed = P["bootstrap"]["seed"]

    # G1: chi2 per block, BH-FDR across blocks
    g1_pvals = np.array([s["chi2_p"] for s in stats_by_block])
    g1_reject = bh_fdr(g1_pvals, alpha)
    for s, r in zip(stats_by_block, g1_reject):
        s["G1"] = {"p": float(s["chi2_p"]), "rejected": bool(r)}
    G1_pass = bool(not g1_reject.any())

    # G3: tail z per (block, t), BH-FDR across 20 cells
    tail_cells = [c for s in stats_by_block for c in s["tail"]]
    g3_pvals = np.array([c["p"] for c in tail_cells])
    g3_reject = bh_fdr(g3_pvals, alpha)
    g3_q = bh_fdr_q(g3_pvals)
    for cell, r, q in zip(tail_cells, g3_reject, g3_q):
        cell["sig"] = bool(r)
        cell["fdr_q"] = float(q)
    G3_pass = bool(not g3_reject.any())

    # G4 (KS) agreed with G1 after BH-FDR: per prereg, G4 pass = VERDICT EQUALITY.
    # Under H0 both methods return no rejection ([] == []); under a deviation both
    # must reject in the same blocks. KS rejecting is corroboration, not a gate error.
    g4_pvals = np.array([s["ks_p"] for s in stats_by_block])
    g4_reject = bh_fdr(g4_pvals, alpha)
    for s, r in zip(stats_by_block, g4_reject):
        s["G4"] = {"p": float(s["ks_p"]), "rejected": bool(r)}
    G4_pass = bool((g1_reject == g4_reject).all())

    # C3 seed-ladder pool launched BEFORE G2 so the ladder bootstraps run on other
    # cores while the parent computes the primary G2 bootstrap (each bootstrap is
    # fully deterministic: streams come from rng(label, seed) in every process).
    P = prereg["parameters"]
    ladder = P["seed_ladder"]["seeds"]
    ladder_label = P["seed_ladder"]["rng_label"]
    block_labels = [s["label"] for s in stats_by_block]
    c3_args = [(seed, block_labels, deltas_by_block, bs, ladder_label) for seed in ladder]
    c3_async = None
    c3_pool = None
    try:
        from multiprocessing import get_context
        c3_pool = get_context("spawn").Pool(processes=min(len(ladder), 5))
        c3_async = c3_pool.starmap_async(_c3_bootstrap_for_seed, c3_args)
    except Exception as exc:
        progress(f"C3 parallel pool unavailable ({exc!r}); will run serial")
        if c3_pool is not None:
            c3_pool.terminate()
            c3_pool.join()

    # G2: bootstrap percentile CI on mean(delta) per block
    rng_boot = rng(bs_label, bs_seed)
    G2_pass = True
    for s, d in zip(stats_by_block, deltas_by_block):
        resamples = bootstrap_means(d, bs, rng_boot)
        ci_low = float(np.percentile(resamples, 2.5))
        ci_high = float(np.percentile(resamples, 97.5))
        s["bootstrap"] = {"n_draws": bs, "rng_label": bs_label, "seed": bs_seed,
                          "mean": float(np.mean(resamples)),
                          "ci_low": ci_low, "ci_high": ci_high,
                          "contains_anchor": bool(ci_low <= 1.0 <= ci_high)}
        if not s["bootstrap"]["contains_anchor"]:
            G2_pass = False
    progress("G2 bootstrap complete")

    # collect the C3 ladder results
    seed_results = None
    if c3_async is not None:
        try:
            seed_results = c3_async.get()
        finally:
            c3_pool.close()
            c3_pool.join()
    if seed_results is None:
        progress("C3 ladder: serial fallback")
        seed_results = [_c3_bootstrap_for_seed(*a) for a in c3_args]
    ref_verdicts = seed_results[0]["block_verdicts"]
    C3_pass = bool(all(row["block_verdicts"] == ref_verdicts for row in seed_results[1:]))
    progress("C3 seed ladder complete")

    # C2: positive control (Gamma shape=0.5 scale=2 mean=1 var=4) — pipeline MUST flag
    rng_c2 = rng(P["positive_control"]["rng_label"], prereg["seed"])
    c2_results = []
    for b, s in zip(P["blocks"], stats_by_block):
        n = s["n_gaps"]
        sample = rng_c2.gamma(shape=0.5, scale=2.0, size=n)
        st = stats_from_deltas(sample, P["bins"]["J"], alpha)
        c2_results.append({"label": "C2_" + s["label"], "n": n, "chi2_p": st["chi2_p"], "ks_p": st["ks_p"]})
    c2_pvals = np.array([r["chi2_p"] for r in c2_results])
    c2_reject = bh_fdr(c2_pvals, alpha)
    C2_pass = bool(c2_reject.any())

    # C1: null/random control (iid Exp(1)) — pipeline MUST NOT flag
    rng_c1 = rng(P["null_control"]["rng_label"], prereg["seed"])
    c1_results = []
    for b, s in zip(P["blocks"], stats_by_block):
        n = s["n_gaps"]
        sample = rng_c1.exponential(1.0, size=n)
        st = stats_from_deltas(sample, P["bins"]["J"], alpha)
        c1_results.append({"label": "C1_" + s["label"], "n": n, "chi2_p": st["chi2_p"], "ks_p": st["ks_p"]})
    c1_pvals = np.array([r["chi2_p"] for r in c1_results])
    c1_reject = bh_fdr(c1_pvals, alpha)
    C1_pass = bool(not c1_reject.any())

    # C4: resolution variation J in {8, 10, 12} — chi2 GOF verdict (BH-FDR across blocks)
    #      must be identical across J
    c4_verdicts = {}
    for Jc in P["resolution_variation"]["J_values"]:
        pvals = []
        for s, d in zip(stats_by_block, deltas_by_block):
            st = stats_from_deltas(d, Jc, alpha)
            pvals.append(st["chi2_p"])
        rej = bh_fdr(np.array(pvals), alpha)
        c4_verdicts[str(Jc)] = rej.tolist()
    base = c4_verdicts["10"]
    C4_pass = bool(all(c4_verdicts[str(k)] == base for k in P["resolution_variation"]["J_values"]))

    # C5: method agreement (chi2 G1 vs KS G4 verdict vectors identical)
    C5_pass = bool(G4_pass)

    # C6: residue-class conditioning (falsification robustness)
    C6_pass, c6_detail = residue_conditioning(prereg, stats_by_block, deltas_by_block,
                                              lower_primes_by_block, alpha, g1_reject)

    # C7: independent implementation
    c7_pass, c7_detail = run_c7(prereg, stats_by_block)

    gates = {
        "G1": G1_pass, "G2": G2_pass, "G3": G3_pass, "G4": G4_pass,
        "C1": C1_pass, "C2": C2_pass, "C3": C3_pass, "C4": C4_pass,
        "C5": C5_pass, "C6": C6_pass, "C7": c7_pass,
    }

    # Decision per prereg decision_rule (frozen).
    primary_deviates = (not G1_pass) or (not G2_pass) or (not G3_pass)
    if all(gates.values()):
        decision = "H0_SUPPORTED"
        reason = ("all gates and controls pass; normalized prime gaps match Exp(1) within "
                  "bootstrap uncertainty across four disjoint ranges; C7 agrees block-by-block.")
    elif primary_deviates and c6_detail["survives_in_ranges"] >= 2 and c7_pass:
        decision = "H1_SUPPORTED"
        reason = (f"G1/G2/G3 rejected and the deviation survives residue-class conditioning in "
                  f"{c6_detail['survives_in_ranges']} disjoint ranges; C7 agrees -> reproducible deviation.")
    elif primary_deviates:
        decision = "INCONCLUSIVE"
        reason = (f"a primary gate rejected (G1={G1_pass} G2={G2_pass} G3={G3_pass}) but the "
                  f"deviation has not survived residue-conditioning robustness (survives in "
                  f"{c6_detail['survives_in_ranges']}/2 disjoint ranges); recorded honestly.")
    elif any(v is False for k, v in gates.items() if k not in ("G1", "G2", "G3", "G4", "C5")):
        decision = "INCONCLUSIVE"
        reason = "a control failed while the primary gates passed; experiment recorded honestly."
    else:
        decision = "INCONCLUSIVE"
        reason = "a gate was ambiguous; experiment recorded honestly."

    return gates, decision, reason, {
        "C1_results": c1_results, "C2_results": c2_results,
        "C3_seed_ladder": seed_results,
        "C4_J_values": P["resolution_variation"]["J_values"],
        "C4_verdicts": c4_verdicts,
        "C6_results": c6_detail,
        "C7_results": c7_detail,
    }


def residue_conditioning(prereg, stats_by_block, deltas_by_block, lower_primes_by_block,
                         alpha, g1_reject):
    """C6 — split each block's gaps by lower prime mod 12 (valid residues {1,5,7,11}).

    Gate part (a): no significant chi2 deviation after BH-FDR across
    (block, residue) cells. Part (b): if a primary gate rejected in a block,
    the deviation must also be seen in >= 2 disjoint ranges after conditioning.
    """
    P = prereg["parameters"]
    cond = P["residue_conditioning"]
    valid = cond["valid_residues"]
    min_p = cond["exclude_primes_below"]
    J = P["bins"]["J"]

    cells = []
    for s, d, lp in zip(stats_by_block, deltas_by_block, lower_primes_by_block):
        keep = lp >= min_p
        res = (lp % 12)[keep]
        dd = np.asarray(d, dtype=float)[keep]
        for r in valid:
            m = res == r
            if int(m.sum()) == 0:
                cells.append({"block": s["label"], "residue": r, "n": 0, "chi2": None,
                              "chi2_p": None, "ks_p": None})
                continue
            st = stats_from_deltas(dd[m], J, alpha)
            cells.append({"block": s["label"], "residue": r, "n": int(m.sum()),
                          "chi2": st["chi2"], "chi2_p": st["chi2_p"], "ks_p": st["ks_p"]})

    present = [c for c in cells if c["n"] > 0]
    chi2_p = np.array([c["chi2_p"] for c in present])
    reject = bh_fdr(chi2_p, alpha)
    for c, r in zip(present, reject):
        c["rejected_after_fdr"] = bool(r)
    C6_pass = bool(not reject.any())

    # Part (b): count blocks where a primary rejection survives conditioning.
    survival = 0
    for b_idx, (s, r) in enumerate(zip(stats_by_block, g1_reject)):
        if not r:
            continue
        blk_cells = [c for c in present if c["block"] == s["label"]]
        if any(c["rejected_after_fdr"] for c in blk_cells):
            survival += 1
    return C6_pass, {
        "cells": cells,
        "survives_in_ranges": survival,
        "note_part_a": "no significant chi2 after BH-FDR across (block, residue) cells",
        "note_part_b": ">=2 disjoint ranges must show the deviation after conditioning for H1",
        "excluded_primes_below": min_p,
        "valid_residues": valid,
    }


def run_c7(prereg, stats_by_block):
    """Run the independent implementation and compare verdicts + same-binning vectors."""
    indep = os.path.join(INVESTIGATION, "REPLICATION", "independent_check.py")
    report_path = os.path.join(REPLICATION_DIR, "C7_exp0008_report.json")
    if not os.path.exists(indep):
        return False, {"error": "independent_check.py not found"}
    # Sidecar carries the primary verdicts + same-binning vectors to the checker
    # (the checker is deliberately a separate path; it must not read our RESULTS).
    sidecar = {
        "g1_verdicts": [bool(s["G1"]["rejected"]) for s in stats_by_block],
        "chi2": [s["chi2"] for s in stats_by_block],
        "ks": [s["ks_stat"] for s in stats_by_block],
        "alpha": prereg["alpha"],
    }
    sidecar_path = os.path.join(REPLICATION_DIR, "_exp0008_primary_sidecar.json")
    with open(sidecar_path, "w", encoding="utf-8") as fh:
        json.dump(sidecar, fh, sort_keys=True)

    proc = subprocess.run(
        [sys.executable, indep, str(prereg["parameters"]["N_MAX"]),
         PREREG_DEFAULT, sidecar_path],
        cwd=INVESTIGATION, capture_output=True, text=True, timeout=7200)
    if proc.returncode != 0 or not os.path.exists(report_path):
        return False, {"returncode": proc.returncode, "stderr_tail": (proc.stderr or "")[-1500:]}
    c7 = json.load(open(report_path, encoding="utf-8"))
    agg = c7.get("agreement_with_primary", {})
    agreement = bool(agg.get("agreement")) if isinstance(agg, dict) else False
    detail = {
        "returncode": proc.returncode,
        "report_path": report_path,
        "agreement": agreement,
        "verdict_agreement": agg.get("verdict_agreement"),
        "chi2_diff_max": agg.get("chi2_diff_max"),
        "ks_diff_max": agg.get("ks_diff_max"),
        "chi2_diff_tol": 1e-9,
        "ks_diff_tol": 1e-9,
        "method": "C7 equal-width GOF (independent) + same-binning vector match",
    }
    return agreement, detail


def write_outputs(report, prereg, elapsed):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    raw_path = os.path.join(RESULTS_DIR, "EXP-0008_raw.json")
    results_path = os.path.join(RESULTS_DIR, "EXP-0008_results.json")
    raw = {
        "experiment_id": "EXP-0008", "question_id": "Q-M002", "hypothesis_id": "HYP-005",
        "prereg_path": PREREG_DEFAULT, "prereg_sha256": prereg.get("prereg_sha256"),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": prereg["seed"], "alpha": prereg["alpha"], "run_seconds": elapsed,
        "parameters": prereg["parameters"],
        "raw_statistics": report["primary_results"]["blocks"],
        "raw_controls": report["controls"],
        "raw_replication": report["replication"],
    }
    with open(raw_path, "w", encoding="utf-8") as fh:
        json.dump(raw, fh, indent=2, sort_keys=True)
    with open(results_path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
    return raw_path, results_path


def write_experiment_json(prereg, results_path, decision, reason, elapsed, gates):
    from engine.utilities.core import make_experiment_json
    record = make_experiment_json(
        experiment_id="EXP-0008",
        question="Q-M002",
        hypothesis="HYP-005",
        seed=prereg["seed"],
        parameters=prereg["parameters"],
        result={
            "decision": decision,
            "reason": reason,
            "primary_results_path": results_path,
            "raw_results_path": os.path.join(RESULTS_DIR, "EXP-0008_raw.json"),
            "prereg_sha256": prereg.get("prereg_sha256"),
            "gates": gates,
            "run_seconds": elapsed,
        },
        extra={"prereg_path": PREREG_DEFAULT},
    )
    out = os.path.join(INVESTIGATION, "CONFIG", "EXP-0008_experiment.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)
    return record, out


def write_reports(report, prereg, elapsed):
    blocks = report["primary_results"]["blocks"]
    gates = report["gates"]
    tech_lines = [
        "# TECHNICAL_EXP-0008 — prime gaps vs Poisson/Gallagher (Q-M002, HYP-005)",
        "",
        f"Experiment: EXP-0008 | Question: Q-M002 | Hypothesis: HYP-005 | Decision: **{report['decision']}**",
        f"Prereg: {PREREG_DEFAULT} (sha256 {report['meta']['prereg_sha256'][:16]}...) | "
        f"Seed: {prereg['seed']} | Alpha (BH-FDR): {prereg['alpha']} | Run: {elapsed:.2f}s",
        "",
        "## Primary result",
        "",
        "Normalized prime gaps `delta = (p_{i+1} - p_i) / ln(p_i)` in four disjoint ranges below 10^8 — "
        "null hypothesis H0 is Exp(1) (Gallagher/Poisson, 1976).",
        "",
        "| block | range | n | mean(delta) | std | chi2_red | chi2_p | KS_p | CI95 mean |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for s in blocks:
        bt = s.get("bootstrap", {})
        tech_lines.append(
            f"| {s['label']} | [{s['lo']}, {s['hi']}) | {s['n_gaps']} | {s['mean_delta']:.6f} | {s['std_delta']:.6f} | "
            f"{s['chi2_red']:.4f} | {s['chi2_p']:.4g} | {s['ks_p']:.4g} | [{bt.get('ci_low', float('nan')):.5f}, {bt.get('ci_high', float('nan')):.5f}] |"
        )
    combined = report["primary_results"]["combined"]
    tech_lines += [
        "",
        f"Combined chi2 = {combined['chi2']:.4f} (dof {combined['dof']}, chi2_red = {combined['chi2'] / combined['dof']:.4f}, p = {combined['p']:.4g}).",
        "",
        "## Every gate",
    ]
    for k, v in gates.items():
        tech_lines.append(f"- **{k}**: {v}")
    tech_lines += ["", "## Every control", ""]
    for k, v in report["controls"].items():
        tech_lines.append(f"- **{k}**: {'PASS' if v['pass'] else 'FAIL'} — {v.get('expected', '')}")
    tech_lines.append(f"- **C7 independent replication**: {'PASS' if report['replication']['C7_independent']['pass'] else 'FAIL'}")
    tech_lines += [
        "", "## Tail survival P(delta > t) vs exp(-t) (BH-FDR across 20 cells)", "",
        "| block | t | observed | expected | z | p | sig after FDR |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for s in blocks:
        for c in s["tail"]:
            tech_lines.append(f"| {s['label']} | {c['t']} | {c['observed']} | {c['expected']:.1f} | {c['z']:.3f} | {c['p']:.4g} | {c['sig']} |")
    tech_lines += [
        "", "## Falsification result", "", report["reason"],
        "Falsification protocol: FALSIFICATION/planning_checks.md.",
        "", "## Separated diagnostics (report-only, not gates)", "",
        f"- primes found: {report['diagnostics']['primes_count']:,}; sieve time: {report['diagnostics']['sieve_seconds']:.4f}s (deterministic; RNG unused).",
        f"- prereg sha256: {report['meta']['prereg_sha256']}",
        "- C7 uses an equal-width GOF for its independent verdict and a same-binning "
        "(exponential-quantile) vector for the tabulated 1e-9 tolerance (see "
        "state/EXP-0008_decisions.md for the prereg-contradiction resolution).",
        "- No evidence state above CONTROLLED; no novelty claimed.",
    ]
    os.makedirs(os.path.join(INVESTIGATION, "REPORT"), exist_ok=True)
    open(os.path.join(INVESTIGATION, "REPORT", "TECHNICAL_EXP-0008.md"), "w", encoding="utf-8") \
        .write("\n".join(tech_lines) + "\n")

    plain_lines = [
        "# PLAIN_EXP-0008 — prime gaps vs Poisson/Gallagher (Q-M002)",
        "",
        f"Decision: **{report['decision']}**. Question: do prime gaps follow the Poisson/Gallagher model?",
        "",
        "We counted the gaps between consecutive primes up to 100 million in four ranges, "
        "divided each gap by the log of its lower prime, and compared the result to an exponential "
        "distribution (the standard prediction for primes).",
        "",
        f"**Result:** {report['reason']}",
        "",
        "**Every gate:** " + ", ".join(f"{k}={v}" for k, v in gates.items()),
        "",
        ("**Replication:** an independent implementation (different prime generator, different binning, "
         "different statistics entry point) agreed block by block." if report["replication"]["C7_independent"]["pass"]
         else "**Replication:** pending."),
        "",
        "**What this does NOT prove:** nothing new in number theory; this reproduces a known result "
        "(Gallagher 1976) with honest uncertainty. No novelty is claimed.",
    ]
    open(os.path.join(INVESTIGATION, "REPORT", "PLAIN_EXP-0008.md"), "w", encoding="utf-8") \
        .write("\n".join(plain_lines) + "\n")


def append_registry(results_path, prereg, decision):
    reg_path = os.path.join(INVESTIGATION, "CONFIG", "registry.jsonl")
    row = json.dumps({
        "decision": decision,
        "experiment_id": "EXP-0008",
        "hypothesis": "HYP-005",
        "question": "Q-M002",
        "result_path": results_path,
        "seed": prereg["seed"],
        "prereg_sha256": prereg.get("prereg_sha256"),
    }, sort_keys=True)
    with open(reg_path, "a", encoding="utf-8") as fh:
        fh.write(row + "\n")


def sieve_primes(N_MAX):
    t0 = time.time()
    sieve = np.ones(N_MAX + 1, dtype=bool)
    sieve[0:2] = False
    for i in range(2, int(N_MAX ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = False
    primes = np.flatnonzero(sieve)
    return primes, time.time() - t0


def build_report(prereg):
    t0 = time.time()
    P = prereg["parameters"]
    blocks_param = P["blocks"]
    J = P["bins"]["J"]
    alpha = prereg["alpha"]
    N_MAX = P["N_MAX"]

    progress("sieving to N_MAX=%d ..." % N_MAX)
    primes, sieve_seconds = sieve_primes(N_MAX)
    progress(f"sieve done: {len(primes):,} primes in {sieve_seconds:.2f}s")

    block_primes = []
    for b in blocks_param:
        mask = (primes >= b["lo"]) & (primes < b["hi"])
        block_primes.append(primes[mask])

    deltas_by_block = []
    lower_primes_by_block = []
    stats_by_block = []
    for bp, b in zip(block_primes, blocks_param):
        lower = bp[:-1].astype(np.float64)
        upper = bp[1:].astype(np.float64)
        deltas = (upper - lower) / np.log(lower)
        deltas_by_block.append(deltas)
        lower_primes_by_block.append(lower)
        s = stats_from_deltas(deltas, J, alpha)
        s["label"] = b["label"]
        s["lo"] = b["lo"]
        s["hi"] = b["hi"]
        stats_by_block.append(s)
    progress("primary statistics computed")

    gates, decision, reason, extra = run_block_gates(
        prereg, stats_by_block, deltas_by_block, lower_primes_by_block, alpha)
    progress(f"gates/controls complete -> decision={decision}")

    combined = {
        "chi2": float(sum(s["chi2"] for s in stats_by_block)),
        "dof": int(sum(s["dof"] for s in stats_by_block)),
    }
    combined["chi2_red"] = combined["chi2"] / combined["dof"] if combined["dof"] else None
    combined["p"] = float(sp_stats.chi2.sf(combined["chi2"], combined["dof"]))

    report = {
        "meta": {
            "experiment_id": prereg["experiment_id"],
            "question_id": prereg["question_id"],
            "hypothesis_id": prereg["hypothesis_id"],
            "prereg_sha256": prereg.get("prereg_sha256"),
            "prereg_path": PREREG_DEFAULT,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "seed": prereg["seed"], "alpha": alpha,
            "run_seconds": round(time.time() - t0, 3),
            "software": version_info(),
            "machine": machine_info(),
        },
        "primary_results": {
            "blocks": stats_by_block,
            "combined": combined,
            "primary_verdict": gates,
        },
        "controls": {
            "C1_null_random": {"pass": gates["C1"], "detail": extra["C1_results"],
                               "expected": "no significant block (calibration)"},
            "C2_positive_control": {"pass": gates["C2"], "detail": extra["C2_results"],
                                    "expected": "at least one significant block (validates gate power)"},
            "C3_seed_ladder": {"pass": gates["C3"], "detail": extra["C3_seed_ladder"],
                               "expected": "identical per-block verdict across seeds"},
            "C4_resolution_variation": {"pass": gates["C4"], "detail": extra["C4_verdicts"],
                                        "expected": "identical verdict across J"},
            "C5_method_agreement": {"pass": gates["C5"], "expected": "chi2 vs KS agree after BH-FDR"},
            "C6_residue_conditioning": {"pass": gates["C6"], "detail": extra["C6_results"],
                                        "expected": "no significant deviation after conditioning"},
        },
        "replication": {"C7_independent": {"pass": gates["C7"],
                                           "detail": extra.get("C7_results", {})}},
        "diagnostics": {
            "primes_count": int(len(primes)),
            "sieve_seconds": round(sieve_seconds, 4),
            "N_MAX": N_MAX, "blocks": blocks_param,
            "note_report_only": "mean delta and std per block are descriptive; gates G1-G4 are the primary evidence.",
        },
        "gates": {k: ("PASS" if v else "FAIL") for k, v in gates.items()},
        "decision": decision,
        "reason": reason,
    }
    return report, stats_by_block, deltas_by_block


if __name__ == "__main__":
    path = PREREG_DEFAULT if len(sys.argv) < 2 else sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "run"
    prereg = load_prereg(path)
    P = prereg["parameters"]
    if mode == "validate":
        used = {
            "N_MAX": P["N_MAX"], "blocks": P["blocks"], "J": P["bins"]["J"],
            "alpha": prereg["alpha"], "bootstrap_seed": P["bootstrap"]["seed"],
            "bootstrap_draws": P["bootstrap"]["n_draws"], "seed_ladder": P["seed_ladder"]["seeds"],
            "positive_ctrl": P["positive_control"]["distribution"],
            "null_ctrl": P["null_control"]["distribution"],
            "resolution_values": P["resolution_variation"]["J_values"],
            "tail_t": P["secondary"]["tail"]["t_values"],
            "primary_stat": P["statistics"]["primary"],
            "secondary_stat": P["secondary"],
            "c7": P["independent_replication"],
        }
        print(json.dumps({
            "validation": "PASS",
            "source": path,
            "prereg_sha256": prereg.get("prereg_sha256"),
            "parameters_used": used,
        }, indent=2))
        sys.exit(0)

    progress("building report")
    report, stats, deltas = build_report(prereg)
    elapsed = report["meta"]["run_seconds"]
    raw_path, results_path = write_outputs(report, prereg, elapsed)
    record, exp_path = write_experiment_json(prereg, results_path, report["decision"],
                                             report["reason"], elapsed, report["gates"])
    write_reports(report, prereg, elapsed)
    append_registry(results_path, prereg, report["decision"])
    progress(f"wrote {results_path} / {raw_path} / {exp_path} / registry row")
    print(json.dumps({"experiment_id": "EXP-0008", "decision": report["decision"],
                      "reason": report["reason"], "gates": report["gates"],
                      "prereg_sha256": prereg.get("prereg_sha256"),
                      "raw": raw_path, "results": results_path,
                      "run_seconds": elapsed}, indent=2))