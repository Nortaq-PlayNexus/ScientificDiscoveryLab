# CONTROLS — EXP-0015 (water acoustic response simulator)

Every cell runs these controls; any surprise triggers the kill-the-hypothesis
battery. Numbering is per-experiment (as in EXP-0003 / EXP-0007).

| # | Control | Implementation | Rule |
|---|---|---|---|
| C1 | Null / no-drive | S4: p0 = 0; S2: drive amplitude 0; S6: Gamma = 0 with released mode | response stays at numerical noise (< 1e-9 of a wavelength-scale quantity); a null that "responds" invalidates the module |
| C2 | Positive control | S1: seawater S=35, T=0, P=0 must be reproduced by BOTH formulas; S2: driving exactly at a predicted f_n must produce a large, phase-locked response | method must detect a known effect before we trust a null |
| C3 | Seed variation | S4 initial-position sets and S6 initial perturbations drawn from SEED_LADDER = (42, 7, 123, 2023, 314159, 271828) via `engine.utilities.core.rng` | spread of t_90 < 25 % relative sd; S6 selection independent of seed |
| C4 | Resolution ladder | S2: ppw {20, 40, 80}; S3: ppw {10, 20, 40, 80}; S6: Nz {6, 12, 24, 48} | residual must fall monotonically and ~ as (step)^2; a residual that plateaus = defect, not physics |
| C5 | Method variation | S1: UNESCO vs Mackenzie (independent fits); S2: frequency-domain Helmholtz vs time-domain finite-difference propagation; S5: Rayleigh-Plesset vs linearised oscillator near resonance; S6: discrete vertical Laplace solve vs analytic tanh(kh) | two independent routes must agree inside the module tolerance |
| C6 | Boundary variation | S2: rigid-rigid vs rigid-free end; repeat at L = 0.25 m and 0.50 m | ladder must move to the *predicted* series and scale exactly as 1/L, not merely shift |
| C7 | Linearity | S2: response amplitude vs drive amplitude (small-signal range); S4: v vs p0 (expect v ~ p0^2); S5: (R_max - R0) vs p_a below 0.2 P0 | log-log slope must equal the predicted power (1, 2, 1) within 0.05 |
| C8 | Shift / grid-lock falsifier | S4: translate all initial positions by lambda/4 (half the node spacing) and re-run | final node set must be identical to < 1e-6 lambda (inherited from the predecessor optical project's grid-locking failure) |
| C9 | Matched contrast-sign control | S4: same physics with phi -> -phi (and an air-bubble-like phi << 0) | particles must move to the *opposite* extrema; identical outcome = broken solver |
| C10 | Damping-independence | S6: repeat the threshold measurement at two damping levels (nu and 2 nu) | Gamma_c must scale ~ linearly with mu and must track 4 mu/omega_0 at both levels |
| C11 | FDR | Benjamini-Hochberg at alpha = 0.01 across every preregistered cell/gate p-value | controls the family-wise false-discovery rate across modules |
| C12 | Independent implementation | `REPLICATION/independent_check.py`, written from the equations by a different route (no imports from `CODE/`) | must reproduce S1b, S2a, S3a, S4a, S5a and S6a inside their module tolerances |

## Definitive-falsifier battery (only if a deviation survives C1-C11)

- **Is it a boundary artefact?** Vary the ROI / probe position and the wall
  condition; require the peak or node set to move exactly as the analytic
  boundary condition dictates.
- **Is it a discretisation artefact?** Refine dx, dt, df, Nz by 2x twice more
  than the preregistered ladder; require the residual to keep falling ~4x per
  halving. If it stops falling, the defect is in the model, not the grid.
- **Is it an aliasing artefact?** Re-run at a lower frequency with identical
  points-per-wavelength; an artefact follows the grid, a feature follows physics.
- **Is it a damping-model artefact (S6)?** Double mu; the threshold must follow
  4 mu/omega_0. If it does not, the tongues are being produced by something
  other than parametric resonance.
- **Is it a circularity artefact (S1/S3/S6)?** Replace the reference formula with
  the independent one (Mackenzie / classical absorption / analytic tanh) and
  re-evaluate. If the "agreement" only exists against the formula the code
  implements, the test was circular.
- **Is it a peak-picking artefact (S2)?** Halve df near each peak and re-locate;
  the located frequency must not move by more than 1 %.

Per RESEARCH_RULES section 5: any deviation surviving all of the above is
reported as a controlled deviation or a documented model limitation. It is
**never** interpreted as new physics.
