#!/usr/bin/env python3
"""EXP-0015: discrete optical-vortex detection bias investigation.

This is a lab-native, self-contained NumPy/SciPy implementation.  It does not
import the historical sandbox detector or propagation code.  Historical claims
are inputs to the falsification program, not assumptions.

The script is intentionally staged.  A stage writes one JSON artifact and can
be rerun without changing the frozen protocol.  Raw complex fields are not
silently overwritten: each stage writes a new timestamped file plus a stable
``latest`` pointer only after successful completion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from scipy import ndimage, stats
from scipy.optimize import linear_sum_assignment

try:
    import torch
    TORCH_VERSION = torch.__version__
except Exception:  # pragma: no cover - optional architecture check
    torch = None
    TORCH_VERSION = None

LAB = Path(__file__).resolve().parents[4]
EXPERIMENT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = EXPERIMENT_DIR / "RESULTS"
CONFIG_DIR = EXPERIMENT_DIR / "CONFIG"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FOV_UM = 256.0
BASE_WAVELENGTH_NM = 694.3
REFERENCE_GRID = 2048
SEEDS = (42, 7, 123)
SHIFTS = (0.0, 0.1, 0.2, 0.25, 0.33, 0.5, 0.67, 0.75, 0.9)
Z_SWEEP_UM = (0.0, 20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 160.0,
              200.0, 240.0, 320.0, 400.0, 480.0, 560.0, 640.0, 720.0,
              800.0, 880.0, 960.0, 1040.0, 1120.0, 1200.0, 1280.0,
              1360.0, 1440.0, 1520.0, 1600.0)
WAVELENGTHS_NM = (405.0, 450.0, 488.0, 532.0, 589.0, 632.8, 650.0,
                  671.0, 694.3, 780.0, 850.0, 1064.0)
PADDING_FRACTIONS = (0.0, 0.25, 0.5, 1.0, 2.0, 3.0)
DETECTORS = (
    "raw_winding",
    "clustered_winding",
    "supported_clustered_winding",
    "local_minimum_contour",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_array(a: np.ndarray) -> str:
    return sha256_bytes(np.ascontiguousarray(a).tobytes())


def json_safe(value: Any) -> Any:
    """Convert NumPy values and non-finite values to strict JSON values."""
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return str(value)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(json_safe(payload), indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.write_text(text, encoding="utf-8")


def cell_coordinates(shape: tuple[int, int], fov_um: float = FOV_UM) -> tuple[np.ndarray, np.ndarray, float, float]:
    """Return cell-centre coordinates in pixels and micrometres.

    Cell centres are used so that grids with different N represent the same
    periodic physical domain without an endpoint-origin shift.
    """
    h, w = shape
    dy_um = fov_um / h
    dx_um = fov_um / w
    y_um = (np.arange(h, dtype=float) + 0.5) * dy_um
    x_um = (np.arange(w, dtype=float) + 0.5) * dx_um
    return y_um[:, None] * np.ones((1, w)), x_um[None, :] * np.ones((h, 1)), dx_um, dy_um


def physical_to_pixel(x_um: float, y_um: float, shape: tuple[int, int], fov_um: float = FOV_UM) -> tuple[float, float]:
    h, w = shape
    return x_um / (fov_um / w) - 0.5, y_um / (fov_um / h) - 0.5


def make_known_field(
    shape: tuple[int, int],
    case: str,
    seed: int = 42,
    fov_um: float = FOV_UM,
    wavelength_nm: float = BASE_WAVELENGTH_NM,
    shift_px: float = 0.0,
    amp_floor: float = 0.03,
    sigma_um: float = 55.0,
) -> tuple[np.ndarray, list[dict[str, float]], dict[str, Any]]:
    """Construct a continuous scalar field with analytically known vortices.

    Positions are physical coordinates.  ``shift_px`` translates the physical
    design relative to the computational grid, so no interpolation is needed
    for the direct-sampling control.
    """
    h, w = shape
    y_um, x_um, dx_um, dy_um = cell_coordinates(shape, fov_um)
    cx = fov_um / 2.0
    cy = fov_um / 2.0
    dx_shift = shift_px * dx_um
    dy_shift = shift_px * dy_um

    positions: list[tuple[float, float, int]] = []
    if case == "single_vortex":
        positions = [(cx + dx_shift, cy + dy_shift, 1)]
    elif case == "vortex_pair":
        positions = [
            (cx - 22.0 + dx_shift, cy + dy_shift, 1),
            (cx + 22.0 + dx_shift, cy + dy_shift, -1),
        ]
    elif case == "double_vortex":
        positions = [(cx + dx_shift, cy + dy_shift, 2)]
    elif case == "four_vortex_lattice":
        positions = [
            (cx - 28.0 + dx_shift, cy - 24.0 + dy_shift, 1),
            (cx + 28.0 + dx_shift, cy - 24.0 + dy_shift, -1),
            (cx - 28.0 + dx_shift, cy + 24.0 + dy_shift, -1),
            (cx + 28.0 + dx_shift, cy + 24.0 + dy_shift, 1),
        ]
    elif case == "six_by_eight_lattice":
        # A clean bounded analogue of the historical design.  It is not the
        # historical generator, whose staggered right-edge sites crossed the
        # sample boundary; the distinction is recorded in the metadata.
        for row in range(6):
            for col in range(8):
                x = 16.0 + 32.0 * col + (16.0 if row % 2 else 0.0)
                y = 20.0 + (216.0 / 5.0) * row
                q = 1 if (row + col) % 2 == 0 else -1
                positions.append((x + dx_shift, y + dy_shift, q))
    elif case == "random_complex_gaussian":
        rng = np.random.default_rng(seed)
        real = rng.normal(size=shape)
        imag = rng.normal(size=shape)
        field = real + 1j * imag
        # Band-limit by a smooth Gaussian in Fourier space.  The scale is in
        # cycles per pixel and deliberately well below Nyquist.
        fy = np.fft.fftfreq(h)[None, :]
        fx = np.fft.fftfreq(w)[:, None]
        spectrum = np.fft.fft2(field)
        k2 = (2 * np.pi * fx) ** 2 + (2 * np.pi * fy) ** 2
        spectrum *= np.exp(-0.5 * (k2 / (2 * np.pi * 0.12) ** 2))
        field = np.fft.ifft2(spectrum)
        field /= np.max(np.abs(field)) or 1.0
        truth = []
        meta = {
            "case": case,
            "seed": seed,
            "wavelength_nm": wavelength_nm,
            "fov_um": fov_um,
            "pixel_um": [dy_um, dx_um],
            "shift_px": shift_px,
            "amplitude_floor": amp_floor,
            "sigma_um": sigma_um,
            "true_vortices": 0,
            "note": "Random Gaussian field has no position truth; use density/null analyses.",
        }
        return field.astype(np.complex128), truth, meta
    else:
        raise ValueError(f"unknown analytical case: {case}")

    phase = np.zeros(shape, dtype=float)
    truth: list[dict[str, float]] = []
    for x0, y0, q in positions:
        phase += q * np.arctan2(y_um - y0, x_um - x0)
        truth.append({"x_um": float(x0), "y_um": float(y0), "charge": int(q)})

    envelope = np.exp(-((x_um - cx) ** 2 + (y_um - cy) ** 2) / (2.0 * sigma_um**2))
    # Include a finite physical core depression.  A phase winding exists even
    # when amplitude is non-zero, but a detector that requires an intensity
    # support signal needs an actual core minimum.  The width is tied to the
    # current sampling scale and is recorded in the metadata.
    core_sigma_um = 4.0
    core_profile = np.ones(shape, dtype=float)
    for x0, y0, _q in positions:
        core_profile *= 1.0 - 0.98 * np.exp(
            -((x_um - x0) ** 2 + (y_um - y0) ** 2) / (2.0 * core_sigma_um**2)
        )
    amplitude = amp_floor + (1.0 - amp_floor) * envelope * np.maximum(core_profile, 0.02)
    field = amplitude * np.exp(1j * phase)
    meta = {
        "case": case,
        "seed": seed,
        "wavelength_nm": wavelength_nm,
        "fov_um": fov_um,
        "pixel_um": [dy_um, dx_um],
        "shift_px": shift_px,
        "amplitude_floor": amp_floor,
        "sigma_um": sigma_um,
        "core_sigma_um": core_sigma_um,
        "true_vortices": len(truth),
        "true_net_charge": int(sum(p["charge"] for p in truth)),
        "position_note": "Positions are exact cell-centre-independent design coordinates; detector positions are reported in pixel coordinates.",
    }
    return field.astype(np.complex128), truth, meta


def make_matched_spectrum_surrogate(field: np.ndarray, seed: int) -> np.ndarray:
    """Preserve the periodic power spectrum and randomize Fourier phases."""
    rng = np.random.default_rng(seed)
    spectrum = np.fft.fft2(field)
    magnitude = np.abs(spectrum)
    phase = rng.uniform(-np.pi, np.pi, size=field.shape)
    surrogate = np.fft.ifft2(magnitude * np.exp(1j * phase))
    scale = np.sqrt(np.sum(np.abs(field) ** 2) / max(np.sum(np.abs(surrogate) ** 2), 1e-30))
    return surrogate * scale


def make_matched_amplitude_surrogate(field: np.ndarray, seed: int) -> np.ndarray:
    """Keep |E| pointwise and randomize phase independently at every sample."""
    rng = np.random.default_rng(seed)
    return np.abs(field) * np.exp(1j * rng.uniform(-np.pi, np.pi, size=field.shape))


def frequency_grid(shape: tuple[int, int], dx_um: float, dy_um: float) -> tuple[np.ndarray, np.ndarray]:
    fy = np.fft.fftfreq(shape[0], d=dy_um * 1e-6)
    fx = np.fft.fftfreq(shape[1], d=dx_um * 1e-6)
    return np.meshgrid(fx, fy, indexing="xy")


def asm_numpy(field: np.ndarray, z_m: float, dx_um: float, dy_um: float, wavelength_nm: float) -> np.ndarray:
    """Periodic band-limited angular-spectrum propagator; z is in metres."""
    if z_m == 0:
        return np.asarray(field, dtype=np.complex128).copy()
    fx, fy = frequency_grid(field.shape, dx_um, dy_um)
    k = 2.0 * np.pi / (wavelength_nm * 1e-9)
    kz_sq = k * k - (2.0 * np.pi * fx) ** 2 - (2.0 * np.pi * fy) ** 2
    propagating = kz_sq >= 0.0
    h = np.zeros(field.shape, dtype=np.complex128)
    h[propagating] = np.exp(1j * np.sqrt(kz_sq[propagating]) * z_m)
    return np.fft.ifft2(np.fft.fft2(field) * h)


def fresnel_numpy(field: np.ndarray, z_m: float, dx_um: float, dy_um: float, wavelength_nm: float) -> np.ndarray:
    """Paraxial transfer-function propagator; z is in metres."""
    if z_m == 0:
        return np.asarray(field, dtype=np.complex128).copy()
    fx, fy = frequency_grid(field.shape, dx_um, dy_um)
    h = np.exp(-1j * np.pi * (wavelength_nm * 1e-9) * z_m * (fx * fx + fy * fy))
    return np.fft.ifft2(np.fft.fft2(field) * h)


def asm_torch(field: np.ndarray, z_m: float, dx_um: float, dy_um: float, wavelength_nm: float) -> np.ndarray:
    """Independent architecture check using torch's FFT implementation."""
    if torch is None:
        raise RuntimeError("torch is unavailable")
    if z_m == 0:
        return np.asarray(field, dtype=np.complex128).copy()
    tensor = torch.from_numpy(np.asarray(field, dtype=np.complex128)).to(torch.complex128)
    h_shape, w_shape = field.shape
    fy = torch.fft.fftfreq(h_shape, d=dy_um * 1e-6, dtype=torch.float64)
    fx = torch.fft.fftfreq(w_shape, d=dx_um * 1e-6, dtype=torch.float64)
    FX, FY = torch.meshgrid(fx, fy, indexing="xy")
    k = 2.0 * np.pi / (wavelength_nm * 1e-9)
    kz_sq = k * k - (2.0 * np.pi * FX) ** 2 - (2.0 * np.pi * FY) ** 2
    propagating = kz_sq >= 0
    h = torch.zeros(field.shape, dtype=torch.complex128)
    h[propagating] = torch.exp(1j * torch.sqrt(kz_sq[propagating].to(torch.float64)) * z_m).to(torch.complex128)
    out = torch.fft.ifft2(torch.fft.fft2(tensor) * h)
    return out.numpy()


def fourier_shift(field: np.ndarray, dy_px: float, dx_px: float) -> np.ndarray:
    """Translate the sampled complex field with the Fourier shift theorem."""
    h, w = field.shape
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    return np.fft.ifft2(np.fft.fft2(field) * np.exp(-2j * np.pi * (fy * dy_px + fx * dx_px)))


def propagate_padded(field: np.ndarray, z_m: float, fraction: float, dx_um: float, dy_um: float, wavelength_nm: float) -> np.ndarray:
    """Zero-pad, propagate periodically, and crop the original field region."""
    if fraction <= 0:
        return asm_numpy(field, z_m, dx_um, dy_um, wavelength_nm)
    h, w = field.shape
    # A fraction is per side; cap only for accidental misuse of the full matrix.
    py = int(math.ceil(fraction * h))
    px = int(math.ceil(fraction * w))
    padded = np.pad(field, ((py, py), (px, px)), mode="constant")
    out = asm_numpy(padded, z_m, dx_um, dy_um, wavelength_nm)
    return out[py:py + h, px:px + w]


def _principal_difference(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.angle(np.exp(1j * (a - b)))


def winding_cells(field: np.ndarray) -> np.ndarray:
    phase = np.angle(field)
    a = phase[:-1, :-1]
    b = phase[:-1, 1:]
    c = phase[1:, 1:]
    d = phase[1:, :-1]
    curl = _principal_difference(b, a) + _principal_difference(c, b) + _principal_difference(d, c) + _principal_difference(a, d)
    return np.rint(curl / (2.0 * np.pi)).astype(np.int8)


def _cell_intensity(field: np.ndarray) -> np.ndarray:
    intensity = np.abs(field) ** 2
    return 0.25 * (intensity[:-1, :-1] + intensity[:-1, 1:] + intensity[1:, :-1] + intensity[1:, 1:])


def _cells_to_records(cells: np.ndarray, field: np.ndarray) -> list[dict[str, float]]:
    intensity = _cell_intensity(field)
    ys, xs = np.where(np.abs(cells) > 0.5)
    return [
        {"y": float(y + 0.5), "x": float(x + 0.5), "charge": int(cells[y, x]), "intensity": float(intensity[y, x])}
        for y, x in zip(ys, xs)
    ]


def _cluster_cells(cells: np.ndarray, field: np.ndarray) -> list[dict[str, float]]:
    intensity = _cell_intensity(field)
    records: list[dict[str, float]] = []
    for sign in (-1, 1):
        mask = cells == sign
        if not np.any(mask):
            continue
        labels, nlabels = ndimage.label(mask, structure=np.ones((3, 3), dtype=np.int8))
        for label in range(1, nlabels + 1):
            yy, xx = np.where(labels == label)
            weights = np.abs(cells[yy, xx]).astype(float)
            charge = int(np.sum(cells[yy, xx]))
            records.append({
                "y": float(np.average(yy + 0.5, weights=weights)),
                "x": float(np.average(xx + 0.5, weights=weights)),
                "charge": charge,
                "intensity": float(np.average(intensity[yy, xx], weights=weights)),
                "n_cells": int(len(yy)),
            })
    return records


def _support_mask(cells: np.ndarray, field: np.ndarray, min_contrast: float = 0.01) -> np.ndarray:
    """Keep winding cells whose local amplitude is below a surrounding ring."""
    intensity = np.abs(field) ** 2
    h, w = cells.shape
    padded = np.pad(intensity, 2, mode="edge")
    core = 0.25 * (
        intensity[:-1, :-1] + intensity[:-1, 1:]
        + intensity[1:, :-1] + intensity[1:, 1:]
    )
    # The 4x4 ring is evaluated by twelve vectorized shifted-array values.
    # A ring *mean* is used instead of a ring minimum so that a single
    # off-centre low-amplitude sample cannot suppress a genuine subpixel core.
    ring_sum = np.zeros((h, w), dtype=float)
    ring_count = 0
    for dy in range(4):
        for dx in range(4):
            if dy in (1, 2) and dx in (1, 2):
                continue
            ring_sum += padded[2 + dy:2 + dy + h, 2 + dx:2 + dx + w]
            ring_count += 1
    ring = ring_sum / float(ring_count)
    contrast = (ring - core) / np.maximum(ring, 1e-15)
    return (np.abs(cells) > 0.5) & (contrast >= min_contrast)


def _bilinear_phase(field: np.ndarray, y: float, x: float) -> float:
    h, w = field.shape
    if y < 0 or x < 0 or y > h - 1 or x > w - 1:
        return float("nan")
    y0, x0 = int(math.floor(y)), int(math.floor(x))
    y1, x1 = min(y0 + 1, h - 1), min(x0 + 1, w - 1)
    fy, fx = y - y0, x - x0
    # Interpolate the complex field before taking its phase.  Interpolating
    # principal phase angles directly is branch-cut dependent and is precisely
    # the kind of implementation artifact this experiment is meant to expose.
    value = ((1 - fy) * (1 - fx) * field[y0, x0]
             + (1 - fy) * fx * field[y0, x1]
             + fy * (1 - fx) * field[y1, x0]
             + fy * fx * field[y1, x1])
    return float(np.angle(value))


def local_minimum_contour(field: np.ndarray, radius: float = 2.0, n_points: int = 32, max_candidates: int = 500) -> list[dict[str, float]]:
    """Independent detector: contour winding around strong local minima."""
    h, w = field.shape
    intensity = np.abs(field) ** 2
    local_min = ndimage.minimum_filter(intensity, size=3, mode="nearest")
    yy, xx = np.where(np.isfinite(intensity) & (intensity <= local_min + 1e-14))
    if len(yy) == 0:
        return []
    # Prefer the darkest candidates and enforce a minimum separation.  This is
    # a bounded detector, not a claim that all local minima are singularities.
    order = np.argsort(intensity[yy, xx])
    # Bound the candidate pool before greedy nonmaximum suppression.  Without
    # this bound, a random 512² field can make the Python suppression loop
    # quadratic in the number of local minima and dominate the experiment.
    pool = min(len(order), max(64, max_candidates * 2))
    yy, xx = yy[order][:pool], xx[order][:pool]
    selected: list[tuple[int, int]] = []
    min_sep2 = max(1.0, (0.8 * radius) ** 2)
    for y, x in zip(yy.tolist(), xx.tolist()):
        if len(selected) >= max_candidates:
            break
        if all((y - sy) ** 2 + (x - sx) ** 2 >= min_sep2 for sy, sx in selected):
            selected.append((y, x))
    records: list[dict[str, float]] = []
    theta = np.arange(n_points, dtype=float) * (2.0 * np.pi / n_points)
    for y0, x0 in selected:
        if y0 < radius + 1 or x0 < radius + 1 or y0 >= h - radius - 1 or x0 >= w - radius - 1:
            continue
        phases = np.array([
            _bilinear_phase(field, y0 + radius * np.sin(t), x0 + radius * np.cos(t))
            for t in theta
        ])
        if not np.all(np.isfinite(phases)):
            continue
        phase_steps = _principal_difference(np.roll(phases, -1), phases)
        winding = int(np.rint(np.sum(phase_steps) / (2.0 * np.pi)))
        if abs(winding) < 0.5:
            continue
        # A low-core/high-ring check suppresses ordinary local minima.
        yy0, xx0 = max(0, int(y0 - radius)), max(0, int(x0 - radius))
        yy1, xx1 = min(h, int(y0 + radius + 1)), min(w, int(x0 + radius + 1))
        local = intensity[yy0:yy1, xx0:xx1]
        core = float(intensity[y0, x0])
        ring = float(np.mean(np.delete(local.ravel(), np.argmax(local)))) if local.size > 1 else core
        if ring <= 0 or (ring - core) / ring < 0.01:
            continue
        records.append({"y": float(y0), "x": float(x0), "charge": winding, "intensity": core, "ring_intensity": ring})
    return records


def detect(field: np.ndarray, detector: str) -> list[dict[str, float]]:
    if detector == "raw_winding":
        return _cells_to_records(winding_cells(field), field)
    if detector == "clustered_winding":
        return _cluster_cells(winding_cells(field), field)
    if detector == "supported_clustered_winding":
        cells = winding_cells(field)
        supported = np.zeros_like(cells, dtype=bool)
        if np.any(cells):
            supported = _support_mask(cells, field)
        return _cluster_cells(np.where(supported, cells, 0).astype(np.int8), field)
    if detector == "local_minimum_contour":
        return local_minimum_contour(field)
    raise ValueError(f"unknown detector {detector}")


def match_records(records: list[dict[str, float]], truth: list[dict[str, float]], shape: tuple[int, int], fov_um: float = FOV_UM, tolerance_px: float = 2.0) -> dict[str, Any]:
    if not truth:
        return {"true_positive": None, "false_positive": None, "false_negative": None, "charge_correct": None, "localization_rmse_px": None}
    h, w = shape
    true_xy = np.array([[physical_to_pixel(t["x_um"], t["y_um"], shape, fov_um)[0], physical_to_pixel(t["x_um"], t["y_um"], shape, fov_um)[1]] for t in truth])
    pred_xy = np.array([[r["x"], r["y"]] for r in records]) if records else np.empty((0, 2))
    if len(pred_xy) == 0:
        return {"true_positive": 0, "false_positive": 0, "false_negative": len(truth), "charge_correct": 0, "localization_rmse_px": None}
    cost = np.linalg.norm(true_xy[:, None, :] - pred_xy[None, :, :], axis=2)
    rows, cols = linear_sum_assignment(cost)
    tp = 0
    charge_correct = 0
    errors: list[float] = []
    for r, c in zip(rows, cols):
        distance = float(cost[r, c])
        if distance <= tolerance_px:
            tp += 1
            errors.append(distance)
            if int(records[c]["charge"]) == int(truth[r]["charge"]):
                charge_correct += 1
    return {
        "true_positive": int(tp),
        "false_positive": int(len(records) - tp),
        "false_negative": int(len(truth) - tp),
        "charge_correct": int(charge_correct),
        "localization_rmse_px": float(np.sqrt(np.mean(np.square(errors)))) if errors else None,
    }


def summarize(field: np.ndarray, detector: str, truth: list[dict[str, float]] | None = None, shape: tuple[int, int] | None = None) -> dict[str, Any]:
    records = detect(field, detector)
    charges = np.array([int(r["charge"]) for r in records], dtype=int)
    intensities = np.array([float(r.get("intensity", 0.0)) for r in records], dtype=float)
    out: dict[str, Any] = {
        "detector": detector,
        "count": int(len(records)),
        "positive": int(np.sum(charges > 0)),
        "negative": int(np.sum(charges < 0)),
        "net_charge": int(charges.sum()) if len(charges) else 0,
        "absolute_charge": int(np.abs(charges).sum()) if len(charges) else 0,
        "minimum_feature_intensity": float(intensities.min()) if len(intensities) else None,
        "median_feature_intensity": float(np.median(intensities)) if len(intensities) else None,
    }
    if truth is not None and shape is not None:
        out["truth_match"] = match_records(records, truth, shape)
    return out


def ncc(a: np.ndarray, b: np.ndarray) -> float:
    aa = np.asarray(a).ravel() - np.mean(a)
    bb = np.asarray(b).ravel() - np.mean(b)
    den = np.linalg.norm(aa) * np.linalg.norm(bb)
    return float(abs(np.vdot(aa, bb)) / den) if den else 0.0


def field_stats(field: np.ndarray) -> dict[str, float]:
    energy = float(np.sum(np.abs(field) ** 2))
    return {
        "energy": energy,
        "max_abs": float(np.max(np.abs(field))),
        "mean_intensity": float(np.mean(np.abs(field) ** 2)),
        "sha256": sha256_array(field),
    }


def run_calibration(seed: int = 42) -> dict[str, Any]:
    t0 = time.time()
    grids = (32, 48, 64, 96, 128, 160, 192, 256, 320, 384, 512)
    cases = ("single_vortex", "vortex_pair", "double_vortex", "four_vortex_lattice")
    shifts = (0.0, 0.1, 0.25, 0.33, 0.5, 0.67, 0.75, 0.9)
    rows: list[dict[str, Any]] = []
    for case in cases:
        for n in grids:
            for shift in shifts:
                field, truth, meta = make_known_field((n, n), case, seed=seed, shift_px=shift)
                for detector in DETECTORS:
                    row = {"case": case, "grid": n, "shift_px": shift, "truth": meta["true_vortices"], "seed": seed}
                    row.update(summarize(field, detector, truth, (n, n)))
                    row["relative_bias"] = (row["count"] - row["truth"]) / row["truth"] if row["truth"] else None
                    rows.append(row)
    # Negative controls: plane wave and a flat-amplitude random phase map.
    negative: list[dict[str, Any]] = []
    for n in (64, 128, 256, 512):
        plane = np.ones((n, n), dtype=np.complex128)
        flat_phase = np.exp(1j * np.random.default_rng(seed + n).uniform(-np.pi, np.pi, (n, n)))
        for name, field in (("plane_wave", plane), ("flat_amplitude_random_phase", flat_phase)):
            for detector in DETECTORS:
                negative.append({"case": name, "grid": n, "seed": seed, **summarize(field, detector)})
    return {
        "experiment": "EXP-0015",
        "stage": "calibration",
        "timestamp_utc": utc_now(),
        "seed": seed,
        "parameters": {"grids": grids, "cases": cases, "shifts": shifts, "detectors": DETECTORS},
        "rows": rows,
        "negative_controls": negative,
        "runtime_s": time.time() - t0,
    }


def run_convergence(seed: int = 42) -> dict[str, Any]:
    t0 = time.time()
    grids = (64, 96, 128, 160, 192, 256, 320, 384, 512)
    shifts = (0.0, 0.1, 0.25, 0.33, 0.5, 0.67, 0.75, 0.9)
    # A dense z sweep is performed on two representative grids; the full grid
    # ladder at selected planes follows it.
    z_sweep_rows: list[dict[str, Any]] = []
    for n in (128, 256):
        field0, truth, meta = make_known_field((n, n), "four_vortex_lattice", seed=seed, shift_px=0.0)
        _, _, dy_um, dx_um = cell_coordinates((n, n))
        for z_um in Z_SWEEP_UM:
            field = asm_numpy(field0, z_um * 1e-6, dx_um, dy_um, BASE_WAVELENGTH_NM)
            for detector in DETECTORS:
                row = {"grid": n, "z_um": z_um, "detector": detector, "field_case": "four_vortex_lattice", "truth": len(truth)}
                row.update(summarize(field, detector, truth, (n, n)))
                z_sweep_rows.append(row)
    selected_z = (0.0, 320.0, 640.0, 1280.0)
    selected_shift_rows: list[dict[str, Any]] = []
    wavelength_rows: list[dict[str, Any]] = []
    for n in grids:
        for shift in shifts:
            field, truth, meta = make_known_field((n, n), "four_vortex_lattice", seed=seed, shift_px=shift)
            _, _, dy_um, dx_um = cell_coordinates((n, n))
            for z_um in selected_z:
                propagated = asm_numpy(field, z_um * 1e-6, dx_um, dy_um, BASE_WAVELENGTH_NM)
                for detector in DETECTORS:
                    row = {"grid": n, "z_um": z_um, "shift_px": shift, "detector": detector, "truth": len(truth)}
                    row.update(summarize(propagated, detector, truth, (n, n)))
                    selected_shift_rows.append(row)
        # Wavelength sweep at the same physical field and selected z values.
        for wavelength_nm in WAVELENGTHS_NM:
            field, truth, _ = make_known_field((n, n), "four_vortex_lattice", seed=seed, wavelength_nm=wavelength_nm)
            _, _, dy_um, dx_um = cell_coordinates((n, n))
            for z_um in (640.0, 1280.0):
                propagated = asm_numpy(field, z_um * 1e-6, dx_um, dy_um, wavelength_nm)
                for detector in DETECTORS:
                    row = {"grid": n, "z_um": z_um, "wavelength_nm": wavelength_nm, "detector": detector, "truth": len(truth)}
                    row.update(summarize(propagated, detector, truth, (n, n)))
                    wavelength_rows.append(row)
    # Padding is tested only on smaller grids to avoid allocating 8x padded
    # arrays at the largest convergence sizes.
    padding_rows: list[dict[str, Any]] = []
    for n in (64, 128, 256, 384):
        field0, truth, _ = make_known_field((n, n), "four_vortex_lattice", seed=seed)
        _, _, dy_um, dx_um = cell_coordinates((n, n))
        for fraction in PADDING_FRACTIONS:
            for z_um in (640.0, 1280.0):
                field = propagate_padded(field0, z_um * 1e-6, fraction, dx_um, dy_um, BASE_WAVELENGTH_NM)
                for detector in DETECTORS:
                    row = {"grid": n, "z_um": z_um, "padding_fraction": fraction, "detector": detector, "truth": len(truth)}
                    row.update(summarize(field, detector, truth, (n, n)))
                    padding_rows.append(row)
    return {
        "experiment": "EXP-0015",
        "stage": "convergence",
        "timestamp_utc": utc_now(),
        "seed": seed,
        "parameters": {
            "grids": grids, "shifts": shifts, "z_sweep_um": Z_SWEEP_UM,
            "selected_z_um": selected_z, "wavelengths_nm": WAVELENGTHS_NM,
            "padding_fractions": PADDING_FRACTIONS, "detectors": DETECTORS,
        },
        "z_sweep": z_sweep_rows,
        "grid_shift": selected_shift_rows,
        "wavelength": wavelength_rows,
        "padding": padding_rows,
        "runtime_s": time.time() - t0,
    }


def bilinear_sample(field: np.ndarray, y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Vectorized bilinear complex interpolation on pixel-centre coordinates."""
    h, w = field.shape
    y0 = np.floor(y).astype(int)
    x0 = np.floor(x).astype(int)
    y0 = np.clip(y0, 0, h - 1)
    x0 = np.clip(x0, 0, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)
    x1 = np.minimum(x0 + 1, w - 1)
    fy = np.clip(y - y0, 0.0, 1.0)
    fx = np.clip(x - x0, 0.0, 1.0)
    return ((1 - fy) * (1 - fx) * field[y0, x0]
            + (1 - fy) * fx * field[y0, x1]
            + fy * (1 - fx) * field[y1, x0]
            + fy * fx * field[y1, x1])


def downsample_reference(field: np.ndarray, shape: tuple[int, int], fov_um: float = FOV_UM) -> np.ndarray:
    """Sample a periodic reference at the target cell-centre coordinates."""
    h, w = field.shape
    th, tw = shape
    y_h = (np.arange(h, dtype=float) + 0.5) * fov_um / h
    x_h = (np.arange(w, dtype=float) + 0.5) * fov_um / w
    y_t = (np.arange(th, dtype=float) + 0.5) * fov_um / th
    x_t = (np.arange(tw, dtype=float) + 0.5) * fov_um / tw
    yy, xx = np.meshgrid(y_t, x_t, indexing="ij")
    # Convert physical coordinates to source pixel-centre indices.
    ypix = yy / (fov_um / h) - 0.5
    xpix = xx / (fov_um / w) - 0.5
    return bilinear_sample(field, ypix, xpix)


def run_oversample(seed: int = 42, reference_grid: int = REFERENCE_GRID) -> dict[str, Any]:
    t0 = time.time()
    target_grids = (64, 96, 128, 160, 192, 256, 320, 384, 512, 768, 1024)
    z_values_um = (0.0, 160.0, 320.0, 640.0, 960.0, 1280.0, 1600.0)
    # Generate and propagate the reference sequentially to limit peak memory.
    reference0, truth_ref, meta_ref = make_known_field(
        (reference_grid, reference_grid), "four_vortex_lattice", seed=seed, fov_um=FOV_UM,
    )
    _, _, dy_ref, dx_ref = cell_coordinates((reference_grid, reference_grid))
    rows: list[dict[str, Any]] = []
    for z_um in z_values_um:
        reference = asm_numpy(reference0, z_um * 1e-6, dx_ref, dy_ref, BASE_WAVELENGTH_NM)
        for n in target_grids:
            sampled = downsample_reference(reference, (n, n))
            # Direct continuous field at the same z is a propagation-free
            # comparison; it is generated at the coarse grid directly.
            direct0, truth_direct, _ = make_known_field((n, n), "four_vortex_lattice", seed=seed, fov_um=FOV_UM)
            _, _, dy_n, dx_n = cell_coordinates((n, n))
            direct = asm_numpy(direct0, z_um * 1e-6, dx_n, dy_n, BASE_WAVELENGTH_NM)
            for detector in DETECTORS:
                row_sampled = {"path": "oversample_then_downsample", "reference_grid": reference_grid, "grid": n, "z_um": z_um, "detector": detector, "truth": len(truth_direct)}
                row_sampled.update(summarize(sampled, detector, truth_direct, (n, n)))
                row_direct = {"path": "direct_coarse_propagation", "reference_grid": None, "grid": n, "z_um": z_um, "detector": detector, "truth": len(truth_direct)}
                row_direct.update(summarize(direct, detector, truth_direct, (n, n)))
                row_sampled["direct_count"] = row_direct["count"]
                row_sampled["path_difference"] = row_sampled["count"] - row_direct["count"]
                rows.append(row_sampled)
        del reference
    # Subpixel shifts of the reference, measured after downsampling, are kept
    # separate from the grid rows to expose detector-grid coupling.
    shift_rows: list[dict[str, Any]] = []
    reference_shift, _, _ = make_known_field((reference_grid, reference_grid), "four_vortex_lattice", seed=seed, fov_um=FOV_UM)
    for shift in SHIFTS:
        shifted = fourier_shift(reference_shift, shift, shift)
        for n in (128, 256, 512):
            sampled = downsample_reference(shifted, (n, n))
            _, truth, _ = make_known_field((n, n), "four_vortex_lattice", seed=seed, fov_um=FOV_UM)
            for detector in DETECTORS:
                row = {"grid": n, "shift_px": shift, "detector": detector, "truth": len(truth)}
                row.update(summarize(sampled, detector, truth, (n, n)))
                shift_rows.append(row)
    return {
        "experiment": "EXP-0015",
        "stage": "oversample",
        "timestamp_utc": utc_now(),
        "seed": seed,
        "parameters": {"reference_grid": reference_grid, "target_grids": target_grids, "z_values_um": z_values_um, "shifts": SHIFTS, "detectors": DETECTORS},
        "rows": rows,
        "subpixel_rows": shift_rows,
        "reference_metadata": meta_ref,
        "runtime_s": time.time() - t0,
    }


def run_nulls(seed: int = 42) -> dict[str, Any]:
    t0 = time.time()
    rows: list[dict[str, Any]] = []
    for n in (64, 128, 256, 512):
        field, truth, _ = make_known_field((n, n), "four_vortex_lattice", seed=seed)
        _, _, dy_um, dx_um = cell_coordinates((n, n))
        variants = {
            "target": field,
            "matched_spectrum": make_matched_spectrum_surrogate(field, seed + 1000 + n),
            "matched_amplitude": make_matched_amplitude_surrogate(field, seed + 2000 + n),
            "random_complex_gaussian": make_known_field((n, n), "random_complex_gaussian", seed=seed + 3000 + n)[0],
        }
        for z_um in (0.0, 320.0, 640.0, 1280.0):
            for variant_name, variant in variants.items():
                propagated = asm_numpy(variant, z_um * 1e-6, dx_um, dy_um, BASE_WAVELENGTH_NM)
                for detector in DETECTORS:
                    row = {"grid": n, "z_um": z_um, "variant": variant_name, "detector": detector}
                    row.update(summarize(propagated, detector, None, None))
                    row["spectrum_power_ncc"] = ncc(np.abs(np.fft.fft2(variant)) ** 2, np.abs(np.fft.fft2(variants["target"])) ** 2)
                    row["amplitude_ncc"] = ncc(np.abs(variant), np.abs(variants["target"]))
                    rows.append(row)
    return {
        "experiment": "EXP-0015", "stage": "nulls", "timestamp_utc": utc_now(), "seed": seed,
        "parameters": {"grids": (64, 128, 256, 512), "z_values_um": (0, 320, 640, 1280), "detectors": DETECTORS},
        "rows": rows, "runtime_s": time.time() - t0,
    }


def run_implementation_checks(seed: int = 42) -> dict[str, Any]:
    t0 = time.time()
    n = 256
    field, truth, _ = make_known_field((n, n), "four_vortex_lattice", seed=seed)
    _, _, dy_um, dx_um = cell_coordinates((n, n))
    z_m = 1280.0e-6
    asm = asm_numpy(field, z_m, dx_um, dy_um, BASE_WAVELENGTH_NM)
    fresnel = fresnel_numpy(field, z_m, dx_um, dy_um, BASE_WAVELENGTH_NM)
    reverse = asm_numpy(asm, -z_m, dx_um, dy_um, BASE_WAVELENGTH_NM)
    torch_result = None
    torch_ncc = None
    if torch is not None:
        try:
            torch_result = asm_torch(field, z_m, dx_um, dy_um, BASE_WAVELENGTH_NM)
            torch_ncc = ncc(asm, torch_result)
        except Exception as exc:
            torch_ncc = f"ERROR: {type(exc).__name__}: {exc}"
    rows = []
    for detector in DETECTORS:
        rows.append({"detector": detector, "asm": summarize(asm, detector, truth, (n, n)), "fresnel": summarize(fresnel, detector, truth, (n, n))})
    return {
        "experiment": "EXP-0015", "stage": "implementation_checks", "timestamp_utc": utc_now(), "seed": seed,
        "parameters": {"grid": n, "z_um": 1280.0, "wavelength_nm": BASE_WAVELENGTH_NM, "z_unit": "metres"},
        "asm_fresnel_complex_ncc": ncc(asm, fresnel),
        "asm_reverse_complex_ncc": ncc(reverse, field),
        "energy_input": field_stats(field), "energy_asm": field_stats(asm),
        "torch_version": TORCH_VERSION, "asm_torch_complex_ncc": torch_ncc,
        "detectors": rows, "runtime_s": time.time() - t0,
    }


def environment() -> dict[str, Any]:
    try:
        import scipy
        scipy_version = scipy.__version__
    except Exception:
        scipy_version = None
    return {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "numpy": np.__version__,
        "scipy": scipy_version,
        "torch": TORCH_VERSION,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("calibration", "convergence", "oversample", "nulls", "implementation", "full"), default="calibration")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reference-grid", type=int, default=REFERENCE_GRID)
    args = parser.parse_args()
    stages = {
        "calibration": lambda: run_calibration(args.seed),
        "convergence": lambda: run_convergence(args.seed),
        "oversample": lambda: run_oversample(args.seed, args.reference_grid),
        "nulls": lambda: run_nulls(args.seed),
        "implementation": lambda: run_implementation_checks(args.seed),
    }
    selected = list(stages) if args.stage == "full" else [args.stage]
    all_results: dict[str, Any] = {
        "schema_version": "1.0",
        "experiment": "EXP-0015",
        "run_timestamp_utc": utc_now(),
        "environment": environment(),
        "command": " ".join(sys.argv),
        "preregistration": str(CONFIG_DIR / "prereg_EXP-0015.json"),
        "stages": {},
    }
    for stage in selected:
        print(f"Starting {stage}...", flush=True)
        result = stages[stage]()
        all_results["stages"][stage] = result
        path = RESULTS_DIR / f"{stage}_{args.seed}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        write_json(path, result)
        print(f"Wrote {path} ({result.get('runtime_s', 0.0):.1f}s)", flush=True)
    write_json(RESULTS_DIR / "latest.json", all_results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
