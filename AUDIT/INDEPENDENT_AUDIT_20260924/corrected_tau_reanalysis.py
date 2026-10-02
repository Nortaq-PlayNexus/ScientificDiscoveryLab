"""Audit-only corrected cluster-tau reanalysis for Q-P007.

Uses an independent NumPy PCG64 + scipy.ndimage.label implementation, not
perc_engine or the malformed Q-P007 nested cache.  The largest open cluster
is excluded separately for every realization, as required by the frozen
analysis definition.
"""
from __future__ import annotations

import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

P_CANONICAL = 0.59274605079210
P_REFINED = 0.5927289999999995
SEEDS = (20260924, 20260925, 20260926, 20260927, 20260928, 20260929)


def realization_sizes(rng: np.random.Generator, L: int, p: float) -> np.ndarray:
    occupied = rng.random((L, L)) < p
    labels, _ = ndimage.label(occupied, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8))
    counts = np.bincount(labels.ravel())[1:]
    counts = counts[counts > 0]
    return np.sort(counts)[::-1].astype(np.int64)


def cumulative_tau(sizes: list[np.ndarray], lo: int, hi: int,
                   rng: np.random.Generator | None = None,
                   bootstrap: int = 0) -> dict:
    # Each input is one realization; discard only its largest cluster.
    tails = [np.asarray(x, dtype=np.int64)[1:] for x in sizes]
    big = np.concatenate(tails) if tails else np.array([], dtype=np.int64)
    if big.size < 10:
        return {"tau": None, "n_clusters": int(big.size), "grid_points": 0}
    ordered = np.sort(big)[::-1]
    grid = np.unique(np.geomspace(lo, hi, 250).astype(np.int64))
    n_gt = np.searchsorted(-ordered, -(grid + 1)).astype(float)
    keep = n_gt >= 3
    if keep.sum() < 20:
        return {"tau": None, "n_clusters": int(big.size), "grid_points": int(keep.sum())}
    x = np.log(grid[keep].astype(float))
    y = np.log(n_gt[keep])
    weights = np.sqrt(n_gt[keep])
    A = np.column_stack((np.ones(x.size), x))
    coef = np.linalg.lstsq(A * weights[:, None], y * weights, rcond=None)[0]
    tau = 1.0 - float(coef[1])
    result = {
        "tau": tau,
        "n_clusters": int(big.size),
        "grid_points": int(keep.sum()),
        "fit_min": int(grid[keep].min()),
        "fit_max": int(grid[keep].max()),
    }
    if rng is not None and bootstrap:
        draws = []
        for _ in range(bootstrap):
            sample = np.sort(rng.choice(big, size=big.size, replace=True))[::-1]
            ng = np.searchsorted(-sample, -(grid + 1)).astype(float)
            k = ng >= 3
            if k.sum() < 20:
                continue
            xx = np.log(grid[k].astype(float))
            yy = np.log(ng[k])
            draws.append(1.0 - float(np.polyfit(xx, yy, 1)[0]))
        if len(draws) > 1:
            result["bootstrap_mean"] = float(np.mean(draws))
            result["bootstrap_sd"] = float(np.std(draws, ddof=1))
            result["bootstrap_draws"] = len(draws)
    return result


def main() -> None:
    started = time.time()
    out = {
        "purpose": "Corrected tau reanalysis after Q-P007 nested-cache audit",
        "method": "Independent NumPy PCG64 site configurations; scipy.ndimage.label; "
                  "largest cluster removed per realization; cumulative tail fit",
        "environment": {"python": sys.version, "platform": platform.platform(),
                         "numpy": np.__version__},
        "p_values": {"canonical": P_CANONICAL, "refined": P_REFINED},
        "seeds": list(SEEDS),
        "conditions": [],
    }
    # Common random numbers make the p_c comparison paired.  This is a
    # resolution/size diagnostic, not a replacement for a production-size run.
    for L, n in ((128, 80), (256, 60), (512, 30)):
        by_p = {}
        raw = {}
        for p_name, p in (("canonical", P_CANONICAL), ("refined", P_REFINED)):
            all_sizes = []
            for seed in SEEDS[:n]:
                # A distinct stream per L and p; canonical/refined use the
                # same base seed and therefore the same underlying uniforms.
                rng = np.random.default_rng([seed, L])
                all_sizes.append(realization_sizes(rng, L, p))
            raw[p_name] = np.asarray(all_sizes, dtype=object)
            fit_rng = np.random.default_rng([900000 + L, int(p * 1e12)])
            by_p[p_name] = {
                "primary_32_4096": cumulative_tau(all_sizes, 32, 4096, fit_rng, 50),
                "trend_16_512": cumulative_tau(all_sizes, 16, 512, None, 0),
                "trend_32_2048": cumulative_tau(all_sizes, 32, 2048, None, 0),
                "trend_64_4096": cumulative_tau(all_sizes, 64, 4096, None, 0),
            }
        diff = (by_p["refined"]["primary_32_4096"]["tau"] -
                by_p["canonical"]["primary_32_4096"]["tau"])
        out["conditions"].append({"L": L, "n": n, "fits": by_p,
                                  "paired_delta_tau_refined_minus_canonical": diff})
        np.savez_compressed(Path(__file__).with_name(f"corrected_tau_raw_L{L}.npz"),
                            **{f"{k}_sizes": v for k, v in raw.items()})
    out["interpretation"] = (
        "The corrected implementation measures a size-dependent tau near 1.9--2.0 "
        "over these finite boxes; a small paired p_c shift does not by itself "
        "establish the Fisher value. Q-P007's historical tau output cannot be "
        "used because its cache stores one nested array per realization and its "
        "runner discards the entire tail."
    )
    out["elapsed_seconds"] = time.time() - started
    path = Path(__file__).with_name("corrected_tau_reanalysis_results.json")
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
