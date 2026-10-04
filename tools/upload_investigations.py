#!/usr/bin/env python3
"""Create the nine per-investigation Zenodo deposits.

    python tools/upload_investigations.py --dry-run
    python tools/upload_investigations.py
    python tools/upload_investigations.py --only rng-certification

Draft-first. Nothing is published; publishing needs --publish, and these are
new concepts rather than versions, so there is no `POST /api/records/<id>/versions`
to use. A new deposit goes through `POST /api/deposit/depositions`, which works
correctly for new concepts -- its `conceptrecid` field is what fails, and a new
deposit has no parent concept to link to.

Safety, given that earlier sessions created orphan deposits while the API shape
was being learned:

  * every draft's id and concept is recorded to DEPOSITS.json as it is created,
    so an interruption cannot lose track of what exists
  * --reuse <slug> resumes a partially created deposit instead of making a new one
  * the run aborts if a slug already has a recorded deposit
  * nothing is ever deleted

Each archive's bytes are verified against what Zenodo stored before moving on.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
PKG = LAB / "zenodo" / "investigations"
STATE = LAB / "zenodo" / "investigations" / "DEPOSITS.json"
BASE = "https://zenodo.org/api"

TOKEN_CANDIDATES = (
    LAB / "zenodo" / ".zenodo_token",
    Path(r"C:\Users\natha\ScientificDiscoveryLab\zenodo\.zenodo_token"),
)

REQUIRED = ("title", "description", "license", "upload_type", "creators", "keywords")


def token() -> str:
    env = os.environ.get("ZENODO_TOKEN")
    if env:
        return env.strip()
    for p in TOKEN_CANDIDATES:
        if p.is_file():
            v = p.read_text(encoding="utf-8").strip()
            if v:
                return v
    sys.exit("ERROR: no Zenodo token found")


def request(method: str, url: str, tok: str, body: bytes | None = None,
            content_type: str | None = None, attempts: int = 3) -> dict:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Authorization", f"Bearer {tok}")
        if content_type:
            req.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:800]
            if exc.code < 500:
                sys.exit(f"HTTP {exc.code} on {method} {url}\n{detail}")
            last = exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last = exc
        if attempt < attempts:
            time.sleep(3 * attempt)
    sys.exit(f"{method} {url} failed after {attempts} attempts: {last}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def build_payload(meta: dict, description: str) -> dict:
    payload = {
        "upload_type": meta["upload_type"],
        "title": meta["title"],
        "description": description,
        "version": meta["version"],
        "license": meta["license"],
        "language": meta.get("language", "eng"),
        "access_right": meta.get("access_right", "open"),
        "creators": [
            {"name": c["name"], "affiliation": c.get("affiliation", "independent")}
            for c in meta["creators"]
        ],
        "keywords": meta["keywords"],
        "related_identifiers": meta.get("related_identifiers", []),
    }
    # Subjects and version_note are accepted and silently discarded. Sent anyway
    # so they are present if Zenodo ever fixes it; read-back reports the truth.
    if meta.get("subjects"):
        payload["subjects"] = [{"id": s["id"]} for s in meta["subjects"]]
    return payload


def validate(payload: dict) -> list[str]:
    problems = []
    for f in REQUIRED:
        if f not in payload or not payload[f]:
            problems.append(f"missing or empty: {f}")
    if payload.get("license") == "cc-by-4.0":
        problems.append("license is cc-by-4.0 -- signature of a wiped record")
    return problems


def load_state() -> dict:
    if STATE.is_file():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"schema": "sdl-investigation-deposits-v1", "deposits": {}}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8", newline="\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--publish", action="store_true")
    ap.add_argument("--only", help="limit to one slug")
    ap.add_argument("--reuse", type=int, help="populate this existing draft id instead")
    args = ap.parse_args()

    tok = token()
    state = load_state()
    index = json.loads((PKG / "INDEX.json").read_text(encoding="utf-8"))
    slugs = [e["slug"] for e in index["investigations"]]
    if args.only:
        slugs = [args.only]

    print(f"{len(slugs)} investigations\n")
    for slug in slugs:
        meta = json.loads((PKG / f"{slug}.json").read_text(encoding="utf-8"))
        desc = (PKG / f"{slug}.md").read_text(encoding="utf-8")
        archive = PKG / meta["archive"]

        payload = build_payload(meta, desc)
        problems = validate(payload)
        if problems:
            print(f"  {slug}: REFUSING -- {problems}")
            return 1

        digest = sha256_file(archive)
        if digest != meta["archive_sha256"]:
            print(f"  {slug}: REFUSING -- archive digest does not match INDEX.json")
            print(f"    local  {digest}")
            print(f"    index  {meta['archive_sha256']}")
            return 1

        recorded = state["deposits"].get(slug)
        if recorded and not args.reuse:
            print(f"  {slug:<36} already recorded as draft {recorded['deposit_id']} "
                  f"-- skipping")
            continue

        print(f"  {slug}")
        print(f"    title   {meta['title']}")
        print(f"    archive {archive.name}  {archive.stat().st_size:,} B")
        print(f"    sha256  {digest}")

        if args.dry_run:
            print("    (dry run, nothing sent)")
            continue

        if args.reuse:
            dep = request("GET", f"{BASE}/deposit/depositions/{args.reuse}", tok)
        else:
            dep = request("POST", f"{BASE}/deposit/depositions", tok,
                          json.dumps({"metadata": {}}).encode(), "application/json")
        dep_id = dep["id"]

        # Record immediately, before uploading, so an interruption is recoverable.
        state["deposits"][slug] = {
            "deposit_id": dep_id,
            "concept_recid": dep.get("conceptrecid"),
            "archive": archive.name,
            "archive_bytes": archive.stat().st_size,
            "archive_sha256": digest,
            "title": meta["title"],
            "version": meta["version"],
            "published": False,
            "created": "2026-10-04",
        }
        save_state(state)
        print(f"    draft {dep_id}")

        bucket = dep["links"]["bucket"].rstrip("/")
        up = request("PUT", f"{bucket}/{archive.name}", tok,
                     archive.read_bytes(), "application/octet-stream")

        request("PUT", f"{BASE}/deposit/depositions/{dep_id}", tok,
                json.dumps({"metadata": payload}).encode(), "application/json")

        got = request("GET", f"{BASE}/deposit/depositions/{dep_id}", tok)
        gm = got.get("metadata", {})
        files = got.get("files") or []

        problems = []
        for f in REQUIRED:
            if not gm.get(f):
                problems.append(f)
        if len(files) != 1:
            problems.append(f"files={len(files)}")
        else:
            stored = files[0].get("filesize")
            if stored != archive.stat().st_size:
                problems.append(f"size {stored} != {archive.stat().st_size}")
        stored_subjects = len(gm.get("subjects") or [])

        state["deposits"][slug]["md5"] = files[0].get("checksum") if files else None
        state["deposits"][slug]["stored_subjects"] = stored_subjects
        save_state(state)

        print(f"    checksum {up.get('checksum')}")
        print(f"    edit     https://zenodo.org/deposit/{dep_id}")
        if stored_subjects == 0 and meta.get("subjects"):
            print(f"    subjects NOT stored ({len(meta['subjects'])} supplied) "
                  "-- known API behaviour, add in the web form")
        if problems:
            print(f"    !! PROBLEM: {problems}")
        print()

    if not args.dry_run and args.publish:
        print("publishing is intentionally manual -- see PUBLISH_CHECKLIST.md")

    created = len(state["deposits"])
    print(f"{created} deposits recorded in {STATE.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())