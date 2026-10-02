# Q-P006 — Precision study of 2D percolation critical exponents

## Question
At L in [512, 1024, 2048], what are the 5 critical exponents (D_f, gamma/nu, beta/nu, tau, 1/nu) with full bootstrap uncertainty quantification, and do the ~1sigma deviations from EXP-0009 shrink with L?

## Parent Result
EXP-0009: D_f=1.8697, gamma/nu=1.7596, beta/nu=0.1295, tau=1.9404, 1/nu=0.7434 at L in [128,256,512,1024]. All gates PASS; 3/5 exponents miss tolerances by ~1sigma. EXP-0010 diagnosed as lattice-size artifact.

## Hypothesis (from frozen prereg)
Deviations shrink as L increases (they were lattice-size artifacts at small L). At L=2048, all 5 exponents should be within tolerance.

## Falsification Test
If deviations do NOT shrink with L (or widen), the lattice-artifact diagnosis is incomplete and there is a genuine systematic effect.

## Method (from frozen prereg)
Reuse EXP-0009/EXP-0010 machinery (same prereg, same gates, same C7). Add L=2048. Bootstrap 2000 draws per exponent.

## Parameters (frozen)
- p_c = 0.5927460507921
- L_list = [512, 1024, 2048]
- n_real = {'512': 200, '1024': 100, '2048': 50}
- bootstrap_draws = 2000
- tau_fit_range = [32, 4096]
- tau_L = 2048

## Results
- D_f: 1.863312 +/- 0.042293 (expected 91/48=1.895833, tol=0.015)
- gamma/nu: 1.730146 +/- 0.060413 (expected 43/24=1.791667, tol=0.03)
- beta/nu: 0.137169 +/- 0.040919 (expected 5/48=0.104167, tol=0.015)
- tau: 1.975310 +/- 0.004770 (expected 187/91=2.054945, tol=0.05)
- 1/nu: NOT COMPUTED (runner stub at lines 80-83)

## Audit Notes (2026-09-19)
- All 4 computed exponents deviate from theory (ABNORMAL confirmed numerically)
- tau fails at 16.7sigma
- 1/nu gap is a METHODOLOGY GAP, not a numerical error
- Gates C1, C6, C7, FG not evaluated in results JSON
- _cells files were saved to wrong directory (Q-P005_exponents); COPIED to correct location
