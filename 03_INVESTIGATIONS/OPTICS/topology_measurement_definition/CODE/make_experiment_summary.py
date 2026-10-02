#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
R = BASE / "RESULTS"

def main() -> None:
    prereg = json.loads((BASE / "CONFIG" / "prereg_EXP-0016.json").read_text(encoding="utf-8"))
    changes = [json.loads(line) for line in (BASE / "CONFIG" / "changes.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    validation = json.loads((R / "validation_summary.json").read_text(encoding="utf-8"))
    result = {
        "experiment": "EXP-0016",
        "status": "COMPLETE / MEASUREMENT-DEFINITION RESULT / NO_NOVELTY_CLAIM",
        "preregistration": str(BASE / "CONFIG" / "prereg_EXP-0016.json"),
        "preregistration_sha256": prereg["config_sha256"],
        "change_log_entries": len(changes),
        "change_log_head": changes[-1]["entry_hash"] if changes else None,
        "validation": str(R / "validation_summary.json"),
        "validation_status": validation["status"],
        "analysis": str(R / "topology_analysis_summary.json"),
        "artifact_manifest": str(R / "experiment_manifest.json"),
        "historical_experiment_files_modified": False,
        "novelty_claim": False,
    }
    (R / "experiment.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Wrote", R / "experiment.json")

if __name__ == "__main__":
    main()
