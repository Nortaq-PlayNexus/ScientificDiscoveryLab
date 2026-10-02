#!/usr/bin/env python3
"""EXP-0015 rectangular and physical-geometry controls."""
from __future__ import annotations
import json, time
from pathlib import Path
import numpy as np
from run_convergence import DETECTORS, RESULTS_DIR, BASE_WAVELENGTH_NM, asm_numpy, cell_coordinates, make_known_field, summarize, utc_now

SHAPES = ((128, 256), (256, 128), (256, 512), (512, 256))
Z = (0.0, 640.0, 1280.0)
SHIFTS = (0.0, 0.25, 0.5, 0.75)


def main() -> int:
    start = time.time(); rows = []
    for shape in SHAPES:
        for shift in SHIFTS:
            field, truth, meta = make_known_field(shape, "four_vortex_lattice", shift_px=shift)
            _, _, dy, dx = cell_coordinates(shape)
            for z_um in Z:
                out = asm_numpy(field, z_um * 1e-6, dx, dy, BASE_WAVELENGTH_NM)
                for detector in DETECTORS:
                    row = {"shape": list(shape), "shift_px": shift, "z_um": z_um, "detector": detector, "truth": len(truth)}
                    row.update(summarize(out, detector, truth, shape))
                    rows.append(row)
    # Same 256² sampling grid at three physical FOVs, with the same normalized
    # vortex layout. This separates pixel pitch from physical scale only partly;
    # it is explicitly labelled a scale control, not a physical prediction.
    scale_rows = []
    for fov_um in (128.0, 256.0, 512.0):
        shape = (256, 256)
        field, truth, meta = make_known_field(shape, "four_vortex_lattice", fov_um=fov_um)
        _, _, dy, dx = cell_coordinates(shape, fov_um)
        for z_um in (0.0, 640.0, 1280.0):
            out = asm_numpy(field, z_um * 1e-6, dx, dy, BASE_WAVELENGTH_NM)
            for detector in DETECTORS:
                row = {"fov_um": fov_um, "pixel_um": dx, "z_um": z_um, "detector": detector, "truth": len(truth)}
                row.update(summarize(out, detector, truth, shape))
                scale_rows.append(row)
    result = {"experiment": "EXP-0015", "stage": "geometry_controls", "timestamp_utc": utc_now(), "status": "EXPLORATORY_CONTROL", "parameters": {"shapes": SHAPES, "z_um": Z, "shifts": SHIFTS, "fov_um": (128.0, 256.0, 512.0)}, "rectangular_rows": rows, "scale_rows": scale_rows, "runtime_s": time.time() - start}
    path = RESULTS_DIR / f"geometry_controls_{time.strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
