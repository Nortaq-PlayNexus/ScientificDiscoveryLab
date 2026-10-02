# CONTROLS — EXP-0003 (vortex density)

Every cell runs these controls; any surprise triggers the kill-the-hypothesis battery.

| # | Control | Implementation | Rule |
|---|---|---|---|
| C1 | Analytic consistency | n_pred from the exact discrete spectrum vs from finite-difference moments of the generated field | must agree in the narrow-band, well-resolved regime |
| C2 | Detector agreement | winding-number (D1) vs contour-intersection (D2) | agree within 10% for narrow band; divergence documented for broad band |
| C3 | Charge neutrality | count signed (+/-) vortices separately | \|n+ - n-\|/n < 2% |
| C4 | Shift invariance | translate field 0.5 px in x and y via a Fourier phase ramp; recount | change < 3% (grid-lock falsifier) |
| C5 | Amplitude scaling | multiply E by a constant; recount | identical count (estimator scale-free) |
| C6 | Independent implementation | REPLICATION: explicit plane-wave sum + independent detector | reproduce within 5% (narrow band) |
| C7 | Resolution ladder | k0 ladder at N=1024 and N in {256,512,1024} at fixed k0 | ratio -> 1 as pixels-per-wavelength grows |
| C8 | Bandwidth ladder | Gaussian sigma_k ladder at fixed k0 | deficit grows with near-Nyquist power (failure zone) |
| C9 | Seed ladder | re-estimate at SEED_LADDER seeds | spread consistent with Monte-Carlo error |
| C10 | FDR | BH-FDR (alpha 0.01) across all preregistered cells | controls multiple testing |

## Definitive-falsifier (only if a deviation survives C1-C9)

- Is it a boundary effect? -> vary ROI margin; require invariance.
- Is it a phase-unwrapping artifact? -> recount with an unwrap-free method (D1 uses
  only principal phase increments, so it cannot wrap-accumulate).
- Is it aliasing of the high-k tail? -> re-test at reduced k0 with identical
  bandwidth fractions.
- Is it the estimator or the field? -> regenerate with an independent construction
  (C6) AND an analytic second-moment calculation.
- Persisting mismatch -> label H1-dev, do NOT interpret; escalate (report only).
