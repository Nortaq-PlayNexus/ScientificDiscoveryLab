"""Figure for EXP-0002: r = C*sqrt(M) vs M for each grid size."""

from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
res = json.load(open(os.path.join(HERE, "RESULTS", "EXP-0002_results.json")))
cells = res["cells"]

fig, ax = plt.subplots(figsize=(7, 4.5))
colors = {32: "#1f77b4", 64: "#d62728", 128: "#2ca02c", 256: "#9467bd"}
for n in (32, 64, 128, 256):
    ks = sorted([k for k, v in cells.items() if v["n"] == n],
                key=lambda k: cells[k]["m"])
    ms = [cells[k]["m"] for k in ks]
    rs = [cells[k]["r"] for k in ks]
    ax.plot(ms, rs, "o-", color=colors[n], label=f"N={n}")
ax.axhline(1.0, color="k", ls="--", lw=1, label="theory C=1/sqrt(M)")
ax.set_xscale("log", base=2)
ax.set_xlabel("M (summed speckle patterns)")
ax.set_ylabel(r"$C \cdot \sqrt{M}$")
ax.set_title("EXP-0002 speckle contrast law: deviation shrinks with grid size N")
ax.set_ylim(0.97, 1.02)
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
out = os.path.join(HERE, "FIGURES", "EXP-0002_contrast_law.png")
fig.savefig(out, dpi=150)
print("figure:", out)