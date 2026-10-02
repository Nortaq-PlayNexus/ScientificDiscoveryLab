# Independent EXP-0003 broadband vortex-density convergence audit

**Sub-agent:** EXP-0003 broadband/near-Nyquist audit  
**Date:** 2026-09-24  
**Scope:** independent reproduction and resolution-convergence study; no historical experiment or registry file was edited.

## Executive verdict

The EXP-0003 broadband deficit is **a finite-sampling/spectral-resolution effect, not a persistent failure of the Kac–Rice/Nye–Berry law and not a grid-lock of the winding counter**. With the physical Gaussian spectrum held fixed, the measured/theoretical ratio rises toward 1 as the pixel pitch is refined. The effect is especially strong for the broad `sigma_k=0.50` and `0.75` cases.

The evidence separates the causes as follows:

1. **Finite cell/phase-topology sampling is the dominant cause.** At `P=4`, `sigma_k=0.75` gives `0.7966 [0.7887,0.8047]` versus the continuous prediction, while at `P=16` it is `0.9865 [0.9796,0.9930]` and at `P=64` it is `0.9966 [0.9877,1.0044]`.
2. **Spectral truncation/aliasing contributes, especially for `sigma_k=0.75`, but is not the whole deficit.** At `P=4`, the sampled-mode prediction is `0.8285` while the full continuous-spectrum prediction is `0.7966`; the latter difference is the unresolved high-`k` tail. Nevertheless, a deficit remains even against the renormalized sampled-mode prediction.
3. **Finite-difference derivative error is real but is not the vortex-count cause by itself.** The forward finite-difference density is only `0.7164` of the exact spectral prediction at `P=4, sigma=0.75`, yet the winding detector is already much closer (`0.7966` to full, `0.8285` to discrete). The exact spectral derivative is the appropriate predictor for this diagnosis.
4. **Both detectors show the low-resolution deficit.** The contour detector is even more undercounting at `P=4` (`sigma=0.75`: D2/D1 about `0.91`), so the issue is not unique to the winding implementation.
5. **Phase wrapping is not a global-unwrapping bug.** Principal edge increments are used directly; fractional shifts produce small count changes, and a synthetic off-grid unit vortex is detected by both detectors. The likely mechanism is that a rapidly varying phase between adjacent samples can traverse a branch cut more than once, which a plaquette winding on the coarse samples cannot represent. Explicit Fourier interpolation recovers the missing count.
6. **The physical spectrum, rather than a hidden change in `sigma_k`, drives the trend.** The physical `k0=pi/2` and the four physical `sigma_k` values were held fixed while `dx=4/P`; a 128-wavelength validation at `P=4` reproduced the historical `N=512` ratios.

**No persistent broadband deficit remains at `P>=16` in this audit, and no alternative physical implementation issue was found.** This is a controlled resolution result, not a claim of new physics or novelty.

## 1. Historical material inspected

I inspected:

- `03_INVESTIGATIONS/OPTICS/vortex_density/CODE/run_vortex_density.py`
- `RESULTS/EXP-0003_results.json` and `CONFIG/EXP-0003_experiment.json`
- `CONFIG/prereg_EXP-0003.json`
- `EXPERIMENT_PLAN.md`, `HYPOTHESIS.md`, `PREDICTIONS.md`, `CONTROLS.md`, `QUESTION.md`, `README.md`
- `REPORT/TECHNICAL_SUMMARY.md` and `LITERATURE.md`
- `REPLICATION/independent_check.py` and its JSON output
- `FALSIFICATION/planning_checks.md`, `CHANGELOG.md`, and the machine-readable changelog

There is no separate `METHODOLOGY.md` in the historical directory; the methodology is split across `EXPERIMENT_PLAN.md`, `QUESTION.md`, and the code comments. The historical preregistration explicitly fixed the broad Gaussian cases at `k0=pi/2`, `N=512`, and did not run the fixed-physical-spectrum resolution ladder requested here.

The historical result being audited was:

| historical `sigma_k` | historical winding ratio at `N=512` | historical contour ratio |
|---:|---:|---:|
| 0.10 | 1.0160 | 0.9855 |
| 0.25 | 0.9898 | 0.9543 |
| 0.50 | 0.9130 | 0.8615 |
| 0.75 | 0.8287 | 0.7558 |

The historical report correctly called this a “near-Nyquist finite-grid effect,” but explicitly said it was characterized rather than explained. The present audit tests that statement.

## 2. Independent design and physical convention

The independent implementation is self-contained in:

- `CODE/run_broadband_convergence.py`
- `CODE/summarize_audit.py`
- `CODE/run_window_validation.py`

It does not import the historical EXP-0003 code or the shared laboratory RNG.

### Fixed physical spectrum

I used the EXP-0003 reference-pixel physical units:

\[
 k_0^{\rm phys}=\pi/2,\qquad
 S(k)=\exp\left[-\frac{(|k|-k_0^{\rm phys})^2}{2\sigma_{k,\rm phys}^2}\right],
\]

with

\[
 \sigma_{k,\rm phys}\in\{0.10,0.25,0.50,0.75\}.
\]

For a requested pixels-per-wavelength value `P`, the pixel pitch is

\[
 dx=4/P,
\]

so the dimensionless sampled central wavenumber is `k0*dx=2*pi/P`, exactly matching the EXP-0003 `P=4` convention. The physical box was held fixed at 24 central wavelengths, hence `N=24P` (N=96 at P=4 and N=1536 at P=64). This makes the physical `k0` and every physical `sigma_k` fixed as the pitch changes. A one-wavelength interior margin was used for the main sweep.

The 24-wavelength box was chosen for a tractable nine-resolution sweep. It is not assumed to be exact: a separate 128-wavelength run used `N=512` at `P=4` and reproduced the historical values (see below). At `P=4`, the carrier itself is resolved (`k0=pi/2` is a DFT mode, `m=N/4`); the unresolved issue is the high-`k` tail and phase variation *within* a pixel cell, not absence of the central carrier mode.

### Predictions and uncertainty

The continuous isotropic Kac–Rice/Nye–Berry prediction was evaluated from the radial integral

\[
 n_{\rm phys}=\frac{1}{4\pi}
 \frac{\int_0^\infty k^3 S(k)\,dk}
      {\int_0^\infty k S(k)\,dk},
\]

and converted to a density per pixel cell with `n_cell=n_phys*dx^2`. I also recorded:

- the exact sampled-mode prediction `sum(kx^2 S)/(2*pi*sum(S))`;
- the continuous prediction after truncating the integral at the grid Nyquist limit;
- forward and central finite-difference derivative moments.

The main table below uses the **continuous full-spectrum prediction**. Each condition has 6 seeds × 4 independent realizations = 24 fields. The intervals are 99% percentile bootstrap intervals over fields (2,000 resamples), not over correlated pixels. Seeds were the existing ladder `(42,7,123,2023,314159,271828)`, with independent NumPy PCG64/SeedSequence streams.

## 3. Main convergence result

The complete nine-point table is in `RESULTS/convergence_table.md`; the raw 864 rows are in `RESULTS/main_rows.csv` and the derived table is in `RESULTS/main_summary.csv`.

| `sigma_k` | P=4 ratio [99% CI] | P=8 | P=16 | P=32 | P=64 |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.0183 [1.0080, 1.0284] | 1.0091 | 1.0041 | 1.0027 | 0.9980 [0.9911,1.0052] |
| 0.25 | 0.9935 [0.9860, 1.0023] | 0.9984 | 1.0007 | 1.0069 | 0.9975 [0.9890,1.0066] |
| 0.50 | 0.9133 [0.9029, 0.9242] | 0.9854 | 1.0007 | 0.9957 | 0.9971 [0.9867,1.0082] |
| 0.75 | 0.7966 [0.7887, 0.8047] | 0.9557 | 0.9865 | 0.9966 | 0.9966 [0.9877,1.0044] |

For every width, all point estimates at `P>=16` are within 3% of one. The endpoint reduction in absolute error is `0.0163`, `0.0040`, `0.0838`, and `0.2000` for `sigma=0.10,0.25,0.50,0.75`, respectively. The high-resolution CIs include one.

The exact sampled-mode ratios at `P=4` were `1.0183`, `0.9935`, `0.9146`, and `0.8285`. The difference between the last sampled-mode value and the full-spectrum value is the continuous high-`k` tail omitted at the `P=4` Nyquist limit. It is large only for the broadest case.

### Sigma-specific verdicts

- **`sigma_k=0.10`: no material broadband deficit.** The `P=4` value is a small positive finite-cell/phase-sampling offset and is already within 3%; the high-resolution values are centered on one.
- **`sigma_k=0.25`: no material deficit at the tested resolutions.** `P=4` is within 1% and the ladder is flat around one.
- **`sigma_k=0.50`: a robust but vanishing finite-resolution deficit.** The `P=4` deficit is about 8.7% relative to the full prediction, about 8.5% relative to the sampled-mode prediction, and shrinks below 1.5% by `P=8` and below 0.5% by `P=16`.
- **`sigma_k=0.75`: the largest and most clearly resolution-dependent deficit.** It is about 20.3% low versus the full continuum prediction (`17.2%` versus the renormalized sampled-mode prediction) at `P=4`, about 4.4% low at `P=8`, 1.35% low at `P=16`, and within Monte Carlo error of one by `P>=24`.

## 4. Targeted controls and mechanism separation

### 4.1 Exact discrete-mode prediction versus finite differences

At `P=4`, the forward finite-difference prediction relative to the exact discrete spectral prediction was:

| `sigma_k` | forward difference | central difference | winding ratio to full prediction |
|---:|---:|---:|---:|
| 0.10 | 0.8588 | 0.5238 | 1.0183 |
| 0.25 | 0.8269 | 0.4785 | 0.9935 |
| 0.50 | 0.7779 | 0.3784 | 0.9133 |
| 0.75 | 0.7164 | 0.2904 | 0.7966 |

At `P=64`, the corresponding forward values are `1.0066`, `0.9995`, `0.9984`, and `0.9993`; central values are `1.0047`, `0.9974`, `0.9954`, and `0.9950`.

This demonstrates that the historical forward-difference diagnostic is badly biased near Nyquist, even when the winding count is good (`sigma=0.10`). It also demonstrates that the broadband winding deficit cannot be repaired by simply interpreting the forward derivative as the density. The exact DFT derivative is the appropriate reference for this test.

### 4.2 Winding versus contour intersection, phase increments, and shifts

At `P=4`, D2 is more undercounting than D1, especially for the broad spectrum:

| `sigma_k` | P=4 D1 | P=4 D2 | P=8 D1 | P=8 D2 | P=16 D1 | P=16 D2 |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.009 | 0.978 | 1.005 | 1.001 | 0.996 | 0.995 |
| 0.50 | 0.923 | 0.874 | 0.983 | 0.975 | 0.995 | 0.995 |
| 0.75 | 0.828 | 0.753 | 0.957 | 0.945 | 0.987 | 0.986 |

The principal-angle edge increments are bounded by `pi`; the largest observed magnitude was approximately `pi-10^-5`. This is expected for `np.angle`, but it means a coarse edge can hide more than one physical phase turn. Across the main sweep, the maximum absolute plaquette winding was 1 and the largest charge imbalance was about 1.2%, so the deficit is not explained by a systematic `+2/-2` cancellation within a plaquette. Fractional Fourier shifts did not produce a grid-lock-sized discontinuity. For `P=4,sigma=0.75`, the mean half-pixel shift change was about 1.8% and the largest single realization was 4.1%; at `P=8` the mean was about 0.5%, and at `P=16` about 0.4%. The large-window and fixed-field controls show the deficit is not a fixed lattice phase offset.

A synthetic unit vortex placed between samples was detected once by both winding and contour detectors. A deliberately ill-posed vortex placed exactly on a sample vertex was not counted; that edge case is recorded in `RESULTS/sanity_controls.json` and is not a random-field occurrence.

### 4.3 Explicit band-limited interpolation

I zero-padded the centered DFT to obtain exact trigonometric interpolation of the same periodic field at 2× and 4× spatial density. This is not nearest-neighbour or bilinear upsampling. The refinement density was converted back to density per original pixel cell by multiplying by `factor^2`.

For `sigma=0.75` at `P=4`, the six-seed means were:

| sampling | ratio |
|---|---:|
| original | 0.8197 |
| 2× Fourier interpolation | 0.9493 |
| 4× Fourier interpolation | 0.9786 |

For `sigma=0.50` at `P=4`, the corresponding values were `0.9159`, `0.9846`, and `0.9958`. At `P=6,sigma=0.75`, 4× interpolation gave about `1.002`; at `P=8`, it gave about `1.006`. This is strong evidence that unresolved phase topology between coarse samples, not a bad Kac–Rice denominator or a unique winding-counter coding error, produces much of the deficit.

### 4.4 Low-pass spectral truncation and aliasing

The fixed 128-wavelength master spectrum gives the fraction of power above each coarse grid’s Nyquist limit. At `P=4` (`k_Nyq=2 k0`) it is approximately:

- `sigma=0.10`: `2.3e-55`
- `sigma=0.25`: `3.9e-10`
- `sigma=0.50`: `1.8e-3`
- `sigma=0.75`: `3.99e-2`

At `P=8`, these are effectively zero for all four widths.

The controlled low-pass sweep confirms that removing high-`k` power helps but does not eliminate the `P=4` deficit. Ratios to the *truncated* prediction for `sigma=0.75` were approximately:

| cutoff / k0 | P=4 | P=8 | P=16 | P=32 |
|---:|---:|---:|---:|---:|
| 1.50 | 0.921 | 0.989 | 1.009 | 1.004 |
| 2.00 | 0.851 | 0.976 | 1.002 | 0.995 |

Thus spectral truncation/aliasing is a real secondary mechanism, while coarse-cell phase sampling remains necessary to explain the low-`P` residual.

### 4.5 One fixed continuous field across resolutions

I generated one master field at `P=32` (N=768, 24 wavelengths) for each width and seed, then sampled the same periodic field on nested grids at `P=4,8,16,32`. This removes Monte Carlo changes in the field identity from the convergence comparison.

For `sigma=0.75`, the six-seed mean ratios to the continuous prediction were:

| P | ratio to full prediction | ratio of measured physical density to master measured density | master power above coarse Nyquist |
|---:|---:|---:|---:|
| 4 | 0.8215 | 0.8120 | 0.0399 |
| 8 | 0.9700 | 0.9587 | ~0 |
| 16 | 1.0040 | 0.9923 | ~0 |
| 32 | 1.0118 | 1.0000 | ~0 |

The same-field control is therefore consistent with the independent-field ladder and rules out a changing-random-realization explanation.

### 4.6 Independent field construction

The main route generates independent real `u` and `v` components with corrected Hermitian symmetry. A separate direct route drew arbitrary complex Fourier coefficients directly, without Hermitian pairing, which is valid because the field `E` itself is complex. Across the 12 width/P construction cells, the mean direct-minus-corrected ratio difference was at most about `0.010`, with field-to-field standard deviations roughly `0.015–0.027`. This agrees within Monte Carlo error and is an independent construction check, although both routes use the same winding implementation.

### 4.7 Non-square and non-power-of-two grids

At `P=8,sigma=0.75`, six-seed mean ratios were:

- square `192×192`: `0.9618`
- rectangular `221×192`: `0.9651`
- rectangular `193×192`: `0.9592`

The differences are within the observed realization scatter; no rectangular-grid or FFT-shape defect was found.

### 4.8 ROI margin

Using margins of 0.5, 1, and 2 central wavelengths changed the six-seed mean ratio only slightly. For `P=4,sigma=0.75`, the means were `0.8230`, `0.8219`, and `0.8204`; for `P=8` they were `0.9546`, `0.9562`, and `0.9540`. The deficit is therefore not a boundary-margin artifact.

### 4.9 Hermitian symmetry, normalization, Nyquist modes, and determinism

Two implementation details were checked explicitly:

1. The historical `real_gaussian` symmetrizes complex coefficients at self-conjugate locations as well as paired locations. This halves the variance of the self-conjugate coefficients. In the tested Gaussian spectrum, the self-conjugate power fraction is only `4.56e-5`, and corrected versus historical symmetrization power calibrations were indistinguishable (`0.9974±0.0245` versus `0.9974±0.0245`). It is a real implementation imperfection but not a material source of the broadband deficit.
2. The historical `complex_field` passes `S/2` into a routine that itself applies `sqrt(S/2)`, producing approximately half the requested total complex-field power. The independent calibration measured `0.5004±0.0092` relative to the requested power. This is a genuine normalization bug for absolute power, but global amplitude cancels from `n_meas/n_pred`, so it cannot explain the ratio deficit.

A same-stream rerun was bitwise identical (`determinism_bitwise_equal=true`, maximum difference 0). This is a determinism check, not independent validation; all main fields share the self-contained generator and detector implementation.

## 5. Literature/novelty search

A live Crossref/OpenAlex metadata and abstract search was performed on 2026-09-24. The detailed query list, URLs, abstracts, and limitations are in `LITERATURE_SEARCH.md`.

Primary sources located include:

- Nye & Berry (1974), DOI `10.1098/rspa.1974.0012`;
- Berry & Dennis (2000/2001), DOI `10.1098/rspa.2000.0602`, plus its correction;
- Rice (1944), DOI `10.1002/j.1538-7305.1944.tb00874.x`;
- Balistreri et al. (2000), DOI `10.1103/PhysRevLett.85.294`, and Vohnsen & Bozhevolnyi (2001), DOI `10.1103/PhysRevLett.87.259401`;
- Dändliker et al. (2004), DOI `10.1088/1464-4258/6/5/009`, on measuring phase singularities at subwavelength resolution;
- Wang et al. (2003), DOI `10.1117/12.516629`, on phase singularities in dynamic speckle and limitations of phase-based analysis.

The underlying Kac–Rice/Nye–Berry law and the need for careful local phase-singularity identification are established. I found no primary or authoritative source in the searches that exactly matches this full protocol and parameter ladder. **I therefore make no novelty claim.** The exact fixed-spectrum convergence plus explicit Fourier-interpolation control is a useful laboratory result/control package, not evidence of new physics.

## 6. Limitations and shared dependencies

- The main sweep uses a 24-central-wavelength physical box for tractability. The 128-wavelength validation at `P=4,8,16` reproduced the same trends; at `P=4` its six-seed means were `1.0168`, `0.9916`, `0.9100`, and `0.8273` for the four widths, essentially matching the historical values.
- The main sweep uses independent fields at each resolution, not one common field. The nested fixed-field control supplies a common-field convergence check.
- Controls use six fields per targeted condition (often one realization per seed) and are diagnostic rather than powered hypothesis tests.
- The physical spectrum is isotropic and Gaussian; no anisotropic, correlated, non-Gaussian, or experimentally measured field was tested.
- The Kac–Rice prediction assumes the ideal complex Gaussian model. This audit tests the numerical realization of that model, not the physical universality of the law.
- The historical and independent routes share no code, but the main, interpolation, low-pass, margin, and fixed-field controls share the corrected field/detector implementation. The direct-complex construction is the independent construction check; it is not a second complete detector implementation.
- Search-engine and publisher-full-text access was incomplete; see `LITERATURE_SEARCH.md`.

## 7. Flag for the main auditor

The direction of the historical conclusion is supported, but the wording “near-Nyquist finite-grid effect” is incomplete. The evidence supports the more specific statement:

> **At fixed physical spectrum, the coarse-grid broadband deficit is a combination of unresolved high-k spectral content and sampling-induced loss of phase topology between pixels; both independent detectors show it, exact spectral prediction is valid, and the ratio converges to one with refinement.**

The historical normalization and self-conjugate Hermitian details should be recorded as implementation bugs/limitations even though they do not change the ratio. No unexpected persistent deviation or potentially novel physical effect was found.

## 8. Artifact index

- Main code: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE/run_broadband_convergence.py`
- Main raw rows: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/RESULTS/main_rows.csv`
- Main summary: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/RESULTS/main_summary.csv`
- Main convergence figure: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/RESULTS/main_convergence.png`
- Derived condition verdicts: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/RESULTS/condition_verdicts.json`
- Curated key values: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/RESULTS/selected_values.json`
- Controls: `detail_controls`, `construction_controls`, `interpolation_controls`, `lowpass_controls`, `margin_controls`, `non_square_controls`, `fixed_field_controls`
- Window validation: `large_window_validation.csv` and `large_window_validation_summary.json`
- Sanity/normalization/determinism: `sanity_controls.json`
- Final environment/runtime record: `RESULTS/final_environment.json`
- Literature: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/LITERATURE_SEARCH.md`
- Exact commands/runtime: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/COMMANDS_AND_RUNTIME.md`
- Logs: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/LOGS/`
- Parallel-runner coexistence record: `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/COLLISION_NOTE.md`
