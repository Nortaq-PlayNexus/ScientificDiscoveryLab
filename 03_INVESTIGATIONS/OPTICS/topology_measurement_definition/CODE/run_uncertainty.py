#!/usr/bin/env python3
"""EXP-0016 deterministic uncertainty subset.

Each trial samples grid, charge, core width, and subpixel shift from a frozen
seed. This is a numerical-estimator uncertainty study, not a physical sample.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

import run_topology_definition as main


def random_truth(rng: np.random.Generator, n: int, q: int, core: float):
    dx = main.FOV_UM / n
    j0 = n // 2
    # Independent x/y fractional offsets, bounded away from the FOV edge.
    sx = float(rng.uniform(-0.75, 0.75))
    sy = float(rng.uniform(-0.75, 0.75))
    x0 = (j0 + 0.5 + sx) * dx
    y0 = (j0 + 0.5 + sy) * dx
    return [{"x_um": x0, "y_um": y0, "charge": q}], sx, sy


def run() -> dict:
    rng = np.random.default_rng(42)
    rows = []
    start = time.time()
    for trial in range(96):
        n = int(rng.choice((64, 128, 256)))
        q = int(rng.choice((-2, -1, 1, 2)))
        core = float(rng.choice((1.0, 2.0, 4.0, 8.0)))
        truth, sx, sy = random_truth(rng, n, q, core)
        field, _ = main.make_field((n, n), truth, core_sigma_um=core, hard_zero=True)
        for detector in main.DETECTORS:
            row = main.row(
                field, detector, truth, (n, n),
                stage="uncertainty", family="randomized_single",
                trial_id=trial, grid=n, charge=q, core_sigma_um=core,
                shift_x_px=sx, shift_y_px=sy, z_um=0.0,
            )
            rows.append(row)
    return {
        "experiment": "EXP-0016",
        "stage": "uncertainty",
        "timestamp_utc": main.now(),
        "seed": 42,
        "trial_count": 96,
        "parameters": {"grids": (64, 128, 256), "charges": (-2, -1, 1, 2), "core_sigmas": (1.0, 2.0, 4.0, 8.0), "shift_range_px": (-0.75, 0.75)},
        "rows": rows,
        "runtime_s": time.time() - start,
    }


if __name__ == "__main__":
    result = run()
    path = main.RESULTS / f"uncertainty_{time.strftime('%Y%m%d_%H%M%S')}.json"
    main.write_json(path, result)
    print("Wrote", path)
