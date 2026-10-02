# HYPOTHESIS — HYP-004 (EXP-0005, frozen before execution)

## Claim

HYP-004 (H0): In this lab's controlled Monte Carlo pipeline (certified RNG,
scipy.ndimage batched labeling + pure-Python union-find estimators, fixed-exponent
finite-size scaling):

- P1: The extrapolated bond-percolation p_c from VERTICAL SPANNING (open square)
  lies within **0.01** of 1/2 (exact anchor).
- P2: The extrapolated bond-percolation p_c from the TORUS WRAPPING estimator
  (small-report-scale systems) lies within **0.01** of 1/2.
- P3: The extrapolated SITE-percolation p_c from vertical spanning lies within
  **0.01** of 0.5927460508.
- P4 (diagnostic): the free correlation-length exponent from the crossing-width
  log-log slope lies in [0.60, 0.90] (1/nu = 3/4 expected). Report-only order-
  parameter detail: beta/nu is NOT gated in this experiment (out of scope).

## Why this is falsifiable

Every tolerance is numeric and pre-committed. A deviation that survives the
compatibility gates (C2 estimator agreement, C4 scale stability, C7 independent
implementation) and the fit-goodness gate would be an ABNORMAL finding (escalate,
do not interpret). A broken procedure (gates trip) is INCONCLUSIVE by design — the
estimator/BC machinery, not physics, is the suspect.

## Honest scope

- Reproduction of WELL-KNOWN values; no novelty claimed. Success calibrates the
  lab's random-lattice machinery; failure (after bug-fixing per lab flow) would be
  a red flag for the whole lab.
- "nu = 4/3" is the 2D percolation universality-class value used as the fixed
  exponent in the FSS model and as the diagnostic target; the lab measures it only
  as a diagnostic, not as a proof.

## Relationship

HYP-004 is a HYGIENE hypothesis. It does not inherit from HYP-001..003, and no
prior lab question is affected by its outcome either way.