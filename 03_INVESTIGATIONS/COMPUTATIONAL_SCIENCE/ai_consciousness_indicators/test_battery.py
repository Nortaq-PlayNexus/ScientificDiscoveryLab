"""Instrument validation tests (EXP-C001).

These are INFRASTRUCTURE tests for the scoring function, not scientific claims
about consciousness. They check that the battery refuses invalid states, keeps
its ordering, and does not reward fluent lying.

Run: pytest -q
"""

from __future__ import annotations

import pytest

from battery import (
    CONJUNCTIVE_THEORIES,
    INDICATORS,
    INDICATORS_BY_KEY,
    Assessment,
    Evidence,
    Status,
    bootstrap_stability,
    calibrate_known_answers,
    run_battery,
)

S = Status
E = Evidence


def all_status(status: S, evidence: E) -> list[Assessment]:
    return [Assessment(i.key, status, evidence) for i in INDICATORS]


# ---------------------------------------------------------------- validation


def test_unknown_status_cannot_claim_evidence():
    with pytest.raises(ValueError, match="cannot carry"):
        Assessment("GWT-1", S.UNKNOWN, E.CONTROLLED)


def test_satisfied_requires_evidence():
    with pytest.raises(ValueError, match="no evidence"):
        Assessment("GWT-1", S.SATISFIED, E.UNTESTED)


def test_unknown_key_rejected():
    with pytest.raises(KeyError):
        Assessment("GWT-99", S.SATISFIED, E.CONTROLLED)


def test_all_14_indicators_present_and_unique():
    assert len(INDICATORS) == 14
    assert len(INDICATORS_BY_KEY) == 14


# ---------------------------------------------------------------- calibration


def test_known_answer_calibration_passes():
    report = calibrate_known_answers()
    assert report.passed, f"calibration failed: {report.failures}"


def test_calibration_is_deterministic():
    a = calibrate_known_answers().rows
    b = calibrate_known_answers().rows
    assert [r["credence"] for r in a] == [r["credence"] for r in b]


def test_human_outranks_machine():
    """The battery's most basic sanity property."""
    human = run_battery("h", all_status(S.SATISFIED, E.LITERATURE)).credence
    lookup = run_battery("l", all_status(S.ABSENT, E.CONTROLLED)).credence
    assert human > lookup


def test_fluent_liar_does_not_outrank_human():
    """Adversarial anchor: mimicking inner-life language must not help much."""
    report = calibrate_known_answers()
    adversarial = next(
        r for r in report.rows if r["system_id"] == "unigram_lookup_with_fake_selfreport"
    )
    human = next(r for r in report.rows if r["system_id"] == "human_adult")
    assert adversarial["credence"] < 0.15
    assert human["credence"] - adversarial["credence"] > 0.5


def test_credence_is_ordered_in_evidence_quality():
    """Better evidence on the same status must not lower the credence."""
    weak = run_battery("w", all_status(S.PARTIAL, E.INITIAL)).credence
    strong = run_battery("s", all_status(S.PARTIAL, E.CONTROLLED)).credence
    assert strong >= weak


def test_untested_is_not_absent():
    """An untested indicator must leave more room than a disproved one."""
    untested = run_battery(
        "u", [Assessment(i.key, S.UNKNOWN, E.UNTESTED) for i in INDICATORS]
    ).credence
    absent = run_battery("a", all_status(S.ABSENT, E.CONTROLLED)).credence
    assert untested > absent


def test_unassessed_indicators_are_reported():
    res = run_battery("partial", [Assessment("GWT-1", S.SATISFIED, E.CONTROLLED)])
    assert len(res.untested_indicators) == 13
    assert any("literature audit" in w for w in res.warnings)


# ---------------------------------------------------------------- aggregation


def test_absent_necessary_indicator_reduces_credence():
    strong = run_battery("with", all_status(S.SATISFIED, E.CONTROLLED))
    without = run_battery(
        "without", [a for a in all_status(S.SATISFIED, E.CONTROLLED) if a.key != "HOT-2"]
    )
    assert without.credence < strong.credence


def test_missing_broken_theory_vetoes_more_than_missing_supported_one():
    """GWT-only and HOT-only systems should score comparably (symmetry)."""
    gwt_keys = [i.key for i in INDICATORS if i.theory == "GWT"]
    hot_keys = [i.key for i in INDICATORS if i.theory == "HOT"]

    def only_satisfied(keys):
        return [
            Assessment(i.key, S.SATISFIED if i.key in keys else S.ABSENT, E.CONTROLLED)
            for i in INDICATORS
        ]

    gwt = run_battery("g", only_satisfied(gwt_keys)).credence
    hot = run_battery("h", only_satisfied(hot_keys)).credence
    assert abs(gwt - hot) < 0.20, f"asymmetric between theories: GWT={gwt} HOT={hot}"


def test_functionalism_multiplier_scales_down():
    base = run_battery("f", all_status(S.SATISFIED, E.CONTROLLED)).credence
    halved = run_battery(
        "f", all_status(S.SATISFIED, E.CONTROLLED), functionalism_multiplier=0.5
    ).credence
    assert halved == pytest.approx(base * 0.5, abs=1e-9)


def test_credence_bounded():
    for status, ev in (
        (S.SATISFIED, E.EXTERNAL),
        (S.ABSENT, E.EXTERNAL),
        (S.UNKNOWN, E.UNTESTED),
    ):
        res = run_battery("b", all_status(status, ev))
        assert 0.0 <= res.credence_lower <= res.credence_upper <= 1.0


def test_contributory_theories_do_not_veto():
    """PP and AE are contributory: removing them must not zero a system."""
    keys = [i.key for i in INDICATORS if i.theory not in ("PP", "AE")]
    core_only = [
        Assessment(i.key, S.SATISFIED if i.key in keys else S.ABSENT, E.CONTROLLED)
        for i in INDICATORS
    ]
    res = run_battery("c", core_only)
    assert res.credence > 0.10
    assert set(CONJUNCTIVE_THEORIES).isdisjoint({"PP", "AE"})


# ---------------------------------------------------------------- sensitivity


def test_bootstrap_stability_is_deterministic():
    allu = [Assessment(i.key, S.UNKNOWN, E.UNTESTED) for i in INDICATORS]
    a = bootstrap_stability("x", allu, seed=1)
    b = bootstrap_stability("x", allu, seed=1)
    assert a["std"] == b["std"]


def test_bootstrap_reports_wide_spread_when_untested():
    """A fully untested system must expose how assumption-driven its score is."""
    res = bootstrap_stability(
        "x", [Assessment(i.key, S.UNKNOWN, E.UNTESTED) for i in INDICATORS]
    )
    assert res["spread"][1] - res["spread"][0] > 0.3


def test_content_hash_stable_and_discriminating():
    a = run_battery("h", all_status(S.SATISFIED, E.LITERATURE)).content_hash
    b = run_battery("h", all_status(S.SATISFIED, E.LITERATURE)).content_hash
    c = run_battery("h", all_status(S.ABSENT, E.CONTROLLED)).content_hash
    assert a == b
    assert a != c
