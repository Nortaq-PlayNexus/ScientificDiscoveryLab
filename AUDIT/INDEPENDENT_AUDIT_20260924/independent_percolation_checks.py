from __future__ import annotations

import json
import math
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(r"C:\Users\natha\ScientificDiscoveryLab")
OUT = ROOT / "AUDIT" / "INDEPENDENT_AUDIT_20260924" / "independent_percolation_results.json"
P_C = 0.59274605079210
BASE_SEED = 20260924
STRUCTURE = ndimage.generate_binary_structure(2, 1)


def boxcount(image, box_size):
    h, w = image.shape
    h2, w2 = (h // box_size) * box_size, (w // box_size) * box_size
    blocks = image[:h2, :w2].reshape(h2 // box_size, box_size, w2 // box_size, box_size)
    return np.sum(blocks.any(axis=(1, 3)))


def simulate_largest(L, n, seed, keep_components=False):
    g = np.random.default_rng(seed)
    masses = np.empty(n, dtype=np.float64)
    components = [] if keep_components else None
    for i in range(n):
        occupied = g.random((L, L)) < P_C
        lab, count = ndimage.label(occupied, structure=STRUCTURE)
        if count == 0:
            masses[i] = 0
            if keep_components:
                components.append(np.zeros((L, L), dtype=bool))
        else:
            sizes = np.bincount(lab.ravel())
            masses[i] = int(sizes[1:].max())
            if keep_components and i < 30:
                components.append(lab == (1 + np.argmax(sizes[1:])))
    return masses, components


def slope_summary(Ls, masses_by_L, seed, draws=10000):
    g = np.random.default_rng(seed)
    x = np.log(np.asarray(Ls, float))
    slopes = np.empty(draws)
    for d in range(draws):
        means = [a[g.integers(0, len(a), len(a))].mean() for a in masses_by_L]
        slopes[d] = np.polyfit(x, np.log(means), 1)[0]
    return {
        "Df_mean": float(slopes.mean()), "Df_se": float(slopes.std(ddof=1)),
        "normal_ci95": [float(slopes.mean()-1.96*slopes.std(ddof=1)),
                        float(slopes.mean()+1.96*slopes.std(ddof=1))],
        "theory": 91/48,
    }


def run_sequence(name, sizes, n, seed_offset, keep=False):
    masses, comps = [], []
    for L in sizes:
        t = time.time()
        m, c = simulate_largest(L, n, BASE_SEED + seed_offset + L*1009, keep_components=keep)
        masses.append(m)
        if keep:
            comps.append(c)
        print(name, L, n, float(m.mean()), f"{time.time()-t:.2f}s", flush=True)
    out = {"sizes": list(sizes), "n_per_size": n, "mean_mass": [float(x.mean()) for x in masses],
           "slope": slope_summary(sizes, masses, BASE_SEED + seed_offset + 77)}
    if keep:
        box = [[2,4,8,16,32] for _ in comps]
        individual = []
        for ci, component_list in enumerate(comps):
            for j, img in enumerate(component_list):
                box_sizes = box[ci]
                counts = np.asarray([boxcount(img, b) for b in box_sizes], float)
                ok = np.array(box_sizes) >= 8
                if ok.sum() >= 3:
                    individual.append(np.polyfit(np.log(1/np.array(box_sizes)[ok]), np.log(counts[ok]), 1)[0])
        arr = np.asarray(individual)
        out["box_counting"] = {"n_clusters": len(arr), "mean_Df": float(arr.mean()),
                               "se": float(arr.std(ddof=1)/math.sqrt(len(arr))),
                               "median_Df": float(np.median(arr)), "quantiles": np.quantile(arr,[.025,.5,.975]).tolist()}
    return out


report = {"p_c": P_C, "method": "Independent NumPy PCG64 + scipy.ndimage.label, free-boundary 4-neighbor square site percolation.", "sequences": {}}
report["sequences"]["stored_nonpower2_sequence"] = run_sequence("nonpower2", [127,191,253,449], 200, 10000, keep=True)
report["sequences"]["matched_even_nonpower2"] = run_sequence("even", [126,190,254,446], 200, 20000)
report["sequences"]["matched_odd_nonpower2"] = run_sequence("odd", [129,193,257,445], 200, 30000)
report["sequences"]["power2_original"] = run_sequence("power2", [128,256,512], 150, 40000)
report["sequences"]["power2_extended"] = run_sequence("power2ext", [128,256,512,1024], 60, 50000)
report["sequences"]["nearby_mixed"] = run_sequence("mixed", [129,193,257,449], 200, 60000)

p2 = report["sequences"]["power2_extended"]["slope"]
npow = report["sequences"]["stored_nonpower2_sequence"]["slope"]
diff = p2["Df_mean"] - npow["Df_mean"]
sediff = math.hypot(p2["Df_se"], npow["Df_se"])
report["comparison_power2_vs_nonpower2"] = {
    "difference": diff, "SE_difference": sediff, "z_like": diff/sediff,
    "interpretation": "A single non-power-of-two sequence is not enough to identify power-of-two lattice locking. Compare the matched parity/sequence controls and overlapping confidence intervals."
}

OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(OUT)
print(json.dumps({k: v["slope"] for k,v in report["sequences"].items()}, indent=2))
print(json.dumps(report["comparison_power2_vs_nonpower2"], indent=2))
