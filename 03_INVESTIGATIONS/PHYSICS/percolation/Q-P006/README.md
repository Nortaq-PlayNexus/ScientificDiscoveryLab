# Q-P006 — Precision study of 2D percolation critical exponents

## Question
At L ∈ {512, 1024, 2048}, what are the 5 critical exponents (D_f, γ/ν, β/ν, τ, 1/ν) with full bootstrap uncertainty quantification, and do the ~1σ deviations from EXP-0009 shrink with L?

## Parent Result
EXP-0009: D_f=1.8697, γ/ν=1.7596, β/ν=0.1295, τ=1.9404, 1/ν=0.7434 at L ∈ {128,256,512,1024}. All gates PASS. 3/5 exponents miss tolerances by ~1σ. EXP-0010 diagnosed as lattice artifact.

## Hypothesis
Deviations shrink as L increases (they were lattice-size artifacts at small L). At L=2048, all 5 exponents should be within tolerance.

## Falsification Test
If deviations do NOT shrink with L (or widen), the lattice-artifact diagnosis is incomplete and there is a genuine systematic effect.

## Method
Reuse EXP-0009/EXP-0010 machinery (same prereg, same gates, same C7). Add L=2048. Bootstrap 2000 draws per exponent.

## Computational Requirements
CPU-hours (L=2048 at 200 realizations is ~8× EXP-0009 at L=1024).

## Parameters
- p_c = 0.5927460507921 (site, square lattice)
- L_list = [512, 1024, 2048]
- n_real per L: varies (EXP-0011 pilot: L8=500, L16=200, L24=50; main run EXP-0013: L128=1000, L256=500, L512=100)
- bootstrap_draws = 2000
- seeds: 101, 202, 303 per L (independent)

## Prereg Status

FROZEN and executed (EXP-0011, 2026-09-19). Decision: ABNORMAL (gates PASS, exponents out of tolerance).

## Files
- CONFIG/prereg_Q-P006.json (frozen)
- CODE/run_exp0011.py (executed, EXP-0011)
- CODE/RESULTS/ (populated)
- REPORT/TECHNICAL_EXP-0009-precision.md (populated)
