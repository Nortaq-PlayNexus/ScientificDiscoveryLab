#!/usr/bin/env python3
"""Aggregate EXP-0016 outputs into a definition-focused evidence map."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

BASE = Path(__file__).resolve().parent.parent
RESULTS = BASE / "RESULTS"
REPORT = BASE / "REPORT"
REPORT.mkdir(parents=True, exist_ok=True)


def latest(prefix: str) -> Path | None:
    files = sorted(RESULTS.glob(prefix + "*.json"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def load(prefix: str) -> tuple[Path | None, dict[str, Any] | None]:
    p = latest(prefix)
    return p, (json.loads(p.read_text(encoding="utf-8")) if p else None)


def mean(vals: Iterable[float]) -> float | None:
    a = list(vals)
    return float(np.mean(a)) if a else None


def rate(rows: list[dict[str, Any]], predicate) -> float | None:
    return float(np.mean([bool(predicate(r)) for r in rows])) if rows else None


def success(r: dict[str, Any]) -> bool:
    return (
        r.get("location_count_error") == 0
        and r.get("absolute_charge_error") == 0
        and r.get("signed_charge_error") == 0
    )


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "n": len(rows),
        "joint_success_rate": rate(rows, success),
        "location_match_rate": rate(rows, lambda r: r.get("location_count_error") == 0),
        "absolute_charge_match_rate": rate(rows, lambda r: r.get("absolute_charge_error") == 0),
        "signed_charge_match_rate": rate(rows, lambda r: r.get("signed_charge_error") == 0),
        "mean_location_count": mean(r.get("location_count") for r in rows),
        "mean_component_count": mean(r.get("component_count") for r in rows),
        "mean_winding_cell_count": mean(r.get("winding_cell_count") for r in rows),
        "mean_absolute_charge": mean(r.get("absolute_charge") for r in rows),
        "mean_signed_charge": mean(r.get("signed_charge") for r in rows),
        "location_count_values": sorted(set(r.get("location_count") for r in rows)),
        "winding_cell_count_values": sorted(set(r.get("winding_cell_count") for r in rows)),
        "absolute_charge_values": sorted(set(r.get("absolute_charge") for r in rows)),
        "charge_normalized_count_values": sorted(set(r.get("charge_normalized_count") for r in rows)),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in keys})


def ratio_bin(x: float | None) -> str:
    if x is None or not math.isfinite(x):
        return "unknown"
    edges = [0, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 20.0, float("inf")]
    labels = ["<0.5", "0.5-0.75", "0.75-1", "1-1.5", "1.5-2", "2-3", "3-4", "4-6", "6-8", "8-12", "12-20", ">20"]
    for i in range(len(edges) - 1):
        if edges[i] <= x < edges[i + 1]:
            return labels[i]
    return "unknown"


def phase_failure_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        if r["family"] == "single":
            ratio = r["core_sigma_um"] / (64.0 / r["grid"])
            key = ("single", r["detector"], r["charge"], ratio_bin(ratio))
        elif r["family"] == "close_pair":
            ratio = r["separation_um"] / (64.0 / r["grid"])
            key = ("close_pair", r["detector"], 0, ratio_bin(ratio))
        else:
            continue
        groups[key].append(r)
    out = []
    for (family, detector, charge, rb), rs in sorted(groups.items()):
        a = aggregate(rs)
        out.append({"family": family, "detector": detector, "charge": charge, "normalized_bin": rb,
                    "core_or_separation_over_pixel": rb, **a})
    return out


def disagreement_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        if r["family"] == "single":
            key = (r["family"], r["grid"], r["charge"], r["position_mode"], r["core_sigma_um"])
        elif r["family"] in ("close_pair", "opposite_pair"):
            key = (r["family"], r["grid"], r["position_mode"], r["separation_um"])
        else:
            key = (r["family"], r["grid"], r["position_mode"], r["separation_um"])
        groups[key].append(r)
    out = []
    for key, rs in sorted(groups.items(), key=lambda x: str(x[0])):
        metrics = ["location_count", "component_count", "absolute_charge", "signed_charge"]
        values = {m: sorted(set(r.get(m) for r in rs)) for m in metrics}
        out.append({"case": list(key), "n_estimators": len(rs), "disagreement": any(len(v) > 1 for v in values.values()),
                    "values": values})
    return out


def calibration_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[(r["detector"], r["charge"], r["position_mode"])].append(r)
    return [{"detector": k[0], "charge": k[1], "position_mode": k[2], **aggregate(v)} for k, v in sorted(groups.items())]


def null_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[(r["family"], r["detector"])].append(r)
    return [{"null_family": k[0], "detector": k[1], **aggregate(v)} for k, v in sorted(groups.items())]


def boundary_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        # Distances are signed in the raw control; use the absolute distance
        # to the nearest FOV edge and keep inside/outside status explicit.
        d = abs(float(r["distance_to_boundary_px"]))
        band = "0-1" if d <= 1 else "1-3" if d <= 3 else "3-6" if d <= 6 else ">6"
        groups[(r["detector"], r["position_inside"], band)].append(r)
    out = []
    for (detector, inside, band), rs in sorted(groups.items(), key=lambda x: str(x[0])):
        out.append({
            "detector": detector, "position_inside": inside, "distance_band_px": band,
            "n": len(rs),
            "unpadded_location_mean": mean(r["unpadded_location_count"] for r in rs),
            "padded_location_mean": mean(r["padded_location_count"] for r in rs),
            "unpadded_charge_mean": mean(r["unpadded_absolute_charge"] for r in rs),
            "padded_charge_mean": mean(r["padded_absolute_charge"] for r in rs),
            "padded_full_location_mean": mean(r["padded_full_location_count"] for r in rs),
            "padded_full_charge_mean": mean(r["padded_full_absolute_charge"] for r in rs),
            "location_change_rate": mean(r["unpadded_location_count"] != r["padded_location_count"] for r in rs),
            "full_vs_crop_location_change_rate": mean(r["padded_full_location_count"] != r["padded_location_count"] for r in rs),
            "charge_change_rate": mean(r["unpadded_absolute_charge"] != r["padded_absolute_charge"] for r in rs),
            "full_vs_crop_charge_change_rate": mean(r["padded_full_absolute_charge"] != r["padded_absolute_charge"] for r in rs),
            "unpadded_boundary_fp_rate": mean(r["unpadded_boundary_false_positive"] for r in rs),
            "padded_boundary_fp_rate": mean(r["padded_boundary_false_positive"] for r in rs),
        })
    return out


def propagation_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[(r["detector"], r["grid"], r["position_mode"], r["z_um"])].append(r)
    out = []
    for k, rs in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], x[0][3])):
        a = aggregate(rs)
        out.append({"detector": k[0], "grid": k[1], "position_mode": k[2], "z_um": k[3], **a})
    return out


def bootstrap_uncertainty(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rng = np.random.default_rng(42)
    out = []
    for detector in sorted(set(r["detector"] for r in rows)):
        rs = [r for r in rows if r["detector"] == detector]
        by_trial = defaultdict(list)
        for r in rs:
            by_trial[r["trial_id"]].append(success(r))
        trial_values = np.array([float(np.mean(v)) for v in by_trial.values()])
        draws = rng.choice(trial_values, size=(2000, len(trial_values)), replace=True).mean(axis=1)
        out.append({"detector": detector, "trial_count": len(trial_values),
                    "joint_success_mean": float(trial_values.mean()),
                    "bootstrap_ci95_low": float(np.quantile(draws, 0.025)),
                    "bootstrap_ci95_high": float(np.quantile(draws, 0.975))})
    return out


def independent_comparison(main_rows: list[dict[str, Any]], ind_rows: list[dict[str, Any]]) -> dict[str, Any]:
    # Main uses names with _pixel suffix; independent uses short names.
    detector_map = {"raw": "raw_winding", "clustered": "clustered_winding", "contour": "circular_contour"}
    mode_map = {"exact": "exact_pixel", "half": "half_pixel", "quarter": "quarter_pixel"}
    lookup = {(r["detector"], r["grid"], r["charge"], r["position_mode"]): r for r in main_rows}
    comparisons = []
    for r in ind_rows:
        key = (detector_map[r["detector"]], r["grid"], r["q"], mode_map[r["mode"]])
        m = lookup.get(key)
        if m is None:
            continue
        comparisons.append({
            "detector": r["detector"], "grid": r["grid"], "charge": r["q"], "mode": r["mode"],
            "record_count_equal": r.get("record_count") == m.get("record_count"),
            "location_count_equal": r.get("location_count") == m.get("location_count"),
            "absolute_charge_equal": r.get("abs") == m.get("absolute_charge"),
            "signed_charge_equal": r.get("signed") == m.get("signed_charge"),
        })
    return {"n": len(comparisons), **aggregate_flag_rows(comparisons)}


def aggregate_flag_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    keys = ["record_count_equal", "location_count_equal", "absolute_charge_equal", "signed_charge_equal"]
    return {k: float(np.mean([bool(r[k]) for r in rows])) for k in keys}


def reference_summary(ref: dict[str, Any] | None) -> dict[str, Any]:
    if not ref:
        return {"available": False}
    rr = ref.get("reference_rows", [])
    pp = ref.get("padding_rows", [])
    out = {"available": True, "reference_n": len(rr), "padding_n": len(pp), "by_detector": {}}
    for detector in sorted(set(r["detector"] for r in rr)):
        x = [r for r in rr if r["detector"] == detector]
        y = [r for r in pp if r["detector"] == detector]
        out["by_detector"][detector] = {
            "reference_field_rms_median": float(np.median([r["field_relative_rms"] for r in x])),
            "reference_location_disagreement_rate": float(np.mean([r["direct_location_count"] != r["reference_location_count"] for r in x])),
            "reference_winding_disagreement_rate": float(np.mean([r["direct_winding_cell_count"] != r["reference_winding_cell_count"] for r in x])),
            "padding_field_rms_max": max([r["field_relative_rms"] for r in y], default=None),
            "padding_location_change_rate": float(np.mean([r["direct_location_count"] != r["padded_location_count"] for r in y])),
            "padding_winding_change_rate": float(np.mean([r["direct_winding_cell_count"] != r["padded_winding_cell_count"] for r in y])),
        }
    return out


def main() -> None:
    paths = {}
    data = {}
    for name, prefix in (("calibration", "calibration_"), ("phase", "phase_diagram_"), ("propagation", "propagation_"), ("nulls", "nulls_"), ("uncertainty", "uncertainty_"), ("boundary", "boundary_controls_"), ("independent", "independent_topology_replication_"), ("reference", "reference_padding_")):
        p, d = load(prefix)
        paths[name] = str(p) if p else None
        data[name] = d
    phase_rows = data["phase"]["rows"] if data["phase"] else []
    cal_rows = data["calibration"]["rows"] if data["calibration"] else []
    prop_rows = data["propagation"]["rows"] if data["propagation"] else []
    null_rows = data["nulls"]["rows"] if data["nulls"] else []
    uncertainty_rows = data["uncertainty"]["rows"] if data["uncertainty"] else []
    boundary_rows = data["boundary"]["rows"] if data["boundary"] else []
    ind_rows = data["independent"]["rows"] if data["independent"] else []

    disagreement = disagreement_table(phase_rows)
    failure = phase_failure_table(phase_rows)
    calibration = calibration_table(cal_rows)
    nulls = null_table(null_rows)
    propagation = propagation_table(prop_rows)
    uncertainty = bootstrap_uncertainty(uncertainty_rows) if uncertainty_rows else []
    independent = independent_comparison(cal_rows, ind_rows) if cal_rows and ind_rows else {"n": 0}
    reference = reference_summary(data["reference"])
    boundary = boundary_table(boundary_rows) if boundary_rows else []

    write_csv(RESULTS / "failure_phase_diagram.csv", failure)
    write_csv(RESULTS / "phase_disagreement.csv", disagreement)
    write_csv(RESULTS / "calibration_summary.csv", calibration)
    write_csv(RESULTS / "null_summary.csv", nulls)
    write_csv(RESULTS / "propagation_summary.csv", propagation)
    write_csv(RESULTS / "uncertainty_bootstrap.csv", uncertainty)
    write_csv(RESULTS / "boundary_summary.csv", boundary)

    prereg = BASE / "CONFIG" / "prereg_EXP-0016.json"
    prereg_hash = json.loads(prereg.read_text(encoding="utf-8")).get("config_sha256") if prereg.exists() else None
    summary = {
        "experiment": "EXP-0016",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "preregistration": str(prereg),
        "preregistration_sha256": prereg_hash,
        "input_paths": paths,
        "definitions": {
            "truth_location": "continuous analytical singularity position",
            "location_count": "number of estimated location records; raw winding uses same-sign connected components as its location proxy",
            "component_count": "number of connected estimator components/accepted records; raw winding uses same-sign components",
            "winding_cell_count": "number of nonzero plaquette winding cells; zero means not applicable for contour/Jacobian records",
            "absolute_charge": "sum of absolute estimated charges",
            "signed_charge": "sum of estimated charges",
            "charge_normalized_count": "absolute charge divided by maximum absolute truth charge (a charge-mass unit, not a universal vortex count)",
            "joint_success": "zero location-count error, absolute-charge error, and signed-charge error",
        },
        "calibration": calibration,
        "failure_phase_diagram": failure,
        "disagreement": {
            "n_cases": len(disagreement),
            "n_disagreeing_cases": sum(bool(r["disagreement"]) for r in disagreement),
            "rate": (sum(bool(r["disagreement"]) for r in disagreement) / len(disagreement)) if disagreement else None,
            "by_family": {fam: {"n": len([r for r in disagreement if r["case"][0] == fam]), "disagreement_rate": mean([r["disagreement"] for r in disagreement if r["case"][0] == fam])} for fam in sorted(set(r["case"][0] for r in disagreement))},
        },
        "nulls": nulls,
        "propagation": propagation,
        "boundary_controls": boundary,
        "uncertainty_bootstrap": uncertainty,
        "independent_comparison": independent,
        "reference_padding": reference,
    }
    (RESULTS / "topology_analysis_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("Wrote", RESULTS / "topology_analysis_summary.json")
    print("Inputs:", json.dumps(paths, indent=2))


if __name__ == "__main__":
    main()
