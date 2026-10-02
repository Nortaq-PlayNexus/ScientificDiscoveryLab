# HYPOTHESIS — HYP-005 (EXP-0009, frozen before execution)

## Claim

HYP-005 (H0): In this lab's controlled Monte Carlo pipeline (certified RNG,
graph-CSR connected-components, open-cluster site census, fixed-range log-log
FSS), at p_c = 0.5927460508 on the square lattice:

- P1: D_f from E[M_max] ~ L^{D_f} is within **0.015** of 91/48 (= 1.8958).
- P2: gamma/nu from chi(L) ~ L^{gamma/nu} is within **0.03** of 43/24
  (= 1.7917).
- P3: beta/nu from P_inf(L) = E[M_max]/L^2 ~ L^{-(2 - D_f)} equals 2 - D_f
  and is within **0.015** of 5/48 (= 0.1042).
- P4: the direct tau from the cumulative-rank estimator (L = 1024, range
  [32, 4096]) lies in the apparent window **[1.885, 2.225]** (Fisher value
  187/91 = 2.0549 is only reached asymptotically through the documented
  lattice crossover; the direct finite-domain estimate sits ~1.8-2.0) AND
  rises toward 2.055 with L (tau at L=512 >= tau at L=256 - se, L=1024 >=
  L=512 - se, shared range [32, 2048]).
- P5 (diagnostic to gate): 1/nu from the probit width of a p-scan lies in
  **[0.60, 0.90]** (3/4 expected; SAME gate as Q-P004).
- P6 (scaling relations, internal consistency):
  - R1: |direct tau_meas - (1 + 2/D_f_meas)| <= **0.12** (independent routes
    must agree; this is the strict tau test given the crossover)
  - R2: |2*beta/nu_meas + gamma/nu_meas - 2| <= **0.05**
  - R3: |D_f_meas - (2 - beta/nu_meas)| <= **0.015**

All values are pre-committed tolerances; the estimator *ranges* (L sizes, chi
definition, tau fit range) are frozen in CONFIG/prereg_EXP-0009.json.

## Why this is falsifiable

Every tolerance and estimator is numeric and pre-committed. If the
compatibility gates (C1 determinism, C6 seed ladder, C7 independent
implementation, FG slope stability) hold and the exponents still miss the
windows, the finding is ABNORMAL (escalate; do not interpret). If a gate
trips, the outcome is INCONCLUSIVE by design (estimator/procedure suspect).

## Honest scope

- Reproduction of WELL-KNOWN universality-class exponents via a controlled
  pipeline; NO novelty claimed. Evidence ceiling: CONTROLLED.
- This is the direct quantitative successor of Q-P004's diagnostic-only
  exponent work: beta/nu and 1/nu were report-only there; here they are gated.
- Tau framing is PRE-DECIDED accounting for the known finite-domain crossover
  (apparent exponent < 2.055 at moderate s): the direct gate is an apparent
  window + L-rise check; the precise test lives in R1.

## Relationship

HYP-005 stands on Q-P004's certified RNG + lattice machinery. Q-P004 outcome
is not affected either way by HYP-005.