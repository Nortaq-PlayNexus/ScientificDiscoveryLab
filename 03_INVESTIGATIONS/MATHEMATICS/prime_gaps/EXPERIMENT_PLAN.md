# EXPERIMENT_PLAN — EXP-0008 (Q-M002)

## Purpose

Reproduce the Poisson/Gallagher (1976) prediction for normalized prime
gaps at four disjoint ranges up to 10^8 on this machine, with a complete
control suite, bootstrap uncertainty, BH-FDR correction, an independent
replication (C7), and an explicit falsification protocol. Same epistemic
posture as EXP-0002/0003/0004: known-law reproduction / calibration.
Evidence ceiling: CONTROLLED (reproduction) unless a reproducible
deviation survives all gates and conditioning; then escalation only, no
novelty claim.

## Dataset generation (deterministic)

- Prime generation: sieve of Eratosthenes over [0, N_MAX] with N_MAX = 10^8,
  implemented with numpy boolean arrays. Deterministic; no RNG used for
  primes (the integers are what they are).
- Blocks (disjoint ranges by lower prime p):
  - B1 = [10^4, 10^5), B2 = [10^5, 10^6), B3 = [10^6, 10^7), B4 = [10^7, 1e8).
  - Block assignment is by p_i (the lower prime of the gap), so blocks are
    disjoint in prime index space.
- Normalized gap δ_i = (p_{i+1} − p_i) / ln(p_i) (float64).
- No external datasets, no downloads, CPU-only.

## Primary statistic

- χ² goodness-of-fit vs Exp(1) on J = 10 exponential-quantile bins
  (edges −ln(1 − j/10), j = 1..9, so each bin has expected count n_b/10).
  χ2_red = χ² / dof (dof = 9 per block).
- Combined across blocks = sum of per-block χ² (dof = 36).

## Secondary statistics

- Bootstrap 95% percentile CI on mean(δ_b): 10000 resamples, rng
  "exp0008-boot", seed 42 per block.
- KS vs fully-specified Exp(1) per block (exact, no parameter estimation).
- Tail survival P(δ > t) at t ∈ {1,2,3,4,5}: per block, z = (observed − n·e^{−t}) / √(n·e^{−t}·(1−e^{−t})); two-sided p vs standard normal; BH-FDR across 20 cells.

## Statistical tests / alpha

- BH-FDR at alpha = 0.01 for all multiplicity-adjusted decisions
  (RESEARCH_RULES §6 default). No post-hoc alpha changes.

## Decision rule (frozen)

- **H0_SUPPORTED**: G1 (χ2_red not significant after BH-FDR, all blocks),
  G2 (bootstrap 95% CI of mean(δ_b) contains 1 for all blocks),
  G3 (tail z not significant after BH-FDR, all (block,t) cells),
  G4 (KS verdict agrees with G1 after BH-FDR), AND C1 passes (null control
  makes no false flag), AND C2 passes (positive control IS flagged),
  AND C7 (independent implementation) agrees block-by-block.
- **INCONCLUSIVE**: any gate ambiguous OR any control fails while primary
  gates pass.
- **H1_SUPPORTED / INCONSISTENT**: G1 or G2 or G3 rejects AND the deviation
  survives C6 residue-class conditioning (≥2 disjoint ranges) AND C7
  agrees. Escalate only; no novelty claim.

## Controls / replication required

- C1 null control, C2 positive control, C3 seed ladder, C4 resolution
  variation, C5 method agreement, C6 residue conditioning (falsification
  robustness), C7 independent implementation (separate code path).
- All seeds from rng(label, seed) except the deterministic sieve.
