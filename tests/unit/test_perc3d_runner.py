"""Tests for the fail-closed Q-P008 audit-repair runner."""

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

LAB_ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = (
    LAB_ROOT
    / "03_INVESTIGATIONS"
    / "PHYSICS"
    / "percolation_3d"
    / "CODE"
    / "run_audit_repair.py"
)
CONFIG_PATH = (
    LAB_ROOT
    / "03_INVESTIGATIONS"
    / "PHYSICS"
    / "percolation_3d"
    / "CONFIG"
    / "prereg_QP008_AUDIT_R1_SMOKE.json"
)
spec = importlib.util.spec_from_file_location("qp008_audit_runner", RUNNER_PATH)
assert spec is not None and spec.loader is not None
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

C7_PATH = RUNNER_PATH.parent / "REPLICATION" / "independent_check_EXP0011.py"
c7_spec = importlib.util.spec_from_file_location("qp008_c7", C7_PATH)
assert c7_spec is not None and c7_spec.loader is not None
c7 = importlib.util.module_from_spec(c7_spec)
c7_spec.loader.exec_module(c7)


def test_smoke_config_is_content_addressed_and_valid():
    config, digest = runner.load_config(CONFIG_PATH)
    assert config["experiment_id"] == "QP008-AUDIT-R1-SMOKE"
    assert config["config_sha256"] == digest
    assert config["parameters"]["purpose"] == "infrastructure_smoke"


def test_c7_and_primary_runner_use_identical_repaired_seed_and_label_policy():
    config, digest = runner.load_config(CONFIG_PATH)
    c7_config, c7_digest = c7._load_config(CONFIG_PATH)
    assert digest == c7_digest
    for L in (4, 6):
        for realization in (0, 1, 7):
            assert runner.realization_seed(
                config, L, 0, realization
            ) == c7._realization_seed(c7_config, L, realization)
        assert runner.cell_label(config, L, "exp") == c7._cell_label(
            c7_config, L, "exp"
        )
    assert c7.synthetic_self_test()["pass"] is True


def test_non_smoke_config_requires_preregistered_probit_width_estimator():
    config, _ = runner.load_config(CONFIG_PATH)
    invalid = copy.deepcopy(config)
    invalid["parameters"]["purpose"] = "scientific_production"
    with pytest.raises(runner.ConfigError, match="probit_mle"):
        runner.validate_config(invalid)


def test_config_fails_closed_before_monte_carlo_for_invalid_tau_size():
    config, _ = runner.load_config(CONFIG_PATH)
    invalid = copy.deepcopy(config)
    invalid["parameters"]["tau_L"] = 24
    with pytest.raises(runner.ConfigError, match="tau_L"):
        runner.validate_config(invalid)


def test_width_crossing_does_not_substitute_unbracketed_nearest_point():
    result = runner.interpolate_width_crossing(
        [
            {"p": 0.30, "width": 0.2},
            {"p": 0.31, "width": 0.3},
            {"p": 0.32, "width": 0.4},
        ]
    )
    assert result["bracketed"] is False
    assert result["p_c"] is None

    crossed = runner.interpolate_width_crossing(
        [
            {"p": 0.30, "width": 0.4},
            {"p": 0.32, "width": 0.6},
        ]
    )
    assert crossed["p_c"] == pytest.approx(0.31)


def test_ragged_bootstrap_uses_each_configured_length():
    logx = np.log(np.asarray([4, 6], dtype=float))
    rows = [np.arange(1, 6, dtype=float), np.arange(1, 10, dtype=float)]
    first = runner.bootstrap_slope_ragged(logx, rows, 20, "test-ragged", 7)
    second = runner.bootstrap_slope_ragged(logx, rows, 20, "test-ragged", 7)
    assert first.shape == (20,)
    assert np.array_equal(first, second)
    assert np.all(np.isfinite(first))


def test_tau_bootstrap_is_realization_level_and_nonempty():
    tails = [np.arange(1, 501, dtype=np.int64) for _ in range(8)]
    result = runner.fit_tau_realization_bootstrap(
        tails,
        (2, 500),
        draws=20,
        label="test-tau-realization",
        seed=11,
    )
    assert result["status"] == "FITTED"
    assert result["tau"] is not None
    assert result["n_realizations_nonempty_tail"] == 8
    assert result["bootstrap_accepted"] > 0
    assert result["uncertainty_unit"] == "realization"


def test_historical_results_descendants_are_refused():
    historical_child = runner.HERE / "RESULTS" / "should-not-exist"
    with pytest.raises(runner.ConfigError, match="historical RESULTS"):
        runner.main(
            ["--config", str(CONFIG_PATH), "--output-dir", str(historical_child)]
        )
    assert not historical_child.exists()


def test_end_to_end_smoke_is_partial_nonzero_and_authenticated(tmp_path):
    output = tmp_path / "qp008-smoke"
    assert runner.main(["--config", str(CONFIG_PATH), "--output-dir", str(output)]) == 3
    result_path = output / "QP008-AUDIT-R1-SMOKE_results.json"
    sidecar_path = output / "QP008-AUDIT-R1-SMOKE_results.sha256.json"
    record = json.loads(result_path.read_text(encoding="utf-8"))
    result = record["result"]
    assert result["schema"] == "q-p008/audit-repair-result/v2"
    assert result["status"] == "INFRASTRUCTURE_SMOKE_PARTIAL"
    assert result["required_analysis_complete"] is False
    assert result["decision"] == "INCONCLUSIVE"
    assert result["science_authorized"] is False
    assert result["scientific_result"] is None
    assert result["novelty_claim"] is False
    assert result["width"]["width_estimator"] == "adjacent_linear_smoke_diagnostic"
    assert set(result["width"]["raw_manifest"]) == {"4", "6"}
    assert set(result["raw_manifest"]) == {"4", "6"}
    assert result["exponents"]["Df"]["n_by_L"] == {"4": 4, "6": 3}
    assert record["result_hash_scope"] == "canonical_json_utf8_result_object"
    assert runner.verify_experiment_result_hash(record)["valid"] is True
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["sha256"] == hashlib.sha256(result_path.read_bytes()).hexdigest()
    assert sidecar["size_bytes"] == result_path.stat().st_size
    assert sidecar["hash_scope"] == "exact_artifact_bytes"

    with pytest.raises(runner.ConfigError, match="overwrite"):
        runner.main(["--config", str(CONFIG_PATH), "--output-dir", str(output)])
