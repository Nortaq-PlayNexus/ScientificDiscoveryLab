# EXPERIMENT_PLAN — EXP-0003 (Q-O002 / HYP-002)

Preregistered protocol. Frozen before execution; any later change is appended to
CONFIG/changelog.jsonl via engine.hypothesis_testing.prereg.log_change.

## Physics model

A statistically isotropic, zero-mean complex Gaussian random field
E(x, y) = u(x, y) + i v(x, y), where u, v are independent real Gaussian fields with
the same isotropic power spectrum S(k). A phase singularity (vortex) sits where
E = 0; its charge is the winding of arg(E) around that point (+/-1 generically).

## Analytic prediction (Appendix A)

For an isotropic complex Gaussian field,

    n_pred = <|dE/dx|^2> / (2 * pi * <|E|^2>) = sum_k (kx^2 S_k) / (2*pi * sum_k S_k)

and for an isotropic narrow-band field of wavenumber k0 this is n = k0^2/(4*pi).
For the discrete implementation, n_pred uses the exact discrete spectrum (the
right-hand form), because the narrow-band sum over the discrete shell is not exactly
k0^2/2.

## Implementation (CODE/run_vortex_density.py)

- Field generation: in the DFT plane fill independent complex Gaussian amplitudes
  with variance S(k)/2, then enforce Hermitian symmetry with the correct
  (-k mod N) partner indexing, then inverse FFT to get each real component u, v.
  (Rationale: the predecessor project's surrogate code had a Hermitian-pairing bug;
  this construction is written correctly and unit-checked, see C1.)
- Spectrum families:
  - narrow ring: S = 1 where | (|k| - k0) | < 0.20 rad/px, else 0.
  - broadband Gaussian: S = exp( -(|k| - k0)^2 / (2 sigma_k^2) ).
- Detectors:
  - D1 winding number: for each unit plaquette, circ = ex + ey_top - ex - ey_bottom
    using principal phase increments, w = round(circ / 2*pi); count |w| != 0.
  - D2 contour intersection: locate the Re E = 0 and Im E = 0 zero-contour
    crossings on cell edges by linear interpolation; count cells whose two contour
    segments intersect (a zero of E).
- ROI: count only cells whose corners lie inside a margin-interior region.
- n_meas: interior count / interior area (area in pixel^2; k in rad/pixel).
- Bootstrap: resample realisations (block = one realisation) to get a 99% CI on the
  mean density.
- Predicted ratio rho = n_meas / n_pred; recorded with its 99% CI.
- BH-FDR across all cells (alpha 0.01).

## Steps

1. Freeze preregistration to CONFIG/prereg_EXP-0003.json.
2. Narrow-band k0 ladder at N in {256, 512, 1024}; 40 realisations per cell.
3. Broadband Gaussian sigma_k ladder at N=512.
4. Controls C1-C10 (including the half-pixel shift test, amplitude scaling, seed
   ladder, charge neutrality).
5. Decision per the frozen rule; write RESULTS/EXP-0003_results.json and
   CONFIG/EXP-0003_experiment.json; append a registry row.
6. REPLICATION/independent_check.py: explicit plane-wave superposition + independent
   detector; compare.
7. REPORT/TECHNICAL_SUMMARY.md and REPORT/PLAIN_ENGLISH_SUMMARY.md.

## Decision rules (frozen)

- **H0 supported** iff, for every narrow-band cell with k0 <= pi/4 (P >= 8) at
  N=1024: ratio point estimate in [0.97, 1.03] AND its 99% CI within [0.95, 1.05];
  AND charge neutrality holds (C3) for all cells; AND shift invariance holds (C4)
  for all narrow-band cells; AND C6 reproduces within 5%.
- **S1-S3 characterised** (secondary): report sign balance, shift deltas, and the
  bandwidth-ladder deficit; these are characterisation, not discovery.
- **H1-dev flagged** iff a narrow-band well-resolved cell fails H0 by more than
  tolerance AND the failure does not diminish as pixels-per-wavelength grows. If
  flagged: run the kill-the-hypothesis battery; claim nothing beyond "controlled
  deviation".

## Evidence-state intent

If H0 holds: evidence state CONTROLLED (a reproduced, well-known law). Literature
cross-check and independent implementation remain to be completed for REPLICATED /
INDEPENDENTLY REPRODUCED.

## Appendix A — derivation of n_pred (Kac-Rice)

Let E = u + iv with u, v independent stationary isotropic zero-mean Gaussian fields,
variance sigma^2 = <u^2> = <v^2> = <|E|^2>/2. A vortex is a simultaneous zero of u
and v. Kac-Rice for the 2-D field (x, y) -> (u, v):

    n = E[ |det J| * delta(u) * delta(v) ],   J = d(u, v)/d(x, y).

Values and derivatives of a stationary Gaussian field are uncorrelated, so the
delta-factors decouple: delta-terms contribute p_u(0) p_v(0) = 1/(2*pi*sigma^2).
Isotropy makes the four entries of J i.i.d. N(0, mu) with mu = <u_x^2> = <v_x^2>;
then E|det J| = mu (Ginibre-style 2x2 identity; verified numerically during
planning). Hence

    n = mu / (2*pi*sigma^2) = mu / (pi*<|E|^2>)
      = <|dE/dx|^2> / (2*pi*<|E|^2>),      since <|dE/dx|^2> = 2*mu.

In the DFT the x-derivative multiplies each mode by i*kx, giving
sum_k kx^2 S_k / (2*pi*sum_k S_k). For isotropic narrow band, <kx^2> = k0^2/2, so
n = k0^2/(4*pi). Remark: isotropy is required for E|det J| = mu; anisotropic
spectra are outside the registered scope.
