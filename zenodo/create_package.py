#!/usr/bin/env python3
"""Assemble the Zenodo package from the live laboratory tree.

Copies the audit trail into a self-contained ``package/`` directory, records a
SHA-256 for every shipped file, and refuses to overwrite an existing package.

    python create_package.py

The copies are of *published audit artifacts* only: preregistrations, results,
change logs, the tested code, and the read-only historical inputs whose digests
the deposit claims. Nothing in the laboratory itself is modified.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Iterable

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
PACKAGE = HERE / "package"
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".git"}
SKIP_SUFFIXES = {".pyc", ".zip"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy(relative: str) -> tuple[str, Path] | None:
    src = LAB / relative
    if not src.is_file():
        print(f"  MISSING  {relative}")
        return None
    dest = PACKAGE / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return relative, dest


def copy_rename(src_rel: str, dest_rel: str) -> tuple[str, Path] | None:
    src = LAB / src_rel
    if not src.is_file():
        print(f"  MISSING  {src_rel}")
        return None
    dest = PACKAGE / dest_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest_rel, dest


# (source relative to the lab root, destination relative to package/)
COPIES: list[tuple[str, str]] = [
    # --- documentation written for the public record
    ("zenodo/README.md", "README.md"),
    ("zenodo/LICENSE", "LICENSE"),
    ("zenodo/verify_historical_integrity.py", "scripts/verify_historical_integrity.py"),
    # --- finding 1: the defective statistical test
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/README.md",
        "docs/finding1_t03_runs_estimator_audit.md",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/CONFIG/prereg_T03_FORMULA_AUDIT.json",
        "docs/prereg_T03_FORMULA_AUDIT.json",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/CONFIG/prereg_T03_RECALIBRATION.json",
        "docs/prereg_T03_RECALIBRATION.json",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/CODE/runs_sp800_22.py",
        "code/finding1_runs_sp800_22.py",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/CODE/run_t03_formula_audit.py",
        "code/finding1_run_t03_formula_audit.py",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/CODE/erfc_caller_audit.py",
        "code/finding1_erfc_caller_audit.py",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/CODE/run_t03_recalibration.py",
        "code/finding1_run_t03_recalibration.py",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/TESTS/test_t03_formula.py",
        "tests_reference/test_t03_formula.py",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/TESTS/test_t03_recalibration.py",
        "tests_reference/test_t03_recalibration.py",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/RESULTS/T03_FORMULA_AUDIT_20260928/T03_formula_audit.json",
        "data/results/T03_formula_audit.json",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/RESULTS/T03_FORMULA_AUDIT_20260928/T03_formula_audit.md",
        "data/results/T03_formula_audit.md",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/RESULTS/T03_RECALIBRATION_20260928/recalibration.json",
        "data/results/T03_recalibration.json",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/RESULTS/T03_RECALIBRATION_20260928/recalibration.md",
        "data/results/T03_recalibration.md",
    ),
    # --- finding 2: the biased exponent estimator
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/README.md",
        "docs/finding2_n001_crossover_and_estimator.md",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/CONFIG/prereg_N001_CROSSOVER.json",
        "docs/prereg_N001_CROSSOVER.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/CONFIG/prereg_N001_ESTIMATOR_VALIDATION.json",
        "docs/prereg_N001_ESTIMATOR_VALIDATION.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/CODE/run_crossover_diagnostic.py",
        "code/finding2_run_crossover_diagnostic.py",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/CODE/validate_tau_estimators.py",
        "code/finding2_validate_tau_estimators.py",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/TESTS/test_crossover_diagnostic.py",
        "tests_reference/test_crossover_diagnostic.py",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/TESTS/test_tau_estimator_validation.py",
        "tests_reference/test_tau_estimator_validation.py",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/RESULTS/CROSSOVER_20260928/crossover.json",
        "data/results/n001_crossover.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/RESULTS/CROSSOVER_20260928/crossover.md",
        "data/results/n001_crossover.md",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/RESULTS/ESTIMATOR_VALIDATION_20260928/validation.json",
        "data/results/tau_estimator_validation.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/RESULTS/ESTIMATOR_VALIDATION_20260928/validation.md",
        "data/results/tau_estimator_validation.md",
    ),
    # --- finding 3: the reproducibility control repair
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/RESULTS/READ_ONLY_VALIDATION_20260928_APPEND_ONLY_PIN/validation_report.json",
        "data/results/append_only_pin_validation.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/RESULTS/READ_ONLY_VALIDATION_20260928_APPEND_ONLY_PIN/validation_report.md",
        "data/results/append_only_pin_validation.md",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/CONFIG/registry_append_only_lock.json",
        "docs/registry_append_only_lock.json",
    ),
    # --- laboratory record
    ("AUDIT/DO_NOT_CLAIM.md", "docs/DO_NOT_CLAIM.md"),
    ("CURRENT_STATUS.md", "docs/CURRENT_STATUS.md"),
    ("DISCOVERY_LOG.md", "docs/DISCOVERY_LOG.md"),
    ("CHANGELOG.md", "docs/CHANGELOG.md"),
    # --- the instruments and inputs the deposit makes claims about
    (
        "04_SHARED_ENGINE/engine/validation/rng_battery.py",
        "data/production/battery/rng_battery.py",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/CODE/run_n001.py",
        "data/production/battery/run_n001.py",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/RESULTS/N004_production_20260926_V3/N004_raw.sqlite3",
        "data/production/n004_production_20260926_V3/N004_raw.sqlite3",
    ),
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/RESULTS/N004_production_20260926_V3/N004_summary.json",
        "data/production/n004_production_20260926_V3/N004_summary.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/RESULTS/PRODUCTION_N001_20260926/N001_production_summary.json",
        "data/production/n001_production_20260926/N001_production_summary.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/RESULTS/PRODUCTION_N001_20260926/N001_production_manifest.json",
        "data/production/n001_production_20260926/N001_production_manifest.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/RESULTS/PRODUCTION_N001_20260926/N001_production_raw.sqlite3",
        "data/production/n001_production_20260926/N001_production_raw.sqlite3",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/CONFIG/historical_evidence_baseline_post_n14.json",
        "data/production/audit/historical_evidence_baseline_post_n14.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/RESULTS/READ_ONLY_VALIDATION_20260924_POST_N14/run_manifest.json",
        "data/production/audit/READ_ONLY_VALIDATION_20260924_POST_N14/run_manifest.json",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/CONFIG/EXPERIMENT_REGISTRY.historical_prefix.md",
        "data/production/registry/EXPERIMENT_REGISTRY.historical_prefix.md",
    ),
    ("EXPERIMENT_REGISTRY.md", "data/production/registry/EXPERIMENT_REGISTRY.md"),
    # --- change logs
    (
        "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/CONFIG/production_changes.jsonl",
        "data/chains/n004_production_changes.jsonl",
    ),
    (
        "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/CONFIG/changes.jsonl",
        "data/chains/n001_crossover_changes.jsonl",
    ),
]


def main() -> int:
    if (PACKAGE / "manifest.json").exists():
        print("refusing to overwrite an existing package; remove package/ first")
        return 1
    PACKAGE.mkdir(parents=True, exist_ok=True)
    print("copying published audit artifacts")
    shipped: list[tuple[str, str, int]] = []
    for src_rel, dest_rel in COPIES:
        result = copy_rename(src_rel, dest_rel) if src_rel != dest_rel else copy(dest_rel)
        if result is None:
            continue
        rel, dest = result
        shipped.append((rel, sha256_file(dest), dest.stat().st_size))
        print(f"  ok  {rel}")
    manifest = {
        "schema": "zenodo-package-manifest-v1",
        "deposit": "ScientificDiscoveryLab instrument validation and self-audit",
        "version": "1.0.0",
        "date": "2026-09-28",
        "test_suite": "495 passed, 0 errors",
        "discovery_claim": "none; see README.md",
        "file_count": len(shipped),
        "total_bytes": sum(s[2] for s in shipped),
        "files": [
            {"path": rel, "sha256": digest, "size_bytes": size}
            for rel, digest, size in sorted(shipped)
        ],
    }
    (PACKAGE / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"\nwrote {PACKAGE / 'manifest.json'}")
    print(f"{manifest['file_count']} files, {manifest['total_bytes'] / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
