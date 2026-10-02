# Parallel sub-agent task — EXP-0003 broadband vortex-density convergence

You are an independent scientific sub-agent working in `C:\Users\natha\ScientificDiscoveryLab` while the main agent conducts a full laboratory audit. Do not pause or alter the main audit.

## Scope
Investigate whether the broadband vortex-density deficit in EXP-0003 is caused by finite-grid/near-Nyquist resolution, aliasing, spectral truncation, finite-difference derivative error, vortex detection, phase wrapping, or another implementation issue.

## Required work
1. Inspect `03_INVESTIGATIONS/OPTICS/vortex_density/CODE/run_vortex_density.py`, its results, preregistration, methodology, and both detectors. Do not assume existing conclusions are correct.
2. Design and actually run a resolution-convergence experiment while holding the physical spectrum fixed. Test pixels-per-wavelength approximately 4, 6, 8, 12, 16, 24, 32, 48, and 64.
3. Test Gaussian radial spectral widths `sigma_k = 0.10, 0.25, 0.50, 0.75` around `k0=pi/2`, matching EXP-0003. Clearly define how `sigma_k` is held physically fixed as pixel pitch changes.
4. Use multiple independent seeds. Prefer the existing seed ladder `(42,7,123,2023,314159,271828)`, but add a clearly independent NumPy PCG64 route if useful.
5. At every condition calculate measured vortex density divided by the theoretical Kac-Rice/Nye-Berry density, with uncertainty. Determine whether ratios converge systematically to 1 as pixels-per-wavelength increases.
6. Separate these effects with targeted controls:
   - exact discrete-mode spectral prediction versus finite-difference derivative prediction;
   - winding counter versus contour-intersection detector;
   - fractional Fourier shifts;
   - low-pass spectral truncation at controlled cutoffs;
   - non-square/non-power-of-two grids if feasible;
   - explicit band-limited interpolation of one fixed continuous random field across resolutions, if scientifically valid.
7. Check implementation details including Hermitian symmetry, `np.angle` wrapping, Nyquist modes, margin selection, normalization, and whether the current `k0=pi/2` Gaussian spectrum is actually resolved at four pixels per wavelength.
8. Perform a serious literature/novelty search using primary/authoritative sources if web access is available. Determine whether broadband resolution convergence and near-Nyquist vortex-count loss are already characterized. Do not call the effect novel without evidence.
9. Treat same-code reruns as determinism checks, not independent validation. Explain any shared implementation dependencies.

## Output location and safety
- The main audit is actively writing under `AUDIT/INDEPENDENT_AUDIT_20260924/`.
- Put all sub-agent code, raw results, logs, and report under `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/`.
- Do not overwrite historical experiment files, registries, reports, or original results. Do not edit `EXPERIMENT_REGISTRY.md` or other root files. The main auditor will integrate any proposed registry entry after reviewing the evidence.
- Include exact commands, environment, runtime, seeds, parameters, raw result files, observed values, comparisons, artifact tests, bugs, limitations, and a concise verdict for each sigma condition.
- If something unexpected or potentially novel appears, flag it explicitly rather than silently changing the main hypothesis.

Return a concise final summary to the invoking agent with the output paths and main verdict.