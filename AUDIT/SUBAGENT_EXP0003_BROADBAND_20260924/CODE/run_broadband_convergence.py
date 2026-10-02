"""Independent EXP-0003 broadband vortex-density convergence audit.

This script is deliberately self-contained: it does not import the historical
EXP-0003 implementation or the shared RNG.  It writes only below
AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/.

The principal sweep samples one fixed physical Gaussian radial spectrum at
physical pixel pitches corresponding to P = 4,6,8,12,16,24,32,48,64 samples
per central wavelength.  The physical box is held fixed at WAVELENGTHS
central wavelengths, so N = P * WAVELENGTHS.  At P=4 this has the same
normalized spectral cutoff relative to k0 as the historical N=512 cell only
when WAVELENGTHS is chosen appropriately; the physical definition used here is
more important than matching that arbitrary box size.

Definitions
-----------
k0_phys = pi/2 rad per physical unit (the EXP-0003 reference-pixel scale).
At sampling parameter P, dx = 2*pi/(k0_phys*P), hence
k0_dimensionless = k0_phys*dx = 2*pi/P.
The EXP-0003 sigma values are already in the same physical reference-pixel
units, so sigma_phys = sigma_EXP.  Thus the physical Gaussian widths are held
fixed as dx changes, while the dimensionless spectrum is evaluated as
S(k_dim)=exp(-((k_dim/dx-k0_phys)^2)/(2*sigma_EXP^2)).  At P=4 this
reproduces EXP-0003's k0=pi/2 and sigma_k values exactly (up to the smaller
independent physical box used here).  The fixed ratios are
sigma_k/k0_phys = [0.06366,0.15915,0.31831,0.47746].

The reported Kac--Rice prediction is the continuous isotropic integral
n_phys = (1/(4*pi)) * integral k^3 S(k) dk / integral k S(k) dk.
The corresponding cell density is n_phys*dx^2.  We also record the finite
DFT-mode prediction and the continuous prediction after applying the current
Nyquist cutoff; these distinguish truncation/aliasing from detector error.

Run from the laboratory root:
    python AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE/run_broadband_convergence.py
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
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

import numpy as np

try:
    from scipy.integrate import quad
    from scipy.stats import linregress
except Exception:  # pragma: no cover - environment is expected to have scipy
    quad = None
    linregress = None

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover
    plt = None


HERE = Path(__file__).resolve().parent
AUDIT = HERE.parent
RESULTS = AUDIT / "RESULTS"
LOGS = AUDIT / "LOGS"
REPORT = AUDIT / "REPORT"
for d in (RESULTS, LOGS, REPORT):
    d.mkdir(parents=True, exist_ok=True)

# Physical experiment choices.
P_VALUES = (4, 6, 8, 12, 16, 24, 32, 48, 64)
SIGMA_EXP = (0.10, 0.25, 0.50, 0.75)
SEEDS = (42, 7, 123, 2023, 314159, 271828)
KAPPA0 = np.pi / 2.0
WAVELENGTHS = 24
BASE_EXP_P = 4
SIGMA_PHYS = {s: float(s) for s in SIGMA_EXP}
MARGIN_WAVELENGTHS = 1.0
N_BOOT = 2000
RNG_TAG = 0xE11A0BE

# The master fixed-field control uses a nested grid.  P=32 is sufficient to
# resolve the Gaussian tails for all four EXP-0003 widths (max k=16*k0).
FIXED_MASTER_P = 32
FIXED_P_VALUES = (4, 8, 16, 32)


def jsonable(x: Any) -> Any:
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, Path):
        return str(x)
    raise TypeError(type(x).__name__)


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=jsonable) + "\n", encoding="utf-8")


def rng_for(seed: int, sigma: float, p: int, realization: int, tag: int = RNG_TAG) -> np.random.Generator:
    """Independent NumPy PCG64 stream for every field."""
    # SeedSequence avoids relying on Python hash randomization or shared engine state.
    entropy = [int(seed), int(round(float(sigma) * 1_000_000)), int(p), int(realization), int(tag)]
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(entropy)))


def fft_kx(nx: int, ny: int | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if ny is None:
        ny = nx
    fx = 2.0 * np.pi * np.fft.fftfreq(nx)
    fy = 2.0 * np.pi * np.fft.fftfreq(ny)
    KX, KY = np.meshgrid(fx, fy, indexing="xy")
    return KX, KY, np.hypot(KX, KY)


def make_spectrum(
    ny: int,
    nx: int,
    dx: float,
    sigma_phys: float,
    cutoff_kappa0: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return S, KX, KY, KR_phys for the physical isotropic Gaussian spectrum."""
    KX, KY, KR = fft_kx(nx, ny)
    KR_phys = KR / dx
    z = (KR_phys - KAPPA0) / sigma_phys
    S = np.exp(-0.5 * z * z)
    if cutoff_kappa0 is not None:
        S = S * (KR_phys <= cutoff_kappa0 * KAPPA0)
    return S, KX, KY, KR_phys


def discrete_prediction(S: np.ndarray, KX: np.ndarray) -> float:
    """Kac--Rice density per pixel cell using the sampled DFT modes."""
    den = float(S.sum())
    if den <= 0.0:
        return float("nan")
    return float((KX * KX * S).sum() / den / (2.0 * np.pi))


def continuum_prediction(sigma_phys: float, cutoff_kappa0: float | None = None) -> float:
    """Continuous isotropic Kac--Rice density (physical units), radial integral."""
    if quad is None:
        # Deterministic fallback, adequate for the Gaussian tails used here.
        kmax = 100.0 if cutoff_kappa0 is None else cutoff_kappa0 * KAPPA0
        k = np.linspace(0.0, kmax, 2000001)
        s = np.exp(-0.5 * ((k - KAPPA0) / sigma_phys) ** 2)
        return float(np.trapezoid(k**3 * s, k) / (4.0 * np.pi * np.trapezoid(k * s, k)))
    kmax = 100.0 if cutoff_kappa0 is None else cutoff_kappa0 * KAPPA0

    def s(k: float) -> float:
        return math.exp(-0.5 * ((k - KAPPA0) / sigma_phys) ** 2)

    den = quad(lambda k: k * s(k), 0.0, kmax, epsabs=1e-11, epsrel=1e-10, limit=200)[0]
    num = quad(lambda k: k**3 * s(k), 0.0, kmax, epsabs=1e-11, epsrel=1e-10, limit=200)[0]
    return float(num / (4.0 * np.pi * den))


def corrected_real_field(component_spectrum: np.ndarray, gen: np.random.Generator) -> np.ndarray:
    """Generate a real Gaussian field with correct Hermitian self-mode handling.

    Historical EXP-0003 symmetrized complex coefficients at self-conjugate
    locations too, which halves the variance of the (0,0), (0,N/2), ...
    coefficients.  This independent route treats those coefficients as real
    with the requested variance.
    """
    ny, nx = component_spectrum.shape
    coeff = np.sqrt(component_spectrum) * (
        gen.standard_normal((ny, nx)) + 1j * gen.standard_normal((ny, nx))
    )
    ix = (-np.arange(nx)) % nx
    iy = (-np.arange(ny)) % ny
    coeff = 0.5 * (coeff + np.conj(coeff[np.ix_(iy, ix)]))
    # A self-conjugate coefficient must be real, not a symmetrized complex draw.
    corners = {(0, 0), (0, nx // 2), (ny // 2, 0), (ny // 2, nx // 2)}
    for iy0, ix0 in corners:
        coeff[iy0, ix0] = np.sqrt(component_spectrum[iy0, ix0]) * gen.standard_normal()
    return np.real(np.fft.ifft2(coeff))


def historical_real_field(component_spectrum: np.ndarray, gen: np.random.Generator) -> np.ndarray:
    """The exact historical symmetrization route, for an implementation control."""
    ny, nx = component_spectrum.shape
    coeff = np.sqrt(component_spectrum) * (
        gen.standard_normal((ny, nx)) + 1j * gen.standard_normal((ny, nx))
    )
    ix = (-np.arange(nx)) % nx
    iy = (-np.arange(ny)) % ny
    coeff = 0.5 * (coeff + np.conj(coeff[np.ix_(iy, ix)]))
    return np.real(np.fft.ifft2(coeff))


def legacy_nested_real_field(argument_spectrum: np.ndarray, gen: np.random.Generator) -> np.ndarray:
    """Reproduce historical real_gaussian's internal sqrt(argument/2) factor."""
    return historical_real_field(0.5 * argument_spectrum, gen)


def legacy_nested_complex_field(S: np.ndarray, gen: np.random.Generator) -> np.ndarray:
    """Historical complex_field(complex_field passes S/2 into a /2 routine)."""
    return legacy_nested_real_field(0.5 * S, gen) + 1j * legacy_nested_real_field(0.5 * S, gen)


def make_field(S: np.ndarray, gen: np.random.Generator, route: str = "corrected") -> np.ndarray:
    fn = corrected_real_field if route == "corrected" else historical_real_field
    u = fn(0.5 * S, gen)
    v = fn(0.5 * S, gen)
    return u + 1j * v


def direct_complex_field(S: np.ndarray, gen: np.random.Generator) -> np.ndarray:
    """Independent construction: arbitrary complex Fourier coefficients.

    E is itself complex, so its Fourier coefficients need not satisfy Hermitian
    symmetry.  This route avoids the real-component/Hermitian-pair code used by
    the main generator and is an independent construction check, not merely a
    rerun of the same implementation.
    """
    coeff = np.sqrt(S) * (gen.standard_normal(S.shape) + 1j * gen.standard_normal(S.shape))
    return np.fft.ifft2(coeff)


def margin_for(p: int) -> int:
    return max(2, int(round(MARGIN_WAVELENGTHS * p)))


def winding_metrics(E: np.ndarray, margin: int) -> dict[str, float]:
    """Principal-increment plaquette winding; no global phase unwrapping."""
    ex = np.angle(E[:, 1:] * np.conj(E[:, :-1]))
    ey = np.angle(E[1:, :] * np.conj(E[:-1, :]))
    circ = ex[:-1, :] + ey[:, 1:] - ex[1:, :] - ey[:, :-1]
    w = np.rint(circ / (2.0 * np.pi)).astype(np.int16)
    wc = w[margin:-margin, margin:-margin]
    area = float(wc.size)
    nz = wc != 0
    return {
        "winding_density": float(nz.sum() / area),
        "winding_abs_density": float(np.abs(wc).sum() / area),
        "winding_plus_density": float((wc > 0).sum() / area),
        "winding_minus_density": float((wc < 0).sum() / area),
        "winding_charge_sum_density": float(wc.sum() / area),
        "winding_charge_imbalance": float(abs(wc.sum()) / max(1, np.abs(wc).sum())),
        "winding_abs_charge_max": float(np.max(np.abs(wc))),
        "winding_zero_vertex_samples": float(np.count_nonzero(E == 0)),
        "winding_edge_phase_max_abs": float(max(np.max(np.abs(ex)), np.max(np.abs(ey)))),
    }


def _edge_crossings(G: np.ndarray) -> tuple[np.ndarray, ...]:
    """Two linear zero-contour crossings per cell, with explicit edge tests."""
    ny, nx = G.shape
    jj, ii = np.meshgrid(np.arange(ny - 1), np.arange(nx - 1), indexing="ij")
    a, b = G[:-1, :-1], G[:-1, 1:]
    c, d = G[1:, :-1], G[1:, 1:]
    eps = 1e-14
    ta = np.abs(a) / (np.abs(a) + np.abs(b) + eps)
    tb = np.abs(c) / (np.abs(c) + np.abs(d) + eps)
    tl = np.abs(a) / (np.abs(a) + np.abs(c) + eps)
    tr = np.abs(b) / (np.abs(b) + np.abs(d) + eps)
    MT, MB, ML, MR = a * b < 0, c * d < 0, a * c < 0, b * d < 0
    ok = MT.astype(np.int8) + MB.astype(np.int8) + ML.astype(np.int8) + MR.astype(np.int8) == 2
    P1x = np.where(MT, jj + ta, np.where(MB, jj + tb, np.where(ML, jj, jj + 1)))
    P1y = np.where(MT, ii, np.where(MB, ii + 1, np.where(ML, ii + tl, ii)))
    P2x = np.where(MR, jj + 1, np.where(ML, jj, np.where(MB, jj + tb, jj + ta)))
    P2y = np.where(MR, ii + tr, np.where(ML, ii + tl, np.where(MB, ii + 1, ii)))
    return P1x, P1y, P2x, P2y, ok


def contour_metrics(E: np.ndarray, margin: int) -> dict[str, float]:
    """Independent Re=0/Im=0 segment-intersection detector."""
    ar = _edge_crossings(E.real)
    ai = _edge_crossings(E.imag)
    d1x, d1y = ar[2] - ar[0], ar[3] - ar[1]
    d2x, d2y = ai[2] - ai[0], ai[3] - ai[1]
    den = d1x * d2y - d1y * d2x
    wx, wy = ai[0] - ar[0], ai[1] - ar[1]
    with np.errstate(divide="ignore", invalid="ignore"):
        s = (wx * d2y - wy * d2x) / den
        u = (wx * d1y - wy * d1x) / den
    hit = ar[4] & ai[4] & (den != 0) & (s >= 0) & (s <= 1) & (u >= 0) & (u <= 1)
    z = hit[margin:-margin, margin:-margin]
    return {"contour_density": float(z.sum() / z.size)}


def fd_prediction(E: np.ndarray, kind: str = "forward") -> float:
    if kind == "forward":
        d = E[:, 1:] - E[:, :-1]
    elif kind == "central":
        d = 0.5 * (E[:, 2:] - E[:, :-2])
    else:
        raise ValueError(kind)
    return float((np.abs(d) ** 2).mean() / (2.0 * np.pi * (np.abs(E) ** 2).mean()))


def shift_field(E: np.ndarray, dx: float, dy: float) -> np.ndarray:
    ny, nx = E.shape
    fy = np.fft.fftfreq(ny)
    fx = np.fft.fftfreq(nx)
    ramp = np.exp(-2j * np.pi * (fy[:, None] * dy + fx[None, :] * dx))
    return np.fft.ifft2(np.fft.fft2(E) * ramp)


def fourier_refine(E: np.ndarray, factor: int) -> np.ndarray:
    """Explicit trigonometric (Fourier) band-limited interpolation.

    Zero-padding the centered DFT is exact interpolation of the periodic
    band-limited interpolant, not nearest-neighbour or bilinear upsampling.
    The amplitude is rescaled so the refined samples have the same physical
    field amplitude as the original samples.
    """
    if factor not in (2, 4) or E.shape[0] != E.shape[1] or E.shape[0] % 2:
        raise ValueError("refinement currently supports even square grids and factor 2 or 4")
    n = E.shape[0]
    m = n * factor
    centered = np.fft.fftshift(np.fft.fft2(E))
    padded = np.zeros((m, m), dtype=complex)
    lo = (m - n) // 2
    padded[lo:lo + n, lo:lo + n] = centered
    return np.fft.ifft2(np.fft.ifftshift(padded)) * (float(m * m) / float(n * n))


def refined_winding_density(E: np.ndarray, margin: int, factor: int) -> float:
    """Winding density per original pixel cell after Fourier refinement."""
    Er = fourier_refine(E, factor)
    mr = margin * factor
    wm = winding_metrics(Er, mr)
    # The refined cell area is dx^2/factor^2, so convert density per refined
    # cell back to density per original cell by multiplying by factor^2.
    return float(wm["winding_density"] * (factor * factor))


def row_base(p: int, sigma_exp: float, seed: int, realization: int, dx: float) -> dict[str, Any]:
    sigma_phys = SIGMA_PHYS[sigma_exp]
    return {
        "p_pixels_per_wavelength": p,
        "sigma_exp_rad_per_pixel_at_P4": sigma_exp,
        "sigma_physical": sigma_phys,
        "sigma_over_k0": sigma_phys / KAPPA0,
        "kappa0_physical": KAPPA0,
        "dx_physical": dx,
        "physical_box_wavelengths": WAVELENGTHS,
        "seed": seed,
        "realization": realization,
        "rng_route": "numpy_PCG64_SeedSequence",
    }


def run_realization(
    p: int,
    sigma_exp: float,
    seed: int,
    realization: int,
    *,
    detail: bool = False,
    route: str = "corrected",
    do_shifts: bool = False,
) -> dict[str, Any]:
    n = p * WAVELENGTHS
    dx = 2.0 * np.pi / (KAPPA0 * p)
    sigma_phys = SIGMA_PHYS[sigma_exp]
    S, KX, KY, KRphys = make_spectrum(n, n, dx, sigma_phys)
    pred_disc = discrete_prediction(S, KX)
    pred_cont_full_cell = continuum_prediction(sigma_phys) * dx * dx
    kmax_kappa0 = (n / 2.0) / WAVELENGTHS  # physical kmax/k0
    pred_cont_trunc_cell = continuum_prediction(sigma_phys, kmax_kappa0) * dx * dx
    m = margin_for(p)
    gen = rng_for(seed, sigma_exp, p, realization)
    E = make_field(S, gen, route=route)
    out = row_base(p, sigma_exp, seed, realization, dx)
    out.update({
        "n": n,
        "n_physical_kappa0": n / WAVELENGTHS,
        "nyquist_over_k0": kmax_kappa0,
        "margin_pixels": m,
        "roi_cells": (n - 2 * m - 1) ** 2,
        "spectral_prediction_discrete_cell": pred_disc,
        "spectral_prediction_cont_full_cell": pred_cont_full_cell,
        "spectral_prediction_cont_trunc_cell": pred_cont_trunc_cell,
        "spectral_prediction_discrete_physical": pred_disc / dx**2,
        "spectral_prediction_cont_full_physical": pred_cont_full_cell / dx**2,
        "spectral_prediction_cont_trunc_physical": pred_cont_trunc_cell / dx**2,
        "spectrum_power_sum": float(S.sum()),
        "spectrum_power_above_nyquist_master_reference": None,
    })
    wm = winding_metrics(E, m)
    out.update(wm)
    out["ratio_discrete"] = wm["winding_density"] / pred_disc
    out["ratio_cont_full"] = wm["winding_density"] / pred_cont_full_cell
    out["ratio_cont_trunc"] = wm["winding_density"] / pred_cont_trunc_cell
    out["ratio_abs_discrete"] = wm["winding_abs_density"] / pred_disc
    out["ratio_abs_cont_full"] = wm["winding_abs_density"] / pred_cont_full_cell
    out["fd_forward_prediction_cell"] = fd_prediction(E, "forward")
    out["fd_central_prediction_cell"] = fd_prediction(E, "central")
    out["fd_forward_over_discrete"] = out["fd_forward_prediction_cell"] / pred_disc
    out["fd_central_over_discrete"] = out["fd_central_prediction_cell"] / pred_disc
    if detail:
        out.update(contour_metrics(E, m))
        out["ratio_contour_discrete"] = out["contour_density"] / pred_disc
        out["ratio_contour_cont_full"] = out["contour_density"] / pred_cont_full_cell
        for label, (sx, sy) in {
            "shift_0p5_0p5": (0.5, 0.5),
            "shift_0p37_0p13": (0.37, 0.13),
            "shift_minus0p23_0p41": (-0.23, 0.41),
        }.items():
            Es = shift_field(E, sx, sy)
            ws = winding_metrics(Es, m)
            out[f"{label}_density"] = ws["winding_density"]
            out[f"{label}_rel_delta"] = abs(ws["winding_density"] - wm["winding_density"]) / max(wm["winding_density"], 1e-15)
    return out


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    # Preserve a stable union of keys, with the first row's natural order first.
    keys: list[str] = []
    seen = set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in keys})


def append_csv(path: Path, row: dict[str, Any], fieldnames: list[str] | None = None) -> None:
    new = not path.exists() or path.stat().st_size == 0
    if fieldnames is None:
        fieldnames = list(row)
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in fieldnames})


def bootstrap_ci(values: Iterable[float], seed: int, n_boot: int = N_BOOT, alpha: float = 0.01) -> tuple[float, float, float]:
    v = np.asarray(list(values), dtype=float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return float("nan"), float("nan"), float("nan")
    if v.size == 1:
        x = float(v[0])
        return x, x, 0.0
    gen = np.random.Generator(np.random.PCG64(np.random.SeedSequence([int(seed), 0xB007, v.size])))
    indices = gen.integers(0, v.size, size=(n_boot, v.size))
    means = v[indices].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi), float(np.std(v, ddof=1) / math.sqrt(v.size))


def aggregate_rows(rows: list[dict[str, Any]], ratio_key: str) -> list[dict[str, Any]]:
    groups: dict[tuple[int, float], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        groups[(int(r["p_pixels_per_wavelength"]), float(r["sigma_exp_rad_per_pixel_at_P4"]))].append(r)
    out = []
    for (p, s), rr in sorted(groups.items()):
        rec: dict[str, Any] = {
            "p_pixels_per_wavelength": p,
            "sigma_exp_rad_per_pixel_at_P4": s,
            "n_real": len(rr),
            "n_grid": rr[0]["n"],
            "nyquist_over_k0": rr[0]["nyquist_over_k0"],
            "pred_discrete_cell": rr[0]["spectral_prediction_discrete_cell"],
            "pred_cont_full_cell": rr[0]["spectral_prediction_cont_full_cell"],
            "pred_cont_trunc_cell": rr[0]["spectral_prediction_cont_trunc_cell"],
        }
        for key in ("winding_density", "winding_abs_density", "contour_density", "ratio_discrete", "ratio_cont_full", "ratio_cont_trunc", "ratio_abs_discrete", "ratio_abs_cont_full", "fd_forward_over_discrete", "fd_central_over_discrete"):
            vals = [float(x[key]) for x in rr if key in x and x[key] is not None and np.isfinite(float(x[key]))]
            if not vals:
                continue
            lo, hi, se = bootstrap_ci(vals, seed=10000 + p * 100 + int(round(s * 1000)))
            rec[f"{key}_mean"] = float(np.mean(vals))
            rec[f"{key}_std"] = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
            rec[f"{key}_se"] = se
            rec[f"{key}_ci99_low"] = lo
            rec[f"{key}_ci99_high"] = hi
            rec[f"{key}_n"] = len(vals)
        seed_means = []
        for seed in SEEDS:
            vv = [float(x[ratio_key]) for x in rr if int(x["seed"]) == seed and ratio_key in x]
            if vv:
                seed_means.append(float(np.mean(vv)))
        rec["seed_ratio_min"] = min(seed_means) if seed_means else float("nan")
        rec["seed_ratio_max"] = max(seed_means) if seed_means else float("nan")
        rec["seed_ratio_range"] = (max(seed_means) - min(seed_means)) if seed_means else float("nan")
        out.append(rec)
    # Trend diagnostics, separately for every ratio that is present.
    for s in sorted({r["sigma_exp_rad_per_pixel_at_P4"] for r in out}):
        rr = [r for r in out if r["sigma_exp_rad_per_pixel_at_P4"] == s]
        for key in ("ratio_discrete", "ratio_cont_full", "ratio_cont_trunc", "ratio_abs_cont_full", "ratio_contour_discrete"):
            vals = [(float(r["p_pixels_per_wavelength"]), float(r[f"{key}_mean"])) for r in rr if f"{key}_mean" in r]
            if len(vals) < 3:
                continue
            x = np.log2([v[0] for v in vals])
            y = np.array([v[1] for v in vals])
            if linregress is not None:
                fit = linregress(x, y)
                slope, intercept, rvalue, pvalue, stderr = [float(getattr(fit, q)) for q in ("slope", "intercept", "rvalue", "pvalue", "stderr")]
            else:
                slope = float(np.polyfit(x, y, 1)[0])
                intercept, rvalue, pvalue, stderr = [float("nan")] * 4
            for r in rr:
                r[f"{key}_trend_slope_per_doubling"] = slope
                r[f"{key}_trend_pvalue"] = pvalue
                r[f"{key}_trend_r2"] = rvalue * rvalue
            first, last = vals[0][1], vals[-1][1]
            for r in rr:
                r[f"{key}_abs_error_first"] = abs(first - 1.0)
                r[f"{key}_abs_error_last"] = abs(last - 1.0)
                r[f"{key}_endpoint_improvement"] = abs(first - 1.0) - abs(last - 1.0)
    return out


def make_main_plot(summary: list[dict[str, Any]]) -> None:
    if plt is None:
        return
    fig, ax = plt.subplots(figsize=(8.5, 5.2), dpi=150)
    for s in SIGMA_EXP:
        rr = [r for r in summary if float(r["sigma_exp_rad_per_pixel_at_P4"]) == s]
        if not rr:
            continue
        x = np.array([r["p_pixels_per_wavelength"] for r in rr], dtype=float)
        y = np.array([r.get("ratio_cont_full_mean", np.nan) for r in rr], dtype=float)
        lo = np.array([r.get("ratio_cont_full_ci99_low", np.nan) for r in rr], dtype=float)
        hi = np.array([r.get("ratio_cont_full_ci99_high", np.nan) for r in rr], dtype=float)
        ax.errorbar(x, y, yerr=[np.maximum(0.0, y - lo), np.maximum(0.0, hi - y)], marker="o", capsize=2, label=fr"$\sigma_k={s:.2f}$")
    ax.axhline(1.0, color="black", lw=0.8, ls="--")
    ax.set_xscale("log", base=2)
    ax.set_xticks(P_VALUES)
    ax.set_xticklabels([str(p) for p in P_VALUES])
    ax.set_xlabel("pixels per central wavelength P (fixed physical spectrum)")
    ax.set_ylabel("winding density / continuous Kac–Rice prediction")
    ax.set_title("EXP-0003 independent broadband convergence audit")
    ax.grid(alpha=0.25)
    ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "main_convergence.png")
    plt.close(fig)


def run_main(realizations: int, quick: bool = False) -> list[dict[str, Any]]:
    path = RESULTS / "main_rows.csv"
    if path.exists():
        path.unlink()
    all_rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    total = len(P_VALUES) * len(SIGMA_EXP) * len(SEEDS) * realizations
    done = 0
    fieldnames: list[str] | None = None
    for p in P_VALUES:
        for s in SIGMA_EXP:
            for seed in SEEDS:
                for rep in range(realizations):
                    # D2 is measured in a separate control so the principal
                    # sweep remains tractable at P=64.
                    row = run_realization(p, s, seed, rep, detail=False)
                    if fieldnames is None:
                        fieldnames = list(row)
                    append_csv(path, row, fieldnames)
                    all_rows.append(row)
                    done += 1
                    print(f"MAIN {done}/{total} P={p} sigma={s} seed={seed} rep={rep} ratio_full={row['ratio_cont_full']:.5f} ratio_disc={row['ratio_discrete']:.5f}", flush=True)
    summary = aggregate_rows(all_rows, "ratio_cont_full")
    write_csv(RESULTS / "main_summary.csv", summary)
    write_json(RESULTS / "main_summary.json", {
        "description": "Fixed physical Gaussian spectrum, independent PCG64 fields; ratios and 99% bootstrap intervals.",
        "rows": summary,
        "elapsed_seconds": time.perf_counter() - t0,
    })
    make_main_plot(summary)
    return all_rows


def run_detail_controls(realizations: int = 1) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in (4, 8, 16, 32):
        for s in (0.10, 0.50, 0.75):
            for seed in SEEDS:
                for rep in range(realizations):
                    r = run_realization(p, s, seed, rep, detail=True, do_shifts=True)
                    r["control_family"] = "detector_shift_fd"
                    rows.append(r)
                    print(f"DETAIL P={p} sigma={s} seed={seed} D1={r['ratio_discrete']:.4f} D2={r['ratio_contour_discrete']:.4f} shift={r['shift_0p5_0p5_rel_delta']:.4f}", flush=True)
    write_csv(RESULTS / "detail_controls.csv", rows)
    write_json(RESULTS / "detail_controls.json", rows)
    return rows


def run_margin_controls() -> list[dict[str, Any]]:
    """Check that the physical ROI margin is not producing the deficit."""
    rows: list[dict[str, Any]] = []
    for p in (4, 8, 16):
        for s in (0.10, 0.50, 0.75):
            n = p * WAVELENGTHS
            dx = 2.0 * np.pi / (KAPPA0 * p)
            S, KX, KY, KR = make_spectrum(n, n, dx, SIGMA_PHYS[s])
            pred = discrete_prediction(S, KX)
            for seed in SEEDS:
                E = make_field(S, rng_for(seed, s, p, 2100, tag=RNG_TAG + 97))
                for wavelengths in (0.5, 1.0, 2.0):
                    m = max(2, int(round(wavelengths * p)))
                    if 2 * m + 2 >= n:
                        continue
                    wm = winding_metrics(E, m)
                    r = row_base(p, s, seed, 0, dx)
                    r.update({
                        "control_family": "roi_margin",
                        "margin_wavelengths": wavelengths,
                        "margin_pixels": m,
                        "n": n,
                        "roi_cells": (n - 2 * m - 1) ** 2,
                        "spectral_prediction_discrete_cell": pred,
                        "winding_density": wm["winding_density"],
                        "ratio_discrete": wm["winding_density"] / pred,
                    })
                    rows.append(r)
            print(f"MARGIN P={p} sigma={s} complete", flush=True)
    write_csv(RESULTS / "margin_controls.csv", rows)
    write_json(RESULTS / "margin_controls.json", rows)
    return rows


def run_construction_controls() -> list[dict[str, Any]]:
    """Compare the real-component construction with direct complex Fourier draws."""
    rows: list[dict[str, Any]] = []
    for p in (4, 8, 16, 32):
        for s in (0.10, 0.50, 0.75):
            n = p * WAVELENGTHS
            dx = 2.0 * np.pi / (KAPPA0 * p)
            S, KX, KY, KR = make_spectrum(n, n, dx, SIGMA_PHYS[s])
            m = margin_for(p)
            pred = discrete_prediction(S, KX)
            for seed in SEEDS:
                g1 = rng_for(seed, s, p, 1800, tag=RNG_TAG + 83)
                g2 = rng_for(seed, s, p, 1800, tag=RNG_TAG + 84)
                E_corrected = make_field(S, g1, route="corrected")
                E_direct = direct_complex_field(S, g2)
                wc = winding_metrics(E_corrected, m)
                wd = winding_metrics(E_direct, m)
                r = row_base(p, s, seed, 0, dx)
                r.update({
                    "control_family": "independent_construction",
                    "n": n,
                    "margin_pixels": m,
                    "spectral_prediction_discrete_cell": pred,
                    "corrected_real_component_ratio": wc["winding_density"] / pred,
                    "direct_complex_fourier_ratio": wd["winding_density"] / pred,
                    "direct_minus_corrected": wd["winding_density"] / pred - wc["winding_density"] / pred,
                    "corrected_charge_imbalance": wc["winding_charge_imbalance"],
                    "direct_charge_imbalance": wd["winding_charge_imbalance"],
                })
                rows.append(r)
            print(f"CONSTRUCTION P={p} sigma={s} direct-corrected={np.mean([x['direct_minus_corrected'] for x in rows[-len(SEEDS):]]):.4f}", flush=True)
    write_csv(RESULTS / "construction_controls.csv", rows)
    write_json(RESULTS / "construction_controls.json", rows)
    return rows


def run_interpolation_controls() -> list[dict[str, Any]]:
    """Test whether the P=4 deficit is lost phase topology between samples."""
    rows: list[dict[str, Any]] = []
    for p in (4, 6, 8, 12, 16):
        for s in (0.10, 0.50, 0.75):
            for seed in SEEDS:
                n = p * WAVELENGTHS
                dx = 2.0 * np.pi / (KAPPA0 * p)
                S, KX, KY, KR = make_spectrum(n, n, dx, SIGMA_PHYS[s])
                gen = rng_for(seed, s, p, 1600, tag=RNG_TAG + 71)
                E = make_field(S, gen)
                m = margin_for(p)
                wm = winding_metrics(E, m)
                pred = discrete_prediction(S, KX)
                refined_ratios = {}
                for factor in (2, 4):
                    dens = refined_winding_density(E, m, factor)
                    refined_ratios[factor] = dens / pred
                    r = row_base(p, s, seed, 0, dx)
                    r.update({
                        "control_family": "fourier_bandlimited_interpolation",
                        "n": n,
                        "margin_pixels_original": m,
                        "refinement_factor": factor,
                        "refined_n": n * factor,
                        "spectral_prediction_discrete_cell": pred,
                        "winding_density_original": wm["winding_density"],
                        "winding_density_refined_per_original_cell": dens,
                        "ratio_original": wm["winding_density"] / pred,
                        "ratio_refined": dens / pred,
                        "refinement_gain": dens / max(wm["winding_density"], 1e-15),
                    })
                    rows.append(r)
                print(f"INTERP P={p} sigma={s} seed={seed} orig={wm['winding_density']/pred:.4f} x2={refined_ratios[2]:.4f} x4={refined_ratios[4]:.4f}", flush=True)
    write_csv(RESULTS / "interpolation_controls.csv", rows)
    write_json(RESULTS / "interpolation_controls.json", rows)
    return rows


def run_lowpass_controls() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cutoffs = (1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0, 32.0)
    for p in P_VALUES:
        n = p * WAVELENGTHS
        dx = 2.0 * np.pi / (KAPPA0 * p)
        grid_kmax = (n / 2.0) / WAVELENGTHS
        for s in (0.50, 0.75):
            sp = SIGMA_PHYS[s]
            for cutoff in cutoffs:
                if cutoff > grid_kmax + 1e-12:
                    continue
                for seed in SEEDS[:3]:
                    gen = rng_for(seed, s, p, 900 + int(cutoff * 100), tag=RNG_TAG + 11)
                    S, KX, KY, KR = make_spectrum(n, n, dx, sp, cutoff_kappa0=cutoff)
                    E = make_field(S, gen)
                    m = margin_for(p)
                    wm = winding_metrics(E, m)
                    pred_disc = discrete_prediction(S, KX)
                    pred_cont = continuum_prediction(sp, cutoff) * dx * dx
                    row = row_base(p, s, seed, 0, dx)
                    row.update({
                        "control_family": "lowpass",
                        "cutoff_over_k0": cutoff,
                        "grid_nyquist_over_k0": grid_kmax,
                        "n": n,
                        "margin_pixels": m,
                        "spectral_prediction_discrete_cell": pred_disc,
                        "spectral_prediction_cont_full_cell": continuum_prediction(sp) * dx * dx,
                        "spectral_prediction_cont_trunc_cell": pred_cont,
                        "winding_density": wm["winding_density"],
                        "winding_abs_density": wm["winding_abs_density"],
                        "ratio_discrete": wm["winding_density"] / pred_disc,
                        "ratio_cont_trunc": wm["winding_density"] / pred_cont,
                        "ratio_cont_full": wm["winding_density"] / (continuum_prediction(sp) * dx * dx),
                        "power_fraction_above_cutoff": float("nan"),
                    })
                    rows.append(row)
                    print(f"LOWPASS P={p} sigma={s} cutoff={cutoff:g} ratio_disc={row['ratio_discrete']:.4f}", flush=True)
    write_csv(RESULTS / "lowpass_controls.csv", rows)
    write_json(RESULTS / "lowpass_controls.json", rows)
    return rows


def run_non_square_controls() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    p = 8
    dx = 2.0 * np.pi / (KAPPA0 * p)
    for seed in SEEDS:
        for label, (ny, nx) in (("square_192x192", (192, 192)), ("rect_221x192", (221, 192)), ("rect_193x192", (193, 192))):
            S, KX, KY, KR = make_spectrum(ny, nx, dx, SIGMA_PHYS[0.75])
            gen = rng_for(seed, 0.75, p, 1200, tag=RNG_TAG + 23)
            E = make_field(S, gen)
            m = margin_for(p)
            wm = winding_metrics(E, m)
            pred = discrete_prediction(S, KX)
            r = row_base(p, 0.75, seed, 0, dx)
            r.update({
                "control_family": "non_square_grid",
                "grid_label": label,
                "ny": ny,
                "nx": nx,
                "n": nx,
                "margin_pixels": m,
                "physical_box_x_wavelengths": nx * dx / (2.0 * np.pi / KAPPA0),
                "physical_box_y_wavelengths": ny * dx / (2.0 * np.pi / KAPPA0),
                "spectral_prediction_discrete_cell": pred,
                "spectral_prediction_cont_full_cell": continuum_prediction(SIGMA_PHYS[0.75]) * dx * dx,
                "winding_density": wm["winding_density"],
                "ratio_discrete": wm["winding_density"] / pred,
                "ratio_cont_full": wm["winding_density"] / (continuum_prediction(SIGMA_PHYS[0.75]) * dx * dx),
            })
            rows.append(r)
            print(f"NONSQUARE {label} seed={seed} ratio={r['ratio_discrete']:.4f}", flush=True)
    write_csv(RESULTS / "non_square_controls.csv", rows)
    write_json(RESULTS / "non_square_controls.json", rows)
    return rows


def run_fixed_field_controls() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    p_master = FIXED_MASTER_P
    n_master = p_master * WAVELENGTHS
    dx_master = 2.0 * np.pi / (KAPPA0 * p_master)
    for s in SIGMA_EXP:
        sp = SIGMA_PHYS[s]
        S, KX, KY, KR = make_spectrum(n_master, n_master, dx_master, sp)
        pred_master_disc = discrete_prediction(S, KX)
        pred_master_full = continuum_prediction(sp)
        m_master = margin_for(p_master)
        for seed in SEEDS:
            gen = rng_for(seed, s, p_master, 0, tag=RNG_TAG + 37)
            E_master = make_field(S, gen)
            wm_master = winding_metrics(E_master, m_master)
            for p in FIXED_P_VALUES:
                factor = p_master // p
                if p_master % p:
                    raise ValueError("fixed-field grids must be nested")
                E = E_master[::factor, ::factor]
                n = p * WAVELENGTHS
                dx = 2.0 * np.pi / (KAPPA0 * p)
                m = margin_for(p)
                wm = winding_metrics(E, m)
                # Fraction of master spectral power outside this coarse grid's
                # Nyquist limit.  This is an explicit aliasing diagnostic.
                coarse_kmax = p / 2.0
                # `KR` returned by make_spectrum is already physical k.
                alias_fraction = float(S[KR > coarse_kmax * KAPPA0].sum() / S.sum())
                r = row_base(p, s, seed, 0, dx)
                r.update({
                    "control_family": "fixed_continuous_field_nested",
                    "master_p": p_master,
                    "master_n": n_master,
                    "master_spectral_prediction_discrete_cell": pred_master_disc,
                    "master_spectral_prediction_cont_full_physical": pred_master_full,
                    "master_winding_density": wm_master["winding_density"],
                    "master_ratio_to_cont_full": wm_master["winding_density"] / (pred_master_full * dx_master * dx_master),
                    "n": n,
                    "margin_pixels": m,
                    "nyquist_over_k0": p / 2.0,
                    "alias_power_fraction_master_above_coarse_nyquist": alias_fraction,
                    "spectral_prediction_discrete_cell": pred_master_disc * (dx / dx_master) ** 2,
                    "spectral_prediction_cont_full_cell": pred_master_full * dx * dx,
                    "spectral_prediction_cont_trunc_cell": continuum_prediction(sp, p / 2.0) * dx * dx,
                    "winding_density": wm["winding_density"],
                    "winding_abs_density": wm["winding_abs_density"],
                    "ratio_discrete": wm["winding_density"] / (pred_master_disc * (dx / dx_master) ** 2),
                    "ratio_cont_full": wm["winding_density"] / (pred_master_full * dx * dx),
                    "ratio_cont_trunc": wm["winding_density"] / (continuum_prediction(sp, p / 2.0) * dx * dx),
                    "ratio_to_master_d1": (wm["winding_density"] / (dx * dx)) / (wm_master["winding_density"] / (dx_master * dx_master)),
                })
                rows.append(r)
                print(f"FIXED sigma={s} seed={seed} P={p} ratio_full={r['ratio_cont_full']:.4f} ratio_master={r['ratio_to_master_d1']:.4f} alias={alias_fraction:.4g}", flush=True)
    write_csv(RESULTS / "fixed_field_controls.csv", rows)
    write_json(RESULTS / "fixed_field_controls.json", rows)
    return rows


def run_sanity_controls() -> dict[str, Any]:
    out: dict[str, Any] = {}
    # A known unit vortex at the center of a small periodic grid.
    n = 65
    yy, xx = np.mgrid[0:n, 0:n]
    # Put the zero between four samples; a zero exactly on a lattice vertex
    # is a singular test case for a plaquette winding implementation.
    Etest = (xx - n // 2 + 0.5) + 1j * (yy - n // 2 + 0.5)
    m = 4
    out["synthetic_unit_vortex"] = winding_metrics(Etest, m)
    out["synthetic_unit_vortex_contour"] = contour_metrics(Etest, m)
    # A zero exactly on a sample is a deliberately ill-posed lattice case;
    # record it rather than silently treating it as a detector failure.
    E_vertex = (xx - n // 2) + 1j * (yy - n // 2)
    out["synthetic_vertex_zero_edge_case"] = winding_metrics(E_vertex, m)

    # Hermitian implementation comparison and a deterministic repeat check.
    n = 96
    dx = 2.0 * np.pi / 8.0
    S, KX, KY, KR = make_spectrum(n, n, dx, SIGMA_PHYS[0.75])
    corrected_power = []
    historical_power = []
    legacy_nested_power = []
    for r in range(24):
        g1 = rng_for(42, 0.75, 8, 5000 + r, tag=RNG_TAG + 51)
        g2 = rng_for(42, 0.75, 8, 5000 + r, tag=RNG_TAG + 51)
        g3 = rng_for(42, 0.75, 8, 5000 + r, tag=RNG_TAG + 51)
        u1 = corrected_real_field(0.5 * S, g1)
        u2 = historical_real_field(0.5 * S, g2)
        E_legacy = legacy_nested_complex_field(S, g3)
        p1 = np.abs(np.fft.fft2(u1)) ** 2
        p2 = np.abs(np.fft.fft2(u2)) ** 2
        p3 = np.abs(np.fft.fft2(E_legacy)) ** 2
        expected = 0.5 * S
        # Least-squares amplitude calibration of the realized Fourier power
        # against the requested component spectrum.  Values near one mean the
        # Hermitian construction has the intended variance.
        corrected_power.append(float((p1 * expected).sum() / max(1e-30, (expected * expected).sum())))
        historical_power.append(float((p2 * expected).sum() / max(1e-30, (expected * expected).sum())))
        expected_complex = S
        legacy_nested_power.append(float((p3 * expected_complex).sum() / max(1e-30, (expected_complex * expected_complex).sum())))
    out["hermitian_self_conjugate_power_fraction"] = float(
        sum(0.5 * S[i, j] for i, j in ((0, 0), (0, n // 2), (n // 2, 0), (n // 2, n // 2))) / (0.5 * S.sum())
    )
    out["hermitian_corrected_over_target_power"] = {
        "mean": float(np.mean(corrected_power)),
        "std": float(np.std(corrected_power, ddof=1)),
    }
    out["hermitian_historical_symmetrization_over_target_power"] = {
        "mean": float(np.mean(historical_power)),
        "std": float(np.std(historical_power, ddof=1)),
    }
    out["legacy_nested_normalization_over_target_power"] = {
        "mean": float(np.mean(legacy_nested_power)),
        "std": float(np.std(legacy_nested_power, ddof=1)),
        "interpretation": "The historical complex_field passes S/2 into real_gaussian, which itself applies sqrt(S/2); this is a factor-1/2 power normalization, not a density-ratio cause because global amplitude cancels.",
    }
    # Exact repeat check: same stream and same condition must be bitwise stable.
    gA = rng_for(42, 0.75, 8, 777, tag=RNG_TAG + 61)
    gB = rng_for(42, 0.75, 8, 777, tag=RNG_TAG + 61)
    Sa, _, _, _ = make_spectrum(96, 96, dx, SIGMA_PHYS[0.75])
    Ea = make_field(Sa, gA)
    Eb = make_field(Sa, gB)
    out["determinism_bitwise_equal"] = bool(np.array_equal(Ea, Eb))
    out["determinism_max_abs_difference"] = float(np.max(np.abs(Ea - Eb)))
    write_json(RESULTS / "sanity_controls.json", out)
    return out


def environment_record(command: str, quick: bool, realizations: int) -> dict[str, Any]:
    versions = {"python": sys.version, "platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor()}
    for name in ("numpy", "scipy", "matplotlib"):
        try:
            mod = __import__(name)
            versions[name] = getattr(mod, "__version__", "?")
        except Exception:
            versions[name] = "not-installed"
    return {
        "command": command,
        "quick": quick,
        "realizations_per_seed": realizations,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "versions": versions,
        "parameters": {
            "P": list(P_VALUES),
            "sigma_EXP": list(SIGMA_EXP),
            "seeds": list(SEEDS),
            "kappa0_physical": KAPPA0,
            "sigma_physical": SIGMA_PHYS,
            "wavelengths_across_box": WAVELENGTHS,
            "margin_wavelengths": MARGIN_WAVELENGTHS,
            "n_boot": N_BOOT,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="one realization per seed for a fast smoke test")
    parser.add_argument("--realizations", type=int, default=None)
    parser.add_argument("--skip-main", action="store_true")
    parser.add_argument("--skip-controls", action="store_true")
    args = parser.parse_args()
    realizations = args.realizations if args.realizations is not None else (1 if args.quick else 4)
    command = "python " + str(Path(__file__).relative_to(AUDIT.parent.parent).as_posix())
    write_json(RESULTS / "run_manifest.json", environment_record(command, args.quick, realizations))
    t0 = time.perf_counter()
    if not args.skip_main:
        run_main(realizations, quick=args.quick)
    if not args.skip_controls:
        run_sanity_controls()
        run_detail_controls(realizations=1)
        run_construction_controls()
        run_interpolation_controls()
        run_lowpass_controls()
        run_non_square_controls()
        run_fixed_field_controls()
    elapsed = time.perf_counter() - t0
    summary = {
        "elapsed_seconds": elapsed,
        "results_dir": str(RESULTS),
        "main_summary": str(RESULTS / "main_summary.json") if (RESULTS / "main_summary.json").exists() else None,
        "report_dir": str(REPORT),
    }
    write_json(RESULTS / "run_summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
