#!/usr/bin/env python3
"""Assemble a git-sized copy of the deposit: code and docs, not the bulk data.

The full package is 63.5 MB, almost all of it the 60 MB percolation raw SQLite
database. Committing that to git would bloat the repository permanently for no
benefit, because a release can carry the archive as an asset instead.

This builds a slim tree containing everything a reader needs to understand,
audit, and re-run the analysis, minus the large binaries. The omitted files
stay listed in ``manifest.json`` with their digests, so a reader who downloads
the archive from the release can confirm they have the right bytes.

    python create_slim_tree.py <destination>
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "package"

# Files too large for git, carried as a release asset instead.
BULK = {
    "data/production/n001_production_20260926/N001_production_raw.sqlite3",
}

README = """# ScientificDiscoveryLab — instrument validation and self-audit

This repository holds the code, documentation, tests and machine-readable
results behind three defects found by a self-audit of an autonomous simulation
laboratory. **No scientific discovery is claimed.**

| # | Finding | Status |
|---|---|---|
| 1 | A PRNG statistical test applies a spurious `sqrt(2)` to a statistic the standard already defines in `erfc` units | `ESTIMATOR_DEFECTIVE`; corrected cell status `UNRESOLVED_NOT_APPLICABLE` |
| 2 | A 2D percolation cluster-mass exponent rests on an estimator biased upward by +0.11 to +0.35 | `ESTIMATOR_BIASED`; deviation from Fisher **strengthened** |
| 3 | A reproducibility control pinned an append-only registry by whole-file hash | Repaired **without refreshing any baseline** |

Test suite: **495 passed, 0 errors** (was 391 passed / 10 errors).

## What is not in this repository

The 60 MB percolation raw SQLite database is **not committed**, to keep the
repository usable. It is attached to the GitHub release and deposited on Zenodo.
Its expected SHA-256 is recorded in `manifest.json`, so you can confirm the copy
you obtained is the right one:

    expected sha256 prefix: 9f421d06732d1d05

## Verify the claims yourself

```bash
python scripts/verify_historical_integrity.py
```

This re-computes SHA-256 digests and checks them against values recorded at the
time each artifact was written — from the laboratory's own manifests, not from
prose. It never writes anything. A missing bulk file is reported as `SKIP` with
its expected digest, not as a pass.

## Honest limitations

- Q-P007 remains **open**. The deviation's *direction* is robust under every
  estimator and window; its *magnitude* is not trusted.
- `CROSSOVER_NOT_ESTABLISHED` is not crossover excluded. Three sizes spanning a
  factor of four cannot see a slow drift.
- The *mechanism* of the exponent bias is **not established**, only its
  magnitude. Two hypotheses were tested and rejected; a third was not found.
- Both preregistrations are labelled **informed, not blind** and state exactly
  what had been seen before they were frozen.
- The statistical test's defect is provable as an exact algebraic identity, but
  its empirical *detection* is resolution- and seed-dependent.

## Layout

```
code/             analysis code for both findings
docs/             preregistrations, findings write-ups, lab record, do-not-claim
data/results/     machine-readable results and rendered reports
data/production/  the instruments and inputs the claims are about
data/chains/      hash-chained change logs
tests_reference/  byte-copies of the tests as run in the laboratory
scripts/          integrity verification
manifest.json     SHA-256 of every file in the full package
```

The files in `tests_reference/` are byte-copies for inspection. They are **not**
runnable here: they import from laboratory-relative paths. The authoritative
tests live in the laboratory tree.

## Scope note

This project is **unrelated** to DOI `10.5281/zenodo.22849652` (EXP-0007,
coherent optical vortex propagation). The two share no data, code, or
conclusions.

## License

MIT — see `LICENSE`.
"""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    dest = Path(sys.argv[1]).resolve()
    if dest.exists():
        print(f"refusing to overwrite existing destination: {dest}")
        return 1
    if not PACKAGE.is_dir():
        print("run create_package.py first")
        return 1

    copied = 0
    skipped: list[str] = []
    for src in sorted(PACKAGE.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(PACKAGE).as_posix()
        if "__pycache__" in rel or rel == "manifest.json":
            continue
        if rel in BULK:
            skipped.append(rel)
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        copied += 1

    (dest / "README.md").write_text(README, encoding="utf-8", newline="\n")
    (dest / ".gitignore").write_text(
        "__pycache__/\n*.pyc\n*.sqlite3\n.pytest_cache/\n",
        encoding="utf-8",
        newline="\n",
    )

    full = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    # The slim manifest must describe the tree as it actually is, so digests are
    # computed from the destination. The repository README is generated and
    # therefore differs from the package README by design.
    present = sorted(
        p.relative_to(dest).as_posix()
        for p in dest.rglob("*")
        if p.is_file() and "__pycache__" not in p.as_posix() and p.name != "manifest.json"
    )
    slim_manifest = {
        "schema": "zenodo-package-manifest-v1-slim",
        "note": (
            "Git tree. The full package additionally contains the bulk binaries "
            "listed in 'omitted_from_git', which are carried as a release asset "
            "and deposited on Zenodo. Digests of shared files are identical to "
            "the full package; README.md is generated for the repository and "
            "differs from the package README."
        ),
        "deposit": full["deposit"],
        "version": full["version"],
        "date": full["date"],
        "test_suite": full["test_suite"],
        "discovery_claim": full["discovery_claim"],
        "full_package_file_count": full["file_count"],
        "omitted_from_git": [
            {"path": rel, "sha256": next(f["sha256"] for f in full["files"] if f["path"] == rel)}
            for rel in skipped
            if any(f["path"] == rel for f in full["files"])
        ],
        "files": [
            {
                "path": rel,
                "sha256": sha256_file(dest / rel),
                "size_bytes": (dest / rel).stat().st_size,
            }
            for rel in present
        ],
    }
    (dest / "manifest.json").write_text(
        json.dumps(slim_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )

    total = sum(1 for _ in dest.rglob("*") if _.is_file())
    size = sum(p.stat().st_size for p in dest.rglob("*") if p.is_file())
    print(f"built {dest}")
    print(f"  {total} files, {size / 1e6:.1f} MB")
    print(f"  omitted from git: {len(skipped)} bulk file(s), {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
