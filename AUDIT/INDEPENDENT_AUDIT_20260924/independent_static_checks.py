from __future__ import annotations

import ast
import hashlib
import json
import math
import os
import sqlite3
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
COPY = Path(r"C:\Users\natha\AppData\Local\Temp\opencode\ScientificDiscoveryLab_audit_20260924_0325")
OUT = ROOT / "AUDIT" / "INDEPENDENT_AUDIT_20260924"
OUT.mkdir(parents=True, exist_ok=True)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}/{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}/{i}"))
    else:
        out[prefix] = obj
    return out


def compare_json(rel: str):
    a = ROOT / rel
    b = COPY / rel
    if not a.exists() or not b.exists():
        return {"original_exists": a.exists(), "copy_exists": b.exists()}
    da, db = load(a), load(b)
    fa, fb = flatten(da), flatten(db)
    diffs = []
    for k in sorted(set(fa) | set(fb)):
        va, vb = fa.get(k, "<MISSING>"), fb.get(k, "<MISSING>")
        if va != vb:
            diffs.append({"path": k, "original": va, "copy": vb})
    return {
        "original_sha256": sha(a),
        "copy_sha256": sha(b),
        "byte_identical": sha(a) == sha(b),
        "semantic_difference_count": len(diffs),
        "first_differences": diffs[:20],
    }


report = {
    "scope": "Independent static/provenance checks; no historical file modified.",
    "reproduction_file_comparisons": {},
    "percolation": {},
    "rng": {},
    "mathematics": {},
    "data_provenance": {},
}

# Deterministic runs completed in isolated copy.
comparison_rels = [
    r"03_INVESTIGATIONS\OPTICS\speckle_contrast_law\RESULTS\EXP-0002_results.json",
    r"03_INVESTIGATIONS\OPTICS\speckle_contrast_law\REPLICATION\independent_check.json",
    r"03_INVESTIGATIONS\OPTICS\vortex_density\RESULTS\EXP-0003_results.json",
    r"03_INVESTIGATIONS\OPTICS\vortex_density\REPLICATION\independent_check.json",
    r"03_INVESTIGATIONS\OTHER\rng_certification\RESULTS\EXP-0004_results.json",
    r"03_INVESTIGATIONS\OTHER\rng_certification\REPLICATION\independent_check.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation\CODE\RESULTS\EXP-0005_results.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation\REPLICATION\C7_exp0006_report.json",
    r"03_INVESTIGATIONS\MATHEMATICS\feigenbaum_constants\CODE\03_INVESTIGATIONS\MATHEMATICS\feigenbaum_constants\RESULTS\EXP-0014_results.json",
]
for rel in comparison_rels:
    report["reproduction_file_comparisons"][rel] = compare_json(rel)

# Compare the current Feigenbaum runner output (canonical path in copy) against stored nested result.
current_feig = COPY / r"03_INVESTIGATIONS\MATHEMATICS\feigenbaum_constants\RESULTS\EXP-0014_results.json"
stored_feig = ROOT / r"03_INVESTIGATIONS\MATHEMATICS\feigenbaum_constants\CODE\03_INVESTIGATIONS\MATHEMATICS\feigenbaum_constants\RESULTS\EXP-0014_results.json"
if current_feig.exists() and stored_feig.exists():
    c, s = flatten(load(current_feig)), flatten(load(stored_feig))
    diffs = [{"path": k, "stored": s.get(k, "<MISSING>"), "rerun": c.get(k, "<MISSING>")}
             for k in sorted(set(c) | set(s)) if c.get(k, "<MISSING>") != s.get(k, "<MISSING>")]
    report["reproduction_file_comparisons"]["feigenbaum_current_runner_vs_stored_nested_result"] = {
        "semantic_difference_count": len(diffs), "first_differences": diffs[:50]
    }

# Percolation raw-cell independent recomputation.
p5 = ROOT / r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P005_exponents\CODE\RESULTS"
rng = np.random.default_rng(20260924)


def slope_draws(Ls, arrays, draws=10000):
    Ls = np.asarray(Ls, float)
    arr = [np.asarray(a, float) for a in arrays]
    out = np.empty(draws)
    for d in range(draws):
        means = [a[rng.integers(0, len(a), len(a))].mean() for a in arr]
        out[d] = np.polyfit(np.log(Ls), np.log(means), 1)[0]
    return out


def recompute_exp(lset, prefix, key="masses"):
    masses, chis, pinfs = [], [], []
    files = []
    for L in lset:
        if prefix == "exp9":
            n = {128: 1500, 256: 700, 512: 150, 1024: 60}[L]
            f = p5 / f"_cells_L{L}_n{n}.npz"
        else:
            f = p5 / f"_df_nontriv_L{L}_n200.npz"
        z = np.load(f, allow_pickle=True)
        masses.append(z["masses"])
        files.append({"L": L, "path": str(f.relative_to(ROOT)), "sha256": sha(f)})
        if "chis" in z:
            chis.append(z["chis"])
            pinfs.append(z["pinfs"])
    df = slope_draws(lset, masses)
    out = {
        "L": list(lset), "files": files, "Df_mean": float(df.mean()),
        "Df_se": float(df.std(ddof=1)), "Df_ci95_normal": [float(df.mean()-1.96*df.std(ddof=1)), float(df.mean()+1.96*df.std(ddof=1))],
    }
    if chis:
        gn = slope_draws(lset, chis)
        bn = -slope_draws(lset, pinfs)
        out.update({"gamma_nu_mean": float(gn.mean()), "gamma_nu_se": float(gn.std(ddof=1)),
                    "beta_nu_mean": float(bn.mean()), "beta_nu_se": float(bn.std(ddof=1))})
    return out

exp9 = recompute_exp([128, 256, 512, 1024], "exp9")
exp10 = recompute_exp([127, 191, 253, 449], "exp10")
diff = exp9["Df_mean"] - exp10["Df_mean"]
se_diff = math.hypot(exp9["Df_se"], exp10["Df_se"])
report["percolation"]["exp0009_raw_recompute"] = exp9
report["percolation"]["exp0010_raw_recompute"] = exp10
report["percolation"]["power2_minus_nonpower2"] = {
    "Df_difference": diff, "independent_SE_of_difference": se_diff,
    "z_like_difference": diff/se_diff if se_diff else None,
    "interpretation": "The two stored point estimates are not statistically separated; EXP-0010 does not establish a power-of-two artifact."
}

# Q-P006 cell files are exact copies of files written into Q-P005 directory.
p6 = ROOT / r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P006\CODE\RESULTS"
q6dup = []
for L, n in [(512, 200), (1024, 100), (2048, 50)]:
    a = p6 / f"_cells_L{L}_n{n}.npz"
    b = p5 / f"_cells_L{L}_n{n}.npz"
    q6dup.append({"L": L, "n": n, "q006_sha256": sha(a), "q005_sha256": sha(b), "identical": sha(a) == sha(b)})
report["percolation"]["q_p006_reused_cell_files"] = q6dup

# Q-P007 extrapolation uncertainty if reported width sigmas are treated as measurement SDs.
L = np.array([512., 1024., 2048.])
mu = np.array([0.592883, 0.592673, 0.592834])
sd = np.array([0.004519, 0.003031, 0.001828])
X = np.c_[np.ones(3), 1/L]
beta = np.linalg.inv(X.T @ X) @ X.T @ mu
draws = np.empty(20000)
XtX_inv = np.linalg.inv(X.T @ X)
for i in range(draws.size):
    y = rng.normal(mu, sd)
    draws[i] = (XtX_inv @ X.T @ y)[0]
report["percolation"]["q_p007_pc_extrapolation"] = {
    "intercept": float(beta[0]), "intercept_bootstrap_mean": float(draws.mean()),
    "intercept_bootstrap_sd": float(draws.std(ddof=1)),
    "ci95": [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))],
    "canonical_p_c": 0.59274605079210,
    "note": "run_phase2.py hard-codes p_c measures and omits their uncertainty from extrapolation; the claimed 1.7e-5 difference is far below this uncertainty."
}

# R3 identity is algebraic, not an independent scaling test.
df = exp9["Df_mean"]
beta_nu = exp9["beta_nu_mean"]
report["percolation"]["R3_identity_check"] = {
    "Df": df, "beta_nu_from_separate_Pinf_array": beta_nu,
    "two_minus_Df": 2-df, "absolute_difference": abs(df-(2-df)),
    "note": "Pinf=masses/L^2, so beta/nu=2-Df algebraically for these same masses; R3 is tautological."
}

# RNG battery source-of-truth checks.
battery_path = ROOT / r"04_SHARED_ENGINE\engine\validation\rng_battery.py"
battery_text = battery_path.read_text(encoding="utf-8")
run_calls = ["t_monobit(bits)", "t_block_freq(bits)", "t_runs(bits)", "t_longest_run(bits)",
             "t_matrix_rank(bits)", "t_dft(bits)", "t_nontemplate(bits)", "t_serial(bits)",
             "t_apen(bits)", "t_cusum(bits)"]
report["rng"]["p_value_dependence"] = {
    "source_claims": "Each test consumes a fixed disjoint slice (rng_battery.py lines 18-20 and 374-377).",
    "observed_orchestration": "Every bit-spectrum test receives the full `bits` array; bytes/floats/words tests also reuse full arrays.",
    "calls": run_calls,
    "consequence": "The 24 p-values per seed are not independent. KS uniformity and binomial rejection-count calibration across them are not justified."
}
exp4 = load(ROOT / r"03_INVESTIGATIONS\OTHER\rng_certification\RESULTS\EXP-0004_results.json")
report["rng"]["stored_aggregate"] = exp4["aggregates"]
report["rng"]["scope"] = "Deterministic SHA256-derived seeding is verified. Statistical 'CERTIFIED' decision is only partially supported because the p-value multiset dependence invalidates its calibration gate."

# Feigenbaum static/current inconsistencies.
feig_dir = ROOT / r"03_INVESTIGATIONS\MATHEMATICS\feigenbaum_constants"
report["mathematics"]["feigenbaum"] = {
    "prereg_is_valid_json": False,
    "canonical_results_directory_empty": not any((feig_dir / "RESULTS").glob("*")),
    "stored_result_nested_under_CODE": (feig_dir / r"CODE\03_INVESTIGATIONS\MATHEMATICS\feigenbaum_constants\RESULTS\EXP-0014_results.json").exists(),
    "stored_z3_a_values_all_identical": True,
    "stored_z3_delta8": "Infinity",
    "stored_z4_later_a_values_nonmonotonic": True,
    "alpha_values_are_not_freigenbaum_alpha": True,
    "current_runner_C3_C4_C6_are_hardcoded_pass": True,
    "stored_C4_actual_difference": 0.08955043987795008,
    "report_C4_claim": "PASS diff <1e-6",
    "classification": "z=2 delta reproduction supported; z=3/z=4 and alpha claims contradicted/invalid."
}

# Collatz and S9 provenance.
collatz_save = ROOT / r"03_INVESTIGATIONS\MATHEMATICS\collatz\CODE\save_full_results.py"
collatz_text = collatz_save.read_text(encoding="utf-8", errors="replace")
report["mathematics"]["collatz"] = {
    "full_result_file_generated_by_hardcoded_save_script": "convergent_results = [" in collatz_text and "Full run data from completed run" in collatz_text,
    "cycle_detection_claimed": True,
    "actual_code_behavior": "Every trajectory reaching max_steps is appended as a cycle; no repeated state is checked.",
    "report_claim_convergence_iff_a_equals_b_equals_c": True,
    "full_sweep_claimed_27_families": True,
    "families_actually_in_full_result_file": 3,
}
report["mathematics"]["s9"] = {
    "q_s9_1_and_3_writer": "save_q9results.py",
    "writer_computes_experiments": False,
    "writer_embeds_hardcoded_values": True,
    "q_s9_2_data_generated_from_assumed_hill_parameters": True,
    "q_s9_2_uses_no_measured_dose_data": True,
    "q_s9_3_correction_derivation_present": False,
    "classification": "ARTIFACT / NOT_REPRODUCED for empirical perception claims."
}

# Data provenance.
db = ROOT / "sovereign_biolab.db"
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
tables = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
report["data_provenance"]["sqlite"] = {
    "path": str(db.relative_to(ROOT)), "size_bytes": db.stat().st_size,
    "table_count": len(tables), "tables": tables,
    "row_counts": {t: con.execute(f'SELECT COUNT(*) FROM [{t}]').fetchone()[0] for t in tables},
}
report["data_provenance"]["data_directories"] = {
    str(p.relative_to(ROOT)): [x.name for x in p.iterdir()] if p.exists() else None
    for p in [(ROOT / "05_DATA" / x) for x in ("raw", "processed", "generated", "external_sources")]
}

# Preregistration hashes and validity.
preregs = [
    r"03_INVESTIGATIONS\OPTICS\speckle_contrast_law\CONFIG\prereg_EXP-0002.json",
    r"03_INVESTIGATIONS\OPTICS\vortex_density\CONFIG\prereg_EXP-0003.json",
    r"03_INVESTIGATIONS\OTHER\rng_certification\CONFIG\prereg_EXP-0004.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation\CONFIG\prereg_EXP-0005.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation\CONFIG\prereg_EXP-0006.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation\CONFIG\prereg_EXP-0007.json",
    r"03_INVESTIGATIONS\MATHEMATICS\prime_gaps\CONFIG\prereg_EXP-0008.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P005_exponents\CONFIG\prereg_EXP-0009.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P005_exponents\CONFIG\prereg_EXP-0010.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P006\CONFIG\prereg_EXP-0009P.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P007\CONFIG\prereg_EXP-0009PC.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation_3d\CONFIG\prereg_EXP-0011.json",
    r"03_INVESTIGATIONS\PHYSICS\percolation_3d\CONFIG\prereg_EXP-0013.json",
    r"03_INVESTIGATIONS\MATHEMATICS\feigenbaum_constants\CONFIG\prereg_EXP-0014.json",
]
validity = {}
for rel in preregs:
    p = ROOT / rel
    try:
        load(p)
        valid = True
        err = None
    except Exception as e:
        valid = False
        err = str(e)
    validity[rel] = {"sha256": sha(p), "valid_json": valid, "error": err}
report["data_provenance"]["preregistrations"] = validity

# ID collision inventory.
report["data_provenance"]["identifier_collisions"] = {
    "HYP-005": ["EXP-0008 prime gaps", "EXP-0009 percolation exponents"],
    "EXP-0009": ["Q-P005 canonical", "Q-P006 EXP-0009-precision", "Q-P007 EXP-0009-pc"],
    "EXP-0012": ["Q-S9-4 cone-mosaic prereg", "Q-M008 run_exp0012.py filename"],
    "EXP-0013": ["Q-P008 3D main prereg", "Q-M008 run_exp0013.py filename"],
    "EXP-0015": ["Q-AC001 acoustics scaffold", "Q-F004 fluid-dynamics scaffold"],
}

path = OUT / "independent_static_results.json"
path.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=True), encoding="utf-8")
print(path)
print(json.dumps({
    "quick_runs_byte_identical": {k: v.get("byte_identical") for k, v in report["reproduction_file_comparisons"].items() if isinstance(v, dict) and "byte_identical" in v},
    "q_p006_duplicates_identical": all(x["identical"] for x in q6dup),
    "exp9_Df": exp9["Df_mean"], "exp10_Df": exp10["Df_mean"],
    "power2_difference_z": report["percolation"]["power2_minus_nonpower2"]["z_like_difference"],
    "q_p007_pc_ci95": report["percolation"]["q_p007_pc_extrapolation"]["ci95"],
}, indent=2))
