#!/usr/bin/env python3
"""Build a hashable inventory and provenance map for the optical corpus."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LAB = Path(r"C:\Users\natha\ScientificDiscoveryLab")
ROOTS = {
    "laboratory": LAB,
    "sandbox": Path(r"C:\Users\natha\code\coherent-optical-ai-sandbox"),
    "exp0007": Path(r"C:\Users\natha\AI_RESEARCH\EXP-0007"),
}
OUT_DIR = LAB / "05_EXTERNAL_RESEARCHER_DOSSIER"
OUT_JSON = OUT_DIR / "EVIDENCE_MAP.json"
OUT_MD = OUT_DIR / "EVIDENCE_MAP.md"
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "node_modules"}
TEXT_EXT = {".py", ".md", ".txt", ".json", ".jsonl", ".csv", ".log", ".yml", ".yaml", ".toml", ".ini", ".ipynb"}
KEYWORDS = re.compile(r"vortex|phase.?singular|topolog|angular.?spectrum|speckle|percolation|propagat|alias|padding|grid|detector|density|null|audit|prereg|seed", re.I)

# These are the major numerical claims found during the audit.  Each record
# deliberately distinguishes a direct source from a second-hand report.
PROVENANCE = [
    {
        "id": "HIST-01",
        "claim": "Historical 32 µm structure is inherited from the imposed vortex-lattice pitch.",
        "source_code": [
            r"C:\Users\natha\code\coherent-optical-ai-sandbox\app\optics\structured_light.py",
            r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\exp1_detector_audit.py",
        ],
        "raw_or_generated": [
            r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\EXP-1_summary.json",
            r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\results\exp1_detector_audit_42.jsonl",
        ],
        "analysis": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\exp1_detector_audit.py"],
        "report": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\FINAL_PHASE_REPORT.md", r"C:\Users\natha\ScientificDiscoveryLab\05_EXTERNAL_RESEARCHER_DOSSIER\KEY_RESULTS.md"],
        "status": "historical, partially re-derived; dossier on audit hold",
        "reason": "The design pitch and emergence/inheritance controls are documented, but the old dossier wording must not be treated as a fresh physical result.",
    },
    {
        "id": "HIST-02",
        "claim": "48 design cores have alternating charge and net +24/-24.",
        "source_code": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\app\optics\structured_light.py"],
        "raw_or_generated": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\EXP-1_summary.json"],
        "analysis": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\exp1_detector_audit.py"],
        "report": [r"C:\Users\natha\ScientificDiscoveryLab\05_EXTERNAL_RESEARCHER_DOSSIER\KEY_RESULTS.md"],
        "status": "controlled historical result; detector output is not automatically a physical census",
        "reason": "The design topology is known; propagation-plane feature counts remain detector-dependent.",
    },
    {
        "id": "HIST-03",
        "claim": "ASM is unitary and energy conserving to numerical precision.",
        "source_code": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\app\optics\propagation.py"],
        "raw_or_generated": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\reproducibility\raw\run_01.json", r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\reproducibility\raw\run_02.json", r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\reproducibility\raw\run_03.json"],
        "analysis": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\reproducibility\verify_baseline.py", r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\replication\independent_impl\compare.py"],
        "report": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\reproducibility\INDEPENDENT_REPLICATION.md"],
        "status": "reproduced known numerical property",
        "reason": "Unitarity does not establish detector correctness or physical vortex count.",
    },
    {
        "id": "HIST-04",
        "claim": "Well-resolved random-field vortex density agrees with Kac-Rice/Nye-Berry; near-Nyquist failure exists.",
        "source_code": [r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\OPTICS\vortex_density\CODE"],
        "raw_or_generated": [r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\OPTICS\vortex_density\RESULTS"],
        "analysis": [r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\OPTICS\vortex_density\REPORT"],
        "report": [r"C:\Users\natha\ScientificDiscoveryLab\EXPERIMENT_REGISTRY.md"],
        "status": "controlled reproduction; not new physics",
        "reason": "This is a hard anchor for random-field controls and a warning that near-Nyquist sampling can fail.",
    },
    {
        "id": "HIST-05",
        "claim": "The historical z=+1280 µm DBS excess was significant only on the 256² grid and is classified as pixelation/detector resonance.",
        "source_code": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\exp2b_z1280_preregistered.py", r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\exp2c_mechanism_probe.py"],
        "raw_or_generated": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\results\exp2b_D01_42.jsonl", r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\results\exp2c_A.jsonl", r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\results\exp2c_B.jsonl"],
        "analysis": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\EXP-2B_z1280_summary.json", r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\next_phase\EXP-2C_probe_summary.json"],
        "report": [r"C:\Users\natha\code\coherent-optical-ai-sandbox\research\FINAL_PHASE_REPORT.md", r"C:\Users\natha\ScientificDiscoveryLab\05_EXTERNAL_RESEARCHER_DOSSIER\NEGATIVE_AND_DIAGNOSTIC_RESULTS.md"],
        "status": "known/expected numerical artifact; corrected EXP-0007 target-distance result remains physically unresolved",
        "reason": "The original R14 call used 1280 m rather than 1280 µm; the corrected audit must be kept separate from the historical claim.",
    },
    {
        "id": "HIST-06",
        "claim": "EXP-0007 corrected +1280 µm DBS output is 176 features; physical vortex count is unresolved.",
        "source_code": [r"C:\Users\natha\AI_RESEARCH\EXP-0007\scripts\run_target_distance_audit.py"],
        "raw_or_generated": [r"C:\Users\natha\AI_RESEARCH\EXP-0007\results\updates\target_distance_audit_2026-09-24.json"],
        "analysis": [r"C:\Users\natha\AI_RESEARCH\EXP-0007\docs\erratum-2026-09-24.md", r"C:\Users\natha\AI_RESEARCH\EXP-0007\docs\detector-improvement.md"],
        "report": [r"C:\Users\natha\AI_RESEARCH\EXP-0007\README.md", r"C:\Users\natha\AI_RESEARCH\EXP-0007\FINAL_OUTPUT.md"],
        "status": "inconclusive physical count; detector diagnostic reproduced",
        "reason": "Fixed-FOV refinement is non-convergent and the DBS semantics are not independently validated as physical zeros.",
    },
    {
        "id": "NEW-01",
        "claim": "EXP-0015 tests discrete detector bias with analytical truth, detector battery, convergence, padding, nulls, and oversampling.",
        "source_code": [r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_convergence.py", r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\independent_replication.py"],
        "raw_or_generated": [r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\RESULTS"],
        "analysis": [r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CONFIG\prereg_EXP-0015.json"],
        "report": [r"C:\Users\natha\ScientificDiscoveryLab\05_EXTERNAL_RESEARCHER_DOSSIER\DISCOVERY_STATUS.md"],
        "status": "partial / Level 1; no novelty claim",
        "reason": "No promotion until all frozen gates pass; first detector calibration failure is recorded in changes.jsonl.",
    },
]


def category(path: Path) -> str:
    s = str(path).replace("\\", "/").lower()
    if "/tests/" in s or "/test_" in s or "test_" in path.name.lower():
        return "test"
    if any(x in s for x in ("prereg", "registry", "manifest", "config")):
        return "preregistration_or_config"
    if any(x in s for x in ("report", "dossier", "readme", "status", "audit")):
        return "report_or_audit"
    if path.suffix.lower() in {".npz", ".npy", ".csv", ".jsonl"}:
        return "raw_or_generated_data"
    if path.suffix.lower() in TEXT_EXT:
        return "source_or_analysis"
    return "other_artifact"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    records: list[dict[str, Any]] = []
    for root_name, root in ROOTS.items():
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.name in {OUT_JSON.name, OUT_MD.name}:
                continue
            try:
                size = path.stat().st_size
                records.append({
                    "root": root_name,
                    "path": str(path),
                    "relative_to_root": str(path.relative_to(root)),
                    "bytes": size,
                    "extension": path.suffix.lower(),
                    "category": category(path),
                    "sha256": digest(path),
                })
            except OSError as exc:
                records.append({"root": root_name, "path": str(path), "error": str(exc)})
    counts = Counter(r.get("category", "error") for r in records)
    ext_counts = Counter(r.get("extension", "") for r in records)
    payload = {
        "schema_version": "1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": {"platform": platform.platform(), "python": sys.version},
        "roots": {k: str(v) for k, v in ROOTS.items()},
        "file_count": len(records),
        "total_bytes": sum(int(r.get("bytes", 0)) for r in records),
        "category_counts": dict(counts),
        "extension_counts": dict(ext_counts),
        "files": records,
        "provenance_records": PROVENANCE,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    lines = [
        "# Evidence map — coherent-optics discovery ecosystem",
        "",
        f"Generated: `{payload['generated_utc']}`",
        "",
        "This inventory is a provenance aid, not a claim that every historical file is valid. Historical reports remain preserved and their supersession notices remain authoritative.",
        "",
        "## Inventory summary",
        "",
        f"- Files indexed: **{payload['file_count']}**",
        f"- Bytes indexed: **{payload['total_bytes']}**",
        f"- Roots: {', '.join(f'`{v}`' for v in payload['roots'].values())}",
        "",
        "| Category | Files |",
        "|---|---:|",
    ]
    lines.extend(f"| {k} | {v} |" for k, v in sorted(counts.items()))
    lines.extend(["", "## Major provenance records", "", "| ID | Claim | Status | Source / raw / analysis / report |", "|---|---|---|---|"])
    for p in PROVENANCE:
        paths = "<br>".join(f"`{x}`" for x in p["source_code"] + p["raw_or_generated"] + p["analysis"] + p["report"])
        lines.append(f"| {p['id']} | {p['claim']} | **{p['status']}** | {paths} |")
    lines.extend(["", "## Known provenance gaps and conflicts", "",
        "- The historical dossier explicitly places several old claims on audit hold; it must not be cited unchanged.",
        "- R14's archived `z=1280` call used a metre-based API with a value of 1280, so it did not test 1280 µm.",
        "- DBS plaquette features and physical complex-field zeros are not interchangeable; several archived reports conflate them.",
        "- Fixed-FOV refinement changes the envelope-center convention with N, so its 150/176/204/220 sequence is not a strict identical-field convergence proof.",
        "- The old 8-pixel autocorrelation floor is a detector/analysis property, not a demonstrated physical length.",
        "- Some sandbox registry rows report missing/hash-drift conditions; those rows are preserved as data-integrity evidence, not physics evidence.",
        "- The new EXP-0015 first calibration pass exposed a detector-calibration defect; it is logged in `03_INVESTIGATIONS/OPTICS/discrete_vortex_bias/CONFIG/changes.jsonl` and is not silently discarded.",
        "", "## Full machine-readable inventory", "", "See `EVIDENCE_MAP.json` for every indexed path, byte count, SHA-256 hash, and category."])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Indexed {len(records)} files ({payload['total_bytes']} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
