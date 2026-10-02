"""Read-only second-pass evidence collection.

Writes only under AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/MAIN_AUDIT/.
Historical experiment files are never modified.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import importlib.util
import json
import math
import os
import pathlib
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats as sps

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "AUDIT" / "CROSS_PROJECT_ANOMALY_SCAN_20260924" / "MAIN_AUDIT"
OUT.mkdir(parents=True, exist_ok=True)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def load_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def source_lines(p: Path, start: int, end: int) -> list[str]:
    return [f"{i}: {line}" for i, line in enumerate(p.read_text(encoding="utf-8-sig").splitlines(), 1) if start <= i <= end]


def import_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def evidence_3d_boundary() -> dict[str, Any]:
    p = ROOT / "03_INVESTIGATIONS/PHYSICS/percolation/ENGINE/perc_engine.py"
    sys.path.insert(0, str(p.parent))
    import perc_engine as pe  # type: ignore

    results = []
    for L in (8, 16, 24):
        src, dst, N = pe.cubic_lattice_3d(L)
        # Same deterministic route for every sample; current and corrected
        # boundary tests are applied to the identical component labels.
        label = f"second-pass-3d-boundary-L{L}"
        gen = pe.rng(label, 42)
        top = np.arange(L * L)
        bottom = np.arange((L - 1) * L * L, L**3)
        xleft = np.arange(N).reshape(L, L, L)[:, 0, :].ravel()
        xright = np.arange(N).reshape(L, L, L)[:, -1, :].ravel()
        counts = np.zeros(4, dtype=np.int64)
        n = 1000
        for _ in range(n):
            occ = gen.random(N) < 0.3116079
            labels, _ = pe.build_component_array(src, dst, N, None, occ)
            current_v, current_h = pe.spanning_flags(labels, N, L)
            correct_v = bool(set(labels[top].tolist()) & set(labels[bottom].tolist()))
            correct_h = bool(set(labels[xleft].tolist()) & set(labels[xright].tolist()))
            counts += np.array([current_v, current_h, correct_v, correct_h], dtype=np.int64)
        results.append({
            "L": L,
            "n": n,
            "p": 0.3116079,
            "current_slice_v": int(counts[0]),
            "current_slice_h": int(counts[1]),
            "correct_z_v": int(counts[2]),
            "correct_x_h": int(counts[3]),
            "current_v_minus_correct_v": int(counts[0] - counts[2]),
            "current_h_minus_correct_h": int(counts[1] - counts[3]),
        })
    return {
        "source": rel(p),
        "source_excerpt": source_lines(p, 226, 251),
        "results": results,
        "interpretation": "For 3D, spanning_flags constructs rows/cols of length L^2 while labels has L^3 entries; its default boundaries select a z=0 slice and a y-row inside that slice, not the two opposite z planes. The C7 implementation repeats the same boundary convention, so agreement does not detect this shared defect.",
        "static_agent_cross_check": "AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance/verified_candidate_evidence.json:exp0011_3d_boundary",
    }


def evidence_3d_runner() -> dict[str, Any]:
    runner = ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py"
    cfg11 = ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0011.json"
    cfg13 = ROOT / "03_INVESTIGATIONS/PHYSICS/percelation_3d/CONFIG/prereg_EXP-0013.json"
    # Correct the intentional path typo defensively for this audit script.
    if not cfg13.exists():
        cfg13 = ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0013.json"
    c11 = load_json(cfg11)
    c13 = load_json(cfg13)
    return {
        "runner": rel(runner),
        "configured_width_n_each_EXP0011": {k: v["n_each"] for k, v in c11["parameters"]["width_grid"].items()},
        "actual_expression": "max(4, n_each // 10)",
        "actual_width_n_each_EXP0011": {k: max(4, v["n_each"] // 10) for k, v in c11["parameters"]["width_grid"].items()},
        "main_L_list": c13["parameters"]["L_list"],
        "main_config_tau_L": c13["parameters"]["tau_L"],
        "runner_hardcoded_tau_L": 24,
        "main_tau_key_absent_from_runner_L": 24 not in c13["parameters"]["L_list"],
        "exponent_truncation": {
            "source": "min_n = min(len(cells[L]['masses']) for L in L_LIST); arrays are sliced [:min_n]",
            "configured_n_real_EXP0011": c11["parameters"]["n_real"],
            "effective_n_for_slope_EXP0011": min(c11["parameters"]["n_real"].values()),
            "configured_n_real_EXP0013": c13["parameters"]["n_real"],
            "effective_n_for_slope_EXP0013_if_completed": min(c13["parameters"]["n_real"].values()),
        },
        "nested_tau_source": source_lines(runner, 140, 183),
        "pilot_result": rel(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_pilot_results.json"),
        "pilot_tau": load_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_pilot_results.json").get("tau"),
        "c7_artifacts": {
            "failed_artifact": {
                "path": rel(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/C7_exp0011_pilot.json"),
                "summary": load_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/C7_exp0011_pilot.json"),
            },
            "passing_artifact": {
                "path": rel(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/REPLICATION/C7_EXP-0011_report.json"),
                "summary": {k: load_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/REPLICATION/C7_EXP-0011_report.json").get(k) for k in ("all_pass",)},
            },
            "primary_result_has_c7_gate": "c7" in load_json(ROOT / "03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/RESULTS/EXP-0011_results.json"),
            "passing_script_L_list": [8, 16],
            "prereg_C7_L_list": [8, 16, 24],
        },
    }


def evidence_exp0006() -> dict[str, Any]:
    runner = ROOT / "03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0006.py"
    result_path = ROOT / "03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0006_results.json"
    d = load_json(result_path)
    def interp(ps, W, wrong: bool):
        below = np.asarray(W) < 0.5
        above = np.asarray(W) > 0.5
        i = int(np.flatnonzero(below)[-1])
        j = int(np.flatnonzero(above)[0])
        p0, p1 = ps[i], ps[j]
        w0, w1 = W[i], W[j]
        return float(p0 + (0.5 - w0) * (p1 - p0) / ((w1 - p0) if wrong else (w1 - w0)))
    rows = []
    for system, cells in d["cells"].items():
        for L in sorted({int(c["L"]) for c in cells}):
            cc = [c for c in cells if int(c["L"]) == L]
            ps = np.array([float(c["p"]) for c in cc])
            ks = np.array([float(c.get("k", c.get("k_v"))) for c in cc])
            ns = np.array([float(c["n"]) for c in cc])
            W = ks / ns
            rows.append({"system": system, "L": L, "wrong_current_formula": interp(ps, W, True), "correct_formula": interp(ps, W, False), "stored_p50": d["p50"][system][str(L)]["p50"]})
    return {
        "runner": rel(runner),
        "runner_interpolation_excerpt": source_lines(runner, 50, 66),
        "result": rel(result_path),
        "runner_mtime": dt.datetime.fromtimestamp(runner.stat().st_mtime, dt.timezone.utc).isoformat(),
        "result_mtime": dt.datetime.fromtimestamp(result_path.stat().st_mtime, dt.timezone.utc).isoformat(),
        "rows": rows,
        "stored_c2": d.get("c2"),
        "hardcoded_c2_excerpt": source_lines(runner, 290, 295),
        "interpretation": "The current runner's literal denominator is w1-p0, not w1-w0. Re-evaluating the stored cells with that expression does not reproduce the stored p50 values; the stored artifact is consistent with a different/corrected calculation. The current runner also assigns C2 pass=True without rerunning the second estimator.",
    }


def evidence_qm008() -> dict[str, Any]:
    p12 = ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py"
    p1e10 = ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_1e10.py"
    m12 = import_path("audit_qm008_run_exp0012", p12)
    # Small deterministic segment test for the first-segment sieve bug.
    m1e10 = import_path("audit_qm008_run_1e10", p1e10)
    gaps_test, n_test = m1e10.segmented_gap_stats(1000, segment_size=1000)
    is_prime = np.ones(1001, dtype=bool); is_prime[:2] = False
    for i in range(2, int(math.isqrt(1000)) + 1):
        if is_prime[i]: is_prime[i*i::i] = False
    expected_n = int(is_prime.sum())
    # Small BH counterexample: later rank passes but earlier does not.
    p = [0.009, 0.008]
    order = np.argsort(p)
    wrong_bh = [False] * len(p)
    for rank, idx in enumerate(order, 1):
        wrong_bh[idx] = p[idx] <= rank / len(p) * 0.01
    sorted_p = sorted(p)
    k = 0
    for rank, val in enumerate(sorted_p, 1):
        if val <= rank / len(p) * 0.01: k = rank
    correct_bh = [False] * len(p)
    for idx in order[:k]: correct_bh[idx] = True
    huge_chi2 = 868281.0185213662
    # High precision avoids confusing underflow with the 1-cdf cancellation itself.
    import mpmath as mp
    mp.mp.dps = 80
    mp_p = mp.gammainc(mp.mpf(9) / 2, mp.mpf(str(huge_chi2)) / 2, mp.inf, regularized=True)
    mp_log10_p = float(mp.log10(mp_p))
    return {
        "run_exp0012": rel(p12),
        "gap_formula_excerpt": source_lines(p12, 43, 50),
        "bh_excerpt": source_lines(p12, 100, 113),
        "chi2_excerpt": source_lines(p12, 51, 64),
        "gap_definition": {
            "code": "(p[i+1]-p[i]) / log(p[i+1])",
            "report_claim": "(p[i+1]-p[i]) / log(p[i])",
            "example_primes": [3, 5, 7, 11],
            "code_values": m12.compute_gaps(np.array([3, 5, 7, 11])).tolist(),
            "lower_log_values": ((np.array([5, 7, 11]) - np.array([3, 5, 7])) / np.log(np.array([3, 5, 7]))).tolist(),
        },
        "bh_counterexample": {"p_values": p, "wrong_implementation": wrong_bh, "correct_step_up": correct_bh},
        "p_value_cancellation": {
            "chi2": huge_chi2,
            "dof": 9,
            "one_minus_cdf": float(1 - sps.chi2.cdf(huge_chi2, 9)),
            "high_precision_log10_survival": mp_log10_p,
        },
        "segmented_sieve_small_test": {
            "limit": 1000,
            "segment_size": 1000,
            "returned_prime_count": int(n_test),
            "expected_prime_count": expected_n,
            "returned_gap_count": int(len(gaps_test)),
            "first_segment_marking_excerpt": source_lines(p1e10, 46, 66),
        },
    }


def evidence_qm007() -> dict[str, Any]:
    script = ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/compute_bhfr_40cell.py"
    result = load_json(ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/BHFR_40cell_results.json")
    cells = result["cells"]
    b1 = [c for c in cells if c["bin"] == 1]
    examples = []
    for c in b1[:4]:
        z = c["std_residual"]
        chi = c["chi2_cell"]
        correct = math.erfc(abs(math.sqrt(chi)) / math.sqrt(2)) if chi >= 0 else float("nan")
        examples.append({"block": c["block"], "std_residual": z, "stored_p": c["p_value"], "correct_chi1_upper_tail": correct, "ratio_stored_to_correct": c["p_value"] / correct if correct else None})
    return {
        "script": rel(script),
        "script_excerpt": source_lines(script, 14, 60),
        "stored_significant_cells": result["significant_cells"],
        "bin1_examples": examples,
        "interpretation": "The per-block standardized residuals are available and are squared, but the p-value transform is wrong: the Wilson–Hilferty exponent is 1/6 instead of 1/3 and the code uses 0.5*erfc rather than the chi-square(1) upper tail. Thus the 38/40 count happens to remain under an exact step-up calculation, but the stored p-values are not valid p-values.",
        "report": rel(ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/REPORT/TECHNICAL_Q-M007.md"),
    }


def evidence_speckle() -> dict[str, Any]:
    runner = ROOT / "03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CODE/run_speckle_contrast.py"
    controls = ROOT / "03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CONTROLS.md"
    prereg = load_json(ROOT / "03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CONFIG/prereg_EXP-0002.json")
    # Null calibration of the exact bootstrap-p formula used by the runner.
    def p_from_bootstrap(values: np.ndarray, m: int, nboot: int, seed: int) -> float:
        g = np.random.default_rng(seed)
        dist = np.array([values[g.integers(0, len(values), len(values))].mean() * math.sqrt(m) for _ in range(nboot)])
        return min(1.0, 2 * min(float((dist >= 1).mean()), float((dist <= 1).mean())) + np.finfo(float).eps)
    ps = np.array([p_from_bootstrap(np.random.default_rng(i).normal(1, .1, 32), 1, 500, i) for i in range(2000)])
    return {
        "runner": rel(runner),
        "bootstrap_p_excerpt": source_lines(runner, 49, 60),
        "control_excerpt": source_lines(runner, 161, 207),
        "prereg_controls": prereg["preregistered_controls"],
        "controls_doc_controls": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"],
        "code_actually_computes": ["C1-C5 approximations", "FDR flags", "interior contrast", "seed spot-check"],
        "independent_C7_result_path": "03_INVESTIGATIONS/OPTICS/speckle_contrast_law/REPLICATION/independent_check.json",
        "null_bootstrap_calibration": {"n_datasets": len(ps), "ks_uniform_p": float(sps.kstest(ps, "uniform").pvalue), "alpha_0.01_rejection_rate": float((ps <= .01).mean()), "mean_p": float(ps.mean())},
        "interpretation": "The KS check samples correlated pixels from one image, and the bootstrap tail proportion is reported as a p-value. The decision path does not consume the independent replication result or FDR flags.",
    }


def evidence_app() -> dict[str, Any]:
    from rdkit import Chem
    from src.molecular.engine import MoleculeInspector
    from src.reaction.mixer import classify_interaction
    with contextlib.redirect_stderr(io_stderr := __import__("io").StringIO()):
        ethanol = MoleculeInspector("CCO").get_all_descriptors()
        interaction = classify_interaction("c1ccccc1", "CCO")
        depiction_error = None
        try:
            MoleculeInspector("c1ccccc1").get_2d_structure()
        except Exception as exc:
            depiction_error = {"type": type(exc).__name__, "message": str(exc)}
    actual_formal_charge = Chem.GetFormalCharge(Chem.MolFromSmiles("CCO"))
    return {
        "formal_charge_field": ethanol.get("formal_charge"),
        "actual_formal_charge_ethanol": actual_formal_charge,
        "descriptor_source": "src/molecular/engine.py:76-83 uses Descriptors.MaxAbsPartialCharge",
        "interaction_example": interaction,
        "analyze_reaction_source": "src/reaction/engine.py:91-118 returns UNKNOWN/E0 for dissimilar valid structures",
        "depiction_error": depiction_error,
        "test_gap": "tests/unit/test_plant_engine.py:49 contains `... or True`, making the assertion tautological; no test covers formal_charge, get_2d_structure, or the E0->E3 interaction path.",
    }


def evidence_s9() -> dict[str, Any]:
    q1 = load_json(ROOT / "CODE/dmt-laser-s9-battery/q_s9_1_results.json")
    rates = sorted([(x["complexity"], x["code_rate"]) for x in q1["complexity_levels"]], key=lambda x: x[0])
    violations = [({"complexity": a, "rate": ra}, {"complexity": b, "rate": rb}) for (a, ra), (b, rb) in zip(rates, rates[1:]) if rb < ra]
    dose = load_json(ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response_results.json")
    x = np.array([float(k) for k in dose["dose_response_A"]], dtype=float)
    y = np.array(list(dose["dose_response_A"].values()), dtype=float)
    def hill(x, ec50, h, maxi, base): return base + maxi * (x**h) / ((ec50**h) + (x**h))
    fit, _ = __import__("scipy.optimize", fromlist=["curve_fit"]).curve_fit(hill, x, y, p0=[30, 2, .48, .205], bounds=([1, .5, .1, .05], [100, 10, 1, .5]), maxfev=10000)
    return {
        "q_s9_1_rates": rates,
        "monotonicity_violations": violations,
        "q_s9_1_report": rel(ROOT / "03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-1.md"),
        "q_s9_2_stored_fit": dose["fit_parameters"],
        "q_s9_2_actual_fit_from_stored_points": [float(v) for v in fit],
        "q_s9_2_writer_excerpt": source_lines(ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", 66, 86) + source_lines(ROOT / "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py", 127, 141),
        "missing_reproduction_script": "03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-1.md cites code/dmt-laser-s9-battery/q_s9_1_complexity.py, which is absent",
    }


def evidence_hash_semantics() -> dict[str, Any]:
    rows = []
    for cfg, result in [
        ("03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CONFIG/EXP-0002_experiment.json", "03_INVESTIGATIONS/OPTICS/speckle_contrast_law/RESULTS/EXP-0002_results.json"),
        ("03_INVESTIGATIONS/OPTICS/vortex_density/CONFIG/EXP-0003_experiment.json", "03_INVESTIGATIONS/OPTICS/vortex_density/RESULTS/EXP-0003_results.json"),
        ("03_INVESTIGATIONS/OTHER/rng_certification/CONFIG/EXP-0004_experiment.json", "03_INVESTIGATIONS/OTHER/rng_certification/RESULTS/EXP-0004_results.json"),
        ("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CONFIG/EXP-0008_experiment.json", "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/RESULTS/EXP-0008_results.json"),
    ]:
        c = load_json(ROOT / cfg)
        r = load_json(ROOT / result)
        canonical = hashlib.sha256(json.dumps(c.get("result"), sort_keys=True).encode("utf-8")).hexdigest()
        file_hash = hashlib.sha256((ROOT / result).read_bytes()).hexdigest()
        rows.append({"config": cfg, "result": result, "recorded_result_hash": c.get("result_hash"), "canonical_loaded_config_result_hash": canonical, "exact_result_file_sha256": file_hash, "recorded_matches_canonical": c.get("result_hash") == canonical, "recorded_matches_file": c.get("result_hash") == file_hash})
    return {"rows": rows, "interpretation": "The shared helper documents result hashes but does not define a single artifact-byte convention. For EXP-0002/0003 the recorded field matches neither the exact result file bytes nor the canonical hash of the loaded config result object, so it cannot be used as an integrity check without further provenance."}


def main() -> None:
    evidence = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "read-only second-pass cross-project anomaly scan",
        "findings": {
            "3d_spanning_boundary": evidence_3d_boundary(),
            "3d_runner_wiring": evidence_3d_runner(),
            "exp0006_runner_result_mismatch": evidence_exp0006(),
            "qm008_numerical_and_sieve": evidence_qm008(),
            "qm007_fdr_approximation": evidence_qm007(),
            "speckle_controls_and_pvalues": evidence_speckle(),
            "application_layer": evidence_app(),
            "s9_report_consistency": evidence_s9(),
            "result_hash_semantics": evidence_hash_semantics(),
        },
    }
    (OUT / "second_pass_evidence.json").write_text(json.dumps(evidence, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(json.dumps({"output": str(OUT / "second_pass_evidence.json"), "sections": list(evidence["findings"])}, indent=2))


if __name__ == "__main__":
    main()
