"""EXP-0003 - Phase-singularity (vortex) density in random wave fields (Q-O002/HYP-002).

Tests the Kac-Rice / Nye-Berry prediction
    n_pred = sum_k (kx^2 S_k) / (2*pi * sum_k S_k)
against a discrete winding-number count, for isotropic complex Gaussian fields, and
characterises the finite-grid (pixels-per-wavelength) failure zone.

Carries forward the predecessor project's lesson: the winding counter is tested for
grid-locking via a half-pixel shift control (C4).

Run from the investigation folder:
    python CODE/run_vortex_density.py
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

ENGINE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "04_SHARED_ENGINE")
)
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

from engine.hypothesis_testing.prereg import freeze_config  # noqa: E402
from engine.reproducibility.experiments import append_registry_row  # noqa: E402
from engine.statistics.testers import bh_fdr  # noqa: E402
from engine.utilities.core import (  # noqa: E402
    SEED_LADDER,
    make_experiment_json,
    rng,
)

INV = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENT_ID = "EXP-0003"
QUESTION_ID = "Q-O002"
HYPOTHESIS_ID = "HYP-002"
SEED = 42
ALPHA = 0.01

K0_LIST = (np.pi / 32, np.pi / 16, np.pi / 8, np.pi / 4, np.pi / 2)
N_LIST = (256, 512, 1024)
RING_HALFWIDTH = 0.20
GAUSS_CENTRE = np.pi / 2
SIGMA_LIST = (0.10, 0.25, 0.50, 0.75)
N_REAL = 40
N_BOOT = 2000
TOL_POINT = 0.03
TOL_CI = 0.05


def margin_for(n):
    return 24 if n <= 512 else 48


def spectrum_grid(n, kind, k0, param):
    f = np.fft.fftfreq(n) * 2 * np.pi
    KX, KY = np.meshgrid(f, f, indexing="xy")
    KR = np.sqrt(KX**2 + KY**2)
    if kind == "ring":
        S = ((KR - k0) ** 2 < param**2).astype(float)
    elif kind == "gauss":
        S = np.exp(-((KR - k0) ** 2) / (2.0 * param**2))
    else:
        raise ValueError(kind)
    return S, KX, KY


def real_gaussian(n, S, gen):
    """Real stationary Gaussian field with power spectrum S.

    Hermitian symmetry uses the correct (-k mod N) partner (this was a bug source in
    the predecessor project's surrogate code).
    """
    W = np.sqrt(S / 2.0) * (gen.standard_normal((n, n)) + 1j * gen.standard_normal((n, n)))
    idx = (-np.arange(n)) % n
    W = 0.5 * (W + np.conj(W[np.ix_(idx, idx)]))
    return np.real(np.fft.ifft2(W))


def complex_field(n, S, gen):
    """E = u + i v with independent real components, so E has spectrum S."""
    half = S / 2.0
    u = real_gaussian(n, half, gen)
    v = real_gaussian(n, half, gen)
    return u + 1j * v


def winding_counts(E, margin):
    ex = np.angle(E[:, 1:] * np.conj(E[:, :-1]))
    ey = np.angle(E[1:, :] * np.conj(E[:-1, :]))
    circ = ex[:-1, :] + ey[:, 1:] - ex[1:, :] - ey[:, :-1]
    w = np.round(circ / (2 * np.pi)).astype(int)
    w = w[margin:-margin, margin:-margin]
    area = float(w.size)
    return (
        float((w != 0).sum()) / area,
        float((w > 0).sum()) / area,
        float((w < 0).sum()) / area,
    )


def crossing_density_naive(E, margin):
    """Naive independent detector: cells where BOTH Re E and Im E zero-contours
    cross (each with exactly two edge crossings). Cheap, vectorised, no phase
    unwrapping. NOTE: this overcounts, because two contours may each cross a cell
    without intersecting inside it. Kept as a documented negative (detector choice
    matters); the certified D2 is crossing_density()."""
    out = None
    for G in (E.real, E.imag):
        a, b = G[:-1, :-1], G[:-1, 1:]
        c, d = G[1:, :-1], G[1:, 1:]
        nc = (a * b < 0).astype(int) + (c * d < 0).astype(int) + \
             (a * c < 0).astype(int) + (b * d < 0).astype(int)
        m = (nc == 2)
        out = m if out is None else (out & m)
    z = out[margin:-margin, margin:-margin]
    return float(z.sum()) / float(z.size)


def _edge_crossings(G):
    """Return (P1x,P1y,P2x,P2y,ok): the two zero-contour crossings of a cell's
    boundary (priority order T,B,L,R) where exactly two edges cross."""
    n = G.shape[0]
    jj, ii = np.meshgrid(np.arange(n - 1), np.arange(n - 1), indexing="xy")
    eps = 1e-12
    a, b = G[:-1, :-1], G[:-1, 1:]
    c, d = G[1:, :-1], G[1:, 1:]
    ta = np.abs(a) / (np.abs(a) + np.abs(b) + eps)
    tb = np.abs(c) / (np.abs(c) + np.abs(d) + eps)
    tl = np.abs(a) / (np.abs(a) + np.abs(c) + eps)
    tr = np.abs(b) / (np.abs(b) + np.abs(d) + eps)
    MT, MB, ML, MR = a * b < 0, c * d < 0, a * c < 0, b * d < 0
    Tx, Ty = jj + ta, ii
    Bx, By = jj + tb, ii + 1
    Lx, Ly = jj, ii + tl
    Rx, Ry = jj + 1, ii + tr
    ok = (MT.astype(int) + MB.astype(int) + ML.astype(int) + MR.astype(int)) == 2
    P1x = np.where(MT, Tx, np.where(MB, Bx, np.where(ML, Lx, Rx)))
    P1y = np.where(MT, Ty, np.where(MB, By, np.where(ML, Ly, Ry)))
    P2x = np.where(MR, Rx, np.where(ML, Lx, np.where(MB, Bx, Tx)))
    P2y = np.where(MR, Ry, np.where(ML, Ly, np.where(MB, By, Ty)))
    return P1x, P1y, P2x, P2y, ok


def crossing_density(E, margin):
    """Certified D2: cells where the Re E = 0 and Im E = 0 zero-contour segments
    actually intersect inside the cell (orientation test). Independent of the
    winding method; uses no phase unwrapping."""
    Ar1x, Ar1y, Ar2x, Ar2y, okR = _edge_crossings(E.real)
    Br1x, Br1y, Br2x, Br2y, okI = _edge_crossings(E.imag)
    d1x, d1y = Ar2x - Ar1x, Ar2y - Ar1y
    d2x, d2y = Br2x - Br1x, Br2y - Br1y
    den = d1x * d2y - d1y * d2x
    wx, wy = Br1x - Ar1x, Br1y - Ar1y
    with np.errstate(divide="ignore", invalid="ignore"):
        s = (wx * d2y - wy * d2x) / den
        u = (wx * d1y - wy * d1x) / den
    hit = okR & okI & (den != 0) & (s >= 0) & (s <= 1) & (u >= 0) & (u <= 1)
    z = hit[margin:-margin, margin:-margin]
    return float(z.sum()) / float(z.size)


def shift_field(E, dx, dy):
    n = E.shape[0]
    f = np.fft.fftfreq(n)
    ramp = np.exp(-2j * np.pi * (f[:, None] * dx + f[None, :] * dy))
    return np.fft.ifft2(np.fft.fft2(E) * ramp)


def spectral_prediction(S, KX):
    return float((KX**2 * S).sum() / S.sum() / (2 * np.pi))


def fd_prediction(E):
    dE = E[:, 1:] - E[:, :-1]
    return float((np.abs(dE) ** 2).mean() / (2 * np.pi * (np.abs(E) ** 2).mean()))


def bootstrap_ci(values, gen, n_boot, alpha=ALPHA):
    v = np.asarray(values, dtype=float)
    n = v.size
    means = np.empty(n_boot)
    for i in range(n_boot):
        means[i] = v[gen.integers(0, n, n)].mean()
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi), means


def run_cell(n, S, KX, seed_label, do_shift=False, do_crossing=False):
    gen = rng(seed_label, SEED)
    margin = margin_for(n)
    n_pred = spectral_prediction(S, KX)
    dens, dplus, dminus, cross, cross_naive, ratios = [], [], [], [], [], []
    pred_fd = []
    shift_delta = None
    for _ in range(N_REAL):
        E = complex_field(n, S, gen)
        nt, npo, nne = winding_counts(E, margin)
        dens.append(nt)
        dplus.append(npo)
        dminus.append(nne)
        ratios.append(nt / n_pred)
        pred_fd.append(fd_prediction(E))
        if do_crossing:
            cross.append(crossing_density(E, margin))
            cross_naive.append(crossing_density_naive(E, margin))
        if do_shift and shift_delta is None:
            Es = shift_field(E, 0.5, 0.5)
            nt_s, _, _ = winding_counts(Es, margin)
            shift_delta = abs(nt_s - nt) / nt
    dens = np.array(dens)
    ci_gen = rng("vortex-bootstrap", SEED)
    lo, hi, means = bootstrap_ci(dens / n_pred, ci_gen, N_BOOT)
    p = 2.0 * min(float((means >= 1.0).mean()), float((means <= 1.0).mean()))
    p = min(1.0, p + np.finfo(float).eps)
    return {
        "n": n,
        "n_pred": n_pred,
        "n_pred_from_field_fd_mean": float(np.mean(pred_fd)),
        "n_meas_mean": float(dens.mean()),
        "ratio": float(dens.mean() / n_pred),
        "ratio_ci_low": lo,
        "ratio_ci_high": hi,
        "p_two_sided_ratio_eq_1": p,
        "n_plus_mean": float(np.mean(dplus)),
        "n_minus_mean": float(np.mean(dminus)),
        "charge_imbalance": float(
            abs(np.mean(dplus) - np.mean(dminus)) / dens.mean()
        ),
        "crossing_ratio": (float(np.mean(cross) / n_pred) if cross else None),
        "crossing_naive_ratio": (
            float(np.mean(cross_naive) / n_pred) if cross_naive else None
        ),
        "shift_rel_delta": shift_delta,
        "n_real": N_REAL,
    }


def main():
    for sub in ("CONFIG", "RESULTS", "FIGURES", "REPORT", "REPLICATION"):
        os.makedirs(os.path.join(INV, sub), exist_ok=True)

    freeze_config(
        experiment_id=EXPERIMENT_ID,
        hypothesis_id=HYPOTHESIS_ID,
        question_id=QUESTION_ID,
        seed=SEED,
        alpha=ALPHA,
        controls=(
            "C1 analytic-vs-FD consistency",
            "C2 winding vs contour crossing",
            "C3 charge neutrality",
            "C4 half-pixel shift invariance (grid-lock falsifier)",
            "C5 amplitude scaling",
            "C6 independent implementation",
            "C7 resolution/pixels-per-wavelength ladder",
            "C8 bandwidth ladder (Nyquist failure zone)",
            "C9 seed ladder",
            "C10 BH-FDR",
        ),
        analyses=("ratio vs 1 (99% bootstrap CI)", "BH-FDR across cells"),
        params={
            "k0_rad_per_px": [float(k) for k in K0_LIST],
            "N_list": list(N_LIST),
            "ring_halfwidth": RING_HALFWIDTH,
            "gauss_centre": float(GAUSS_CENTRE),
            "sigma_list": list(SIGMA_LIST),
            "n_realisations": N_REAL,
            "n_boot": N_BOOT,
            "tolerance_point": TOL_POINT,
            "tolerance_ci": TOL_CI,
        },
        out_path=os.path.join(INV, "CONFIG", "prereg_EXP-0003.json"),
        note="Frozen before execution. Primary H0 on narrow-band cells k0<=pi/4 at N=1024.",
    )

    cells = {}

    for k0 in K0_LIST:
        for n in N_LIST:
            S, KX, KY = spectrum_grid(n, "ring", k0, RING_HALFWIDTH)
            key = f"ring_k0_{round(k0,5)}_N{n}"
            cells[key] = run_cell(
                n, S, KX,
                seed_label=f"ring-{round(k0,5)}-{n}",
                do_shift=True,
                do_crossing=True,
            )
            cells[key]["kind"] = "ring"
            cells[key]["k0"] = float(k0)
            cells[key]["pixels_per_wavelength"] = float(2 * np.pi / k0)

    for sk in SIGMA_LIST:
        n = 512
        S, KX, KY = spectrum_grid(n, "gauss", GAUSS_CENTRE, sk)
        key = f"gauss_sigma_{sk}_N{n}"
        cells[key] = run_cell(
            n, S, KX, seed_label=f"gauss-{sk}-{n}", do_shift=False, do_crossing=True
        )
        cells[key]["kind"] = "gauss"
        cells[key]["k0"] = float(GAUSS_CENTRE)
        cells[key]["sigma_k"] = float(sk)
        cells[key]["pixels_per_wavelength"] = float(2 * np.pi / GAUSS_CENTRE)

    # ---------- C10: BH-FDR across all cells ----------
    keys = sorted(cells)
    pvals = np.array([cells[k]["p_two_sided_ratio_eq_1"] for k in keys])
    sig, (_ranked, thr, order) = bh_fdr(pvals, alpha=ALPHA)
    for i, k in enumerate(keys):
        cells[k]["fdr_significant_vs_ratio_1"] = bool(sig[i])
        cells[k]["within_point_tolerance"] = bool(
            abs(cells[k]["ratio"] - 1.0) <= TOL_POINT
        )

    # ---------- C5 amplitude scaling (spot check) ----------
    S, KX, _ = spectrum_grid(512, "ring", np.pi / 4, RING_HALFWIDTH)
    g = rng("vortex-amplitude", SEED)
    E = complex_field(512, S, g)
    n0, _, _ = winding_counts(E, 24)
    n_scaled, _, _ = winding_counts(3.7 * E, 24)
    amp_rel_delta = abs(n_scaled - n0) / n0

    # ---------- C9 seed ladder (spot check, k0=pi/4, N=512) ----------
    S, KX, _ = spectrum_grid(512, "ring", np.pi / 4, RING_HALFWIDTH)
    seed_ratios = {}
    n_pred = spectral_prediction(S, KX)
    for s in SEED_LADDER:
        gs = rng(f"ring-{round(np.pi/4,5)}-512", s)
        vals = []
        for _ in range(12):
            E = complex_field(512, S, gs)
            nt, _, _ = winding_counts(E, 24)
            vals.append(nt / n_pred)
        seed_ratios[s] = float(np.mean(vals))

    # ---------- decision ----------
    primary_keys = [
        k for k in keys
        if cells[k]["kind"] == "ring" and cells[k]["n"] == 1024
        and cells[k]["k0"] <= np.pi / 4 + 1e-9
    ]
    primary = [cells[k] for k in primary_keys]
    h0 = all(
        c["within_point_tolerance"]
        and c["ratio_ci_low"] >= 1 - TOL_CI
        and c["ratio_ci_high"] <= 1 + TOL_CI
        for c in primary
    )
    charge_ok = all(c["charge_imbalance"] < 0.02 for c in cells.values())
    shift_ok = all(
        c["shift_rel_delta"] is not None and c["shift_rel_delta"] < 0.03
        for c in cells.values()
        if c["kind"] == "ring"
    )

    if h0 and charge_ok and shift_ok:
        decision = "H0_SUPPORTED"
        conclusion = (
            "Narrow-band vortex density matches the Kac-Rice/Nye-Berry prediction "
            "within the 3% tolerance in the well-resolved regime; charge-neutral and "
            "shift-invariant (no grid-locking). Broadband deficit characterised as a "
            "near-Nyquist finite-grid effect."
        )
    elif not h0:
        decision = "H1_DEV_FLAGGED"
        conclusion = (
            "A well-resolved narrow-band cell exceeded tolerance; run the "
            "kill-the-hypothesis battery and independent implementation; claim "
            "nothing beyond a controlled deviation."
        )
    else:
        decision = "PARTIAL_CONTROLS_FAILED"
        conclusion = (
            "Primary density agreement held but a control (charge neutrality or "
            "shift invariance) failed; treat the estimator as NOT certified."
        )

    result = {
        "experiment": EXPERIMENT_ID,
        "question": QUESTION_ID,
        "hypothesis": HYPOTHESIS_ID,
        "cells": cells,
        "primary_cells": primary_keys,
        "amplitude_scaling_rel_delta": amp_rel_delta,
        "seed_ladder_ratio": seed_ratios,
        "decision": decision,
        "conclusion_lab": conclusion,
    }
    res_path = os.path.join(INV, "RESULTS", "EXP-0003_results.json")
    with open(res_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)

    make_experiment_json(
        experiment_id=EXPERIMENT_ID,
        question=QUESTION_ID,
        hypothesis=HYPOTHESIS_ID,
        seed=SEED,
        parameters={
            "k0_rad_per_px": [float(k) for k in K0_LIST],
            "N_list": list(N_LIST),
            "ring_halfwidth": RING_HALFWIDTH,
            "sigma_list": list(SIGMA_LIST),
            "n_realisations": N_REAL,
            "n_boot": N_BOOT,
        },
        result=result,
        out_path=os.path.join(INV, "CONFIG", f"{EXPERIMENT_ID}_experiment.json"),
    )
    append_registry_row(
        os.path.join(INV, "CONFIG", "registry.jsonl"),
        {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis": HYPOTHESIS_ID,
            "question": QUESTION_ID,
            "seed": SEED,
            "decision": decision,
            "result_path": res_path,
        },
    )

    print(f"{EXPERIMENT_ID} decision: {decision}")
    for k in keys:
        c = cells[k]
        print(
            f"  {k:28s} ratio={c['ratio']:.4f} "
            f"[{c['ratio_ci_low']:.4f},{c['ratio_ci_high']:.4f}] "
            f"charge={c['charge_imbalance']:.4f} "
            f"shift={c['shift_rel_delta'] if c['shift_rel_delta'] is None else round(c['shift_rel_delta'],4)} "
            f"cross={c['crossing_ratio'] if c['crossing_ratio'] is None else round(c['crossing_ratio'],4)} "
            f"fdr={c['fdr_significant_vs_ratio_1']}"
        )
    return result


if __name__ == "__main__":
    main()
