"""Audit-only corrected controls for the EXP-0003 broadband sub-audit.

The parallel sub-agent's raw interpolation output exposed a factor-of-4/16
normalization error in its refined-density helper. This script does not alter
that historical/sub-agent code; it reruns the controls with the corrected
conversion (refined density * factor^2), plus direct-complex, low-pass, and
regularized synthetic-vortex checks.
"""
from __future__ import annotations

import importlib.util
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SUB = HERE.parent / "SUBAGENT_EXP0003_BROADBAND_20260924"
mod_path = SUB / "CODE" / "run_broadband_convergence.py"
spec = importlib.util.spec_from_file_location("broadband_impl", mod_path)
assert spec and spec.loader
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def corrected_refined_density(E: np.ndarray, margin: int, factor: int) -> float:
    Er = b.fourier_refine(E, factor)
    wm = b.winding_metrics(Er, margin * factor)
    # A refined grid has factor^2 times as many cells. Convert density per
    # refined cell back to density per original physical cell by multiplying.
    return float(wm["winding_density"] * factor * factor)


def regularized_vortex(n: int = 65) -> np.ndarray:
    yy, xx = np.mgrid[0:n, 0:n]
    E = (xx - n // 2).astype(complex) + 1j * (yy - n // 2)
    E[n // 2, n // 2] = 1e-12 * (1 + 1j)
    return E


def direct_complex_field(S: np.ndarray, gen: np.random.Generator) -> np.ndarray:
    coeff = np.sqrt(0.5 * S) * (
        gen.standard_normal(S.shape) + 1j * gen.standard_normal(S.shape)
    )
    return np.fft.ifft2(coeff)


def summarize_interpolation() -> list[dict]:
    rows = []
    for p in (4, 6, 8, 12, 16):
        for s in (0.10, 0.50, 0.75):
            n = p * b.WAVELENGTHS
            dx = 2.0 * np.pi / (b.KAPPA0 * p)
            S, KX, _, _ = b.make_spectrum(n, n, dx, s)
            m = b.margin_for(p)
            pred = b.discrete_prediction(S, KX)
            for seed in b.SEEDS:
                E = b.make_field(S, b.rng_for(seed, s, p, 2600, tag=0xE11A0BE + 171))
                original = b.winding_metrics(E, m)["winding_density"]
                for factor in (2, 4):
                    refined = corrected_refined_density(E, m, factor)
                    rows.append({
                        "control": "corrected_fourier_interpolation",
                        "P": p, "sigma": s, "seed": seed, "factor": factor,
                        "prediction_per_original_cell": pred,
                        "original_density": original,
                        "refined_density_per_original_cell": refined,
                        "original_ratio": original / pred,
                        "refined_ratio": refined / pred,
                        "gain": refined / original if original else None,
                    })
    return rows


def summarize_lowpass() -> list[dict]:
    rows = []
    for p in (4, 8, 16, 32):
        n = p * b.WAVELENGTHS
        dx = 2.0 * np.pi / (b.KAPPA0 * p)
        nyq_over_k0 = p / 2.0
        for s in (0.50, 0.75):
            for cutoff in (1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0):
                if cutoff > nyq_over_k0 + 1e-12:
                    continue
                for seed in b.SEEDS:
                    S, KX, _, _ = b.make_spectrum(n, n, dx, s, cutoff_kappa0=cutoff)
                    E = b.make_field(S, b.rng_for(seed, s, p, 2700, tag=0xE11A0BE + 181))
                    m = b.margin_for(p)
                    measured = b.winding_metrics(E, m)["winding_density"]
                    pred_disc = b.discrete_prediction(S, KX)
                    pred_cont_phys = b.continuum_prediction(s, cutoff)
                    pred_cont = pred_cont_phys * dx * dx
                    rows.append({
                        "control": "controlled_lowpass",
                        "P": p, "sigma": s, "seed": seed,
                        "cutoff_over_k0": cutoff, "grid_nyquist_over_k0": nyq_over_k0,
                        "measured_density": measured,
                        "discrete_prediction": pred_disc,
                        "continuous_truncated_prediction": pred_cont,
                        "ratio_discrete": measured / pred_disc,
                        "ratio_continuous_truncated": measured / pred_cont,
                    })
    return rows


def summarize_direct() -> list[dict]:
    rows = []
    for p in (4, 8, 16, 32):
        n = p * b.WAVELENGTHS
        dx = 2.0 * np.pi / (b.KAPPA0 * p)
        for s in (0.10, 0.50, 0.75):
            S, KX, _, _ = b.make_spectrum(n, n, dx, s)
            pred = b.discrete_prediction(S, KX)
            for seed in b.SEEDS:
                E = direct_complex_field(S, b.rng_for(seed, s, p, 2800, tag=0xE11A0BE + 191))
                measured = b.winding_metrics(E, b.margin_for(p))["winding_density"]
                rows.append({
                    "control": "direct_complex_fft", "P": p, "sigma": s,
                    "seed": seed, "measured_density": measured,
                    "prediction": pred, "ratio": measured / pred,
                })
    return rows


def main() -> None:
    t0 = time.time()
    out = {
        "purpose": "Corrected controls after sub-agent interpolation normalization failure",
        "source_implementation": str(mod_path),
        "environment": {"python": sys.version, "platform": platform.platform()},
        "known_bug_corrected": "refined density was divided by factor^2; corrected helper multiplies by factor^2",
        "synthetic_vortex": {},
        "interpolation": summarize_interpolation(),
        "lowpass": summarize_lowpass(),
        "direct_complex": summarize_direct(),
    }
    E = regularized_vortex()
    out["synthetic_vortex"] = {
        "winding": b.winding_metrics(E, 4),
        "contour": b.contour_metrics(E, 4),
    }
    # Compact summaries for report use.
    def group(rows, keys, ratio_key):
        result = []
        groups = {}
        for r in rows:
            k = tuple(r[x] for x in keys)
            groups.setdefault(k, []).append(r[ratio_key])
        for k, vals in groups.items():
            v = np.asarray(vals, dtype=float)
            result.append({**dict(zip(keys, k)), "n": len(v), "mean": float(v.mean()),
                           "sd": float(v.std(ddof=1)) if len(v) > 1 else 0.0})
        return result
    out["summaries"] = {
        "interpolation_by_P_sigma_factor": group(out["interpolation"], ["P", "sigma", "factor"], "refined_ratio"),
        "lowpass_by_P_sigma_cutoff": group(out["lowpass"], ["P", "sigma", "cutoff_over_k0"], "ratio_discrete"),
        "direct_by_P_sigma": group(out["direct_complex"], ["P", "sigma"], "ratio"),
    }
    out["elapsed_seconds"] = time.time() - t0
    path = HERE / "broadband_controls_corrected_results.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"synthetic_vortex": out["synthetic_vortex"],
                      "summaries": out["summaries"]}, indent=2))
    print(f"Wrote {path}; elapsed={out['elapsed_seconds']:.1f}s")


if __name__ == "__main__":
    main()
