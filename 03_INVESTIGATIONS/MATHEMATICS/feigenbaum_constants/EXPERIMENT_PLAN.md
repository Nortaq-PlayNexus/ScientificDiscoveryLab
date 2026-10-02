# EXPERIMENT_PLAN — EXP-0014 (preregistered)

## Experiment ID
EXP-0014

## Date
2026-09-21

## Question
Q-M005 — Feigenbaum universality in higher-order 1D maps

## Hypothesis
HYP-M005 — delta_n and alpha_n converge to z-dependent universal constants

## Protocol (frozen)

1. Implement the superstable-cycle finder for f(x) = 1 - a*|x|^z on [-1,1].
2. For each z in {2, 3, 4}:
   a. Find parameters a_n for n = 1..8 where the critical point x=0 is periodic with period 2^n.
   b. Compute delta_n = (a_{n-1} - a_{n-2}) / (a_n - a_{n-1}).
   c. Compute alpha_n from eigenvalue scaling at the period-2^n orbit.
3. Record all a_n, delta_n, alpha_n with full precision.
4. Compare against published values (Feigenbaum 1978, Hu & Mao 1982).
5. Assess convergence rate and numerical stability.
6. Run controls C1–C7.

## Parameters (frozen)
- Map family: f(x) = 1 - a*|x|^z, z in {2, 3, 4}
- Domain: [-1, 1]
- n range: 1..8 (period 2..256)
- Root finder: Newton with brentq fallback
- Convergence tolerance: 1e-12
- Seeds: 1, 2, 3, 4, 5 (for seed variation control)

## Steps
baseline (z=2 known values) / control (C1-C7) / experiment (all z) /
statistics (convergence analysis) / report

## Result
null (pending)

## Evidence
UNTESTED