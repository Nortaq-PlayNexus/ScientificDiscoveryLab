"""Tests for the calibration gate and the validation paths (EXP-C001).

Separate from `test_battery.py` because these tests deliberately break the
instrument's own invariants. They are the tests that would have caught F08 and
F09 at the moment those defects were introduced.
"""

from __future__ import annotations

import pytest

import battery as B
from battery import (
    Assessment,
    CalibrationNotEstablished,
    Evidence,
    Status,
    calibration_state,
    run_battery,
)

S = Status
E = Evidence


# ---------------------------------------------------------------- F08


def test_calibration_passed_is_computed_not_asserted():
    """Regression test for F08.

    `BatteryResult.calibration_passed` was previously assigned
    `not require_calibration or True`, which is unconditionally True. A status
    field that cannot report failure hands out false assurance: any caller
    checking it would conclude the battery was calibrated no matter what.

    It is now derived from `calibration_state()["passed"]`, which either runs the
    anchors or returns None during reentrant entry.
    """
    state = calibration_state()
    assert state["passed"] is True, state["failures"]
    assert set(state["rows"]) == {c["system_id"] for c in B.KNOWN_ANSWERS}

    res = run_battery("g", [Assessment(i.key, S.SATISFIED, E.LITERATURE) for i in B.INDICATORS])
    assert res.calibration_passed is True
    assert res.calibration_checked is True


def test_gate_raises_when_calibration_has_not_passed(monkeypatch):
    """The gate must actually close when calibration fails.

    Simulates a failing calibration by injecting a failing state, then asserts
    that `run_battery` refuses rather than returning a number that looks
    calibrated.
    """
    monkeypatch.setattr(
        B,
        "_CALIBRATION_CACHE",
        {"passed": False, "failures": ["injected failure"], "rows": {}},
    )
    with pytest.raises(CalibrationNotEstablished, match="calibration has not passed"):
        run_battery(
            "gated",
            [Assessment(i.key, S.SATISFIED, E.LITERATURE) for i in B.INDICATORS],
            require_calibration=True,
        )


def test_uncalibrated_diagnostic_is_available_explicitly(monkeypatch):
    """`require_calibration=False` must still work, and say so."""
    monkeypatch.setattr(
        B,
        "_CALIBRATION_CACHE",
        {"passed": False, "failures": ["injected failure"], "rows": {}},
    )
    res = run_battery(
        "diag",
        [Assessment(i.key, S.SATISFIED, E.LITERATURE) for i in B.INDICATORS],
        require_calibration=False,
    )
    assert res.calibration_passed is False
    assert res.calibration_checked is False
    assert 0.0 <= res.credence <= 1.0


def test_reentrant_calibration_reports_not_yet_established(monkeypatch):
    """Never claim `passed` while the anchors are themselves being scored.

    `calibrate_known_answers` scores anchors by calling `run_battery`, which
    wants the calibration state. Returning `True` during that window would be a
    lie that also happens to be self-justifying.
    """
    monkeypatch.setattr(B, "_CALIBRATION_IN_PROGRESS", True)
    monkeypatch.setattr(B, "_CALIBRATION_CACHE", None)
    state = calibration_state()
    assert state["passed"] is None
    assert state["failures"]


# ---------------------------------------------------------------- F09


def test_duplicate_indicator_keys_are_rejected():
    """Regression test for F09.

    The duplicate check was `len(list(by_key.values())) != len(set(by_key))`,
    where `by_key` is a dict keyed on indicator key. A dict cannot contain
    duplicate keys, so both sides were always equal and the check could never
    fire — silently accepting contradictory assessments.
    """
    duplicate = [
        Assessment("GWT-1", S.SATISFIED, E.CONTROLLED, "first"),
        Assessment("GWT-1", S.ABSENT, E.CONTROLLED, "second"),
    ]
    with pytest.raises(ValueError, match="duplicate indicator key"):
        run_battery("dup", duplicate, require_calibration=False)


def test_conflicting_duplicate_is_not_silently_resolved():
    """The two assertions genuinely contradict; last-wins would hide that."""
    with pytest.raises(ValueError):
        run_battery(
            "dup",
            [
                Assessment("HOT-2", S.SATISFIED, E.EXTERNAL),
                Assessment("HOT-2", S.ABSENT, E.EXTERNAL),
            ],
            require_calibration=False,
        )


def test_repeated_identical_key_still_rejected():
    """Even non-contradictory duplicates are ambiguous and must be caught."""
    with pytest.raises(ValueError, match="duplicate indicator key"):
        run_battery(
            "dup",
            [
                Assessment("RPT-1", S.SATISFIED, E.CONTROLLED),
                Assessment("RPT-1", S.SATISFIED, E.CONTROLLED),
            ],
            require_calibration=False,
        )


# ---------------------------------------------------------------- perturbation P4


def test_conscious_rate_shift_actually_perturbs():
    """Regression test for F10.

    `score_under_params` computed `conscious_rate` from the P4 shift and never
    used it, so one of the six advertised perturbation families did nothing.
    A credible-sounding robustness claim was resting on 5 real parameters.
    """
    from perturbation import PerturbedParams, sample_params, score_under_params
    from _rng import rng

    assessments = [Assessment(i.key, S.SATISFIED, E.CONTROLLED) for i in B.INDICATORS]

    gen = rng("t", 0)
    base = sample_params(gen, wide=False)

    zero_shift = PerturbedParams(
        soft_or_temperature=base.soft_or_temperature,
        evidence_scale=base.evidence_scale,
        base_rate_shift=base.base_rate_shift,
        conscious_rate_shift={k: 0.0 for k in base.conscious_rate_shift},
        absence_factor=base.absence_factor,
        necessity_penalty=base.necessity_penalty,
    )
    big_shift = PerturbedParams(
        soft_or_temperature=base.soft_or_temperature,
        evidence_scale=base.evidence_scale,
        base_rate_shift=base.base_rate_shift,
        conscious_rate_shift={k: -0.5 for k in base.conscious_rate_shift},
        absence_factor=base.absence_factor,
        necessity_penalty=base.necessity_penalty,
    )

    a = score_under_params(assessments, zero_shift)
    b = score_under_params(assessments, big_shift)
    assert a != b, "P4 conscious_rate_shift has no effect — it is inert"


def test_all_six_perturbation_families_reach_the_score():
    """Every sampled family must be able to move the output.

    Uses a partial assessment with several ABSENT indicators. An all-SATISFIED
    system saturates at credence 1.0 regardless of temperature, so a temperature
    perturbation would be invisible there — the family would look inert when it is
    merely saturated. Absence of movement at saturation is not absence of effect.
    """
    from perturbation import PerturbedParams, sample_params, score_under_params
    from _rng import rng

    partial = {
        "GWT-1": S.SATISFIED, "GWT-2": S.SATISFIED, "GWT-3": S.PARTIAL,
        "GWT-4": S.PARTIAL, "RPT-1": S.SATISFIED, "RPT-2": S.PARTIAL,
        "HOT-1": S.SATISFIED, "HOT-2": S.PARTIAL, "HOT-3": S.SATISFIED,
        "HOT-4": S.PARTIAL, "AST-1": S.ABSENT, "PP-1": S.PARTIAL,
        "AE-1": S.PARTIAL, "AE-2": S.ABSENT,
    }
    assessments = [
        Assessment(k, v, E.CONTROLLED) for k, v in partial.items()
    ]

    gen = rng("t", 1)
    p = sample_params(gen, wide=False)

    def score(**over):
        return score_under_params(assessments, PerturbedParams(**{**p.__dict__, **over}))

    baseline = score()
    assert 0.0 < baseline < 1.0, f"test needs a non-saturated system, got {baseline}"

    # Each family is tried in BOTH directions and must move the score in at least
    # one. Testing a single direction would produce false reports of inertness:
    # the combiner is monotone, so near a boundary a family can move the result
    # downward while clamping flat upward. Inertness means "cannot move it either
    # way", which is the property F10 actually violated.
    families = {
        "P1 soft_or_temperature": [
            dict(soft_or_temperature=p.soft_or_temperature * 2.5),
            dict(soft_or_temperature=p.soft_or_temperature / 4.0),
        ],
        "P2 evidence_scale": [
            dict(evidence_scale={k: v * 0.5 for k, v in p.evidence_scale.items()}),
            dict(evidence_scale={k: min(1.5, v * 1.4) for k, v in p.evidence_scale.items()}),
        ],
        "P3 base_rate_shift": [
            dict(base_rate_shift={k: v + 0.30 for k, v in p.base_rate_shift.items()}),
            dict(base_rate_shift={k: v - 0.30 for k, v in p.base_rate_shift.items()}),
        ],
        "P4 conscious_rate_shift": [
            dict(conscious_rate_shift={k: v - 0.40 for k, v in p.conscious_rate_shift.items()}),
            dict(conscious_rate_shift={k: v + 0.20 for k, v in p.conscious_rate_shift.items()}),
        ],
        "P5 absence_factor": [
            dict(absence_factor=0.85),
            dict(absence_factor=0.32),
        ],
        "P6 necessity_penalty": [
            dict(necessity_penalty=p.necessity_penalty + 0.8),
            dict(necessity_penalty=max(1.0, p.necessity_penalty - 0.5)),
        ],
    }

    inert = [
        name
        for name, variants in families.items()
        if all(score(**v) == baseline for v in variants)
    ]
    assert not inert, (
        f"perturbation families with no effect in either direction: {inert}. "
        "A family that cannot move the score is not a robustness check."
    )
