# EXPERIMENT_PLAN — Q-P008 / EXP-0011 (pilot) and EXP-0013 (main run)

## Purpose

Extend lab pipeline to 3D site percolation. Measure critical exponents (p_c, D_f, gamma/nu, beta/nu, tau) at published 3D values (p_c ≈ 0.3116, D_f ≈ 2.53, gamma/nu ≈ 1.40, beta/nu ≈ 0.41). Test whether the lab's controlled pipeline (perc_engine, G_LAB rng, C7 independent implementation) reproduces these through a pre-registered discipline.

## Systems

3D simple cubic lattice, site percolation, vertical spanning (open BC).

### EXP-0011 (pilot — COMPLETE)
| L | n_real (width) | n_real (exponents) |
|---|---|---|
| 8 | 300 | 500 |
| 16 | 200 | 200 |
| 24 | 100 | 50 |

### EXP-0013 (main — PENDING)
| L | n_real (width) | n_real (exponents) |
|---|---|---|
| 128 | 10 | 1000 |
| 256 | 5 | 500 |
| 512 | 10 | 100 |

## Estimators

- Width: probit MLE per L, crossing at P=0.5, linear 1/L extrapolation
- Exponents: bootstrap log-log slopes of cluster statistics from perc_engine.run_span_cell_edges
- tau: cumulative rank N_>(s) over [4, 1000] at L=24

## Decision rule (from frozen prereg)

- All gates PASS and predictions in tolerance → H0_SUPPORTED
- Gates PASS, predictions out of tolerance → ABNORMAL
- Any gate FAILS → INCONCLUSIVE

## Gates

- C1: width curve at L=16 reproducible (sha256) [pilot config, should be updated to match main L values]
- C7: pure-Python union-find independent: L in {8,16} [pilot config], n=50
- FG: slope stability of D_f on inner L values
- PC1: bootstrap SE + chi2_red reported

## Note on gate config

Gates in prereg files reference pilot L values (8, 16). The main run EXP-0013 uses L in {128, 256, 512}. Gates should be updated to match the actual execution scale when EXP-0013 is run.
