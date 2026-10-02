#!/usr/bin/env python3
"""Finite-size crossover diagnostic for the N-001 cluster-mass exponent.

This is a **diagnostic on stored data**. The N-001 production already stored one
flat non-increasing int64 cluster-size array per realization and per p arm at
L = 256, 512 and 1024, so a per-size analysis needs no new Monte Carlo.

The estimator is re-implemented here from its written specification rather than
imported from the production runner, so that reproducing the stored production
tau is a real independent-implementation control instead of a tautology.

Frozen design and decision rule: ``CONFIG/prereg_N001_CROSSOVER.json``.
Outputs refuse to overwrite. The stored production database is opened read-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sqlite3
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
PREREG = AREA / "CONFIG" / "prereg_N001_CROSSOVER.json"

RAW_DB = PRODUCTION / "N001_production_raw.sqlite3"
STORED_SUMMARY = PRODUCTION / "N001_production_summary.json"

FISHER_TAU = 187.0 / 91.0
PRIMARY_WINDOW = (32, 4096)
ACTIVE_TAU_L = 1024
STORED_WINDOWS = ((16, 512), (32, 4096), (32, 2048), (64, 4096))
L_SIZES = (256, 512, 1024)
GRID_POINTS = 250
MIN_SURVIVORS = 3
MIN_FIT_POINTS = 20
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_SEED = 2201024

REPORT_SCHEMA = "n001-crossover-diagnostic-v1"


class DiagnosticError(RuntimeError):
    """Fail-closed diagnostic failure."""


# --------------------------------------------------------------------------- #
# estimator, re-implemented from the stored specification
# --------------------------------------------------------------------------- #


def weighted_loglog_fit(
    x: np.ndarray, y: np.ndarray, weights: np.ndarray, tau_sign: float
) -> dict[str, Any]:
    """Weighted least-squares slope in log-log space, as specified by N-001.

    Spec: solve ``argmin_b sum_i w_i (y_i - b0 - b1 x_i)^2`` via ``lstsq`` on the
    weight-rooted design matrix, take the slope standard error from the inverse of
    the weighted normal matrix, and reduce chi-square by ``points - 2``.
    """
    if x.size < 3 or x.size != y.size or x.size != weights.size:
        raise DiagnosticError("log-log fit needs at least three aligned points")
    design = np.column_stack((np.ones(x.size), x))
    root = np.sqrt(np.asarray(weights, dtype=float))
    coefficients, *_ = np.linalg.lstsq(design * root[:, None], y * root, rcond=None)
    residual = y - design @ coefficients
    information = design.T @ (np.asarray(weights, dtype=float)[:, None] * design)
    covariance = np.linalg.pinv(information, rcond=1e-12)
    slope = float(coefficients[1])
    return {
        "tau": float(tau_sign * slope),
        "intercept": float(coefficients[0]),
        "slope": slope,
        "slope_standard_error": float(math.sqrt(max(float(covariance[1, 1]), 0.0))),
        "chi2_reduced_diagnostic": float(
            np.sum((residual * root) ** 2) / max(x.size - 2, 1)
        ),
        "points": int(x.size),
    }


def fit_tau(tails: Sequence[np.ndarray], estimator: str, lo: int, hi: int) -> dict[str, Any] | None:
    """Cumulative or histogram tau over the window [lo, hi].

    Cumulative: ``N_>(s) ~ s^-(tau-1)`` on a 250-point log-spaced grid of integer
    s, keeping points with at least 3 survivors, so ``tau = 1 - slope``.
    Histogram: ``n_s ~ s^-tau`` on the observed support, so ``tau = -slope``.
    Weights are the square root of the observed count in both cases.
    """
    arrays = [np.asarray(t, dtype=np.int64) for t in tails]
    arrays = [a for a in arrays if a.size]
    if not arrays:
        return None
    pooled = np.concatenate(arrays)
    if np.any(pooled <= 0):
        raise DiagnosticError("tail contains non-positive cluster sizes")

    if estimator == "cumulative":
        ordered = np.sort(pooled)[::-1]
        grid = np.unique(np.geomspace(int(lo), int(hi), GRID_POINTS).astype(np.int64))
        survivors = np.searchsorted(-ordered, -(grid + 1)).astype(float)
        keep = survivors >= MIN_SURVIVORS
        if int(keep.sum()) < MIN_FIT_POINTS:
            return None
        fit = weighted_loglog_fit(
            np.log(grid[keep].astype(float)),
            np.log(survivors[keep]),
            np.sqrt(survivors[keep]),
            tau_sign=1.0,
        )
        fit["tau"] = float(1.0 - fit["slope"])
        fit["used_window"] = [int(grid[keep].min()), int(grid[keep].max())]
    elif estimator == "histogram":
        counts = np.bincount(pooled)
        sizes = np.arange(counts.size, dtype=np.int64)
        keep = (sizes >= int(lo)) & (sizes <= int(hi)) & (counts > 0)
        if int(keep.sum()) < 12:
            return None
        fit = weighted_loglog_fit(
            np.log(sizes[keep].astype(float)),
            np.log(counts[keep].astype(float)),
            np.sqrt(counts[keep].astype(float)),
            tau_sign=-1.0,
        )
        fit["used_window"] = [int(sizes[keep].min()), int(sizes[keep].max())]
    else:
        raise DiagnosticError(f"unknown estimator {estimator!r}")

    fit.update(
        {
            "estimator": estimator,
            "requested_window": [int(lo), int(hi)],
            "realizations": len(arrays),
            "tail_clusters": int(pooled.size),
        }
    )
    return fit


# --------------------------------------------------------------------------- #
# stored data access, read-only
# --------------------------------------------------------------------------- #


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stored_digest_guard() -> dict[str, Any]:
    """Fail closed if the stored production artifact is not the one described."""
    import importlib.util

    manifest = json.loads(
        (PRODUCTION / "N001_production_manifest.json").read_text(encoding="utf-8-sig")
    )
    recorded = manifest.get("artifact", {}).get("sha256")
    actual = sha256_file(RAW_DB)
    if not recorded:
        raise DiagnosticError(
            "production manifest records no raw artifact digest, so this diagnostic "
            "cannot prove it is reading the intended data"
        )
    if recorded != actual:
        raise DiagnosticError(
            f"stored production raw database changed: manifest {recorded}, actual {actual}"
        )
    return {
        "raw_database": RAW_DB.name,
        "raw_sha256": actual,
        "manifest_recorded_sha256": recorded,
        "raw_unmodified": True,
        "manifest_pairing_label": manifest.get("pairing"),
        "manifest_pairing_label_note": (
            "the manifest's pairing field carries the literal text "
            "'iid_cluster_bootstrap'. The production code actually resamples "
            "realization blocks (resampling_unit='realization_block', block_size=1, "
            "which is one realization per block), so the label is stale text and "
            "not the method. Recorded rather than corrected, because the manifest "
            "is a historical artifact."
        ),
    }


def load_tails(arm: str) -> dict[int, list[np.ndarray]]:
    con = sqlite3.connect(f"file:{RAW_DB}?mode=ro", uri=True)
    try:
        out: dict[int, list[np.ndarray]] = {int(L): [] for L in L_SIZES}
        for L, blob in con.execute(
            "SELECT L, full_sizes FROM cluster_arrays WHERE p_arm = ? ORDER BY L, realization_index",
            (arm,),
        ):
            arr = np.frombuffer(blob, dtype="<i8")
            if int(L) in out:
                out[int(L)].append(arr)
    finally:
        con.close()
    for L, arrs in out.items():
        if not arrs:
            raise DiagnosticError(f"no stored tails for L={L} arm={arm}")
    return out


# --------------------------------------------------------------------------- #
# realization-block bootstrap
# --------------------------------------------------------------------------- #


def block_bootstrap(
    tails_by_realization: Sequence[np.ndarray],
    estimator: str,
    lo: int,
    hi: int,
    draws: int,
    seed: int,
) -> dict[str, Any]:
    """Resample realizations with replacement; never resample clusters.

    Clusters inside one realization share a common seed and a common threshold
    geometry, so treating them as independent would understate the interval.
    """
    n = len(tails_by_realization)
    rng = np.random.default_rng(seed)
    values: list[float] = []
    for _ in range(draws):
        picks = rng.integers(0, n, size=n)
        resampled = [tails_by_realization[int(i)] for i in picks]
        fit = fit_tau(resampled, estimator, lo, hi)
        if fit is not None and np.isfinite(fit["tau"]):
            values.append(float(fit["tau"]))
    if len(values) < max(int(0.9 * draws), 10):
        raise DiagnosticError(
            f"bootstrap acceptance too low: {len(values)} of {draws} draws produced a fit"
        )
    arr = np.asarray(values)
    return {
        "draws_requested": draws,
        "draws_accepted": int(arr.size),
        "draws_rejected": int(draws - arr.size),
        "mean": float(arr.mean()),
        "standard_deviation": float(arr.std(ddof=1)),
        "ci95": [float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))],
        "block": "realization",
    }


# --------------------------------------------------------------------------- #
# analysis
# --------------------------------------------------------------------------- #


def per_size(arm: str, bootstrap: bool) -> dict[str, Any]:
    tails = load_tails(arm)
    cells = []
    for L in L_SIZES:
        arrs = tails[L]
        # one largest cluster removed per realization, as the production did
        trimmed = [a[1:] if a.size > 1 else a for a in arrs]
        point = fit_tau(trimmed, "cumulative", *PRIMARY_WINDOW)
        if point is None:
            cells.append({"L": L, "scorable": False, "reason": "primary fit not scorable"})
            continue
        cell: dict[str, Any] = {
            "L": L,
            "scorable": True,
            "realizations": len(arrs),
            "tail_clusters": point["tail_clusters"],
            "tau": point["tau"],
            "slope_standard_error": point["slope_standard_error"],
            "chi2_reduced_diagnostic": point["chi2_reduced_diagnostic"],
            "fit_points": point["points"],
            "used_window": point["used_window"],
            "deviation_from_fisher": point["tau"] - FISHER_TAU,
        }
        if bootstrap:
            cell["bootstrap"] = block_bootstrap(
                trimmed, "cumulative", *PRIMARY_WINDOW, BOOTSTRAP_DRAWS, BOOTSTRAP_SEED + L
            )
        cells.append(cell)
    return {"arm": arm, "window": list(PRIMARY_WINDOW), "cells": cells}


def l_trend(cells: list[dict[str, Any]]) -> dict[str, Any]:
    usable = [c for c in cells if c.get("scorable")]
    if len(usable) < 3:
        return {
            "status": "INDETERMINATE",
            "reason": f"only {len(usable)} scorable sizes; three are required",
        }
    L = np.array([c["L"] for c in usable], dtype=float)
    tau = np.array([c["tau"] for c in usable], dtype=float)
    x = np.log(L)
    design = np.column_stack((np.ones(x.size), x))
    coefficients, *_ = np.linalg.lstsq(design, tau, rcond=None)
    slope = float(coefficients[1])
    residual = tau - design @ coefficients
    dof = max(x.size - 2, 1)
    variance = float(np.sum(residual**2) / dof)
    covariance = variance * np.linalg.pinv(design.T @ design, rcond=1e-12)
    slope_se = float(math.sqrt(max(float(covariance[1, 1]), 0.0)))
    intercept = float(coefficients[0])
    crossing_ln = (FISHER_TAU - intercept) / slope if slope != 0 else None

    monotonic = all(usable[i]["tau"] < usable[i + 1]["tau"] for i in range(len(usable) - 1))
    interval_excludes_zero_increasing = (
        slope - 1.96 * slope_se > 0.0 and slope + 1.96 * slope_se > 0.0
    )
    crossing_beyond_1024 = (
        crossing_ln is not None and crossing_ln > math.log(max(L_SIZES))
    )
    return {
        "status": "COMPUTED",
        "sizes": [int(v) for v in L],
        "tau": [float(v) for v in tau],
        "deviation_from_fisher": [float(v - FISHER_TAU) for v in tau],
        "slope_tau_per_log_L": slope,
        "slope_standard_error": slope_se,
        "slope_ci95": [slope - 1.96 * slope_se, slope + 1.96 * slope_se],
        "intercept": intercept,
        "fisher_tau": FISHER_TAU,
        "excludes_zero_increasing_direction": bool(interval_excludes_zero_increasing),
        "monotonic_increasing": bool(monotonic),
        "extrapolated_ln_L_at_fisher": crossing_ln,
        "extrapolated_L_at_fisher": (math.exp(crossing_ln) if crossing_ln else None),
        "extrapolation_is_meaningful": bool(interval_excludes_zero_increasing and slope != 0.0),
        "extrapolation_caveat": (
            "The extrapolated L is a purely arithmetic consequence of a fitted slope. "
            "When the slope interval includes zero the slope is not distinguishable "
            "from no drift at all, and the extrapolated L is meaningless: it would "
            "diverge as the slope goes to zero. It is retained for transparency only "
            "and must not be quoted as a required system size."
        ),
        "crossing_beyond_1024": bool(crossing_beyond_1024),
        "crossing_beyond_1024_is_meaningful": bool(
            interval_excludes_zero_increasing and crossing_beyond_1024
        ),
        "residual_tau_rms": float(np.sqrt(np.mean(residual**2))),
        "power_caveat": (
            "Only three sizes spanning a factor of four in L are available, so this "
            "slope test has low power against a slow drift. NOT ESTABLISHED is not "
            "the same as excluded: a weak crossover that only bites above L = 1024 "
            "would not be visible here. What is excluded is a crossover large enough "
            "to explain the deviation within this size range."
        ),
    }


def window_curvature(tails: dict[int, list[np.ndarray]]) -> dict[str, Any]:
    """Curvature measured two ways, on the production's own pooling scope.

    Pools the active tau_L size only, which is what the production sensitivity
    fits used, so the cumulative column also reproduces the four stored values
    and acts as a second control on this implementation.
    """
    pooled = [a[1:] if a.size > 1 else a for a in tails[ACTIVE_TAU_L]]
    stored = json.loads(STORED_SUMMARY.read_text(encoding="utf-8-sig"))["fits"]
    stored_map = {
        "sensitivity_16_512": (16, 512),
        "primary_32_4096": (32, 4096),
        "sensitivity_32_2048": (32, 2048),
        "sensitivity_64_4096": (64, 4096),
    }
    rows = []
    for lo, hi in STORED_WINDOWS:
        cum = fit_tau(pooled, "cumulative", lo, hi)
        hist = fit_tau(pooled, "histogram", lo, hi)
        key = next(
            (k for k, w in stored_map.items() if w == (lo, hi)), None
        )
        stored_tau = (
            stored[key]["cumulative"]["canonical"]["tau"] if key else None
        )
        rows.append(
            {
                "window": [lo, hi],
                "cumulative_tau": (cum or {}).get("tau"),
                "stored_cumulative_tau": stored_tau,
                "cumulative_reproduces_stored": (
                    None
                    if cum is None or stored_tau is None
                    else bool(abs(cum["tau"] - stored_tau) < 1e-12)
                ),
                "histogram_tau": (hist or {}).get("tau"),
                "estimator_disagreement": (
                    abs(cum["tau"] - hist["tau"])
                    if cum and hist and np.isfinite(cum["tau"]) and np.isfinite(hist["tau"])
                    else None
                ),
            }
        )
    cum_values = [r["cumulative_tau"] for r in rows if r["cumulative_tau"] is not None]
    disagreements = [r["estimator_disagreement"] for r in rows if r["estimator_disagreement"]]
    return {
        "note": (
            "For an exact power law the cumulative and histogram estimators agree. "
            "Their disagreement, and the spread of the cumulative value across "
            "windows, are direct measures of curvature."
        ),
        "pooling_scope": f"L = {ACTIVE_TAU_L} only, matching the production sensitivity fits",
        "all_windows_reproduce_stored": all(
            r["cumulative_reproduces_stored"] is True for r in rows
        ),
        "rows": rows,
        "cumulative_spread": (max(cum_values) - min(cum_values)) if cum_values else None,
        "max_estimator_disagreement": max(disagreements) if disagreements else None,
    }


def paired_threshold_check(tails: dict[int, list[np.ndarray]]) -> dict[str, Any]:
    """Canonical and refined arms share seeds, so this is a paired comparison."""
    canonical = load_tails("canonical")
    rows = []
    for L in L_SIZES:
        c = fit_tau([a[1:] for a in canonical[L]], "cumulative", *PRIMARY_WINDOW)
        r = fit_tau([a[1:] for a in tails[L]], "cumulative", *PRIMARY_WINDOW)
        if c and r:
            rows.append({"L": L, "delta_tau_refined_minus_canonical": r["tau"] - c["tau"]})
    return {
        "note": "arms share seeds by construction, so differences are paired, not independent",
        "rows": rows,
        "max_abs_delta": max((abs(r["delta_tau_refined_minus_canonical"]) for r in rows), default=None),
    }


def reproduction_control() -> dict[str, Any]:
    """Re-derive the stored production primary tau with this independent code.

    The production primary pools the active tau_L size only. That is worth
    stating because the laboratory status line reports '1,462,967 pooled tail
    clusters', which is exactly the L = 1024 tail after one largest cluster per
    realization is removed, not a pool over all three sizes. Pooling across
    sizes instead shifts tau by about -0.0115, which is itself reported below.
    """
    stored = json.loads(STORED_SUMMARY.read_text(encoding="utf-8-sig"))
    target = stored["fits"]["primary_32_4096"]["cumulative"]["canonical"]["tau"]
    tails = load_tails("canonical")
    pooled_active = [a[1:] for a in tails[ACTIVE_TAU_L]]
    pooled_all = [a[1:] for L in L_SIZES for a in tails[L]]
    mine = fit_tau(pooled_active, "cumulative", *PRIMARY_WINDOW)
    pooled_fit = fit_tau(pooled_all, "cumulative", *PRIMARY_WINDOW)
    if mine is None or pooled_fit is None:
        raise DiagnosticError("reproduction control produced no fit")
    delta = abs(mine["tau"] - target)
    return {
        "stored_production_tau": target,
        "this_implementation_tau": mine["tau"],
        "abs_delta": delta,
        "reproduces_stored_value": bool(delta < 1e-12),
        "active_tau_L": ACTIVE_TAU_L,
        "active_L_tail_clusters": mine["tail_clusters"],
        "pooled_across_all_L_tau": pooled_fit["tau"],
        "pooling_scope_shift": pooled_fit["tau"] - target,
        "note": (
            "The estimator was re-implemented from its written specification, not "
            "imported from the production runner, so exact agreement is an "
            "independent-implementation control rather than a tautology."
        ),
    }


def analyze(bootstrap: bool) -> dict[str, Any]:
    prereg = json.loads(PREREG.read_text(encoding="utf-8-sig"))
    guard = stored_digest_guard()
    repro = reproduction_control()

    canonical = per_size("canonical", bootstrap)
    trend = l_trend(canonical["cells"])
    tails_refined = load_tails("refined")
    curvature = window_curvature(load_tails("canonical"))
    paired = paired_threshold_check(tails_refined)

    scorable = trend.get("status") == "COMPUTED"
    if not scorable:
        status = "INDETERMINATE"
    elif trend["monotonic_increasing"] and trend["excludes_zero_increasing_direction"] \
            and trend["crossing_beyond_1024"]:
        status = "CROSSOVER_SUPPORTED"
    else:
        status = "CROSSOVER_NOT_ESTABLISHED"
    curvature_flag = bool(
        (curvature["cumulative_spread"] or 0.0) > 0.01
        or (curvature["max_estimator_disagreement"] or 0.0) > 0.01
    )

    return {
        "schema": REPORT_SCHEMA,
        "prereg_sha256": sha256_file(PREREG),
        "prereg_experiment_id": prereg.get("experiment_id"),
        "disclosure": prereg.get("disclosure_of_prior_knowledge"),
        "fisher_tau": FISHER_TAU,
        "primary_window": list(PRIMARY_WINDOW),
        "stored_data_guard": guard,
        "reproduction_control": repro,
        "per_size_canonical": canonical,
        "l_trend": trend,
        "window_curvature": curvature,
        "paired_threshold_check": paired,
        "decision": {
            "status": status,
            "curvature_present": curvature_flag,
            "preregistered_order_satisfied": trend.get("monotonic_increasing"),
            "interpretation": (
                "A supported result relocates the question to larger L; it does not "
                "resolve Q-P007 and is not a discovery."
                if status == "CROSSOVER_SUPPORTED"
                else "The finite-size-crossover explanation is not supported by the "
                "stored data, so the deviation is unexplained at these sizes and "
                "requires larger L than 1024, not a repeat of N-001."
            ),
        },
        "claim_guards": prereg.get("claim_guards"),
    }


def write_new(path: Path, text: str) -> None:
    if path.exists():
        raise DiagnosticError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--no-bootstrap", action="store_true")
    p.add_argument("--output-json", type=Path, required=True)
    p.add_argument("--output-markdown", type=Path, required=True)
    args = p.parse_args(argv)

    report = analyze(bootstrap=not args.no_bootstrap)
    if not report["reproduction_control"]["reproduces_stored_value"]:
        raise DiagnosticError(
            "reproduction control FAILED: this implementation does not reproduce the "
            "stored production tau, so nothing downstream is trustworthy"
        )
    write_new(args.output_json, json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")

    t = report["l_trend"]
    d = report["decision"]
    lines = [
        "# N-001 finite-size crossover diagnostic",
        "",
        f"- prereg `{report['prereg_experiment_id']}` (`{report['prereg_sha256'][:16]}`)",
        f"- stored raw database unmodified: {report['stored_data_guard']['raw_unmodified']}",
        f"- reproduction control: stored tau {report['reproduction_control']['stored_production_tau']:.12f}"
        f" vs this implementation {report['reproduction_control']['this_implementation_tau']:.12f}"
        f" (delta {report['reproduction_control']['abs_delta']:.2e})",
        "",
        "## Primary: tau at each size, window s in [32, 4096], canonical arm",
        "",
        "| L | realizations | tail clusters | tau | 95% CI | deviation from 187/91 | chi2_red |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in report["per_size_canonical"]["cells"]:
        if not c.get("scorable"):
            lines.append(f"| {c['L']} | - | - | not scorable | - | - | - |")
            continue
        ci = c.get("bootstrap", {}).get("ci95")
        ci_txt = f"[{ci[0]:.4f}, {ci[1]:.4f}]" if ci else "not run"
        lines.append(
            f"| {c['L']} | {c['realizations']} | {c['tail_clusters']} | **{c['tau']:.5f}** | "
            f"{ci_txt} | {c['deviation_from_fisher']:+.5f} | {c['chi2_reduced_diagnostic']:.3f} |"
        )
    lines += [
        "",
        f"Fisher tau = 187/91 = {FISHER_TAU:.6f}",
        "",
        "## Trend in log L (pre-registered directional test)",
        "",
    ]
    if t.get("status") == "COMPUTED":
        lines += [
            f"- slope d(tau)/d(ln L) = **{t['slope_tau_per_log_L']:+.5f}** "
            f"(SE {t['slope_standard_error']:.5f}, 95% CI "
            f"[{t['slope_ci95'][0]:+.5f}, {t['slope_ci95'][1]:+.5f}])",
            f"- monotonic increasing in the preregistered order: **{t['monotonic_increasing']}**",
            f"- interval excludes zero in the increasing direction: **{t['excludes_zero_increasing_direction']}**",
            f"- extrapolated L where tau would reach 187/91: **{t['extrapolated_L_at_fisher']}**",
            f"- crossing beyond L = 1024: **{t['crossing_beyond_1024']}**",
            f"- residual RMS around the log-log line: {t['residual_tau_rms']:.5f}",
        ]
    else:
        lines.append(f"- {t.get('reason')}")
    lines += [
        "",
        "## Curvature diagnostics (independent of the L trend)",
        "",
        "| window | cumulative tau | histogram tau | estimator disagreement |",
        "|---|---|---|---|",
    ]
    for r in report["window_curvature"]["rows"]:
        ct = f"{r['cumulative_tau']:.5f}" if r["cumulative_tau"] else "n/a"
        ht = f"{r['histogram_tau']:.5f}" if r["histogram_tau"] else "n/a"
        dg = f"{r['estimator_disagreement']:.5f}" if r["estimator_disagreement"] else "n/a"
        lines.append(f"| {r['window']} | {ct} | {ht} | {dg} |")
    lines += [
        "",
        f"- cumulative spread across windows: **{report['window_curvature']['cumulative_spread']}**",
        f"- max estimator disagreement: **{report['window_curvature']['max_estimator_disagreement']}**",
        f"- curvature present: **{d['curvature_present']}**",
        "",
        "## Paired threshold check (canonical vs refined, shared seeds)",
        "",
        "| L | refined - canonical |",
        "|---|---|",
    ]
    for r in report["paired_threshold_check"]["rows"]:
        lines.append(f"| {r['L']} | {r['delta_tau_refined_minus_canonical']:+.6f} |")
    lines += [
        "",
        f"max |delta| = **{report['paired_threshold_check']['max_abs_delta']}**",
        "",
        "## Decision",
        "",
        f"**{d['status']}**",
        "",
        d["interpretation"],
        "",
        "## Disclosure",
        "",
        report["disclosure"] or "",
        "",
        "## Claim boundary",
        "",
    ]
    lines += [f"- {g}" for g in report["claim_guards"]]
    write_new(args.output_markdown, "\n".join(lines) + "\n")
    print(json.dumps(d, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
