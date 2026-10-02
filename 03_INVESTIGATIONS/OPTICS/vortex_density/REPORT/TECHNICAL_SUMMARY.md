# TECHNICAL SUMMARY — EXP-0003 (Q-O002 / HYP-002)

Status: **complete** | Decision: **H0_SUPPORTED** | Evidence state: **CONTROLLED**
(this is a reproduction of a known law plus instrument certification, not new science).

## Claim tested

For an isotropic, zero-mean complex Gaussian field E with power spectrum S(k), the
phase-singularity (vortex) number density is

    n_pred = <|dE/dx|^2> / (2*pi*<|E|^2>) = sum_k kx^2 S_k / (2*pi * sum_k S_k),

which for a narrow-band isotropic field of wavenumber k0 reduces to k0^2/(4*pi)
(Nye & Berry 1974; Berry 1978, 2000; Kac-Rice). Prediction `n_pred` was computed from
the exact discrete spectrum of each generated field.

## Method

- Fields: complex Gaussian E = u + i v, u, v independent real fields with the target
  spectrum, generated in the DFT plane with correct (-k mod N) Hermitian pairing.
- Spectra: narrow ring (half-width 0.20 rad/px) at k0 in {pi/32, pi/16, pi/8, pi/4,
  pi/2}; and Gaussian at centre pi/2 with sigma_k in {0.10, 0.25, 0.50, 0.75}.
- Grids N in {256, 512, 1024}; 40 realisations/cell; interior ROI margin 24 px
  (N<=512), 48 px (N=1024); alpha=0.01; BH-FDR across all cells.
- Detector D1: plaquette winding number (principal phase increments, no unwrapping).
- Detector D2: certified zero-contour intersection (Re E = 0 and Im E = 0 segments
  crossing inside a cell), written independently of D1.

## Results

### Primary (narrow band, N=1024, prediction tolerance +/-3%)

| k0 (rad/px) | P = 2pi/k0 (px) | n_meas/n_pred | 99% CI |
|---|---|---|---|
| pi/32 = 0.0982 | 64 | 0.9978 | [0.9931, 1.0026] |
| pi/16 = 0.1963 | 32 | 0.9952 | [0.9901, 1.0001] |
| pi/8  = 0.3927 | 16 | 0.9958 | [0.9932, 0.9984] |
| pi/4  = 0.7854 | 8  | 1.0011 | [1.0000, 1.0024] |

All four primary cells are inside the +/-3% point tolerance with 99% CIs inside
+/-5%. k0 = pi/2 (P = 4) measured 1.0137 (within +/-3%, but excluded from the
primary set a priori because it is the worst-resolved).

### Controls

- C1 analytic vs finite-difference: the spectral predictor and the FD field predictor
  agree in the well-resolved regime; FD underestimates at k0 = pi/2 (discretisation),
  as expected. Recorded per cell.
- C2 detector agreement: D2/D1 within 1% for every narrow-band cell (max deviation
  0.6%). Brokerage note: an initial naive D2 (cell has two crossings of each
  contour) overcounted by ~2.5x because it did not check intersection; it was
  replaced (see CONFIG/changelog.jsonl) and is retained as a documented negative.
- C3 charge neutrality: |n+ - n-|/n <= 0.0024 for all cells.
- C4 shift invariance (grid-lock falsifier): half-pixel shift changed the count by
  <= 2.1% (most cells < 0.7%); no jump. This is the direct answer to the predecessor
  project's grid-locked counter.
- C5 amplitude scaling: rel. delta = 0.0 (counts identical under E -> 3.7 E).
- C6 independent implementation: explicit plane-wave sum + independently written
  loop-based contour detector gives 0.992 +/- 0.033, 0.999 +/- 0.018, 0.985 +/- 0.019
  at k0 = pi/8, pi/4, pi/2 (within 5%). Charge imbalance < 1.4%.
- C7 pixels-per-wavelength ladder: ratio -> 1 with no residual trend for P >= 8.
- C8 bandwidth ladder: see below.
- C9 seed ladder (k0=pi/4, N=512): ratios 0.9987-1.0022 across the lab seed ladder.
- C10 BH-FDR: several cells are statistically distinguishable from exactly 1 at
  alpha=0.01 (e.g. k0=pi/8 N=1024). This is expected: a ~0.4% finite-grid bias with
  a tight CI is significant but well inside the pre-registered 3% practical
  tolerance. Statistical significance is NOT practical significance here.

### Failure zone (C8, Gaussian sigma_k ladder at N=512, k0=pi/2)

| sigma_k | winding D1 | contour D2 |
|---|---|---|
| 0.10 | 1.0160 | 0.9855 |
| 0.25 | 0.9898 | 0.9543 |
| 0.50 | 0.9130 | 0.8615 |
| 0.75 | 0.8287 | 0.7558 |

The deficit grows monotonically as continuum power approaches the Nyquist shell.
Both independent detectors show it, and it is a detector/grid resolution limit
(unresolved high-k structure), not a physics effect. The narrow-band cells with
P >= 8 show no such deficit.

### Documented estimator trap

For the independent plane-wave construction, whose wavevectors are off the DFT grid,
the FFT-moment predictor of <|dE/dx|^2> is biased by spectral leakage (ratio ~0.89 at
k0=pi/8). Using the correct mode-weighted prediction removes the bias. This is
recorded because it is a plausible way a future analysis could manufacture a fake
deficit.

## What this does NOT show

- No new physics: n_pred = Kac-Rice/Nye-Berry is established.
- No claim of novelty; no literature search was performed programmatically (see
  LITERATURE.md).
- The broadband deficit is characterised, not explained from first principles.
- Only isotropic spectra were tested (the derivation requires isotropy).

## Reproduction

    python CODE/run_vortex_density.py
    python REPLICATION/independent_check.py
    python CODE/make_figure.py

Outputs: RESULTS/EXP-0003_results.json, CONFIG/prereg_EXP-0003.json,
CONFIG/EXP-0003_experiment.json, CONFIG/registry.jsonl, CONFIG/changelog.jsonl,
REPLICATION/independent_check.json, FIGURES/EXP-0003_vortex_density.png.
