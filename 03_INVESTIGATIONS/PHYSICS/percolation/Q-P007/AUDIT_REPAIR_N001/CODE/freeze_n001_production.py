#!/usr/bin/env python3
"""Freeze the N-001 PRODUCTION scientific preregistration exactly once.

This is the separate immutable pre-run lock that the N-001 repair README
required before any production execution. It binds:

  * the repair configuration file (byte hash),
  * the exact production profile object (canonical-JSON hash),
  * the scientific decision rule, primary/secondary statistics, robustness
    gates, and the explicit limits of the claim.

The runner refuses production without this file, and
``verify_frozen_config()`` detects any later edit. Post-freeze amendments must
go to ``CONFIG/production_changes.jsonl`` via ``log_change()``; the file is
never rewritten.

Deliberately NOT decided by this file: any interpretation beyond the declared
interval rule, any novelty statement, and any re-estimation of p_c.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPAIR_ROOT = Path(__file__).resolve().parents[1]
# .../03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001 -> parents[4]
LAB_ROOT = REPAIR_ROOT.parents[4]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
if str(SHARED_ENGINE) not in sys.path:
    sys.path.insert(0, str(SHARED_ENGINE))

from engine.hypothesis_testing.prereg import freeze_config  # noqa: E402

REPAIR_CONFIG = REPAIR_ROOT / "CONFIG" / "n001_repair_config.json"
DEFAULT_TARGET = REPAIR_ROOT / "CONFIG" / "prereg_N001_PRODUCTION.json"

FISHER = 187.0 / 91.0  # 2.0549450549450545, the 2D Fisher cluster-mass exponent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def production_profile() -> dict:
    """Return the production profile exactly as the runner hashes it."""
    config = json.loads(REPAIR_CONFIG.read_text(encoding="utf-8"))
    return config["profiles"]["production"]


def profile_sha256(profile: dict) -> str:
    payload = json.dumps(
        profile,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256_bytes(payload)


PARAMS = {
    # --- runner-enforced bindings (validated by run_n001.validate_production_prereg)
    "audit_finding_id": "N-001",
    "profile_name": "production",
    # filled in by build_params() below
    "source_repair_config_sha256": None,
    "production_profile_sha256": None,
    # --- scientific content, frozen before the run ---
    "execution_class": "expensive_production",
    "investigation_id": "Q-P007",
    "scientific_question": (
        "Does a correctly stored, dependence-aware finite-size cluster tail "
        "reproduce the 2D Fisher exponent 187/91 at the exact site threshold, "
        "and does the historical refined p_c change that estimate?"
    ),
    "known_law_reproduction_only": True,
    "novelty_claim": False,
    "p_c_reestimation_in_scope": False,
    "p_c_inputs": {
        "canonical": 0.5927460507921,
        "refined": 0.5927289999999997,
        "note": (
            "Fixed historical inputs inherited from the repair config. p_c is "
            "NOT re-estimated here, so any p_c error propagates into tau as a "
            "finite-size effect and is not diagnosed by this experiment."
        ),
    },
    "primary_statistic": {
        "quantity": "cluster mass exponent tau",
        "arm": "canonical",
        "estimator": "cumulative",
        "window": "primary_32_4096",
        "active_tau_L": 1024,
        "fisher_reference": FISHER,
        "fisher_reference_expression": "187/91",
        "uncertainty": (
            "paired contiguous realization-block bootstrap, 2000 draws, "
            "block_size=1 (the resampling unit is the independent realization, "
            "never an individual cluster); 95% percentile interval"
        ),
    },
    "decision_rule": {
        "REPRODUCED_FISHER": (
            "the 95% realization-block bootstrap interval for the primary "
            "statistic contains 187/91"
        ),
        "DEVIATION_FROM_FISHER": (
            "the same 95% interval excludes 187/91"
        ),
        "INCONCLUSIVE": (
            "anything else, including any interval that straddles the boundary, "
            "a bootstrap success fraction below the configured 0.9 minimum, a "
            "raw-data round-trip or manifest-integrity failure, or an empty "
            "stored tail"
        ),
        "explicitly_not_a_decision_rule": (
            "post-hoc window selection, tolerance-band fitting, dropping the "
            "largest cluster more than once, or iid-cluster bootstrap. Any of "
            "these would be a protocol change and must be logged in the "
            "hash-chained change log before use."
        ),
    },
    "secondary_analyses": {
        "refined_arm": (
            "apply the identical interval rule to the refined-p_c arm; report "
            "as a separate verdict, never merged with the primary"
        ),
        "paired_delta": (
            "tau_refined - tau_canonical with a paired 95% interval. "
            "REFINED_PC_RESOLVES_DISCREPANCY only if that interval excludes 0; "
            "otherwise NO_RESOLVABLE_REFINED_EFFECT"
        ),
        "histogram_estimator": (
            "reported alongside cumulative as a correlated-bin diagnostic; it "
            "cannot overturn the cumulative primary verdict on its own"
        ),
        "sensitivity_windows": (
            "sensitivity_16_512, sensitivity_32_2048, sensitivity_64_4096 and "
            "primary_32_4096 are all reported"
        ),
    },
    "robustness_gate": {
        "rule": (
            "WINDOW_SENSITIVE if any of the four declared windows yields "
            "DEVIATION_FROM_FISHER while the primary window does not"
        ),
        "effect_on_verdict": (
            "a WINDOW_SENSITIVE flag downgrades the primary verdict to "
            "WINDOW_SENSITIVE and blocks any tau conclusion"
        ),
    },
    "resolution_statement": {
        "timing": "post_run_only",
        "content": (
            "minimum resolvable difference in tau at 80% power, computed from "
            "the observed realization-block bootstrap SD of the primary "
            "statistic and of the paired delta"
        ),
        "is_a_preregistered_power_claim": False,
    },
    "claim_guards": [
        "This is a known-law reproduction test. It cannot establish new physics.",
        "An INCONCLUSIVE verdict is a result and must be reported as one.",
        "A DEVIATION verdict is an anomaly requiring escalation, not a discovery.",
        "p_c is inherited, not measured; a deviation cannot be attributed to "
        "the refined threshold without a separate threshold experiment.",
        "Realization-block bootstrap addresses within-realization cluster "
        "dependence only; unmodelled cross-realization block dependence "
        "remains a stated limitation.",
        "Histogram bins and cumulative survival estimates are correlated, so "
        "the weighted chi-square-like value is diagnostic, not a goodness-of-fit "
        "test.",
    ],
    "known_limitations_carried_forward": [
        "one largest-cluster entry removed per realization before pooling",
        "component backend is scipy.ndimage.label with four-neighbour structure",
        "no independent second implementation of the cluster census in this run",
    ],
}


def build_params() -> dict:
    params = dict(PARAMS)
    params["source_repair_config_sha256"] = sha256_file(REPAIR_CONFIG)
    params["production_profile_sha256"] = profile_sha256(production_profile())
    if params["source_repair_config_sha256"] is None or params["production_profile_sha256"] is None:
        raise RuntimeError("failed to compute binding hashes")
    return params


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()

    params = build_params()
    target = Path(args.target).expanduser().resolve()
    frozen = freeze_config(
        experiment_id="N-001-QP007-PRODUCTION",
        hypothesis_id="HYP-N001-QP007-PROD",
        question_id="Q-P007",
        seed=20260926,
        alpha=0.01,
        controls=(
            "paired canonical/refined masks from one common uniform field per realization",
            "one largest-cluster entry removed per realization, both arms",
            "realization-block bootstrap with no iid-cluster fallback",
            "manifest-bound SQLite raw artifact with tail hashes and mask hashes",
            "raw-data round-trip validation before any fit is reported",
            "four preregistered fit windows as a window-sensitivity gate",
        ),
        analyses=(
            "primary: cumulative tau, canonical arm, window primary_32_4096, L=1024",
            "secondary: refined arm under the identical interval rule",
            "secondary: paired refined-minus-canonical delta interval",
            "secondary: histogram estimator as correlated-bin diagnostic",
            "post-run resolution statement from observed bootstrap variance",
        ),
        params=params,
        out_path=target,
        note=(
            "Production scientific preregistration for audit finding N-001. "
            "Frozen before execution; this lock cannot certify a new physical "
            "law, only test reproduction of the 2D Fisher exponent and the "
            "effect of the historical refined p_c. Amend only through "
            "CONFIG/production_changes.jsonl."
        ),
    )
    print(json.dumps({
        "created": str(target),
        "config_sha256": frozen["config_sha256"],
        "source_repair_config_sha256": params["source_repair_config_sha256"],
        "production_profile_sha256": params["production_profile_sha256"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
