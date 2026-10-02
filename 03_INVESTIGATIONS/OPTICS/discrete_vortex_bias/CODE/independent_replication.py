#!/usr/bin/env python3
"""Independent EXP-0015 replication.

This file intentionally does not import ``run_convergence`` or the historical
sandbox.  It uses a separately written field generator, SciPy FFT propagation,
and a raw winding implementation.  The purpose is architecture and coding
independence, not a second arbitrary parameter search.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from scipy import fft as sfft
from scipy import ndimage

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = HERE.parent / "RESULTS"
OUT.mkdir(parents=True, exist_ok=True)
FOV = 256.0
WAVELENGTH = 694.3


def coordinates(n: int) -> tuple[np.ndarray, np.ndarray]:
    pitch = FOV / n
    axis = (np.arange(n, dtype=float) + 0.5) * pitch
    return np.meshgrid(axis, axis, indexing="xy")


def field_four(n: int, shift: float = 0.0) -> tuple[np.ndarray, list[tuple[float, float, int]]]:
    xx, yy = coordinates(n)
    pitch = FOV / n
    positions: list[tuple[float, float, int]] = []
    for row in range(2):
        for col in range(2):
            x = FOV / 2 + (-28 if col == 0 else 28) + shift * pitch
            y = FOV / 2 + (-24 if row == 0 else 24) + shift * pitch
            q = 1 if (row + col) % 2 == 0 else -1
            positions.append((x, y, q))
    phase = np.zeros_like(xx)
    core = np.ones_like(xx)
    for x, y, q in positions:
        phase += q * np.arctan2(yy - y, xx - x)
        core *= 1.0 - 0.98 * np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * 4.0**2))
    env = np.exp(-((xx - FOV / 2) ** 2 + (yy - FOV / 2) ** 2) / (2 * 55.0**2))
    amp = 0.03 + 0.97 * env * np.maximum(core, 0.02)
    return amp * np.exp(1j * phase), positions


def propagate(u: np.ndarray, z_um: float, n: int, pixel_pitch_um: float | None = None) -> np.ndarray:
    if z_um == 0:
        return u.copy()
    if pixel_pitch_um is None:
        pixel_pitch_um = FOV / n
    dx = pixel_pitch_um * 1e-6
    fy = sfft.fftfreq(n, d=dx)
    fx = sfft.fftfreq(n, d=dx)
    kx, ky = np.meshgrid(2 * np.pi * fx, 2 * np.pi * fy, indexing="xy")
    k0 = 2 * np.pi / (WAVELENGTH * 1e-9)
    q = k0 * k0 - kx * kx - ky * ky
    h = np.zeros((n, n), dtype=np.complex128)
    mask = q >= 0
    h[mask] = np.exp(1j * np.sqrt(q[mask]) * (z_um * 1e-6))
    return sfft.ifft2(sfft.fft2(u) * h)


def winding(u: np.ndarray) -> tuple[int, int, int, float]:
    p = np.angle(u)
    a, b = p[:-1, :-1], p[:-1, 1:]
    c, d = p[1:, 1:], p[1:, :-1]
    dphi = lambda x, y: np.angle(np.exp(1j * (x - y)))
    curl = dphi(b, a) + dphi(c, b) + dphi(d, c) + dphi(a, d)
    q = np.rint(curl / (2 * np.pi)).astype(np.int8)
    nonzero = q != 0
    count = int(nonzero.sum())
    net = int(q.sum())
    pos = int((q > 0).sum())
    neg = int((q < 0).sum())
    return count, net, pos + neg, float(np.mean(np.abs(u) ** 2))


def run() -> dict[str, Any]:
    start = time.time()
    rows: list[dict[str, Any]] = []
    for n in (64, 96, 128, 160, 192, 256, 320, 384, 512):
        for shift in (0.0, 0.1, 0.25, 0.33, 0.5, 0.67, 0.75, 0.9):
            u0, truth = field_four(n, shift)
            for z_um in (0.0, 320.0, 640.0, 960.0, 1280.0, 1600.0):
                u = propagate(u0, z_um, n)
                count, net, signed, mean_i = winding(u)
                rows.append({
                    "grid": n,
                    "shift_px": shift,
                    "z_um": z_um,
                    "count": count,
                    "net_charge": net,
                    "signed_count": signed,
                    "mean_intensity": mean_i,
                    "truth_count": len(truth),
                    "truth_net": sum(q for _, _, q in truth),
                })
    # A separate pad check, coded with scipy.pad rather than the main module.
    pad_rows: list[dict[str, Any]] = []
    for n in (64, 128, 256):
        u0, truth = field_four(n)
        for fraction in (0.0, 0.25, 0.5, 1.0, 2.0, 3.0):
            py = px = int(np.ceil(fraction * n))
            if py == 0:
                up = u0
            else:
                up = propagate(np.pad(u0, ((py, py), (px, px))), 1280.0, n + 2 * py, pixel_pitch_um=FOV / n)[py:py + n, px:px + n]
            count, net, signed, mean_i = winding(up)
            pad_rows.append({"grid": n, "padding_fraction": fraction, "count": count, "net_charge": net, "mean_intensity": mean_i})
    return {
        "schema_version": "1.0",
        "experiment": "EXP-0015",
        "implementation": "independent SciPy FFT and raw winding; no main-module imports",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "rows": rows,
        "padding_rows": pad_rows,
        "runtime_s": time.time() - start,
    }


def main() -> int:
    result = run()
    path = OUT / f"independent_replication_{time.strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
