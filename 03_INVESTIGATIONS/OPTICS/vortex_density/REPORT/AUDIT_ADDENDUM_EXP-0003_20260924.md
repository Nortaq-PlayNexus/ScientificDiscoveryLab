# AUDIT ADDENDUM — EXP-0003 broadband resolution convergence

**Date:** 2026-09-24  
**Status:** independent audit addendum; no historical EXP-0003 result was overwritten.  
**Primary evidence directory:** `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/`  
**Corrected controls:** `AUDIT/INDEPENDENT_AUDIT_20260924/broadband_controls_corrected_results.json`

## Question

Does the broad-band vortex-density deficit at low pixels per wavelength arise from finite-grid/near-Nyquist sampling rather than a new physical density law?

## Method

A self-contained NumPy PCG64 implementation held the physical Gaussian spectrum fixed while varying pixels per central wavelength:

- P = 4, 6, 8, 12, 16, 24, 32, 48, 64;
- sigma_k = 0.10, 0.25, 0.50, 0.75;
- six seeds: 42, 7, 123, 2023, 314159, 271828;
- four independent realizations per seed (24 fields per condition);
- continuous, discrete-mode, and finite-Nyquist Kac–Rice/Nye–Berry predictions;
- winding detector plus targeted detector, low-pass, direct-complex, rectangular, and Fourier-interpolation controls.

The physical convention and all raw rows are recorded in the sub-agent README and `RESULTS/main_summary.json`.

## Main result

Representative measured/discrete-prediction ratios:

| sigma_k | P=4 | P=8 | P=16 | P=32 | P=64 |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.018 | 1.009 | 1.004 | 1.003 | 0.998 |
| 0.25 | 0.994 | 0.998 | 1.001 | 1.007 | 0.997 |
| 0.50 | 0.915 | 0.985 | 1.001 | 0.996 | 0.997 |
| 0.75 | 0.828 | 0.956 | 0.986 | 0.997 | 0.997 |

The deficit is strongest for broad spectra at low P and decreases toward one as the grid resolves the spectrum. Narrow spectra are already close to one, with small finite-window bias.

## Controls and failures

- Corrected direct-complex fields reproduce the convergence.
- Controlled low-pass spectra show the same approach to the prediction as the grid resolves the spectrum.
- The first sub-agent Fourier-interpolation helper had an extra division by `factor**2`; its raw output is preserved but invalid. The corrected audit-only helper multiplies by `factor**2` and returns near-unity ratios.
- A regularized unit vortex is detected by the winding counter. The contour sanity test with the exact zero on a grid vertex is degenerate and is not treated as a detector failure.
- A separate static review found that the historical real-field generator treats self-conjugate Fourier coefficients approximately; the aggregate effect is small in the tested condition but should be fixed for precision work.

## Classification

**Finite-resolution/spectral-support artifact supported in this protocol.** The result is a useful control study, not a claim of a new physical law. The exact broadband-resolution protocol was not matched in the metadata/abstract literature search, so novelty remains unresolved.

## Reproduction

```text
python AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE/run_broadband_convergence.py --realizations 4 --skip-controls
python AUDIT/INDEPENDENT_AUDIT_20260924/broadband_controls_corrected.py
```

The first command writes only under `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/`; the second writes only under `AUDIT/INDEPENDENT_AUDIT_20260924/`.
