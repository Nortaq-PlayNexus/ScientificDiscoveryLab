"""Read-only verification cases for the claims/data cross-project scan.

This script is intentionally confined to reads of historical artifacts.  The only
writes are the JSON/log files beside this script.  It never calls a historical
runner that writes results, registries, preregistrations, or reports.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import re
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
OUT = Path(__file__).resolve().parent


def p(rel: str) -> Path:
    return ROOT / rel


def r(rel: str) -> str:
    return rel.replace("\\", "/")


def read_text(rel: str) -> str:
    return p(rel).read_text(encoding="utf-8-sig", errors="replace")


def read_json(rel: str) -> Any:
    return json.loads(read_text(rel))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def line_ref(rel: str, needle: str, occurrence: int = 1) -> str:
    hits = [i for i, line in enumerate(read_text(rel).splitlines(), 1) if needle in line]
    if len(hits) < occurrence:
        return f"{rel}:<not found:{needle!r}>"
    return f"{rel}:{hits[occurrence - 1]}"


def excerpt(rel: str, start: int, end: int) -> list[str]:
    lines = read_text(rel).splitlines()
    return [f"{i}: {lines[i - 1]}" for i in range(start, min(end, len(lines)) + 1)]


def walk(obj: Any, path: str = "$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, obj


def case_hash_contract() -> dict[str, Any]:
    pairs = [
        ("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CONFIG/EXP-0002_experiment.json", "03_INVESTIGATIONS/OPTICS/speckle_contrast_law/RESULTS/EXP-0002_results.json"),
        ("03_INVESTIGATIONS/OPTICS/vortex_density/CONFIG/EXP-0003_experiment.json", "03_INVESTIGATIONS/OPTICS/vortex_density/RESULTS/EXP-0003_results.json"),
        ("03_INVESTIGATIONS/OTHER/rng_certification/CONFIG/EXP-0004_experiment.json", "03_INVESTIGATIONS/OTHER/rng_certification/RESULTS/EXP-0004_results.json"),
        ("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CONFIG/EXP-0008_experiment.json", "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/RESULTS/EXP-0008_results.json"),
    ]
    rows = []
    for cfg_rel, result_rel in pairs:
        cfg = read_json(cfg_rel)
        recorded = cfg.get("result_hash")
        canonical = hashlib.sha256(json.dumps(cfg.get("result"), sort_keys=True).encode("utf-8")).hexdigest()
        file_hash = sha(p(result_rel))
        rows.append({
            "config": cfg_rel,
            "result": result_rel,
            "recorded": recorded,
            "canonical_loaded_result": canonical,
            "file_sha256": file_hash,
            "recorded_matches_canonical": recorded == canonical,
            "recorded_matches_file": recorded == file_hash,
        })
    return {
        "rows": rows,
        "helper": line_ref("04_SHARED_ENGINE/engine/utilities/core.py", '"result_hash"'),
        "contract": excerpt("REPRODUCIBILITY.md", 43, 54),
    }


def case_freeze_overwrite() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "04_SHARED_ENGINE"))
    from engine.hypothesis_testing.prereg import freeze_config
    with tempfile.TemporaryDirectory(dir=str(OUT), prefix="_tmp_freeze_") as td:
        target = Path(td) / "prereg.json"
        freeze_config(experiment_id="X", hypothesis_id="H", question_id="Q", seed=1, params={"x": 1}, out_path=target)
        first = sha(target)
        first_obj = read_json(str(target.relative_to(OUT)).replace("\\", "/")) if False else json.loads(target.read_text(encoding="utf-8"))
        freeze_config(experiment_id="X", hypothesis_id="H", question_id="Q", seed=1, params={"x": 2}, out_path=target)
        second = sha(target)
        second_obj = json.loads(target.read_text(encoding="utf-8"))
        return {
            "first_hash": first,
            "second_hash": second,
            "changed": first != second,
            "first_params": first_obj["parameters"],
            "second_params": second_obj["parameters"],
            "helper_contract": excerpt("04_SHARED_ENGINE/engine/hypothesis_testing/prereg.py", 27, 46),
            "callers": [
                line_ref("03_INVESTIGATIONS/OTHER/rng_certification/CODE/run_rng_cert.py", "freeze_config("),
                line_ref("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CODE/run_speckle_contrast.py", "freeze_config("),
            ],
        }


def case_empty_data() -> dict[str, Any]:
    dirs = {}
    for name in ["05_DATA", "06_RESULTS", "07_REPORTS", "08_REPLICATION", "99_ARCHIVE"]:
        q = p(name)
        files = [x for x in q.rglob("*") if x.is_file()] if q.exists() else []
        dirs[name] = {"exists": q.exists(), "file_count": len(files), "bytes": sum(x.stat().st_size for x in files)}
    con = sqlite3.connect(p("sovereign_biolab.db"))
    tables = []
    for (name,) in con.execute("select name from sqlite_master where type='table' order by name"):
        n = con.execute('select count(*) from "' + name.replace('"', '""') + '"').fetchone()[0]
        tables.append({"name": name, "rows": n})
    integrity = con.execute("pragma integrity_check").fetchone()[0]
    con.close()
    return {"directories": dirs, "db_integrity": integrity, "db_tables": tables, "db_table_count": len(tables), "db_total_rows": sum(x["rows"] for x in tables)}


def case_registry() -> dict[str, Any]:
    reg = read_text("EXPERIMENT_REGISTRY.md")
    table_ids = re.findall(r"^\| (EXP-\d+) \|", reg, flags=re.M)
    qtext = read_text("QUESTIONS.md")
    q_rows = re.findall(r"^\| (Q-[A-Z0-9-]+) \|.*?\| (OPEN|PLANNED|ANSWERED_LOCALLY|INVESTIGATING|CLOSED|COMPLETE|H0_SUPPORTED|CONTROLLED|PARTIALLY_ANSWERED|WITHDRAWN|CLOSED_LITERATURE) \|", qtext, flags=re.M)
    return {
        "root_registry_table_ids": table_ids,
        "root_registry_table_count": len(table_ids),
        "audit_claim": line_ref("AUDIT/EXPERIMENT_REGISTER.md", "Total experiments:"),
        "question_rows_of_interest": [x for x in q_rows if x[0] in {"Q-M008", "Q-S9-1", "Q-S9-2", "Q-S9-3", "Q-P008"}],
        "current_status_claims": {
            "q_s9": line_ref("CURRENT_STATUS.md", "Q-S9-1, Q-S9-2, Q-S9-3"),
            "q_m008": line_ref("QUESTIONS.md", "| Q-M008 |"),
        },
        "inventory_collisions": excerpt("AUDIT/PROJECT_INVENTORY.md", 88, 96),
    }


def case_external() -> dict[str, Any]:
    idx = read_text("05_EXTERNAL_RESEARCHER_DOSSIER/DATA_INDEX.md")
    outside = Path(r"C:\Users\natha\code\coherent-optical-ai-sandbox")
    return {
        "data_index_base_paths": excerpt("05_EXTERNAL_RESEARCHER_DOSSIER/DATA_INDEX.md", 10, 25),
        "claim": line_ref("05_EXTERNAL_RESEARCHER_DOSSIER/KEY_RESULTS.md", "Every number is from"),
        "outside_path_exists": outside.exists(),
        "outside_path_under_audited_root": False,
        "relative_sandbox_path_under_root_exists": (ROOT / "code" / "coherent-optical-ai-sandbox").exists(),
    }


def case_application() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT))
    from rdkit import Chem
    from src.molecular.engine import MoleculeInspector
    ethanol = MoleculeInspector("CCO")
    formal = ethanol.get_formal_charge()
    actual = Chem.GetFormalCharge(Chem.MolFromSmiles("CCO"))
    try:
        ethanol.get_2d_structure()
        depiction_error = None
    except Exception as exc:
        depiction_error = {"type": type(exc).__name__, "message": str(exc)[:1000]}
    return {
        "formal_charge_reported": formal,
        "actual_formal_charge": actual,
        "descriptor_source": excerpt("src/molecular/engine.py", 77, 83),
        "depiction_error": depiction_error,
        "tautological_assertion": line_ref("tests/unit/test_plant_engine.py", "or True"),
        "tests_for_formal_charge": [x for x in ["formal_charge", "get_2d_structure"] if x in "\n".join(read_text("tests/unit/test_molecular_engine.py").splitlines())],
    }


def case_exp0006() -> dict[str, Any]:
    result_rel = "03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0006_results.json"
    data = read_json(result_rel)
    rows = []
    for system, cells in data["cells"].items():
        for L in sorted({int(x["L"]) for x in cells}):
            cc = [x for x in cells if int(x["L"]) == L]
            ps = np.array([float(x["p"]) for x in cc])
            ks = np.array([float(x.get("k", x.get("k_v"))) for x in cc])
            ns = np.array([float(x["n"]) for x in cc])
            W = ks / ns
            below = np.flatnonzero(W < 0.5)
            above = np.flatnonzero(W >= 0.5)
            if not len(below) or not len(above):
                continue
            i, j = int(below[-1]), int(above[0])
            p0, p1, w0, w1 = ps[i], ps[j], W[i], W[j]
            wrong = float(p0 + (0.5 - w0) * (p1 - p0) / (w1 - p0))
            correct = float(p0 + (0.5 - w0) * (p1 - p0) / (w1 - w0))
            rows.append({"system": system, "L": L, "wrong": wrong, "correct": correct, "stored": float(data["p50"][system][str(L)]["p50"]), "abs_wrong_correct": abs(wrong - correct)})
    return {
        "runner": excerpt("03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0006.py", 51, 64),
        "c2": excerpt("03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0006.py", 290, 294),
        "result_c2": data.get("c2"),
        "rows": rows,
        "max_wrong_correct": max(x["abs_wrong_correct"] for x in rows),
    }


def case_qp006() -> dict[str, Any]:
    pairs = [
        ("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L512_n200.npz", "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L512_n200.npz"),
        ("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L1024_n100.npz", "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L1024_n100.npz"),
        ("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/_cells_L2048_n50.npz", "03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L2048_n50.npz"),
    ]
    hashes = []
    for a, b in pairs:
        ha, hb = sha(p(a)), sha(p(b))
        hashes.append({"a": a, "b": b, "a_sha256": ha, "b_sha256": hb, "identical": ha == hb})
    prereg = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CONFIG/prereg_EXP-0009P.json")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/EXP-0009-precision_results.json")
    report = read_text("03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/REPORT/TECHNICAL_EXP-0009-precision.md")
    return {"hashes": hashes, "prereg_no_reuse": "No cells from EXP-0009/EXP-0010 reused" in prereg["note"], "result_top_keys": list(result), "report_gap_lines": [x for x in report.splitlines() if "NOT COMPUTED" in x or "not evaluated" in x], "import_path": excerpt("03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/run_q_p006.py", 16, 20)}


def case_exp0010() -> dict[str, Any]:
    pre = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CONFIG/prereg_EXP-0010.json")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/RESULTS/EXP-0010_results.json")
    report = read_text("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/REPORT.md")
    primary = result["primary_results"]
    return {
        "prereg_test": pre["predictions"]["D_f"]["test"],
        "prereg_gates": pre["gates"],
        "result_Df_keys": list(primary["D_f"]),
        "result_gate_keys": list(primary["gates"]),
        "per_L_values": {k: v["mean_mass"] for k, v in primary["D_f"]["per_L"].items()},
        "joint_Df": primary["D_f"]["measured"],
        "report_repeats_joint": [x for x in report.splitlines() if "| 127 |" in x or "| joint" in x],
        "code_decision": excerpt("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/CODE/run_exp0010.py", 113, 147),
    }


def case_qp007() -> dict[str, Any]:
    pre = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CONFIG/prereg_EXP-0009PC.json")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_results.json")
    src = read_text("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py")
    ns = {int(k): int(v) for k, v in pre["parameters"]["n_real"].items()}
    min_n = min(ns.values())
    return {
        "prereg_n_real": ns,
        "effective_aligned_n": min_n,
        "retained_fractions": {str(k): min_n / v for k, v in ns.items()},
        "source_p_c_literals": excerpt("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", 61, 63),
        "source_truncation": excerpt("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", 125, 133),
        "result_p_c": result["p_c_refined"],
        "result_reported_n": result["n_real"],
        "tau_raw": result.get("tau_raw"),
    }


def case_qp007_tau() -> dict[str, Any]:
    files = {}
    for L in (512, 1024, 2048):
        rel = f"03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_L{L}_cells.npz"
        with np.load(p(rel), allow_pickle=True) as z:
            files[str(L)] = {"keys": z.files, "sizes_n_shape": list(z["sizes_n"].shape), "sizes_n_total": z["sizes_n_total"].tolist()}
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_results.json")
    return {"npz": files, "cache_writer": excerpt("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", 39, 55), "tau_code": excerpt("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py", 141, 149), "result_tau": result["exponents"]["tau"], "result_tau_raw": result["tau_raw"]}


def case_3d_boundary() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation/ENGINE"))
    import perc_engine as pe  # type: ignore
    L = 4
    N = L**3
    labels = np.arange(N, dtype=np.int64)
    # Put one connected component on z=0 and the opposite z face.
    labels[1] = 999
    labels[(L - 1) * L * L + 1] = 999
    current = pe.spanning_flags(labels, N, L, bottom_rows=(L - 1,))
    z0 = list(range(L * L))
    zlast = list(range((L - 1) * L * L, L**3))
    actual_z = bool(set(labels[z0].tolist()) & set(labels[zlast].tolist()))
    return {"L": L, "N": N, "current_flags": {"v": bool(current[0]), "h": bool(current[1])}, "actual_opposite_z": actual_z, "rows_length": L * L, "labels_length": len(labels), "source": excerpt("03_INVESTIGATIONS/PHYSICS/percolation/ENGINE/perc_engine.py", 226, 251), "c7": excerpt("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/REPLICATION/independent_check_EXP0011.py", 77, 88)}


def case_3d_runner() -> dict[str, Any]:
    c11 = read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0011.json")
    c13 = read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0013.json")
    result = read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_results.json")
    cfg_n = {k: int(v["n_each"]) for k, v in c11["parameters"]["width_grid"].items()}
    return {"pilot_width_configured": cfg_n, "pilot_width_effective": {k: max(4, v // 10) for k, v in cfg_n.items()}, "pilot_n_real": c11["parameters"]["n_real"], "effective_slope_n": min(c11["parameters"]["n_real"].values()), "main_L": c13["parameters"]["L_list"], "main_tau_L": c13["parameters"]["tau_L"], "main_tau_L_in_main": c13["parameters"]["tau_L"] in c13["parameters"]["L_list"], "source_width": line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", "max(4, n_each // 10)"), "source_truncation": excerpt("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", 165, 183), "result_tau": result["tau"]}


def case_3d_main() -> dict[str, Any]:
    src = read_text("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py")
    c13 = read_json("03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0013.json")
    return {"default_config_order": excerpt("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", 18, 34), "hardcoded_tau": line_ref("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py", "tL = 24"), "main_L": c13["parameters"]["L_list"], "main_tau_L": c13["parameters"]["tau_L"], "would_key_error": 24 not in c13["parameters"]["L_list"], "main_result_exists": p("03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0013_results.json").exists()}


def case_qm007() -> dict[str, Any]:
    result = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/BHFR_40cell_results.json")
    from scipy.stats import chi2
    c = result["cells"][0]
    x = float(c["chi2_cell"])
    z = ((x / 1.0) ** (1.0 / 6.0) * (1.0 - 2.0 / 9.0)) / math.sqrt(2.0 / 9.0)
    code_p = 0.5 * math.erfc(z / math.sqrt(2.0))
    exact_p = float(chi2.sf(x, 1))
    mismatches = 0
    for cell in result["cells"]:
        xx = float(cell["chi2_cell"])
        zz = ((xx / 1.0) ** (1.0 / 6.0) * (1.0 - 2.0 / 9.0)) / math.sqrt(2.0 / 9.0)
        pp = 0.5 * math.erfc(zz / math.sqrt(2.0))
        mismatches += pp != cell["p_value"]
    report = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/REPORT/TECHNICAL_Q-M007.md")
    return {"total": result["total_cells"], "significant": result["significant_cells"], "first_cell": c, "source_formula_p": code_p, "exact_chi2_sf_p": exact_p, "formula_mismatch_count": mismatches, "source": excerpt("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/compute_bhfr_40cell.py", 27, 51), "report_claim": [x for x in report.splitlines() if "38/40" in x or "BH-FDR" in x][:8], "bin1_structural_note": [x for x in report.splitlines() if "| 1 | 0 |" in x]}


def case_qm007_controls() -> dict[str, Any]:
    report = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/REPORT/TECHNICAL_Q-M007.md")
    changelog = read_text("CHANGELOG.md")
    source = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/compute_bhfr_40cell.py")
    return {"report_control_lines": [x for x in report.splitlines() if "| C" in x or "not reapplied" in x], "changelog_scope": [x for x in changelog.splitlines() if "Q-M007" in x or "BH-FDR NOT" in x], "source_reads_only": [x for x in source.splitlines() if "data_path" in x or "q_m007_results" in x], "report_claims_c7": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/REPORT/TECHNICAL_Q-M007.md", "C7 independent")}


def case_qm008() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE"))
    import run_exp0012 as mod  # type: ignore
    pvals = np.array([0.003, 0.004, 0.02, 0.03, 0.04])
    order = np.argsort(pvals)
    sorted_p = pvals[order]
    thresholds = np.arange(1, len(pvals) + 1) / len(pvals) * 0.01
    naive = sorted_p <= thresholds
    valid = np.flatnonzero(naive)
    k = int(valid.max() + 1) if valid.size else 0
    proper = np.zeros(len(pvals), dtype=bool)
    proper[order[:k]] = True
    return {"code_gap": excerpt("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py", 43, 50), "exp0008_gap": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CODE/run_prime_gaps.py", "deltas = (upper - lower)"), "block_code": excerpt("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py", 119, 126), "bh_code": excerpt("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py", 100, 113), "bh_counterexample": {"p": pvals.tolist(), "sorted": sorted_p.tolist(), "naive_sorted_mask": naive.tolist(), "proper_input_mask": proper.tolist(), "proper_k": k}, "p_value_lines": [line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py", "1 - sp_stats.chi2.cdf"), line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py", "2 * (1 - sp_stats.norm.cdf")], "plan_status": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/PLAN.md", "## Status"), "report_status": line_ref("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/REPORT/TECHNICAL_Q-M008.md", "**Status:**")}


def case_qm008_sieve() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE"))
    import run_1e10 as mod  # type: ignore
    gaps, n = mod.segmented_gap_stats(1000, segment_size=1000)
    is_prime = np.ones(1001, dtype=bool)
    is_prime[:2] = False
    for i in range(2, int(math.isqrt(1000)) + 1):
        if is_prime[i]:
            is_prime[i * i::i] = False
    return {"returned_prime_count": int(n), "expected_prime_count": int(is_prime.sum()), "returned_gap_count": int(len(gaps)), "source": excerpt("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_1e10.py", 46, 66), "other_runner": excerpt("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0013.py", 46, 65), "one_e10_result_exists": p("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/RESULTS/Q-M008_1e10_results.json").exists()}


def case_s9_hardcoded() -> dict[str, Any]:
    src = read_text("save_q9results.py")
    tree = ast.parse(src)
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"q_s9_1_results", "q_s9_3_results"}:
                    values[target.id] = ast.literal_eval(node.value)
    rates = [(x["complexity"], x["code_rate"]) for x in values["q_s9_1_results"]["complexity_levels"]]
    violations = [(a, b) for (a, ra), (b, rb) in zip(rates, rates[1:]) if rb < ra]
    corrections = values["q_s9_3_results"]["observed_rates"]
    return {"literal_writer_lines": [line_ref("save_q9results.py", "q_s9_1_results ="), line_ref("save_q9results.py", "q_s9_3_results =")], "q_s9_1_rates": rates, "monotonicity_violations_in_stored_order": violations, "q_s9_3_corrections": corrections, "q_s9_3_wavelength_factor": 0.850, "wavelength_relative_change_percent": (1 - 0.850) * 100, "missing_cited_script": not (ROOT / "code/dmt-laser-s9-battery/q_s9_1_complexity.py").exists(), "report_claims": [line_ref("03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-1.md", "monotonic"), line_ref("03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-3.md", "All corrections <5%")], "writer": src}


def case_s9_synthetic() -> dict[str, Any]:
    from scipy.optimize import curve_fit
    doses = np.linspace(0, 1, 11) * 100
    def hill(x, ec50, h, maxi, base):
        return base + maxi * (x ** h) / ((ec50 ** h) + (x ** h))
    rates = np.array([hill(float(x), 30.0, 2.0, 0.483, 0.205) for x in doses])
    noise = np.random.default_rng(42).normal(0, 0.02, len(doses))
    observed = np.clip(rates + noise, 0, 1)
    result = read_json("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response_results.json")
    x = np.array([float(k) for k in result["dose_response_A"]], dtype=float)
    y = np.array(list(result["dose_response_A"].values()), dtype=float)
    fit, _ = curve_fit(hill, x, y, p0=[30, 2, .48, .205], bounds=([1, .5, .1, .05], [100, 10, 1.0, .5]), maxfev=10000)
    baseline, max_infl = 0.205, 0.483
    return {"stored_fit_parameters": result["fit_parameters"], "actual_fit_from_stored_points": [float(x) for x in fit], "max_abs_generated_vs_stored": float(np.max(np.abs(observed - y))), "source_simulation": excerpt("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", 27, 45), "source_true_parameters": excerpt("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", 52, 58), "source_writer": excerpt("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", 127, 141), "additive_saturation": baseline + max_infl, "relative_increase_if_additive": (baseline + max_infl - baseline) / baseline, "relative_increase_intended": max_infl, "report_claim": line_ref("03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-2.md", "48.3% increase")}


def case_collatz() -> dict[str, Any]:
    result = read_json("03_INVESTIGATIONS/MATHEMATICS/collatz/RESULTS/Q-M001_full_results.json")
    pre = read_json("03_INVESTIGATIONS/MATHEMATICS/collatz/prereg_Q-M001.json")
    combos = [(a, b, c) for a in pre["parameters"]["a_values"] for b in pre["parameters"]["b_values"] for c in pre["parameters"]["c_values"]]
    n, a, b, c, M = 55, 3, 3, 1, 1000
    seen = set(); repeated = False
    for _ in range(M):
        if n in seen:
            repeated = True
            break
        seen.add(n)
        n = n // a if n % a == 0 else n * b + c
    return {"stored_rows": len(result["results"]), "stored_pilot_rows": len(result["divergent_pilot"]), "prereg_combinations": len(combos), "stored_families": [(x["a"], x["b"], x["c"], x["N"]) for x in result["results"] + result["divergent_pilot"]], "hardcoded_writer": [line_ref("03_INVESTIGATIONS/MATHEMATICS/collatz/CODE/save_full_results.py", "convergent_results = ["), line_ref("03_INVESTIGATIONS/MATHEMATICS/collatz/CODE/save_full_results.py", "with open(output_dir / \"Q-M001_full_results.json\"")], "timeout_cycle_code": excerpt("03_INVESTIGATIONS/MATHEMATICS/collatz/CODE/run_collatz_full.py", 27, 36), "synthetic_timeout_repeated_state": repeated, "report_claims": [line_ref("03_INVESTIGATIONS/MATHEMATICS/collatz/REPORT/TECHNICAL_Q-M001.md", "27 families tested"), line_ref("03_INVESTIGATIONS/MATHEMATICS/collatz/REPORT/TECHNICAL_Q-M001.md", "convergence iff")]}


def case_optics_pvalues() -> dict[str, Any]:
    result = read_json("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/RESULTS/EXP-0002_results.json")
    vals = []
    for cell in result["cells"].values():
        if "p_two_sided_null_r_eq_1" in cell:
            vals.append(float(cell["p_two_sided_null_r_eq_1"]))
    report = read_text("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/REPORT/TECHNICAL_SUMMARY.md")
    return {
        "cell_count": len(vals),
        "p_min": min(vals),
        "p_values_below_001": sum(x < 0.01 for x in vals),
        "p_values_equal_0.004": sum(abs(x - 0.004) < 1e-12 for x in vals),
        "possible_two_sided_resolution": 2.0 / 500.0,
        "source": excerpt("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CODE/run_speckle_contrast.py", 49, 60),
        "report_claims": [x for x in report.splitlines() if "p-value" in x or "FDR" in x or "99% bootstrap" in x],
    }


def case_feigenbaum() -> dict[str, Any]:
    result_rel = "03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/RESULTS/EXP-0014_results.json"
    result = read_json(result_rel)
    try:
        json.loads(read_text("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CONFIG/prereg_EXP-0014.json"))
        prereg_error = None
    except Exception as exc:
        prereg_error = f"{type(exc).__name__}: {exc}"
    c4 = result["controls"]["C4"]
    return {"nested_result": result_rel, "canonical_results_files": [x.relative_to(ROOT).as_posix() for x in (ROOT / "03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/RESULTS").glob("*")] if (ROOT / "03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/RESULTS").exists() else [], "prereg_error": prereg_error, "z3_a_unique": len(set(result["z3"]["a_vals"].values())), "z3_a_count": len(result["z3"]["a_vals"]), "z3_deltas": result["z3"]["deltas"], "z4_deltas": result["z4"]["deltas"], "c4": c4, "hardcoded_controls": [line_ref("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/run_feigenbaum.py", '"pass": True'), line_ref("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/run_feigenbaum.py", '"pass": True', 2)], "fallback_without_period_check": excerpt("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/feigenbaum_engine.py", 121, 132), "report_controls": [line_ref("03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/REPORT/TECHNICAL_EXP-0014.md", "All 7 controls PASS")]}


def case_rng() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "04_SHARED_ENGINE"))
    from engine.utilities.core import rng
    from engine.validation.rng_battery import run_battery, streams_for
    rows = []
    ids = None
    for seed in range(20):
        b, f, w, bits = streams_for(rng("Q-I004:cert", seed))
        vals = run_battery(bits, b, f, w)
        ids = [x for x, _ in vals]
        rows.append([p for _, p in vals])
    x = np.asarray(rows, dtype=float)
    corr = np.corrcoef(x, rowvar=False)
    corr = np.corrcoef(x.T)
    np.fill_diagonal(corr, 0.0)
    i, j = np.unravel_index(np.nanargmax(np.abs(corr)), corr.shape)
    return {"fresh_seed_count": 20, "max_abs_offdiag_corr": float(abs(corr[i, j])), "pair": [ids[i], ids[j]], "aggregate_code": excerpt("03_INVESTIGATIONS/OTHER/rng_certification/CODE/run_rng_cert.py", 104, 131), "battery_inputs": excerpt("04_SHARED_ENGINE/engine/validation/rng_battery.py", 372, 400), "c7_same_stream": excerpt("03_INVESTIGATIONS/OTHER/rng_certification/REPLICATION/independent_check.py", 1, 10), "stored_decision": read_json("03_INVESTIGATIONS/OTHER/rng_certification/RESULTS/EXP-0004_results.json")["decision"]}


def case_stale_audit() -> dict[str, Any]:
    summary = read_text("AUDIT/DISCOVERY_SUMMARY.md")
    final = read_text("AUDIT/FINAL_SCIENTIFIC_AUDIT_REPORT.md")
    qm007 = read_text("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/REPORT/TECHNICAL_Q-M007.md")
    changelog = read_text("CHANGELOG.md")
    return {"summary_claims": [x for x in summary.splitlines() if "38/40" in x or "No overclaims" in x or "proves the deviation" in x or "8/8" in x], "qm007_contradicting_lines": [x for x in qm007.splitlines() if "not reapplied" in x or "38/40" in x], "changelog_contradicting_lines": [x for x in changelog.splitlines() if "BH-FDR NOT applied" in x or "H1_SUPPORTED status" in x], "final_audit_claims": [x for x in final.splitlines() if "Pre-registered experiments" in x or "Overclaims" in x or "7/7 controls" in x or "Hash verification" in x or "Database contents" in x]}


CASES = {
    "hash_contract": case_hash_contract,
    "freeze_overwrite": case_freeze_overwrite,
    "empty_data": case_empty_data,
    "registry": case_registry,
    "external": case_external,
    "application": case_application,
    "exp0006": case_exp0006,
    "qp006": case_qp006,
    "exp0010": case_exp0010,
    "qp007": case_qp007,
    "qp007_tau": case_qp007_tau,
    "3d_boundary": case_3d_boundary,
    "3d_runner": case_3d_runner,
    "3d_main": case_3d_main,
    "qm007": case_qm007,
    "qm007_controls": case_qm007_controls,
    "qm008": case_qm008,
    "qm008_sieve": case_qm008_sieve,
    "s9_hardcoded": case_s9_hardcoded,
    "s9_synthetic": case_s9_synthetic,
    "collatz": case_collatz,
    "optics_pvalues": case_optics_pvalues,
    "feigenbaum": case_feigenbaum,
    "rng": case_rng,
    "stale_audit": case_stale_audit,
}


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", action="append", choices=sorted(CASES))
    args = ap.parse_args()
    selected = args.case or list(CASES)
    out: dict[str, Any] = {"root": str(ROOT), "cases": {}}
    for name in selected:
        try:
            out["cases"][name] = {"ok": True, "evidence": CASES[name]()}
        except Exception as exc:
            out["cases"][name] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
    (OUT / "verification_results.json").write_text(json.dumps(out, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
