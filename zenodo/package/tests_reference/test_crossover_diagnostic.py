"""Tests for the N-001 finite-size crossover diagnostic.

The decisive assertions are about honesty rather than about a number:

* the independent estimator must reproduce the stored production tau exactly, so
  nothing downstream rests on a reimplementation that merely looks similar;
* the decision must be taken by the preregistered rule, not by whichever way the
  numbers came out;
* a slope indistinguishable from zero must never be turned into a confident
  statement about how large a system would be needed; and
* the N-001 production decision must be untouched.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
import pytest

AREA = Path(__file__).resolve().parents[1]
LAB_ROOT = Path(__file__).resolve().parents[6]

_spec = importlib.util.spec_from_file_location(
    "crossover", AREA / "CODE" / "run_crossover_diagnostic.py"
)
assert _spec is not None and _spec.loader is not None
diag = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = diag
_spec.loader.exec_module(diag)

PREREG = AREA / "CONFIG" / "prereg_N001_CROSSOVER.json"
STORED = AREA / "RESULTS" / "CROSSOVER_20260928" / "crossover.json"
PRODUCTION_SUMMARY = (
    LAB_ROOT
    / "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001"
    / "RESULTS/PRODUCTION_N001_20260926/N001_production_summary.json"
)


@pytest.fixture(scope="module")
def stored() -> dict:
    return json.loads(STORED.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# the reproduction control
# --------------------------------------------------------------------------- #


def test_independent_estimator_reproduces_the_stored_production_tau_exactly() -> None:
    control = diag.reproduction_control()
    assert control["reproduces_stored_value"] is True
    assert control["abs_delta"] == 0.0
    assert control["this_implementation_tau"] == control["stored_production_tau"]


def test_reproduction_control_explains_the_pooling_scope() -> None:
    control = diag.reproduction_control()
    stored = json.loads(PRODUCTION_SUMMARY.read_text(encoding="utf-8-sig"))
    active = stored["active_tau_L"]
    assert control["active_tau_L"] == active == 1024
    # The status line's "1,462,967 pooled tail clusters" is the active size only.
    assert control["active_L_tail_clusters"] == 1462967
    assert control["pooling_scope_shift"] < 0.0
    assert "re-implemented from its written specification" in control["note"]


def test_every_stored_window_also_reproduces() -> None:
    curvature = diag.window_curvature(diag.load_tails("canonical"))
    assert curvature["all_windows_reproduce_stored"] is True
    assert len(curvature["rows"]) == 4


def test_stored_raw_database_is_unmodified_and_digest_guarded() -> None:
    guard = diag.stored_digest_guard()
    assert guard["raw_unmodified"] is True
    assert guard["raw_sha256"] == guard["manifest_recorded_sha256"]
    # The stale manifest label is recorded, not silently corrected.
    assert "iid_cluster_bootstrap" in str(guard["manifest_pairing_label"])
    assert "stale text" in guard["manifest_pairing_label_note"]


# --------------------------------------------------------------------------- #
# the estimator itself
# --------------------------------------------------------------------------- #


def _synthetic_power_law(tau: float, lo: int, hi: int, amplitude: float) -> np.ndarray:
    """A pool whose per-size counts follow n_s proportional to s**-tau exactly."""
    sizes = np.arange(lo, hi + 1, dtype=np.int64)
    counts = np.floor(amplitude * sizes.astype(float) ** (-tau)).astype(np.int64)
    keep = counts > 0
    return np.repeat(sizes[keep], counts[keep])


def test_cumulative_estimator_is_biased_upward_on_a_known_power_law() -> None:
    # This test originally asserted the cumulative estimator recovers a known
    # exponent. It does not, and discovering that is the point of
    # test_tau_estimator_validation.py. The bias is upward and window-dependent,
    # so the assertion is now the measured behaviour, not the hoped-for one.
    pool = _synthetic_power_law(2.05, 32, 4096, 3.0e8)
    fit = diag.fit_tau([pool], "cumulative", 32, 4096)
    assert fit is not None
    assert fit["tau"] > 2.05 + 0.05
    # the cumulative definition is tau = 1 - survival slope, and that identity
    # holds exactly even though the value it returns is biased
    assert fit["tau"] == pytest.approx(1.0 - fit["slope"])


def test_histogram_estimator_recovers_a_known_power_law_exponent() -> None:
    # The histogram estimator is the unbiased anchor of the whole investigation.
    pool = _synthetic_power_law(2.05, 32, 4096, 3.0e8)
    fit = diag.fit_tau([pool], "histogram", 32, 4096)
    assert fit is not None
    assert fit["tau"] == pytest.approx(2.05, abs=0.01)


def test_the_two_estimators_disagree_on_an_exact_power_law_too() -> None:
    # The disagreement on real percolation data is therefore NOT purely a
    # curvature signal: a known pure power law already separates them.
    pool = _synthetic_power_law(2.05, 32, 4096, 3.0e8)
    cum = diag.fit_tau([pool], "cumulative", 32, 4096)
    hist = diag.fit_tau([pool], "histogram", 32, 4096)
    assert cum is not None and hist is not None
    assert abs(cum["tau"] - hist["tau"]) > 0.05


def test_fit_tau_rejects_a_non_positive_tail() -> None:
    with pytest.raises(diag.DiagnosticError):
        diag.fit_tau([np.array([1, 0, 5], dtype=np.int64)], "cumulative", 1, 10)


def test_fit_tau_returns_none_when_a_size_is_not_scorable() -> None:
    tiny = [np.array([1000], dtype=np.int64)]
    assert diag.fit_tau(tiny, "cumulative", 32, 4096) is None


def test_weighted_fit_requires_three_aligned_points() -> None:
    with pytest.raises(diag.DiagnosticError):
        diag.weighted_loglog_fit(np.zeros(2), np.zeros(2), np.ones(2), 1.0)


# --------------------------------------------------------------------------- #
# the preregistered decision
# --------------------------------------------------------------------------- #


def test_stored_decision_is_crossover_not_established(stored: dict) -> None:
    assert stored["decision"]["status"] == "CROSSOVER_NOT_ESTABLISHED"
    assert stored["decision"]["preregistered_order_satisfied"] is False


def test_the_preregistered_monotonic_order_is_genuinely_violated(stored: dict) -> None:
    trend = stored["l_trend"]
    assert trend["status"] == "COMPUTED"
    assert trend["monotonic_increasing"] is False
    assert trend["tau"][1] < trend["tau"][0], "tau must dip at L=512 to violate the order"
    assert trend["excludes_zero_increasing_direction"] is False
    assert trend["slope_ci95"][0] < 0.0 < trend["slope_ci95"][1]


def test_the_deviation_is_nearly_size_independent(stored: dict) -> None:
    # This is the signature that matters: a roughly constant offset is not the
    # shrinking offset that finite-size crossover would produce.
    devs = stored["l_trend"]["deviation_from_fisher"]
    assert len(devs) == 3
    assert all(d < 0.0 for d in devs)
    assert (max(devs) - min(devs)) < 0.05
    assert all(abs(d + 0.15) < 0.03 for d in devs)


def test_a_null_slope_never_yields_a_meaningful_extrapolated_size(stored: dict) -> None:
    trend = stored["l_trend"]
    assert trend["extrapolation_is_meaningful"] is False
    assert trend["crossing_beyond_1024_is_meaningful"] is False
    assert "must not be quoted as a required system size" in trend["extrapolation_caveat"]
    assert "NOT ESTABLISHED is not the same as excluded" in trend["power_caveat"]


def test_curvature_is_reported_independently_of_the_l_trend(stored: dict) -> None:
    assert stored["decision"]["curvature_present"] is True
    curvature = stored["window_curvature"]
    assert curvature["cumulative_spread"] > 0.0
    assert curvature["max_estimator_disagreement"] > 0.0
    # The histogram estimate falls steeply as the window extends upward.
    hist = [r["histogram_tau"] for r in curvature["rows"]]
    assert hist[-1] < hist[0]


def test_paired_threshold_check_shows_the_refinement_is_not_the_cause(stored: dict) -> None:
    paired = stored["paired_threshold_check"]
    assert len(paired["rows"]) == 3
    assert paired["max_abs_delta"] < 0.002
    assert "paired, not independent" in paired["note"]


# --------------------------------------------------------------------------- #
# integrity of the claim boundary
# --------------------------------------------------------------------------- #


def test_preregistration_declares_its_own_informedness(stored: dict) -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    disclosure = prereg["disclosure_of_prior_knowledge"]
    assert "INFORMED" in disclosure
    assert "NOT DISCLOSED-FREE" in disclosure
    assert "had NOT been seen" in disclosure
    assert stored["disclosure"] == disclosure


def test_preregistration_freezes_the_directional_prediction_from_theory() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    assert "tau(256) < tau(512) < tau(1024)" in prereg["primary_prediction"]
    assert "derived from finite-size theory" in prereg["disclosure_of_prior_knowledge"]


def test_decision_rule_cannot_report_a_null_slope_as_agreement() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    rule = prereg["decision_rule"]
    assert "CROSSOVER_NOT_ESTABLISHED" in rule
    assert "includes zero" in rule["CROSSOVER_NOT_ESTABLISHED"]
    # the guard against calling a null slope agreement lives in claim_guards
    assert "false positive" in " ".join(prereg["claim_guards"])
    assert "it is a real result" in prereg["falsification"]


def test_bootstrap_uses_realization_blocks_not_clusters(stored: dict) -> None:
    # One realization per block: the interval must come from realization counts,
    # so a cell with few realizations must report few accepted draws relative to
    # its realization count, never millions of pseudo-independent clusters.
    for cell in stored["per_size_canonical"]["cells"]:
        if not cell.get("scorable"):
            continue
        boot = cell.get("bootstrap")
        if boot is None:
            continue
        assert boot["block"] == "realization"
        assert boot["draws_requested"] == diag.BOOTSTRAP_DRAWS
        assert cell["realizations"] in (50, 100)


def test_production_decision_is_not_edited(stored: dict) -> None:
    stored_summary = json.loads(PRODUCTION_SUMMARY.read_text(encoding="utf-8-sig"))
    assert stored_summary["scientific_result"] is None
    assert stored_summary["status"] == "PRODUCTION_REQUIRES_SEPARATE_SCIENTIFIC_REVIEW"
    guards = " ".join(stored["claim_guards"])
    assert "is not edited, reversed, or softened" in guards
    assert "does not resolve Q-P007" in guards
    assert "No new physics is claimed" in guards
