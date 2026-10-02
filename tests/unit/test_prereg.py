"""Regression tests for immutable, content-addressed preregistrations."""

import json
import sys
from pathlib import Path

import pytest

LAB_ROOT = Path(__file__).resolve().parents[2]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
if str(SHARED_ENGINE) not in sys.path:
    sys.path.insert(0, str(SHARED_ENGINE))

from engine.hypothesis_testing.prereg import (  # noqa: E402
    PreregistrationExistsError,
    PreregistrationIntegrityError,
    freeze_config,
    log_change,
    verify_change_log,
    verify_frozen_config,
)


def _freeze(path: Path, *, x: int = 1):
    return freeze_config(
        experiment_id="EXP-TEST",
        hypothesis_id="HYP-TEST",
        question_id="Q-TEST",
        seed=42,
        controls=("C1",),
        analyses=("analysis-a",),
        params={"x": x},
        out_path=path,
        note="frozen once",
    )


def test_freeze_writes_verifiable_content_addressed_config(tmp_path):
    target = tmp_path / "prereg.json"

    frozen = _freeze(target)

    loaded = verify_frozen_config(
        target,
        expected={
            "experiment_id": "EXP-TEST",
            "parameters": {"x": 1},
            "preregistered_controls": ["C1"],
        },
    )
    assert loaded == frozen
    assert len(loaded["config_sha256"]) == 64


def test_freeze_refuses_to_overwrite_existing_protocol(tmp_path):
    target = tmp_path / "prereg.json"
    _freeze(target, x=1)
    before = target.read_bytes()

    with pytest.raises(PreregistrationExistsError):
        _freeze(target, x=2)

    assert target.read_bytes() == before
    assert verify_frozen_config(target)["parameters"] == {"x": 1}


def test_verify_frozen_config_rejects_duplicate_keys(tmp_path):
    target = tmp_path / "prereg.json"
    _freeze(target)
    raw = target.read_text(encoding="utf-8")
    target.write_text(
        '{"experiment_id":"EXP-TEST","experiment_id":"EXP-TEST",' + raw[1:],
        encoding="utf-8",
    )

    with pytest.raises(PreregistrationIntegrityError, match="duplicate JSON key"):
        verify_frozen_config(target)


def test_verify_frozen_config_detects_tampering(tmp_path):
    target = tmp_path / "prereg.json"
    _freeze(target)
    document = json.loads(target.read_text(encoding="utf-8"))
    document["parameters"]["x"] = 999
    target.write_text(json.dumps(document, indent=2, sort_keys=True), encoding="utf-8")

    with pytest.raises(PreregistrationIntegrityError, match="mismatch"):
        verify_frozen_config(target)


def test_verify_frozen_config_rejects_expected_payload_mismatch(tmp_path):
    target = tmp_path / "prereg.json"
    _freeze(target, x=1)

    with pytest.raises(PreregistrationIntegrityError, match="payload mismatch"):
        verify_frozen_config(target, expected={"parameters": {"x": 2}})


def test_invalid_nonfinite_parameter_does_not_create_partial_file(tmp_path):
    target = tmp_path / "prereg.json"

    with pytest.raises(ValueError):
        _freeze(target, x=float("nan"))

    assert not target.exists()


def test_change_log_refuses_unterminated_existing_line(tmp_path):
    target = tmp_path / "changes.jsonl"
    target.write_text('{"not":"a complete chain"}\n', encoding="utf-8")
    # Remove the newline while leaving otherwise parseable JSON.
    target.write_text('{"not":"a complete chain"}', encoding="utf-8")
    with pytest.raises(PreregistrationIntegrityError, match="end with a newline"):
        verify_change_log(target)


def test_change_log_is_append_only_hash_chain_and_detects_tampering(tmp_path):
    target = tmp_path / "changes.jsonl"
    first = log_change(
        experiment_id="EXP-TEST",
        what_changed="analysis window",
        reason="pre-run correction",
        changelog_path=target,
    )
    second = log_change(
        experiment_id="EXP-TEST",
        what_changed="bootstrap count",
        reason="resource limit",
        changelog_path=target,
    )

    assert verify_change_log(target) == [first, second]
    assert second["previous_entry_hash"] == first["entry_hash"]

    rows = [json.loads(line) for line in target.read_text(encoding="utf-8").splitlines()]
    rows[0]["reason"] = "silently altered"
    target.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    with pytest.raises(PreregistrationIntegrityError):
        verify_change_log(target)
