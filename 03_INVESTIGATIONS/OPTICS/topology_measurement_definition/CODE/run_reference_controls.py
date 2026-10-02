#!/usr/bin/env python3
"""EXP-0016 high-resolution and padding controls.

This is a control driver, not a new detector. It compares the finite-grid
field with a 2048² analytical reference sampled at the low-grid coordinates,
and repeats the finite-grid calculation after padding/cropping around the
field of view. The reference is deliberately downsampled before applying
low-grid estimators; applying a fixed-pixel contour to a 2048² array would
change the estimator geometry and is not a valid comparison.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage

import run_topology_definition as main

OUT = main.RESULTS
HIGH_N = 2048


def sample_at_low_centers(field: np.ndarray, n: int, fov_um: float = main.FOV_UM) -> np.ndarray:
    """Bilinearly sample a high-resolution field at low-grid cell centers."""
    low_coord = (np.arange(n, dtype=float) + 0.5) * (fov_um / n) / (fov_um / field.shape[0]) - 0.5
    yy, xx = np.meshgrid(low_coord, low_coord, indexing="ij")
    coords = np.stack((yy.ravel(), xx.ravel()))
    real = ndimage.map_coordinates(field.real, coords, order=1, mode="nearest")
    imag = ndimage.map_coordinates(field.imag, coords, order=1, mode="nearest")
    return (real + 1j * imag).reshape(n, n)


def relative_rms(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.abs(a - b) ** 2)) / max(np.sqrt(np.mean(np.abs(b) ** 2)), 1e-30))


def padded_crop(n: int, pad: int, truth: list[dict[str, Any]]) -> np.ndarray:
    dx = main.FOV_UM / n
    fov_pad = (n + 2 * pad) * dx
    shifted = [{"x_um": t["x_um"] + pad * dx, "y_um": t["y_um"] + pad * dx, "charge": t["charge"]} for t in truth]
    padded, _ = main.make_field((n + 2 * pad, n + 2 * pad), shifted, fov_um=fov_pad, hard_zero=True)
    return padded[pad:pad + n, pad:pad + n]


def main_run() -> dict[str, Any]:
    start = time.time()
    reference_rows: list[dict[str, Any]] = []
    cases: list[tuple[int, str, int, float, str]] = []
    for n in (64, 128, 256):
        for q in (-2, -1, 1, 2):
            for mode in ("exact_pixel", "half_pixel", "quarter_pixel"):
                cases.append((n, "single", q, 2.0, mode))
    for n in (64, 128):
        for mode in ("exact_pixel", "half_pixel"):
            cases.append((n, "opposite_pair", 0, 8.0, mode))
    for n in (64, 128):
        for sep in (2.0, 4.0):
            cases.append((n, "close_pair", 0, sep, "half_pixel"))

    for n, family, q, separation, mode in cases:
        truth_family = "opposite_pair" if family == "close_pair" else family
        truth = main.truth_positions((n, n), truth_family, charge=q, separation_um=separation, position_mode=mode)
        direct, _ = main.make_field((n, n), truth, hard_zero=True)
        high, _ = main.make_field((HIGH_N, HIGH_N), truth, fov_um=main.FOV_UM, hard_zero=False)
        reference = sample_at_low_centers(high, n)
        del high
        for detector in main.DETECTORS:
            d = main.summarize(direct, detector, truth, (n, n))
            r = main.summarize(reference, detector, truth, (n, n))
            reference_rows.append({
                "control": "2048_reference_downsample",
                "family": family, "grid": n, "charge": q,
                "separation_um": separation if family != "single" else None,
                "position_mode": mode, "detector": detector,
                "field_relative_rms": relative_rms(direct, reference),
                "direct_location_count": d["location_count"],
                "reference_location_count": r["location_count"],
                "direct_winding_cell_count": d["winding_cell_count"],
                "reference_winding_cell_count": r["winding_cell_count"],
                "direct_absolute_charge": d["absolute_charge"],
                "reference_absolute_charge": r["absolute_charge"],
                "direct_signed_charge": d["signed_charge"],
                "reference_signed_charge": r["signed_charge"],
                "direct_location_count_error": d["location_count_error"],
                "reference_location_count_error": r["location_count_error"],
            })

    padding_rows: list[dict[str, Any]] = []
    for n in (64, 128):
        for q in (-1, 1, 2, -2):
            truth = main.truth_positions((n, n), "single", charge=q, position_mode="half_pixel")
            direct, _ = main.make_field((n, n), truth, hard_zero=True)
            for pad in (0, 4, 8, 16, 32):
                crop = direct if pad == 0 else padded_crop(n, pad, truth)
                for detector in main.DETECTORS:
                    d = main.summarize(direct, detector, truth, (n, n))
                    p = main.summarize(crop, detector, truth, (n, n))
                    padding_rows.append({
                        "control": "padding_crop", "family": "single", "grid": n,
                        "charge": q, "position_mode": "half_pixel", "pad_pixels": pad,
                        "detector": detector, "field_relative_rms": relative_rms(direct, crop),
                        "direct_location_count": d["location_count"],
                        "padded_location_count": p["location_count"],
                        "direct_winding_cell_count": d["winding_cell_count"],
                        "padded_winding_cell_count": p["winding_cell_count"],
                        "direct_absolute_charge": d["absolute_charge"],
                        "padded_absolute_charge": p["absolute_charge"],
                        "direct_signed_charge": d["signed_charge"],
                        "padded_signed_charge": p["signed_charge"],
                    })
    return {
        "experiment": "EXP-0016",
        "stage": "reference_padding_controls",
        "timestamp_utc": main.now(),
        "parameters": {
            "reference_grid": HIGH_N,
            "reference_sampling": "bilinear sample at low-grid cell centers",
            "grids": (64, 128, 256),
            "padding_pixels": (0, 4, 8, 16, 32),
            "detectors": main.DETECTORS,
        },
        "reference_rows": reference_rows,
        "padding_rows": padding_rows,
        "runtime_s": time.time() - start,
    }


if __name__ == "__main__":
    result = main_run()
    path = OUT / f"reference_padding_{time.strftime('%Y%m%d_%H%M%S')}.json"
    main.write_json(path, result)
    print("Wrote", path)
