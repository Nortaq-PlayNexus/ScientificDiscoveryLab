# Independent EXP-0003 broadband audit artifacts

This directory is isolated from the historical experiment and contains no edits to
`03_INVESTIGATIONS/OPTICS/vortex_density` or the laboratory registry.

## Reproduction commands run

```text
python AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE/run_broadband_convergence.py --realizations 4 --skip-controls
python AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE/run_broadband_convergence.py --skip-main
```

The first command performs the nine-resolution, four-width, six-seed main sweep
(4 independent realizations per seed). The second performs the targeted controls.
A one-realization smoke test was also run before the final sweep; its log is retained.

## Primary artifacts

- `RESULTS/main_rows.csv`: one row per independent field realization.
- `RESULTS/main_summary.csv`: condition means, standard errors, and 99% bootstrap intervals.
- `RESULTS/main_summary.json`: machine-readable condition summary and elapsed time.
- `RESULTS/main_convergence.png`: ratio versus pixels per central wavelength.
- `RESULTS/detail_controls.*`: winding, contour, fractional-shift, and finite-difference controls.
- `RESULTS/interpolation_controls.*`: explicit Fourier band-limited interpolation at 2x and 4x.
- `RESULTS/lowpass_controls.*`: controlled spectral cutoffs and alias/truncation diagnostics.
- `RESULTS/non_square_controls.*`: rectangular and non-power-of-two grids.
- `RESULTS/fixed_field_controls.*`: one continuous master field sampled on nested grids.
- `RESULTS/construction_controls.*`: corrected real-component route versus direct complex-Fourier route.
- `RESULTS/large_window_validation*`: 128-wavelength finite-window sensitivity check (N=512 at P=4).
- `RESULTS/sanity_controls.json`: synthetic vortex, Hermitian-symmetry, normalization, and determinism checks.
- `RESULTS/condition_verdicts.*`, `RESULTS/control_summary.json`, and `RESULTS/convergence_table.md`: derived audit tables.
- `COMMANDS_AND_RUNTIME.md`: exact commands, runtimes, and known exploratory corrections.
- `COLLISION_NOTE.md`: records a separate pre-existing runner found in this folder; it was left untouched.
- `RUN_COMPLETE.json`: completion/verdict marker for integration.
- `RESULTS/run_manifest.json` and `RESULTS/run_summary.json`: environment/runtime metadata.
- `LITERATURE_SEARCH.md`: live Crossref/OpenAlex search record and novelty limitation.
- `REPORT/SUBAGENT_REPORT.md`: final concise audit report and verdict.
- `LOGS/`: stdout/stderr logs for the actual runs.

## Physical convention

The reference physical spectrum is
`S(k)=exp(-((|k|-pi/2)^2)/(2 sigma_k^2))` with
`sigma_k in {0.10,0.25,0.50,0.75}` in the same reference-pixel units as EXP-0003.
At pixels-per-wavelength `P`, pixel pitch is `dx=4/P`; the physical box is held
at 24 central wavelengths, so `N=24P`. Thus the physical `k0` and all physical
`sigma_k` values remain fixed while the pitch changes. At P=4 the dimensionless
spectrum is the EXP-0003 `k0=pi/2`, `sigma_k` spectrum on a 24-wavelength box.
The smaller box is an explicit finite-window control/limitation, not a silent
redefinition of the spectrum.
