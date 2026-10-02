"""Independent replication of the speckle contrast law (no lab engine, no FFT).

Different route: complex Gaussian speckle is generated DIRECTLY as
E = X + iY with X,Y iid N(0,1); intensity |E|^2 is then Exponential, i.e. a
fully-developed speckle pattern (the image-plane limit of a random-phase pupil
by the central limit theorem). Contrast of a sum of M such patterns should be
1/sqrt(M).

Uses numpy's own default_rng (NOT the lab RNG), so agreement is not a shared-
implementation artifact.

Run:  python REPLICATION/independent_check.py
"""

from __future__ import annotations

import json
import os

import numpy as np

rng = np.random.default_rng(20240917)  # independent generator
SHAPE = (256, 256)
N_REAL = 64
M_LADDER = (1, 2, 4, 8, 16)

results = {}
for m in M_LADDER:
    cs = []
    for _ in range(N_REAL):
        summed = np.zeros(SHAPE)
        for _ in range(m):
            x = rng.normal(size=SHAPE)
            y = rng.normal(size=SHAPE)
            summed += x * x + y * y
        cs.append(summed.std() / summed.mean())
    r = float(np.mean(cs) * np.sqrt(m))
    se = float(np.std(cs, ddof=1) * np.sqrt(m) / np.sqrt(N_REAL))
    results[f"M{m}"] = {"r": r, "se": se, "ci_low": r - 3 * se, "ci_high": r + 3 * se}
    print(f"M={m:2d}  r=C*sqrt(M) = {r:.5f}  +/- {3*se:.5f} (3 sigma)")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "independent_check.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump({"generator": "numpy.default_rng(20240917)", "shape": SHAPE,
               "n_real": N_REAL, "results": results}, fh, indent=2, sort_keys=True)
print("\nwritten:", out)