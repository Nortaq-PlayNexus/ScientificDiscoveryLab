# QUESTION — Speckle contrast law

- QUESTION_ID: Q-O001
- FIELD: optics (statistical optics / simulation validation)

## Question

For simulated fully-developed laser speckle, does the contrast law

    C(M) = 1 / sqrt(M)

hold quantitatively, where M is the number of summed uncorrelated fully-developed
speckle intensity patterns, and at which M / resolution configurations does
residual (finite-grid, interpolation, sampling) correlation break it?

## Why this question matters

- It is the first-order statistical-optics textbook law (Goodman).
- It is the perfect FIRST experiment for this laboratory: cheap, deterministic, and
  it validates both (a) the shared engine's simulation/statistics pipeline and
  (b) our honesty about grid artifacts — before any bigger optics claim is attempted.
- The "breakdown regime" at finite grid size is a numerical-science measurement
  (scheme/resolution dependent), i.e., an honest target; we are NOT trying to
  "discover" anything exotic.

## What scientists already know

- Single fully-developed speckle, intensity is exponentially distributed; mean =
  1, variance = 1 for mean-normalised intensity (contrast C = 1).
- Sum of M independent fully-developed speckle intensities -> gamma distribution
  with contrast 1/sqrt(M) exactly (in the idealised continuous limit).
- Real detectors / finite grids introduce cross-correlation between pixels; this
  reduces the number of effective independent modes and bends C(M) upward.

## What remains unknown / what we test

- The quantitative agreement of a *specific*, fully specified computational recipe
  (grid, interpolation-free, count of independent realisations) with 1/sqrt(M)
  including Monte-Carlo confidence intervals.
- The resolution dependence of the small deviation (bias) at finite grid size:
  does the deviation shrink with grid size ("sampling artifact") or persist
  ("genuine finite-aperture effect")?

## Known methods

- Monte-Carlo: generate M independent complex Gaussian speckle fields (via random
  phase screens in the Fourier plane), sum intensities, compute ensemble/space
  contrast.
- Compare to analytic gamma-distribution prediction; bootstrap the estimator.

## Available data

None external required. All synthetic and reproducible with the lab RNG.

## Possible experiment

Summarised in EXPERIMENT_PLAN.md and CONTROLS.md. Compute C(M) for M ladder,
variance across independent realisations, and a resolution ladder; compare ratios
C(M)*sqrt(M) to 1 within Monte Carlo CI.

## Null hypothesis

C(M) = 1/sqrt(M) within Monte Carlo error for all tested M and resolutions
(definition: no systematic deviation beyond the finite-M estimator spread).

## Alternative hypothesis

C(M)*sqrt(M) deviates systematically from 1 in a way that does NOT vanish when
resolution rises (i.e., not pure sampling artifact).

## Falsification test

- Resolution ladder: deviation should shrink with N (grid side).
- Realisation ladder: C(sqrt)*M ratio vs number of spatial samples / realisations.
- Seed ladder: estimators stable across seeds.
- Independent implementation of the generator (step 6 REPLICATION) must reproduce
  the same numbers.

## Expected difficulty

Low (compute); this is primarily pipeline validation with a known answer.

## Likely computational cost

CPU-minutes (grids <= 256^2, M <= 16, seeds small).

## Known pitfalls

- Averaging over FEW independent speckle "cells" biases the contrast estimator low
  or high depending on estimator (mean of pixel-level intensity variances either
  uses spatial or ensemble statistics incorrectly).
- Treating sibling pixels as independent samples.
- Boundary/aliasing when the phase screen is undersampled.
- Reporting "deviation" without CI, thereby calling an estimator spread a signal.

## Relevant papers

- Goodman, "Statistical Optics" (1985/2015), ch. on speckle contrast.
- Goodman, "Speckle Phenomena in Optics" (2007).

## Why AI could help

- Runs a fully disciplined realisation/resolution sweep with bootstraped CIs and
  honest reporting; documents exactly which numerical detail controls the result.

## What would count as a real result

- Reproduction of C(M) = 1/sqrt(M) within stated tolerance + a quantified
  characterisation of the residual grid-size dependence with controls. That is a
  "real result" as a validated measurement and engine certification — NOT a claim
  of new physics.