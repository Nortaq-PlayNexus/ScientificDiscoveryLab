#!/usr/bin/env python3
"""EXP-0016 boundary-crossing controls.

A unit vortex is translated through each edge of a finite sampled field. The
same case is repeated in a padded field and cropped back to the original FOV,
which distinguishes a boundary-convention loss from a field-topology change.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

import run_topology_definition as main


def case_truth(n: int, side: str, offset_px: float, q: int = 1):
    dx = main.FOV_UM / n
    c = (n // 2 + 0.5) * dx
    if side == "left":
        x, y = offset_px * dx, c
    elif side == "right":
        x, y = main.FOV_UM - offset_px * dx, c
    elif side == "top":
        x, y = c, offset_px * dx
    elif side == "bottom":
        x, y = c, main.FOV_UM - offset_px * dx
    elif side == "lower_left":
        x, y = offset_px * dx, offset_px * dx
    else:
        raise ValueError(side)
    inside = 0.0 < x < main.FOV_UM and 0.0 < y < main.FOV_UM
    truth = [{"x_um": x, "y_um": y, "charge": q}] if inside else []
    distance = min(x, y, main.FOV_UM - x, main.FOV_UM - y) / dx
    return truth, {"x_um": x, "y_um": y, "charge": q}, inside, distance


def padded_crop(n: int, truth_physical: dict, pad: int = 16):
    dx = main.FOV_UM / n
    shifted = [{"x_um": truth_physical["x_um"] + pad * dx, "y_um": truth_physical["y_um"] + pad * dx, "charge": truth_physical["charge"]}]
    padded, _ = main.make_field((n + 2 * pad, n + 2 * pad), shifted, fov_um=(n + 2 * pad) * dx, hard_zero=True)
    return padded, padded[pad:pad + n, pad:pad + n], shifted


def metrics_for(field, detector, truth, shape, fov_um=main.FOV_UM):
    m = main.summarize(field, detector, truth, shape, fov_um=fov_um)
    if not truth:
        # No singularity is inside the crop; any accepted record is an
        # explicit boundary false positive for this diagnostic.
        m["boundary_false_positive"] = int(m["record_count"] > 0)
        m["false_positive"] = int(m["record_count"])
        m["false_negative"] = 0
    else:
        m["boundary_false_positive"] = 0
    return m


def run() -> dict:
    rows = []
    start = time.time()
    for n in (64, 128, 256):
        for q in (1, 2):
            for side in ("left", "right", "top", "bottom", "lower_left"):
                for offset in (-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0, 5.0):
                    truth, physical, inside, distance = case_truth(n, side, offset, q)
                    direct, _ = main.make_field((n, n), [{"x_um": physical["x_um"], "y_um": physical["y_um"], "charge": q}], hard_zero=True)
                    full, crop, shifted_truth = padded_crop(n, physical, pad=16)
                    for detector in main.DETECTORS:
                        a = metrics_for(direct, detector, truth, (n, n))
                        b = metrics_for(crop, detector, truth, (n, n))
                        c = metrics_for(full, detector, shifted_truth, full.shape, fov_um=full.shape[0] * (main.FOV_UM / n))
                        rows.append({
                            "control": "boundary_crossing", "grid": n, "charge": q,
                            "side": side, "offset_px": offset,
                            "distance_to_boundary_px": distance,
                            "position_inside": inside, "detector": detector,
                            "unpadded_location_count": a["location_count"],
                            "unpadded_winding_cell_count": a["winding_cell_count"],
                            "unpadded_absolute_charge": a["absolute_charge"],
                            "unpadded_signed_charge": a["signed_charge"],
                            "unpadded_false_positive": a["false_positive"],
                            "unpadded_boundary_false_positive": a["boundary_false_positive"],
                            "padded_location_count": b["location_count"],
                            "padded_winding_cell_count": b["winding_cell_count"],
                            "padded_absolute_charge": b["absolute_charge"],
                            "padded_signed_charge": b["signed_charge"],
                            "padded_false_positive": b["false_positive"],
                            "padded_boundary_false_positive": b["boundary_false_positive"],
                            "padded_full_location_count": c["location_count"],
                            "padded_full_winding_cell_count": c["winding_cell_count"],
                            "padded_full_absolute_charge": c["absolute_charge"],
                            "padded_full_signed_charge": c["signed_charge"],
                        })
    return {
        "experiment": "EXP-0016", "stage": "boundary_controls",
        "timestamp_utc": main.now(), "seed": 42,
        "parameters": {"grids": (64, 128, 256), "charges": (1, 2), "sides": ("left", "right", "top", "bottom", "lower_left"), "offsets_px": (-2.0, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0, 5.0), "pad_pixels": 16},
        "rows": rows, "runtime_s": time.time() - start,
    }


if __name__ == "__main__":
    result = run()
    path = main.RESULTS / f"boundary_controls_{time.strftime('%Y%m%d_%H%M%S')}.json"
    main.write_json(path, result)
    print("Wrote", path)
