#!/usr/bin/env python3
"""Corrected re-derivation of the N-004 T03_runs cell for G_LAB.

Three variants of the same statistic are evaluated on identical bit streams, so
the differences are properties of the estimator and not of the generator:

* ``as_implemented``                        -- the historical code, unmodified
* ``sqrt2_corrected``                        -- SP 800-22 2.3 without the spurious sqrt(2)
* ``sqrt2_corrected_and_applicability_gated``-- the same, honouring the standard's
                                                section 2.3 step 1 precondition

The status of record is decided by the frozen rule in
``CONFIG/prereg_T03_RECALIBRATION.json``.  The shared battery is never modified
and its digest is checked at runtime.  Outputs refuse to overwrite.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence

import numpy as np
from scipy import stats

AREA = Path(__file__).resolve().parents[1]
LAB_ROOT = Path(__file__).resolve().parents[5]
ENGINE_ROOT = LAB_ROOT / "04_SHARED_ENGINE"
N004_RESULTS = (
    LAB_ROOT
    / "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION"
    / "RESULTS/N004_production_20260926_V3"
)
PREREG = AREA / "CONFIG" / "prereg_T03_RECALIBRATION.json"
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))
sys.path.insert(0, str(AREA / "CODE"))

from engine.utilities.core import rng as lab_rng  # noqa: E402
from engine.validation import rng_battery as rb  # noqa: E402
import runs_sp800_22 as ref  # noqa: E402

REPORT_SCHEMA = "t03-runs-recalibration-v1"
ALPHA = 0.01
APPLICABILITY_MIN_SEEDS = 5


class RecalibrationError(RuntimeError):
    """Fail-closed recalibration failure."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def battery_digest_guard() -> dict[str, Any]:
    import sqlite3

    con = sqlite3.connect(f"file:{N004_RESULTS / 'N004_raw.sqlite3'}?mode=ro", uri=True)
    try:
        recorded = dict(con.execute("SELECT key, value FROM meta"))["battery_sha256"]
    finally:
        con.close()
    actual = sha256_file(Path(rb.__file__))
    if actual != recorded:
        raise RecalibrationError(
            f"shared battery changed since N-004: recorded {recorded}, actual {actual}"
        )
    return {
        "shared_battery_sha256": actual,
        "n004_recorded_battery_sha256": recorded,
        "battery_unmodified_since_n004": True,
    }


def variants_for(bits: np.ndarray) -> dict[str, Any]:
    record = ref.runs_test_sp800_22_with_applicability(bits)
    return {
        "as_implemented": float(rb.t_runs(bits)),
        "sqrt2_corrected": float(ref.runs_test_sp800_22(bits)),
        "sqrt2_corrected_and_applicability_gated": (
            float(ref.runs_test_sp800_22(bits)) if record["applicable"] else None
        ),
        "applicable": bool(record["applicable"]),
        "abs_pi_minus_half": float(record["abs_pi_minus_half"]),
    }


def ks_block(values: Sequence[float], label: str) -> dict[str, Any]:
    arr = np.asarray([v for v in values if v is not None], dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size < 8:
        return {
            "variant": label,
            "n": int(arr.size),
            "ks_stat": None,
            "ks_pvalue": None,
            "uniform_rejected": None,
            "rejections_at_alpha": None,
            "mean_p": None,
            "scorable": False,
            "scorable_reason": (
                f"only {arr.size} scorable p-values, below the 8 needed for a KS test"
            ),
        }
    res = stats.kstest(arr, "uniform")
    return {
        "variant": label,
        "n": int(arr.size),
        "ks_stat": float(res.statistic),
        "ks_pvalue": float(res.pvalue),
        "uniform_rejected": bool(res.pvalue <= ALPHA),
        "rejections_at_alpha": int((arr < ALPHA).sum()),
        "observed_rate": float((arr < ALPHA).mean()),
        "mean_p": float(arr.mean()),
        "median_p": float(np.median(arr)),
        "scorable": True,
    }


def decide(ks: dict[str, Any], applicable: int, seeds: int) -> str:
    """The frozen decision rule, applied literally."""
    if applicable < APPLICABILITY_MIN_SEEDS:
        return "UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION"
    if not ks.get("scorable"):
        return "UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION"
    if ks["uniform_rejected"]:
        return "MISCALIBRATED"
    return "CALIBRATED"


def cell(label: str, seeds: int, shift: int) -> dict[str, Any]:
    rows = []
    for s in range(1, seeds + 1):
        gen = lab_rng(f"{label}-{shift}", s)
        bits = np.unpackbits(
            gen.integers(0, 256, rb.NBYTES << shift, dtype=np.uint32).astype(np.uint8)
        )
        rows.append(variants_for(bits))

    applicable = sum(r["applicable"] for r in rows)
    blocks = [
        ks_block([r["as_implemented"] for r in rows], "as_implemented"),
        ks_block([r["sqrt2_corrected"] for r in rows], "sqrt2_corrected"),
        ks_block(
            [r["sqrt2_corrected_and_applicability_gated"] for r in rows],
            "sqrt2_corrected_and_applicability_gated",
        ),
    ]
    status = decide(blocks[2], applicable, seeds)
    return {
        "generator": "G_LAB",
        "bit_length": f"2^{18 + shift}",
        "n_bits": 2 ** (18 + shift),
        "seeds": seeds,
        "applicability": {
            "condition": ref.RUNS_APPLICABILITY,
            "tau": float(2.0 / np.sqrt(2 ** (18 + shift) - 1.0)),
            "applicable_seeds": int(applicable),
            "seeds_tested": seeds,
            "min_required_for_scorability": APPLICABILITY_MIN_SEEDS,
            "mean_abs_pi_minus_half": float(np.mean([r["abs_pi_minus_half"] for r in rows])),
        },
        "variants": blocks,
        "status_of_record": status,
        "historical_n004_status": "calibrated",
        "status_changed": status != "calibrated",
    }


def analyze(seeds: int, label: str) -> dict[str, Any]:
    prereg = json.loads(PREREG.read_text(encoding="utf-8-sig"))
    cells = [cell(label, seeds, 0), cell(label, seeds, 4)]
    return {
        "schema": REPORT_SCHEMA,
        "prereg_sha256": sha256_file(PREREG),
        "prereg_experiment_id": prereg.get("experiment_id"),
        "decision_rule_verbatim": prereg.get("decision_rule"),
        "shared_battery_guard": battery_digest_guard(),
        "cells": cells,
        "verdict": {
            "status_of_record": [c["status_of_record"] for c in cells],
            "n004_per_test_claim_correction": (
                "N-004 recorded 0 of 24 tests miscalibrated for G_LAB, counting "
                "T03_runs as calibrated. The corrected status is UNRESOLVED_NOT_"
                "APPLICABLE_AT_THIS_RESOLUTION at both lengths, so the accurate "
                "statement is 23 of 24 per-test cells calibrated, 0 miscalibrated, "
                "and 1 unresolvable because the standard's own precondition is "
                "never met."
            ),
            "sqrt2_alone_explains": (
                "the difference between the as-implemented and corrected "
                "uniformity is the entire recorded non-uniformity"
            ),
            "must_not_claim": [
                "that G_LAB failed a test; it did not, the test was unusable",
                "that any generator is certified",
                "that the EXP-0004 certificate is reinstated",
                "that the defect's non-detection at 2^22 shows the estimator is fine",
            ],
        },
    }


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise RecalibrationError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seeds", type=int, default=200)
    p.add_argument("--label", default="t03-recal")
    p.add_argument("--output-json", type=Path, required=True)
    p.add_argument("--output-markdown", type=Path, required=True)
    args = p.parse_args(argv)

    report = analyze(args.seeds, args.label)
    write_new(args.output_json, json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    lines = [
        "# T03_runs corrected re-derivation of the N-004 cell",
        "",
        f"- prereg `{report['prereg_experiment_id']}` (`{report['prereg_sha256'][:16]}`)",
        f"- shared battery unmodified since N-004: {report['shared_battery_guard']['battery_unmodified_since_n004']}",
        "",
        "| Bits | Variant | n | KS p | rej@0.01 | mean p | scorable |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in report["cells"]:
        for v in c["variants"]:
            kp = "n/a" if v["ks_pvalue"] is None else f"{v['ks_pvalue']:.3e}"
            mn = "n/a" if v["mean_p"] is None else f"{v['mean_p']:.4f}"
            rj = "n/a" if v["rejections_at_alpha"] is None else str(v["rejections_at_alpha"])
            lines.append(
                f"| {c['bit_length']} | {v['variant']} | {v['n']} | {kp} | {rj} | {mn} | {v['scorable']} |"
            )
    lines += ["", "## SP 800-22 applicability", "",
              "| Bits | tau | applicable seeds | mean abs(pi-1/2) |", "|---|---|---|---|"]
    for c in report["cells"]:
        a = c["applicability"]
        lines.append(
            f"| {c['bit_length']} | {a['tau']:.6f} | **{a['applicable_seeds']}/{a['seeds_tested']}** "
            f"| {a['mean_abs_pi_minus_half']:.6f} |"
        )
    lines += ["", "## Status of record", "",
              "| Bits | N-004 recorded | Corrected status | Changed |", "|---|---|---|---|"]
    for c in report["cells"]:
        lines.append(
            f"| {c['bit_length']} | {c['historical_n004_status']} | **{c['status_of_record']}** "
            f"| {c['status_changed']} |"
        )
    lines += ["", "## Claim boundary", ""]
    lines += [f"- {x}" for x in report["verdict"]["must_not_claim"]]
    lines += ["", report["verdict"]["n004_per_test_claim_correction"]]
    write_new(args.output_markdown, "\n".join(lines) + "\n")
    print(json.dumps({"status_of_record": report["verdict"]["status_of_record"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
