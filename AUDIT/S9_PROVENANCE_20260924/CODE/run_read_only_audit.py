#!/usr/bin/env python3
"""Read-only provenance audit for the S9/§9 battery.

This audit never imports or executes the external battery, never writes to it,
and never treats generated JSON as raw participant data.  It records exact
hashes and classifies the in-tree S9 result artifacts according to the source
signals that are actually present.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LAB_ROOT = Path(__file__).resolve().parents[3]
EXTERNAL_ROOT = Path(r"C:\Users\natha\code\dmt-laser-s9-battery")
IN_TREE_ROOT = LAB_ROOT / "CODE" / "dmt-laser-s9-battery"
REPORT_SCHEMA = "s9-provenance-audit/v1"

EXPECTED_EXTERNAL_FILES = (
    "README.md",
    "stimulus_gen.py",
    "perceptual_sim.py",
    "analysis.py",
    "run_battery.py",
    "wavelength_ladder.py",
    "q_s9_1_complexity.py",
    "q_s9_3_debias.py",
    "q_s9_4_cone_mosaic.py",
)
EXPECTED_IN_TREE_RESULTS = ("q_s9_1_results.json", "q_s9_3_results.json")
RAW_EXTENSIONS = {".csv", ".tsv", ".parquet", ".npy", ".npz", ".mat", ".h5", ".hdf5", ".tif", ".tiff", ".png", ".jpg", ".jpeg", ".edf", ".xlsx"}


class AuditError(RuntimeError):
    """Base class for fail-closed provenance errors."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise AuditError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _reject_constant(value: str) -> None:
    raise AuditError(f"non-finite JSON constant: {value}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, AuditError) as exc:
        raise AuditError(f"cannot read strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AuditError(f"JSON root must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise AuditError(f"required file is missing: {path}")
    return {
        "path": str(path),
        "sha256": sha256(path),
        "size_bytes": path.stat().st_size,
    }


def source_markers(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    marker_groups = {
        "simulated_perceptual_responses": (
            "simulate_subject",
            "simulate_population",
            "CODE_PRESENT_SOBER",
            "DOSE_INFLATION",
        ),
        "hardcoded_rates_or_models": (
            "true_rate",
            "det_rate",
            "raw_rates",
            "observed_rates",
            "DOSE_INFLATION",
        ),
        "raw_empirical_input_loaders": (
            "Image.open",
            "read_csv",
            "read_parquet",
            "loadmat",
            "h5py",
            "read_edf",
        ),
        "external_package_dependency": (
            "coherent-optical-ai-sandbox",
            "from optics.",
            "import research.program_core",
        ),
    }
    return {
        "sha256": sha256(path),
        "markers": {
            group: [marker for marker in markers if marker in text]
            for group, markers in marker_groups.items()
        },
    }


def raw_input_inventory(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise AuditError(f"external package is missing: {root}")
    candidates = []
    for path in root.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in RAW_EXTENSIONS:
            candidates.append(file_record(path))
    return {
        "search_root": str(root),
        "extensions_searched": sorted(RAW_EXTENSIONS),
        "raw_input_files": sorted(candidates, key=lambda item: item["path"]),
        "raw_input_file_count": len(candidates),
    }


def analyze() -> dict[str, Any]:
    if not EXTERNAL_ROOT.is_dir():
        raise AuditError(f"external package is missing: {EXTERNAL_ROOT}")
    if not IN_TREE_ROOT.is_dir():
        raise AuditError(f"in-tree result directory is missing: {IN_TREE_ROOT}")

    external_sources = {}
    for name in EXPECTED_EXTERNAL_FILES:
        path = EXTERNAL_ROOT / name
        if not path.is_file():
            raise AuditError(f"expected external source is missing: {path}")
        external_sources[name] = source_markers(path) if path.suffix == ".py" else file_record(path)

    in_tree_results = {}
    for name in EXPECTED_IN_TREE_RESULTS:
        path = IN_TREE_ROOT / name
        payload = load_json(path)
        in_tree_results[name] = {
            **file_record(path),
            "top_level_keys": sorted(payload),
            "experiment": payload.get("experiment"),
            "method": payload.get("method"),
        }

    raw_inventory = raw_input_inventory(EXTERNAL_ROOT)
    simulated_markers = {
        name: record.get("markers", {})
        for name, record in external_sources.items()
        if name.endswith(".py")
    }
    has_simulated_response_model = any(
        "simulated_perceptual_responses" in markers
        and markers["simulated_perceptual_responses"]
        for markers in simulated_markers.values()
    )
    has_hardcoded_model = any(
        "hardcoded_rates_or_models" in markers
        and markers["hardcoded_rates_or_models"]
        for markers in simulated_markers.values()
    )
    no_raw_loaders = not any(
        markers.get("raw_empirical_input_loaders")
        for markers in simulated_markers.values()
    )

    return {
        "schema": REPORT_SCHEMA,
        "audit_timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "Read-only inspection of the external dmt-laser-s9-battery package and the two in-tree S9 result JSON files",
        "execution_policy": {
            "external_package_imported": False,
            "external_package_executed": False,
            "external_package_written": False,
            "in_tree_historical_files_written": False,
            "raw_participant_data_claimed": False,
        },
        "source_package": {
            "path": str(EXTERNAL_ROOT),
            "source_files": external_sources,
            "raw_input_inventory": raw_inventory,
            "source_package_is_in_lab_tree": False,
        },
        "in_tree_results": in_tree_results,
        "classification": {
            "status": "SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE",
            "simulated_perceptual_response_model_present": has_simulated_response_model,
            "hardcoded_rates_or_models_present": has_hardcoded_model,
            "raw_empirical_loader_markers_present": not no_raw_loaders,
            "raw_input_files_found_in_declared_package": raw_inventory["raw_input_file_count"],
            "q_s9_1": "SYNTHETIC_AND_HARDCODED_OUTPUT",
            "q_s9_3": "DERIVED_FROM_HARDCODED_RATES_NOT_RAW_MEASUREMENTS",
            "q_s9_4": "SYNTHETIC_SIMULATION_IF_RETAINED",
            "battery_A_equals_B": "IMPLEMENTATION/SIMULATION_NULL_ONLY",
            "dose_response": "MODELLED_SYNTHETIC_RESPONSE_NOT_PHARMACOLOGICAL_EVIDENCE",
            "wavelength_tracking": "SYNTHETIC_LADDER_RESULT_NOT_EMPIRICAL_CONFIRMATION",
        },
        "unsupported_claims": [
            "The S9 outputs do not establish empirical participant responses.",
            "The A==B result does not establish a biological or perceptual mechanism.",
            "The dose-response and wavelength results do not establish real dose, detection, or biological effects.",
        ],
        "required_before_reclassification": [
            "Obtain consent-/privacy-reviewed raw participant response data and immutable provenance.",
            "Obtain raw stimulus images or independently hashed acquisition records.",
            "Freeze a new preregistration that distinguishes simulation from empirical measurement.",
            "Re-run the analysis from raw inputs with an independent implementation.",
        ],
    }


def write_exclusive(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        raise AuditError(f"refusing to overwrite existing report: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = analyze()
        write_exclusive(args.output.expanduser().resolve(), report)
    except (AuditError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps({
        "status": report["classification"]["status"],
        "raw_input_files_found": report["source_package"]["raw_input_inventory"]["raw_input_file_count"],
        "output": str(args.output.expanduser().resolve()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
