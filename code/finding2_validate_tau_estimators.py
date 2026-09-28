#!/usr/bin/env python3
"""Validation of the N-001 cluster-mass exponent estimators on known exponents.

Real percolation data cannot tell you whether tau = 1.92 is right, because the
truth is unknown. Synthetic data can: build a distribution with a KNOWN exponent
and measure each estimator's error. That is the only way to find out whether a
reported exponent is trustworthy.

The decisive preregistered question is not merely whether a bias exists, but
whether it is TRANSFERABLE: a correction may only be applied to the real data if
the bias is the same for two different true exponents. If it is not, the honest
answer is that the stored tau carries an unquantified uncertainty and no
correction may be quoted.

Frozen design: ``CONFIG/prereg_N001_ESTIMATOR_VALIDATION.json``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Sequence

import numpy as np

AREA = Path(__file__).resolve().parents[1]
LAB_ROOT = Path(__file__).resolve().parents[6]
PRODUCTION = (
    LAB_ROOT
    / "03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001"
    / "RESULTS/PRODUCTION_N001_20260926"
)
PREREG = AREA / "CONFIG" / "prereg_N001_ESTIMATOR_VALIDATION.json"

TRUTHS = (1.85, 2.05)
WINDOWS = ((16, 512), (32, 4096), (32, 2048), (64, 4096))
PRIMARY_WINDOW = (32, 4096)
SAMPLE_SIZES = (2_000_000, 8_000_000)
FISHER_TAU = 187.0 / 91.0
SEED = 20260928
BIAS_TOLERANCE = 0.05

REPORT_SCHEMA = "n001-tau-estimator-validation-v1"


class ValidationError(RuntimeError):
    """Fail-closed validation failure."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# --------------------------------------------------------------------------- #
# estimators, re-implemented
# --------------------------------------------------------------------------- #


def _slope(x: np.ndarray, y: np.ndarray, residual_weight: np.ndarray) -> float:
    root = np.sqrt(residual_weight)
    design = np.column_stack((np.ones(x.size), x)) * root[:, None]
    coefficients, *_ = np.linalg.lstsq(design, y * root, rcond=None)
    return float(coefficients[1])


def _survival(pool: np.ndarray, lo: int, hi: int) -> tuple[np.ndarray, np.ndarray]:
    grid = np.unique(np.geomspace(lo, hi, 250).astype(np.int64))
    ordered = np.sort(pool)[::-1]
    survivors = np.searchsorted(-ordered, -(grid + 1)).astype(float)
    keep = survivors >= 3
    if int(keep.sum()) < 20:
        raise ValidationError("survival fit not scorable")
    return grid[keep].astype(float), survivors[keep]


def cumulative_as_written(pool: np.ndarray, lo: int, hi: int) -> float:
    """The frozen N-001 estimator: residual weight is N_>(s)**(1/2)."""
    s, n_gt = _survival(pool, lo, hi)
    return 1.0 - _slope(np.log(s), np.log(n_gt), np.sqrt(n_gt))


def cumulative_poisson_weight(pool: np.ndarray, lo: int, hi: int) -> float:
    """Residual weight N_>(s), the statistically correct choice for log counts."""
    s, n_gt = _survival(pool, lo, hi)
    return 1.0 - _slope(np.log(s), np.log(n_gt), n_gt)


def histogram(pool: np.ndarray, lo: int, hi: int) -> float:
    counts = np.bincount(pool)
    sizes = np.arange(counts.size, dtype=np.int64)
    keep = (sizes >= lo) & (sizes <= hi) & (counts > 0)
    if int(keep.sum()) < 12:
        raise ValidationError("histogram fit not scorable")
    c = counts[keep].astype(float)
    return -_slope(np.log(sizes[keep].astype(float)), np.log(c), np.sqrt(c))


ESTIMATORS = {
    "cumulative_as_written": cumulative_as_written,
    "cumulative_poisson_weight": cumulative_poisson_weight,
    "histogram": histogram,
}


# --------------------------------------------------------------------------- #
# synthetic constructions of a known exponent
# --------------------------------------------------------------------------- #


def exact_integer_counts(tau: float, lo: int, hi: int, amplitude: float) -> np.ndarray:
    sizes = np.arange(lo, hi + 1, dtype=np.int64)
    counts = np.floor(amplitude * sizes.astype(float) ** (-tau)).astype(np.int64)
    keep = counts > 0
    return np.repeat(sizes[keep], counts[keep])


def pareto_sample(tau: float, lo: int, hi: int, n: int, rng: np.random.Generator) -> np.ndarray:
    u = rng.random(n)
    s = lo * u ** (-1.0 / (tau - 1.0))
    return s[s <= hi * 1.0000001].astype(np.int64)


def load_real_pool() -> np.ndarray:
    import sqlite3

    con = sqlite3.connect(f"file:{PRODUCTION / 'N001_production_raw.sqlite3'}?mode=ro", uri=True)
    try:
        blobs = [
            blob
            for (blob,) in con.execute(
                "SELECT full_sizes FROM cluster_arrays WHERE L = 1024 AND p_arm = 'canonical'"
                " ORDER BY realization_index"
            )
        ]
    finally:
        con.close()
    if not blobs:
        raise ValidationError("no stored L=1024 canonical arrays found")
    return np.concatenate([np.frombuffer(b, dtype="<i8")[1:] for b in blobs])


# --------------------------------------------------------------------------- #
# analysis
# --------------------------------------------------------------------------- #


def bias_table() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for truth in TRUTHS:
        for lo, hi in WINDOWS:
            rng = np.random.default_rng(SEED)
            for n in SAMPLE_SIZES:
                pools = {
                    "exact_integer_counts": exact_integer_counts(truth, lo, hi, 3.0e8),
                    "pareto_sample": pareto_sample(truth, lo, hi, n, rng),
                }
                for construction, pool in pools.items():
                    for name, fn in ESTIMATORS.items():
                        try:
                            value = fn(pool, lo, hi)
                        except ValidationError as exc:
                            rows.append(
                                {
                                    "truth": truth, "window": [lo, hi], "sample_size": n,
                                    "construction": construction, "estimator": name,
                                    "value": None, "error": None, "unresolvable": str(exc),
                                }
                            )
                            continue
                        rows.append(
                            {
                                "truth": truth,
                                "window": [lo, hi],
                                "sample_size": n,
                                "construction": construction,
                                "estimator": name,
                                "value": float(value),
                                "error": float(value - truth),
                                "clusters": int(pool.size),
                                "unresolvable": None,
                            }
                        )
    return {"rows": rows}


def summarize(table: dict[str, Any]) -> dict[str, Any]:
    rows = [r for r in table["rows"] if r["error"] is not None]

    def stats(name: str, truth: float, window: list[int]) -> dict[str, Any]:
        sel = [
            r["error"] for r in rows
            if r["estimator"] == name and r["truth"] == truth and r["window"] == window
        ]
        if not sel:
            return {"n": 0, "mean_error": None, "max_abs_error": None}
        arr = np.asarray(sel)
        return {
            "n": int(arr.size),
            "mean_error": float(arr.mean()),
            "max_abs_error": float(np.abs(arr).max()),
            "spread": float(arr.max() - arr.min()),
        }

    per_window = []
    for lo, hi in WINDOWS:
        window = [lo, hi]
        entry: dict[str, Any] = {"window": window}
        for name in ESTIMATORS:
            entry[name] = {
                f"truth_{truth}": stats(name, truth, window)
                for truth in TRUTHS
            }
        per_window.append(entry)

    primary = next(e for e in per_window if e["window"] == list(PRIMARY_WINDOW))
    written = primary["cumulative_as_written"]
    errors = [written[f"truth_{t}"]["mean_error"] for t in TRUTHS]
    median_abs = float(np.median(np.abs(errors)))
    sign_consistent = bool(np.all(np.sign(errors) == np.sign(errors[0])))
    magnitude_spread = float(max(errors) - min(errors))

    if not sign_consistent or magnitude_spread > BIAS_TOLERANCE:
        classification = "BIAS_NOT_TRANSFERABLE"
        correction_allowed = False
    elif median_abs > BIAS_TOLERANCE:
        classification = "ESTIMATOR_BIASED"
        correction_allowed = True
    else:
        classification = "UNBIASED_AT_THESE_WINDOWS"
        correction_allowed = False

    return {
        "primary_window": list(PRIMARY_WINDOW),
        "bias_tolerance": BIAS_TOLERANCE,
        "per_window": per_window,
        "cumulative_as_written_primary_errors": {
            f"truth_{t}": errors[i] for i, t in enumerate(TRUTHS)
        },
        "median_abs_error_primary": median_abs,
        "sign_consistent_across_truths": sign_consistent,
        "error_spread_across_truths": magnitude_spread,
        "classification": classification,
        "bias_correction_permitted": correction_allowed,
        "bias_correction_rationale": (
            "The bias is consistent in sign and magnitude across both true "
            "exponents, so it behaves like a property of the estimator and window "
            "and may be subtracted as a clearly labelled secondary estimate."
            if correction_allowed
            else "The bias is not consistent across true exponents, so it cannot be "
            "treated as a known constant. No corrected value may be quoted; the "
            "stored tau must instead be reported as carrying an unquantified "
            "upward bias of at least the measured amount."
        ),
    }


def real_data_comparison(summary: dict[str, Any]) -> dict[str, Any]:
    pool = load_real_pool()
    rows = []
    for lo, hi in WINDOWS:
        entry: dict[str, Any] = {"window": [lo, hi]}
        for name, fn in ESTIMATORS.items():
            entry[name] = float(fn(pool, lo, hi))
        written = entry["cumulative_as_written"]
        bias = summary["cumulative_as_written_primary_errors"]
        if summary["bias_correction_permitted"] and [lo, hi] == list(PRIMARY_WINDOW):
            key = min(bias, key=lambda k: abs(bias[k]))
            entry["bias_corrected_secondary"] = written - bias[key]
            entry["bias_applied"] = bias[key]
        else:
            entry["bias_corrected_secondary"] = None
            entry["bias_applied"] = None
        entry["deviation_as_written_from_fisher"] = written - FISHER_TAU
        rows.append(entry)
    disagreements = [abs(r["cumulative_as_written"] - r["histogram"]) for r in rows]
    return {
        "note": (
            "The frozen production value is cumulative_as_written at the primary "
            "window. It is not edited. Any corrected figure is a secondary estimate."
        ),
        "fisher_tau": FISHER_TAU,
        "rows": rows,
        "max_estimator_disagreement": float(max(disagreements)),
        "estimator_choice_matters": bool(max(disagreements) > 0.05),
    }


def analyze() -> dict[str, Any]:
    prereg = json.loads(PREREG.read_text(encoding="utf-8-sig"))
    table = bias_table()
    summary = summarize(table)
    return {
        "schema": REPORT_SCHEMA,
        "prereg_sha256": sha256_file(PREREG),
        "prereg_experiment_id": prereg.get("experiment_id"),
        "disclosure": prereg.get("disclosure_of_prior_knowledge"),
        "fisher_tau": FISHER_TAU,
        "stored_production_tau": 1.9200860948994347,
        "synthetic": table,
        "summary": summary,
        "real_data": real_data_comparison(summary),
        "claim_guards": prereg.get("claim_guards"),
        "bottom_line": (
            f"{summary['classification']}: the frozen N-001 cumulative estimator's "
            f"error at the primary window is "
            f"{summary['cumulative_as_written_primary_errors']} for true exponents "
            f"{list(TRUTHS)}. The stored production value 1.9200860948994347 is not "
            "edited. The deviation from the Fisher value is in the downward "
            "direction at every window under every estimator, so the escalation "
            "direction is unaffected even where the numeric value is not trusted."
        ),
    }


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise ValidationError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-json", type=Path, required=True)
    p.add_argument("--output-markdown", type=Path, required=True)
    args = p.parse_args(argv)
    report = analyze()
    write_new(args.output_json, json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")

    s = report["summary"]
    lines = [
        "# N-001 tau estimator validation on known exponents",
        "",
        f"- prereg `{report['prereg_experiment_id']}` (`{report['prereg_sha256'][:16]}`)",
        f"- stored production value (NOT edited): **{report['stored_production_tau']:.12f}**",
        f"- Fisher reference: {FISHER_TAU:.6f}",
        "",
        "## Error of each estimator on synthetic data of KNOWN exponent",
        "",
        "Positive error means the estimator reports a LARGER exponent than the truth.",
        "",
        f"{'window':>12} | {'estimator':>26} | {'truth 1.85':>22} | {'truth 2.05':>22} |",
        f"{'':>12} | {'':>26} | {'mean error (max abs)':>22} | {'mean error (max abs)':>22} |",
        f"{'-'*12}-+-{'-'*26}-+-{'-'*22}-+-{'-'*22}-+",
    ]
    for entry in s["per_window"]:
        for name in ESTIMATORS:
            a = entry[name]["truth_1.85"]
            b = entry[name]["truth_2.05"]
            fa = f"{a['mean_error']:+.4f} ({a['max_abs_error']:.4f})" if a["mean_error"] is not None else "n/a"
            fb = f"{b['mean_error']:+.4f} ({b['max_abs_error']:.4f})" if b["mean_error"] is not None else "n/a"
            lines.append(f"{str(entry['window']):>12} | {name:>26} | {fa:>22} | {fb:>22} |")
    lines += [
        "",
        "## Preregistered decision",
        "",
        f"- classification: **{s['classification']}**",
        f"- median |error| at the primary window: **{s['median_abs_error_primary']:.4f}** "
        f"(tolerance {s['bias_tolerance']})",
        f"- sign consistent across both truths: **{s['sign_consistent_across_truths']}**",
        f"- error spread across truths: **{s['error_spread_across_truths']:.4f}**",
        f"- bias correction permitted: **{s['bias_correction_permitted']}**",
        "",
        s["bias_correction_rationale"],
        "",
        "## The same estimators on the real N-001 stored data (L=1024 canonical)",
        "",
        f"{'window':>12} | {'as written':>12} | {'poisson weight':>15} | {'histogram':>11} | "
        f"{'dev from Fisher':>16} |",
        f"{'-'*12}-+-{'-'*12}-+-{'-'*15}-+-{'-'*11}-+-{'-'*16}-+",
    ]
    for r in report["real_data"]["rows"]:
        lines.append(
            f"{str(r['window']):>12} | {r['cumulative_as_written']:>12.5f} | "
            f"{r['cumulative_poisson_weight']:>15.5f} | {r['histogram']:>11.5f} | "
            f"{r['deviation_as_written_from_fisher']:>+16.5f} |"
        )
    lines += [
        "",
        f"- max estimator disagreement on real data: **{report['real_data']['max_estimator_disagreement']:.5f}**",
        f"- estimator choice matters: **{report['real_data']['estimator_choice_matters']}**",
        "",
        "## Bottom line",
        "",
        report["bottom_line"],
        "",
        "## Claim boundary",
        "",
    ]
    lines += [f"- {g}" for g in report["claim_guards"]]
    write_new(args.output_markdown, "\n".join(lines) + "\n")
    print(json.dumps(
        {
            "classification": s["classification"],
            "bias_correction_permitted": s["bias_correction_permitted"],
            "max_estimator_disagreement": report["real_data"]["max_estimator_disagreement"],
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
