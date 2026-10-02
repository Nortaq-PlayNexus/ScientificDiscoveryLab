#!/usr/bin/env python3
"""Copy this project to a clean directory and verify it reproduces standalone.

Run from the repository root:

    python verify_clean_room.py

Copies every tracked file except VCS metadata and caches into a temporary
directory, installs nothing, and re-runs the test suite plus the result-hash
verifier from that copy. Proves the published repo has no dependency on the
originating laboratory's shared engine.

Exit code 0 means the clean room passed.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    "build",
    "dist",
    # Generated deposit staging area. Excluding it matters: a copy of the same
    # test modules inside it produces duplicate basenames, which makes pytest
    # collect them twice and fail on module import.
    "zenodo",
}
EXCLUDE_SUFFIX = {".pyc", ".pyo"}
COPY_EXTRA = {".github"}


def stage(dest: Path) -> list[str]:
    copied: list[str] = []
    for src in sorted(Path.cwd().rglob("*")):
        rel = src.relative_to(Path.cwd())
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if src.suffix in EXCLUDE_SUFFIX or not src.is_file():
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        copied.append(str(rel))
    return copied


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=900)
    return proc.returncode, (proc.stdout + proc.stderr)


def main() -> int:
    dest = Path(tempfile.mkdtemp(prefix="cib-cleanroom-"))
    try:
        files = stage(dest)
        print(f"staged {len(files)} files -> {dest}\n")

        steps: list[tuple[str, list[str]]] = [
            ("test suite", [sys.executable, "-m", "pytest", "-q"]),
            (
                "result hash integrity",
                [
                    sys.executable,
                    "experiment_verify.py",
                    "RESULTS/experiment.json",
                    "RESULTS/experiment_C003.json",
                ],
            ),
            (
                "headline claims reproduce",
                [
                    sys.executable,
                    "-c",
                    "from battery import calibrate_known_answers\n"
                    "from perturbation import compare_regions\n"
                    "cal = calibrate_known_answers()\n"
                    "assert cal.passed, cal.failures\n"
                    "r = compare_regions(seed=0)\n"
                    "assert r['verdict_detail']['load_claim_FB_holds_both']\n"
                    "print('calibration PASS; F-B holds both regions')\n",
                ],
            ),
        ]

        failures = 0
        for label, cmd in steps:
            code, out = run(cmd, dest)
            status = "PASS" if code == 0 else "FAIL"
            print(f"[{status}] {label}")
            tail = [ln for ln in out.strip().splitlines() if ln.strip()][-4:]
            for line in tail:
                print(f"       {line}")
            failures += code != 0
            print()

        print("CLEAN ROOM PASSED" if failures == 0 else f"CLEAN ROOM FAILED ({failures} step(s))")
        return 0 if failures == 0 else 1
    finally:
        shutil.rmtree(dest, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
