# Experiment Plan — Q-P007 (EXP-0009PC)

## Purpose

Determine whether refined p_c accuracy explains the exponent deviations measured in EXP-0009 (Q-P006). Measure p_c via width-curve crossing at L in {512, 1024, 2048}, extrapolate to L→∞, re-measure critical exponents at refined p_c.

## System

Square lattice site percolation, open BC, width curves at L in {512, 1024, 2048}.

| L | width n_each | width grid | exponent n_real |
|---|---|---|---|
| 512 | 200 | [0.588, 0.597, 0.001] | 100 |
| 1024 | 140 | [0.589, 0.596, 0.0005] | 50 |
| 2048 | 100 | [0.590, 0.595, 0.0005] | 25 |

## Method

1. Width curves at each L (probit MLE, s0=0.10)
2. Linear 1/L extrapolation → p_c(L→∞)
3. Re-measure D_f, gamma/nu, beta/nu at refined p_c using run_exp0009 machinery
4. tau via cumulative rank at L=2048 (diagnostic)

## Decision rule (from frozen prereg)

- All gates PASS and predictions in tolerance → H0_SUPPORTED
- Gates PASS, predictions out of tolerance → ABNORMAL
- Any gate FAILS → INCONCLUSIVE

## Status

COMPLETE (2026-09-19, 813s). Result: p_c(L→∞) = 0.59272900 (|dev| from Ziff: 0.000017). All computable exponents PASS.
