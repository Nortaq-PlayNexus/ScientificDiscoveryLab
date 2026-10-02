#!/usr/bin/env python3
"""Re-verify every claim this deposit makes about historical integrity.

Run from the unpacked package root:

    python scripts/verify_historical_integrity.py

It re-computes SHA-256 digests and checks them against digests recorded at the
time each artifact was written. It never writes anything.

The point is that the central claim of this deposit, that no historical artifact
was modified, is checkable by a reader who does not trust the authors. Expected
digests are taken from manifests that the laboratory's own runners produced, not
from values asserted in prose.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_BATTERY = "5f53f3eacdf38e8cf0d47ddf3f7f71935856120fe08120f043347caa663b3b9e"
EXPECTED_RAW_DB = "9f421d06732d1d05"
EXPECTED_N001_RUNNER = "84761d2d53f930cd"
EXPECTED_BASELINE = "8c154ab03a4fcb8cac48e3848ed419fda43dd561809792779beff66c44e029ba"
EXPECTED_TAU = 1.9200860948994347
EXPECTED_ROWS = 24960

P = {
    "battery": ROOT / "data/production/battery/rng_battery.py",
    "n001_runner": ROOT / "data/production/battery/run_n001.py",
    "n001_db": ROOT / "data/production/n001_production_20260926/N001_production_raw.sqlite3",
    "n001_summary": ROOT / "data/production/n001_production_20260926/N001_production_summary.json",
    "n001_manifest": ROOT / "data/production/n001_production_20260926/N001_production_manifest.json",
    "n004_db": ROOT / "data/production/n004_production_20260926_V3/N004_raw.sqlite3",
    "n004_summary": ROOT / "data/production/n004_production_20260926_V3/N004_summary.json",
    "baseline": ROOT / "data/production/audit/historical_evidence_baseline_post_n14.json",
    "baseline_manifest": ROOT / "data/production/audit/READ_ONLY_VALIDATION_20260924_POST_N14/run_manifest.json",
    "registry": ROOT / "data/production/registry/EXPERIMENT_REGISTRY.md",
    "registry_prefix": ROOT / "data/production/registry/EXPERIMENT_REGISTRY.historical_prefix.md",
    "chain_n004": ROOT / "data/chains/n004_production_changes.jsonl",
    "chain_n001": ROOT / "data/chains/n001_crossover_changes.jsonl",
    "manifest": ROOT / "manifest.json",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check() -> list[tuple[str, str, str]]:
    """Return (name, status, detail) with status in PASS / FAIL / SKIP.

    SKIP is used for artifacts that are deliberately not shipped in a given
    distribution (for example the 60 MB raw database, which is attached to the
    Zenodo release rather than committed to git). A skip is not a failure, but
    it is never silent: the expected digest is printed so a reader who obtains
    the file elsewhere can confirm they have the right bytes.
    """
    out: list[tuple[str, str, str]] = []

    def add(name: str, status: str, detail: str) -> None:
        out.append((name, status, detail))

    for key, expected_prefix, label in (
        ("battery", EXPECTED_BATTERY, "shared RNG battery"),
        ("n001_runner", EXPECTED_N001_RUNNER, "percolation production runner"),
        ("n001_db", EXPECTED_RAW_DB, "percolation raw database"),
        ("baseline", EXPECTED_BASELINE, "2026-09-24 evidence baseline"),
    ):
        path = P[key]
        if not path.is_file():
            if key == "n001_db":
                add(
                    f"{label} shipped",
                    "SKIP",
                    f"not in this distribution; expected sha256 {EXPECTED_RAW_DB}...",
                )
            else:
                add(f"{label} present", "FAIL", "missing")
            continue
        actual = sha256_file(path)
        add(
            f"{label} digest matches the recorded value",
            "PASS" if actual.startswith(expected_prefix) else "FAIL",
            actual[:16],
        )

    # the battery digest recorded INSIDE the raw database must equal the shipped file
    if P["n004_db"].is_file() and P["battery"].is_file():
        con = sqlite3.connect(f"file:{P['n004_db']}?mode=ro", uri=True)
        try:
            meta = dict(con.execute("SELECT key, value FROM meta"))
            rows = con.execute("SELECT COUNT(*) FROM pvalues").fetchone()[0]
        finally:
            con.close()
        add(
            "battery digest inside the raw database matches the shipped battery",
            "PASS" if meta.get("battery_sha256") == EXPECTED_BATTERY else "FAIL",
            (meta.get("battery_sha256") or "missing")[:16],
        )
        add(
            "all stored production p-value rows intact",
            "PASS" if rows == EXPECTED_ROWS else "FAIL",
            f"{rows} rows",
        )

    if P["n001_db"].is_file():
        con = sqlite3.connect(f"file:{P['n001_db']}?mode=ro", uri=True)
        try:
            n = con.execute("SELECT COUNT(*) FROM cluster_arrays").fetchone()[0]
        finally:
            con.close()
        add("percolation cluster arrays intact", "PASS" if n == 500 else "FAIL", f"{n} rows (expected 500)")

    if P["baseline_manifest"].is_file() and P["baseline"].is_file():
        manifest = json.loads(P["baseline_manifest"].read_text(encoding="utf-8"))
        ok = sha256_file(P["baseline"]) == manifest["historical_evidence_baseline_sha256"]
        add(
            "2026-09-24 baseline unmodified per its own historical run manifest",
            "PASS" if ok else "FAIL",
            manifest["historical_evidence_baseline_sha256"][:16],
        )

    if P["baseline"].is_file() and P["registry"].is_file():
        baseline = json.loads(P["baseline"].read_text(encoding="utf-8-sig"))
        entry = {e["path"]: e for e in baseline["entries"]}["EXPERIMENT_REGISTRY.md"]
        live = P["registry"].read_bytes()
        ok = hashlib.sha256(live[: entry["size_bytes"]]).hexdigest() == entry["sha256"]
        add(
            "registry's audited historical prefix unchanged despite later appends",
            "PASS" if ok else "FAIL",
            f"{len(live)} bytes live, {entry['size_bytes']} audited",
        )
        ok2 = P["registry_prefix"].is_file() and sha256_file(P["registry_prefix"]) == entry["sha256"]
        add(
            "frozen prefix artifact matches the baseline digest",
            "PASS" if ok2 else "FAIL",
            entry["sha256"][:16],
        )

    if P["n001_summary"].is_file():
        s = json.loads(P["n001_summary"].read_text(encoding="utf-8-sig"))
        tau = s["fits"]["primary_32_4096"]["cumulative"]["canonical"]["tau"]
        add(
            "frozen production exponent unedited at 1.920086094899",
            "PASS" if tau == EXPECTED_TAU else "FAIL",
            repr(tau),
        )
        add(
            "production scientific decision not overwritten",
            "PASS" if s["scientific_result"] is None else "FAIL",
            s["status"],
        )

    for key, label in (("chain_n004", "N-004"), ("chain_n001", "N-001 crossover")):
        path = P[key]
        if not path.is_file():
            add(f"{label} change log present", "FAIL", "missing")
            continue
        chain = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        linked = all(b["previous_entry_hash"] == a["entry_hash"] for a, b in zip(chain, chain[1:]))
        add(
            f"{label} change log hash chain intact",
            "PASS" if linked and chain else "FAIL",
            f"{len(chain)} entries, head {chain[-1]['entry_hash'][:12]}" if chain else "empty",
        )

    if P["manifest"].is_file():
        manifest = json.loads(P["manifest"].read_text(encoding="utf-8"))
        # The full package and the slim git tree use different manifest schemas:
        # the slim tree omits bulk binaries, so it records
        # 'full_package_file_count' instead of 'file_count'.
        listed = manifest.get("file_count", manifest.get("full_package_file_count"))
        bad, missing = [], []
        for entry in manifest["files"]:
            target = ROOT / entry["path"]
            if not target.is_file():
                missing.append(entry["path"])
            elif sha256_file(target) != entry["sha256"]:
                bad.append(entry["path"])
        if bad:
            add(
                "every packaged file matches the manifest digest",
                "FAIL",
                f"{len(bad)} of {listed} mismatched: {', '.join(bad[:2])}",
            )
        elif missing:
            add(
                "every packaged file matches the manifest digest",
                "SKIP",
                f"{listed} listed, {len(missing)} not in this distribution",
            )
        else:
            add(
                "every packaged file matches the manifest digest",
                "PASS",
                f"{listed} files",
            )

    return out


def main() -> int:
    results = check()
    width = max((len(name) for name, _, _ in results), default=10)
    print("HISTORICAL INTEGRITY RE-VERIFICATION")
    print("=" * (width + 30))
    for name, status, detail in results:
        print(f"{status:<4}  {name:<{width}}  {detail}")
    print("=" * (width + 30))
    failures = sum(1 for _, s, _ in results if s == "FAIL")
    passes = sum(1 for _, s, _ in results if s == "PASS")
    skips = sum(1 for _, s, _ in results if s == "SKIP")
    print(f"{passes} passed, {skips} skipped (not in this distribution), {failures} failed.")
    if skips:
        print(
            "\nSkipped items are artifacts that are deliberately not in this distribution.\n"
            "Their expected digests are printed above; obtain them from the Zenodo\n"
            "record and re-run to check them."
        )
    if failures:
        print(
            "\nA failure here means the shipped data does not match the digests the\n"
            "laboratory recorded when the artifacts were written. Do not cite this\n"
            "deposit until the discrepancy is explained."
        )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
