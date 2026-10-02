"""EXP-0003 REPLICATION - independent construction and detector.

Construction: an explicit superposition of many plane waves on a ring of radius k0
with independent complex Gaussian weights (no FFT spectral shaping). By the central
limit theorem this is an isotropic complex Gaussian field.

Detector: a from-scratch, loop-based zero-contour intersection test (Re E = 0 and
Im E = 0 line segments crossing inside a cell), with the vortex charge taken from
the sign of the Jacobian determinant det d(Re,Im)/d(x,y) by central differences.
This is independent of the vectorised winding-number counter in CODE/.

Run from this folder:  python independent_check.py
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

from engine.utilities.core import rng  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
N = 256
MARGIN = 24
N_REAL = 20
M_MODES = 4000


def plane_wave_field(n, k0, gen):
    """E = sum_m A_m exp(i (k_m . r + phi_m)), k_m on ring of radius k0.

    Separable evaluation: E = (U * c) @ V.T with U[x,m]=exp(i kx_m x),
    V[y,m]=exp(i ky_m y), c_m = A_m exp(i phi_m).

    Returns (E, pred_mode, fft_bias_ratio): pred_mode is the correct predictor for
    this construction, <|dE/dx|^2>/(2*pi*<|E|^2>) = sum|c_m|^2 kx_m^2 / sum|c_m|^2 /
    (2*pi). The FFT-moment predictor is ALSO returned, because it is biased for a
    field whose frequencies are off the DFT grid (spectral leakage) - a documented
    artifact (see NOTES below).
    """
    theta = gen.uniform(0.0, 2.0 * np.pi, M_MODES)
    kx = k0 * np.cos(theta)
    ky = k0 * np.sin(theta)
    amp = gen.standard_normal(M_MODES) + 1j * gen.standard_normal(M_MODES)
    ph = gen.uniform(0.0, 2.0 * np.pi, M_MODES)
    c = amp * np.exp(1j * ph)
    x = np.arange(n)
    U = np.exp(1j * np.outer(x, kx))
    V = np.exp(1j * np.outer(x, ky))
    E = (U * c) @ V.T
    pred_mode = float(
        (np.abs(c) ** 2 * kx**2).sum() / (np.abs(c) ** 2).sum() / (2 * np.pi)
    )
    return E, pred_mode


def fft_prediction(E):
    """FFT-moment predictor. Biased for off-grid (non-band-limited) fields: leakage
    pushes power to high k, inflating <|dE/dx|^2>. Recorded only to document this."""
    n = E.shape[0]
    f = np.fft.fftfreq(n) * 2 * np.pi
    KX = np.meshgrid(f, f, indexing="xy")[0]
    S = np.abs(np.fft.fft2(E)) ** 2
    return float((KX**2 * S).sum() / S.sum() / (2 * np.pi))


def _two_crossings(vals):
    a, b, c, d = vals
    pts = []
    if a * b < 0:
        pts.append((abs(a) / (abs(a) + abs(b)), "t"))
    if c * d < 0:
        pts.append((abs(c) / (abs(c) + abs(d)), "b"))
    if a * c < 0:
        pts.append((abs(a) / (abs(a) + abs(c)), "l"))
    if b * d < 0:
        pts.append((abs(b) / (abs(b) + abs(d)), "r"))
    if len(pts) != 2:
        return None
    out = []
    for t, tag in pts:
        if tag == "t":
            out.append((t, 0.0))
        elif tag == "b":
            out.append((t, 1.0))
        elif tag == "l":
            out.append((0.0, t))
        else:
            out.append((1.0, t))
    return out


def _segments_cross(p, q):
    (x1, y1), (x2, y2) = p
    (x3, y3), (x4, y4) = q
    d1x, d1y = x2 - x1, y2 - y1
    d2x, d2y = x4 - x3, y4 - y3
    den = d1x * d2y - d1y * d2x
    if den == 0:
        return False
    wx, wy = x3 - x1, y3 - y1
    s = (wx * d2y - wy * d2x) / den
    u = (wx * d1y - wy * d1x) / den
    return 0.0 <= s <= 1.0 and 0.0 <= u <= 1.0


def detect_loop(E, margin):
    """Return (density_total, density_plus, density_minus) via loop-based detection."""
    n = E.shape[0]
    R, I = E.real, E.imag
    npos = nneg = ntot = 0
    for i in range(margin, n - margin - 1):
        for j in range(margin, n - margin - 1):
            rc = _two_crossings((R[i, j], R[i, j + 1], R[i + 1, j], R[i + 1, j + 1]))
            ic = _two_crossings((I[i, j], I[i, j + 1], I[i + 1, j], I[i + 1, j + 1]))
            if rc is None or ic is None:
                continue
            if _segments_cross(rc, ic):
                ntot += 1
                dEdx = 0.5 * (E[i, j + 1] - E[i, j - 1])
                dEdy = 0.5 * (E[i + 1, j] - E[i - 1, j])
                det = dEdx.real * dEdy.imag - dEdy.real * dEdx.imag
                if det > 0:
                    npos += 1
                else:
                    nneg += 1
    area = float((n - 2 * margin - 1) ** 2)
    return ntot / area, npos / area, nneg / area


def main():
    out = {}
    for k0 in (np.pi / 8, np.pi / 4, np.pi / 2):
        gen = rng(f"independent-{round(k0,5)}", 42)
        pred_thin = k0**2 / (4 * np.pi)
        ratios, ratios_fft, plus, minus = [], [], [], []
        for _ in range(N_REAL):
            E, pred_mode = plane_wave_field(N, k0, gen)
            tot, po, ne = detect_loop(E, MARGIN)
            ratios.append(tot / pred_mode)
            ratios_fft.append(tot / fft_prediction(E))
            plus.append(po)
            minus.append(ne)
        mean_tot = float(np.mean(np.array(plus) + np.array(minus)))
        out[f"k0_{round(k0,5)}"] = {
            "k0": float(k0),
            "n_real": N_REAL,
            "n_modes": M_MODES,
            "pred_thin_ring_k0sq_over_4pi": float(pred_thin),
            "ratio_mean": float(np.mean(ratios)),
            "ratio_std": float(np.std(ratios, ddof=1)),
            "ratio_vs_biased_fft_mean": float(np.mean(ratios_fft)),
            "charge_imbalance": float(
                abs(np.mean(plus) - np.mean(minus)) / mean_tot if mean_tot > 0 else 0.0
            ),
        }
    out["note"] = (
        "Independent construction (explicit plane-wave sum) and independent "
        "loop-based contour detector. Ratio is to the correct MODE-WEIGHTED "
        "prediction sum|c|^2 kx^2 / sum|c|^2 / (2*pi). The extra "
        "'ratio_vs_biased_fft_mean' uses the FFT-moment predictor, which is biased "
        "for fields whose frequencies are off the DFT grid (spectral leakage); it is "
        "recorded to document that estimator trap."
    )
    path = os.path.join(HERE, "independent_check.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
