from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = Path(__file__).resolve().parents[1] / "CODE" / "run_read_only_audit.py"
REPORT = Path(__file__).resolve().parents[1] / "RESULTS" / "provenance_report.json"
SPEC = importlib.util.spec_from_file_location("s9_provenance_audit", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def test_read_only_audit_classifies_synthetic_package() -> None:
    report = module.analyze()
    assert report["schema"] == "s9-provenance-audit/v1"
    assert report["execution_policy"] == {
        "external_package_executed": False,
        "external_package_imported": False,
        "external_package_written": False,
        "in_tree_historical_files_written": False,
        "raw_participant_data_claimed": False,
    }
    assert report["classification"]["status"] == "SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE"
    assert report["classification"]["simulated_perceptual_response_model_present"] is True
    assert report["classification"]["hardcoded_rates_or_models_present"] is True
    assert report["classification"]["raw_input_files_found_in_declared_package"] == 0


def test_report_hashes_and_in_tree_results_are_strict() -> None:
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["classification"]["status"] == "SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE"
    for record in report["in_tree_results"].values():
        path = Path(record["path"])
        assert path.is_file()
        assert module.sha256(path) == record["sha256"]
        assert path.stat().st_size == record["size_bytes"]
    assert set(report["in_tree_results"]) == {"q_s9_1_results.json", "q_s9_3_results.json"}


def test_exclusive_report_writer_refuses_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "report.json"
    module.write_exclusive(target, {"status": "first"})
    with pytest.raises(module.AuditError, match="refusing to overwrite"):
        module.write_exclusive(target, {"status": "second"})
    assert json.loads(target.read_text(encoding="utf-8"))["status"] == "first"
