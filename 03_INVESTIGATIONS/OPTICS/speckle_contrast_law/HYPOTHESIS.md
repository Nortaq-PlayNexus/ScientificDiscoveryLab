# HYPOTHESIS — Speckle contrast law

- HYPOTHESIS_ID: HYP-001
- QUESTION: Q-O001

## Preregistered hypothesis (frozen)

**H1 (null, default):** The summed fully-developed speckle contrast satisfies
C(M) = 1/sqrt(M) within Monte Carlo error for every M in the tested ladder and
every grid size N in the tested resolution ladder. "Within Monte Carlo error" is
operationalised as: the bootstrap 99% CI on C(M)*sqrt(M) contains 1.0.

**H2 (alternative):** C(M)*sqrt(M) departs from 1 in a resolution-PERSISTENT way
(i.e., deviation width does not shrink towards zero as N grows).

## Rules

- If H2 is not supported at N_max (largest grid), the honest conclusion is H1:
  the law holds; remaining nuisance is sampling.
- If H2 survives at N_max, escalate to REPLICATION + independent implementation
  before any stronger claim; a resolution-persistent deviation at fixed M is
  plausible physics (finite aperture statistics), not automatically a discovery.
- No hypothesis may be changed after seeing the data without a logged change
  (hypothesis_testing.prereg.log_change).

## Prediction

- C(M)*sqrt(M) ~ 1 for all M >= 4, with binomial-scale CI shrinking as N^2 grows.
- Any deviation at fixed M should scale as ~1/N (or faster) if it is a genuine
  grid-sampling artifact (testable at ladder N = 32, 64, 128, 256).