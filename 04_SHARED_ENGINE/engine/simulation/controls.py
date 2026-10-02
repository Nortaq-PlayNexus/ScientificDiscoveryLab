"""simulation.controls — control generators (RESEARCH_RULES.md section 3).

Provides honest comparison pipelines for simulated experiments:
  - null field generator (matched mean/variance)
  - matched-spectrum surrogate (preserve Fourier magnitude distribution)
  - resolution ladder
  - seed ladder
"""

from __future__ import annotations

import numpy as np

from ..utilities.core import rng, SEED_LADDER


def gaussian_field(shape, seed, mean=0.0, var=1.0, label="null"):
    """Gaussian white noise field with requested mean/variance."""
    gen = rng(label, seed)
    out = gen.normal(0.0, 1.0, size=shape)
    out = (out - out.mean()) / out.std() * np.sqrt(var) + mean
    return out


def matched_spectrum_surrogate(field, seed, label="surrogate"):
    """A REAL field with the SAME Fourier magnitude spectrum as `field` but random phase.

    This is the strongest general surrogate-null used in the lab (sandbox D02-style):
    any statistic that depends only on the power spectrum is reproduced by the
    surrogate; anything that survives it does not depend trivially on the spectrum.

    The random phase factor is built Hermitian-symmetric so the inverse transform is
    exactly real and the magnitude spectrum is preserved bit-for-bit.
    """
    F = np.fft.fft2(field)
    gen = rng(label, seed)
    phases = gen.uniform(0.0, 2.0 * np.pi, size=F.shape)
    P = np.exp(1j * phases)
    rows = np.mod(-np.arange(F.shape[0]), F.shape[0])
    cols = np.mod(-np.arange(F.shape[1]), F.shape[1])
    P = P * np.conj(P[rows][:, cols])  # Hermitian unit phases -> real inverse
    return np.fft.ifft2(P * F).real


def phase_shuffle_1d(signal, seed, label="phase-shuffle"):
    """Shuffle the phase of a 1D signal's Fourier transform (null for spectrums)."""
    ft = np.fft.fft(np.asarray(signal, dtype=float))
    gen = rng(label, seed)
    phases = gen.uniform(0.0, 2.0 * np.pi, size=ft.size)
    return np.fft.ifft(np.abs(ft) * np.exp(1j * phases)).real


def resolution_ladder(base=32, steps=4, factor=2):
    """Yield a resolution ladder (32, 64, 128, ...) for grid-convergence controls."""
    sizes = []
    for _ in range(steps):
        sizes.append(base)
        base *= factor
    return tuple(sizes)


def seed_ladder(seed=0, labels=("a", "b", "c", "d", "e")):
    """A fixed ladder of labelled seeds for seed-robustness checks."""
    return SEED_LADDER


def permuted_rows(matrix, seed, label="perm-null"):
    """Permute each row/column independently (parameter-shuffle null helper)."""
    gen = rng(label, seed)
    arr = np.asarray(matrix)
    return arr[:, gen.permutation(arr.shape[1])]