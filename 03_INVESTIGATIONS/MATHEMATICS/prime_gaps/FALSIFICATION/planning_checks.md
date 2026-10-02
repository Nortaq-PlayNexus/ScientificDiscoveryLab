# FALSIFICATION — EXP-0008 (kill-the-hypothesis)

## Attack plan on any interesting result

If any primary gate (G1/G2/G3) flags a deviation from Exp(1):

1. **Is it numerical?** — Gaps are integers, δ computed in float64; no
   integration or optimization; no rounding-sensitive statistic. Ruled out
   by construction.
2. **Is it sampling / range effects?** — Require the deviation to appear in
   ≥ 2 of the 4 disjoint ranges (C6). Single-range deviations are
   treated as finite-range fluctuations and reported, not interpreted.
3. **Is it residue-class structure (small-prime effects)?** — Apply C6
   conditioning by lower prime mod 12 (residues {1,5,7,11} for p ≥ 10^4);
   a deviation "explained" by conditioning is downgraded to a known
   small-prime effect and reported, not escalated.
4. **Is it an estimator artifact?** — C5 method agreement (χ2 vs KS);
   C4 resolution variation (J ∈ {8,10,12}); C3 seed ladder. A deviation
   that depends on bin choice or seed choice is treated as estimator
   noise, not physics.
5. **Is it real but already known?** — Compare to Gallagher (1976) /
   Conrey–Goldston–Keating predictions: the expected answer is agreement,
   since the Poisson model is the standard baseline. Any "deviation" must
   first be reproduced by the independent implementation (C7) before it is
   described as real.
6. **Is it new physics?** — No: prime gaps are a well-studied area; the
   lab never turns an exploratory observation into a preregistered
   conclusion. Even a robust deviation would be reported as
   "inconsistent with the standard Poisson model at these scales" and
   escalated to human scientific review; it would NOT be described as a
   discovery.

## Preregistered falsification criteria (from MASTER_CANDIDATES M2)

- Deviation must survive bootstrap bands across disjoint ranges.
- Deviation must survive residue-class conditioning.
- C2 positive control (Gamma mean-1 surrogate) must be flagged by the
  pipeline (otherwise the gates are not valid and the experiment stops).
