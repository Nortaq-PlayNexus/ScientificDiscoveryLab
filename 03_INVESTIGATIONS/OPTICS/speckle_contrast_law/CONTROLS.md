# CONTROLS — Speckle contrast law

Every (M, N) cell runs these controls; any surprise gets the full kill-the-
hypothesis battery.

| # | Control | Implementation | Rule |
|---|---|---|---|
| C1 | Positive control | M = 1 single speckle: C ~ 1.0 (known exponential) | must hold |
| C2 | MC/realisation spread | 32 realisations; bootstrap CI on C | 99% band reported |
| C3 | Seed ladder | re-estimate C at SEED_LADDER seeds | estimator stable |
| C4 | Resolution ladder | N = 32,64,128,256 at fixed M | deviation must shrink ~1/N if sampling |
| C5 | Generator check | exponential single-speckle marginal histogram vs Exponential(λ=k) KS test | pass required |
| C6 | Independent implementation | REPLICATION/ code regenerates intensities by a different route (direct complex Gaussian) | must reproduce |
| C7 | Ensemble-vs-space estimator | compare ensemble contrast (across realisations at one pixel) vs spatial | agree within CI |
| C8 | FDR | BH-FDR (alpha 0.01) across all grid cells | controls multiple testing |

## Kill-the-hypothesis (only if a deviation survives C1..C7)

- Is the deviation a boundary effect? (measure interior-only ROI)
- Is it a phase-screen undersampling effect? (more phase cells vs grid)
- Is it interpolation? (this code uses none — states FFT)
- Is it FFT normalisation? (take two equivalent normalisations)
- Is it real finite-aperture statistics? (then it should reproduce at 2 independent
  implementations AND match an analytic second-moment calculation)