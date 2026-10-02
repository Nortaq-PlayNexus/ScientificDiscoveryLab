from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
AUDIT_ROOT = HERE.parent
sys.path.insert(0, str(AUDIT_ROOT))

import run_audit_repair as repair  # noqa: E402


CONFIG_PATH = AUDIT_ROOT / "CONFIG" / "prereg_pga_audit_n06_n08_20260924.json"
DIGEST_PATH = AUDIT_ROOT / "CONFIG" / "prereg_pga_audit_n06_n08_20260924.sha256"


def test_frozen_config_loads_and_is_hash_locked() -> None:
    config = repair.load_frozen_config(CONFIG_PATH, DIGEST_PATH)
    assert config["analysis_id"] == repair.ANALYSIS_ID
    assert config["sieve_smoke"]["run_production"] is False


def test_missing_config_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(repair.AuditInputError):
        repair.load_frozen_config(tmp_path / "missing.json", tmp_path / "missing.sha256")


def test_hash_mismatch_fails_closed(tmp_path: Path) -> None:
    config_copy = tmp_path / "config.json"
    config_copy.write_bytes(CONFIG_PATH.read_bytes())
    digest_copy = tmp_path / "config.sha256"
    digest_copy.write_text("0" * 64 + " config.json\n", encoding="ascii")
    with pytest.raises(repair.AuditIntegrityError):
        repair.load_frozen_config(config_copy, digest_copy)


def test_malformed_config_fails_closed(tmp_path: Path) -> None:
    config_copy = tmp_path / "config.json"
    config_copy.write_text('{"schema_version":', encoding="utf-8")
    digest_copy = tmp_path / "config.sha256"
    digest_copy.write_text(
        hashlib.sha256(config_copy.read_bytes()).hexdigest() + " config.json\n",
        encoding="ascii",
    )
    with pytest.raises(repair.AuditInputError):
        repair.load_frozen_config(config_copy, digest_copy)


def test_missing_required_config_key_fails_closed(tmp_path: Path) -> None:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    del config["normalization"]
    config_copy = tmp_path / "config.json"
    config_copy.write_text(json.dumps(config), encoding="utf-8")
    digest_copy = tmp_path / "config.sha256"
    digest_copy.write_text(
        hashlib.sha256(config_copy.read_bytes()).hexdigest() + " config.json\n",
        encoding="ascii",
    )
    with pytest.raises(repair.AuditInputError):
        repair.load_frozen_config(config_copy, digest_copy)


def test_lower_prime_normalization_and_boundary_assignment() -> None:
    lower = np.asarray([10007, 10009, 10037], dtype=np.int64)
    upper = np.asarray([10009, 10037, 10039], dtype=np.int64)
    delta = (upper - lower).astype(np.float64) / np.log(lower.astype(np.float64))
    np.testing.assert_allclose(
        delta[:2],
        [(10009 - 10007) / math.log(10007), (10037 - 10009) / math.log(10009)],
    )
    upper_normalized = (upper - lower).astype(np.float64) / np.log(
        upper.astype(np.float64)
    )
    assert not np.allclose(delta, upper_normalized)

    edges = repair.make_exponential_bin_edges()
    accumulator = repair.StreamingGapAccumulator(
        [repair.BlockSpec("left", 10007, 10009), repair.BlockSpec("right", 10009, 10037)],
        edges,
        simulation_replicates=0,
        seed=1,
    )
    accumulator.ingest_segment(
        repair.PrimeSegment(
            0,
            0,
            20000,
            np.asarray([10007, 10009, 10037, 10039], dtype=np.int64),
        )
    )
    assert accumulator.states["left"].n == 1
    assert accumulator.states["right"].n == 1
    assert accumulator.states["right"].last_upper == 10037


def test_step_up_bh_propagates_later_rank() -> None:
    result = repair.bh_step_up([math.log10(0.009), math.log10(0.008)], 0.01)
    assert result["rejected"] == [True, True]
    assert result["largest_qualifying_rank"] == 2


def test_log_survival_has_no_artificial_zero() -> None:
    result = repair.chi_square_survival(868281.0185213662, 9)
    assert result["p_value"] is None
    assert result["p_value_representable"] is False
    assert -188527.0 < result["log10_p_value"] < -188525.0
    moderate = repair.chi_square_survival(836.2, 1)
    assert moderate["p_value"] is not None
    assert moderate["p_value"] > 0.0
    assert math.isclose(moderate["p_value"], 7.273513898650269e-184, rel_tol=1e-12)
    extreme = repair.normal_two_sided_survival(1000.0)
    assert extreme["p_value"] is None
    assert extreme["log10_p_value"] < -200000.0


def test_exact_parity_support_leaves_first_bin_empty() -> None:
    edges = repair.make_exponential_bin_edges()
    lower = np.asarray([10_000, 99_999], dtype=np.float64)
    probabilities = repair.parity_bin_probabilities(lower, edges)
    assert np.all(probabilities[:, 0] == 0.0)
    assert np.allclose(probabilities.sum(axis=1), 1.0)
    rng = np.random.default_rng(20260924)
    simulated = repair.simulate_discrete_gap_values(lower, rng)
    bins = np.searchsorted(edges[1:-1], simulated, side="right")
    assert np.all(bins != 0)
    reconstructed_steps = simulated * np.log(lower) / 2.0
    np.testing.assert_allclose(reconstructed_steps, np.rint(reconstructed_steps))


def test_segmented_sieve_matches_trusted_small_sieves_and_boundaries() -> None:
    checks = repair.verify_small_sieve_controls()
    assert all(item["match"] for item in checks["checks"])
    assert checks["boundary_ranges_limit_10_size_4"] == [
        {"lo": 0, "hi": 3},
        {"lo": 4, "hi": 7},
        {"lo": 8, "hi": 10},
    ]
    primes = np.fromiter(repair.iter_segmented_primes(1000, 7), dtype=np.int64)
    np.testing.assert_array_equal(primes, repair.simple_sieve_primes(1000))
    assert len(primes) == 168


def test_first_segment_retains_all_primes_through_1e8() -> None:
    # This is intentionally a real first-segment control, not a mocked count.
    primes = np.fromiter(
        repair.iter_segmented_primes(repair.FIRST_SEGMENT_LIMIT, repair.FIRST_SEGMENT_LIMIT),
        dtype=np.int64,
    )
    assert len(primes) == 5_761_455
    assert int(primes[0]) == 2
    assert int(primes[-1]) == 99_999_989
    assert int(np.count_nonzero(primes <= repair.FIRST_SEGMENT_LIMIT)) == len(primes)


def test_production_limit_is_fail_closed() -> None:
    config = repair.load_frozen_config(CONFIG_PATH, DIGEST_PATH)
    config["sieve_smoke"]["sieve_limit"] = repair.PRODUCTION_LIMIT
    with pytest.raises(repair.AuditInputError):
        repair.run_smoke(config)


def test_exclusive_writer_refuses_overwrite(tmp_path: Path) -> None:
    path = tmp_path / "artifact.json"
    repair.write_exclusive(path, b"first")
    with pytest.raises(repair.AuditOutputError):
        repair.write_exclusive(path, b"second")
    assert path.read_bytes() == b"first"


def test_positive_expected_in_impossible_cell_is_not_given_fake_p() -> None:
    result = repair.pearson_chi_square([1, 1], [0.0, 2.0], True, "test")
    assert result["status"] == "INCOMPATIBLE_WITH_DECLARED_SUPPORT"
    assert result["p_value"] is None
    assert result["log10_p_value"] is None
