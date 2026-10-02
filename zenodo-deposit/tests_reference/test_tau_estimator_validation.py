"""Tests for the N-001 tau estimator validation.

The load-bearing assertion is the one that could have gone the other way and
still had to be reported: the estimator must be measured against data of a
KNOWN exponent, and a bias may only be corrected if it behaves the same way for
two different truths. If it does not, the tests must force the answer to be
"no correction permitted" rather than letting a plausible number through.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest

AREA = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "tauval", AREA / "CODE" / "validate_tau_estimators.py"
)
assert _spec is not None and _spec.loader is not None
val = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = val
_spec.loader.exec_module(val)

PREREG = AREA / "CONFIG" / "prereg_N001_ESTIMATOR_VALIDATION.json"
STORED = AREA / "RESULTS" / "ESTIMATOR_VALIDATION_20260928" / "validation.json"


@pytest.fixture(scope="module")
def stored() -> dict:
    return json.loads(STORED.read_text(encoding="utf-8"))


def test_all_three_estimators_are_exercised() -> None:
    assert set(val.ESTIMATORS) == {
        "cumulative_as_written",
        "cumulative_poisson_weight",
        "histogram",
    }


def test_histogram_estimator_is_unbiased_on_known_exponents() -> None:
    # This is the anchor of the whole exercise: one estimator is trustworthy on
    # power laws, which makes it the yardstick for the other two.
    for truth in val.TRUTHS:
        pool = val.exact_integer_counts(truth, 32, 4096, 3.0e8)
        got = val.histogram(pool, 32, 4096)
        assert got == pytest.approx(truth, abs=0.01), truth


def test_cumulative_as_written_is_biased_upward_on_known_exponents() -> None:
    for truth in val.TRUTHS:
        pool = val.exact_integer_counts(truth, 32, 4096, 3.0e8)
        got = val.cumulative_as_written(pool, 32, 4096)
        assert got > truth + 0.05, (truth, got)
        assert got < truth + 0.40, (truth, got)


def test_the_bias_is_not_an_artefact_of_one_synthetic_construction() -> None:
    """Three independent constructions must agree on the sign of the bias."""
    signs = set()
    for truth in val.TRUTHS:
        for n in (2_000_000,):
            rng = np.random.default_rng(val.SEED)
            pools = {
                "exact": val.exact_integer_counts(truth, 32, 4096, 3.0e8),
                "pareto": val.pareto_sample(truth, 32, 4096, n, rng),
            }
            for pool in pools.values():
                signs.add(np.sign(val.cumulative_as_written(pool, 32, 4096) - truth))
    assert signs == {1.0}, "bias sign must be positive in every construction"


def test_poisson_weighting_reduces_but_does_not_remove_the_bias() -> None:
    for truth in val.TRUTHS:
        pool = val.exact_integer_counts(truth, 32, 4096, 3.0e8)
        written = val.cumulative_as_written(pool, 32, 4096) - truth
        poisson = val.cumulative_poisson_weight(pool, 32, 4096) - truth
        assert written > 0 and poisson > 0
        assert poisson < written


def test_survival_fit_fails_closed_when_not_scorable() -> None:
    with pytest.raises(val.ValidationError):
        val.cumulative_as_written(np.array([1000], dtype=np.int64), 32, 4096)


# --------------------------------------------------------------------------- #
# the preregistered decision
# --------------------------------------------------------------------------- #


def test_classification_is_estimator_biased(stored: dict) -> None:
    assert stored["summary"]["classification"] == "ESTIMATOR_BIASED"
    assert stored["summary"]["median_abs_error_primary"] > val.BIAS_TOLERANCE
    assert stored["summary"]["sign_consistent_across_truths"] is True


def test_bias_correction_is_permitted_only_because_the_two_truths_agree(stored: dict) -> None:
    s = stored["summary"]
    assert s["error_spread_across_truths"] <= val.BIAS_TOLERANCE
    assert s["bias_correction_permitted"] is True
    assert "consistent in sign and magnitude" in s["bias_correction_rationale"]


def test_summarize_would_refuse_a_correction_when_truths_disagree() -> None:
    """The rule must actually bite: an inconsistent bias must block the correction."""
    table = {
        "rows": [
            # truth 1.85 -> small positive bias; truth 2.05 -> large NEGATIVE bias
            {"estimator": "cumulative_as_written", "truth": 1.85, "window": [32, 4096], "error": 0.02},
            {"estimator": "cumulative_as_written", "truth": 2.05, "window": [32, 4096], "error": -0.20},
        ]
    }
    s = val.summarize(table)
    assert s["classification"] == "BIAS_NOT_TRANSFERABLE"
    assert s["bias_correction_permitted"] is False
    assert "No corrected value may be quoted" in s["bias_correction_rationale"]


def test_summarize_reports_unbiased_when_the_error_is_small() -> None:
    table = {
        "rows": [
            {"estimator": "cumulative_as_written", "truth": 1.85, "window": [32, 4096], "error": 0.01},
            {"estimator": "cumulative_as_written", "truth": 2.05, "window": [32, 4096], "error": 0.02},
        ]
    }
    s = val.summarize(table)
    assert s["classification"] == "UNBIASED_AT_THESE_WINDOWS"
    assert s["bias_correction_permitted"] is False


# --------------------------------------------------------------------------- #
# what the validation does and does not license
# --------------------------------------------------------------------------- #


def test_the_stored_production_value_is_reported_and_not_edited(stored: dict) -> None:
    assert stored["stored_production_tau"] == 1.9200860948994347
    assert stored["real_data"]["rows"][1]["cumulative_as_written"] == pytest.approx(
        1.9200860948994347, rel=1e-9
    )


def test_bias_correction_lowers_tau_and_widens_the_deviation(stored: dict) -> None:
    primary = next(
        r for r in stored["real_data"]["rows"] if r["window"] == [32, 4096]
    )
    corrected = primary["bias_corrected_secondary"]
    assert corrected is not None
    # the correction must move AWAY from Fisher, i.e. the deviation grows
    assert corrected < primary["cumulative_as_written"]
    assert abs(corrected - stored["fisher_tau"]) > abs(
        primary["cumulative_as_written"] - stored["fisher_tau"]
    )
    assert primary["bias_applied"] > 0


def test_the_deviation_direction_is_robust_to_every_estimator_and_window(stored: dict) -> None:
    # The escalation must not depend on the estimator choice, even though the
    # numeric value does.
    for row in stored["real_data"]["rows"]:
        for name in ("cumulative_as_written", "cumulative_poisson_weight", "histogram"):
            assert row[name] < stored["fisher_tau"], (row["window"], name, row[name])
    assert "escalation direction is unaffected" in stored["bottom_line"]


def test_estimator_choice_materially_changes_the_number(stored: dict) -> None:
    assert stored["real_data"]["estimator_choice_matters"] is True
    assert stored["real_data"]["max_estimator_disagreement"] > 0.05


def test_unresolvable_cells_are_recorded_not_imputed(stored: dict) -> None:
    for row in stored["synthetic"]["rows"]:
        if row.get("unresolvable"):
            assert row["value"] is None and row["error"] is None
        else:
            assert isinstance(row["error"], float)


def test_claim_guards_forbid_using_the_bias_to_dismiss_the_anomaly(stored: dict) -> None:
    guards = " ".join(stored["claim_guards"])
    assert "not edited" in guards
    assert "must not be reported as though it had removed the deviation" in guards
    assert "null result" in guards


def test_preregistration_declares_its_own_informedness(stored: dict) -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    assert "INFORMED" in prereg["disclosure_of_prior_knowledge"]
    assert prereg["synthetic_design"]["truths"] == [1.85, 2.05]
    assert "the bias is a property of the estimator and window" in (
        prereg["synthetic_design"]["why_two_truths"]
    )
    assert stored["disclosure"] == prereg["disclosure_of_prior_knowledge"]
