# QUESTION — Phase-singularity (vortex) density in random wave fields

- QUESTION_ID: Q-O002
- FIELD: optics / statistical physics (random waves, singular optics)
- HYPOTHESIS_ID: HYP-002

## Question

For a zero-mean, statistically isotropic complex Gaussian random field E(x, y) with
power spectrum S(k), does the number density of phase singularities (optical
vortices) equal the Kac-Rice / Nye-Berry prediction

    n_pred = <|dE/dx|^2> / (2 * pi * <|E|^2>)

and, for the special case of an isotropic narrow-band field of wavenumber k0, the
textbook form n = k0^2 / (4*pi)?  Over which operating regimes (bandwidth, pixels
per wavelength) does a discrete-grid winding-number counter measure this quantity
faithfully, and when does it fail?

## Why this question matters

- This is the central quantitative law of singular optics (Nye & Berry 1974;
  Berry 1978, 2000) and of dislocation lines in random wave fields.
- It is the direct continuation of the lab's predecessor project
  (`coherent-optical-ai-sandbox`), whose audit found its winding-count detector was
  **grid-locked**: the count jumped (48 -> 218) under a one-third-pixel shift. This
  investigation rebuilds the measurement with that lesson built in, and tests the
  detector for shift-invariance explicitly.
- It delivers a reusable, certified vortex-density estimator for later optics work
  (e.g. propagation and turbulence studies) before any such experiment is attempted.

## What scientists already know

- A phase singularity is a point where |E| = 0 with a definite integer winding
  (+/-1 in generic random fields); singularities are created and annihilated in
  charge-neutral pairs.
- Kac-Rice theory gives the density of zeros of a 2-D random field; for an isotropic
  complex Gaussian field the phase-singularity density is
  n = <|dE/dx|^2> / (2*pi*<|E|^2>) (derivation in EXPERIMENT_PLAN.md Appendix A).
- For an isotropic narrow-band ("random wave") field of wavenumber k0 this reduces to
  n = k0^2 / (4*pi).
- Nye & Berry (1974) and Berry (1978, 1981, 2000) establish the scaling and the
  statistics of dislocation densities; Freund (1998) studied the dynamics.

## What remains unknown / what we test

- Whether a *specific, fully specified* discrete measurement recipe reproduces the
  prediction within Monte-Carlo confidence intervals, at finite grid.
- The exact safe operating regime of a discrete winding-number counter: how the
  measured/predicted ratio depends on pixels-per-wavelength and on the high-k
  (near-Nyquist) tail of the spectrum.
- Whether this lab's re-implemented counter is free of the grid-locking seen in the
  sandbox (a half-pixel shift test), or whether it inherits the same flaw.

## Known methods

- Winding-number counting on lattice plaquettes (sum of wrapped phase increments).
- Contour-intersection counting (Re E = 0 and Im E = 0 zero-contour crossing).
- Analytic Kac-Rice prediction from the spectrum.

## Available data

None external. All fields are synthetic and reproducible with the lab RNG.

## Possible experiment

In EXPERIMENT_PLAN.md and CONTROLS.md: generate isotropic Gaussian fields with
controlled spectra (narrow ring, and broad Gaussian), count vortices in an interior
ROI with two independent detectors, compare to n_pred, and run bandwidth /
resolution / shift / seed / surrogate / independent-implementation controls.

## Null hypothesis (H0)

The measured density equals n_pred within the pre-registered tolerance (3%) for
well-resolved fields; any residual is finite-grid sampling that disappears as
pixels-per-wavelength increases.

## Alternative hypothesis (H1-dev)

A systematic mismatch that does NOT vanish as pixels-per-wavelength increases, i.e.
not explainable as a resolution artifact (would require the kill-the-hypothesis
battery and independent re-derivation before any interpretation).

## Falsification test

- Bandwidth ladder: the deficit must track the near-Nyquist tail, not the ROI size.
- Pixels-per-wavelength ladder: ratio -> 1 as wavelength grows.
- Shift-invariance test: density must not jump under a half-pixel translation
  (this is the falsifier that caught the sandbox detector).
- Independent implementation: an explicit plane-wave superposition with an
  independently written detector must reproduce the density.

## Expected difficulty

Low-moderate. The law is known; the work is in controlled, artifact-aware execution.

## Likely computational cost

CPU-minutes. Grids <= 1024^2, tens of realisations, a handful of spectra.

## Known pitfalls

- Grid-locked winding counters (predecessor-project precedent).
- Boundary vortices: count only an interior ROI with a margin.
- Interpolation / phase unwrapping creating spurious sign flips.
- Under-counting when power sits near the Nyquist frequency (unresolved high-k).
- Reporting a deficit without stating the pixels-per-wavelength regime.

## Relevant papers

- Nye & Berry (1974), "Dislocations in wave trains", Proc. R. Soc. A 336, 165.
- Berry (1978), "Dislocations in wave trains and the propagation of dislocations".
- Berry (2000/2001), "Phase singularities in isotropic random waves".
- Freund (1998), optical vortex dynamics in speckle.

## Why an AI lab could help

- It can run a fully specified, preregistered sweep with two detectors, bootstrap
  CIs, BH-FDR, and explicit artifact ladders - and it documents exactly which
  numerical detail controls the answer.

## What would count as a real result

- A certified vortex-density estimator that reproduces n_pred within tolerance in a
  stated operating regime, with an honestly quantified failure zone near Nyquist,
  charge neutrality verified, and shift-invariance demonstrated. This is a
  controlled reproduction and instrument certification - NOT a claim of new physics.
