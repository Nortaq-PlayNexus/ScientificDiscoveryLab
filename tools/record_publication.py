#!/usr/bin/env python3
"""Record publication outcomes and verification results for the 12 deposits.

    python tools/record_publication.py

Reads the live public API for every deposit, records the minted DOI, the concept
it belongs to, and the byte-level integrity check, then writes the result to
zenodo/investigations/DEPOSITS.json.

The integrity check is the point. A publish click reports success regardless of
whether the bytes that arrived are the bytes that were sent, so every record is
compared against the local build by size and MD5 rather than trusted. Records
that cannot be verified are marked UNVERIFIED, not assumed good.

Written to be re-runnable: it queries the API rather than carrying hardcoded
DOIs, so a later version can be recorded the same way.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
PKG = LAB / "zenodo" / "investigations"
STATE = PKG / "DEPOSITS.json"
API = "https://zenodo.org/api/records"

#: deposit id -> umbrella record (slug -> record id), filled in as published
UMBRELLA = {
    23122664: "consciousness-indicator-battery",
    23122787: "ScientificDiscoveryLab",
    23123095: "phantom-vision-lab",
}

VERIFY_DATE = "2026-10-04"


def md5_file(path: Path) -> tuple[str, int]:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest(), path.stat().st_size


def get(record_id: int) -> dict:
    url = f"{API}/{record_id}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        return json.loads(resp.read())


def verify(record: dict, local: Path | None) -> dict:
    """Byte-level check of what Zenodo stored against what we built."""
    files = record.get("files") or []
    out = {
        "file_count": len(files),
        "stored_checksum": files[0].get("checksum") if files else None,
        "stored_bytes": files[0].get("size") if files else None,
        "local_archive": local.name if local else None,
    }
    if local is None or not local.is_file() or not files:
        out["verdict"] = "UNVERIFIED"
        out["reason"] = "no local build available to compare against"
        return out
    digest, size = md5_file(local)
    size_ok = files[0].get("size") == size
    md5_ok = files[0].get("checksum") == f"md5:{digest}"
    out["local_checksum"] = f"md5:{digest}"
    out["local_bytes"] = size
    out["verdict"] = "BYTE_IDENTICAL" if (size_ok and md5_ok) else "MISMATCH"
    return out


def main() -> int:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    deposits = state["deposits"]

    for slug, rec in deposits.items():
        dep_id = rec["deposit_id"]
        try:
            record = get(dep_id)
        except Exception as exc:  # noqa: BLE001
            rec["verification"] = {"verdict": "UNVERIFIED", "reason": str(exc)}
            print(f"  {slug:<36} UNVERIFIED -- {exc}")
            continue

        rec["doi"] = record["doi"]
        rec["concept_doi"] = record.get("conceptdoi")
        rec["concept_recid"] = record.get("conceptrecid")
        rec["published"] = True
        rec["published_date"] = record["metadata"].get("publication_date")
        rec["url"] = f"https://doi.org/{record['doi']}"

        local = PKG / rec["archive"] if rec.get("archive") else None
        rec["verification"] = verify(record, local)

        subj = record["metadata"].get("subjects") or []
        rec["subjects_published"] = len(subj)
        refs = record["metadata"].get("references") or []
        rec["references_published"] = len(refs)

        v = rec["verification"]["verdict"]
        print(f"  {slug:<36} {record['doi']}  {v}")

    state["published"] = {
        "verified_on": VERIFY_DATE,
        "count": sum(1 for r in deposits.values() if r.get("published")),
        "byte_identical": sum(
            1 for r in deposits.values()
            if r.get("verification", {}).get("verdict") == "BYTE_IDENTICAL"
        ),
        "note": (
            "Investigations only. The three umbrella records (battery, laboratory, "
            "phantom vision lab) are tracked in their own repositories."
        ),
        "umbrella": UMBRELLA,
        "known_defect": {
            "field": "subjects",
            "state": "ZERO on all 12 published records",
            "cause": (
                "Zenodo's deposition API accepts the field, reports success and "
                "stores nothing. Verified against both /api/deposit/depositions "
                "and /api/records/<id>/draft on 2026-10-04."
            ),
            "remedy": (
                "Published Zenodo records are immutable. Fixing this requires a "
                "new version of each record with subjects entered in the web form."
            ),
        },
    }

    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8", newline="\n")
    print(f"\n  wrote {STATE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())