# Q-M008 Plan — Prime Gap Scaling Test (10^9/10^10)

## Status: PLANNED (2026-09-23)

## Background
EXP-0008 tested prime gap distribution vs Poisson/Gallagher at site p_c to 10^8 (4 blocks). Primary gates G1 (χ²) and G3 (tail z) FAIL after BH-FDR at α=0.01 across all 4 blocks. Deviation survives residue conditioning in 4/4 ranges. C7 perfect match confirms pipeline integrity. Q-M007 characterized the shape: narrower than Exp(1), both tails lighter, mid-bins over-represented. BH-FDR on 40-cell grid: 38/40 significant.

## Question
Does the prime gap deviation persist at 10^9 and 10^10, or is it a finite-range artifact?

## Hypothesis
Deviation persists (the prime gap distribution has a reproducible deviation from Poisson at all ranges).

## Computational Requirements
- Sieve to 10^9: ~10× EXP-0008 cost
- Sieve to 10^10: ~100× EXP-0008 cost
- Estimated: hours to days for full sweep
- Memory: ~1GB for 10^9 bit sieve, ~10GB for 10^10

## Required Steps
1. Write `CODE/run_exp0012.py` — sieve to 10^9 and 10^10 with same block structure as EXP-0008
2. Compute chi2, tail z, and residue conditioning at each scale
3. Apply BH-FDR correction
4. Compare effect sizes across scales (10^8 → 10^9 → 10^10)
5. Apply Q-M007 shape analysis (10 bins × 4 blocks) at each scale

## Block Structure (must match EXP-0008)
- 4 blocks of size B (EXP-0008 used block-based structure per CONFIG/EXP-0008_experiment.json)
- Same chi2 computation methodology
- Same tail z computation methodology

## Decision Rule
- H0_SUPPORTED: deviation persists at both 10^9 and 10^10 with effect size comparable to 10^8
- ABNORMAL: deviation persists but effect size changes significantly
- INCONCLUSIVE: deviation disappears at either scale

## Resources Needed
- CPU hours: moderate to high
- RAM: 4–16 GB depending on sieve approach
- No GPU needed

## Open Questions
- Should 10^10 be attempted in a single run or broken into segments?
- Can the EXP-0008 `run_prime_gaps.py` be extended or do we need a new runner?
- Should we check EXP-0008 RESULTS for existing partial results at higher N?

## Relation to D1 (Q-M007 Finding)
- If deviation persists at 10^9/10^10: D1 shape characterization is an asymptotic property, not finite-range artifact
- If deviation disappears: D1 is a finite-range phenomenon, less theoretically interesting
- Either way: D1's shape analysis is valid for the range tested
