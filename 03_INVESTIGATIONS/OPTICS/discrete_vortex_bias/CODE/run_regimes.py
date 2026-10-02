#!/usr/bin/env python3
"""EXP-0015 exploratory regime map.

The primary convergence matrix uses well-separated vortices and therefore acts
as a negative control: it should be stable. This stage deliberately adds
close pairs, high-charge vortices, dense lattices, and band-limited random
fields to locate the finite-resolution failure regime. It is exploratory and
cannot promote a candidate without a new confirmatory run.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from run_convergence import (
    DETECTORS, RESULTS_DIR, FOV_UM, BASE_WAVELENGTH_NM, asm_numpy,
    cell_coordinates, detect, match_records, summarize, utc_now,
)

SEED = 42
GRIDS = (32, 48, 64, 96, 128, 160, 192, 256, 320, 384, 512)
SHIFTS = (0.0, 0.25, 0.5, 0.75)
Z_VALUES = (0.0, 1280.0)


def make_field(shape: tuple[int, int], positions: list[tuple[float, float, int]], shift_px: float = 0.0, fov_um: float = FOV_UM, core_sigma_um: float = 4.0, envelope_sigma_um: float = 55.0, seed: int = SEED, random_band: float | None = None) -> tuple[np.ndarray, list[dict[str, float]], dict[str, Any]]:
    h, w = shape
    yy, xx, dx_um, dy_um = cell_coordinates(shape, fov_um)
    cx = fov_um / 2.0
    cy = fov_um / 2.0
    if random_band is not None:
        rng = np.random.default_rng(seed)
        u = rng.normal(size=shape) + 1j * rng.normal(size=shape)
        fy = np.fft.fftfreq(h)[None, :]
        fx = np.fft.fftfreq(w)[:, None]
        k2 = (2 * np.pi * fx) ** 2 + (2 * np.pi * fy) ** 2
        u = np.fft.ifft2(np.fft.fft2(u) * np.exp(-0.5 * (k2 / (2 * np.pi * random_band)) ** 2))
        u /= np.max(np.abs(u)) or 1.0
        return u.astype(np.complex128), [], {"case": "random_gaussian", "random_band": random_band, "seed": seed, "pixel_um": [dy_um, dx_um]}
    dx_shift = shift_px * dx_um
    dy_shift = shift_px * dy_um
    phase = np.zeros(shape, dtype=float)
    core = np.ones(shape, dtype=float)
    truth: list[dict[str, float]] = []
    for x0, y0, q in positions:
        x = x0 + dx_shift
        y = y0 + dy_shift
        phase += q * np.arctan2(yy - y, xx - x)
        core *= 1.0 - 0.98 * np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * core_sigma_um**2))
        truth.append({"x_um": float(x), "y_um": float(y), "charge": int(q)})
    envelope = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * envelope_sigma_um**2))
    amp = 0.03 + 0.97 * envelope * np.maximum(core, 0.02)
    return amp * np.exp(1j * phase), truth, {"case": "known", "pixel_um": [dy_um, dx_um], "shift_px": shift_px, "core_sigma_um": core_sigma_um, "true_vortices": len(truth), "true_net_charge": sum(p["charge"] for p in truth)}


def row_for(field: np.ndarray, detector_name: str, truth: list[dict[str, float]], shape: tuple[int, int], **tags: Any) -> dict[str, Any]:
    row = dict(tags)
    # Dense-array localization matching is quadratic in the number of true
    # sites and is not needed for the count-bias endpoint. Keep its truth
    # cardinality, but skip Hungarian matching above a small control size.
    match_truth = truth if len(truth) <= 20 else []
    row.update(summarize(field, detector_name, match_truth, shape))
    if truth:
        row["relative_bias"] = (row["count"] - len(truth)) / len(truth)
    else:
        row["relative_bias"] = None
    return row


def run() -> dict[str, Any]:
    start = time.time()
    rows: list[dict[str, Any]] = []
    # Close opposite-charge pairs: true total remains two, but the two cores
    # become below the detector's resolving scale as the separation shrinks.
    for separation_um in (2.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 32.0, 48.0):
        positions = [(128.0 - separation_um / 2, 128.0, 1), (128.0 + separation_um / 2, 128.0, -1)]
        for n in GRIDS:
            for shift in SHIFTS:
                field, truth, meta = make_field((n, n), positions, shift_px=shift)
                _, _, dy, dx = cell_coordinates((n, n))
                for z_um in Z_VALUES:
                    propagated = asm_numpy(field, z_um * 1e-6, dx, dy, BASE_WAVELENGTH_NM)
                    for detector in DETECTORS:
                        rows.append(row_for(propagated, detector, truth if z_um == 0 else [], (n, n), regime="close_pair", separation_um=separation_um, grid=n, shift_px=shift, z_um=z_um, detector=detector))
    # Higher-charge positive vortices expose charge representation differences.
    for charge in (1, 2, 3, 4, 6):
        positions = [(128.0, 128.0, charge)]
        for n in GRIDS:
            for shift in (0.0, 0.5):
                field, truth, meta = make_field((n, n), positions, shift_px=shift)
                _, _, dy, dx = cell_coordinates((n, n))
                for z_um in Z_VALUES:
                    propagated = asm_numpy(field, z_um * 1e-6, dx, dy, BASE_WAVELENGTH_NM)
                    for detector in DETECTORS:
                        rows.append(row_for(propagated, detector, truth if z_um == 0 else [], (n, n), regime="high_order", charge=charge, grid=n, shift_px=shift, z_um=z_um, detector=detector))
    # Dense alternating arrays: separation and core width are both smaller
    # than in the historical well-resolved lattice.
    for pitch_um in (8.0, 12.0, 16.0, 24.0):
        positions = []
        cols = max(2, int(224.0 // pitch_um))
        rows_n = max(2, int(224.0 // pitch_um))
        x0 = 128.0 - (cols - 1) * pitch_um / 2
        y0 = 128.0 - (rows_n - 1) * pitch_um / 2
        for r in range(rows_n):
            for c in range(cols):
                positions.append((x0 + c * pitch_um, y0 + r * pitch_um, 1 if (r + c) % 2 == 0 else -1))
        for n in (64, 128, 256, 512):
            for shift in (0.0, 0.5):
                field, truth, meta = make_field((n, n), positions, shift_px=shift)
                _, _, dy, dx = cell_coordinates((n, n))
                for z_um in Z_VALUES:
                    propagated = asm_numpy(field, z_um * 1e-6, dx, dy, BASE_WAVELENGTH_NM)
                    for detector in DETECTORS:
                        rows.append(row_for(propagated, detector, truth if z_um == 0 else [], (n, n), regime="dense_lattice", pitch_um=pitch_um, grid=n, shift_px=shift, z_um=z_um, detector=detector))
    # Band-limited random fields: no positional truth, so only count statistics
    # and cross-detector comparison are reported.
    for band in (0.05, 0.10, 0.20, 0.35):
        for n in (64, 128, 256, 512):
            for shift in (0.0, 0.5):
                field, truth, meta = make_field((n, n), [], shift_px=shift, random_band=band)
                _, _, dy, dx = cell_coordinates((n, n))
                for z_um in Z_VALUES:
                    propagated = asm_numpy(field, z_um * 1e-6, dx, dy, BASE_WAVELENGTH_NM)
                    for detector in DETECTORS:
                        rows.append(row_for(propagated, detector, [], (n, n), regime="random_gaussian", random_band=band, grid=n, shift_px=shift, z_um=z_um, detector=detector))
    return {
        "experiment": "EXP-0015", "stage": "exploratory_regime_map", "timestamp_utc": utc_now(), "seed": SEED,
        "status": "EXPLORATORY_NOT_PRIMARY", "parameters": {"grids": GRIDS, "shifts": SHIFTS, "z_values_um": Z_VALUES, "detectors": DETECTORS},
        "rows": rows, "runtime_s": time.time() - start,
    }


def main() -> int:
    result = run()
    path = RESULTS_DIR / f"exploratory_regime_map_{time.strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
