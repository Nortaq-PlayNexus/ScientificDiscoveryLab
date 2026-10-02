"""EXP-0004 - p-value distribution figures (purely visual; not a decision input).

Reads RESULTS/EXP-0004_results.json and draws, per generator, the p-value
histogram with the expected Uniform(0,1) density and the KS p-value.

Run from the investigation folder:
    python CODE/plot_battery.py
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INV = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_PATH = os.path.join(INV, "RESULTS", "EXP-0004_results.json")
FIG_DIR = os.path.join(INV, "FIGURES")

GEN_NAMES = ("G_LAB", "G_PCG", "G_MT")
GEN_TITLES = {
    "G_LAB": "Lab RNG (sha256-derived PCG64)",
    "G_PCG": "Control: raw PCG64 (numpy default_rng)",
    "G_MT": "Control: MT19937 (numpy RandomState)",
}


def main():
    with open(RESULTS_PATH, "r", encoding="utf-8") as fh:
        res = json.load(fh)

    fig, axes = plt.subplots(1, len(GEN_NAMES), figsize=(6.5 * len(GEN_NAMES), 4.6))
    if len(GEN_NAMES) == 1:
        axes = [axes]
    for ax, name in zip(axes, GEN_NAMES):
        pvals = []
        for ps in res["generators"][name]:
            pvals.extend(ps["pvals"].values())
        pvals = np.asarray(pvals)
        ks_p = res["aggregates"][name]["ks_p"]
        n_ok = res["aggregates"][name]["small_p_count"]
        band = res["aggregates"][name]["binomial_band"]

        ax.hist(pvals, bins=20, range=(0, 1), density=True, alpha=0.65,
                color="#4c6ef5", label=f"n={pvals.size}")
        ax.axhline(1.0, color="#e03131", ls="--", lw=1.2, label="Uniform(0,1)")
        ax.set_title(f"{GEN_TITLES[name]}\nKS p={ks_p:.3f}")
        ax.set_xlabel("p-value")
        ax.set_ylabel("density")
        ax.text(0.03, 0.95,
                f"p<={res['alpha']}: {n_ok} (band [{band['lo']},{band['hi']}])\n"
                f"FDR flags: {res['aggregates'][name]['fdr_flag_count']}",
                transform=ax.transAxes, fontsize=9, va="top")
        ax.legend(loc="upper right", fontsize=8)

    fig.suptitle(
        f"EXP-0004 lab RNG battery — p-value distributions (decision: "
        f"{res['decision']})",
        fontsize=13,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    os.makedirs(FIG_DIR, exist_ok=True)
    out = os.path.join(FIG_DIR, "EXP-0004_pvalue_distribution.png")
    fig.savefig(out, dpi=150)
    print(f"wrote {out}")


if __name__ == "__main__":
    sys.exit(main() or 0)