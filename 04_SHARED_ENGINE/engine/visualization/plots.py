"""visualization.plots — deterministic matplotlib helpers.

Keeps figures readable and reproducible; no styling magic that could hide
artifacts (a figure that hides data is a liability, per falsification_rules.md).
"""

from __future__ import annotations

import os

import numpy as np


def save_figure(fig, path, dpi=150, tight=True):
    """Save (and close) a figure; returns the path."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    if tight:
        fig.tight_layout()
    fig.savefig(path, dpi=dpi)
    import matplotlib.pyplot as plt

    plt.close(fig)
    return path


def default_palette():
    return ["#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b"]


def add_error_band(ax, x, center, lo, hi, color, alpha=0.25, label=None):
    """Shade a bootstrapped/CI band."""
    ax.plot(x, center, color=color, label=label)
    ax.fill_between(x, lo, hi, color=color, alpha=alpha)
    return ax


def heatmap(ax, matrix, cmap="viridis", vmin=None, vmax=None, cbar=True):
    from matplotlib import cm as _cm

    im = ax.imshow(np.asarray(matrix), cmap=cmap, vmin=vmin, vmax=vmax,
                   origin="lower", aspect="auto")
    if cbar:
        ax.figure.colorbar(im, ax=ax)
    return ax