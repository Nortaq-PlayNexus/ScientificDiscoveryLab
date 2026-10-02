#!/usr/bin/env python3
"""Fail-closed validation for EXP-0016."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
LAB = BASE.parents[2]
sys.path.insert(0, str(LAB / "04_SHARED_ENGINE"))
from engine.hypothesis_testing.prereg import verify_change_log, verify_frozen_config  # noqa: E402

RESULTS = BASE / "RESULTS"
PREREG = BASE / "CONFIG" / "prereg_EXP-0016.json"
CHANGELOG = BASE / "CONFIG" / "changes.jsonl"


def latest(prefix: str) -> Path:
    files = sorted(RESULTS.glob(prefix + "*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        raise FileNotFoundError(prefix)
    return files[-1]


def load(prefix: str) -> tuple[Path, dict[str, Any]]:
    p = latest(prefix)
    return p, json.loads(p.read_text(encoding="utf-8"))


def joint(r: dict[str, Any]) -> bool:
    return r.get("location_count_error") == 0 and r.get("absolute_charge_error") == 0 and r.get("signed_charge_error") == 0


def main() -> int:
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, details: Any = None) -> None:
        checks.append({"name": name, "pass": bool(condition), "details": details})

    try:
        frozen = verify_frozen_config(PREREG, expected={"experiment_id": "EXP-0016", "question_id": "Q-O007", "hypothesis_id": "HYP-OPT-TMD-001"})
        check("preregistration_hash_and_identity", True, frozen["config_sha256"])
    except Exception as exc:
        check("preregistration_hash_and_identity", False, repr(exc))

    try:
        entries = verify_change_log(CHANGELOG)
        check("change_log_hash_chain", True, {"entries": len(entries), "head": entries[-1]["entry_hash"] if entries else None})
    except Exception as exc:
        check("change_log_hash_chain", False, repr(exc))

    paths = {}
    data = {}
    for key, prefix in (("calibration", "calibration_"), ("phase", "phase_diagram_"), ("propagation", "propagation_"), ("nulls", "nulls_"), ("uncertainty", "uncertainty_"), ("boundary", "boundary_controls_"), ("independent", "independent_topology_replication_"), ("reference", "reference_padding_")):
        try:
            p, d = load(prefix)
            paths[key] = str(p)
            data[key] = d
            check(f"{key}_artifact_present", True, str(p))
        except Exception as exc:
            check(f"{key}_artifact_present", False, repr(exc))

    if "calibration" in data:
        rows = data["calibration"]["rows"]
        check("calibration_row_count", len(rows) == 192, len(rows))
        contour = [r for r in rows if r["detector"] in ("circular_contour", "jacobian_locator")]
        check("calibration_contour_jacobian_truth_match", all(joint(r) for r in contour), {"n": len(contour), "failures": sum(not joint(r) for r in contour)})
        unit_raw = [r for r in rows if r["detector"] in ("raw_winding", "clustered_winding") and abs(r["charge"]) == 1]
        check("calibration_unit_charge_raw_cluster_match", all(joint(r) for r in unit_raw), {"n": len(unit_raw), "failures": sum(not joint(r) for r in unit_raw)})
        high = [r for r in rows if r["detector"] in ("raw_winding", "clustered_winding") and abs(r["charge"]) == 2]
        check("charge_two_semantic_split_is_observed", any(r["winding_cell_count"] > 1 for r in high), {"rows": len(high), "max_cells": max((r["winding_cell_count"] for r in high), default=None)})
        check("schema_separates_location_and_cells", all(r["location_count"] == r["component_count"] for r in rows), "all rows")

    if "phase" in data:
        rows = data["phase"]["rows"]
        fams = {r["family"] for r in rows}
        check("phase_families_complete", {"single", "opposite_pair", "close_pair", "four_lattice"}.issubset(fams), sorted(fams))
        check("phase_all_charges_present", {-2, -1, 1, 2}.issubset({r["charge"] for r in rows if r["family"] == "single"}), sorted({r["charge"] for r in rows if r["family"] == "single"}))
        close_fail = [r for r in rows if r["family"] == "close_pair" and r["separation_um"] == 2.0 and not joint(r)]
        check("close_pair_failure_control_observed", len(close_fail) > 0, {"failures": len(close_fail)})
        four = [r for r in rows if r["family"] == "four_lattice"]
        check("four_lattice_control", all(joint(r) for r in four), {"n": len(four), "failures": sum(not joint(r) for r in four)})
        check("phase_no_nan_metrics", all(all(v is None or (isinstance(v, (int, float)) and math.isfinite(v)) for v in r.values() if isinstance(v, (int, float))) for r in rows), "numeric fields")

    if "propagation" in data:
        rows = data["propagation"]["rows"]
        z0 = [r for r in rows if r["z_um"] == 0.0 and r["grid"] in (128, 256) and r["position_mode"] == "exact_pixel"]
        z400 = [r for r in rows if r["z_um"] == 400.0 and r["grid"] in (128, 256) and r["position_mode"] == "exact_pixel"]
        check("propagation_initial_pair", len(z0) > 0 and all(r["location_count"] == 2 and r["absolute_charge"] == 2 for r in z0), {"n": len(z0)})
        check("propagation_post_annihilation_zero", len(z400) > 0 and all(r["location_count"] == 0 and r["absolute_charge"] == 0 for r in z400), {"n": len(z400)})

    if "nulls" in data:
        rows = data["nulls"]["rows"]
        clean = [r for r in rows if r["family"] in ("plane_wave", "smooth_no_vortex")]
        check("null_clean_fields_zero", all(r["location_count"] == 0 and r["absolute_charge"] == 0 for r in clean), {"n": len(clean)})
        stress = [r for r in rows if r["family"] == "matched_amplitude_random_phase"]
        check("random_phase_stress_is_explicit", len(stress) > 0 and any(r["location_count"] > 0 for r in stress), {"n": len(stress)})

    if "uncertainty" in data:
        d = data["uncertainty"]
        check("uncertainty_trial_count", d.get("trial_count") == 96, d.get("trial_count"))
        check("uncertainty_seed", d.get("seed") == 42, d.get("seed"))

    if "boundary" in data:
        rows = data["boundary"]["rows"]
        check("boundary_control_row_count", len(rows) == 1080, len(rows))
        full_crop_changes = [r for r in rows if r["padded_full_location_count"] != r["padded_location_count"] or r["padded_full_absolute_charge"] != r["padded_absolute_charge"]]
        check("boundary_padding_separates_full_and_crop", len(full_crop_changes) > 0, {"rows": len(full_crop_changes)})
        near_inside = [r for r in rows if r["position_inside"] and abs(r["distance_to_boundary_px"]) <= 1]
        check("boundary_near_edge_control_present", len(near_inside) > 0, {"rows": len(near_inside)})

    if "independent" in data and "calibration" in data:
        ind = data["independent"]["rows"]
        main_rows = data["calibration"]["rows"]
        detector_map = {"raw": "raw_winding", "clustered": "clustered_winding", "contour": "circular_contour"}
        mode_map = {"exact": "exact_pixel", "half": "half_pixel", "quarter": "quarter_pixel"}
        lookup = {(r["detector"], r["grid"], r["charge"], r["position_mode"]): r for r in main_rows}
        comparisons = []
        for r in ind:
            m = lookup.get((detector_map[r["detector"]], r["grid"], r["q"], mode_map[r["mode"]]))
            if m:
                comparisons.append((r, m))
        def equal(independent_field: str, main_field: str) -> float:
            return sum(a.get(independent_field) == b.get(main_field) for a, b in comparisons) / len(comparisons)
        check("independent_implementation_coverage", len(comparisons) == 144, len(comparisons))
        check("independent_implementation_reproduces", all(equal(a, b) >= 0.95 for a, b in (("record_count", "record_count"), ("location_count", "location_count"), ("abs", "absolute_charge"), ("signed", "signed_charge"))), {"n": len(comparisons), "record_count": equal("record_count", "record_count"), "location_count": equal("location_count", "location_count"), "absolute_charge": equal("abs", "absolute_charge"), "signed_charge": equal("signed", "signed_charge")})

    if "reference" in data:
        d = data["reference"]
        check("reference_padding_available", len(d.get("reference_rows", [])) > 0 and len(d.get("padding_rows", [])) > 0, {"reference": len(d.get("reference_rows", [])), "padding": len(d.get("padding_rows", []))})

    passed = all(c["pass"] for c in checks)
    result = {"experiment": "EXP-0016", "status": "PASS" if passed else "FAIL", "checks": checks, "artifacts": paths}
    (RESULTS / "validation_summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
