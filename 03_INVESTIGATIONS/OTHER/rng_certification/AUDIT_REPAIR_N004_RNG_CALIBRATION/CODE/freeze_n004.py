#!/usr/bin/env python3
"""Freeze the bounded N-004 infrastructure smoke protocol exactly once."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPAIR_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = REPAIR_ROOT.parents[3]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
if str(SHARED_ENGINE) not in sys.path:
    sys.path.insert(0, str(SHARED_ENGINE))

from engine.hypothesis_testing.prereg import freeze_config  # noqa: E402

DEFAULT_CONFIG = REPAIR_ROOT / "CONFIG" / "n004_smoke_config.json"

HISTORICAL_HASHES = {
    "03_INVESTIGATIONS/OTHER/rng_certification/CODE/run_rng_cert.py": "3a16573cdd08c4428cf9b5ff15a4576505085d8000c04c35bd9c0733070e2054",
    "03_INVESTIGATIONS/OTHER/rng_certification/CONFIG/prereg_EXP-0004.json": "5c10b4f3b1b9edbbee56da691e3c9c9c65ed17f8d5a204681f707115487df26c",
    "03_INVESTIGATIONS/OTHER/rng_certification/RESULTS/EXP-0004_results.json": "8cf7c22dbd19bbe4e34939c325e04185ee318e56e2861310cf9e7dc8f2c6493e",
    "03_INVESTIGATIONS/OTHER/rng_certification/REPLICATION/independent_check.py": "b110dd9ae6282f7c309fff56905905038e3300f65a492ce7a2231beb5b67e109",
    "03_INVESTIGATIONS/OTHER/rng_certification/REPLICATION/independent_check.json": "d20deccdf38ad7ca82a5dba7667ec50cd3c7e79825b3a9ea97472751e0ed3b23",
    "04_SHARED_ENGINE/engine/validation/rng_battery.py": "5f53f3eacdf38e8cf0d47ddf3f7f71935856120fe08120f043347caa663b3b9e",
    "04_SHARED_ENGINE/engine/utilities/core.py": "386ab309422192337ecc9666f4052e1bf7c8f8a1da8e6cca97b289d9e0184694",
    "AUDIT/INDEPENDENT_AUDIT_20260924/rng_calibration_audit.py": "7f7b06be9b292a0c0ff0bf869e77515d06c3ea335d885ad56f06aee0a3068827",
    "AUDIT/INDEPENDENT_AUDIT_20260924/rng_calibration_results.json": "513749bd6ba9217c965f52f20deffef7e9f94e01c32105ec357b71093989ac22",
}

PARAMS = {
    "audit_finding_id": "N-004",
    "execution_class": "infrastructure_smoke",
    "purpose": "Read-only replay and bounded stream-plumbing smoke; no certification",
    "historical_audit_result": "AUDIT/INDEPENDENT_AUDIT_20260924/rng_calibration_results.json",
    "historical_input_sha256": HISTORICAL_HASHES,
    "historical_replay_seeds": list(range(100000, 100080)),
    "historical_stream_mode": "historical_shared_arrays",
    "per_test_familywise_rule": "Holm step-down FWER across 24 named test marginals",
    "dependence_policy": "preserve seed rows; report dependence diagnostics; no pooled-p inference",
    "live_plumbing_generators": ["G_LAB", "G_PCG", "G_MT"],
    "live_plumbing_seeds": [200001, 200002, 200003, 200004],
    "live_plumbing_bit_lengths": [4096, 16384],
    "live_battery_analysis": False,
    "production_run": False,
    "certification_claim": False,
    "scientific_result": None,
}


def freeze_protocol(target: Path = DEFAULT_CONFIG) -> Path:
    target = Path(target).expanduser().resolve()
    freeze_config(
        experiment_id="N-004-RNG-CALIBRATION-SMOKE",
        hypothesis_id="HYP-N004-CALIBRATION-SMOKE",
        question_id="N-004",
        seed=20260924,
        alpha=0.01,
        controls=(
            "exact replay of the historical 80x24 audit matrix",
            "shared-stream labeling",
            "Holm per-test family-wise diagnostic",
            "row-preserving dependence diagnostics",
            "bounded generator plumbing smoke",
        ),
        analyses=(
            "recompute stored audit summaries",
            "report per-test marginal calibration",
            "report shared-array dependence without pooled inference",
        ),
        params=PARAMS,
        out_path=target,
        note=(
            "Infrastructure smoke only. This protocol cannot certify a generator, "
            "authorize a production run, or create a scientific result."
        ),
    )
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args()
    created = freeze_protocol(args.config)
    print(created)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
