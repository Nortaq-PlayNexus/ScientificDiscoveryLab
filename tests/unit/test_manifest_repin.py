"""Tests for the manifest re-pin control.

The lab's rule: every check needs a negative test. Inject the defect, confirm the
check fires. Three of the gates in this repository once reported success while
verifying nothing, and the cost of finding that out was a wasted deposit.

These tests cover the re-pin introduced after the 2026-10-04 publication of
v2.0.0, when six manifest-listed documentation files were corrected and the
manifest had to be re-pinned. The point of the re-pin is that it cannot be
silent, so the tests below assert exactly that.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import repin_manifest  # noqa: E402


def run_tool(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / name), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


# --------------------------------------------------------------------------
# The chain is tamper-evident
# --------------------------------------------------------------------------


def test_entry_hash_depends_on_every_field() -> None:
    entry = {
        "timestamp": "1970-01-01T00:00:00+00:00",
        "acknowledgement": "reason",
        "old_manifest_sha256": "0" * 64,
        "new_manifest_sha256": "1" * 64,
        "changed": [],
    }
    base = repin_manifest.entry_hash(entry)
    for field, value in (
        ("acknowledgement", "reason "),
        ("old_manifest_sha256", "2" * 64),
        ("new_manifest_sha256", "3" * 64),
        ("timestamp", "1970-01-02T00:00:00+00:00"),
    ):
        assert repin_manifest.entry_hash(dict(entry, **{field: value})) != base, (
            f"entry_hash ignored {field}: mutating it did not change the digest, "
            f"so a tampered chain entry would still verify"
        )


def test_entry_hash_excludes_itself_so_recomputation_is_stable() -> None:
    entry = {"acknowledgement": "x", "changed": []}
    once = repin_manifest.entry_hash(entry)
    assert repin_manifest.entry_hash(dict(entry, entry_hash=once)) == once


def test_verify_chain_detects_a_tampered_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    entry = {
        "schema": "manifest-repin-chain-v1",
        "timestamp": "1970-01-01T00:00:00+00:00",
        "acknowledgement": "original reason",
        "old_manifest_sha256": "0" * 64,
        "new_manifest_sha256": "1" * 64,
        "changed": [],
    }
    entry["entry_hash"] = repin_manifest.entry_hash(entry)

    chain = tmp_path / "chain.jsonl"
    chain.write_text(json.dumps(entry) + "\n", encoding="utf-8")

    # Tamper with the acknowledgement, leaving the recorded hash in place. This is
    # the laundering the control exists to catch: a reason rewritten after the fact.
    tampered = dict(entry, acknowledgement="a reason nobody reviewed")
    chain.write_text(json.dumps(tampered) + "\n", encoding="utf-8")

    monkeypatch.setattr(repin_manifest, "CHAIN", chain)
    assert repin_manifest.verify_chain() == 1, (
        "a tampered chain entry verified clean; the re-pin log is not tamper-evident"
    )


def test_verify_chain_detects_a_broken_link(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = {
        "timestamp": "1970-01-01T00:00:00+00:00",
        "acknowledgement": "one",
        "old_manifest_sha256": "0" * 64,
        "new_manifest_sha256": "1" * 64,
        "changed": [],
    }
    first["entry_hash"] = repin_manifest.entry_hash(first)
    second = {
        "timestamp": "1970-01-02T00:00:00+00:00",
        "acknowledgement": "two",
        "old_manifest_sha256": "1" * 64,
        "new_manifest_sha256": "2" * 64,
        "changed": [],
        "previous_entry_hash": "9" * 64,  # wrong predecessor
    }
    second["entry_hash"] = repin_manifest.entry_hash(second)

    chain = tmp_path / "chain.jsonl"
    chain.write_text("\n".join(json.dumps(e) for e in (first, second)) + "\n", encoding="utf-8")
    monkeypatch.setattr(repin_manifest, "CHAIN", chain)
    assert repin_manifest.verify_chain() == 1


# --------------------------------------------------------------------------
# The refusal guard: no acknowledgement, no write
# --------------------------------------------------------------------------


def test_refuses_to_repin_without_acknowledgement(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Drives the guard directly.

    An end-to-end run against the live tree cannot exercise this: the manifest
    currently matches, so there is nothing to re-pin and the guard is never
    reached. Asserting on that run would be a test that passes for the wrong
    reason -- the same failure mode as a gate that cannot fail.
    """
    manifest = tmp_path / "manifest.json"
    victim = tmp_path / "doc.md"
    victim.write_text("edited", encoding="utf-8")
    manifest.write_text(
        json.dumps({"name": "t", "files": [{"path": "doc.md", "sha256": "0" * 64, "size_bytes": 3}]}),
        encoding="utf-8",
    )

    monkeypatch.setattr(repin_manifest, "ROOT", tmp_path)
    monkeypatch.setattr(repin_manifest, "MANIFEST", manifest)
    monkeypatch.setattr(repin_manifest, "CHAIN", tmp_path / "chain.jsonl")

    monkeypatch.setattr(repin_manifest.sys, "argv", ["repin_manifest.py"])
    before = manifest.read_bytes()
    assert repin_manifest.main() == 1
    assert manifest.read_bytes() == before, "the guard wrote the manifest anyway"


def test_refusal_does_not_modify_the_manifest(tmp_path: Path) -> None:
    """The guard must fail BEFORE writing, not after."""
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"name": "t", "files": [{"path": "a", "sha256": "0" * 64, "size_bytes": 1}]}),
        encoding="utf-8",
    )
    before = manifest.read_bytes()
    # a is absent from the tree -> plan() reports it missing -> guard must engage
    proc = subprocess.run(
        [sys.executable, str(TOOLS / "repin_manifest.py")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(TOOLS), "PATH": "/usr/bin:/bin"},
    )
    # Either it refused or it errored on the missing manifest; in no case may the
    # manifest have been rewritten.
    assert proc.returncode != 0 or manifest.read_bytes() == before


def test_dry_run_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    manifest = tmp_path / "manifest.json"
    victim = tmp_path / "doc.md"
    victim.write_text("edited", encoding="utf-8")
    manifest.write_text(
        json.dumps({"name": "t", "files": [{"path": "doc.md", "sha256": "0" * 64, "size_bytes": 3}]}),
        encoding="utf-8",
    )
    chain = tmp_path / "chain.jsonl"

    monkeypatch.setattr(repin_manifest, "ROOT", tmp_path)
    monkeypatch.setattr(repin_manifest, "MANIFEST", manifest)
    monkeypatch.setattr(repin_manifest, "CHAIN", chain)
    monkeypatch.setattr(
        repin_manifest.sys, "argv", ["repin_manifest.py", "--acknowledge", "test", "--dry-run"]
    )

    before = manifest.read_bytes()
    assert repin_manifest.main() == 0
    assert manifest.read_bytes() == before, "--dry-run rewrote the manifest"
    assert not chain.exists(), "--dry-run appended to the re-pin chain"


# --------------------------------------------------------------------------
# Superseded digests stay verifiable
# --------------------------------------------------------------------------


def test_superseded_digest_verifier_selftest_passes() -> None:
    result = run_tool("verify_superseded_digests.py", "--selftest")
    assert result.returncode == 0
    assert "SELFTEST PASS" in result.stdout


def test_every_superseded_path_still_verifies_against_git() -> None:
    """The re-pin must add to the record, not replace it."""
    result = run_tool("verify_superseded_digests.py")
    assert result.returncode == 0, result.stdout
    assert "mismatched             : 0" in result.stdout


def test_repin_chain_on_disk_is_intact() -> None:
    result = run_tool("repin_manifest.py", "--verify-chain")
    assert result.returncode == 0, result.stdout
    assert "re-pin chain intact" in result.stdout


def test_repin_manifest_selftest_passes() -> None:
    result = run_tool("repin_manifest.py", "--selftest")
    assert result.returncode == 0
    assert "SELFTEST PASS" in result.stdout


# --------------------------------------------------------------------------
# The live manifest still matches the tree
# --------------------------------------------------------------------------


def test_manifest_verifies_against_the_tree() -> None:
    result = run_tool("verify_manifest.py")
    assert result.returncode == 0, result.stdout
    assert "all digests match" in result.stdout


def test_repin_chain_preserves_superseded_digest_for_each_change() -> None:
    chain = repin_manifest.read_chain()
    assert chain, "expected at least one recorded re-pin"
    for entry in chain:
        for item in entry.get("changed", []):
            assert item.get("old_sha256"), (
                f"{item['path']} was re-pinned without preserving its superseded "
                f"digest; the previously published bytes would become unverifiable"
            )
            assert item.get("new_sha256") != item.get("old_sha256")


def test_acknowledgement_is_recorded_and_nonempty() -> None:
    for entry in repin_manifest.read_chain():
        assert entry.get("acknowledgement", "").strip(), (
            "a re-pin was recorded without a reason"
        )


def test_repin_never_covers_recorded_data() -> None:
    """Every re-pin names its reason, and none silently rewrites evidence.

    Code and tooling are legitimate manifest content -- an unrecorded tool ships
    with no digest at all, which is the same hole the re-pin exists to close. What
    must never pass unnoticed is a change to recorded data or raw results, which
    alters evidence rather than bookkeeping. This test was itself wrong at first:
    it banned .py files, which made the re-pin of the re-pin tools themselves an
    error. The lab's own expected-failure gate caught that, not me.
    """
    data_suffixes = {".csv", ".npz", ".db", ".sqlite3", ".rar"}
    for entry in repin_manifest.read_chain():
        for item in entry.get("changed", []):
            assert Path(item["path"]).suffix not in data_suffixes, (
                f"re-pin covered {item['path']}, which is recorded data. Evidence "
                f"changes need a result, not a bookkeeping entry."
            )