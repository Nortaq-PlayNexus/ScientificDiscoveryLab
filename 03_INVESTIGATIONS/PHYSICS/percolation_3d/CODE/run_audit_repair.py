"""Canonical, fail-closed Q-P008 runner after the 2026-09-24 audit.

This runner does not read or overwrite historical EXP-0011/EXP-0013 artifacts.
It requires an explicit immutable audit-repair config and output directory,
uses opposite 3D planes, honors configured sample counts, keeps ragged
realization-level samples, validates ``tau_L`` before Monte Carlo, and writes
raw per-size artifacts plus hashes before producing a summary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

HERE = Path(__file__).resolve().parent
QDIR = HERE.parent
PHYSICS = QDIR.parent
LAB_ROOT = HERE.parents[3]
ENGINE = PHYSICS / "percolation" / "ENGINE"
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
for import_root in (ENGINE, SHARED_ENGINE):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

import perc_engine as pe  # noqa: E402
from engine.hypothesis_testing.prereg import verify_frozen_config  # noqa: E402
from engine.utilities.core import (  # noqa: E402
    make_experiment_json,
    verify_experiment_result_hash,
)

REQUIRED_CONFIG_MARKERS = (
    "dimension_aware_boundaries",
    "ragged_realization_samples",
    "realization_level_tau_bootstrap",
)


class ConfigError(ValueError):
    """The active protocol cannot be executed safely."""


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def load_config(path: Path) -> tuple[dict, str]:
    config = verify_frozen_config(path)
    validate_config(config)
    return config, str(config["config_sha256"])


def _positive_int(value, label: str) -> int:
    if type(value) is not int or value <= 0:
        raise ConfigError(f"{label} must be a positive integer")
    return value


def validate_config(config: dict) -> None:
    params = config.get("parameters")
    if not isinstance(params, dict):
        raise ConfigError("missing parameters object")
    if params.get("purpose") != "infrastructure_smoke" and params.get("width_estimator") != "probit_mle":
        raise ConfigError(
            "scientific runs require width_estimator='probit_mle'; "
            "adjacent-linear crossings are smoke diagnostics only"
        )
    markers = set(params.get("required_repairs", []))
    missing = sorted(set(REQUIRED_CONFIG_MARKERS) - markers)
    if missing:
        raise ConfigError(f"config is missing required repair markers: {missing}")
    if params.get("system") != "site_cubic_3d":
        raise ConfigError("system must be site_cubic_3d")
    p_c = params.get("p_c")
    if type(p_c) not in (int, float) or not 0.0 < float(p_c) < 1.0:
        raise ConfigError("p_c must be strictly between zero and one")
    L_list = [_positive_int(L, "L") for L in params.get("L_list", [])]
    if len(L_list) < 2 or len(set(L_list)) != len(L_list):
        raise ConfigError("L_list must contain at least two unique positive sizes")
    width_L = [_positive_int(L, "width L") for L in params.get("width_L_list", [])]
    if width_L != L_list:
        raise ConfigError("width_L_list must exactly match L_list")
    n_real = params.get("n_real", {})
    if set(map(str, L_list)) != set(n_real):
        raise ConfigError("n_real keys must exactly match L_list")
    for L in L_list:
        _positive_int(n_real[str(L)], f"n_real[L={L}]")
    width_grid = params.get("width_grid", {})
    for L in L_list:
        item = width_grid.get(f"L{L}")
        if not isinstance(item, dict):
            raise ConfigError(f"missing width_grid entry for L={L}")
        lo, hi, step = item["grid"]
        if not (0.0 < float(lo) < float(hi) < 1.0 and float(step) > 0.0):
            raise ConfigError(f"invalid width grid for L={L}")
        _positive_int(item.get("n_each"), f"width n_each L={L}")
    tau_L = _positive_int(params.get("tau_L"), "tau_L")
    if tau_L not in L_list:
        raise ConfigError("tau_L must be one of the active L_list values")
    fit_lo, fit_hi = params.get("tau_fit_range", (0, 0))
    if not (0 < int(fit_lo) < int(fit_hi)):
        raise ConfigError("tau_fit_range must be positive and increasing")
    _positive_int(params.get("bootstrap_draws"), "bootstrap_draws")
    for key in ("l_seed_multiplier", "p_seed_stride", "r_seed_stride"):
        _positive_int(params.get(key), key)


def cell_label(config: dict, L: int, kind: str) -> str:
    params = config["parameters"]
    token = config.get("p_canon_token") or params.get("p_canon_token")
    if token is None:
        token = "p" + str(int(round(float(params["p_c"]) * 10_000_000)))
    pattern = params["rng_label_pattern"]
    token = str(token)
    if f"p<pcanon>" in pattern and token.startswith("p"):
        pattern = pattern.replace("p<pcanon>", token)
    else:
        pattern = pattern.replace("<pcanon>", token)
    return pattern.replace("<L>", str(L)).replace("<kind>", kind)


def realization_seed(config: dict, L: int, p_index: int, realization: int) -> int:
    params = config["parameters"]
    return int(
        config["seed"]
        + L * int(params["l_seed_multiplier"])
        + p_index * int(params["p_seed_stride"])
        + realization * int(params["r_seed_stride"])
    )


def width_curve_L(config: dict, L: int) -> tuple[list[dict], np.ndarray, np.ndarray]:
    params = config["parameters"]
    grid = params["width_grid"][f"L{L}"]
    lo, hi, step = map(float, grid["grid"])
    n_pts = int(np.floor((hi - lo) / step + 1e-12)) + 1
    p_grid = lo + step * np.arange(n_pts, dtype=float)
    n_each = int(grid["n_each"])
    src, dst, N = pe.cubic_lattice_3d(int(L))
    label = cell_label(config, int(L), "width")
    rows = []
    outcomes = np.zeros((len(p_grid), n_each), dtype=np.uint8)
    seed_grid = np.zeros((len(p_grid), n_each), dtype=np.int64)
    for p_index, p in enumerate(p_grid):
        k_v = 0
        for realization in range(n_each):
            seed = realization_seed(config, int(L), p_index, realization)
            result = pe.run_span_cell_edges(
                src,
                dst,
                N,
                int(L),
                float(p),
                1,
                seed,
                label,
                semantics="site",
                ndim=3,
            )
            k_v += int(result["k_v"])
            outcomes[p_index, realization] = np.uint8(result["k_v"])
            seed_grid[p_index, realization] = seed
        rows.append(
            {
                "p": float(p),
                "k_v": k_v,
                "n": n_each,
                "width": k_v / n_each,
            }
        )
        print(
            f"[QP008-REPAIR] width L={L} p={p:.6f} W={k_v/n_each:.4f}",
            flush=True,
        )
    return rows, outcomes, seed_grid


def interpolate_width_crossing(rows: list[dict], target: float = 0.5) -> dict:
    """Interpolate adjacent crossings; summarize noisy multiple crossings.

    A finite-sample width curve need not be monotone. The historical runner used
    the last below-grid point and first above-grid point globally, which can
    select indices in reverse order. This repair records every adjacent sign
    change and reports their median as a diagnostic; a production claim should
    additionally use the preregistered probit fit.
    """
    ps = np.asarray([row["p"] for row in rows], dtype=float)
    widths = np.asarray([row["width"] for row in rows], dtype=float)
    if ps.size < 2 or not np.all(np.diff(ps) > 0):
        raise ValueError("width grid must contain at least two strictly increasing p values")
    crossings = []
    exact = []
    for index, width in enumerate(widths):
        if width == target:
            exact.append(float(ps[index]))
    for index in range(ps.size - 1):
        left = widths[index] - target
        right = widths[index + 1] - target
        if left == 0 or right == 0 or left * right > 0:
            continue
        denominator = widths[index + 1] - widths[index]
        if denominator == 0:
            continue
        fraction = (target - widths[index]) / denominator
        crossings.append(
            float(ps[index] + fraction * (ps[index + 1] - ps[index]))
        )
    values = exact + crossings
    if not values:
        return {
            "bracketed": False,
            "p_c": None,
            "method": "adjacent_linear_crossing_diagnostic",
            "reason": "target width is not crossed by any configured adjacent interval",
        }
    return {
        "bracketed": True,
        "p_c": float(np.median(values)),
        "method": "median_adjacent_linear_crossing_diagnostic",
        "crossing_count": len(values),
        "crossings": values,
    }


def _save_width_npz(
    output_dir: Path,
    *,
    config_sha256: str,
    L: int,
    rows: list[dict],
    outcomes: np.ndarray,
    seeds: np.ndarray,
) -> dict:
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / f"width_L{L}_realizations.npz"
    if target.exists():
        raise FileExistsError(f"refusing to overwrite width artifact: {target}")
    p_values = np.asarray([row["p"] for row in rows], dtype="<f8")
    n_each = np.asarray([row["n"] for row in rows], dtype="<i8")
    with target.open("wb") as handle:
        np.savez_compressed(
            handle,
            config_sha256=np.asarray(config_sha256),
            L=np.asarray(L),
            p_values=p_values,
            n_each=n_each,
            outcomes=outcomes,
            seeds=seeds,
        )
        handle.flush()
        os.fsync(handle.fileno())
    with np.load(target, allow_pickle=False) as archive:
        expected_keys = {
            "config_sha256", "L", "p_values", "n_each", "outcomes", "seeds"
        }
        if set(archive.files) != expected_keys:
            raise RuntimeError(f"width NPZ key schema mismatch for L={L}")
        if str(archive["config_sha256"].item()) != config_sha256:
            raise RuntimeError(f"width NPZ config hash mismatch for L={L}")
        if int(archive["L"].item()) != L:
            raise RuntimeError(f"width NPZ L mismatch for L={L}")
        if not np.array_equal(archive["p_values"], p_values):
            raise RuntimeError(f"width NPZ p grid mismatch for L={L}")
        if not np.array_equal(archive["n_each"], n_each):
            raise RuntimeError(f"width NPZ sample counts mismatch for L={L}")
        if not np.array_equal(archive["outcomes"], outcomes):
            raise RuntimeError(f"width NPZ outcomes mismatch for L={L}")
        if not np.array_equal(archive["seeds"], seeds):
            raise RuntimeError(f"width NPZ seeds mismatch for L={L}")
        if outcomes.dtype != np.dtype("u1") or not np.all((outcomes == 0) | (outcomes == 1)):
            raise RuntimeError(f"width outcomes must be binary uint8 for L={L}")
        if seeds.dtype != np.dtype("<i8") or seeds.shape != outcomes.shape:
            raise RuntimeError(f"width seed schema mismatch for L={L}")
        expected_counts = np.asarray([row["k_v"] for row in rows], dtype=np.int64)
        if not np.array_equal(outcomes.sum(axis=1, dtype=np.int64), expected_counts):
            raise RuntimeError(f"width outcome counts disagree with aggregate rows for L={L}")
    return {
        "path": str(target.relative_to(output_dir)).replace("\\", "/"),
        "bytes": target.stat().st_size,
        "sha256": sha256_file(target),
        "n_p_values": int(outcomes.shape[0]),
        "n_real_per_p": int(outcomes.shape[1]),
        "schema": "width_outcomes_v1",
    }


def measure_width(config: dict, output_dir: Path, config_sha256: str) -> dict:
    measured = {}
    raw_manifest = {}
    estimator = config["parameters"].get(
        "width_estimator", "adjacent_linear_smoke_diagnostic"
    )
    for L in config["parameters"]["L_list"]:
        rows, outcomes, seeds = width_curve_L(config, int(L))
        raw_manifest[str(L)] = _save_width_npz(
            output_dir,
            config_sha256=config_sha256,
            L=int(L),
            rows=rows,
            outcomes=outcomes,
            seeds=seeds,
        )
        crossing = interpolate_width_crossing(rows)
        if estimator == "probit_mle":
            ps = np.asarray([row["p"] for row in rows], dtype=float)
            ks = np.asarray([row["k_v"] for row in rows], dtype=np.int64)
            ns = np.asarray([row["n"] for row in rows], dtype=np.int64)
            mu, sigma, converged = pe.probit_fit(ps, ks, ns, s0=0.10)
            primary = {
                "method": "probit_mle",
                "p_c": float(mu) if converged else None,
                "width_sigma": float(sigma) if converged else None,
                "converged": bool(converged),
            }
        else:
            primary = {
                "method": "adjacent_linear_smoke_diagnostic",
                "p_c": crossing["p_c"] if crossing["bracketed"] else None,
                "converged": bool(crossing["bracketed"]),
            }
        measured[str(L)] = {
            "primary": primary,
            "crossing_diagnostic": crossing,
            "curve": rows,
        }
    valid = [
        value["primary"]["p_c"]
        for value in measured.values()
        if value["primary"]["p_c"] is not None
    ]
    extrapolation = None
    if len(valid) == len(config["parameters"]["L_list"]) and len(valid) >= 2:
        Ls = np.asarray(config["parameters"]["L_list"], dtype=float)
        slope, intercept = np.polyfit(1.0 / Ls, np.asarray(valid), 1)
        extrapolation = {
            "method": "linear_1_over_L_diagnostic_only",
            "p_c": float(intercept),
            "slope": float(slope),
            "scientific_use": "diagnostic_only",
        }
    return {
        "boundary_estimand": {
            "k_v": "component intersects z=0 and z=L-1",
            "k_h": "component intersects x=0 and x=L-1 across the full volume",
        },
        "width_estimator": estimator,
        "all_primary_width_fits_valid": len(valid) == len(measured),
        "all_configured_width_grids_bracketed": (
            len(valid) == len(measured)
            if estimator == "adjacent_linear_smoke_diagnostic"
            else None
        ),
        "L": measured,
        "raw_manifest": raw_manifest,
        "extrapolation": extrapolation,
    }


def _validate_raw_npz(
    path: Path,
    *,
    config_sha256: str,
    L: int,
    seeds: np.ndarray,
    masses: np.ndarray,
    chis: np.ndarray,
    pinfs: np.ndarray,
    occupied_sites: np.ndarray,
    sizes: list[np.ndarray],
) -> None:
    expected_keys = {
        "config_sha256",
        "L",
        "seeds",
        "masses",
        "chis",
        "pinfs",
        "occupied_sites",
        *(f"sizes_{index:05d}" for index in range(len(sizes))),
    }
    with np.load(path, allow_pickle=False) as archive:
        if set(archive.files) != expected_keys:
            raise RuntimeError(f"raw NPZ key schema mismatch for L={L}")
        if str(archive["config_sha256"].item()) != config_sha256:
            raise RuntimeError(f"raw NPZ config hash mismatch for L={L}")
        if int(archive["L"].item()) != L:
            raise RuntimeError(f"raw NPZ L mismatch for L={L}")
        vector_expectations = {
            "seeds": (np.asarray(seeds, dtype=np.int64), np.dtype("<i8")),
            "masses": (masses, np.dtype("<i8")),
            "chis": (chis, np.dtype("<f8")),
            "pinfs": (pinfs, np.dtype("<f8")),
            "occupied_sites": (occupied_sites, np.dtype("<i8")),
        }
        for key, (expected, dtype) in vector_expectations.items():
            actual = archive[key]
            if actual.dtype != dtype or actual.shape != expected.shape:
                raise RuntimeError(f"raw NPZ {key} dtype/shape mismatch for L={L}")
            if not np.array_equal(actual, expected):
                raise RuntimeError(f"raw NPZ {key} values changed for L={L}")
        for index, expected in enumerate(sizes):
            actual = archive[f"sizes_{index:05d}"]
            if actual.dtype != np.dtype("<i8") or actual.ndim != 1:
                raise RuntimeError(f"raw NPZ sizes_{index:05d} must be flat little-endian int64")
            if not np.array_equal(actual, expected):
                raise RuntimeError(f"raw NPZ sizes_{index:05d} values changed")
            if actual.size == 0:
                raise RuntimeError(f"raw NPZ sizes_{index:05d} is unexpectedly empty")
            if np.any(actual <= 0) or np.any(np.diff(actual) > 0):
                raise RuntimeError(f"raw NPZ sizes_{index:05d} is not positive/non-increasing")
            if int(actual.sum()) != int(occupied_sites[index]):
                raise RuntimeError(f"raw NPZ sizes_{index:05d} does not sum to occupied sites")


def _save_raw_realizations(
    output_dir: Path,
    config_sha256: str,
    L: int,
    seeds: list[int],
    masses: np.ndarray,
    chis: np.ndarray,
    pinfs: np.ndarray,
    occupied_sites: np.ndarray,
    sizes: list[np.ndarray],
) -> dict:
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    target = raw_dir / f"L{L}_realizations.npz"
    if target.exists():
        raise FileExistsError(f"refusing to overwrite raw artifact: {target}")
    payload = {
        "config_sha256": np.asarray(config_sha256),
        "L": np.asarray(L),
        "seeds": np.asarray(seeds, dtype=np.int64),
        "masses": masses,
        "chis": chis,
        "pinfs": pinfs,
        "occupied_sites": occupied_sites,
    }
    for index, values in enumerate(sizes):
        payload[f"sizes_{index:05d}"] = values
    with target.open("wb") as handle:
        np.savez_compressed(handle, **payload)
        handle.flush()
        os.fsync(handle.fileno())
    _validate_raw_npz(
        target,
        config_sha256=config_sha256,
        L=L,
        seeds=seeds,
        masses=masses,
        chis=chis,
        pinfs=pinfs,
        occupied_sites=occupied_sites,
        sizes=sizes,
    )
    return {
        "path": str(target.relative_to(output_dir)).replace("\\", "/"),
        "bytes": target.stat().st_size,
        "sha256": sha256_file(target),
        "n_realizations": len(seeds),
        "n_cluster_arrays": len(sizes),
    }


def measure_exponents(config: dict, output_dir: Path, config_sha256: str) -> tuple[dict, dict]:
    params = config["parameters"]
    p_c = float(params["p_c"])
    per_L = {}
    raw_manifest = {}
    for L in params["L_list"]:
        n_target = int(params["n_real"][str(L)])
        src, dst, N = pe.cubic_lattice_3d(int(L))
        label = cell_label(config, int(L), "exp")
        masses = np.empty(n_target, dtype=np.int64)
        chis = np.empty(n_target, dtype=np.float64)
        pinfs = np.empty(n_target, dtype=np.float64)
        occupied_sites = np.empty(n_target, dtype=np.int64)
        sizes = []
        seeds = []
        for realization in range(n_target):
            seed = realization_seed(config, int(L), 0, realization)
            result = pe.run_span_cell_edges(
                src,
                dst,
                N,
                int(L),
                p_c,
                1,
                seed,
                label,
                semantics="site",
                want_largest_mass=True,
                want_stats=True,
                want_cluster_sizes=True,
                ndim=3,
            )
            cluster_arrays = result.get("cluster_sizes", [])
            if len(cluster_arrays) != 1 or not isinstance(cluster_arrays[0], np.ndarray):
                raise RuntimeError("cluster_sizes contract is not one flat array per realization")
            cluster_sizes = np.asarray(cluster_arrays[0], dtype=np.int64)
            if (
                cluster_sizes.ndim != 1
                or cluster_sizes.size == 0
                or np.any(cluster_sizes <= 0)
                or np.any(np.diff(cluster_sizes) > 0)
            ):
                raise RuntimeError("cluster sizes must be a nonempty positive non-increasing 1-D array")
            size_sum = int(cluster_sizes.sum())
            occupied_sites[realization] = size_sum
            masses[realization] = int(result["masses"][0])
            chis[realization] = (
                float(np.square(cluster_sizes.astype(float)).sum() / size_sum)
                if size_sum > 0 else 0.0
            )
            pinfs[realization] = masses[realization] / float(N)
            sizes.append(cluster_sizes)
            seeds.append(seed)
        if len(masses) != n_target or len(sizes) != n_target:
            raise RuntimeError("effective realization count does not match config")
        per_L[str(L)] = {
            "masses": masses,
            "chis": chis,
            "pinfs": pinfs,
            "occupied_sites": occupied_sites,
            "sizes": sizes,
            "seeds": seeds,
        }
        raw_manifest[str(L)] = _save_raw_realizations(
            output_dir,
            config_sha256,
            int(L),
            seeds,
            masses,
            chis,
            pinfs,
            occupied_sites,
            sizes,
        )
        _atomic_json(
            output_dir / "raw_manifest.json",
            {"config_sha256": config_sha256, "artifacts": raw_manifest},
            overwrite=True,
        )
        print(
            f"[QP008-REPAIR] exponents L={L} n={n_target} complete",
            flush=True,
        )
    return per_L, raw_manifest


def bootstrap_slope_ragged(
    logx: np.ndarray,
    rows: list[np.ndarray],
    draws: int,
    label: str,
    seed: int,
) -> np.ndarray:
    generator = pe.rng(label, seed)
    values = np.empty(int(draws), dtype=float)
    for draw in range(int(draws)):
        means = []
        for index, row in enumerate(rows):
            sample = row[generator.integers(0, len(row), size=len(row))]
            means.append(sample.mean())
        slope, _ = np.polyfit(logx, np.log(np.asarray(means)), 1)
        values[draw] = slope
    return values


def _tau_point(pooled: np.ndarray, s_grid: np.ndarray) -> dict | None:
    sorted_sizes = np.sort(np.asarray(pooled, dtype=np.int64))
    n_gt = sorted_sizes.size - np.searchsorted(
        sorted_sizes, s_grid, side="right"
    )
    keep = n_gt >= 3
    if int(keep.sum()) < 20:
        return None
    x = np.log(s_grid[keep].astype(float))
    y = np.log(n_gt[keep].astype(float))
    weights = np.sqrt(n_gt[keep].astype(float))
    design = np.vstack([np.ones_like(x), x]).T
    coefficient, *_ = np.linalg.lstsq(
        design * weights[:, None], y * weights, rcond=None
    )
    residual = y - design @ coefficient
    covariance = np.linalg.inv(
        design.T @ (np.diag(weights**2) @ design)
    )
    return {
        "tau": float(1.0 - coefficient[1]),
        "slope_se": float(np.sqrt(covariance[1, 1])),
        "chi2_red": float(
            np.sum((residual * weights) ** 2) / max(len(x) - 2, 1)
        ),
        "n_fit_points": int(keep.sum()),
    }


def fit_tau_realization_bootstrap(
    tails: list[np.ndarray],
    fit_range: tuple[int, int],
    draws: int,
    label: str,
    seed: int,
) -> dict:
    usable = [np.asarray(values, dtype=np.int64) for values in tails if len(values)]
    if not usable:
        return {"tau": None, "status": "INSUFFICIENT_NONEMPTY_TAILS"}
    s_grid = np.unique(
        np.geomspace(float(fit_range[0]), float(fit_range[1]), 250).astype(np.int64)
    )
    pooled = np.concatenate(usable)
    point = _tau_point(pooled, s_grid)
    generator = pe.rng(label, seed)
    estimates = []
    for _ in range(int(draws)):
        indices = generator.integers(0, len(usable), size=len(usable))
        sample = np.concatenate([usable[int(index)] for index in indices])
        fit = _tau_point(sample, s_grid)
        if fit is not None:
            estimates.append(fit["tau"])
    estimates = np.asarray(estimates, dtype=float)
    return {
        "status": "FITTED" if point is not None else "POINT_FIT_FAILED",
        "tau": point["tau"] if point else None,
        "slope_se": point["slope_se"] if point else None,
        "chi2_red": point["chi2_red"] if point else None,
        "n_fit_points": point["n_fit_points"] if point else 0,
        "n_realizations_total": len(tails),
        "n_realizations_nonempty_tail": len(usable),
        "n_clusters_pooled": int(pooled.size),
        "bootstrap_requested": int(draws),
        "bootstrap_accepted": int(estimates.size),
        "bootstrap_failed": int(draws - estimates.size),
        "bootstrap_mean": float(estimates.mean()) if estimates.size else None,
        "bootstrap_se": (
            float(estimates.std(ddof=1)) if estimates.size > 1 else None
        ),
        "fit_range": [int(fit_range[0]), int(fit_range[1])],
        "uncertainty_unit": "realization",
    }


def summarize_exponents(config: dict, measured: dict) -> dict:
    params = config["parameters"]
    L_list = params["L_list"]
    logx = np.log(np.asarray(L_list, dtype=float))
    masses = [measured[str(L)]["masses"] for L in L_list]
    chis = [measured[str(L)]["chis"] for L in L_list]
    pinfs = [measured[str(L)]["pinfs"] for L in L_list]
    draws = int(params["bootstrap_draws"])
    bootstrap_label = params["bootstrap_label"]
    D_f_draws = bootstrap_slope_ragged(
        logx, masses, draws, f"{bootstrap_label}-df", int(config["seed"])
    )
    gamma_draws = bootstrap_slope_ragged(
        logx, chis, draws, f"{bootstrap_label}-gamma", int(config["seed"])
    )
    beta_draws = -bootstrap_slope_ragged(
        logx, pinfs, draws, f"{bootstrap_label}-beta", int(config["seed"])
    )
    predictions = params["predictions"]["exponents"]
    output = {}
    for key, draws_value in (
        ("Df", D_f_draws),
        ("gamma_nu", gamma_draws),
        ("beta_nu", beta_draws),
    ):
        expected = float(predictions[key]["expected"])
        tolerance = float(predictions[key]["tol"])
        mean = float(draws_value.mean())
        output[key] = {
            "mean": mean,
            "bootstrap_se": float(draws_value.std(ddof=1)),
            "bootstrap_requested": draws,
            "bootstrap_accepted": int(draws_value.size),
            "expected": expected,
            "tolerance": tolerance,
            "absolute_deviation": abs(mean - expected),
            "point_in_tolerance": abs(mean - expected) <= tolerance,
            "n_by_L": {
                str(L): len(measured[str(L)]["masses"]) for L in L_list
            },
        }
    tau_L = int(params["tau_L"])
    tails = [
        np.asarray(values[1:], dtype=np.int64)
        for values in measured[str(tau_L)]["sizes"]
    ]
    output["tau"] = fit_tau_realization_bootstrap(
        tails,
        tuple(map(int, params["tau_fit_range"])),
        draws,
        f"{bootstrap_label}-tau-realization",
        int(config["seed"]),
    )
    output["tau"]["tau_L"] = tau_L
    return output


def _atomic_json(path: Path, payload: dict, *, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite result: {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(
            payload,
            handle,
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)

    started = time.time()
    config_path = args.config.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    historical_results = (HERE / "RESULTS").resolve()
    if output_dir == historical_results or historical_results in output_dir.parents:
        raise ConfigError("refusing to write repaired output inside historical RESULTS/")
    if output_dir.exists():
        raise ConfigError(f"refusing to overwrite existing output directory: {output_dir}")

    config, config_sha256 = load_config(config_path)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = output_dir.parent / f".{output_dir.name}.staging-{os.getpid()}-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        print(
            f"[QP008-REPAIR] experiment={config['experiment_id']} "
            f"config_sha256={config_sha256[:16]}...",
            flush=True,
        )
        width = measure_width(config, staging, config_sha256)
        measured, raw_manifest = measure_exponents(
            config, staging, config_sha256
        )
        exponent_summary = summarize_exponents(config, measured)

        params = config["parameters"]
        width_complete = bool(width["all_primary_width_fits_valid"])
        tau_complete = exponent_summary["tau"].get("status") == "FITTED"
        bootstrap_complete = all(
            exponent_summary[name]["bootstrap_accepted"]
            == exponent_summary[name]["bootstrap_requested"]
            for name in ("Df", "gamma_nu", "beta_nu")
        )
        required_analysis_complete = width_complete and tau_complete and bootstrap_complete
        status = (
            "INFRASTRUCTURE_SMOKE_PARTIAL"
            if params["purpose"] == "infrastructure_smoke" and not required_analysis_complete
            else (
                "INFRASTRUCTURE_SMOKE_COMPLETE"
                if params["purpose"] == "infrastructure_smoke"
                else "MEASUREMENTS_COMPLETE_AWAITING_EXTERNAL_C7"
            )
        )
        result_payload = {
            "schema": "q-p008/audit-repair-result/v2",
            "experiment": config["experiment_id"],
            "question": config["question_id"],
            "hypothesis": config["hypothesis_id"],
            "purpose": params["purpose"],
            "status": status,
            "required_analysis_complete": required_analysis_complete,
            "science_authorized": False,
            "scientific_result": None,
            "decision": "INCONCLUSIVE",
            "decision_reason": "This runner does not execute or ingest the independent C7 gate.",
            "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "config_path": str(config_path),
            "config_sha256": config_sha256,
            "engine_path": str(Path(pe.__file__).resolve()),
            "engine_sha256": sha256_file(Path(pe.__file__).resolve()),
            "runner_path": str(Path(__file__).resolve()),
            "runner_sha256": sha256_file(Path(__file__).resolve()),
            "environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "numpy": np.__version__,
                "scipy": scipy.__version__,
            },
            "p_c_canonical": float(params["p_c"]),
            "p_c_used_for_exponents": float(params["p_c"]),
            "width": width,
            "raw_manifest": raw_manifest,
            "exponents": exponent_summary,
            "elapsed_seconds": time.time() - started,
            "novelty_claim": False,
        }
        record = make_experiment_json(
            config["experiment_id"],
            config["question_id"],
            config["hypothesis_id"],
            seed=int(config["seed"]),
            parameters=params,
            result=result_payload,
            extra={
                "prereg_schema": config["schema"],
                "runner_path": str(Path(__file__).resolve()),
                "engine_path": str(Path(pe.__file__).resolve()),
            },
        )
        canonical_report = verify_experiment_result_hash(record)
        if not canonical_report["valid"]:
            raise RuntimeError(f"canonical result self-check failed: {canonical_report}")
        result_path = staging / f"{config['experiment_id']}_results.json"
        _atomic_json(result_path, record)
        exact_report = {
            "schema": "q-p008/exact-result-sidecar/v1",
            "result_filename": result_path.name,
            "size_bytes": result_path.stat().st_size,
            "sha256": sha256_file(result_path),
            "hash_scope": "exact_artifact_bytes",
        }
        _atomic_json(
            staging / f"{config['experiment_id']}_results.sha256.json",
            exact_report,
        )
        os.replace(staging, output_dir)
        final_result_path = output_dir / result_path.name
        print(
            f"[QP008-REPAIR] wrote {final_result_path}; status={status}; "
            "decision=INCONCLUSIVE until independent C7 integration",
            flush=True,
        )
        return 0 if required_analysis_complete else 3
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
