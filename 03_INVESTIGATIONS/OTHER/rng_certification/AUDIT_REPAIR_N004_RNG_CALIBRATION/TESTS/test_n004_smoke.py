from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

REPAIR_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = REPAIR_ROOT.parents[3]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
CODE_ROOT = REPAIR_ROOT / "CODE"
for path in (SHARED_ENGINE, CODE_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

CAL_SPEC = importlib.util.spec_from_file_location("n004_calibration_test", CODE_ROOT / "n004_calibration.py")
assert CAL_SPEC is not None and CAL_SPEC.loader is not None
cal = importlib.util.module_from_spec(CAL_SPEC)
sys.modules[CAL_SPEC.name] = cal
CAL_SPEC.loader.exec_module(cal)

RUN_SPEC = importlib.util.spec_from_file_location("n004_smoke_test", CODE_ROOT / "run_n004_smoke.py")
assert RUN_SPEC is not None and RUN_SPEC.loader is not None
runner = importlib.util.module_from_spec(RUN_SPEC)
sys.modules[RUN_SPEC.name] = runner
RUN_SPEC.loader.exec_module(runner)

FREEZE_SPEC = importlib.util.spec_from_file_location("n004_freeze_test", CODE_ROOT / "freeze_n004.py")
assert FREEZE_SPEC is not None and FREEZE_SPEC.loader is not None
freeze = importlib.util.module_from_spec(FREEZE_SPEC)
sys.modules[FREEZE_SPEC.name] = freeze
FREEZE_SPEC.loader.exec_module(freeze)

CONFIG_PATH = REPAIR_ROOT / "CONFIG" / "n004_smoke_config.json"
AUDIT_RESULT = LAB_ROOT / "AUDIT/INDEPENDENT_AUDIT_20260924/rng_calibration_results.json"


def test_frozen_config_is_valid_and_smoke_only() -> None:
    config = runner.load_config(CONFIG_PATH)
    assert config["experiment_id"] == "N-004-RNG-CALIBRATION-SMOKE"
    assert config["parameters"]["execution_class"] == "infrastructure_smoke"
    assert config["parameters"]["production_run"] is False
    assert config["parameters"]["certification_claim"] is False
    assert config["parameters"]["scientific_result"] is None


def test_exact_historical_80x24_replay() -> None:
    replay = cal.replay_historical_audit(AUDIT_RESULT)
    assert replay["status"] == "PASS_EXACT_80X24_REPLAY"
    assert replay["stream_mode"] == "historical_shared_arrays"
    assert set(replay["summaries"]) == {"G_LAB", "G_PCG", "G_MT"}
    assert replay["summaries"]["G_LAB"]["n_seeds"] == 80
    assert replay["summaries"]["G_LAB"]["holm_fwer_over_test_marginals"]["n_total"] == 24


def test_holm_known_example_and_nan_policy() -> None:
    result = cal.holm_fwer([0.001, 0.02, 0.04, np.nan], alpha=0.05)
    assert result["n_total"] == 4
    assert result["n_finite"] == 3
    assert result["rejected_indices"] == [0, 1, 2]
    assert result["adjusted_pvalues"] == pytest.approx([0.003, 0.04, 0.04, None])


def test_row_preserving_resampling_keeps_duplicate_columns_dependent() -> None:
    base = np.arange(12, dtype=float).reshape(6, 2)
    matrix = np.column_stack([base[:, 0], base[:, 0]])
    sampled, indices = cal.row_preserving_resample(matrix, draws=5, seed=19)
    assert sampled.shape == (5, 6, 2)
    assert indices.shape == (5, 6)
    assert np.array_equal(sampled[:, :, 0], sampled[:, :, 1])


def test_dependence_diagnostics_reports_identical_pair() -> None:
    matrix = np.column_stack([np.arange(8, dtype=float), np.arange(8, dtype=float)])
    result = cal.dependence_diagnostics(matrix)
    assert result["identical_column_pairs"] == [[0, 1]]


def test_production_guard_fails_before_smoke_execution() -> None:
    config = runner.load_config(CONFIG_PATH)
    invalid = copy.deepcopy(config)
    invalid["parameters"]["production_run"] = True
    with pytest.raises(runner.SmokeError, match="production execution"):
        runner.validate_config(invalid)


def test_claim_contract_rejects_decision_fields() -> None:
    with pytest.raises(runner.SmokeError, match="forbidden claim field"):
        runner.validate_claim_contract(
            {
                "status": "INFRASTRUCTURE_SMOKE_ONLY",
                "scientific_result": None,
                "certification_claim": False,
                "production_run_launched": False,
                "decision": "CERTIFIED",
            }
        )


def test_smoke_is_bounded_and_refuses_overwrite(tmp_path: Path) -> None:
    output = tmp_path / "smoke"
    payload = runner.run_smoke(CONFIG_PATH, output)
    assert payload["status"] == "INFRASTRUCTURE_SMOKE_ONLY"
    assert payload["scientific_result"] is None
    assert payload["certification_claim"] is False
    assert payload["production_run_launched"] is False
    assert "decision" not in json.dumps(payload)
    assert (output / "N004_rng_calibration_smoke_results.json").is_file()
    assert (output / "N004_rng_calibration_smoke_manifest.json").is_file()
    with pytest.raises(runner.SmokeError, match="refusing to overwrite"):
        runner.run_smoke(CONFIG_PATH, output)


def test_freeze_is_exclusive(tmp_path: Path) -> None:
    target = tmp_path / "CONFIG" / "frozen.json"
    created = freeze.freeze_protocol(target)
    assert created == target
    assert json.loads(created.read_text(encoding="utf-8"))["experiment_id"] == "N-004-RNG-CALIBRATION-SMOKE"
    with pytest.raises(FileExistsError):
        freeze.freeze_protocol(target)
