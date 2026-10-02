#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, platform, sys, time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "RESULTS" / "experiment_manifest.json"

def digest(p: Path) -> dict:
    b = p.read_bytes()
    return {"path": str(p), "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}

def main() -> None:
    paths = [
        BASE / "README.md",
        BASE / "CONFIG" / "prereg_EXP-0016.json",
        BASE / "CONFIG" / "changes.jsonl",
        BASE / "CODE" / "run_topology_definition.py",
        BASE / "CODE" / "run_reference_controls.py",
        BASE / "CODE" / "run_boundary_controls.py",
        BASE / "CODE" / "run_uncertainty.py",
        BASE / "CODE" / "independent_topology_replication.py",
        BASE / "CODE" / "analyze_topology_results.py",
        BASE / "CODE" / "make_figures.py",
        BASE / "CODE" / "make_birdeye_error_map.py",
        BASE / "CODE" / "make_manifest.py",
        BASE / "CODE" / "make_experiment_summary.py",
        BASE / "CODE" / "validate_topology_results.py",
        BASE / "REPORT" / "TECHNICAL_EXP-0016.md",
        BASE.parent.parent.parent / "EXPERIMENT_REGISTRY.md",
        BASE.parent.parent.parent / "05_EXTERNAL_RESEARCHER_DOSSIER" / "DISCOVERY_STATUS.md",
        BASE.parent.parent.parent / "05_EXTERNAL_RESEARCHER_DOSSIER" / "DISCOVERY_LEDGER.md",
        BASE.parent.parent.parent / "05_EXTERNAL_RESEARCHER_DOSSIER" / "LITERATURE_NOVELTY_MATRIX.md",
        BASE.parent.parent.parent / "05_EXTERNAL_RESEARCHER_DOSSIER" / "OPEN_PROBLEMS.md",
        BASE / "RESULTS" / "topology_analysis_summary.json",
        BASE / "RESULTS" / "failure_phase_diagram.csv",
        BASE / "RESULTS" / "phase_disagreement.csv",
        BASE / "RESULTS" / "calibration_summary.csv",
        BASE / "RESULTS" / "propagation_summary.csv",
        BASE / "RESULTS" / "null_summary.csv",
        BASE / "RESULTS" / "uncertainty_bootstrap.csv",
        BASE / "RESULTS" / "boundary_summary.csv",
        BASE / "RESULTS" / "birdeye_error_spots.csv",
        BASE / "RESULTS" / "birdeye_error_summary.json",
        BASE / "RESULTS" / "validation_summary.json",
        BASE / "RESULTS" / "experiment.json",
    ]
    paths += sorted((BASE / "FIGURES").glob("*.png"))
    paths += sorted((BASE / "RESULTS").glob("calibration_*.json"))[-1:]
    paths += sorted((BASE / "RESULTS").glob("phase_diagram_*.json"))[-1:]
    paths += sorted((BASE / "RESULTS").glob("propagation_*.json"))[-1:]
    paths += sorted((BASE / "RESULTS").glob("nulls_*.json"))[-1:]
    paths += sorted((BASE / "RESULTS").glob("uncertainty_*.json"))[-1:]
    paths += sorted((BASE / "RESULTS").glob("boundary_controls_*.json"))[-1:]
    paths += sorted((BASE / "RESULTS").glob("independent_topology_replication_*.json"))[-1:]
    paths += sorted((BASE / "RESULTS").glob("reference_padding_*.json"))[-1:]
    unique = []
    seen = set()
    for p in paths:
        if p.exists() and str(p) not in seen:
            unique.append(p); seen.add(str(p))
    validation = json.loads((BASE / "RESULTS" / "validation_summary.json").read_text(encoding="utf-8"))
    result = {
        "experiment": "EXP-0016",
        "status": "COMPLETE / MEASUREMENT-DEFINITION RESULT / NO_NOVELTY_CLAIM",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "validation_status": validation.get("status"),
        "preregistration_sha256": json.loads((BASE / "CONFIG" / "prereg_EXP-0016.json").read_text(encoding="utf-8")).get("config_sha256"),
        "environment": {"python": sys.version, "platform": platform.platform()},
        "artifacts": [digest(p) for p in unique],
        "historical_experiment_files_modified": False,
        "dossier_updated": True,
        "commit": None,
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Wrote", OUT)

if __name__ == "__main__":
    main()
