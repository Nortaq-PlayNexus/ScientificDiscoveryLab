"""Finite-window sensitivity check for the fixed-spectrum convergence result.

The main sweep uses a 24-wavelength physical box for tractability.  This check
uses 128 wavelengths, so at P=4 its grid is N=512 (the historical EXP-0003
broadband grid size) and tests whether the convergence ratios depend on the
finite physical window/mode density.  It shares the main implementation by
design; it is a sensitivity/robustness check, not an independent validation.
"""
from __future__ import annotations
import csv, json, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_broadband_convergence as r

r.WAVELENGTHS = 128
OUT = r.RESULTS
rows = []
t0 = time.perf_counter()
for p in (4, 8, 16):
    for s in r.SIGMA_EXP:
        for seed in r.SEEDS:
            row = r.run_realization(p, s, seed, 0, detail=False)
            row["control_family"] = "large_physical_window_128_wavelengths"
            rows.append(row)
            print(f"WINDOW P={p} sigma={s} seed={seed} ratio_full={row['ratio_cont_full']:.5f} ratio_disc={row['ratio_discrete']:.5f}", flush=True)
fields = list(rows[0]) if rows else []
with (OUT / "large_window_validation.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
summary = []
for p in (4, 8, 16):
    for s in r.SIGMA_EXP:
        rr = [x for x in rows if x["p_pixels_per_wavelength"] == p and x["sigma_exp_rad_per_pixel_at_P4"] == s]
        summary.append({"P": p, "sigma_k": s, "n": len(rr), "N": rr[0]["n"] if rr else None, "ratio_full": float(np.mean([x["ratio_cont_full"] for x in rr])) if rr else None, "ratio_discrete": float(np.mean([x["ratio_discrete"] for x in rr])) if rr else None, "ratio_full_std": float(np.std([x["ratio_cont_full"] for x in rr], ddof=1)) if len(rr) > 1 else 0.0})
(OUT / "large_window_validation_summary.json").write_text(json.dumps({"physical_box_wavelengths": 128, "elapsed_seconds": time.perf_counter()-t0, "rows": summary}, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"elapsed_seconds": time.perf_counter()-t0, "summary": summary}, indent=2))
