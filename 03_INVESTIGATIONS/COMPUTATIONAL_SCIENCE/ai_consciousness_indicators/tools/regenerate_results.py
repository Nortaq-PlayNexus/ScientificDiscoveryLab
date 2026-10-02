#!/usr/bin/env python3
"""Regenerate RESULTS/*.json with the current code, then verify.

Run from the repository root after any change to `battery.py` or
`perturbation.py`:

    python tools/regenerate_results.py

Recorded results carry a SHA-256 over a canonical JSON encoding. If the scoring
logic changes, those hashes MUST be regenerated, or `experiment_verify.py` will
report the recorded results as tampered. That is the intended behaviour: a stale
hash is how a reader finds out the code moved under the numbers.

This script prefers the originating lab's shared engine when importable (it
produces the canonical `experiment.json` envelope) and falls back to
`_rng.py` otherwise. Both RNG implementations are asserted bit-identical by
`test_standalone.py`, so the hashes do not depend on which is used.

Writes:
  RESULTS/experiment.json       EXP-C001 calibration + sensitivity
  RESULTS/experiment_C003.json  EXP-C003 robustness
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Optional: the lab's canonical engine, if this checkout sits inside one.
LAB_ENGINE = ROOT.parents[2] / "04_SHARED_ENGINE" if len(ROOT.parents) > 2 else None
if LAB_ENGINE is not None and LAB_ENGINE.is_dir():
    sys.path.insert(0, str(LAB_ENGINE))

import battery as B  # noqa: E402
from perturbation import compare_regions  # noqa: E402


def make_experiment_json(experiment_id, question, hypothesis, seed, parameters, result, out_path):
    """Build the experiment.json envelope, using the lab engine when available."""
    try:
        from engine.utilities.core import make_experiment_json as lab_make

        return lab_make(
            experiment_id, question, hypothesis, seed, parameters, result, out_path=out_path
        )
    except ModuleNotFoundError:
        pass

    # Standalone equivalent, matching the lab's documented contract.
    from datetime import datetime, timezone

    from experiment_verify import sha256_json

    record = {
        "experiment_id": experiment_id,
        "question": question,
        "hypothesis": hypothesis,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": seed,
        "parameters": parameters,
        "software": {
            "python": sys.version.split()[0],
            "numpy": __import__("numpy").__version__,
            "scipy": __import__("scipy").__version__,
        },
        "machine": {"platform": sys.platform},
        "result": result,
        "result_hash": sha256_json(result),
        "result_hash_scope": "canonical_json_utf8_result_object",
        "canonical_json": {
            "allow_nan": False,
            "ensure_ascii": False,
            "separators": [",", ":"],
            "sort_keys": True,
        },
    }
    target = Path(out_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


FIXES = [
    "F08: BatteryResult.calibration_passed was `not require_calibration or True`, "
    "unconditionally True. run_battery now gates on a computed calibration_state() "
    "and raises CalibrationNotEstablished when calibration has not passed.",
    "F09: duplicate-indicator check compared len(dict values) to len(set(keys)), "
    "which can never differ. Contradictory assessments are now rejected.",
    "F10: perturbation family P4 (conscious_rate_shift) was computed and discarded, "
    "so one of six advertised robustness families perturbed nothing.",
]


def main() -> int:
    cal = B.calibration_reference_result()
    all_unknown = [
        B.Assessment(i.key, B.Status.UNKNOWN, B.Evidence.UNTESTED) for i in B.INDICATORS
    ]
    boot = B.bootstrap_stability("all_untested_reference", all_unknown)

    c001 = make_experiment_json(
        "EXP-C001",
        "Q-C001: Can a preregistered indicator battery bound AI consciousness credence, "
        "and does it pass known-answer calibration?",
        "HYP-C001: theory-collapsed aggregator with known-answer gate separates reference "
        "systems and is not raised by fluent self-report",
        20261002,
        {
            "alpha": 0.01,
            "n_indicators": len(B.INDICATORS),
            "n_anchors": len(B.KNOWN_ANSWERS),
            "temperature_selected_by": "sweep_over_anchors_CIRCULAR_see_F01",
        },
        {
            "calibration": cal,
            "bootstrap_all_untested": boot,
            "parameters": {
                "soft_or_temperature": B._SOFT_OR_TEMPERATURE,
                "absence_factor": B._NECESSARY_ABSENCE_FACTOR,
                "necessity_penalty": B._NECESSITY_ABSENCE_PENALTY,
            },
            "layer": "L1 instrument result only",
            "claim": (
                "internally consistent scoring function; NOT a claim about any AI "
                "system's consciousness"
            ),
            "fixes_in_this_record": FIXES,
        },
        ROOT / "RESULTS" / "experiment.json",
    )

    regions = compare_regions(seed=0)
    c003 = make_experiment_json(
        "EXP-C003",
        "Q-C001 (robustness arm): how much of the Q-C001 battery output survives joint "
        "perturbation of all discretionary parameters?",
        "HYP-C001-robustness: ordering and the fluency-vs-architecture separation survive "
        "perturbation, while absolute credences do not",
        20261002,
        {
            "n_draws_per_region": 1500,
            "seed": 0,
            "perturbation_families": 6,
            "regions": 2,
            "alpha": 0.01,
        },
        {
            "verdict": regions["verdict"],
            "verdict_detail": regions["verdict_detail"],
            "plausible_region": regions["plausible_region"],
            "aggressive_region": regions["aggressive_region"],
            "layer": "L1/L2 instrument robustness result; no claim about any AI system",
            "key_finding": (
                "F-B (adversarial fluent-liar < human) holds 1.0000 in BOTH regions; "
                "absolute anchors degrade (F-A 1.00->0.67, F-C 0.98->0.79). Ordering "
                "robust, absolutes assumption-dominated."
            ),
            "fixes_in_this_record": FIXES,
        },
        ROOT / "RESULTS" / "experiment_C003.json",
    )

    print(f"EXP-C001 result_hash: {c001['result_hash']}")
    print(f"EXP-C003 result_hash: {c003['result_hash']}")
    print(f"calibration passed:   {cal['passed']}")
    print("\nverifying:")
    from experiment_verify import verify_file

    for name in ("experiment.json", "experiment_C003.json"):
        rep = verify_file(ROOT / "RESULTS" / name)
        print(f"  {'VALID' if rep['valid'] else 'INVALID'}  {name}")
        if not rep["valid"]:
            print("   ", rep["errors"])
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
