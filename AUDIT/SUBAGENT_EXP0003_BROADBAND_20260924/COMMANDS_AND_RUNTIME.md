# Exact execution record

All commands were run from `C:\Users\natha\ScientificDiscoveryLab` on Windows with Python 3.14.7, NumPy 2.5.3, SciPy 1.18.1, and Matplotlib 3.11.2.  The independent route is self-contained and did not import the historical EXP-0003 code or shared RNG.

## Final main sweep

```powershell
python "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\CODE\run_broadband_convergence.py" --realizations 4 --skip-controls 2>&1 | Tee-Object -FilePath "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\LOGS\full_main_corrected.log"
```

- 9 P values × 4 sigma values × 6 seeds × 4 realizations = **864 fields**.
- Main sweep elapsed time recorded in `RESULTS/main_summary.json`: **206.067 s**.
- P values: 4, 6, 8, 12, 16, 24, 32, 48, 64.
- Seeds: 42, 7, 123, 2023, 314159, 271828.
- Each field uses a distinct NumPy PCG64/SeedSequence stream.

## Targeted controls

```powershell
python "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\CODE\run_broadband_convergence.py" --skip-main 2>&1 | Tee-Object -FilePath "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\LOGS\full_controls_corrected.log"
```

- Elapsed time recorded at the end of the control run: **207.515 s**.
- Includes detector/shift/FD, independent direct-complex construction, Fourier interpolation, low-pass cutoffs, rectangular/non-power-of-two grids, and nested fixed-field controls.
- The first attempt at the interpolation control exposed and fixed a density-scaling bug (refined-cell density must be multiplied by `factor**2` to express density per original cell); the corrected control was rerun before reporting. The failed exploratory log is retained as `LOGS/full_controls.log` for transparency.

## Fixed-field correction rerun

After correcting the physical-density conversion in the fixed-field diagnostic:

```powershell
python -c "import sys; sys.path.insert(0, r'AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE'); import run_broadband_convergence as r; r.run_fixed_field_controls()" 2>&1 | Tee-Object -FilePath "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\LOGS\fixed_field_corrected.log"
```

This overwrote only the sub-agent’s `RESULTS/fixed_field_controls.*` files.

## Finite-window validation

```powershell
python "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\CODE\run_window_validation.py" 2>&1 | Tee-Object -FilePath "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\LOGS\large_window_validation.log"
```

- 128-wavelength physical box, P=4,8,16, all four widths, six seeds, one realization per seed = 72 fields.
- Elapsed time: **60.890 s**.
- At P=4, N=512, matching the historical broadband grid size; this is a sensitivity check sharing the main implementation, not independent validation.

## ROI-margin control

```powershell
python -c "import sys; sys.path.insert(0, r'AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE'); import run_broadband_convergence as r; r.run_margin_controls()" 2>&1 | Tee-Object -FilePath "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\LOGS\margin_controls.log"
```

This used P=4,8,16; all four widths; six seeds; and margins of 0.5, 1, and 2 central wavelengths.

## Sanity/normalization controls

```powershell
python -c "import sys; sys.path.insert(0, r'AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE'); import run_broadband_convergence as r; r.run_sanity_controls()"
```

This records the synthetic off-grid/vertex vortex cases, Hermitian self-mode check, historical nested-normalization check, and bitwise determinism check.

## Derivation tables

```powershell
python "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\CODE\summarize_audit.py" > "AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\LOGS\summary_final2.log"
```

Outputs `condition_verdicts.*`, `control_summary.json`, and `convergence_table.md` from the raw CSVs.

## Smoke test

An initial one-realization-per-seed main smoke test was run with `--quick --skip-controls`; it is retained in `LOGS/quick_main.log`. It is not used as the final result. A plotting error in that smoke test (negative bootstrap error-bar component caused by indexing integer indices rather than sampled values) was fixed before the final 864-field run. The final summary uses the corrected bootstrap implementation.
