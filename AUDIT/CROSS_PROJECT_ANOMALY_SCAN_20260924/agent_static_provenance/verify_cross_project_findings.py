"""Read-only cross-project verification for the static/provenance audit.

This verifier reads historical artifacts, performs small in-memory/temp-directory
checks, and writes only ``cross_project_verification.json`` beside this file.
It never invokes a historical result writer and never edits repository evidence.
"""
from __future__ import annotations

import ast
import datetime as dt
import hashlib
import json
import math
import re
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8-sig", errors="replace")


def read_json(path: str) -> Any:
    return json.loads(read_text(path))


def sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def lines(path: str) -> list[str]:
    return read_text(path).splitlines()


def line_ref(path: str, needle: str, occurrence: int = 1) -> str:
    hits = [i for i, line in enumerate(lines(path), 1) if needle in line]
    if len(hits) < occurrence:
        return f"{path}:<missing:{needle}>"
    return f"{path}:{hits[occurrence - 1]}"


def interp(ps: list[float], ws: list[float], denominator: str) -> float | None:
    below = [i for i, w in enumerate(ws) if w < 0.5]
    above = [i for i, w in enumerate(ws) if w > 0.5]
    if not below or not above:
        return None
    i, j = below[-1], above[0]
    p0, p1, w0, w1 = ps[i], ps[j], ws[i], ws[j]
    den = (w1 - p0) if denominator == "wrong" else (w1 - w0)
    if den == 0:
        return None
    return p0 + (0.5 - w0) * (p1 - p0) / den


def check_3d_boundary() -> dict[str, Any]:
    L, n = 4, 4**3
    flat_rows = [i // L for i in range(L * L)]
    flat_cols = [i % L for i in range(L * L)]
    top = [i for i, row in enumerate(flat_rows) if row == 0]
    bottom = [i for i, row in enumerate(flat_rows) if row == L - 1]
    left = [i for i, col in enumerate(flat_cols) if col == 0]
    right = [i for i, col in enumerate(flat_cols) if col == L - 1]
    expected_z0 = list(range(L * L))
    expected_zlast = list(range(L * L, L**3))
    return {
        "L": L,
        "N": n,
        "engine_length_rows_cols": L * L,
        "selected_top": top,
        "selected_bottom": bottom,
        "selected_left": left,
        "selected_right": right,
        "expected_z0": expected_z0,
        "expected_zlast": expected_zlast,
        "selected_bottom_touches_expected_zlast": bool(set(bottom) & set(expected_zlast)),
        "selected_bottom_max": max(bottom),
        "expected_zlast_min": min(expected_zlast),
        "source": line_ref("03_INVESTIGATIONS/PHYSICS/percolation/ENGINE/perc_engine.py", "rows = (np.repeat", occurrence=1),
        "c7_same_boundary_logic": line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/REPLICATION/independent_check_EXP0011.py", "only check z=0 plane"),
    }


def check_nested_tau() -> dict[str, Any]:
    # Exact shape returned by perc_engine for one realization.
    one_realization = [ [1, 2, 3] ]
    sizes_list = [one_realization]
    tails = [ss[1:] for ss in sizes_list]
    return {
        "engine_output_shape": "list containing one size array",
        "sizes_list_nested": type(sizes_list[0]).__name__,
        "tail_lengths": [len(x) for x in tails],
        "all_tails_empty": all(len(x) == 0 for x in tails),
        "source_append": line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", "sizes_list.append(cl_sizes)"),
        "source_tail": line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", "tsizes = [ss[1:]"),
        "stored_tau": read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_results.json")["tau"],
    }


def check_3d_samples() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in ("EXP-0011", "EXP-0013"):
        cfg = read_json(f"03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_{key}.json")
        configured = {k: int(v["n_each"]) for k, v in cfg["parameters"]["width_grid"].items()}
        effective = {k: max(4, v // 10) for k, v in configured.items()}
        out[key] = {
            "configured_width_n_each": configured,
            "effective_width_n_each_from_source_expression": effective,
            "configured_exponent_n_real": cfg["parameters"]["n_real"],
            "aligned_min_n_for_ragged_fit": min(int(v) for v in cfg["parameters"]["n_real"].values()),
        }
    out["source"] = line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", "max(4, n_each // 10)")
    out["fit_truncation_source"] = line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", "min_n = min(len(cells[L][\"masses\"])")
    return out


def check_exp0006() -> dict[str, Any]:
    result_path = "03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0006_results.json"
    data = read_json(result_path)
    rows: list[dict[str, Any]] = []
    for system, by_l in data["p50"].items():
        for l_s, meta in by_l.items():
            cells = [r for r in data["cells"][system] if int(r["L"]) == int(l_s)]
            ps = [float(r["p"]) for r in cells]
            count_key = "k_v" if system != "bond_wrap" else "k"
            ws = [float(r[count_key]) / float(r["n"]) for r in cells]
            rows.append({
                "system": system,
                "L": int(l_s),
                "stored_p50": float(meta["p50"]),
                "literal_denominator_p50": interp(ps, ws, "wrong"),
                "correct_denominator_p50": interp(ps, ws, "correct"),
            })
    return {
        "result": result_path,
        "rows": rows,
        "source_formula": line_ref("03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0006.py", "return float(p0 +"),
        "source_denominator_wrong": line_ref("03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0006.py", "(w1 - p0)"),
        "runner_mtime_utc": dt.datetime.fromtimestamp((ROOT / "03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0006.py").stat().st_mtime, dt.timezone.utc).isoformat(),
        "result_mtime_utc": dt.datetime.fromtimestamp((ROOT / result_path).stat().st_mtime, dt.timezone.utc).isoformat(),
        "root_wrapper": "CODE/run_percolation_exp0006.py:24-31",
        "stored_c2": data.get("c2"),
        "hardcoded_c2_source": line_ref("03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0006.py", "pair = abs(fss_out"),
        "c7_p50_gate_source": line_ref("03_INVESTIGATIONS/PHYSICS/percolation/REPLICATION/independent_check.py", "report[\"max_diff\"] = report[\"max_diff\"]"),
        "c7_report_has_p50_delta": "p50_delta_by_L" in read_text("03_INVESTIGATIONS/PHYSICS/percolation/REPLICATION/C7_exp0006_report.json"),
    }


def check_qm007() -> dict[str, Any]:
    data = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/q_m007_results.json")
    out = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/BHFR_40cell_results.json")
    report = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/REPORT/TECHNICAL_Q-M007.md")
    residuals = data["bin_summary"]["1"]["std_residuals_per_block"]
    literal = []
    exact = []
    for z in residuals:
        x = z * z
        zz = (x ** (1 / 6) * (1 - 2 / 9)) / math.sqrt(2 / 9)
        literal.append(0.5 * math.erfc(zz / math.sqrt(2)))
        exact.append(math.erfc(math.sqrt(x / 2)))
    return {
        "stored_mean_bin1": data["bin_summary"]["1"]["mean_std_residual"],
        "report_bin1_line": next((x for x in report.splitlines() if "| 1 |" in x), None),
        "stored_significant_cells": out["significant_cells"],
        "source_approximation": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/compute_bhfr_40cell.py", "Since we only have bin-level totals"),
        "source_p_formula": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/compute_bhfr_40cell.py", "p_value = 0.5 * math.erfc"),
        "literal_bin1_pvalues": literal,
        "exact_chi_square_upper_tail_bin1": exact,
        "stored_bin1_pvalues": [x["p_value"] for x in out["cells"] if x["bin"] == 1],
        "per_cell_obs_exp_present": all("obs" in data["bin_summary"][str(i)] and "exp" in data["bin_summary"][str(i)] for i in range(1, 11)),
    }


def check_hardcoded_audit_writer() -> dict[str, Any]:
    path = "save_audits.py"
    text = read_text(path)
    audit = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/AUDIT_Q006_Q007.md")
    report = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/REPORT/TECHNICAL_Q-M007.md")
    return {
        "json_load_calls": text.count("json.load"),
        "open_calls": text.count("open("),
        "hardcoded_qm007_verdict": "VERIFIED — H1_SUPPORTED CONFIRMED" in text,
        "hardcoded_no_40cell_fdr": "NO BH-FDR applied to the 40-cell" in text,
        "audit_says_no_40cell_fdr": "NO BH-FDR applied" in audit,
        "report_says_38_of_40": "38/40" in report,
        "writer_writes_audit": "AUDIT_Q006_Q007.md" in text,
        "writer_writes_phase1_literal": "phase1_preserved" in text,
    }


def check_qp007() -> dict[str, Any]:
    p = "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_q_p007.py"
    p2 = "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py"
    t1, t2 = read_text(p), read_text(p2)
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_results.json")
    return {
        "writers_target_same_result": t1.count('f"{EXP_ID}_results.json"') > 0 and t2.count('f"{EXP_ID}_results.json"') > 0,
        "bad_keys_in_first_runner": [k for k in ('["chis"]', '["pinfs"]', '["sizes"]') if k in t1],
        "engine_returns_cluster_sizes": 'out["cluster_sizes"]' in read_text("03_INVESTIGATIONS/PHYSICS/percolation/ENGINE/perc_engine.py"),
        "phase2_hardcoded_p_c_measures": "p_c_measures = {512:" in t2,
        "phase2_hardcoded_p_c_sigmas": "p_c_sig = {512:" in t2,
        "cache_has_sizes_array": False,
        "cache_loader_expects_sizes": '"sizes":' in t2,
        "stored_tau": result["exponents"]["tau"],
        "stored_tail_clusters": result["tau_raw"]["total_tail_clusters"],
        "first_writer": line_ref(p, 'o["chis"]'),
        "second_writer_output": line_ref(p2, 'out = os.path.join'),
    }


def check_q006() -> dict[str, Any]:
    pairs = [
        ["03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L512_n200.npz", "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L512_n200.npz"],
        ["03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L1024_n100.npz", "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L1024_n100.npz"],
        ["03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L2048_n50.npz", "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L2048_n50.npz"],
    ]
    return {
        "pairs": [{"paths": g, "hashes": [sha(x) for x in g], "identical": len({sha(x) for x in g}) == 1} for g in pairs],
        "prereg_no_reuse_claim": "No cells from EXP-0009/EXP-0010 reused" in read_text("03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CONFIG/prereg_EXP-0009P.json"),
        "copy_script": line_ref("fix_q006_cells.py", "shutil.copy2"),
        "inv_nu_stub": line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/run_q_p006.py", "pass"),
    }


def check_freeze_and_hashes() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "04_SHARED_ENGINE"))
    from engine.hypothesis_testing.prereg import freeze_config
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "prereg.json"
        freeze_config(experiment_id="X", hypothesis_id="H", question_id="Q", seed=1, params={"x": 1}, out_path=p)
        h1, o1 = sha(str(p.relative_to(ROOT))) if False else (hashlib.sha256(p.read_bytes()).hexdigest(), read_json(str(p.relative_to(ROOT))) if False else json.loads(p.read_text()))
        freeze_config(experiment_id="X", hypothesis_id="H", question_id="Q", seed=1, params={"x": 2}, out_path=p)
        h2 = hashlib.sha256(p.read_bytes()).hexdigest()
        o2 = json.loads(p.read_text())
    pairs = [
        ("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CONFIG/EXP-0002_experiment.json", "03_INVESTIGATIONS/OPTICS/speckle_contrast_law/RESULTS/EXP-0002_results.json"),
        ("03_INVESTIGATIONS/OPTICS/vortex_density/CONFIG/EXP-0003_experiment.json", "03_INVESTIGATIONS/OPTICS/vortex_density/RESULTS/EXP-0003_results.json"),
        ("03_INVESTIGATIONS/OTHER/rng_certification/CONFIG/EXP-0004_experiment.json", "03_INVESTIGATIONS/OTHER/rng_certification/RESULTS/EXP-0004_results.json"),
        ("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CONFIG/EXP-0008_experiment.json", "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/RESULTS/EXP-0008_results.json"),
    ]
    rows = []
    for c, r in pairs:
        cfg, res = read_json(c), read_json(r)
        recorded = cfg.get("result_hash")
        semantic = hashlib.sha256(json.dumps(cfg.get("result"), sort_keys=True).encode()).hexdigest()
        rows.append({"config": c, "result": r, "recorded": recorded, "semantic_config_result": semantic, "file_bytes": sha(r), "recorded_matches_semantic": recorded == semantic, "recorded_matches_file": recorded == sha(r)})
    return {
        "immutable_helper_source": line_ref("04_SHARED_ENGINE/engine/hypothesis_testing/prereg.py", "Write a frozen, immutable"),
        "overwrite_source": line_ref("04_SHARED_ENGINE/engine/hypothesis_testing/prereg.py", "with open(out_path, \"w\""),
        "temp_first_hash": h1,
        "temp_second_hash": h2,
        "temp_changed": h1 != h2,
        "temp_first_parameters": o1["parameters"],
        "temp_second_parameters": o2["parameters"],
        "hash_rows": rows,
        "hash_helper": line_ref("04_SHARED_ENGINE/engine/utilities/core.py", "sha256_text(json.dumps(result"),
    }


def check_feigenbaum() -> dict[str, Any]:
    prereg = "03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CONFIG/prereg_EXP-0014.json"
    nested = "03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/RESULTS/EXP-0014_results.json"
    try:
        read_json(prereg)
        valid = True
        error = None
    except Exception as exc:
        valid, error = False, f"{type(exc).__name__}: {exc}"
    result = read_json(nested)
    return {
        "prereg_valid": valid,
        "prereg_error": error,
        "canonical_results_entries": len(list((ROOT / "03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/RESULTS").iterdir())),
        "nested_result_exists": (ROOT / nested).exists(),
        "readme_says": next((x for x in lines("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/README.md") if "Status:" in x), None),
        "registry_date": next((x for x in lines("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CONFIG/registry.jsonl") if "date" in x), None),
        "experiment_date": read_json("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CONFIG/experiment.json").get("date"),
        "z3_unique_a": len(set(result["z3"]["a_vals"].values())),
        "z3_delta8": str(result["z3"]["deltas"].get("8")),
        "z4_later_rollback": result["z4"]["a_vals"].get("7") == result["z4"]["a_vals"].get("8"),
        "stored_c4": result.get("controls", {}).get("C4"),
        "hardcoded_control_source": [line_ref("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/run_feigenbaum.py", 'controls["C3"]'), line_ref("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/run_feigenbaum.py", 'controls["C4"]'), line_ref("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/run_feigenbaum.py", 'controls["C6"]')],
    }


def check_qm008() -> dict[str, Any]:
    p = np = None
    import numpy as np  # type: ignore
    code = "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py"
    result = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/RESULTS/Q-M008_1e8_results.json")
    source = read_text(code)
    primes = np.array([3, 5, 7, 11], dtype=float)
    upper = (primes[1:] - primes[:-1]) / np.log(primes[1:])
    lower = (primes[1:] - primes[:-1]) / np.log(primes[:-1])
    # Concrete counterexample for rank-wise BH versus step-up BH.
    pv = np.array([0.004, 0.006, 0.02])
    order = np.argsort(pv)
    thresholds = np.arange(1, len(pv) + 1) / len(pv) * 0.01
    rank = pv[order] <= thresholds
    valid = np.flatnonzero(rank)
    k = int(valid.max() + 1) if valid.size else 0
    proper = np.zeros(len(pv), dtype=bool)
    proper[order[:k]] = True
    wrong = np.zeros(len(pv), dtype=bool)
    for i, idx in enumerate(order):
        wrong[idx] = rank[i]
    return {
        "code_gap_formula": line_ref(code, "log_p = np.log(primes[1:]"),
        "report_gap_formula": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/REPORT/TECHNICAL_Q-M008.md", "delta = (p_{i+1} - p_i) / ln(p_i)"),
        "example_upper_log": upper.tolist(),
        "example_lower_log": lower.tolist(),
        "code_block_lines": [line_ref(code, "blocks = ["), line_ref(code, '"lo": limit // 100')],
        "stored_zero_p_values": sum(1 for x in [result["overall"]["chi2"]["p_value"]] + [b["chi2"]["p_value"] for b in result["blocks"] if "chi2" in b] if x == 0.0),
        "p_value_formula": line_ref(code, "p_value = 1 - sp_stats.chi2.cdf"),
        "bh_implementation": line_ref(code, "significant = sorted_p <= critical"),
        "bh_counterexample": {"p": pv.tolist(), "rankwise": wrong.tolist(), "proper_step_up": proper.tolist()},
    }


def walk(obj: Any, path: str = "$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def check_optics_floor() -> dict[str, Any]:
    out = {}
    for name, key in [("EXP-0002", "p_two_sided_null_r_eq_1"), ("EXP-0003", "p_two_sided_ratio_eq_1")]:
        path = "03_INVESTIGATIONS/OPTICS/speckle_contrast_law/RESULTS/EXP-0002_results.json" if name == "EXP-0002" else "03_INVESTIGATIONS/OPTICS/vortex_density/RESULTS/EXP-0003_results.json"
        eps = float(__import__("numpy").finfo(float).eps)
        hits = [(p, v) for p, v in walk(read_json(path)) if p.endswith(key) and v == eps]
        out[name] = {"epsilon": eps, "floor_count": len(hits), "paths": [p for p, _ in hits[:12]]}
    out["source_speckle"] = line_ref("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CODE/run_speckle_contrast.py", "p = min(1.0, p + np.finfo(float).eps)")
    out["source_vortex"] = line_ref("03_INVESTIGATIONS/OPTICS/vortex_density/CODE/run_vortex_density.py", "p = min(1.0, p + np.finfo(float).eps)")
    return out


def check_s9() -> dict[str, Any]:
    source = read_text("save_q9results.py")
    tree = ast.parse(source)
    literals = []
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"q_s9_1_results", "q_s9_3_results"}:
                    literals.append(target.id)
    dose = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py")
    return {
        "hardcoded_writer_targets": literals,
        "writer_has_input_read": "json.load" in source or "read_csv" in source or "open(" in source.split("with open", 1)[0],
        "writer_lines": [line_ref("save_q9results.py", "q_s9_1_results = {"), line_ref("save_q9results.py", "q_s9_3_results = {")],
        "dose_declares_simulated": "Simulated dose-response data" in dose,
        "dose_generator": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", "def generate_dose_response"),
        "dose_stores_true_parameters": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", '"ec50": TRUE_EC50'),
        "report_claims_reproduction_script": "q_s9_1_complexity.py" in read_text("03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-1.md"),
        "reproduction_script_exists": (ROOT / "CODE/dmt-laser-s9-battery/q_s9_1_complexity.py").exists(),
    }


def check_registry_and_data() -> dict[str, Any]:
    registry = read_text("EXPERIMENT_REGISTRY.md")
    table_registry = registry.split("## Entries", 1)[0]
    current = read_text("CURRENT_STATUS.md")
    plan = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/PLAN.md")
    feig_readme = read_text("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/README.md")
    dirs = {}
    for d in ("raw", "processed", "generated", "external_sources"):
        dirs[d] = len(list((ROOT / "05_DATA" / d).iterdir()))
    db_counts = {}
    db = ROOT / "sovereign_biolab.db"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    tables = [r[0] for r in con.execute("select name from sqlite_master where type='table'").fetchall()]
    for t in tables:
        db_counts[t] = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    con.close()
    return {
        "registry_table_lines": [line_ref("EXPERIMENT_REGISTRY.md", "| EXP-0011 |"), line_ref("EXPERIMENT_REGISTRY.md", "| EXP-0014 |")],
        "registry_omits_0012_0013_0015": all(f"EXP-{x}" not in table_registry for x in ("0012", "0013", "0015")),
        "registry_0011_status_lines": [x for x in registry.splitlines() if "EXP-0011" in x][:4],
        "current_status_0011": [x for x in current.splitlines() if "EXP-0011" in x or "Q-P008" in x][:6],
        "qm008_plan_status": [x for x in plan.splitlines() if "Status" in x][:2],
        "qm008_results_exist": (ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/RESULTS/Q-M008_1e9_results.json").exists(),
        "feigenbaum_readme_status": [x for x in feig_readme.splitlines() if "Status:" in x],
        "data_directory_entry_counts": dirs,
        "sqlite_table_count": len(tables),
        "sqlite_all_row_counts_zero": all(v == 0 for v in db_counts.values()),
        "sqlite_row_counts": db_counts,
        "known_id_collisions": {"HYP-005": ["prime gaps", "percolation"], "EXP-0009": ["Q-P005", "Q-P006", "Q-P007"], "EXP-0012": ["Q-S9-4", "Q-M008 run_exp0012.py"], "EXP-0013": ["Q-P008 3D", "Q-M008 run_exp0013.py"], "EXP-0015": ["acoustics scaffold", "fluid scaffold"]},
    }


def check_exp0007() -> dict[str, Any]:
    prereg = read_json("03_INVESTIGATIONS/PHYSICS/percolation/CONFIG/prereg_EXP-0007.json")
    summary = read_json("03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0007_summary.json")
    report = read_text("03_INVESTIGATIONS/PHYSICS/percolation/REPORT/TECHNICAL_EXP-0007.md")
    return {
        "prereg_says_exp0006_never_executed": "EXP-0006 (never executed)" in prereg["note"],
        "registry_says_exp0006_controlled": "| EXP-0006 |" in read_text("EXPERIMENT_REGISTRY.md") and "CONTROLLED" in read_text("EXPERIMENT_REGISTRY.md"),
        "prereg_bootstrap_draws": prereg["parameters"]["bootstrap"]["n_draws"],
        "stored_effective_bootstrap_draws": summary["estimator_diagnostics"]["width_route"]["bootstrap"]["n_draws"],
        "report_claims_500_draws": "500 draws" in report,
        "prereg_note": prereg["note"],
    }


def check_exp0010_gate_drift() -> dict[str, Any]:
    cfg = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CONFIG/prereg_EXP-0010.json")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/EXP-0010_results.json")
    source = read_text("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/run_exp0010.py")
    return {
        "prereg_all_non_power2_criterion": cfg["predictions"]["D_f"]["test"],
        "prereg_C7_required": "C7" in cfg["gates"],
        "result_D_f_measured": result["primary_results"]["D_f"]["measured"],
        "result_D_f_pass": result["primary_results"]["D_f"]["pass"],
        "result_gate_keys": list(result["primary_results"]["gates"].keys()),
        "result_per_L_keys": list(result["primary_results"]["D_f"]["per_L"].keys()),
        "source_single_pooled_fit": "Df_draws = bootstrap_slope(logx, mmat" in source,
        "source_decision_uses_pooled_Df_only": "df_in_tol = abs(Df - Df_EX)" in source,
        "prereg": "03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CONFIG/prereg_EXP-0010.json:1",
        "source": line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/run_exp0010.py", "Df_draws = bootstrap_slope"),
    }


def check_exp0009_same_stream_c7() -> dict[str, Any]:
    report = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/REPLICATION/C7_exp0009_report.json")
    source = read_text("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/REPLICATION/independent_check_exp0009.py")
    return {
        "report_streams": report.get("streams"),
        "subsample_n": 40,
        "per_realization_identical": report.get("per_realization_Mmax_identical"),
        "C7_pass": report.get("pass"),
        "source_doc_quote": "IDENTICAL frozen streams (same G_LAB rng label + seed, first 40 realizations)",
        "source_line": line_ref("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/REPLICATION/independent_check_exp0009.py", "IDENTICAL frozen streams"),
    }


def check_qm007_first_bin() -> dict[str, Any]:
    exp = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/RESULTS/EXP-0008_results.json")
    q = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/q_m007_results.json")
    edge = -math.log(1 - 1 / 10)
    lower = 2 / math.log(10**8)
    return {
        "first_edge": edge,
        "structural_lower_bound_for_odd_prime_gaps_to_1e8": lower,
        "edge_margin": lower - edge,
        "EXP0008_first_bin_counts": [b["counts"][0] for b in exp["primary_results"]["blocks"]],
        "Q-M007_bin1_observed": q["bin_summary"]["1"]["obs_total"],
        "Q-M007_bin1_expected": q["bin_summary"]["1"]["exp_total"],
        "source_gap_definition": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CODE/run_prime_gaps.py", "deltas = (upper - lower) / np.log(lower)"),
    }


def check_s9_unit_mismatch() -> dict[str, Any]:
    baseline, max_infl = 0.205, 0.483
    saturation = baseline + max_infl
    intended_relative_saturation = baseline * (1 + max_infl)
    source = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py")
    return {
        "formula_saturation": saturation,
        "formula_relative_increase": (saturation - baseline) / baseline,
        "report_intended_relative_saturation": intended_relative_saturation,
        "source_relative_comment": "30.4/20.5 - 1 = 48.3%",
        "source_formula": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", "return baseline + (max_inflation"),
        "source_true_parameter_write": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", '"max_inflation": MAX_INFL'),
    }


def check_qm008_future_sieve() -> dict[str, Any]:
    import importlib.util
    path = ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_1e10.py"
    spec = importlib.util.spec_from_file_location("qm008_run_1e10_probe", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _gaps, n_primes = mod.segmented_gap_stats(1000, segment_size=1000)
    # Independent direct sieve for the same small sanity limit.
    import numpy as np
    is_prime = np.ones(1001, dtype=bool)
    is_prime[:2] = False
    for p in range(2, int(math.isqrt(1000)) + 1):
        if is_prime[p]:
            is_prime[p*p::p] = False
    expected = int(is_prime.sum())
    return {
        "limit": 1000,
        "segmented_runner_prime_count": int(n_primes),
        "direct_sieve_prime_count": expected,
        "missing_primes": expected - int(n_primes),
        "source_marking": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_1e10.py", "if start == p:"),
        "alternate_runner_pass_branch": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0013.py", "pass"),
    }


def check_application_layer() -> dict[str, Any]:
    out: dict[str, Any] = {}
    try:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from src.molecular.engine import MoleculeInspector
        m = MoleculeInspector("CCO")
        out["ethanol_formal_charge_method_value"] = m.get_formal_charge()
        try:
            m.get_2d_structure()
            out["get_2d_structure_error"] = None
        except Exception as exc:
            out["get_2d_structure_error"] = f"{type(exc).__name__}: {str(exc).splitlines()[0]}"
    except Exception as exc:
        out["molecular_import_error"] = f"{type(exc).__name__}: {exc}"
    out["formal_charge_source"] = line_ref("src/molecular/engine.py", "Descriptors.MaxAbsPartialCharge")
    out["dead_assertion"] = line_ref("tests/unit/test_plant_engine.py", "or True")
    return out


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    evidence = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "root": str(ROOT),
        "checks": {
            "3d_boundary": check_3d_boundary(),
            "3d_nested_tau": check_nested_tau(),
            "3d_sample_sizes": check_3d_samples(),
            "exp0006": check_exp0006(),
            "qm007": check_qm007(),
            "hardcoded_audit_writer": check_hardcoded_audit_writer(),
            "qp007": check_qp007(),
            "q006": check_q006(),
            "freeze_and_hashes": check_freeze_and_hashes(),
            "feigenbaum": check_feigenbaum(),
            "qm008": check_qm008(),
            "optics_pvalue_floor": check_optics_floor(),
            "s9": check_s9(),
            "s9_unit_mismatch": check_s9_unit_mismatch(),
            "qm008_future_sieve": check_qm008_future_sieve(),
            "qm007_first_bin": check_qm007_first_bin(),
            "exp0010_gate_drift": check_exp0010_gate_drift(),
            "exp0009_same_stream_c7": check_exp0009_same_stream_c7(),
            "registry_and_data": check_registry_and_data(),
            "exp0007": check_exp0007(),
            "application_layer": check_application_layer(),
        },
    }
    (OUT / "cross_project_verification.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT / "cross_project_verification.json"), "checks": len(evidence["checks"])}, indent=2))


if __name__ == "__main__":
    main()
