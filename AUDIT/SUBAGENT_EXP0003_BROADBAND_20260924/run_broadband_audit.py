"""Non-destructive EXP-0003 broadband resolution/artifact audit.

This script does NOT import or write any canonical EXP-0003 output.  It creates
new raw JSON/CSV artifacts under this directory only.

Primary question
----------------
At a fixed physical Gaussian spectrum, does the measured vortex density approach
Kac--Rice/Nye--Berry as pixels per central wavelength increase, and is the
broadband deficit explained by sampling/aliasing/detector limitations?

Conventions
-----------
The canonical EXP-0003 Gaussian used k0 = pi/2 rad/pixel at four pixels per
wavelength.  We therefore define physical units so that the original P=4
pixel has unit length: k0_phys = pi/2 per baseline length unit, lambda0_phys=4,
and sigma_k values 0.10, 0.25, 0.50, 0.75 are in those same physical units.  At
a target P pixels/wavelength, dx=4/P, so k0_px=(pi/2)*dx=2*pi/P and
sigma_px=sigma_phys*dx.  Thus P=4 exactly reproduces the canonical k0 and
sigma values, while the physical spectrum is held fixed as resolution changes.

For the main independent-ensemble ladder, N=32*P.  Hence the physical domain
is 128 baseline length units (32 central wavelengths) at every P, while the
number of samples increases.  This is the cleanest resolution-only comparison
that remains computationally practical.  A separate nested common-field test
uses a P=64 reference and exact subsampling, and a P=48 reference for the
non-power-of-two nested resolutions.

All random streams are recorded.  The main route uses the project's certified
SHA-256-labelled ``engine.utilities.core.rng`` contract.  A direct NumPy PCG64
route is run as a separate validation subset.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
OUT = ROOT / "AUDIT" / "SUBAGENT_EXP0003_BROADBAND_20260924"
ENGINE = ROOT / "04_SHARED_ENGINE"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
from engine.utilities.core import rng, seed_value  # noqa: E402

P_LIST = (4, 6, 8, 12, 16, 24, 32, 48, 64)
SIGMA_LIST = (0.10, 0.25, 0.50, 0.75)
SEEDS = (42, 7, 123, 2023, 314159, 271828)
K0_PHYS = np.pi / 2.0
LAMBDA_PHYS = 2.0 * np.pi / K0_PHYS
DOMAIN_UNITS = 128.0
ALPHA = 0.05


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def json_dump(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False), encoding="utf-8")


def make_gen(route: str, label: str, seed: int):
    """Return (generator, provenance)."""
    if route == "certified":
        return rng(label, int(seed)), {
            "route": route,
            "label": label,
            "seed": int(seed),
            "seed_value_sha256_16hex": f"{seed_value(label, int(seed)):016x}",
        }
    if route == "pcg64":
        # Deliberately independent of the project label/seed construction.
        ss = np.random.SeedSequence([0xA17C9E5, int(seed) & 0xFFFFFFFF, sum(ord(c) for c in label)])
        return np.random.Generator(np.random.PCG64(ss)), {
            "route": route,
            "label": label,
            "seed": int(seed),
            "bit_generator": "PCG64",
        }
    raise ValueError(route)


def freq_arrays(shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    ny, nx = shape
    fy = np.fft.fftfreq(ny) * (2.0 * np.pi)
    fx = np.fft.fftfreq(nx) * (2.0 * np.pi)
    ky = fy[:, None]
    kx = fx[None, :]
    kr = np.hypot(kx, ky)
    return kx, ky, kr, np.ones(shape, dtype=float)


def gaussian_spectrum(shape: tuple[int, int], p: int, sigma_phys: float):
    """Sample the fixed physical radial Gaussian on the target DFT grid.

    The original P=4 pixel is one physical length unit.  Consequently a
    target grid with P pixels per central wavelength has dx=4/P.
    """
    kx, ky, kr, _ = freq_arrays(shape)
    dx = LAMBDA_PHYS / p
    k0_px = K0_PHYS * dx
    sigma_px = sigma_phys * dx
    s = np.exp(-0.5 * ((kr - k0_px) / sigma_px) ** 2)
    return s, kx, ky, kr, k0_px, sigma_px


def continuum_prediction(sigma_phys: float) -> float:
    """Kac--Rice density in physical units for S(r)=exp[-(r-k0)^2/(2 sigma^2)].

    For an isotropic 2-D spectrum,
       n = (1/(2*pi)) * <kx^2 S>/<S>
         = [int r^3 S(r) dr] / [4*pi int r S(r) dr].
    The finite upper limit is 12 sigma beyond the peak; the omitted tail is
    recorded and is negligible for the specified widths.
    """
    from scipy.integrate import quad

    def s(r: float) -> float:
        return math.exp(-0.5 * ((r - K0_PHYS) / sigma_phys) ** 2)

    upper = K0_PHYS + 14.0 * sigma_phys
    den, den_err = quad(lambda r: r * s(r), 0.0, upper, epsabs=1e-12, epsrel=1e-12, limit=300)
    num, num_err = quad(lambda r: r**3 * s(r), 0.0, upper, epsabs=1e-10, epsrel=1e-12, limit=300)
    return float(num / (4.0 * np.pi * den)), {
        "upper_r": upper,
        "den": float(den),
        "den_quad_abs_error": float(den_err),
        "num": float(num),
        "num_quad_abs_error": float(num_err),
        "tail_note": "radial integral truncated at k0+14 sigma; tail is negligible",
    }


def discrete_prediction(s: np.ndarray, kx: np.ndarray) -> float:
    den = float(np.sum(s, dtype=np.float64))
    if den <= 0.0:
        return float("nan")
    return float(np.sum(kx * kx * s, dtype=np.float64) / den / (2.0 * np.pi))


def real_gaussian(shape: tuple[int, int], spectrum: np.ndarray, gen) -> np.ndarray:
    """Real Gaussian field with correct rectangular-array Hermitian pairing."""
    ny, nx = shape
    z = np.sqrt(spectrum / 2.0) * (
        gen.standard_normal(shape) + 1j * gen.standard_normal(shape)
    )
    iy = (-np.arange(ny)) % ny
    ix = (-np.arange(nx)) % nx
    z = 0.5 * (z + np.conj(z[np.ix_(iy, ix)]))
    return np.fft.ifft2(z).real


def complex_field_canonical(shape: tuple[int, int], spectrum: np.ndarray, gen) -> np.ndarray:
    """Circular complex Gaussian E=u+iv, matching the canonical construction."""
    half = spectrum / 2.0
    return real_gaussian(shape, half, gen) + 1j * real_gaussian(shape, half, gen)


def complex_field_direct(shape: tuple[int, int], spectrum: np.ndarray, gen) -> np.ndarray:
    """Independent circular-complex FFT construction (no Hermitian pairing)."""
    c = np.sqrt(spectrum / 2.0) * (
        gen.standard_normal(shape) + 1j * gen.standard_normal(shape)
    )
    return np.fft.ifft2(c)


def winding_counts(e: np.ndarray, margin: int) -> tuple[float, float, float]:
    """Principal-increment plaquette winding counter (D1)."""
    ex = np.angle(e[:, 1:] * np.conj(e[:, :-1]))
    ey = np.angle(e[1:, :] * np.conj(e[:-1, :]))
    circ = ex[:-1, :] + ey[:, 1:] - ex[1:, :] - ey[:, :-1]
    w = np.rint(circ / (2.0 * np.pi)).astype(np.int8)
    z = w[margin:-margin, margin:-margin]
    area = float(z.size)
    return (
        float(np.count_nonzero(z) / area),
        float(np.count_nonzero(z > 0) / area),
        float(np.count_nonzero(z < 0) / area),
    )


def _edge_crossings(g: np.ndarray):
    """Two linearly interpolated zero crossings on a cell boundary."""
    a, b = g[:-1, :-1], g[:-1, 1:]
    c, d = g[1:, :-1], g[1:, 1:]
    ny, nx = g.shape
    jj, ii = np.meshgrid(np.arange(ny - 1), np.arange(nx - 1), indexing="ij")
    eps = 1e-12
    ta = np.abs(a) / (np.abs(a) + np.abs(b) + eps)
    tb = np.abs(c) / (np.abs(c) + np.abs(d) + eps)
    tl = np.abs(a) / (np.abs(a) + np.abs(c) + eps)
    tr = np.abs(b) / (np.abs(b) + np.abs(d) + eps)
    mt, mb, ml, mr = a * b < 0, c * d < 0, a * c < 0, b * d < 0
    tx, ty = jj + ta, ii
    bx, by = jj + tb, ii + 1
    lx, ly = jj, ii + tl
    rx, ry = jj + 1, ii + tr
    ok = (mt.astype(np.int8) + mb.astype(np.int8) + ml.astype(np.int8) + mr.astype(np.int8)) == 2
    p1x = np.where(mt, tx, np.where(mb, bx, np.where(ml, lx, rx)))
    p1y = np.where(mt, ty, np.where(mb, by, np.where(ml, ly, ry)))
    p2x = np.where(mr, rx, np.where(ml, lx, np.where(mb, bx, tx)))
    p2y = np.where(mr, ry, np.where(ml, ly, np.where(mb, by, ty)))
    return p1x, p1y, p2x, p2y, ok


def contour_density(e: np.ndarray, margin: int) -> float:
    """Certified segment-intersection detector (D2), rectangular arrays."""
    ax, ay, bx, by, okr = _edge_crossings(e.real)
    cx, cy, dx, dy, oki = _edge_crossings(e.imag)
    d1x, d1y = bx - ax, by - ay
    d2x, d2y = dx - cx, dy - cy
    den = d1x * d2y - d1y * d2x
    wx, wy = cx - ax, cy - ay
    with np.errstate(divide="ignore", invalid="ignore"):
        ss = (wx * d2y - wy * d2x) / den
        uu = (wx * d1y - wy * d1x) / den
    hit = okr & oki & (den != 0) & (ss >= 0) & (ss <= 1) & (uu >= 0) & (uu <= 1)
    z = hit[margin:-margin, margin:-margin]
    return float(np.count_nonzero(z) / z.size)


def contour_naive_density(e: np.ndarray, margin: int) -> float:
    """Known intentionally overcounting D2-naive diagnostic."""
    out = None
    for g in (e.real, e.imag):
        a, b = g[:-1, :-1], g[:-1, 1:]
        c, d = g[1:, :-1], g[1:, 1:]
        nc = (a * b < 0).astype(np.int8) + (c * d < 0).astype(np.int8) + \
             (a * c < 0).astype(np.int8) + (b * d < 0).astype(np.int8)
        m = nc == 2
        out = m if out is None else (out & m)
    z = out[margin:-margin, margin:-margin]
    return float(np.count_nonzero(z) / z.size)


def fd_prediction(e: np.ndarray) -> float:
    """Forward-difference field estimate, exactly as canonical C1."""
    dx = e[:, 1:] - e[:, :-1]
    return float(np.mean(np.abs(dx) ** 2) / (2.0 * np.pi * np.mean(np.abs(e) ** 2)))


def fft_prediction(e: np.ndarray) -> float:
    """Observed FFT-moment estimate; useful for detecting off-grid/leakage bias."""
    kx, _, _, _ = freq_arrays(e.shape)
    power = np.abs(np.fft.fft2(e)) ** 2
    return float(np.sum(kx * kx * power) / np.sum(power) / (2.0 * np.pi))


def shift_field(e: np.ndarray, dx: float, dy: float) -> np.ndarray:
    ny, nx = e.shape
    fy = np.fft.fftfreq(ny)[:, None]
    fx = np.fft.fftfreq(nx)[None, :]
    return np.fft.ifft2(np.fft.fft2(e) * np.exp(-2j * np.pi * (fy * dx + fx * dy)))


def phase_edge_stats(e: np.ndarray) -> dict[str, float]:
    ex = np.angle(e[:, 1:] * np.conj(e[:, :-1]))
    ey = np.angle(e[1:, :] * np.conj(e[:-1, :]))
    a = np.abs(np.concatenate((ex.ravel(), ey.ravel())))
    return {
        "edge_phase_abs_mean": float(a.mean()),
        "edge_phase_abs_p95": float(np.percentile(a, 95)),
        "edge_phase_abs_p99": float(np.percentile(a, 99)),
        "edge_phase_frac_gt_0.9pi": float(np.mean(a > 0.9 * np.pi)),
        "edge_phase_frac_gt_0.99pi": float(np.mean(a > 0.99 * np.pi)),
        "edge_phase_max": float(a.max()),
    }


def lowpass_field(e: np.ndarray, cutoff_px: float) -> np.ndarray:
    _, _, kr, _ = freq_arrays(e.shape)
    return np.fft.ifft2(np.fft.fft2(e) * (kr <= cutoff_px))


def summarize(values: list[float] | np.ndarray) -> dict[str, Any]:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if x.size == 0:
        return {"n": 0, "mean": None, "sd": None, "se": None, "ci95": [None, None]}
    mean = float(x.mean())
    sd = float(x.std(ddof=1)) if x.size > 1 else 0.0
    se = sd / math.sqrt(x.size) if x.size > 1 else 0.0
    # Normal 95% interval; seed-block summary below is the inferential primary.
    z = 1.959963984540054
    return {
        "n": int(x.size),
        "mean": mean,
        "sd": sd,
        "se": se,
        "ci95": [mean - z * se, mean + z * se],
        "min": float(x.min()),
        "max": float(x.max()),
    }


def margin_for_p(p: int) -> int:
    # One-half central wavelength in pixel units, while retaining >=8 samples
    # per requested resolution.  The physical ROI width is nearly constant.
    return max(4, int(round(0.5 * p)))


def target_shape(p: int, domain_units: float = DOMAIN_UNITS) -> tuple[int, int]:
    # N*dx = domain_units, with dx=lambda_phys/P.
    n = int(round(domain_units * p / LAMBDA_PHYS))
    return (n, n)


def truncation_diagnostics(s: np.ndarray, kx: np.ndarray, ky: np.ndarray, kr: np.ndarray, p: int, sigma_phys: float) -> dict[str, float]:
    total = float(s.sum())
    outside_axis = (np.abs(kx) > np.pi) | (np.abs(ky) > np.pi)
    # The target square is the sampled periodic domain.  Estimate the
    # continuum power omitted beyond its physical axis Nyquist, and separately
    # beyond a radial Nyquist shell.  At P=4 the physical axis Nyquist is 4*pi
    # in the original baseline-pixel units, not pi.
    from scipy.integrate import quad
    dx = LAMBDA_PHYS / p
    physical_axis_nyquist = np.pi / dx

    def sr(r: float) -> float:
        return math.exp(-0.5 * ((r - K0_PHYS) / sigma_phys) ** 2)

    upper = K0_PHYS + 14 * sigma_phys
    den = quad(lambda r: r * sr(r), 0.0, upper, epsabs=1e-12, limit=300)[0]
    out_num = quad(lambda r: r * sr(r), physical_axis_nyquist, upper, epsabs=1e-12, limit=300)[0]
    return {
        "target_shape_yx": f"{s.shape[0]}x{s.shape[1]}",
        "p": p,
        "dx_physical": dx,
        "k0_px": K0_PHYS * dx,
        "sigma_px": sigma_phys * dx,
        "axis_nyquist_px": np.pi,
        "physical_axis_nyquist": physical_axis_nyquist,
        "discrete_power_fraction_outside_axis_nyquist": float(s[outside_axis].sum() / total),
        "continuum_power_fraction_beyond_axis_nyquist": float(out_num / den),
        "discrete_sum_S": total,
        "discrete_max_kr_px": float(kr.max()),
        "discrete_max_kr_physical": float(kr.max() / dx),
    }


def run_condition(
    *,
    p: int,
    sigma_phys: float,
    seed: int,
    n_real: int,
    route: str,
    do_contour: bool,
    do_shift: bool,
    do_phase: bool,
    domain_units: float = DOMAIN_UNITS,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    shape = target_shape(p, domain_units)
    margin = margin_for_p(p)
    s, kx, ky, kr, k0_px, sigma_px = gaussian_spectrum(shape, p, sigma_phys)
    n_pred_px = discrete_prediction(s, kx)
    n_cont_phys, cont_meta = continuum_prediction(sigma_phys)
    dx = LAMBDA_PHYS / p
    # A pixel covers dx^2 physical area, hence density per pixel is
    # n_physical*dx^2 (and the inverse recovers physical density).
    n_cont_px = n_cont_phys * dx * dx
    diag = truncation_diagnostics(s, kx, ky, kr, p, sigma_phys)
    diag.update({
        "shape_yx": shape,
        "margin_px": margin,
        "roi_cells": int((shape[0] - 2 * margin - 1) * (shape[1] - 2 * margin - 1)),
        "k0_px": k0_px,
        "sigma_px": sigma_px,
        "n_pred_discrete_px": n_pred_px,
        "n_pred_discrete_physical": n_pred_px / (dx * dx),
        "n_pred_continuum_px": n_cont_px,
        "n_pred_continuum_physical": n_cont_phys,
        "continuum_quad": cont_meta,
    })
    rows: list[dict[str, Any]] = []
    label = f"EXP-0003-broadband-audit-p{p}-sig{sigma_phys:.2f}-s{seed}-r{route}"
    gen, rng_info = make_gen(route, label, seed)
    for realization in range(n_real):
        e = complex_field_canonical(shape, s, gen)
        n, plus, minus = winding_counts(e, margin)
        rec: dict[str, Any] = {
            "p": p,
            "sigma_phys": sigma_phys,
            "seed": seed,
            "realization": realization,
            "route": route,
            "shape_y": shape[0],
            "shape_x": shape[1],
            "margin_px": margin,
            "k0_px": k0_px,
            "sigma_px": sigma_px,
            "n_pred_discrete_px": n_pred_px,
            "n_pred_continuum_px": n_cont_px,
            "n_meas_px": n,
            "n_plus_px": plus,
            "n_minus_px": minus,
            "ratio_discrete": n / n_pred_px,
            "ratio_continuum": n / n_cont_px,
            "fd_pred_px": fd_prediction(e),
            "fft_pred_px": fft_prediction(e),
            "charge_imbalance": abs(plus - minus) / n if n else None,
            "zero_fraction": float(np.mean(np.abs(e) < 1e-12)),
        }
        if do_phase:
            rec.update(phase_edge_stats(e))
        if do_contour:
            rec["contour_px"] = contour_density(e, margin)
            rec["contour_naive_px"] = contour_naive_density(e, margin)
            rec["contour_ratio_discrete"] = rec["contour_px"] / n_pred_px
            rec["contour_ratio_continuum"] = rec["contour_px"] / n_cont_px
        if do_shift:
            es = shift_field(e, 0.5, 0.5)
            ns, _, _ = winding_counts(es, margin)
            es2 = shift_field(e, 0.37, 0.61)
            ns2, _, _ = winding_counts(es2, margin)
            rec["shift_half_density_px"] = ns
            rec["shift_irregular_density_px"] = ns2
            rec["shift_half_rel_delta"] = abs(ns - n) / n if n else None
            rec["shift_irregular_rel_delta"] = abs(ns2 - n) / n if n else None
        rec["rng_provenance"] = rng_info
        rows.append(rec)
    return rows, diag


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize a row group while tolerating targeted-control schemas."""
    if not rows:
        return {}
    by_seed: dict[int, list[dict[str, Any]]] = {}
    for r in rows:
        if "seed" in r:
            by_seed.setdefault(int(r["seed"]), []).append(r)

    def vals(key: str) -> list[float]:
        return [float(r[key]) for r in rows if r.get(key) is not None and np.isfinite(float(r[key]))]

    summary: dict[str, Any] = {
        "n_rows": len(rows),
        "n_real_total": len(rows),
        "n_seeds": len(by_seed),
        "n_real_per_seed": {str(k): len(v) for k, v in by_seed.items()},
    }
    for key in (
        "ratio_discrete", "ratio_continuum", "ratio_filtered", "ratio",
        "n_meas_px", "fd_pred_px", "fft_pred_px", "charge_imbalance",
        "contour_px", "contour_ratio_discrete", "contour_ratio_continuum", "contour_naive_px",
        "shift_half_rel_delta", "shift_irregular_rel_delta",
        "edge_phase_frac_gt_0.9pi", "edge_phase_frac_gt_0.99pi", "edge_phase_abs_p99",
    ):
        if key in rows[0] or any(key in r for r in rows):
            summary[key] = summarize(vals(key))
    for key in ("n_pred_discrete_px", "n_pred_continuum_px", "n_pred_mode_px", "n_pred_filtered_px"):
        if key in rows[0] or any(key in r for r in rows):
            vv = vals(key)
            if vv:
                summary[key] = float(vv[0])
    # Seed-block means are the primary uncertainty view for the main ladder.
    for source, target in (("ratio_discrete", "seed_block_ratio_discrete"),
                           ("ratio_continuum", "seed_block_ratio_continuum"),
                           ("ratio", "seed_block_ratio")):
        if source in rows[0] or any(source in r for r in rows):
            means = {}
            for seed, rr in by_seed.items():
                vv = [float(r[source]) for r in rr if r.get(source) is not None]
                if vv:
                    means[str(seed)] = float(np.mean(vv))
            if means:
                summary[f"seed_mean_{source}"] = means
                summary[target] = summarize(list(means.values()))
    return summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    keys: list[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            rr = dict(r)
            # Keep nested RNG provenance out of the flat table.
            rr.pop("rng_provenance", None)
            w.writerow(rr)


def run_primary(out: Path, n_real: int, route: str) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for sigma in SIGMA_LIST:
        for p in P_LIST:
            t0 = time.perf_counter()
            for seed in SEEDS:
                rr, dd = run_condition(
                    p=p, sigma_phys=sigma, seed=seed, n_real=n_real, route=route,
                    do_contour=(seed in (42, 123, 314159)),
                    do_shift=(seed in (42, 7, 2023)),
                    do_phase=(seed == 42),
                )
                rows.extend(rr)
                diagnostics.append(dd)
            print(f"primary route={route} sigma={sigma:.2f} p={p:2d} n={target_shape(p)[0]:4d} elapsed={time.perf_counter()-t0:.1f}s", flush=True)
    raw_path = out / f"primary_{route}_raw.csv"
    write_csv(raw_path, rows)
    grouped: dict[str, Any] = {}
    for sigma in SIGMA_LIST:
        for p in P_LIST:
            sub = [r for r in rows if r["sigma_phys"] == sigma and r["p"] == p]
            grouped[f"sigma_{sigma:.2f}_p{p}"] = summarize_rows(sub)
    payload = {
        "experiment": "EXP-0003-broadband-resolution-audit",
        "route": route,
        "n_real_per_seed": n_real,
        "seeds": list(SEEDS),
        "p_list": list(P_LIST),
        "sigma_list": list(SIGMA_LIST),
        "k0_phys": K0_PHYS,
        "domain_units": DOMAIN_UNITS,
        "raw_rows": len(rows),
        "grouped": grouped,
        "diagnostics": diagnostics,
        "rng_note": "certified route uses engine.utilities.core.rng; pcg64 route is separate",
    }
    json_dump(out / f"primary_{route}_summary.json", payload)
    return payload


def run_common_field(out: Path, ref_p: int, p_list: tuple[int, ...], n_real: int, route: str) -> dict[str, Any]:
    """Nested exact common-field test.

    A field is generated once at reference resolution (ref_p, N=32*ref_p).
    Lower-resolution samples are exact every-(ref_p/P)-th samples when P divides
    ref_p.  No interpolation is used, so this is a clean test of sampling/aliasing
    for one fixed periodic band-limited realization.
    """
    shape = target_shape(ref_p)
    ref_margin = margin_for_p(ref_p)
    rows: list[dict[str, Any]] = []
    diags: list[dict[str, Any]] = []
    for sigma in SIGMA_LIST:
        ref_s, ref_kx, _, ref_kr, _, _ = gaussian_spectrum(shape, ref_p, sigma)
        ref_npred = discrete_prediction(ref_s, ref_kx)
        ncont, _ = continuum_prediction(sigma)
        for seed in SEEDS:
            label = f"EXP-0003-commonfield-ref{ref_p}-sig{sigma:.2f}-s{seed}-r{route}"
            gen, _ = make_gen(route, label, seed)
            for realization in range(n_real):
                ref = complex_field_canonical(shape, ref_s, gen)
                for p in p_list:
                    if ref_p % p != 0:
                        continue
                    stride = ref_p // p
                    e = ref[::stride, ::stride]
                    # Exact target spectrum/prediction for the sampled lattice.
                    s, kx, _, kr, _, _ = gaussian_spectrum(e.shape, p, sigma)
                    npred = discrete_prediction(s, kx)
                    margin = margin_for_p(p)
                    n, plus, minus = winding_counts(e, margin)
                    rec = {
                        "ref_p": ref_p,
                        "p": p,
                        "stride": stride,
                        "sigma_phys": sigma,
                        "seed": seed,
                        "realization": realization,
                        "shape_ref": f"{shape[0]}x{shape[1]}",
                        "shape_sampled": f"{e.shape[0]}x{e.shape[1]}",
                        "n_meas_px": n,
                        "n_pred_discrete_px": npred,
                        "n_pred_reference_px": ref_npred,
                        "n_pred_continuum_px": ncont * ((LAMBDA_PHYS / p) ** 2),
                        "ratio_discrete": n / npred,
                        "ratio_continuum": n / (ncont * ((LAMBDA_PHYS / p) ** 2)),
                        "charge_imbalance": abs(plus - minus) / n if n else None,
                        "fd_pred_px": fd_prediction(e),
                    }
                    rows.append(rec)
            print(f"common ref_p={ref_p} sigma={sigma:.2f} seed={seed}", flush=True)
    write_csv(out / f"common_field_ref{ref_p}_raw.csv", rows)
    grouped: dict[str, Any] = {}
    for sigma in SIGMA_LIST:
        for p in p_list:
            sub = [r for r in rows if r["sigma_phys"] == sigma and r["p"] == p]
            if sub:
                grouped[f"sigma_{sigma:.2f}_p{p}"] = summarize_rows(sub)
    payload = {
        "experiment": "EXP-0003-broadband-common-field-audit",
        "ref_p": ref_p,
        "p_list": list(p_list),
        "sigma_list": list(SIGMA_LIST),
        "seeds": list(SEEDS),
        "n_real_per_seed": n_real,
        "route": route,
        "method": "exact nested subsampling of one fixed periodic field; no interpolation",
        "rows": len(rows),
        "grouped": grouped,
    }
    json_dump(out / f"common_field_ref{ref_p}_summary.json", payload)
    return payload


def run_lowpass(out: Path, n_real: int) -> dict[str, Any]:
    """Targeted spectral-cutoff control on the original P=4-style grid and a resolved grid."""
    rows: list[dict[str, Any]] = []
    for sigma in (0.50, 0.75):
        for p in (4, 8, 16, 32, 64):
            shape = target_shape(p)
            margin = margin_for_p(p)
            s, kx, _, _, _, _ = gaussian_spectrum(shape, p, sigma)
            for seed in (42, 123, 2023):
                gen, _ = make_gen("certified", f"EXP-0003-lowpass-p{p}-sig{sigma}-s{seed}", seed)
                for realization in range(n_real):
                    e = complex_field_canonical(shape, s, gen)
                    for frac in (0.25, 0.50, 0.75, 1.00):
                        cutoff = frac * np.pi
                        ef = lowpass_field(e, cutoff)
                        sf = s.copy()
                        _, _, krf, _ = freq_arrays(shape)
                        sf[krf > cutoff] = 0.0
                        npf = discrete_prediction(sf, kx)
                        n, _, _ = winding_counts(ef, margin)
                        rows.append({
                            "p": p, "sigma_phys": sigma, "seed": seed, "realization": realization,
                            "cutoff_fraction_of_axis_nyquist": frac, "cutoff_px": cutoff,
                            "n_meas_px": n, "n_pred_filtered_px": npf,
                            "ratio_filtered": n / npf if npf else None,
                            "retained_power_fraction": float(sf.sum() / s.sum()),
                        })
            print(f"lowpass sigma={sigma:.2f} p={p}", flush=True)
    write_csv(out / "lowpass_raw.csv", rows)
    grouped: dict[str, Any] = {}
    for sigma in (0.50, 0.75):
        for p in (4, 8, 16, 32, 64):
            for frac in (0.25, 0.50, 0.75, 1.00):
                sub = [r for r in rows if r["sigma_phys"] == sigma and r["p"] == p and r["cutoff_fraction_of_axis_nyquist"] == frac]
                if sub:
                    grouped[f"sigma_{sigma:.2f}_p{p}_cut{frac:.2f}"] = summarize_rows(sub)
    payload = {"experiment": "EXP-0003-broadband-lowpass-audit", "rows": len(rows), "grouped": grouped}
    json_dump(out / "lowpass_summary.json", payload)
    return payload


def run_nonstandard(out: Path, n_real: int) -> dict[str, Any]:
    """Non-square/non-power-of-two shape check at fixed physical spectral law."""
    rows: list[dict[str, Any]] = []
    # At P=8, target square is 256; these grids retain dx=1/8 but slightly
    # different physical side lengths, so they test implementation/shape only.
    shapes = ((255, 255), (257, 257), (255, 257), (257, 255), (253, 259))
    p = 8
    for sigma in SIGMA_LIST:
        for shape in shapes:
            margin = 12
            s, kx, _, _, _, _ = gaussian_spectrum(shape, p, sigma)
            npred = discrete_prediction(s, kx)
            for seed in (42, 123):
                gen, _ = make_gen("certified", f"EXP-0003-nonstandard-{shape}-sig{sigma}-s{seed}", seed)
                for realization in range(n_real):
                    e = complex_field_canonical(shape, s, gen)
                    n, plus, minus = winding_counts(e, margin)
                    rows.append({
                        "shape_y": shape[0], "shape_x": shape[1], "p": p, "sigma_phys": sigma,
                        "seed": seed, "realization": realization, "margin_px": margin,
                        "n_meas_px": n, "n_pred_discrete_px": npred, "ratio_discrete": n / npred,
                        "charge_imbalance": abs(plus - minus) / n if n else None,
                    })
            print(f"nonstandard shape={shape} sigma={sigma:.2f}", flush=True)
    write_csv(out / "nonstandard_raw.csv", rows)
    grouped: dict[str, Any] = {}
    for shape in shapes:
        for sigma in SIGMA_LIST:
            sub = [r for r in rows if (r["shape_y"], r["shape_x"]) == shape and r["sigma_phys"] == sigma]
            grouped[f"{shape[0]}x{shape[1]}_sigma_{sigma:.2f}"] = summarize_rows(sub)
    payload = {"experiment": "EXP-0003-broadband-nonstandard-grid-audit", "rows": len(rows), "grouped": grouped}
    json_dump(out / "nonstandard_summary.json", payload)
    return payload


def run_small_plane_wave_check(out: Path, n_real: int) -> dict[str, Any]:
    """Independent plane-wave construction check at P=4 and P=16.

    This is deliberately small and diagnostic; it does not replace the
    canonical replication.  The mode-weighted Kac--Rice prediction is used.
    """
    rows: list[dict[str, Any]] = []
    modes = 3000
    for sigma in (0.10, 0.25, 0.50, 0.75):
        for p in (4, 8, 16, 32):
            n = min(256, max(96, 32 * p))
            margin = margin_for_p(p)
            for seed in (42, 123):
                gen, _ = make_gen("pcg64", f"EXP-0003-plane-audit-p{p}-sig{sigma}-s{seed}", seed)
                for realization in range(n_real):
                    # Draw radial k from p(k) proportional to k*S(k), then angle.
                    # Rejection sampling is robust for the narrow sigma=.10 case.
                    vals = []
                    while len(vals) < modes:
                        batch = gen.uniform(0.0, K0_PHYS + 8.0 * sigma, 4 * modes)
                        w = batch * np.exp(-0.5 * ((batch - K0_PHYS) / sigma) ** 2)
                        vals.extend(batch[w > 0].tolist())
                    kr = np.asarray(vals[:modes], dtype=float)
                    theta = gen.uniform(0.0, 2.0 * np.pi, modes)
                    dx = LAMBDA_PHYS / p
                    kx = kr * np.cos(theta) * dx
                    ky = kr * np.sin(theta) * dx
                    c = gen.standard_normal(modes) + 1j * gen.standard_normal(modes)
                    x = np.arange(n) * dx
                    # Chunked separable evaluation limits peak memory.
                    e = np.zeros((n, n), dtype=np.complex128)
                    for start in range(0, modes, 256):
                        stop = min(modes, start + 256)
                        u = np.exp(1j * np.outer(x, kx[start:stop])) * c[start:stop]
                        v = np.exp(1j * np.outer(x, ky[start:stop]))
                        e += (u @ v.T)
                    pred = float(np.sum(np.abs(c) ** 2 * kx**2) / np.sum(np.abs(c) ** 2) / (2.0 * np.pi))
                    dens, _, _ = winding_counts(e, margin)
                    rows.append({
                        "p": p, "sigma_phys": sigma, "seed": seed, "realization": realization,
                        "shape_yx": f"{n}x{n}", "modes": modes, "n_meas_px": dens,
                        "n_pred_mode_px": pred, "ratio": dens / pred,
                    })
            print(f"plane-wave p={p} sigma={sigma:.2f}", flush=True)
    write_csv(out / "plane_wave_check_raw.csv", rows)
    grouped: dict[str, Any] = {}
    for sigma in (0.10, 0.25, 0.50, 0.75):
        for p in (4, 8, 16, 32):
            sub = [r for r in rows if r["sigma_phys"] == sigma and r["p"] == p]
            if sub:
                grouped[f"sigma_{sigma:.2f}_p{p}"] = summarize_rows(sub)
    payload = {"experiment": "EXP-0003-broadband-plane-wave-check", "rows": len(rows), "grouped": grouped}
    json_dump(out / "plane_wave_check_summary.json", payload)
    return payload


def environment() -> dict[str, Any]:
    return {
        "timestamp_utc": utc_now(),
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "numpy": np.__version__,
        "scipy": __import__("scipy").__version__,
        "script_sha256": sha256_file(Path(__file__)),
        "command": " ".join([sys.executable, *sys.argv]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-real", type=int, default=8, help="realizations per seed in primary/common tests")
    ap.add_argument("--skip-primary", action="store_true")
    ap.add_argument("--skip-common", action="store_true")
    ap.add_argument("--skip-controls", action="store_true")
    ap.add_argument("--only", choices=["all", "primary", "common", "controls"], default="all")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    env = environment()
    json_dump(OUT / "run_environment.json", env)
    summary: dict[str, Any] = {"environment": env, "started_utc": env["timestamp_utc"]}
    t0 = time.perf_counter()
    if args.only in ("all", "primary") and not args.skip_primary:
        summary["primary_certified"] = run_primary(OUT, args.n_real, "certified")
        # Independent PCG64 route is a validation subset, not a replacement.
        summary["primary_pcg64"] = run_primary(OUT, max(3, args.n_real // 2), "pcg64")
    if args.only in ("all", "common") and not args.skip_common:
        summary["common_ref64"] = run_common_field(OUT, 64, (4, 8, 16, 32, 64), max(3, args.n_real // 2), "certified")
        summary["common_ref48"] = run_common_field(OUT, 48, (6, 12, 24, 48), max(3, args.n_real // 2), "certified")
    if args.only in ("all", "controls") and not args.skip_controls:
        summary["lowpass"] = run_lowpass(OUT, max(2, args.n_real // 2))
        summary["nonstandard"] = run_nonstandard(OUT, max(2, args.n_real // 2))
        summary["plane_wave"] = run_small_plane_wave_check(OUT, max(1, args.n_real // 3))
    summary["finished_utc"] = utc_now()
    summary["elapsed_seconds"] = time.perf_counter() - t0
    json_dump(OUT / "run_summary.json", summary)
    print(json.dumps({"out": str(OUT), "elapsed_seconds": summary["elapsed_seconds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
