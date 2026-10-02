# NEXT EXPERIMENTS — Independent Audit Recommendations

**Purpose:** convert unresolved or invalid historical claims into preregistered, falsifiable experiments. These are recommendations, not completed results.

## Priority 0 — repair before any new claim

### N-001 — Correct Q-P007 cluster-size storage and remeasure tau

**Question:** Does a correctly stored finite-size cluster tail reproduce the 2D Fisher exponent, and does the refined `p_c` matter?

**Design:**

- Implement a new audit branch with one realization per RNG cell and explicit `sizes_per_realization` storage.
- Run L={256,512,1024}, at least n={100,100,50} independent realizations at canonical and refined p_c, with paired random masks.
- Remove the largest cluster per realization before pooling; preserve the complete tail histogram and raw cluster arrays.
- Fit cumulative and histogram tau on preregistered windows, with block/realization bootstrap rather than iid-cluster bootstrap.
- Report power analysis and resolution needed to distinguish 1.98 from 2.054945.

**Falsification:** if the corrected tail remains below the preregistered window with realization-level uncertainty, reject the claim that a small p_c refinement resolves the discrepancy. If the cache cannot round-trip, stop and classify infrastructure failure.

### N-002 — Finalize EXP-0003 broadband resolution audit

**Question:** Is the broad-band deficit explained by finite spectral support/aliasing, finite-difference error, or vortex detection?

**Design:**

- Use the fixed physical convention documented in `SUBAGENT_EXP0003_BROADBAND_20260924/README.md`.
- P={4,6,8,12,16,24,32,48,64}; sigma={0.10,0.25,0.50,0.75}; at least 6 independent seeds and enough realizations for 99% intervals.
- Compare continuous Kac–Rice, exact discrete-mode, Nyquist-truncated, and explicitly low-pass predictions.
- Use corrected Fourier refinement, direct complex FFT, winding and contour detectors, fractional shifts, and rectangular grids.
- Place a known sub-cell vortex for detector sanity; test Hermitian self-conjugate variance.
- Predeclare the primary statistic as ratio versus P and the primary artifact contrast as broad versus narrow sigma.

**Falsification:** no claim of a physical resolution transition if the ratio trend disappears under direct complex/fixed-field controls or if a detector-only correction explains it.

### N-003 — Repair Feigenbaum higher-order computation

**Question:** What are the period-verified z=3 and z=4 superstable sequences and delta limits?

**Design:**

- Freeze a valid JSON preregistration and independent implementation.
- Use 80–100 digit arithmetic, continuation from each verified root, first sign-changing root to the right, and explicit first-return checks.
- Compute at least n=2…10; report sequence monotonicity, delta_n, and a correctly defined alpha only if its estimator is specified.
- Compare z=2 with the published Feigenbaum value and z=3/z=4 with Hu & Mao’s actual paper/metadata.

**Falsification:** any nonmonotone sequence, inherited-period root, or alpha estimate based on an undefined scaling variable invalidates the corresponding claim.

## Priority 1 — strengthen evidence

### N-004 — Dependence-aware RNG calibration

**Current repair status:** bounded read-only replay/plumbing smoke is
implemented in
`03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_RNG_CALIBRATION/`.
It does not certify a generator or replace the historical EXP-0004 result.

**Question:** Which individual battery tests are calibrated for each generator, independent of the pooled decision?

**Design:**

- Pre-register per-test alpha and family-wise correction across independent seeds.
- Use at least 200 fresh seeds per generator, stream lengths spanning 2^18 and 2^22 bits.
- Fit a dependence model or use permutation/max-T controls that respect shared input streams.
- Compare against an official NIST implementation or a second independently coded implementation; do not call a generator certified.

**Falsification:** if control generators fail marginal tests, invalidate the battery before interpreting G_LAB.

### N-005 — Balanced 2D percolation lattice-size test

**Question:** Is there any reproducible power-of-two effect after matching physical size, parity, estimator, and random-stream policy?

**Design:**

- Pre-register a balanced design with power-of-two and non-power-of-two sizes at matched linear dimensions and matched physical area.
- Use independent PCG64 and a second union-find implementation.
- Fit D_f with block bootstrap and report the power/non-power contrast as the primary statistic.
- Include exact `p_c=0.59274605079210` and a separately estimated threshold with propagated uncertainty.

**Falsification:** if the contrast is below a preregistered equivalence margin, classify “lattice artifact” as unsupported; do not select the sequence closest to theory after seeing results.

### N-006 — Production 3D percolation run

**Question:** Does the shared engine reproduce standard 3D percolation exponents at production scale?

**Design:**

- Add a fail-closed configuration guard so `--pilot` cannot select EXP-0013 main settings.
- Pilot L={16,24,32}, then production L={64,96,128} with resource and stopping rules fixed in advance.
- Measure width threshold, cluster mass, susceptibility, and order parameter independently; do not use an algebraically identical mass identity as an independent scaling check.
- Use a second implementation for C7 and preserve all raw cluster-size data.

**Falsification:** incomplete runs, tiny-L extrapolations, or failed raw-data round trips are inconclusive, not abnormal physics.

## Priority 2 — descriptive/statistical follow-ups

### N-007 — Prime-gap finite-range null calibration

- Simulate the exact discrete prime-gap support and residue constraints over the same ranges.
- Use block bootstrap and finite-range dependence; compare asymptotic Gallagher/PNT predictions only at ranges where the approximation is defensible.
- Report power to detect a specified effect size and condition on admissible small gaps.
- Do not call a deviation “novel” without a mechanistic model or external comparison.

### N-008 — Complete Collatz family study

- Define the map and convergence/cycle criteria mathematically before running.
- Add explicit repeated-state detection and distinguish timeouts from cycles.
- Run all preregistered `(a,b,c)` families or label the study a bounded pilot.
- Test scale robustness and publish raw trajectories, not only aggregate counts.

### N-009 — Empirical S9 study

- Obtain raw image/dose data with provenance and consent/privacy documentation.
- Separate detector calibration from biological/perceptual claims.
- Generate Q-S9-1/3 summaries from raw files; fit Q-S9-2 only to measured observations.
- Keep the current hardcoded/synthetic outputs as historical artifacts, not evidence.

## Cross-cutting acceptance gates

1. Raw input/output hashes and environment recorded before analysis.
2. Immutable experiment ID and no identifier collision.
3. Independent implementation or analytic control for every primary claim.
4. Negative controls, known positive controls, and a detector sanity test.
5. Preregistered uncertainty model that preserves dependence.
6. A result is marked `INCONCLUSIVE` if any required raw-data or cache round-trip gate fails.
7. Literature/novelty search is recorded separately from scientific reproduction.
