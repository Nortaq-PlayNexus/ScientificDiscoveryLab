#!/usr/bin/env python3
"""EXP-0016: topology-measurement definition experiment.

The script deliberately reports several observables instead of pretending that
one integer is the vortex count.  It is self-contained and does not import the
historical sandbox or the EXP-0015 detector implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage, optimize

LAB = Path(__file__).resolve().parents[4]
EXP_DIR = Path(__file__).resolve().parents[1]
RESULTS = EXP_DIR / "RESULTS"
CONFIG = EXP_DIR / "CONFIG"
RESULTS.mkdir(parents=True, exist_ok=True)

FOV_UM = 64.0
WAVELENGTH_NM = 694.3
GRIDS = (32, 48, 64, 96, 128, 192, 256)
SHIFTS = (0.0, 0.25, 0.5, 0.75)
SINGLE_CHARGES = (-2, -1, 1, 2)
POSITION_MODES = ("exact_pixel", "half_pixel", "quarter_pixel")
SEPARATIONS = (4.0, 8.0, 16.0, 32.0)
CLOSE_SEPARATIONS = (2.0, 4.0, 6.0, 8.0, 12.0, 16.0)
CORE_SIGMAS = (1.0, 2.0, 4.0, 8.0)
PROP_Z = (0.0, 160.0, 240.0, 280.0, 320.0, 400.0, 640.0, 1280.0)
DETECTORS = ("raw_winding", "clustered_winding", "circular_contour", "jacobian_locator")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def jsonable(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, np.ndarray):
        return jsonable(x.tolist())
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating,)):
        x = float(x)
    if isinstance(x, float):
        return x if math.isfinite(x) else None
    if isinstance(x, (str, int, bool)) or x is None:
        return x
    return str(x)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(jsonable(value), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def cell_grid(shape: tuple[int, int], fov_um: float = FOV_UM) -> tuple[np.ndarray, np.ndarray, float, float]:
    h, w = shape
    dy = fov_um / h
    dx = fov_um / w
    y = (np.arange(h, dtype=float) + 0.5) * dy
    x = (np.arange(w, dtype=float) + 0.5) * dx
    yy = y[:, None] * np.ones((1, w))
    xx = x[None, :] * np.ones((h, 1))
    return yy, xx, dx, dy


def truth_positions(shape: tuple[int, int], family: str, charge: int = 1, separation_um: float = 8.0, position_mode: str = "exact_pixel", fov_um: float = FOV_UM) -> list[dict[str, Any]]:
    h, w = shape
    _, _, dx, dy = cell_grid(shape, fov_um)
    i0 = h // 2
    j0 = w // 2
    cx = (j0 + 0.5) * dx
    cy = (i0 + 0.5) * dy
    if position_mode == "half_pixel":
        cx += dx / 2
        cy += dy / 2
    elif position_mode == "quarter_pixel":
        cx += dx / 4
        cy += dy / 4
    if family == "single":
        return [{"x_um": cx, "y_um": cy, "charge": int(charge)}]
    if family == "opposite_pair":
        return [
            {"x_um": cx - separation_um / 2, "y_um": cy, "charge": 1},
            {"x_um": cx + separation_um / 2, "y_um": cy, "charge": -1},
        ]
    if family == "same_pair":
        return [
            {"x_um": cx - separation_um / 2, "y_um": cy, "charge": int(charge)},
            {"x_um": cx + separation_um / 2, "y_um": cy, "charge": int(charge)},
        ]
    if family == "four_lattice":
        return [
            {"x_um": cx - separation_um, "y_um": cy - separation_um, "charge": 1},
            {"x_um": cx + separation_um, "y_um": cy - separation_um, "charge": -1},
            {"x_um": cx - separation_um, "y_um": cy + separation_um, "charge": -1},
            {"x_um": cx + separation_um, "y_um": cy + separation_um, "charge": 1},
        ]
    raise ValueError(f"unknown truth family: {family}")


def make_field(
    shape: tuple[int, int],
    truth: list[dict[str, Any]],
    fov_um: float = FOV_UM,
    core_sigma_um: float = 2.0,
    envelope_sigma_um: float = 22.0,
    hard_zero: bool = True,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Analytical complex field with known phase singularities.

    A positive radial core factor supplies a physical-looking amplitude zero;
    the phase is the exact sum of integer winding terms.  A hard-zero flag
    sets a sample exactly on a singularity to complex zero, while a small
    numerical regularizer keeps phase defined at off-centre samples.
    """
    yy, xx, dx, dy = cell_grid(shape, fov_um)
    field = np.ones(shape, dtype=np.complex128)
    regularizer = max(1e-6, 0.02 * min(dx, dy))
    for item in truth:
        x0, y0, q = float(item["x_um"]), float(item["y_um"]), int(item["charge"])
        r2 = (xx - x0) ** 2 + (yy - y0) ** 2
        theta = np.arctan2(yy - y0, xx - x0)
        # A finite-width amplitude depression gives a physically plausible
        # dark core without making the entire field vanish away from the
        # singularity. The phase still has the exact requested integer winding.
        core = 1.0 - 0.98 * np.exp(-r2 / (2.0 * core_sigma_um**2))
        if abs(q) > 1:
            core = core ** (abs(q) / 2.0)
        field *= core * np.exp(1j * q * theta)
        if hard_zero:
            exact = (np.abs(xx - x0) < 1e-10) & (np.abs(yy - y0) < 1e-10)
            field[exact] = 0.0
    envelope = np.exp(-((xx - fov_um / 2) ** 2 + (yy - fov_um / 2) ** 2) / (2.0 * envelope_sigma_um**2))
    field *= envelope
    # Global scale has no effect on winding; avoid underflow for close cores.
    scale = np.max(np.abs(field))
    if scale > 0:
        field /= scale
    meta = {
        "shape": list(shape), "fov_um": fov_um, "pixel_um": [dy, dx],
        "core_sigma_um": core_sigma_um, "envelope_sigma_um": envelope_sigma_um,
        "hard_zero": hard_zero, "truth_count": len(truth),
        "truth_signed_charge": int(sum(t["charge"] for t in truth)),
        "truth_absolute_charge": int(sum(abs(t["charge"]) for t in truth)),
        "truth": truth,
    }
    return field, meta


def asm(field: np.ndarray, z_um: float, dx_um: float, dy_um: float, wavelength_nm: float = WAVELENGTH_NM) -> np.ndarray:
    if z_um == 0:
        return field.copy()
    fx = np.fft.fftfreq(field.shape[1], d=dx_um * 1e-6)
    fy = np.fft.fftfreq(field.shape[0], d=dy_um * 1e-6)
    kx, ky = np.meshgrid(2 * np.pi * fx, 2 * np.pi * fy, indexing="xy")
    k = 2 * np.pi / (wavelength_nm * 1e-9)
    kz2 = k * k - kx * kx - ky * ky
    h = np.zeros(field.shape, dtype=np.complex128)
    mask = kz2 >= 0
    h[mask] = np.exp(1j * np.sqrt(kz2[mask]) * (z_um * 1e-6))
    return np.fft.ifft2(np.fft.fft2(field) * h)


def principal(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.angle(np.exp(1j * (a - b)))


def winding_cells(field: np.ndarray) -> np.ndarray:
    p = np.angle(field)
    a, b, c, d = p[:-1, :-1], p[:-1, 1:], p[1:, 1:], p[1:, :-1]
    curl = principal(b, a) + principal(c, b) + principal(d, c) + principal(a, d)
    return np.rint(curl / (2 * np.pi)).astype(np.int8)


def cell_records(cells: np.ndarray, field: np.ndarray) -> list[dict[str, Any]]:
    intensity = np.abs(field) ** 2
    core = 0.25 * (intensity[:-1, :-1] + intensity[:-1, 1:] + intensity[1:, :-1] + intensity[1:, 1:])
    yy, xx = np.where(cells != 0)
    return [{"x": float(x + 0.5), "y": float(y + 0.5), "charge": int(cells[y, x]), "intensity": float(core[y, x])} for y, x in zip(yy, xx)]


def component_records(cells: np.ndarray, field: np.ndarray) -> list[dict[str, Any]]:
    intensity = np.abs(field) ** 2
    core = 0.25 * (intensity[:-1, :-1] + intensity[:-1, 1:] + intensity[1:, :-1] + intensity[1:, 1:])
    result: list[dict[str, Any]] = []
    for sign in (-1, 1):
        mask = cells == sign
        if not np.any(mask):
            continue
        labels, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=np.int8))
        for label in range(1, count + 1):
            yy, xx = np.where(labels == label)
            result.append({"x": float(np.mean(xx + 0.5)), "y": float(np.mean(yy + 0.5)), "charge": int(np.sum(cells[yy, xx])), "intensity": float(np.mean(core[yy, xx])), "n_cells": int(len(yy))})
    return result


def bilinear_complex(field: np.ndarray, y: float, x: float) -> complex:
    h, w = field.shape
    if y < 0 or x < 0 or y > h - 1 or x > w - 1:
        return 0j
    y0, x0 = int(math.floor(y)), int(math.floor(x))
    y1, x1 = min(y0 + 1, h - 1), min(x0 + 1, w - 1)
    fy, fx = y - y0, x - x0
    return complex(
        (1 - fy) * (1 - fx) * field[y0, x0]
        + (1 - fy) * fx * field[y0, x1]
        + fy * (1 - fx) * field[y1, x0]
        + fy * fx * field[y1, x1]
    )


def contour_records(field: np.ndarray, radius: float = 2.0, n_points: int = 32, max_candidates: int = 200) -> list[dict[str, Any]]:
    intensity = np.abs(field) ** 2
    # Seed from the darkest samples rather than requiring a sampled local
    # minimum. A true subpixel zero often has no discrete local minimum.
    yy, xx = np.where(np.isfinite(intensity))
    if len(yy) == 0:
        return []
    order = np.argsort(intensity[yy, xx])
    yy, xx = yy[order][: min(len(order), max_candidates * 2)], xx[order][: min(len(order), max_candidates * 2)]
    selected: list[tuple[float, float]] = []
    records: list[dict[str, Any]] = []
    theta = np.arange(n_points, dtype=float) * 2 * np.pi / n_points
    for y, x in zip(yy.tolist(), xx.tolist()):
        if y < radius + 1 or x < radius + 1 or y >= field.shape[0] - radius - 1 or x >= field.shape[1] - radius - 1:
            continue
        if any((y - sy) ** 2 + (x - sx) ** 2 < (1.5 * radius) ** 2 for sy, sx in selected):
            continue
        values = [bilinear_complex(field, y + radius * math.sin(t), x + radius * math.cos(t)) for t in theta]
        if any(abs(v) < 1e-14 for v in values):
            continue
        phases = np.angle(values)
        winding = int(np.rint(np.sum(principal(np.roll(phases, -1), phases)) / (2 * np.pi)))
        if abs(winding) < 1:
            continue
        selected.append((float(y), float(x)))
        yield_record = {"x": float(x), "y": float(y), "charge": winding, "intensity": float(intensity[y, x]), "method": "circular_contour"}
        records.append(yield_record)
        if len(records) >= max_candidates:
            break
    return records


def jacobian_records(field: np.ndarray, radius: int = 2, max_candidates: int = 200) -> list[dict[str, Any]]:
    """Approximate complex-zero locator using a local linear/Jacobian fit."""
    intensity = np.abs(field) ** 2
    # Seed from the darkest samples rather than requiring a sampled local
    # minimum. A true subpixel zero often has no discrete local minimum.
    yy, xx = np.where(np.isfinite(intensity))
    if len(yy) == 0:
        return []
    order = np.argsort(intensity[yy, xx])
    yy, xx = yy[order][: min(len(order), max_candidates * 2)], xx[order][: min(len(order), max_candidates * 2)]
    records: list[dict[str, Any]] = []
    selected: list[tuple[float, float]] = []
    offsets = np.arange(-radius, radius + 1, dtype=float)
    oy, ox = np.meshgrid(offsets, offsets, indexing="ij")
    design = np.column_stack((np.ones(oy.size), ox.ravel(), oy.ravel()))
    for y, x in zip(yy.tolist(), xx.tolist()):
        if y < radius + 1 or x < radius + 1 or y >= field.shape[0] - radius - 1 or x >= field.shape[1] - radius - 1:
            continue
        patch = field[y - radius:y + radius + 1, x - radius:x + radius + 1].ravel()
        real_coeff, _, _, _ = np.linalg.lstsq(design, patch.real, rcond=None)
        imag_coeff, _, _, _ = np.linalg.lstsq(design, patch.imag, rcond=None)
        ar, br, cr = real_coeff
        ai, bi, ci = imag_coeff
        determinant = float(br * ci - bi * cr)
        if abs(determinant) > 1e-12:
            zx = float((-ar * ci + cr * ai) / determinant)
            zy = float((-br * ai + ar * bi) / determinant)
        else:
            zx = 0.0
            zy = 0.0
        # Recompute the local phase winding around the candidate pixel; the
        # fitted zero is retained as a subpixel position when in-bounds.
        cy, cx = y + zy, x + zx
        if cy < radius + 1 or cx < radius + 1 or cy >= field.shape[0] - radius - 1 or cx >= field.shape[1] - radius - 1:
            continue
        vals = []
        for t in np.arange(16) * 2 * np.pi / 16:
            vals.append(bilinear_complex(field, cy + radius * math.sin(t), cx + radius * math.cos(t)))
        if any(abs(v) < 1e-14 for v in vals):
            continue
        ph = np.angle(vals)
        q = int(np.rint(np.sum(principal(np.roll(ph, -1), ph)) / (2 * np.pi)))
        if abs(q) < 1:
            continue
        if abs(zx) <= radius and abs(zy) <= radius and not any((cx - sx) ** 2 + (cy - sy) ** 2 < (1.5 * radius) ** 2 for sx, sy in selected):
            selected.append((float(cx), float(cy)))
            records.append({"x": float(cx), "y": float(cy), "charge": q, "intensity": float(abs(bilinear_complex(field, cy, cx)) ** 2), "method": "jacobian_locator"})
        if len(records) >= max_candidates:
            break
    return records


def records_for(field: np.ndarray, detector: str) -> tuple[list[dict[str, Any]], int]:
    cells = winding_cells(field)
    if detector == "raw_winding":
        return cell_records(cells, field), int(np.count_nonzero(cells))
    if detector == "clustered_winding":
        return component_records(cells, field), int(np.count_nonzero(cells))
    if detector == "circular_contour":
        return contour_records(field), 0
    if detector == "jacobian_locator":
        return jacobian_records(field), 0
    raise ValueError(detector)


def match(records: list[dict[str, Any]], truth: list[dict[str, Any]], shape: tuple[int, int], fov_um: float = FOV_UM, tolerance_px: float = 2.0) -> dict[str, Any]:
    if not truth:
        return {}
    _, _, dx, dy = cell_grid(shape, fov_um)
    true_xy = np.array([[t["x_um"] / dx - 0.5, t["y_um"] / dy - 0.5] for t in truth])
    pred_xy = np.array([[r["x"], r["y"]] for r in records]) if records else np.empty((0, 2))
    if len(pred_xy) == 0:
        return {"true_positive": 0, "false_positive": 0, "false_negative": len(truth), "charge_correct": 0, "localization_rmse_px": None}
    cost = np.linalg.norm(true_xy[:, None, :] - pred_xy[None, :, :], axis=2)
    ri, ci = optimize.linear_sum_assignment(cost)
    tp = charge_ok = 0; errors = []
    for i, j in zip(ri, ci):
        d = float(cost[i, j])
        if d <= tolerance_px:
            tp += 1; errors.append(d)
            if int(records[j]["charge"]) == int(truth[i]["charge"]): charge_ok += 1
    return {"true_positive": tp, "false_positive": len(records) - tp, "false_negative": len(truth) - tp, "charge_correct": charge_ok, "localization_rmse_px": float(np.sqrt(np.mean(np.square(errors)))) if errors else None}


def summarize(field: np.ndarray, detector: str, truth: list[dict[str, Any]], shape: tuple[int, int], fov_um: float = FOV_UM) -> dict[str, Any]:
    records, winding_cell_count = records_for(field, detector)
    q = np.array([int(r["charge"]) for r in records], dtype=int)
    absq = int(np.abs(q).sum()) if len(q) else 0
    signed = int(q.sum()) if len(q) else 0

    # A raw winding cell is not itself a singularity location.  For the raw
    # estimator, define its location proxy by same-sign connected components;
    # retain the raw cell count separately so charge splitting is visible.
    if detector == "raw_winding":
        location_records = component_records(winding_cells(field), field)
        estimator_unit = "same_sign_winding_components"
    else:
        location_records = records
        estimator_unit = {
            "clustered_winding": "same_sign_winding_components",
            "circular_contour": "accepted_contours",
            "jacobian_locator": "accepted_complex_zero_fits",
        }[detector]
    location_q = np.array([int(r["charge"]) for r in location_records], dtype=int)
    location_abs = int(np.abs(location_q).sum()) if len(location_q) else 0
    location_signed = int(location_q.sum()) if len(location_q) else 0
    component_count = len(location_records)
    truth_abs = int(sum(abs(t["charge"]) for t in truth))
    truth_signed = int(sum(t["charge"] for t in truth))
    normalizer = max(1, max((abs(t["charge"]) for t in truth), default=1))
    truth_match = match(location_records, truth, shape, fov_um)
    result: dict[str, Any] = {
        "detector": detector, "estimator_unit": estimator_unit,
        "record_count": len(records), "location_count": component_count,
        "component_count": component_count, "winding_cell_count": winding_cell_count,
        "raw_nonzero_cell_count": len(records) if detector == "raw_winding" else None,
        "location_absolute_charge": location_abs, "location_signed_charge": location_signed,
        "absolute_charge": absq, "signed_charge": signed,
        "charge_mass_units": absq / normalizer,
        "charge_normalized_count": absq / normalizer,
        "truth_count": len(truth), "truth_absolute_charge": truth_abs,
        "truth_signed_charge": truth_signed,
        "absolute_charge_error": abs(absq - truth_abs),
        "signed_charge_error": abs(signed - truth_signed),
        "location_absolute_charge_error": abs(location_abs - truth_abs),
        "location_signed_charge_error": abs(location_signed - truth_signed),
        "location_count_error": abs(component_count - len(truth)),
        "false_positive": truth_match.get("false_positive"),
        "false_negative": truth_match.get("false_negative"),
        "localization_error_px": truth_match.get("localization_rmse_px"),
        "localization_error": truth_match.get("localization_rmse_px"),
    }
    result["truth_match"] = truth_match
    if detector == "raw_winding":
        result["cell_truth_match"] = match(records, truth, shape, fov_um)
    return result


def row(field: np.ndarray, detector: str, truth: list[dict[str, Any]], shape: tuple[int, int], **tags: Any) -> dict[str, Any]:
    out = dict(tags); out.update(summarize(field, detector, truth, shape)); return out


def run_calibration() -> dict[str, Any]:
    start = time.time(); rows = []
    for n in (32, 64, 128, 256):
        for q in SINGLE_CHARGES:
            for mode in POSITION_MODES:
                truth = truth_positions((n, n), "single", charge=q, position_mode=mode)
                field, meta = make_field((n, n), truth)
                for detector in DETECTORS:
                    rows.append(row(field, detector, truth, (n, n), stage="calibration", family="single", charge=q, grid=n, position_mode=mode, core_sigma_um=2.0, z_um=0.0))
    return {"experiment": "EXP-0016", "stage": "calibration", "timestamp_utc": now(), "rows": rows, "parameters": {"grids": (32, 64, 128, 256), "charges": SINGLE_CHARGES, "position_modes": POSITION_MODES, "detectors": DETECTORS}, "runtime_s": time.time() - start}


def run_phase_diagram() -> dict[str, Any]:
    start = time.time(); rows = []
    for n in GRIDS:
        for q in SINGLE_CHARGES:
            for mode in POSITION_MODES:
                truth = truth_positions((n, n), "single", charge=q, position_mode=mode)
                for core in CORE_SIGMAS:
                    field, _ = make_field((n, n), truth, core_sigma_um=core)
                    for detector in DETECTORS:
                        rows.append(row(field, detector, truth, (n, n), stage="phase_diagram", family="single", charge=q, grid=n, position_mode=mode, separation_um=None, core_sigma_um=core, pixels_per_core=core / (FOV_UM / n), z_um=0.0))
        for sep in SEPARATIONS:
            truth = truth_positions((n, n), "opposite_pair", separation_um=sep, position_mode="exact_pixel")
            field, _ = make_field((n, n), truth, core_sigma_um=2.0)
            for detector in DETECTORS:
                rows.append(row(field, detector, truth, (n, n), stage="phase_diagram", family="opposite_pair", charge=0, grid=n, position_mode="exact_pixel", separation_um=sep, core_sigma_um=2.0, pixels_per_separation=sep / (FOV_UM / n), z_um=0.0))
        for sep in CLOSE_SEPARATIONS:
            truth = truth_positions((n, n), "opposite_pair", separation_um=sep, position_mode="half_pixel")
            field, _ = make_field((n, n), truth, core_sigma_um=2.0)
            for detector in DETECTORS:
                rows.append(row(field, detector, truth, (n, n), stage="phase_diagram", family="close_pair", charge=0, grid=n, position_mode="half_pixel", separation_um=sep, core_sigma_um=2.0, pixels_per_separation=sep / (FOV_UM / n), z_um=0.0))
        truth = truth_positions((n, n), "four_lattice", separation_um=8.0, position_mode="quarter_pixel")
        field, _ = make_field((n, n), truth, core_sigma_um=2.0)
        for detector in DETECTORS:
            rows.append(row(field, detector, truth, (n, n), stage="phase_diagram", family="four_lattice", charge=0, grid=n, position_mode="quarter_pixel", separation_um=16.0, core_sigma_um=2.0, pixels_per_separation=16.0 / (FOV_UM / n), z_um=0.0))
    return {"experiment": "EXP-0016", "stage": "phase_diagram", "timestamp_utc": now(), "rows": rows, "parameters": {"grids": GRIDS, "charges": SINGLE_CHARGES, "position_modes": POSITION_MODES, "separations": SEPARATIONS, "close_separations": CLOSE_SEPARATIONS, "core_sigmas": CORE_SIGMAS, "detectors": DETECTORS}, "runtime_s": time.time() - start}


def run_propagation() -> dict[str, Any]:
    start = time.time(); rows = []
    for n in (64, 128, 256):
        for mode in ("exact_pixel", "half_pixel"):
            truth = truth_positions((n, n), "opposite_pair", separation_um=8.0, position_mode=mode)
            field, _ = make_field((n, n), truth, core_sigma_um=2.0)
            _, _, dx, dy = cell_grid((n, n))
            for z in PROP_Z:
                out = asm(field, z, dx, dy)
                for detector in DETECTORS:
                    rows.append(row(out, detector, truth, (n, n), stage="propagation", family="close_pair", charge=0, grid=n, position_mode=mode, separation_um=8.0, core_sigma_um=2.0, z_um=z))
    return {"experiment": "EXP-0016", "stage": "propagation", "timestamp_utc": now(), "rows": rows, "parameters": {"grids": (64, 128, 256), "position_modes": ("exact_pixel", "half_pixel"), "z_um": PROP_Z, "detectors": DETECTORS}, "runtime_s": time.time() - start}


def run_nulls() -> dict[str, Any]:
    start = time.time(); rows = []
    for n in (64, 128, 256):
        yy, xx, dx, dy = cell_grid((n, n))
        fields = {
            "plane_wave": np.ones((n, n), dtype=np.complex128),
            "smooth_no_vortex": np.exp(1j * 0.02 * np.sin(2 * np.pi * xx / FOV_UM) * np.cos(2 * np.pi * yy / FOV_UM)),
            "matched_amplitude_random_phase": np.exp(1j * np.random.default_rng(1000 + n).uniform(-np.pi, np.pi, (n, n))),
        }
        for name, field in fields.items():
            for detector in DETECTORS:
                rows.append(row(field, detector, [], (n, n), stage="nulls", family=name, charge=0, grid=n, position_mode="none", separation_um=None, core_sigma_um=None, z_um=0.0))
    return {"experiment": "EXP-0016", "stage": "nulls", "timestamp_utc": now(), "rows": rows, "parameters": {"grids": (64, 128, 256), "detectors": DETECTORS}, "runtime_s": time.time() - start}


def environment() -> dict[str, Any]:
    import scipy
    return {"python": sys.version, "executable": sys.executable, "platform": platform.platform(), "numpy": np.__version__, "scipy": scipy.__version__}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("calibration", "phase_diagram", "propagation", "nulls", "all"), default="calibration")
    args = parser.parse_args()
    funcs = {"calibration": run_calibration, "phase_diagram": run_phase_diagram, "propagation": run_propagation, "nulls": run_nulls}
    stages = list(funcs) if args.stage == "all" else [args.stage]
    bundle: dict[str, Any] = {"experiment": "EXP-0016", "run_timestamp_utc": now(), "environment": environment(), "preregistration": str(CONFIG / "prereg_EXP-0016.json"), "stages": {}}
    for stage in stages:
        print(f"Starting {stage}...", flush=True)
        result = funcs[stage]()
        bundle["stages"][stage] = result
        path = RESULTS / f"{stage}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        write_json(path, result)
        print(f"Wrote {path} ({result['runtime_s']:.1f}s)", flush=True)
    write_json(RESULTS / "latest.json", bundle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
