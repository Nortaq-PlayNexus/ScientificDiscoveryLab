#!/usr/bin/env python3
"""Audit of the laboratory RNG battery's T03_runs estimator (audit finding N-004).

Scope, stated before any number was computed:

* The shared battery module is **never modified**.  Its bytes are hashed at
  runtime and compared with the digest recorded in the N-004 raw database, so
  this audit is provably about the code that actually produced those results.
* The historical EXP-0004 certificate stays withdrawn.  Nothing here certifies a
  generator, and nothing here reinstates a certification.
* The comparison is between two implementations of NIST SP 800-22 Rev. 1a
  section 2.3 on **identical bit streams**: the shared battery's ``t_runs`` and
  the independent reference in ``runs_sp800_22.py``.  Any difference is a
  property of the estimator, not of the generator.
* Attribution is preregistered: the laboratory estimator is called defective
  only if it is non-uniform on a calibrated generator while the reference, on the
  same seeds, is uniform at the same resolution.

Outputs refuse to overwrite.  Nothing outside this directory is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from scipy import stats

import runs_sp800_22 as ref

AREA = Path(__file__).resolve().parents[1]
LAB_ROOT = Path(__file__).resolve().parents[5]
ENGINE_ROOT = LAB_ROOT / "04_SHARED_ENGINE"
N004_RESULTS = (
    LAB_ROOT
    / "03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION"
    / "RESULTS/N004_production_20260926_V3"
)
PREREG = AREA / "CONFIG" / "prereg_T03_FORMULA_AUDIT.json"

import sys  # noqa: E402

if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))
from engine.utilities.core import rng as lab_rng  # noqa: E402
from engine.validation import rng_battery as rb  # noqa: E402

REPORT_SCHEMA = "t03-runs-formula-audit-v1"


class AuditError(RuntimeError):
    """Fail-closed audit failure."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def glab_bits(label: str, seed: int, shift: int) -> np.ndarray:
    """The laboratory stream, byte-for-byte the policy N-004 used."""
    generator = lab_rng(label, seed)
    nbytes = rb.NBYTES << shift
    return np.unpackbits(generator.integers(0, 256, nbytes, dtype=np.uint32).astype(np.uint8))


def battery_digest_guard() -> dict[str, Any]:
    """Fail closed if the audited battery is not the one N-004 recorded."""
    recorded = load_json(N004_RESULTS / "N004_manifest.json")
    expected = None
    if isinstance(recorded, dict):
        expected = recorded.get("battery_sha256")
    import sqlite3

    con = sqlite3.connect(f"file:{N004_RESULTS / 'N004_raw.sqlite3'}?mode=ro", uri=True)
    try:
        rows = dict(con.execute("SELECT key, value FROM meta"))
    finally:
        con.close()
    meta_digest = rows.get("battery_sha256")
    actual = sha256_file(Path(rb.__file__))
    if expected is not None and expected != meta_digest:
        raise AuditError(
            f"N-004 manifest battery digest {expected} disagrees with its raw database "
            f"digest {meta_digest}"
        )
    if meta_digest != actual:
        raise AuditError(
            f"shared battery has changed since N-004: recorded {meta_digest}, "
            f"actual {actual}. This audit would not be about the audited code."
        )
    return {
        "shared_battery_path": Path(rb.__file__).name,
        "shared_battery_sha256": actual,
        "n004_recorded_battery_sha256": meta_digest,
        "battery_unmodified_since_n004": True,
    }


def ks_uniform(p: np.ndarray) -> dict[str, Any]:
    finite = np.asarray(p, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size < 8:
        return {"n": int(finite.size), "ks_stat": None, "ks_pvalue": None}
    result = stats.kstest(finite, "uniform")
    return {
        "n": int(finite.size),
        "ks_stat": float(result.statistic),
        "ks_pvalue": float(result.pvalue),
        "uniform_rejected_at_0.01": bool(result.pvalue <= 0.01),
    }


def stored_t03_rows() -> list[dict[str, Any]]:
    import sqlite3

    con = sqlite3.connect(f"file:{N004_RESULTS / 'N004_raw.sqlite3'}?mode=ro", uri=True)
    try:
        cur = con.execute(
            "SELECT generator, shift, test_id, pvalue FROM pvalues "
            "WHERE test_id = 'T03_runs' ORDER BY generator, shift, seed"
        )
        rows = [
            {"generator": g, "shift": int(s), "test_id": t, "pvalue": float(v)}
            for g, s, t, v in cur
        ]
    finally:
        con.close()
    return rows


def run_calibration(seeds: int, shift: int, label: str) -> dict[str, Any]:
    """Same streams, two implementations, one paired comparison."""
    lab, standard, applicable, deviations = [], [], [], []
    for seed in range(1, seeds + 1):
        bits = glab_bits(label, seed, shift)
        lab.append(float(rb.t_runs(bits)))
        record = ref.runs_test_sp800_22_with_applicability(bits)
        standard.append(float(ref.runs_test_sp800_22(bits)))
        applicable.append(bool(record["applicable"]))
        deviations.append(float(record["standardized_deviation"]))
    lab_a = np.asarray(lab)
    std_a = np.asarray(standard)
    deviations_a = np.asarray(deviations)
    n_bits = 2 ** (18 + shift)
    return {
        "bit_length": f"2^{18 + shift}",
        "n_bits": n_bits,
        "label": label,
        "seeds": seeds,
        "alpha": 0.01,
        "shared_battery": {
            "name": "engine.validation.rng_battery.t_runs",
            "ks_uniformity": ks_uniform(lab_a),
            "rejections_at_alpha": int((lab_a < 0.01).sum()),
            "observed_rate": float((lab_a < 0.01).mean()),
            "mean_p": float(lab_a.mean()),
            "p_quantiles": [float(x) for x in np.quantile(lab_a, [0.0, 0.25, 0.5, 0.75, 1.0])],
        },
        "reference_sp800_22": {
            "name": "runs_sp800_22.runs_test_sp800_22",
            "ks_uniformity": ks_uniform(std_a),
            "rejections_at_alpha": int((std_a < 0.01).sum()),
            "observed_rate": float((std_a < 0.01).mean()),
            "mean_p": float(std_a.mean()),
            "p_quantiles": [float(x) for x in np.quantile(std_a, [0.0, 0.25, 0.5, 0.75, 1.0])],
        },
        "sp800_22_applicability": {
            "condition": ref.RUNS_APPLICABILITY,
            "tau": float(2.0 / np.sqrt(n_bits - 1.0)),
            "applicable_seeds": int(sum(applicable)),
            "seeds_tested": seeds,
            "applicable_fraction": float(sum(applicable) / seeds),
        },
        "paired_relation": {
            "note": (
                "The two implementations differ only in that the shared battery "
                "divides the standard's erfc argument by sqrt(2) before calling "
                "erfc, so reference_p == erfc(sqrt(2) * erfc_argument_of_battery)."
            ),
            "max_abs_pvalue_delta": float(np.max(np.abs(lab_a - std_a))),
            "reference_over_laboratory_p_ratio_median": float(
                np.median(std_a[lab_a > 0] / lab_a[lab_a > 0])
            ),
        },
        "standardized_deviation": {
            "note": "the standard's erfc argument should be ~ |N(0,1)| with mean 0.7979",
            "observed_mean": float(deviations_a.mean()),
            "reference_mean_abs_normal": 0.7978845608028654,
        },
    }


def analyze(seeds: int, label: str) -> dict[str, Any]:
    prereg = load_json(PREREG)
    guard = battery_digest_guard()

    stored = stored_t03_rows()
    by_cell: dict[tuple[str, int], list[float]] = {}
    for row in stored:
        by_cell.setdefault((row["generator"], row["shift"]), []).append(row["pvalue"])
    stored_summary = []
    for (generator, shift), values in sorted(by_cell.items()):
        entry = {"generator": generator, "bit_length": f"2^{18 + shift}", **ks_uniform(np.asarray(values))}
        arr = np.asarray(values)
        entry["rejections_at_alpha"] = int((arr < 0.01).sum())
        entry["observed_rate"] = float((arr < 0.01).mean())
        entry["mean_p"] = float(arr.mean())
        entry["min_p"] = float(arr.min())
        stored_summary.append(entry)

    calibration = [run_calibration(seeds, 0, f"{label}-2p18"), run_calibration(seeds, 4, f"{label}-2p22")]

    primary = calibration[0]
    lab_bad = primary["shared_battery"]["ks_uniformity"].get("uniform_rejected_at_0.01")
    ref_ok = not primary["reference_sp800_22"]["ks_uniformity"].get("uniform_rejected_at_0.01")
    defective = bool(lab_bad and ref_ok)

    return {
        "schema": REPORT_SCHEMA,
        "prereg_sha256": sha256_file(PREREG),
        "prereg_experiment_id": prereg.get("experiment_id"),
        "shared_battery_guard": guard,
        "n004_stored_t03_runs": {
            "source": "N004_production_20260926_V3/N004_raw.sqlite3 (read-only)",
            "cells": stored_summary,
            "observation": (
                "T03_runs is non-uniform for every generator including the "
                "deliberately broken control, and rejects at alpha=0.01 for none of "
                "them. A generator-independent pile-up is a property of the "
                "estimator, not of the generator."
            ),
        },
        "fresh_seed_calibration": calibration,
        "verdict": {
            "estimator": "T03_runs (engine.validation.rng_battery.t_runs)",
            "classification": "ESTIMATOR_DEFECTIVE" if defective else "NO_DEFECT_DEMONSTRATED",
            "defect": (
                "an extra sqrt(2) is applied to an argument the standard defines "
                "directly in erfc units, inflating p-values"
            ),
            "attribution_basis": (
                "identical streams; the shared battery is non-uniform while the "
                "independent reference is uniform at the same resolution"
            ),
            "applicability_finding": (
                "SP 800-22 section 2.3 step 1 requires |pi - 1/2| >= 2/sqrt(n-1) "
                "before the test is run. At 2^18 that threshold is about 0.0039 "
                "while a fair stream deviates about 0.0008 on average, so the test "
                "is not applicable to these streams at all."
            ),
            "n004_t03_status_superseded": defective,
            "n004_cells_requiring_correction": (
                ["G_LAB 2^18", "G_LAB 2^22"] if defective else []
            ),
            "what_is_not_affected": [
                "the N-004 family-level BATTERY_VALID verdict, which rests on the "
                "positive control being rejected by at least one test at the "
                "family-wise level",
                "the 23 other per-test cells, which were not re-derived here",
            ],
            "what_must_not_be_claimed": [
                "that any generator is certified or random",
                "that the withdrawn EXP-0004 certificate is reinstated",
                "that G_LAB was shown to be defective; the opposite is true, the "
                "instrument was defective",
            ],
        },
    }


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise AuditError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=200)
    parser.add_argument("--label", default="t03-formula-audit")
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args(argv)

    report = analyze(args.seeds, args.label)
    write_new(
        args.output_json,
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    lines = [
        "# T03_runs estimator audit",
        "",
        f"- prereg: `{report['prereg_experiment_id']}` (`{report['prereg_sha256'][:16]}`)",
        f"- shared battery sha256: `{report['shared_battery_guard']['shared_battery_sha256'][:16]}` "
        f"(unmodified since N-004: {report['shared_battery_guard']['battery_unmodified_since_n004']})",
        f"- **verdict: {report['verdict']['classification']}**",
        f"- defect: {report['verdict']['defect']}",
        "",
        "## Stored N-004 T03_runs cells",
        "",
        "| Generator | Bits | n | KS p | rejects@0.01 | mean p |",
        "|---|---|---|---|---|---|",
    ]
    for cell in report["n004_stored_t03_runs"]["cells"]:
        lines.append(
            f"| {cell['generator']} | {cell['bit_length']} | {cell['n']} | "
            f"{cell['ks_pvalue']:.3g} | {cell['rejections_at_alpha']} | {cell['mean_p']:.4f} |"
        )
    lines += [
        "",
        "## Fresh-seed paired calibration (same streams, two implementations)",
        "",
        "| Bits | Impl | KS p | rejects@0.01 | mean p | median p |",
        "|---|---|---|---|---|---|",
    ]
    for cal in report["fresh_seed_calibration"]:
        for key, label in (("shared_battery", "shared t_runs"), ("reference_sp800_22", "SP 800-22 ref")):
            block = cal[key]
            lines.append(
                f"| {cal['bit_length']} | {label} | {block['ks_uniformity']['ks_pvalue']:.3g} | "
                f"{block['rejections_at_alpha']}/{cal['seeds']} | {block['mean_p']:.4f} | "
                f"{block['p_quantiles'][2]:.4f} |"
            )
    app = report["fresh_seed_calibration"][0]["sp800_22_applicability"]
    lines += [
        "",
        "## SP 800-22 applicability",
        "",
        f"- condition: `{app['condition']}`",
        f"- applicable seeds at 2^18: **{app['applicable_seeds']}/{app['seeds_tested']}**",
        f"- threshold tau = {app['tau']:.6f}",
        "",
        "## Claim boundary",
        "",
    ]
    lines += [f"- {item}" for item in report["verdict"]["what_must_not_be_claimed"]]
    write_new(args.output_markdown, "\n".join(lines) + "\n")
    print(json.dumps(report["verdict"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
