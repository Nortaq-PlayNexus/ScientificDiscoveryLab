#!/usr/bin/env python3
"""Bird's-eye error map for EXP-0016.

This is a visualization of already frozen result rows. It does not introduce a
new estimator, threshold, or physical claim.
"""
from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

BASE = Path(__file__).resolve().parent.parent
R = BASE / "RESULTS"
F = BASE / "FIGURES"
F.mkdir(exist_ok=True)

DET_ORDER = ["raw_winding", "clustered_winding", "circular_contour", "jacobian_locator"]
DET_LABEL = {
    "raw_winding": "raw winding",
    "clustered_winding": "clustered winding",
    "circular_contour": "circular contour",
    "jacobian_locator": "Jacobian locator",
}
COLORS = ["#b24a4a", "#d18b28", "#2878b5", "#4b9b64"]


def latest(prefix: str) -> dict:
    files = sorted(R.glob(prefix + "*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        raise FileNotFoundError(prefix)
    return json.loads(files[-1].read_text(encoding="utf-8"))


def err(row):
    return {
        "joint": int(row.get("location_count_error", 0) != 0 or row.get("absolute_charge_error", 0) != 0 or row.get("signed_charge_error", 0) != 0),
        "location": int(row.get("location_count_error", 0) != 0),
        "absolute": int(row.get("absolute_charge_error", 0) != 0),
        "signed": int(row.get("signed_charge_error", 0) != 0),
    }


def aggregate(rows):
    if not rows:
        return {"n": 0, "joint": 0.0, "location": 0.0, "absolute": 0.0, "signed": 0.0, "mean_location_error": 0.0, "mean_abs_error": 0.0}
    e = [err(r) for r in rows]
    return {
        "n": len(rows),
        "joint": float(np.mean([x["joint"] for x in e])),
        "location": float(np.mean([x["location"] for x in e])),
        "absolute": float(np.mean([x["absolute"] for x in e])),
        "signed": float(np.mean([x["signed"] for x in e])),
        "mean_location_error": float(np.mean([r.get("location_count_error", 0) for r in rows])),
        "mean_abs_error": float(np.mean([r.get("absolute_charge_error", 0) for r in rows])),
    }


def heat(ax, matrix, xlabels, ylabels, title, cbar_label, vmax=1.0):
    im = ax.imshow(matrix, aspect="auto", cmap="magma_r", norm=Normalize(0, vmax))
    ax.set_xticks(range(len(xlabels)), xlabels, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(ylabels)), ylabels, fontsize=8)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("normalized spatial scale", fontsize=8)
    ax.set_ylabel("estimator / case", fontsize=8)
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if np.isfinite(matrix[i, j]):
                txt = f"{matrix[i, j]:.2f}" if matrix[i, j] >= 0.995 or matrix[i, j] == 0 else f"{matrix[i, j]:.1f}"
                ax.text(j, i, txt, ha="center", va="center", fontsize=6, color="white" if matrix[i, j] > 0.55 else "black")
    return im


def main():
    phase = latest("phase_diagram_")["rows"]
    boundary = latest("boundary_controls_")["rows"]
    prop = latest("propagation_")["rows"]
    ref = latest("reference_padding_")

    spots = []
    # Single-vortex core-scale map, preserving the actual discrete ratios.
    single_groups = defaultdict(list)
    for r in phase:
        if r["family"] == "single":
            ratio = r["core_sigma_um"] / (64.0 / r["grid"])
            single_groups[(r["detector"], r["charge"], round(ratio, 6))].append(r)
    single_ratios = sorted({k[2] for k in single_groups})
    single_matrix = np.full((len(DET_ORDER) * 4, len(single_ratios)), np.nan)
    single_labels = []
    for qi, q in enumerate((-2, -1, 1, 2)):
        for di, det in enumerate(DET_ORDER):
            rowi = qi * len(DET_ORDER) + di
            single_labels.append(f"q={q:+d} · {DET_LABEL[det]}")
            for xi, x in enumerate(single_ratios):
                rs = single_groups.get((det, q, x), [])
                if rs:
                    a = aggregate(rs)
                    single_matrix[rowi, xi] = a["joint"]
                    if a["joint"] > 0:
                        spots.append({"spot_type": "single_core_scale", "family": "single", "detector": det, "charge": q, "x": x, "x_label": f"core/pixel={x:g}", **a})

    close_groups = defaultdict(list)
    for r in phase:
        if r["family"] == "close_pair":
            ratio = r["separation_um"] / (64.0 / r["grid"])
            close_groups[(r["detector"], round(ratio, 6))].append(r)
    close_ratios = sorted({k[1] for k in close_groups})
    close_matrix = np.full((len(DET_ORDER), len(close_ratios)), np.nan)
    close_labels = [DET_LABEL[d] for d in DET_ORDER]
    for di, det in enumerate(DET_ORDER):
        for xi, x in enumerate(close_ratios):
            rs = close_groups.get((det, x), [])
            if rs:
                a = aggregate(rs)
                close_matrix[di, xi] = a["joint"]
                if a["joint"] > 0:
                    spots.append({"spot_type": "close_pair_separation", "family": "close_pair", "detector": det, "charge": 0, "x": x, "x_label": f"separation/pixel={x:g}", **a})

    # Boundary full-vs-crop discrepancy, restricted to originally inside points.
    bgroups = defaultdict(list)
    for r in boundary:
        if r["position_inside"]:
            d = abs(r["distance_to_boundary_px"])
            bgroups[(r["detector"], round(d, 6))].append(r)
    bd = sorted({k[1] for k in bgroups})
    bmat = np.full((len(DET_ORDER), len(bd)), np.nan)
    blabels = [DET_LABEL[d] for d in DET_ORDER]
    for di, det in enumerate(DET_ORDER):
        for xi, x in enumerate(bd):
            rs = bgroups.get((det, x), [])
            if rs:
                rate = float(np.mean([r["padded_full_location_count"] != r["padded_location_count"] or r["padded_full_absolute_charge"] != r["padded_absolute_charge"] for r in rs]))
                bmat[di, xi] = rate
                if rate > 0:
                    spots.append({"spot_type": "boundary_full_vs_crop", "family": "boundary", "detector": det, "charge": 0, "x": x, "x_label": f"edge distance/pixel={x:g}", "n": len(rs), "joint": rate, "location": rate, "absolute": rate, "signed": 0.0, "mean_location_error": 0.0, "mean_abs_error": 0.0})

    # Propagation residual relative to the converged z>=400 zero state.
    pgroups = defaultdict(list)
    for r in prop:
        pgroups[(r["detector"], r["grid"], r["position_mode"], r["z_um"])].append(r)
    zs = sorted({r["z_um"] for r in prop})
    pmat = np.full((len(DET_ORDER) * 2, len(zs)), np.nan)
    plabels = []
    for ni, n in enumerate((64, 128)):
        for di, det in enumerate(DET_ORDER):
            rowi = ni * len(DET_ORDER) + di
            plabels.append(f"{n}² · {DET_LABEL[det]}")
            for xi, z in enumerate(zs):
                rs = pgroups.get((det, n, "exact_pixel", z), [])
                if rs:
                    # residual = nonzero output at/after the modeled annihilation window
                    pmat[rowi, xi] = float(rs[0]["location_count"] != 0 or rs[0]["absolute_charge"] != 0)
    # The z=0 pair is intentionally a positive control, so mark it as N/A.
    pmat[:, 0] = np.nan

    fig = plt.figure(figsize=(17, 12), constrained_layout=True)
    gs = fig.add_gridspec(3, 2, height_ratios=[1.35, 1.0, 0.85])
    ax1 = fig.add_subplot(gs[0, 0])
    im1 = heat(ax1, single_matrix, [f"{x:g}" for x in single_ratios], single_labels, "A. Single-vortex error spots: joint truth-match failure", "fraction failed")
    ax2 = fig.add_subplot(gs[0, 1])
    im2 = heat(ax2, close_matrix, [f"{x:g}" for x in close_ratios], close_labels, "B. Close +1/−1 pair error spots", "fraction failed")
    ax3 = fig.add_subplot(gs[1, 0])
    im3 = heat(ax3, bmat, [f"{x:g}" for x in bd], blabels, "C. Boundary loss: full padded field ≠ cropped FOV", "fraction differing")
    ax4 = fig.add_subplot(gs[1, 1])
    im4 = heat(ax4, pmat, [f"{z:g}" for z in zs], plabels, "D. Propagation residual spots (exact-pixel pair)", "fraction nonzero")
    for ax, im in ((ax1, im1), (ax2, im2), (ax3, im3), (ax4, im4)):
        ax.set_xlabel("normalized spatial scale / z (µm)", fontsize=8)
    # Text panel with the main visual readings.
    ax5 = fig.add_subplot(gs[2, :]); ax5.axis("off")
    text = (
        "HOTSPOT READING\n"
        "• q=±2 + half-pixel: raw/clustered winding shows a broad representation-splitting band; it is not a single resolution threshold.\n"
        "• q=any + half-pixel + core/pixel≈0.5–0.75: contour/Jacobian estimators lose the singularity.\n"
        "• close pair: Jacobian retains a low-separation failure pocket; raw/clustered/contour are mostly stable after the first bin.\n"
        "• boundary: the full padded field detects edge-near/outside singularities while the cropped FOV suppresses them — finite support/ROI, not topology loss.\n"
        "• propagation: the 64² control retains a residual near z=320 µm; 128²/256² exact-pixel controls are zero by z=400 µm.\n\n"
        "Color is an error/failure fraction within each cell; numbers are fractions, not vortex counts. This is a diagnostic view, not a novelty claim."
    )
    ax5.text(0.0, 0.98, text, va="top", ha="left", fontsize=10, family="DejaVu Sans")
    cax = fig.add_axes([0.92, 0.42, 0.012, 0.35])
    fig.colorbar(im1, cax=cax, label="fraction failed / differing")
    out = F / "EXP-0016_birdeye_error_map.png"
    fig.savefig(out, dpi=180)
    plt.close(fig)

    # Machine-readable hotspot list.
    fields = ["spot_type", "family", "detector", "charge", "x", "x_label", "n", "joint", "location", "absolute", "signed", "mean_location_error", "mean_abs_error"]
    with (R / "birdeye_error_spots.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for row in spots: w.writerow({k: row.get(k) for k in fields})
    summary = {
        "experiment": "EXP-0016",
        "source_files": {
            "phase": str(sorted(R.glob("phase_diagram_*.json"), key=lambda p: p.stat().st_mtime)[-1]),
            "boundary": str(sorted(R.glob("boundary_controls_*.json"), key=lambda p: p.stat().st_mtime)[-1]),
            "propagation": str(sorted(R.glob("propagation_*.json"), key=lambda p: p.stat().st_mtime)[-1]),
        },
        "hotspot_count": len(spots),
        "hotspots_by_type": {t: sum(s["spot_type"] == t for s in spots) for t in sorted({s["spot_type"] for s in spots})},
        "note": "Visualization of frozen result rows; no new detector or physical claim.",
    }
    (R / "birdeye_error_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Wrote", out)
    print("Wrote", R / "birdeye_error_spots.csv")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
