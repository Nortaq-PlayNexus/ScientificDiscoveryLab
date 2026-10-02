#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
R = BASE / "RESULTS"
F = BASE / "FIGURES"
F.mkdir(exist_ok=True)
p = sorted(R.glob("phase_diagram_*.json"), key=lambda x: x.stat().st_mtime)[-1]
phase = json.loads(p.read_text())["rows"]
prop_path = sorted(R.glob("propagation_*.json"), key=lambda x: x.stat().st_mtime)[-1]
prop = json.loads(prop_path.read_text())["rows"]
boundary_path = sorted(R.glob("boundary_controls_*.json"), key=lambda x: x.stat().st_mtime)[-1]
boundary = json.loads(boundary_path.read_text())["rows"]
colors = {"raw_winding":"#b24a4a", "clustered_winding":"#d18b28", "circular_contour":"#2878b5", "jacobian_locator":"#4b9b64"}
labels = {"raw_winding":"raw winding", "clustered_winding":"clustered winding", "circular_contour":"circular contour", "jacobian_locator":"Jacobian locator"}

def ok(r): return r["location_count_error"] == 0 and r["absolute_charge_error"] == 0 and r["signed_charge_error"] == 0

# Single-vortex failure diagram.
fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), constrained_layout=True)
for ax, q in zip(axes, (1, 2)):
    for det in colors:
        rs = [r for r in phase if r["family"] == "single" and r["charge"] == q and r["detector"] == det]
        groups = {}
        for r in rs:
            x = r["core_sigma_um"] / (64.0 / r["grid"])
            groups.setdefault(x, []).append(ok(r))
        xs = sorted(groups)
        ys = [np.mean(groups[x]) for x in xs]
        ax.plot(xs, ys, "o-", color=colors[det], label=labels[det], linewidth=1.6, markersize=4)
    ax.set_title(f"single charge q={q:+d}")
    ax.set_xlabel("core sigma / pixel pitch")
    ax.set_ylabel("joint truth-match rate")
    ax.set_ylim(-0.05, 1.05)
    ax.grid(alpha=0.25)
axes[1].legend(fontsize=8, loc="lower right")
fig.suptitle("EXP-0016 estimator failure diagram (analytical fields; no novelty claim)")
fig.savefig(F / "single_vortex_failure_phase_diagram.png", dpi=180)
plt.close(fig)

# Close-pair diagram.
fig, ax = plt.subplots(figsize=(7.5, 4.8), constrained_layout=True)
for det in colors:
    rs = [r for r in phase if r["family"] == "close_pair" and r["detector"] == det]
    groups = {}
    for r in rs:
        x = r["separation_um"] / (64.0 / r["grid"])
        groups.setdefault(x, []).append(ok(r))
    xs = sorted(groups)
    ys = [np.mean(groups[x]) for x in xs]
    ax.plot(xs, ys, "o-", color=colors[det], label=labels[det], linewidth=1.6, markersize=4)
ax.set_xlabel("opposite-pair separation / pixel pitch")
ax.set_ylabel("joint truth-match rate")
ax.set_ylim(-0.05, 1.05)
ax.grid(alpha=0.25)
ax.legend(fontsize=8)
ax.set_title("Close +1/−1 pair: estimator-specific failure")
fig.savefig(F / "close_pair_failure_phase_diagram.png", dpi=180)
plt.close(fig)

# Count semantics for q=2, core sigma=2, half-pixel placement.
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
rs = [r for r in phase if r["family"] == "single" and r["charge"] == 2 and r["grid"] == 128 and r["core_sigma_um"] == 2.0 and r["position_mode"] == "half_pixel"]
labels2 = [labels[r["detector"]] for r in rs]
x = np.arange(len(rs)); width = 0.24
ax.bar(x-width, [r["location_count"] for r in rs], width, label="location count", color="#2878b5")
ax.bar(x, [r["winding_cell_count"] for r in rs], width, label="winding cells", color="#b24a4a")
ax.bar(x+width, [r["absolute_charge"] for r in rs], width, label="absolute charge", color="#4b9b64")
ax.set_xticks(x, labels2, rotation=20, ha="right")
ax.set_ylabel("count / charge units")
ax.set_title("One q=+2 singularity: representation units are not interchangeable")
ax.legend(fontsize=8)
ax.grid(axis="y", alpha=0.25)
fig.savefig(F / "charge_two_count_semantics.png", dpi=180)
plt.close(fig)

# Boundary crossing: full padded field versus cropped finite FOV.
fig, ax = plt.subplots(figsize=(8, 4.7), constrained_layout=True)
for det in colors:
    rs = [r for r in boundary if r["detector"] == det and r["position_inside"]]
    groups = {}
    for r in rs:
        x = abs(r["distance_to_boundary_px"])
        groups.setdefault(x, []).append(r)
    xs = sorted(groups)
    full = [np.mean([r["padded_full_location_count"] for r in groups[x]]) for x in xs]
    crop = [np.mean([r["padded_location_count"] for r in groups[x]]) for x in xs]
    ax.plot(xs, full, "o--", color=colors[det], alpha=0.65, linewidth=1.2, markersize=3, label=f"{labels[det]} full")
    ax.plot(xs, crop, "o-", color=colors[det], linewidth=1.6, markersize=3, label=f"{labels[det]} crop")
ax.set_xlabel("distance from singularity to FOV edge (pixels)")
ax.set_ylabel("mean estimated location count")
ax.set_ylim(-0.1, 1.5)
ax.grid(alpha=0.25)
ax.legend(fontsize=6, ncol=2)
ax.set_title("Boundary crossing: full padded field versus cropped finite FOV")
fig.savefig(F / "boundary_crossing_control.png", dpi=180)
plt.close(fig)

# Propagation subset.
fig, ax = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
for det in colors:
    rs = [r for r in prop if r["detector"] == det and r["grid"] == 128 and r["position_mode"] == "exact_pixel"]
    rs.sort(key=lambda r: r["z_um"])
    ax.plot([r["z_um"] for r in rs], [r["location_count"] for r in rs], "o-", color=colors[det], label=labels[det], linewidth=1.5)
ax.set_xlabel("propagation z (µm)")
ax.set_ylabel("estimated location count")
ax.set_ylim(-0.2, 2.3)
ax.set_xticks(sorted(set(r["z_um"] for r in prop)))
ax.grid(alpha=0.25)
ax.legend(fontsize=8, ncol=2)
ax.set_title("Modeled +1/−1 pair annihilation (128² exact-pixel control)")
fig.savefig(F / "propagation_annihilation_subset.png", dpi=180)
plt.close(fig)
print("Wrote figures to", F)
