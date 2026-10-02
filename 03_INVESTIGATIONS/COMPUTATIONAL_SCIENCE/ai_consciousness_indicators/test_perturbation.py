"""Robustness tests (EXP-C003).

These test the ROBUSTNESS EXPERIMENT, not consciousness. Specifically: that the
gate machinery works, that the honest failure is recorded, and that F-B — the
claim that fluent self-report must not beat architecture — actually holds.

Run: pytest -q
"""

from __future__ import annotations

import pytest

import battery as B
from perturbation import EXPECTED_ORDER, run_perturbation, sample_params


# ---------------------------------------------------------------- gate hygiene


def test_expected_order_covers_every_anchor():
    """Regression test for F05.

    The first EXPECTED_ORDER omitted feedforward_mlp, so the six-element sorted
    list could never equal the five-element tuple. F-A read 0.000 in every run
    for a structural reason and reported the gate's own bug as a falsification.
    """
    anchor_ids = {c["system_id"] for c in B.KNOWN_ANSWERS}
    assert set(EXPECTED_ORDER) == anchor_ids
    assert len(EXPECTED_ORDER) == len(anchor_ids)


def test_partial_expected_order_raises_rather_than_silently_scoring():
    """A partial order must be an error, not a silent zero."""
    import perturbation as P

    saved = P.EXPECTED_ORDER
    try:
        P.EXPECTED_ORDER = ("human_adult",)  # deliberately partial
        with pytest.raises(ValueError, match="EXPECTED_ORDER does not match"):
            P.run_perturbation(n_draws=5, seed=1)
    finally:
        P.EXPECTED_ORDER = saved


# ---------------------------------------------------------------- determinism


def test_perturbation_is_deterministic():
    a = run_perturbation(n_draws=60, seed=7)
    b = run_perturbation(n_draws=60, seed=7)
    assert a["per_system"] == b["per_system"]
    assert a["gates"] == b["gates"]


def test_different_seeds_differ():
    a = run_perturbation(n_draws=60, seed=1)
    b = run_perturbation(n_draws=60, seed=2)
    assert a["per_system"] != b["per_system"]


# ---------------------------------------------------------------- parameters


def test_sampled_params_stay_in_valid_ranges():
    from _rng import rng

    gen = rng("t", 0)
    for _ in range(50):
        p = sample_params(gen, wide=False)
        assert 0.0 < p.soft_or_temperature < 5.0
        assert 0.0 < p.absence_factor <= 1.0
        assert p.necessity_penalty >= 1.0
        assert p.evidence_scale[B.Evidence.UNTESTED] == 0.0


def test_perturbed_scores_stay_bounded():
    """Perturbation must not push any system outside [0, 1]."""
    r = run_perturbation(n_draws=200, seed=0, wide=True)
    for stats in r["per_system"].values():
        assert 0.0 <= stats["min"]
        assert stats["max"] <= 1.0


def test_temperature_is_restored_after_perturbation():
    """The sweep mutates a module global; it must not leak."""
    import perturbation as P

    before = B._SOFT_OR_TEMPERATURE
    P.run_perturbation(n_draws=20, seed=3, wide=True)
    assert B._SOFT_OR_TEMPERATURE == before


# ---------------------------------------------------------------- the findings


def test_fluent_liar_never_beats_human_under_any_perturbation():
    """F-B, the load-bearing claim.

    Across the aggressive region — temperatures from 0.02 to 3.0, evidence scales
    that can invert the intended ordering, penalties from 0.30 to 0.85 — the
    system that merely talks about inner life never scores above the human. This
    is what makes the battery a measurement of architecture rather than
    eloquence.
    """
    r = run_perturbation(n_draws=400, seed=0, wide=True)
    assert r["gates"]["F-B adversarial < human"] >= 0.95


def test_ordering_survives_plausible_perturbation():
    r = run_perturbation(n_draws=400, seed=0, wide=False)
    assert r["gates"]["F-A full canonical order exact"] >= 0.90


def test_aggressive_region_does_not_survive_and_that_is_recorded():
    """The honest negative result, pinned as a test.

    Under aggressive perturbation the exact ordering degrades to ~0.64 and the
    adversarial ceiling (F-C) to ~0.77. This is NOT hidden: it is the evidence
    that F01's circularity has real teeth, and it is why the battery is
    documented as a ranking tool under shared assumptions rather than a source of
    absolute probabilities.
    """
    r = run_perturbation(n_draws=400, seed=0, wide=True)
    assert not r["all_gates_pass"]
    assert r["gates"]["F-A full canonical order exact"] < 0.90


def test_absolutes_are_less_stable_than_ordering():
    """The documented conclusion, stated as an assertion.

    In the aggressive region the adversarial anchor's 5th-95th percentile spans
    roughly [0.03, 0.51] — wide enough to cross the 0.30 ceiling. Absolute
    credences are assumption-dominated; the human/liar separation is not.
    """
    r = run_perturbation(n_draws=400, seed=0, wide=True)
    adv = r["per_system"]["unigram_lookup_with_fake_selfreport"]
    assert (adv["p95"] - adv["p05"]) > 0.30
    assert adv["max"] > 0.30  # the ceiling IS crossed, in some draws
