#!/usr/bin/env python3
"""Freeze the N-004 dependence-aware RNG calibration protocol exactly once.

Addresses audit finding N-004 (Priority 1). The historical EXP-0004 "CERTIFIED"
conclusion was WITHDRAWN because its pooled p-values were computed across shared
input streams, which does not support the independence the pooled decision
assumed. The isolated N-004 smoke replays the historical matrix and does bounded
plumbing only; it explicitly does not certify anything.

This production protocol asks the audit's actual question: WHICH INDIVIDUAL
BATTERY TESTS ARE CALIBRATED, per generator, independent of any pooled decision?

Design decisions frozen here, all before execution:

  * Per-test calibration, judged by the uniformity of the per-seed p-values
    across many INDEPENDENT seeds, rather than by one pooled pass/fail.
  * Two stream scales, 2^18 and 2^22 bits, because a test can be calibrated at
    one length and miscalibrated at another.
  * A DELIBERATELY BROKEN generator is included and MUST be flagged. A battery
    that passes everything is worthless; this is the audit's falsification
    condition ("if control generators fail marginal tests, invalidate the
    battery before interpreting G_LAB"), inverted into a positive control.
  * Family-wise inference per seed uses Holm, AND a dependence-respecting
    max-T permutation control across tests, because tests on one stream share
    input and are not independent.
  * No generator may be called certified. The strongest permitted statement is
    per-test calibration with a stated resolution.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INV_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = INV_ROOT.parents[3]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
if str(SHARED_ENGINE) not in sys.path:
    sys.path.insert(0, str(SHARED_ENGINE))

from engine.hypothesis_testing.prereg import freeze_config  # noqa: E402

DEFAULT_TARGET = INV_ROOT / "CONFIG" / "prereg_N004_PRODUCTION.json"

GENERATORS = {
    "G_LAB": {
        "role": "target",
        "description": "the laboratory stream: numpy PCG64 seeded by a sha256-derived "
                       "value of (label, seed), i.e. engine.utilities.core.rng",
        "expectation": "the generator every experiment in this lab depends on",
    },
    "PCG64_direct": {
        "role": "reference",
        "description": "numpy.random.default_rng(seed) with no lab wrapper",
        "expectation": "should be statistically indistinguishable from G_LAB",
    },
    "MT19937": {
        "role": "reference",
        "description": "numpy.random.RandomState(seed), the legacy Mersenne Twister",
        "expectation": "a different, independently implemented generator",
    },
    "WEAK_LCG_BROKEN": {
        "role": "positive_control_must_fail",
        "description": "a deliberately broken generator: a 31-bit LCG whose low bits "
                       "and short-period structure are known to be inadequate",
        "expectation": "MUST be rejected by the battery; if it is not, the battery "
                       "is invalid and no conclusion about G_LAB may be drawn",
    },
}

BIT_LENGTHS = {"2^18": 18, "2^22": 22}
SEEDS = {"2^18": 200, "2^22": 60}
ALPHA = 0.01
FAMILYWISE_METHODS = ("holm_step_down", "max_t_permutation")

RESOLUTION_NOTE = (
    "With S seeds per generator and length, the rejection-rate estimate has "
    "standard error sqrt(alpha*(1-alpha)/S): 0.0071 at S=200 and 0.0127 at S=60. "
    "The uniformity test on per-seed p-values is the more powerful instrument, "
    "and the strongest permitted statement is per-test calibration AT THIS "
    "RESOLUTION. A miscalibration that shifts the true rejection rate from 0.01 "
    "to below about 0.04 is not detectable here and must be reported as "
    "unresolved rather than as calibrated."
)

PARAMS = {
    "audit_finding_id": "N-004",
    "investigation_id": "Q-I004",
    "purpose": "per-test calibration of the shared RNG battery, per generator and "
               "per stream length, with dependence-respecting family-wise inference",
    "battery": {
        "module": "engine.validation.rng_battery",
        "tests": 24,
        "note": "the historical EXP-0004 battery, unmodified; NIST SP 800-22 "
                "footprint plus classic tests, NOT the official NIST harness",
        "sha256_required_at_runtime": True,
    },
    "generators": GENERATORS,
    "bit_lengths": BIT_LENGTHS,
    "seeds_per_generator_and_length": SEEDS,
    "seed_namespace": "N-004-PRODUCTION-v1, disjoint from every historical seed range",
    "alpha": ALPHA,
    "familywise_methods": FAMILYWISE_METHODS,
    "primary_statistic": {
        "quantity": "per-test calibration of the p-value distribution across seeds",
        "test": "one-sample Kolmogorov-Smirnov of the per-seed p-values against "
                "Uniform(0,1), per test per generator per bit length, with "
                "Benjamini-Hochberg FDR across the 24 tests within each cell",
        "secondary": [
            "observed rejection rate at alpha with an exact binomial band",
            "Holm step-down family-wise rejection rate per seed",
            "max-T permutation family-wise rejection rate per seed, which "
            "respects the shared input stream instead of assuming independence",
        ],
    },
    "decision_rule": {
        "BATTERY_VALID": (
            "the positive control WEAK_LCG_BROKEN is rejected by at least one "
            "test at the family-wise level, at every bit length"
        ),
        "BATTERY_INVALID": (
            "the broken control is never rejected. This voids every other number "
            "in the run: no statement about G_LAB may be made"
        ),
        "per_test_calibrated": (
            "the BH-adjusted KS p-value for that test exceeds 0.01 and the "
            "observed rejection rate lies inside the exact binomial band"
        ),
        "per_test_miscalibrated": (
            "the BH-adjusted KS p-value is at or below 0.01, or the rejection "
            "rate lies outside the exact binomial band"
        ),
        "UNRESOLVED_AT_THIS_RESOLUTION": (
            "any test whose interval is too wide to decide; reported as "
            "unresolved, never as calibrated"
        ),
    },
    "positive_control": {
        "generator": "WEAK_LCG_BROKEN",
        "requirement": "must be flagged; this is the falsification condition from "
                       "the audit, inverted into a positive control",
        "on_failure": "the whole run is classified BATTERY_INVALID",
    },
    "controls": [
        "deliberately broken generator as a positive control that must fail",
        "two independent reference generators (raw PCG64 and legacy MT19937)",
        "two stream lengths, because calibration need not be length-independent",
        "max-T permutation family-wise control that does not assume test independence",
        "exact binomial band on rejection rates rather than a normal approximation",
        "BH-FDR across the 24 tests within each generator/length cell",
        "the shared battery module is hash-checked at runtime and never modified",
    ],
    "resolution": RESOLUTION_NOTE,
    "claim_guards": [
        "No generator may be called certified. The historical EXP-0004 certificate "
        "remains withdrawn and this run does not reinstate it.",
        "Passing a test battery is not proof of randomness and not a NIST certification.",
        "A calibrated test at one stream length does not certify the other length.",
        "UNRESOLVED_AT_THIS_RESOLUTION is a real outcome and must not be reported "
        "as agreement.",
        "This experiment says nothing about any physical result; it only "
        "characterises the measurement instrument the rest of the lab depends on.",
    ],
    "known_limitations": [
        "the battery is a NIST footprint, not the official NIST SP 800-22 harness, "
        "so its p-value formulas are reimplementations",
        "tests within a seed share one input stream and are dependent; the max-T "
        "control handles this for the family-wise rate but per-test KS p-values "
        "are still BH-adjusted rather than exactly adjusted",
        "the deliberately broken control is a specific failure mode; a battery "
        "that catches it may still miss others",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()
    frozen = freeze_config(
        experiment_id="N-004-RNG-CALIBRATION-PRODUCTION",
        hypothesis_id="HYP-N004-CALIBRATION-PRODUCTION",
        question_id="Q-I004",
        seed=20260926,
        alpha=ALPHA,
        controls=tuple(PARAMS["controls"]),
        analyses=(
            "primary: per-test KS uniformity of p-values across independent seeds, BH-FDR",
            "secondary: exact-binomial rejection-rate band at alpha",
            "secondary: Holm step-down family-wise rejection rate per seed",
            "secondary: max-T permutation family-wise rejection rate per seed",
            "gate: the deliberately broken generator must be rejected",
        ),
        params=PARAMS,
        out_path=target,
        note=(
            "Production dependence-aware RNG calibration for audit finding N-004. "
            "Frozen before execution. Cannot certify any generator and does not "
            "reinstate the withdrawn EXP-0004 certificate. Amend only through "
            "CONFIG/production_changes.jsonl."
        ),
    )
    print(json.dumps({
        "created": str(target),
        "config_sha256": frozen["config_sha256"],
        "generators": list(GENERATORS),
        "seeds": SEEDS,
        "alpha": ALPHA,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
