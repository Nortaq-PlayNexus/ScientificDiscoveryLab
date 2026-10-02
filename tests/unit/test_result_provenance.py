"""Tests for canonical result hashes and exact result-artifact hashes."""

import json
import sys
from pathlib import Path

import pytest

LAB_ROOT = Path(__file__).resolve().parents[2]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
if str(SHARED_ENGINE) not in sys.path:
    sys.path.insert(0, str(SHARED_ENGINE))

from engine.utilities.core import (  # noqa: E402
    make_experiment_json,
    sha256_file,
    sha256_json,
    verify_experiment_result_hash,
)


def test_result_and_artifact_hashes_have_distinct_explicit_scopes(tmp_path):
    result_path = tmp_path / "result.json"
    result = {"decision": "CONTROLLED", "cells": {"b": 2, "a": 1}}
    # Deliberately non-canonical file formatting and key order.
    result_path.write_text(
        json.dumps(result, indent=4, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    record_path = tmp_path / "experiment.json"

    record = make_experiment_json(
        "EXP-HASH",
        "Q-HASH",
        "HYP-HASH",
        seed=42,
        parameters={"n": 2},
        result=result,
        result_path=result_path,
        out_path=record_path,
    )

    assert record["result_hash"] == sha256_json(result)
    assert record["result_hash_scope"] == "canonical_json_utf8_result_object"
    assert record["result_artifact"]["sha256"] == sha256_file(str(result_path))
    assert record["result_artifact"]["hash_scope"] == "exact_artifact_bytes"
    report = verify_experiment_result_hash(record, result_path=result_path)
    assert report["valid"] is True
    assert report["result_hash_valid"] is True
    assert report["scope_valid"] is True
    assert report["artifact_hash_valid"] is True
    assert report["artifact_size_valid"] is True
    assert report["errors"] == []


def test_result_hash_detects_embedded_result_tampering(tmp_path):
    record = make_experiment_json(
        "EXP-HASH",
        "Q-HASH",
        "HYP-HASH",
        seed=42,
        parameters={},
        result={"value": 1},
    )
    record["result"]["value"] = 2

    report = verify_experiment_result_hash(record)
    assert report["result_hash_valid"] is False


def test_verifier_rejects_tampered_scope_and_size_metadata(tmp_path):
    result_path = tmp_path / "result.json"
    result = {"value": 1}
    result_path.write_text(json.dumps(result), encoding="utf-8")
    record = make_experiment_json(
        "EXP-HASH",
        "Q-HASH",
        "HYP-HASH",
        seed=42,
        parameters={},
        result=result,
        result_path=result_path,
    )
    record["result_hash_scope"] = "unscoped"
    record["canonical_json"]["sort_keys"] = False
    record["result_artifact"]["hash_scope"] = "same_file"
    record["result_artifact"]["size_bytes"] += 1

    report = verify_experiment_result_hash(record, result_path=result_path)
    assert report["valid"] is False
    assert report["scope_valid"] is False
    assert report["artifact_hash_valid"] is True
    assert report["artifact_size_valid"] is False
    assert any("scope mismatch" in error for error in report["errors"])
    assert any("declaration mismatch" in error for error in report["errors"])
    assert any("byte-size mismatch" in error for error in report["errors"])


def test_artifact_hash_detects_file_tampering(tmp_path):
    result_path = tmp_path / "result.json"
    result = {"value": 1}
    result_path.write_text(json.dumps(result), encoding="utf-8")
    record = make_experiment_json(
        "EXP-HASH",
        "Q-HASH",
        "HYP-HASH",
        seed=42,
        parameters={},
        result=result,
        result_path=result_path,
    )
    result_path.write_text(json.dumps({"value": 2}), encoding="utf-8")

    report = verify_experiment_result_hash(record, result_path=result_path)
    assert report["result_hash_valid"] is True
    assert report["artifact_hash_valid"] is False
    assert "result artifact SHA-256 mismatch" in report["errors"]


def test_nonfinite_result_is_rejected_before_record_write(tmp_path):
    result_path = tmp_path / "missing.json"
    record_path = tmp_path / "experiment.json"

    with pytest.raises(ValueError):
        make_experiment_json(
            "EXP-HASH",
            "Q-HASH",
            "HYP-HASH",
            seed=42,
            parameters={},
            result={"bad": float("nan")},
            result_path=result_path,
            out_path=record_path,
        )
    assert not record_path.exists()
