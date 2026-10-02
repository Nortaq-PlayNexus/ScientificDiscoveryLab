# Seed robustness — EXP-0015

**Source:** `RESULTS/seed_ladder_20260924_135627.json`

Six independent seeds `{42, 7, 123, 2023, 314159, 271828}` were used for
band-limited random complex fields at grids 128 and 256, four spectral bands,
and z=0/1280 µm. The table below gives the z=1280 count mean and coefficient
of variation across seeds.

| Grid | Band | Raw | Clustered | Supported | Local-minimum contour |
|---:|---:|---:|---:|---:|---:|
| 128 | 0.05 | 233 ± 21 (CV 9.2%) | 233 ± 21 (9.2%) | 233 ± 22 (9.3%) | 186 ± 13 (7.0%) |
| 128 | 0.10 | 451 ± 18 (4.0%) | 450 ± 18 (4.0%) | 448 ± 17 (3.7%) | 300 ± 18 (6.0%) |
| 128 | 0.20 | 879 ± 19 (2.1%) | 872 ± 21 (2.4%) | 848 ± 22 (2.5%) | 251 ± 8 (3.1%) |
| 128 | 0.35 | 1487 ± 32 (2.1%) | 1450 ± 34 (2.3%) | 1287 ± 39 (3.0%) | 228 ± 14 (5.9%) |
| 256 | 0.05 | 901 ± 37 (4.1%) | 901 ± 37 (4.1%) | 901 ± 37 (4.1%) | 351 ± 10 (2.7%) |
| 256 | 0.10 | 1786 ± 44 (2.5%) | 1781 ± 42 (2.4%) | 1774 ± 45 (2.5%) | 299 ± 10 (3.3%) |
| 256 | 0.20 | 3542 ± 37 (1.0%) | 3515 ± 39 (1.1%) | 3421 ± 39 (1.1%) | 259 ± 9 (3.6%) |
| 256 | 0.35 | 5999 ± 59 (1.0%) | 5836 ± 55 (0.9%) | 5162 ± 40 (0.8%) | 247 ± 7 (2.9%) |

The exact values are in the JSON; the rounded table is descriptive. Seed
variation is small within a fixed detector, but detector means can differ by
orders of magnitude. Therefore a random-field count is not a detector-
independent observable. This is a numerical-method result, not a new physical
density law.
