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
    """The classification must hold whether or not the external package is present.

    The external battery lives outside this repository and is not redistributed
    with it. It is available on the original author's machine and nowhere else,
    so this test runs in two genuinely different states:

      present  -- the markers are read and asserted True
      absent   -- the markers are None, and the audit must NOT report them as
                  False

    That distinction is the point. "I did not look" and "I looked and found
    nothing" are different claims, and a provenance audit that collapses them
    records a negative finding it never made. The conservative
    SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE status is required either
    way: absence of the package does not license treating the in-tree JSON as
    anything other than derived output.
    """
    report = module.analyze()
    assert report["schema"] == "s9-provenance-audit/v1"
    assert report["execution_policy"] == {
        "external_package_executed": False,
        "external_package_imported": False,
        "external_package_written": False,
        "in_tree_historical_files_written": False,
        "raw_participant_data_claimed": False,
    }

    classification = report["classification"]
    assert classification["status"] == "SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE"
    assert classification["external_package_available_for_this_audit"] in (True, False)

    if report["source_package"]["available"]:
        assert classification["simulated_perceptual_response_model_present"] is True
        assert classification["hardcoded_rates_or_models_present"] is True
        assert classification["raw_empirical_loader_markers_present"] is False
        assert classification["raw_input_files_found_in_declared_package"] == 0
        assert report["source_package"]["missing_source_files"] == []
    else:
        # Not inspected, so not False. See the docstring.
        assert classification["simulated_perceptual_response_model_present"] is None
        assert classification["hardcoded_rates_or_models_present"] is None
        assert classification["raw_empirical_loader_markers_present"] is None
        assert classification["raw_input_files_found_in_declared_package"] is None
        assert report["source_package"]["raw_input_inventory"]["available"] is False
        assert "S9_EXTERNAL_ROOT" in report["source_package"]["raw_input_inventory"]["note"]

    # The audit never imports or executes the external package. That is the whole
    # point of it and is asserted regardless of availability.
    assert report["source_package"]["source_package_is_in_lab_tree"] is False


def test_report_hashes_and_in_tree_results_are_strict() -> None:
    """The stored report must verify from any checkout, not just the author's.

    The recorded paths used to be absolute (`C:\\Users\\natha\\...`), so
    `Path(record["path"]).is_file()` was False on CI and on every other
    machine. Paths inside the lab tree are now recorded relative to the root.
    """
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert report["classification"]["status"] == "SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE"
    for record in report["in_tree_results"].values():
        assert record["path_is_repo_relative"] is True, (
            f"{record['path']} is not repo-relative, so this report only verifies "
            "on the machine that generated it"
        )
        path = ROOT / record["path"]
        assert path.is_file(), f"{record['path']} does not resolve from the repo root"
        assert module.sha256(path) == record["sha256"]
        assert path.stat().st_size == record["size_bytes"]
    assert set(report["in_tree_results"]) == {"q_s9_1_results.json", "q_s9_3_results.json"}


def test_exclusive_report_writer_refuses_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "report.json"
    module.write_exclusive(target, {"status": "first"})
    with pytest.raises(module.AuditError, match="refusing to overwrite"):
        module.write_exclusive(target, {"status": "second"})
    assert json.loads(target.read_text(encoding="utf-8"))["status"] == "first"
