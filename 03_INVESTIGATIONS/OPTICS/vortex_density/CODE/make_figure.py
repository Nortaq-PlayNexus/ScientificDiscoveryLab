"""Figure for EXP-0003: vortex density / prediction vs wavenumber and bandwidth."""

from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = json.load(open(os.path.join(HERE, "RESULTS", "EXP-0003_results.json")))
cells = res["cells"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
colors = {256: "#1f77b4", 512: "#d62728", 1024: "#2ca02c"}

for n in (256, 512, 1024):
    ks = sorted(
        [k for k, v in cells.items() if v["kind"] == "ring" and v["n"] == n],
        key=lambda k: cells[k]["k0"],
    )
    x = [cells[k]["k0"] for k in ks]
    y = [cells[k]["ratio"] for k in ks]
    lo = [cells[k]["ratio"] - cells[k]["ratio_ci_low"] for k in ks]
    hi = [cells[k]["ratio_ci_high"] - cells[k]["ratio"] for k in ks]
    ax1.errorbar(x, y, yerr=[lo, hi], marker="o", color=colors[n], label=f"N={n}",
                 capsize=3, lw=1)
ax1.axhline(1.0, color="k", ls="--", lw=1)
ax1.axhspan(0.97, 1.03, color="grey", alpha=0.15, label="+/-3% tolerance")
ax1.set_xscale("log", base=2)
ax1.set_xlabel("ring wavenumber k0 (rad/pixel)")
ax1.set_ylabel(r"$n_{meas}/n_{pred}$")
ax1.set_title("(a) Narrow-band: matches Kac-Rice (P>=8)")
ax1.set_ylim(0.95, 1.06)
ax1.legend(fontsize=8)
ax1.grid(alpha=0.3)

gk = sorted([k for k, v in cells.items() if v["kind"] == "gauss"],
            key=lambda k: cells[k]["sigma_k"])
x = [cells[k]["sigma_k"] for k in gk]
ax2.plot(x, [cells[k]["ratio"] for k in gk], "o-", color="#1f77b4",
         label="winding (D1)")
ax2.plot(x, [cells[k]["crossing_ratio"] for k in gk], "s--", color="#d62728",
         label="contour (D2)")
ax2.axhline(1.0, color="k", ls="--", lw=1)
ax2.set_xlabel(r"Gaussian spectral width $\sigma_k$ (rad/pixel), centre k0=pi/2")
ax2.set_ylabel(r"$n_{meas}/n_{pred}$")
ax2.set_title("(b) Broadband: deficit grows with near-Nyquist power")
ax2.set_ylim(0.7, 1.08)
ax2.legend(fontsize=8)
ax2.grid(alpha=0.3)

fig.tight_layout()
out = os.path.join(HERE, "FIGURES", "EXP-0003_vortex_density.png")
fig.savefig(out, dpi=150)
print("figure:", out)
