# PREDICTIONS — HYP-005

## If H0 is true (expected)

Per block b ∈ {B1=[1e4,1e5), B2=[1e5,1e6), B3=[1e6,1e7), B4=[1e7,1e8)}:
- mean(δ_b) ≈ 1.0 within bootstrap 95% CI (10000 draws).
- std(δ_b) ≈ 1.0 (Exp(1) variance 1).
- chi-square (10 quantile bins, dof 9) chi2_red ≈ 1 ± noise; not
  significant after BH-FDR across 4 blocks.
- KS statistic vs Exp(1) not significant after BH-FDR.
- P(δ > t) matches e^{−t} within binomial 95% CI for t ∈ {1,2,3,4,5};
  not significant after BH-FDR across 20 cells.
- Overall decision: H0_SUPPORTED; evidence CONTROLLED.

## If H1 is true

- At least one of (chi2_red, KS p, tail z) is significant after BH-FDR
  at alpha = 0.01, in ≥ 1 block, AND survives residue-class conditioning
  AND is reproduced by C7.
- Report the deviation precisely (which t, which block, direction,
  effect size, CI); do NOT interpret as new physics — escalation only.
- Decision: H1_SUPPORTED / INCONSISTENT.
