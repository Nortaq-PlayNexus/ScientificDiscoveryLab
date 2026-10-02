# PREDICTIONS — EXP-0003 (frozen before execution)

## Quantitative predictions

1. (Primary, H0) For every narrow-band ring cell with pixels-per-wavelength
   P = 2*pi/k0 >= 8 (i.e. k0 <= pi/4) at N=1024:
   the 99% bootstrap CI of the ratio n_meas / n_pred lies inside [0.95, 1.05], and
   the point ratio lies inside [0.97, 1.03].
   Prediction: n_pred is computed from the *exact discrete spectrum* of the field as
   n_pred = sum(kx^2 S) / sum(S) / (2*pi).

2. (Special case) For the narrow-band ring cells, n_pred is within 3% of the
   textbook k0^2/(4*pi) for P >= 8.

3. (Charge neutrality, S1) For every cell, |n_plus - n_minus| / n_meas < 0.02.

4. (No grid locking, S2) For every narrow-band ring cell, the half-pixel-shifted
   count differs from the unshifted count by less than 3%.

5. (Failure zone, S3) As the Gaussian bandwidth sigma_k grows at fixed k0=pi/2,
   the ratio n_meas/n_pred decreases monotonically once power reaches the Nyquist
   shell. Across the pixels-per-wavelength ladder at fixed narrow bandwidth, the
   ratio approaches 1 from above/below as P grows (no residual trend at large P).

6. (Independent implementation, C6) An explicit plane-wave superposition
   (REPLICATION/independent_check.py), with an independently written detector,
   reproduces n_meas/n_pred within 5% for the narrow-band cells.

## Test grid (pre-registered)

- Grid sizes N: 256, 512, 1024 (primary N = 1024)
- Narrow-ring wavenumbers k0 (rad/pixel): pi/32, pi/16, pi/8, pi/4, pi/2
  (pixels-per-wavelength P = 64, 32, 16, 8, 4)
- Ring thinness (spectral half-width): 0.20 rad/px (fixed)
- Broadband probe: Gaussian spectrum centre k0 = pi/2, widths
  sigma_k in {0.10, 0.25, 0.50, 0.75} rad/px
- Independent realisations per cell: 40
- Bootstrap resamples: 2000
- Interior ROI margin: 24 px (N<=512), 48 px (N=1024)
- Primary seed 42; SEED_LADDER for the seed control
- alpha = 0.01; BH-FDR across all preregistered cells

## Registered outputs to record

- n_meas (both detectors), signed counts, n_pred (spectral and, for narrow band,
  k0^2/(4*pi)), ratio + 99% bootstrap CI, per cell.
- Shift-test delta, amplitude-scaling delta, seed-ladder spread.
- BH-FDR flags across cells.
- Decision label (H0 supported / H1-dev flagged) per the frozen rule in
  EXPERIMENT_PLAN.md.

## Notes on planning checks (disclosed)

While preparing this experiment, throwaway scripts (kept out of the lab; see
FALSIFICATION/planning_checks.md) measured ratios ~1.01 for narrow-band fields and
~0.91-0.94 for broad Gaussian fields at k0=pi/2. These *informed the design of the
failure-zone prediction* (S3) and are disclosed here to avoid any appearance of
post-hoc tuning. The registered test remains a genuine measurement of the
pre-specified quantities.
