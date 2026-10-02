"""Sync the publishable tree back into the laboratory investigation folder.

The laboratory copy is the *record* of the investigation; the published copy under
a temporary directory is the *artifact*. During pre-release review the published
copy was fixed for defects F08-F11 while the laboratory copy still contained them,
which would have left the lab asserting things its own code did not do.

This script copies the publishable tree over the laboratory folder, excluding
anything that belongs to the lab rather than the deposit:

  - CODE/            the lab keeps its own canonical source location
  - __pycache__/     build artefacts
  - zenodo/          release tooling, published-only
  - .git*            the lab folder is not the git repository

Run from the laboratory root:

    python tools/sync_published.py            # dry run
    python tools/sync_published.py --apply
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parent.parent
LAB_INVESTIGATION = (
    LAB_ROOT / "03_INVESTIGATIONS" / "COMPUTATIONAL_SCIENCE" / "ai_consciousness_indicators"
)
PUBLISHED = Path(r"C:\Users\natha\AppData\Local\Temp\opencode\cib-clean")

EXCLUDE_DIRS = {"__pycache__", ".git", ".pytest_cache", ".venv", "zenodo", "CODE", ".ruff_cache"}
EXCLUDE_NAMES = {".git"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".zip"}


def iter_published():
    for src in sorted(PUBLISHED.rglob("*")):
        rel = src.relative_to(PUBLISHED)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if rel.parts and rel.parts[0] in EXCLUDE_NAMES:
            continue
        if src.suffix in EXCLUDE_SUFFIX or not src.is_file():
            continue
        yield src, rel


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default is a dry run)")
    args = ap.parse_args()

    if not PUBLISHED.is_dir():
        print(f"published tree not found: {PUBLISHED}", file=sys.stderr)
        return 1
    if not LAB_INVESTIGATION.is_dir():
        print(f"lab investigation not found: {LAB_INVESTIGATION}", file=sys.stderr)
        return 1

    copied = missing = differing = 0
    actions: list[tuple[str, str]] = []

    for src, rel in iter_published():
        target = LAB_INVESTIGATION / rel
        if not target.exists():
            missing += 1
            actions.append(("create", str(rel)))
        elif src.read_bytes() != target.read_bytes():
            differing += 1
            actions.append(("update", str(rel)))
        else:
            continue
        if args.apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)

    for action, rel in actions:
        print(f"  {action:<7} {rel}")

    verb = "applied" if args.apply else "DRY RUN — nothing written"
    print(
        f"\n{len(actions)} file(s): {missing} new, {differing} updated ({verb})\n"
        f"source: {PUBLISHED}\n"
        f"target: {LAB_INVESTIGATION}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())