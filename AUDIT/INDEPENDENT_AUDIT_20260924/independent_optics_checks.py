from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
OUT = ROOT / "AUDIT" / "INDEPENDENT_AUDIT_20260924" / "independent_optics_results.json"
SEED = 20260924


def summarize(values):
    x = np.asarray(values, float)
    m = float(x.mean())
    se = float(x.std(ddof=1) / math.sqrt(len(x))) if len(x) > 1 else float("nan")
    return {"n": len(x), "mean": m, "se": se, "ci99": [m - 2.5758293035489004 * se, m + 2.5758293035489004 * se]}


def real_gaussian(shape, spectrum, gen):
    w = np.sqrt(spectrum / 2.0) * (gen.standard_normal(shape) + 1j * gen.standard_normal(shape))
    idx = (-np.arange(shape[0])) % shape[0]
    jdx = (-np.arange(shape[1])) % shape[1]
    w = 0.5 * (w + np.conj(w[np.ix_(idx, jdx)]))
    return np.fft.ifft2(w).real


def complex_field(shape, spectrum, gen):
    return real_gaussian(shape, spectrum / 2.0, gen) + 1j * real_gaussian(shape, spectrum / 2.0, gen)


def ring_spectrum(shape, k0, halfwidth=0.20):
    fy = np.fft.fftfreq(shape[0]) * 2 * np.pi
    fx = np.fft.fftfreq(shape[1]) * 2 * np.pi
    ky = fy[:, None]
    kx = fx[None, :]
    kr = np.hypot(kx, ky)
    s = ((kr - k0) ** 2 < halfwidth**2).astype(float)
    pred = float((kx**2 * s).sum() / s.sum() / (2 * np.pi))
    return s, pred


def winding_density(E, margin=24):
    a = E[:-1, :-1]
    b = E[:-1, 1:]
    c = E[1:, 1:]
    d = E[1:, :-1]
    circ = (np.angle(b * np.conj(a)) + np.angle(c * np.conj(b))
            + np.angle(d * np.conj(c)) + np.angle(a * np.conj(d)))
    w = np.rint(circ / (2 * np.pi)).astype(int)
    z = w[margin:-margin, margin:-margin]
    return float(np.count_nonzero(z) / z.size), float(np.mean(z > 0)), float(np.mean(z < 0))


def shift_field(E, dx, dy):
    fy = np.fft.fftfreq(E.shape[0])
    fx = np.fft.fftfreq(E.shape[1])
    ramp = np.exp(-2j * np.pi * (fy[:, None] * dx + fx[None, :] * dy))
    return np.fft.ifft2(np.fft.fft2(E) * ramp)


def edge_crossings(g):
    a, b, c, d = g[:-1, :-1], g[:-1, 1:], g[1:, :-1], g[1:, 1:]
    jj, ii = np.meshgrid(np.arange(g.shape[0] - 1), np.arange(g.shape[1] - 1), indexing="ij")
    eps = 1e-12
    ta = np.abs(a) / (np.abs(a) + np.abs(b) + eps)
    tb = np.abs(c) / (np.abs(c) + np.abs(d) + eps)
    tl = np.abs(a) / (np.abs(a) + np.abs(c) + eps)
    tr = np.abs(b) / (np.abs(b) + np.abs(d) + eps)
    mt, mb, ml, mr = a*b < 0, c*d < 0, a*c < 0, b*d < 0
    tx, ty = jj + ta, ii
    bx, by = jj + tb, ii + 1
    lx, ly = jj, ii + tl
    rx, ry = jj + 1, ii + tr
    ok = mt.astype(int) + mb.astype(int) + ml.astype(int) + mr.astype(int) == 2
    p1x = np.where(mt, tx, np.where(mb, bx, np.where(ml, lx, rx)))
    p1y = np.where(mt, ty, np.where(mb, by, np.where(ml, ly, ry)))
    p2x = np.where(mr, rx, np.where(ml, lx, np.where(mb, bx, tx)))
    p2y = np.where(mr, ry, np.where(ml, ly, np.where(mb, by, ty)))
    return p1x, p1y, p2x, p2y, ok


def contour_density(E, margin=24):
    ar1x, ar1y, ar2x, ar2y, okr = edge_crossings(E.real)
    br1x, br1y, br2x, br2y, oki = edge_crossings(E.imag)
    d1x, d1y = ar2x-ar1x, ar2y-ar1y
    d2x, d2y = br2x-br1x, br2y-br1y
    den = d1x*d2y-d1y*d2x
    wx, wy = br1x-ar1x, br1y-ar1y
    with np.errstate(divide="ignore", invalid="ignore"):
        s = (wx*d2y-wy*d2x)/den
        u = (wx*d1y-wy*d1x)/den
    hit = okr & oki & (den != 0) & (s >= 0) & (s <= 1) & (u >= 0) & (u <= 1)
    z = hit[margin:-margin, margin:-margin]
    return float(z.sum()/z.size)


def speckle_direct(shape, m, gen):
    total = np.zeros(shape)
    for _ in range(m):
        x = gen.normal(size=shape)
        y = gen.normal(size=shape)
        total += x*x+y*y
    return float(total.std()/total.mean())


def speckle_pupil(shape, m, gen):
    radius = int(min(shape)/8)
    y0, x0 = -(shape[0] // 2), -(shape[1] // 2)
    yy, xx = np.mgrid[y0:y0 + shape[0], x0:x0 + shape[1]]
    pupil = (xx*xx+yy*yy) <= radius*radius
    total = np.zeros(shape)
    for _ in range(m):
        phase = gen.uniform(0, 2*np.pi, size=shape)
        field = np.fft.ifft2(pupil*np.exp(1j*phase))
        total += np.abs(field)**2
    return float(total.std()/total.mean())


report = {"seed": SEED, "method": "Independent NumPy PCG64 implementation; no project RNG or project analysis functions.", "speckle": {}, "vortex": {}}

# Speckle direct and pupil routes on non-square and non-power-of-two grids.
gen = np.random.default_rng(SEED + 1)
for shape in [(255, 255), (256, 256), (257, 257), (255, 257), (257, 255)]:
    direct = {}
    pupil = {}
    for m in [1, 2, 4, 8, 16]:
        vals = [speckle_direct(shape, m, gen) for _ in range(80)]
        direct[str(m)] = {**summarize(vals), "r_mean": summarize(vals)["mean"]*math.sqrt(m)}
        vals2 = [speckle_pupil(shape, m, gen) for _ in range(80)]
        pupil[str(m)] = {**summarize(vals2), "r_mean": summarize(vals2)["mean"]*math.sqrt(m)}
    report["speckle"][f"{shape[0]}x{shape[1]}"] = {"direct_complex_gaussian": direct, "random_phase_pupil_fft": pupil}

# Vortex density across square, rectangular, and shifted grids.
for k0, nreal in [(np.pi/8, 20), (np.pi/4, 12)]:
    for shape in [(255,255), (256,256), (257,257), (255,257), (257,255), (509,509)]:
        nr = max(6, nreal//2) if max(shape) >= 509 else nreal
        s, pred = ring_spectrum(shape, k0)
        g = np.random.default_rng(SEED + int(k0*1e6) + shape[0]*1000 + shape[1])
        ratios, contours, plus, minus, shifts = [], [], [], [], []
        for _ in range(nr):
            e = complex_field(shape, s, g)
            n, p, m = winding_density(e)
            ratios.append(n/pred); plus.append(p); minus.append(m)
            if len(ratios) <= min(8, nr):
                contours.append(contour_density(e)/pred)
                es = shift_field(e, 0.5, 0.37)
                ns, _, _ = winding_density(es)
                shifts.append((ns-n)/n if n else np.nan)
        key = f"k0_{k0:.5f}_{shape[0]}x{shape[1]}"
        report["vortex"][key] = {
            "n_real": nr, "prediction": pred,
            "ratio": summarize(ratios),
            "contour_ratio_first8": summarize(contours),
            "mean_plus": float(np.mean(plus)), "mean_minus": float(np.mean(minus)),
            "charge_imbalance": abs(float(np.mean(plus)-np.mean(minus)))/float(np.mean(np.array(plus)+np.array(minus))),
            "half_pixel_shift_relative_delta_first8": summarize(shifts),
        }

OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(OUT)
print(json.dumps({
    "speckle_r_ranges": {
        k: [min(v["direct_complex_gaussian"][m]["r_mean"] for m in v["direct_complex_gaussian"]),
            max(v["direct_complex_gaussian"][m]["r_mean"] for m in v["direct_complex_gaussian"])]
        for k,v in report["speckle"].items()
    },
    "vortex_ratio_ranges_by_k0": {
        f"{k0:.5f}": [min(v["ratio"]["mean"] for k, v in report["vortex"].items() if k.startswith(f"k0_{k0:.5f}")),
                      max(v["ratio"]["mean"] for k, v in report["vortex"].items() if k.startswith(f"k0_{k0:.5f}"))]
        for k0 in [np.pi/8,np.pi/4]
    },
    "max_charge_imbalance": max(v["charge_imbalance"] for v in report["vortex"].values()),
    "max_abs_shift_delta_mean": max(abs(v["half_pixel_shift_relative_delta_first8"]["mean"]) for v in report["vortex"].values()),
}, indent=2))
