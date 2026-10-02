"""Tests for the corrected re-derivation of the N-004 T03_runs cell.

Two jobs:

* lock the stored result, so a future run cannot quietly change the status of
  record; and
* re-derive the decisive facts cheaply from fresh streams, so the locked result
  is not taken on trust.

The central assertion is a negative one: with zero applicable seeds the cell
must be ``UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION`` and must never be
recorded as "calibrated", because the N-004 preregistration states that an
unresolved outcome must not be reported as agreement.
"""
from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
import pytest
from scipy import special

AREA = Path(__file__).resolve().parents[1]
LAB_ROOT = Path(__file__).resolve().parents[5]
ENGINE_ROOT = LAB_ROOT / "04_SHARED_ENGINE"
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))
sys.path.insert(0, str(AREA / "CODE"))

from engine.utilities.core import rng as lab_rng  # noqa: E402
from engine.validation import rng_battery as rb  # noqa: E402
import runs_sp800_22 as ref  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "t03_recal", AREA / "CODE" / "run_t03_recalibration.py"
)
assert _spec is not None and _spec.loader is not None
recal = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = recal
_spec.loader.exec_module(recal)

_spec2 = importlib.util.spec_from_file_location(
    "erfc_audit", AREA / "CODE" / "erfc_caller_audit.py"
)
assert _spec2 is not None and _spec2.loader is not None
audit = importlib.util.module_from_spec(_spec2)
sys.modules[_spec2.name] = audit
_spec2.loader.exec_module(audit)

PREREG = AREA / "CONFIG" / "prereg_T03_RECALIBRATION.json"
STORED = AREA / "RESULTS" / "T03_RECALIBRATION_20260928" / "recalibration.json"


@pytest.fixture(scope="module")
def stored() -> dict:
    return json.loads(STORED.read_text(encoding="utf-8"))


def stream(seed: int, shift: int) -> np.ndarray:
    gen = lab_rng(f"t03-recal-test-{shift}", seed)
    return np.unpackbits(
        gen.integers(0, 256, rb.NBYTES << shift, dtype=np.uint32).astype(np.uint8)
    )


# --------------------------------------------------------------------------- #
# the three variants are the same statistic under different conventions
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("shift", [0, 4])
def test_variants_are_evaluated_on_identical_streams(shift: int) -> None:
    bits = stream(11, shift)
    v = recal.variants_for(bits)
    assert v["as_implemented"] == float(rb.t_runs(bits))
    assert v["sqrt2_corrected"] == float(ref.runs_test_sp800_22(bits))
    gated = v["sqrt2_corrected_and_applicability_gated"]
    if v["applicable"]:
        assert gated == v["sqrt2_corrected"]
    else:
        assert gated is None


@pytest.mark.parametrize("shift", [0, 4])
def test_as_implemented_is_the_sqrt2_corrected_value_times_the_proven_factor(
    shift: int,
) -> None:
    # erfc(z/sqrt2) is never below erfc(z), so the defective variant is always the
    # more permissive of the two. This is a one-sided inequality, not a coincidence.
    for seed in range(1, 9):
        v = recal.variants_for(stream(seed, shift))
        assert v["as_implemented"] >= v["sqrt2_corrected"] - 1e-15


def test_the_sqrt2_is_the_only_difference_between_the_two_unconditional_variants() -> None:
    bits = stream(5, 0)
    n = int(bits.size)
    pi = float(bits.mean())
    num = abs(ref.runs_count(bits) - 2.0 * n * pi * (1.0 - pi))
    den = 2.0 * math.sqrt(2.0 * n) * pi * (1.0 - pi)
    v = recal.variants_for(bits)
    assert v["sqrt2_corrected"] == pytest.approx(special.erfc(num / den), rel=1e-12)
    assert v["as_implemented"] == pytest.approx(special.erfc(num / den / math.sqrt(2.0)), rel=1e-12)


# --------------------------------------------------------------------------- #
# the decision rule, applied literally
# --------------------------------------------------------------------------- #


def test_zero_applicable_seeds_yields_unresolved_never_calibrated() -> None:
    ks = {"scorable": True, "uniform_rejected": False}
    assert recal.decide(ks, applicable=0, seeds=200) == (
        "UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION"
    )
    # A uniform, uncorrected-looking result must still be unresolved while the
    # standard's precondition is unmet. This is the whole point.
    assert recal.decide(ks, 4, 200) == "UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION"
    assert recal.decide(ks, recal.APPLICABILITY_MIN_SEEDS, 200) == "CALIBRATED"


def test_decision_rule_thresholds_match_the_frozen_preregistration() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    rule = prereg["decision_rule"]
    assert "at least 5 of 200" in rule["CALIBRATED"]
    assert "fewer than 5 of 200" in rule["UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION"]
    assert recal.APPLICABILITY_MIN_SEEDS == 5
    assert "must not be reported as agreement" in (
        rule["UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION"]
    )


def test_unscorable_block_is_never_reported_as_agreement() -> None:
    block = recal.ks_block([None] * 5, "gated")
    assert block["scorable"] is False
    assert block["ks_pvalue"] is None
    assert recal.decide(block, applicable=0, seeds=200) == (
        "UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION"
    )


# --------------------------------------------------------------------------- #
# the stored result
# --------------------------------------------------------------------------- #


def test_stored_status_of_record_is_unresolved_at_both_lengths(stored: dict) -> None:
    assert [c["bit_length"] for c in stored["cells"]] == ["2^18", "2^22"]
    for c in stored["cells"]:
        assert c["status_of_record"] == "UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION"
        assert c["historical_n004_status"] == "calibrated"
        assert c["status_changed"] is True
        assert c["applicability"]["applicable_seeds"] == 0
        assert c["applicability"]["seeds_tested"] == 200


def test_stored_result_shows_the_sqrt2_explains_the_whole_non_uniformity(
    stored: dict,
) -> None:
    for c in stored["cells"]:
        by_name = {v["variant"]: v for v in c["variants"]}
        as_impl = by_name["as_implemented"]
        corrected = by_name["sqrt2_corrected"]
        assert as_impl["uniform_rejected"] is True, c["bit_length"]
        assert corrected["uniform_rejected"] is False, c["bit_length"]
        # and the corrected variant's mean sits near the uniform mean of 0.5
        assert corrected["mean_p"] == pytest.approx(0.5, abs=0.05)
        assert as_impl["mean_p"] > corrected["mean_p"] + 0.05
        gated = by_name["sqrt2_corrected_and_applicability_gated"]
        assert gated["n"] == 0
        assert gated["scorable"] is False


def test_stored_correction_states_23_of_24(stored: dict) -> None:
    text = stored["verdict"]["n004_per_test_claim_correction"]
    assert "23 of 24" in text
    assert "0 miscalibrated" in text
    assert "1 unresolvable" in text


def test_stored_result_refuses_every_forbidden_claim(stored: dict) -> None:
    forbidden = stored["verdict"]["must_not_claim"]
    assert any("certified" in f for f in forbidden)
    assert any("EXP-0004" in f for f in forbidden)
    assert any("G_LAB failed" in f for f in forbidden)
    assert any("non-detection" in f for f in forbidden)


# --------------------------------------------------------------------------- #
# the whole _erfc_p helper, not just the one caller
# --------------------------------------------------------------------------- #


def test_exactly_one_erfc_caller_passes_an_erfc_unit_argument() -> None:
    kinds = {tid: meta["argument_kind"] for tid, meta in audit.CALLERS.items()}
    erfc_units = [tid for tid, kind in kinds.items() if kind == "erfc_unit"]
    assert erfc_units == ["T03_runs"]
    assert sum(1 for k in kinds.values() if k == "z_score") == 4


def test_every_caller_declares_the_authority_for_its_classification() -> None:
    for tid, meta in audit.CALLERS.items():
        assert meta["authority"], tid
        assert meta["nist_section"], tid
        assert meta["argument"], tid
        assert meta["caller"], tid
        assert meta["argument_kind"] in ("z_score", "erfc_unit"), tid


def test_caller_audit_fails_closed_rather_than_passing_an_unmeasured_cell() -> None:
    # A cell with no scorable p-values must never read as a pass. This is the
    # fail-open defect class the laboratory has hit twice in production runners.
    empty = audit.ks_uniform(np.array([]))
    assert empty["ks_pvalue"] is None
    assert empty["uniform_rejected"] is None
    assert empty["n"] == 0

    # And a declared key that is never collected must raise, not silently score 0.
    original = dict(audit.CALLERS)
    try:
        audit.CALLERS["T99_bogus"] = {**original["T01_monobit"], "keys": ["T99_never_collected"]}
        with pytest.raises(audit.AuditError, match="never collected"):
            audit.analyze(2, 0, "caller-audit-failclosed")
    finally:
        audit.CALLERS.clear()
        audit.CALLERS.update(original)


def test_caller_keys_resolve_to_real_collected_columns() -> None:
    sample = audit.collect(1, 0, "caller-keys")
    for test_id, meta in audit.CALLERS.items():
        keys = meta.get("keys") or [k for k in sample if k == test_id or k.startswith(test_id)]
        assert keys, test_id
        for key in keys:
            assert key in sample, (test_id, key)


def test_autocorr_caller_pools_all_eight_lags() -> None:
    assert audit.CALLERS["T15_ac1..T15_ac8"]["keys"] == [f"T15_ac{i}" for i in range(1, 9)]
