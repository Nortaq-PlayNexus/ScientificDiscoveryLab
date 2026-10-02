"""reproducibility.experiments — experiment folder scaffolding + append-only registry.

Every investigation folder follows the universal template (see
04_SHARED_ENGINE/experiment_template.md). This module creates the skeleton the same
way every time and manages the append-only per-investigation registry.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone


TEMPLATE_DIRS = (
    "README.md",
    "QUESTION.md",
    "LITERATURE.md",
    "HYPOTHESIS.md",
    "PREDICTIONS.md",
    "CONTROLS.md",
    "EXPERIMENT_PLAN.md",
    "CONFIG",
    "CODE",
    "DATA",
    "RESULTS",
    "FIGURES",
    "REPLICATION",
    "FALSIFICATION",
    "REPORT",
    "CHANGELOG.md",
)


def scaffold_investigation(root: str, title: str, question: str) -> dict:
    """Create the universal template under `root` (non-destructive; skips existing)."""
    root = os.path.abspath(root)
    os.makedirs(root, exist_ok=True)
    made = []
    for name in TEMPLATE_DIRS:
        path = os.path.join(root, name)
        if name.endswith(".md"):
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(f"# {name}\n\nInvestigation: {title}\n")
                made.append(path)
        else:
            os.makedirs(path, exist_ok=True)
            made.append(path)
    result = {"root": root, "title": title, "question": question, "created": made}
    op = os.path.join(root, "experiment.json")
    meta = {
        "investigation": title,
        "question": question,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if not os.path.exists(op):
        with open(op, "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2, sort_keys=True)
        result["experiment.json"] = op
    return result


def append_registry_row(registry_path: str, row: dict) -> None:
    """Append-only: fsync-free but never rewrites; JSONL."""
    os.makedirs(os.path.dirname(os.path.abspath(registry_path)), exist_ok=True)
    with open(registry_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def read_registry(registry_path: str) -> list:
    """Read an append-only JSONL registry (tolerant of a trailing newline)."""
    rows = []
    if not os.path.exists(registry_path):
        return rows
    with open(registry_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows