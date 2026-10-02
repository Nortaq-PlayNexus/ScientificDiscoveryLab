"""Conformance and regression tests for the T03_runs estimator audit.

These lock the *exact* relationship between the shared battery's estimator and
NIST SP 800-22 Rev. 1a section 2.3, so the defect cannot silently change shape,
and they assert the properties that made the audit's attribution legitimate in
the first place: a single, algebraic, one-parameter difference.
"""
from __future__ import annotations

import hashlib
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

from engine.validation import rng_battery as rb  # noqa: E402
import runs_sp800_22 as ref  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "t03_audit_runner", AREA / "CODE" / "run_t03_formula_audit.py"
)
assert _spec is not None and _spec.loader is not None
runner = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = runner
_spec.loader.exec_module(runner)

PREREG = AREA / "CONFIG" / "prereg_T03_FORMULA_AUDIT.json"
N004_DB = (
    LAB_ROOT
    / "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION"
    / "RESULTS/N004_production_20260926_V3/N004_raw.sqlite3"
)


def stream(seed: int, shift: int = 0) -> np.ndarray:
    return runner.glab_bits("t03-formula-test", seed, shift)


# --------------------------------------------------------------------------- #
# 1. the reference implementation is a faithful transcription of the standard
# --------------------------------------------------------------------------- #


def test_runs_count_counts_transitions_plus_one():
    bits = np.array([1, 0, 0, 1, 1, 0, 1, 0, 1, 1], dtype=np.uint8)
    # six adjacent pairs differ, so V_obs = 6 + 1 = 7
    assert ref.runs_count(bits) == 7


def test_runs_count_rejects_degenerate_input():
    with pytest.raises(ValueError):
        ref.runs_count(np.array([1], dtype=np.uint8))
    with pytest.raises(ValueError):
        ref.runs_count(np.zeros((2, 2), dtype=np.uint8))


def test_reference_uses_the_published_erfc_argument_not_a_z_score():
    # Hand-computed from SP 800-22 section 2.3 step 3 for the standard's own
    # 10-bit worked example, where pi = 6/10 and V_obs = 7.
    bits = np.array([1, 0, 0, 1, 1, 0, 1, 0, 1, 1], dtype=np.uint8)
    n = 10
    pi = 0.6
    num = abs(7 - 2.0 * n * pi * (1.0 - pi))
    den = 2.0 * math.sqrt(2.0 * n) * pi * (1.0 - pi)
    assert ref.runs_test_sp800_22(bits) == pytest.approx(special.erfc(num / den))
    # and explicitly NOT the z-score reading, which would divide by sqrt(2) again
    assert ref.runs_test_sp800_22(bits) != pytest.approx(special.erfc(num / den / math.sqrt(2.0)))


def test_monobit_style_z_scores_keep_their_sqrt2_and_runs_does_not():
    # The sqrt(2) belongs to _erfc_p because monobit feeds it a z-score. Runs
    # feeds erfc directly. Conflating the two is exactly the defect under audit.
    bits = np.array([1, 0, 0, 1, 1, 0, 1, 0, 1, 1], dtype=np.uint8)
    n = bits.size
    s = 2 * int(bits.sum()) - n
    assert rb.t_monobit(bits) == pytest.approx(special.erfc(abs(s / math.sqrt(n)) / math.sqrt(2.0)))

    pi = float(bits.mean())
    num = abs(ref.runs_count(bits) - 2.0 * n * pi * (1.0 - pi))
    den = 2.0 * math.sqrt(2.0 * n) * pi * (1.0 - pi)
    battery_argument = num / den / math.sqrt(2.0)  # what the battery does
    assert rb.t_runs(bits) == pytest.approx(special.erfc(battery_argument))
    assert rb.t_runs(bits) > ref.runs_test_sp800_22(bits)


# --------------------------------------------------------------------------- #
# 2. the defect is exactly one algebraic factor, not a bug of unknown shape
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("seed", [1, 2, 3, 7, 11, 23, 101, 997])
def test_battery_equals_reference_with_exactly_one_extra_sqrt2(seed: int):
    bits = stream(seed)
    n = int(bits.size)
    pi = float(bits.mean())
    num = abs(ref.runs_count(bits) - 2.0 * n * pi * (1.0 - pi))
    den = 2.0 * math.sqrt(2.0 * n) * pi * (1.0 - pi)
    standard_p = special.erfc(num / den)
    assert rb.t_runs(bits) == pytest.approx(special.erfc(num / den / math.sqrt(2.0)), rel=1e-12)
    assert rb.t_runs(bits) >= standard_p - 1e-15


def test_battery_pvalues_are_never_smaller_than_the_standard():
    for seed in range(1, 25):
        bits = stream(seed)
        assert rb.t_runs(bits) >= ref.runs_test_sp800_22(bits) - 1e-15


def test_battery_and_reference_differ_materially_not_numerically():
    bits = stream(3)
    assert rb.t_runs(bits) - ref.runs_test_sp800_22(bits) > 1e-3


# --------------------------------------------------------------------------- #
# 3. the applicability precondition the standard requires
# --------------------------------------------------------------------------- #


def test_applicability_condition_is_never_met_by_a_fair_stream_at_lab_lengths():
    for shift in (0, 4):
        n = 2 ** (18 + shift)
        tau = 2.0 / math.sqrt(n - 1.0)
        fair_sd = 0.5 / math.sqrt(n)  # sd of pi for a fair stream
        applicable = sum(
            ref.runs_test_sp800_22_with_applicability(stream(s, shift))["applicable"]
            for s in range(1, 21)
        )
        assert applicable == 0
        # The condition therefore demands roughly a four-sigma deviation in the
        # bit balance, which is why the test is unusable at these lengths.
        assert tau / fair_sd == pytest.approx(4.0, rel=1e-3)


def test_applicability_record_is_internally_consistent():
    bits = stream(1)
    record = ref.runs_test_sp800_22_with_applicability(bits)
    assert record["n"] == int(bits.size)
    assert record["V_obs"] == ref.runs_count(bits)
    assert record["pi"] == pytest.approx(float(bits.mean()))
    assert record["applicable"] is False
    assert record["status"] == "NOT_APPLICABLE_PER_SP800_22"
    assert record["p_value"] is None
    assert record["applicability_condition"] == "abs(pi - 0.5) >= 2 / sqrt(n - 1)"


def test_applicability_can_be_met_by_a_constructively_biased_stream():
    # At n=10 the threshold is 2/sqrt(9) = 0.667, which no proportion can reach,
    # so the condition is unreachable at tiny n. At n=100 the threshold is 0.201
    # and a 80%-ones stream passes, proving the gate is a real condition and not
    # a constant False.
    assert abs(0.6 - 0.5) < 2.0 / math.sqrt(10 - 1.0)
    biased = np.array([1] * 80 + [0] * 20, dtype=np.uint8)
    record = ref.runs_test_sp800_22_with_applicability(biased)
    assert record["applicable"] is True
    assert record["p_value"] is not None
    assert record["status"] == "APPLICABLE"


# --------------------------------------------------------------------------- #
# 4. the audit refuses to run against a battery that has changed
# --------------------------------------------------------------------------- #


def test_shared_battery_is_unmodified_since_n004():
    guard = runner.battery_digest_guard()
    assert guard["battery_unmodified_since_n004"] is True
    import sqlite3

    con = sqlite3.connect(f"file:{N004_DB}?mode=ro", uri=True)
    try:
        recorded = dict(con.execute("SELECT key, value FROM meta"))["battery_sha256"]
    finally:
        con.close()
    assert guard["shared_battery_sha256"] == recorded
    assert recorded == hashlib.sha256(Path(rb.__file__).read_bytes()).hexdigest()


def test_stored_t03_rows_are_read_only_and_complete():
    rows = runner.stored_t03_rows()
    assert len(rows) == 1040  # 4 generators x (200 seeds at 2^18 + 60 at 2^22)
    assert all(0.0 <= r["pvalue"] <= 1.0 for r in rows)
    assert {r["generator"] for r in rows} == {
        "G_LAB", "PCG64_direct", "MT19937", "WEAK_LCG_BROKEN",
    }


def test_stored_t03_never_rejected_at_alpha_for_any_generator():
    rows = runner.stored_t03_rows()
    assert sum(1 for r in rows if r["pvalue"] < 0.01) == 0


# --------------------------------------------------------------------------- #
# 5. the preregistration is frozen and states the falsification direction
# --------------------------------------------------------------------------- #


def test_preregistration_is_frozen_and_self_describing():
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    assert prereg["frozen_before_execution"] is True
    assert prereg["schema"] == "t03-runs-formula-prereg-v1"
    assert prereg["design"]["paired_streams"] is True
    assert prereg["design"]["battery_hash_guard"]
    assert "ESTIMATOR_DEFECTIVE" in prereg["decision_rule"]
    assert "NO_DEFECT_DEMONSTRATED" in prereg["decision_rule"]
    assert prereg["falsification"]
    for guard in prereg["claim_guards"]:
        assert isinstance(guard, str) and guard


def test_preregistration_never_permits_a_certification_claim():
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    blob = json.dumps(prereg).lower()
    assert "certified" in blob and "not reinstated" in blob
    assert prereg["claim_guards"], "claim guards must be non-empty"
