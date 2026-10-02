# HYPOTHESIS — HYP-005

## Claim

Normalized prime gaps δ = (p_{i+1} − p_i) / ln(p_i), computed over the
integers up to 10^8 in four disjoint ranges, are distributed as Exp(1)
(the Poisson/Gallagher model for normalized prime gaps).

## Null hypothesis (H0)

δ_i in each range are i.i.d. Exp(1): mean = 1, variance = 1,
P(δ > t) = e^{−t}. Verified by chi-square goodness-of-fit (10
exponential-quantile bins), Kolmogorov–Smirnov vs fully specified Exp(1),
and binomial survival tests at t ∈ {1,2,3,4,5}.

## Alternative hypothesis (H1)

A reproducible systematic deviation from Exp(1) that (a) survives BH-FDR
correction at alpha = 0.01 across blocks, (b) survives residue-class
conditioning (p mod 12), and (c) is reproduced by an independent
implementation (C7). The prime-gap distribution is NOT the Poisson
model at these ranges/scales.

## Anchor / what reproduction means

- Reproduction = agreement with Exp(1) within bootstrap uncertainty,
  quantified per block and overall via BH-FDR.
- Anchor: Exp(1) with mean 1 and CDF 1 − e^{−t}.
- If H0 holds (expected): evidence = CONTROLLED (known result reproduced).
- If H1 holds: evidence = INCONSISTENT with the standard Poisson model;
  escalation (report only, no claim of new physics — the model is a
  heuristic, and deviations of this kind are numerical/analytic data, not
  a theorem).

## Status

PREREGISTERED (frozen before any run; hash recorded in EXP-0008_experiment.json).
