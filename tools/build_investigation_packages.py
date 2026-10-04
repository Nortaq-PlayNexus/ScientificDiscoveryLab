#!/usr/bin/env python3
"""Build per-investigation Zenodo archives for ScientificDiscoveryLab.

    python tools/build_investigation_packages.py --stage
    python tools/build_investigation_packages.py --stage --verify

Each investigation becomes one citable deposit. An investigation is the unit with
its own README, preregistration, code, config and results -- not an individual
experiment. Q-P004 spans EXP-0005/0006/0007 and Q-P005 spans EXP-0009/0010, and
splitting those across separate DOIs would scatter one scientific answer across
four identifiers.

Excluded from every archive: .git, __pycache__, .pytest_cache, and raw bulk
(`.npz`, `.sqlite3`, `.db`, `.zip`, `.rar`). The bulk is regenerable from the
seeds in each preregistration and would otherwise make the optics and percolation
archives 8-270 MB. What remains is code, preregistrations, results, reports and
audit trails.

Every archive is byte-reproducible: fixed mtimes, sorted entries, fixed mode
bits, and no build timestamp. Verified by building twice and comparing digests,
because a Zenodo file is immutable and there is no way to check afterwards
whether what was uploaded is what was intended.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
INVESTIGATIONS = LAB / "03_INVESTIGATIONS"
OUT = LAB / "zenodo" / "investigations"

FIXED_DATE = (1980, 1, 1, 0, 0, 0)

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git", ".venv", "venv",
                "build", "dist", ".ruff_cache", ".mypy_cache"}
EXCLUDE_SUFFIX = {".pyc", ".pyo", ".npz", ".sqlite3", ".db", ".zip", ".rar", ".whl"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def collect(folder: Path) -> list[Path]:
    found = []
    for p in folder.rglob("*"):
        rel = p.relative_to(folder)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if p.suffix.lower() in EXCLUDE_SUFFIX:
            continue
        if not p.is_file():
            continue
        found.append(p)
    return sorted(found, key=lambda p: p.relative_to(folder).as_posix())


def build(files: list[Path], folder: Path, out: Path) -> tuple[int, int]:
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for p in files:
            rel = p.relative_to(folder).as_posix()
            info = zipfile.ZipInfo(filename=rel, date_time=FIXED_DATE)
            info.external_attr = (0o644 & 0xFFFF) << 16
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, p.read_bytes())
    return len(files), out.stat().st_size


#: slug -> (relative path under 03_INVESTIGATIONS, display title, experiments)
TARGETS = {
    "speckle-contrast-law": (
        "OPTICS/speckle_contrast_law", "Speckle contrast law", "EXP-0002"),
    "vortex-density": (
        "OPTICS/vortex_density", "Vortex density in random wave fields", "EXP-0003"),
    "discrete-vortex-detection-bias": (
        "OPTICS/discrete_vortex_bias", "Discrete optical-vortex detection bias", "EXP-0015"),
    "topology-measurement-definition": (
        "OPTICS/topology_measurement_definition",
        "Topology-measurement definition", "EXP-0016"),
    "rng-certification": (
        "OTHER/rng_certification", "Laboratory RNG statistical certification", "EXP-0004"),
    "percolation-thresholds-and-exponents": (
        "PHYSICS/percolation", "Percolation thresholds and exponents", "EXP-0005, 0006, 0009, 0010, 0017"),
    "feigenbaum-universality": (
        "MATHEMATICS/feigenbaum_constants", "Feigenbaum universality in higher-order 1D maps", "EXP-0014"),
    "prime-gap-statistics": (
        "MATHEMATICS/prime_gaps", "Prime gap distribution statistics", "EXP-0008"),
    "water-acoustic-response": (
        "ACOUSTICS/water_sound_response", "Water acoustic response simulator", "-"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", action="store_true", help="build the archives")
    ap.add_argument("--verify", action="store_true", help="build twice and compare")
    args = ap.parse_args()
    if not args.stage:
        print(__doc__)
        return 0

    index = []
    for slug, (rel, title, exps) in TARGETS.items():
        folder = INVESTIGATIONS / rel
        if not folder.is_dir():
            print(f"  MISSING  {rel}")
            continue
        files = collect(folder)
        out = OUT / f"{slug}.zip"
        count, size = build(files, folder, out)
        digest = sha256_file(out)

        status = ""
        if args.verify:
            probe = out.with_suffix(".probe.zip")
            build(files, folder, probe)
            pd = sha256_file(probe)
            probe.unlink()
            status = " REPRODUCIBLE" if pd == digest else " NOT-REPRODUCIBLE"
            if pd != digest:
                print(f"  !! {slug} is not byte-reproducible")

        print(f"  {slug:<36} {count:>4} files  {size:>10,} B  {digest[:16]}{status}")
        index.append({
            "slug": slug,
            "path_in_lab": f"03_INVESTIGATIONS/{rel}",
            "title": title,
            "experiments": exps,
            "archive": out.name,
            "file_count": count,
            "bytes": size,
            "sha256": digest,
        })

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "INDEX.json").write_text(
        json.dumps({
            "schema": "sdl-investigation-archives-v1",
            "note": (
                "One archive per investigation, not per experiment. Q-P004 spans "
                "EXP-0005/0006/0007 and Q-P005 spans EXP-0009/0010; splitting a "
                "single scientific answer across separate DOIs would make it "
                "harder to cite, not easier."
            ),
            "excluded_suffixes": sorted(EXCLUDE_SUFFIX),
            "excluded_note": (
                "Raw simulation output, regenerable from the seeds recorded in "
                "each preregistration."
            ),
            "investigations": index,
        }, indent=2) + "\n", encoding="utf-8")
    print(f"\n  wrote {OUT / 'INDEX.json'}  ({len(index)} investigations)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())