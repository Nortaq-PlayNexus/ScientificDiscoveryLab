# Null analysis — EXP-0015

**Source:** `RESULTS/nulls_42_20260924_140054.json` (442 s, 256 rows)

The null stage compared the designed four-vortex field with a matched-spectrum
Fourier-phase surrogate, a matched-amplitude pointwise-phase surrogate, and a
band-limited random complex Gaussian field at grids 64, 128, 256, and 512 and
z=0, 320, 640, 1280 µm.

## Representative results at z=1280 µm

| Grid | Detector | Target | Matched spectrum | Matched amplitude | Random Gaussian |
|---:|---|---:|---:|---:|---:|
| 64 | raw | 4 | 16 | 950 | 171 |
| 64 | local contour | 4 | 12 | 183 | 93 |
| 128 | raw | 4 | 28 | 5283 | 626 |
| 128 | local contour | 4 | 24 | 284 | 246 |
| 256 | raw | 4 | 18 | 21850 | 2824 |
| 256 | local contour | 4 | 18 | 289 | 260 |
| 512 | raw | 4 | 22 | 87179 | 10962 |
| 512 | local contour | 4 | 22 | 297 | 235 |

The target is not a high-count excess in these controls. The nulls demonstrate
that raw winding counts are highly sensitive to phase randomization and grid
size, while the bounded local-contour detector counts a very different
population. Pointwise matched-amplitude randomization is not a zero-vortex
null; it creates many phase singularities.

## Statistical limitation

This stage uses one deterministic surrogate per grid/condition, so it is a
stress comparison, not an empirical p-value distribution. The six-seed random
ladder in `SEED_ROBUSTNESS.md` supplies distributional information for random
fields, but a dedicated multi-seed matched-spectrum null is still required
before making a formal significance statement.

## Conclusion

The null battery kills any claim that the clean analytical target's count is
anomalously high. It supports the narrower conclusion that **count semantics
and detector choice dominate the measurement**. No novelty claim follows.
