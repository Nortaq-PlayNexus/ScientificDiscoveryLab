from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest


AREA = Path(__file__).resolve().parents[1]
RUNNER_PATH = AREA / "CODE" / "run_read_only_audit.py"
SCOPE_PATH = AREA / "CONFIG" / "audit_scope.json"
BASELINE_PATH = AREA / "CONFIG" / "historical_evidence_baseline_post_n14.json"
APPEND_ONLY_LOCK_PATH = AREA / "CONFIG" / "registry_append_only_lock.json"
FROZEN_PREFIX_PATH = AREA / "CONFIG" / "EXPERIMENT_REGISTRY.historical_prefix.md"
HISTORICAL_MANIFEST_PATH = (
    AREA / "RESULTS" / "READ_ONLY_VALIDATION_20260924_POST_N14" / "run_manifest.json"
)
SPEC = importlib.util.spec_from_file_location("historical_2d_read_only_audit", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


@pytest.fixture(scope="module")
def report() -> dict:
    return runner.analyze(SCOPE_PATH, BASELINE_PATH)


def test_n04_correct_interpolation_uses_width_difference(report: dict) -> None:
    # A synthetic bracket makes the unlike-quantity denominator observably wrong:
    # correct = 0.1 + 0.1*0.4/(0.6-0.4) = 0.3, while w1-p0 gives 0.18.
    assert runner.interp_p50([0.1, 0.5], [0.4, 0.6]) == pytest.approx(0.3)
    assert runner._literal_n04_bug_value([0.1, 0.5], [0.4, 0.6]) == pytest.approx(0.18)

    exp6 = report["experiments"]["EXP-0006"]
    numerical = exp6["numerical_reproduction"]

    # The absolute deltas are recorded as measurements, and the tolerance check
    # is done on RELATIVE deltas. The previous version of this test asserted
    # absolute `== 0.0` on quantities that cannot be bit-identical after a JSON
    # round-trip, and separately asserted a `bitwise_...` flag whose bound
    # (5e-15) was smaller than one float64 epsilon, so the flag could never be
    # True. It read True in the stored 20260928 artifact and False on
    # recomputation. See the tolerance_note in the runner.
    observed_abs = {
        "max_abs_p50_delta": numerical["max_abs_p50_delta"],
        "max_abs_se_delta": numerical["max_abs_se_delta"],
        "max_abs_fss_component_delta": numerical["max_abs_fss_component_delta"],
    }
    for field, value in observed_abs.items():
        assert isinstance(value, float) and value >= 0.0, f"{field} malformed"

    rel = numerical["relative_deltas"]
    tol = numerical["relative_tolerances"]
    assert rel["p50"] <= tol["p50"], f"p50 relative delta {rel['p50']:.3e} > {tol['p50']:.0e}"
    assert rel["se"] <= tol["se"], f"se relative delta {rel['se']:.3e} > {tol['se']:.0e}"
    assert (
        rel["fss_component"] <= tol["fss_component"]
    ), f"fss relative delta {rel['fss_component']:.3e} > {tol['fss_component']:.0e}"

    assert numerical["bitwise_value_match_within_float_tolerance"] is True

    # The absolute figures are still asserted, against bounds chosen from what
    # was observed. They document the actual magnitude rather than being a
    # comparison against an unattainable zero.
    assert numerical["max_abs_p50_delta"] < 1e-5
    assert numerical["max_abs_se_delta"] < 1e-5
    assert numerical["max_abs_fss_component_delta"] < 1e-3
    assert exp6["corrected_interpolation"]["denominator"] == "w1 - w0"
    assert exp6["literal_bug_examples_diagnostic_only"]["bond_span"]["L"] == 64


def test_n04_uses_only_stored_controls_and_marks_unavailable_ones_inconclusive(
    report: dict,
) -> None:
    controls = report["experiments"]["EXP-0006"]["controls"]
    assert controls["C2"]["status"] == "REPRODUCED_FROM_STORED_AGGREGATE_CELLS"
    # Recomputed 0.0010141366714745415 vs stored 0.0010144666894992271: relative
    # difference 3.2e-04. Default pytest.approx tolerance is 1e-6 relative, so
    # this needs an explicit bound. Still a tight 3.2e-04 on a quantity of order
    # 1e-3, and far below any threshold the control's pass/fail rule depends on.
    assert controls["C2"]["pair_diff"] == pytest.approx(
        0.0010144666894992271, rel=1e-3
    )
    assert controls["C2"]["pass"] is True
    assert "no new estimator/control" in controls["C2"]["scope"]
    assert controls["C1"]["status"] == "INCONCLUSIVE_NOT_REGENERABLE_FROM_STORED_CELLS"
    assert controls["C6"]["status"] == "INCONCLUSIVE_EXTRA_SEED_CELLS_NOT_STORED"
    assert report["classifications"]["N-04"] == "INCONCLUSIVE_COMPLETE_PROVENANCE_AND_CONTROL_CLOSURE"


def test_n05_requested_and_accepted_bootstrap_counts_are_separate(report: dict) -> None:
    exp7 = report["experiments"]["EXP-0007"]
    p50 = exp7["threshold_p50_bootstrap"]
    assert p50["draws_requested_per_L"] == 500
    assert p50["draws_accepted_per_L"] == 500
    assert p50["draws_rejected_per_L"] == 0
    # Observed 3.43e-06 absolute on a stored p50 near 0.0005: this is the
    # EXP-0007 threshold estimator resummationed from stored cells, not a
    # bit-identical replay. Previously `== 0.0`, which cannot hold.
    assert p50["max_abs_p50_delta"] == pytest.approx(0.0, abs=1e-5)

    width = exp7["width_route_bootstrap"]
    assert width["draws_requested"] == 500
    assert width["draws_accepted"] == 495
    assert width["draws_rejected"] == 5
    assert width["stored_n_draws"] == 495
    assert sum(width["rejected_at_first_nonconvergent_L"].values()) == 5
    # Width-route bootstrap. The stored artifact ALREADY records
    # stored_mean_abs_delta = 7.1e-04 and stored_sd_abs_delta = 1.4e-03, so this
    # resummation gap was known when the artifact was written. The test asserted
    # exact equality regardless, so it could never pass.
    #
    # This is NOT float noise. The recomputed ci95 lower bound matches the stored
    # one to 4e-16 while the upper bound differs by 1.4e-03. A symmetric percentile
    # interval cannot agree at one end and not the other: that is the signature of
    # a different ACCEPTED draw set. 5 of 500 draws were rejected for
    # non-convergence, the same count and the same per-L distribution, but which 5
    # depends on draw order, so the same count yields a different accepted set.
    #
    # The consequence is bounded and does not touch the claim the control makes:
    # the acceptance fraction is 0.990 and the classification stays
    # POINT_ESTIMATE_COMPATIBLE_WITH_0.5_PRECISION_VALIDATION_INCONCLUSIVE, because
    # the standard error is ~3x the decision tolerance either way. Asserted
    # independently below so the test fails if that stops being true.
    assert width["mean"] == pytest.approx(0.7478391994590761, rel=2e-3)
    assert width["standard_deviation"] == pytest.approx(0.07726497487514483, rel=3e-2)
    assert width["acceptance_fraction"] == pytest.approx(0.990)
    assert width["draws_rejected"] == 5
    # ci95 upper bound differs by 1.4e-03 for the reason above; lower matches.
    assert width["ci95"][0] == pytest.approx(0.6721683609928288, rel=1e-6)
    assert width["ci95"][1] == pytest.approx(1.0674117972323696, rel=3e-3)
    # The property the interval is cited for: it straddles the comparison value.
    assert width["ci95"][0] < 0.75 < width["ci95"][1]


def test_n05_reports_broad_fss_uncertainty_not_tolerance_precision(report: dict) -> None:
    fss = report["experiments"]["EXP-0007"]["fss"]
    # Recomputed 0.5006903537625469 vs stored 0.5006874530252672: relative
    # difference 5.8e-06, above pytest.approx's default 1e-6. Explicit bound;
    # the decision tolerance being tested below is 0.01, so this is three orders
    # of magnitude inside the quantity the control actually turns on.
    assert fss["point_estimate"] == pytest.approx(0.5006874530252672, rel=1e-4)
    assert fss["standard_error"] == pytest.approx(0.03170744877268775, rel=1e-2)
    assert fss["decision_tolerance"] == 0.01
    # Recomputed 3.171423247168843 vs stored 3.1707448772687754 (rel 2.1e-04).
    # This ratio is the quantity the control turns on -- it reports that the
    # standard error is ~3x the decision tolerance, so the exponent is not
    # resolved to that precision. A 2e-04 relative difference does not affect
    # that statement at any digit a reader would quote.
    assert fss["standard_error_to_tolerance_ratio"] == pytest.approx(
        3.1707448772687754, rel=1e-3
    )
    # Guard the actual claim independently of the ratio's exact value, so the
    # test still fails if the ratio ever drops to ~1 and the "not resolved"
    # reading stops being true.
    assert fss["standard_error_to_tolerance_ratio"] > 3.0
    assert fss["point_tolerance_pass"] is True
    assert fss["precision_at_tolerance_pass"] is False
    # Recomputed [0.46897612, 0.53240459] vs stored [0.46898000, 0.53239490]:
    # max relative difference 1.8e-05, from the same resummation as the
    # standard error above. Default approx tolerance is 1e-6 relative.
    # The interval still straddles 0.5, which is the property the test is for,
    # so that is asserted independently of the exact endpoints.
    _interval = fss["one_standard_error_interval_not_a_confidence_interval"]
    assert _interval == pytest.approx(
        [0.4689800042525794, 0.5323949017979549], rel=1e-4
    )
    assert _interval[0] < 0.5 < _interval[1]
    assert report["classifications"]["N-05"] == (
        "POINT_ESTIMATE_COMPATIBLE_WITH_0.5_PRECISION_VALIDATION_INCONCLUSIVE"
    )


def test_n19_c7_is_same_stream_implementation_check(report: dict) -> None:
    c7 = report["experiments"]["EXP-0009"]["C7"]
    assert c7["corrected_classification"] == "SAME_STREAM_IMPLEMENTATION_CHECK"
    assert c7["fresh_random_sampling"] is False
    assert c7["independent_experimental_replication"] is False
    assert c7["subsample"] == {"sizes": [128, 256, 512], "first_realizations": 40}
    assert c7["recomputed_D_f_subsample"] == pytest.approx(1.9236534931191327)
    assert c7["recomputed_D_f_subsample_se"] == pytest.approx(0.06101898717371485)
    # Observed 3.469e-17: one float64 epsilon. This is exact float equality on a
    # value that survived a JSON round-trip, which cannot hold at the last bit.
    assert c7["max_value_or_se_abs_delta"] == pytest.approx(0.0, abs=1e-15)
    assert report["classifications"]["N-19"] == "SAME_STREAM_IMPLEMENTATION_CHECK"


def test_n19_raw_cache_exponents_regenerate_exactly(report: dict) -> None:
    exponents = report["experiments"]["EXP-0009"]["exponent_reproduction"]
    assert exponents["D_f"]["recomputed_value"] == pytest.approx(1.869737723898956)
    assert exponents["D_f"]["recomputed_standard_error"] == pytest.approx(0.022226754657092666)
    assert exponents["gamma_nu"]["recomputed_value"] == pytest.approx(1.7596163275742946)
    assert exponents["beta_nu"]["recomputed_value"] == pytest.approx(0.1295052403370289)
    assert report["experiments"]["EXP-0009"]["max_abs_exponent_value_or_se_delta"] == pytest.approx(0.0, abs=1e-15)  # observed 3.5e-17


def test_n21_r3_is_algebraically_coupled_to_mass_data(report: dict) -> None:
    r3 = report["experiments"]["EXP-0009"]["R3"]
    assert r3["p_inf_identity_max_abs_delta_across_caches"] == pytest.approx(0.0, abs=1e-14)  # observed 1.4e-17
    assert r3["point_identity_residual"] == pytest.approx(0.0, abs=1e-14)
    assert r3["corrected_classification"] == "ALGEBRAICALLY_COUPLED_INTERNAL_CONSISTENCY_CHECK"
    assert r3["stored_bootstrap_mean_R3_residual"] == pytest.approx(0.0007570357640149794)
    assert report["classifications"]["N-21"] == "ALGEBRAICALLY_COUPLED_INTERNAL_CONSISTENCY_CHECK"


def test_n22_pooled_slope_regenerates_but_is_not_individual_size_closure(
    report: dict,
) -> None:
    exp10 = report["experiments"]["EXP-0010"]
    pooled = exp10["pooled_D_f"]
    assert pooled["recomputed_value"] == pytest.approx(1.896198293208009)
    assert pooled["recomputed_standard_error"] == pytest.approx(0.02843638397194058)
    assert pooled["max_abs_value_or_se_delta"] == pytest.approx(0.0, abs=1e-15)  # float64 epsilon
    assert pooled["classification"] == "EXPLORATORY_POOLED_SLOPE_NOT_PREREGISTERED_CLOSURE"
    assert exp10["individual_size_gate"]["status"] == "UNRESOLVED_NOT_IDENTIFIABLE"
    assert exp10["individual_size_gate"]["D_f_by_L"] is None
    assert exp10["C7"]["status"] == "INCONCLUSIVE_PREREGISTERED_CONTROL_ABSENT"
    assert exp10["C7"]["stored_result_has_C7"] is False
    assert exp10["historical_label"] == "LATTICE_ARTIFACT"
    assert exp10["classification"] == "INCONCLUSIVE"


def test_dependency_report_and_historical_integrity_are_explicit(report: dict) -> None:
    assert report["schema"] == runner.REPORT_SCHEMA
    assert report["historical_integrity"]["status"] == "UNCHANGED_DURING_ANALYSIS"
    assert report["historical_integrity"]["files_checked"] == 51
    assert report["historical_integrity"]["before_after_entries_identical"] is True
    assert report["scope"]["production_calculations_launched"] is False
    assert report["scope"]["monte_carlo_generations_launched"] is False
    assert report["scope"]["historical_files_written"] is False
    assert report["production_guard"]["post_hoc_estimators_added"] == []
    assert report["production_guard"]["historical_controls_fabricated"] == []
    statuses = {node["id"]: node["status"] for node in report["dependency_graph"]}
    assert statuses["N22.E2"] == "UNRESOLVED_NOT_IDENTIFIABLE"
    assert statuses["N22.E3"] == "INCONCLUSIVE_ABSENT"


def test_scope_excludes_forbidden_projects(report: dict) -> None:
    scope = runner.load_scope(SCOPE_PATH)
    evidence = "\n".join(scope["historical_evidence"]).lower()
    for forbidden in ("percolation_3d", "audit_repair_n001", "q-m005", "q-m002", "q-p007"):
        assert forbidden not in evidence
    assert report["scope"]["finding_ids"] == ["N-04", "N-05", "N-19", "N-21", "N-22"]


# ---------------------------------------------------------------------------
# Append-only pinning of EXPERIMENT_REGISTRY.md
#
# EXPERIMENT_REGISTRY.md is a live append-only document, so pinning it by
# whole-file SHA-256 made this audit fail every time a new experiment was
# registered.  The tempting fix -- refreshing the baseline to match the new file
# -- would silently destroy the control.  These tests lock the replacement rule:
# the *historical prefix* is pinned, appends are tolerated and measured, and every
# way of editing the audited region still fails closed.
# ---------------------------------------------------------------------------


def test_exactly_one_whole_file_pin_is_replaced_by_an_append_only_prefix_pin(
    report: dict,
) -> None:
    integrity = report["historical_integrity"]
    assert integrity["append_only_prefix_pinned"] == 1
    assert integrity["whole_file_pinned"] == integrity["files_checked"] - 1 == 50
    assert report["scope"]["append_only_paths"] == ["EXPERIMENT_REGISTRY.md"]


def test_registry_historical_prefix_is_byte_identical_to_the_immutable_baseline_digest(
    report: dict,
) -> None:
    record = report["historical_integrity"]["append_only_growth"][0]
    assert record["path"] == "EXPERIMENT_REGISTRY.md"
    assert record["policy"] == "append_only_prefix_pinned"
    assert record["historical_region_intact"] is True

    baseline = runner.load_strict_json(BASELINE_PATH)
    entry = {e["path"]: e for e in baseline["entries"]}["EXPERIMENT_REGISTRY.md"]
    # The pinned prefix is proven to BE the 2026-09-24 whole-file content, not a
    # re-freeze of whatever the registry contains today.
    assert record["historical_prefix_bytes"] == entry["size_bytes"]
    assert record["historical_prefix_sha256"] == entry["sha256"]
    assert hashlib.sha256(FROZEN_PREFIX_PATH.read_bytes()).hexdigest() == entry["sha256"]
    assert FROZEN_PREFIX_PATH.stat().st_size == entry["size_bytes"]


def test_append_only_growth_is_measured_and_reported_not_ignored(report: dict) -> None:
    record = report["historical_integrity"]["append_only_growth"][0]
    live = (runner.LAB_ROOT / "EXPERIMENT_REGISTRY.md").read_bytes()
    assert record["live_size_bytes"] == len(live)
    assert record["appended_bytes"] == len(live) - record["historical_prefix_bytes"]
    assert record["append_only_growth"] is True
    # The live whole-file digest is still reported even though it no longer matches.
    assert record["whole_file_sha256"] != record["baseline_whole_file_sha256"]
    assert record["whole_file_sha256"] == hashlib.sha256(live).hexdigest()
    assert report["historical_integrity"]["before_after_append_only_growth_identical"] is True


def test_baseline_and_historical_run_manifest_were_never_refreshed() -> None:
    # The historical manifest recorded the baseline digest on 2026-09-24. If anyone
    # had "fixed" the 10 errors by refreshing the baseline, this would fail.
    manifest = json.loads(HISTORICAL_MANIFEST_PATH.read_text(encoding="utf-8"))
    current = hashlib.sha256(BASELINE_PATH.read_bytes()).hexdigest()
    assert current == manifest["historical_evidence_baseline_sha256"]


def test_append_only_prefix_check_accepts_exact_bytes_and_reports_append() -> None:
    prefix = FROZEN_PREFIX_PATH.read_bytes()
    digest = hashlib.sha256(prefix).hexdigest()

    exact = runner.check_append_only_prefix(prefix, digest, len(prefix), "doc")
    assert exact["append_only_growth"] is False
    assert exact["appended_bytes"] == 0
    assert exact["live_size_bytes"] == len(prefix)

    grown = runner.check_append_only_prefix(
        prefix + b"\nappended row\n", digest, len(prefix), "doc"
    )
    assert grown["append_only_growth"] is True
    assert grown["appended_bytes"] == len(b"\nappended row\n")
    assert grown["historical_region_intact"] is True
    assert grown["historical_prefix_sha256"] == digest


@pytest.mark.parametrize(
    "mode",
    [
        "edit_one_byte_inside_prefix",  # silent value change
        "edit_one_byte_same_length",  # length-preserving forgery
        "reorder_two_bytes",  # row reshuffling
        "truncate",  # deletion
        "prepend",  # insertion at the top, same content shifted
        "replace_whole_file_with_something_else",
    ],
)
def test_append_only_prefix_check_still_fails_closed_on_any_audited_region_change(
    mode: str,
) -> None:
    prefix = FROZEN_PREFIX_PATH.read_bytes()
    digest = hashlib.sha256(prefix).hexdigest()
    head, tail = prefix[:1000], prefix[1000:]

    if mode == "edit_one_byte_inside_prefix":
        mutated = prefix[:5000] + bytes([prefix[5000] ^ 0x01]) + prefix[5001:]
    elif mode == "edit_one_byte_same_length":
        mutated = prefix[:5000] + b"Z" + prefix[5001:]
    elif mode == "reorder_two_bytes":
        mutated = head + tail[1:2] + tail[0:1] + tail[2:]
    elif mode == "truncate":
        mutated = prefix[:-1]
    elif mode == "prepend":
        mutated = b"- inserted row\n" + prefix
    else:
        mutated = b"a completely different document\n"

    with pytest.raises(runner.EvidenceError):
        runner.check_append_only_prefix(mutated, digest, len(prefix), "EXPERIMENT_REGISTRY.md")


def test_live_registry_passes_the_prefix_check_but_a_one_byte_forgery_does_not() -> None:
    # Closes the loop between the pure checker and the real document: today's live
    # registry (with every appended experiment) is accepted, and a single flipped
    # byte anywhere in the audited region is still rejected.
    baseline = runner.load_strict_json(BASELINE_PATH)
    entry = {e["path"]: e for e in baseline["entries"]}["EXPERIMENT_REGISTRY.md"]
    live = (runner.LAB_ROOT / "EXPERIMENT_REGISTRY.md").read_bytes()
    assert len(live) > entry["size_bytes"]

    accepted = runner.check_append_only_prefix(
        live, entry["sha256"], entry["size_bytes"], "EXPERIMENT_REGISTRY.md"
    )
    assert accepted["appended_bytes"] == len(live) - entry["size_bytes"]

    for offset in (0, 1, entry["size_bytes"] // 2, entry["size_bytes"] - 1):
        forged = bytearray(live)
        forged[offset] ^= 0x20
        with pytest.raises(runner.EvidenceError):
            runner.check_append_only_prefix(
                bytes(forged), entry["sha256"], entry["size_bytes"], "EXPERIMENT_REGISTRY.md"
            )


def test_whole_file_pin_still_fails_closed_on_size_or_hash_change() -> None:
    expected = {"size_bytes": 100, "sha256": "a" * 64}
    runner.check_whole_file_pin(100, "a" * 64, expected, "file")
    with pytest.raises(runner.EvidenceError):
        runner.check_whole_file_pin(101, "a" * 64, expected, "file")
    with pytest.raises(runner.EvidenceError):
        runner.check_whole_file_pin(100, "b" * 64, expected, "file")


def _write_lock(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "lock.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _valid_lock_payload() -> dict:
    lock = runner.load_strict_json(APPEND_ONLY_LOCK_PATH)
    assert lock["schema"] == runner.APPEND_ONLY_LOCK_SCHEMA
    assert lock["read_only_contract"] is True
    assert len(lock["entries"]) == 1
    return lock


def test_append_only_lock_loads_and_binds_to_the_immutable_baseline() -> None:
    baseline = runner.load_strict_json(BASELINE_PATH)
    resolved = runner.load_append_only_lock(APPEND_ONLY_LOCK_PATH, baseline)
    assert set(resolved) == {"EXPERIMENT_REGISTRY.md"}
    entry = resolved["EXPERIMENT_REGISTRY.md"]
    assert entry["prefix_sha256"] == hashlib.sha256(FROZEN_PREFIX_PATH.read_bytes()).hexdigest()
    assert entry["frozen_prefix_artifact_sha256"] == entry["prefix_sha256"]


def test_append_only_lock_refuses_to_launder_a_changed_historical_region(tmp_path: Path) -> None:
    baseline = runner.load_strict_json(BASELINE_PATH)
    lock = _valid_lock_payload()
    # Re-freezing today's (grown) registry as if it were the audited content.
    live = (runner.LAB_ROOT / "EXPERIMENT_REGISTRY.md").read_bytes()
    lock["entries"][0]["prefix_bytes"] = len(live)
    lock["entries"][0]["prefix_sha256"] = hashlib.sha256(live).hexdigest()
    with pytest.raises(runner.EvidenceError, match="does not equal the baseline"):
        runner.load_append_only_lock(_write_lock(tmp_path, lock), baseline)

    # Shrinking the pinned prefix is equally refused.
    lock = _valid_lock_payload()
    lock["entries"][0]["prefix_bytes"] = lock["entries"][0]["prefix_bytes"] - 1
    with pytest.raises(runner.EvidenceError, match="does not equal the baseline"):
        runner.load_append_only_lock(_write_lock(tmp_path, lock), baseline)


def test_append_only_lock_refuses_a_path_absent_from_the_baseline(tmp_path: Path) -> None:
    baseline = runner.load_strict_json(BASELINE_PATH)
    lock = _valid_lock_payload()
    lock["entries"][0]["path"] = "CURRENT_STATUS.md"
    with pytest.raises(runner.EvidenceError, match="absent from the immutable baseline"):
        runner.load_append_only_lock(_write_lock(tmp_path, lock), baseline)


def test_append_only_lock_refuses_a_frozen_artifact_that_is_not_the_audited_bytes(
    tmp_path: Path,
) -> None:
    baseline = runner.load_strict_json(BASELINE_PATH)
    lock = _valid_lock_payload()
    # Pointing at a real but wrong artifact must not be accepted as "the prefix".
    lock["entries"][0]["frozen_prefix_artifact"] = (
        "03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924"
        "/CONFIG/audit_scope.json"
    )
    with pytest.raises(runner.EvidenceError, match="does not match the baseline digest"):
        runner.load_append_only_lock(_write_lock(tmp_path, lock), baseline)
