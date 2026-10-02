# EXP-0003 broadband vortex-density deficit — parallel verification report

**Audit date:** 2026-09-24  
**Experiment:** EXP-0003 / Q-O002 / HYP-002  
**Role:** independent parallel sub-agent; the main prime-gap audit was not paused, restarted, or modified.  
**Canonical status:** no historical experiment, registry, report, or result file was edited. The read-only hash snapshot is in `CANONICAL_HASHES_NON_DESTRUCTIVE.json`.

## Executive verdict

The historical conclusion that the broadband deficit is a finite-grid effect is **directionally correct but mechanistically incomplete**. At fixed physical Gaussian spectrum, the measured vortex density approaches the Kac–Rice/Nye–Berry prediction as pixels per central wavelength increases. The low-resolution deficit is a combination of:

1. unresolved high-`k` spectral power above the coarse grid's Nyquist limit (aliasing/spectral truncation), especially for `sigma_k=0.50` and `0.75`; and
2. loss of phase topology between coarse samples, where a principal phase increment can hide more than one physical phase turn.

Both effects are sampling/finite-resolution effects, not a persistent failure of the theoretical law and not a unique winding-counter coding error. The broad `sigma_k=0.75` deficit is large at four pixels per wavelength, shrinks monotonically, and is within Monte Carlo error of one by roughly `P>=16–24` in the two independent protocols. The `sigma_k=0.10` and `0.25` cases have no material broadband deficit.

No new physics or novelty claim is made. The result is an audit/methodological characterization of a known law. A combined fixed-spectrum convergence/interpolation package could be useful, but the literature search did not establish novelty and an exhaustive search remains out of scope.

## 1. Historical material and certified seed machinery inspected

The exact historical investigation is:

`03_INVESTIGATIONS/OPTICS/vortex_density/`

I inspected:

- `CODE/run_vortex_density.py` (field construction, spectral prediction, D1 winding, D2 contour detector, shifts, seed ladder);
- `RESULTS/EXP-0003_results.json` and `CONFIG/EXP-0003_experiment.json`;
- `CONFIG/prereg_EXP-0003.json`, `EXPERIMENT_PLAN.md`, `CONTROLS.md`, `HYPOTHESIS.md`, `PREDICTIONS.md`, `QUESTION.md`, and `README.md`;
- `REPORT/TECHNICAL_SUMMARY.md`, `LITERATURE.md`, and `CHANGELOG.md`;
- `REPLICATION/independent_check.py` and `REPLICATION/independent_check.json`;
- `04_SHARED_ENGINE/engine/utilities/core.py` and the related reproducibility conventions.

The certified project RNG is the deterministic SHA-256-labelled contract:

```python
from engine.utilities.core import rng, SEED_LADDER
```

with `SEED_LADDER=(42, 7, 123, 2023, 314159, 271828)`. The root-level verification run used this route for its primary sweep and a deliberately separate NumPy PCG64 route for validation. Same-code reruns would be determinism checks only; they were not counted as independent validation.

The historical broadband ratios (winding D1 / discrete spectral prediction) were:

| historical sigma | D1 ratio | D2 contour ratio |
|---:|---:|---:|
| 0.10 | 1.01596 | 0.98547 |
| 0.25 | 0.98981 | 0.95429 |
| 0.50 | 0.91304 | 0.86149 |
| 0.75 | 0.82868 | 0.75582 |

The historical report correctly called the pattern a near-Nyquist finite-grid effect, but explicitly said it was characterized rather than explained. This audit tests that statement.

## 2. Parallel-runner provenance and collision handling

The assigned audit directory was shared by two non-destructive runners that were already present/active:

- **Root-level runner used for the primary verification described first below:** `run_broadband_audit.py`, with outputs named `primary_*`, `common_field_*`, `lowpass_*`, `nonstandard_*`, and `plane_wave_*` at the audit-folder root.
- **Namespaced independent runner:** `CODE/run_broadband_convergence.py`, with outputs under `RESULTS/`, `REPORT/`, and `LOGS/`. Its detailed report is `REPORT/SUBAGENT_REPORT.md`.

The coexistence is documented in `COLLISION_NOTE.md`. Neither canonical EXP-0003 files nor the other runner's in-progress files were overwritten. The two protocols use different physical box sizes and field-normalization details, so small numerical differences are expected; the convergence signs and mechanism conclusions agree.

## 3. Physical convention and predictions

The EXP-0003 reference convention is retained:

- `k0_phys = pi/2` per original reference-pixel length unit;
- central wavelength `lambda0_phys=4` in those units;
- physical Gaussian widths `sigma_phys in {0.10, 0.25, 0.50, 0.75}` in the same units;
- at target `P` pixels per central wavelength, `dx=4/P`, so the sampled central wavenumber is `k0_px=2*pi/P` and `sigma_px=sigma_phys*dx`.

Thus `P=4` reproduces the historical dimensionless `k0=pi/2` and sigma values. Increasing `P` changes pixel pitch, **not** the physical spectrum.

The continuous isotropic Kac–Rice/Nye–Berry prediction used here is

\[
 n_{\rm phys}=\frac{1}{4\pi}
 \frac{\int_0^\infty k^3 S(k)\,dk}
      {\int_0^\infty k S(k)\,dk},
 \qquad
 S(k)=e^{-(k-k_{0,\rm phys})^2/(2\sigma_{\rm phys}^2)}.
\]

The density per sampled pixel is `n_phys*dx^2`. The exact sampled-mode prediction was also calculated:

\[
 n_{D,\rm px}=\frac{\sum_{\bf k} k_x^2 S({\bf k})}
 {2\pi\sum_{\bf k}S({\bf k})}.
\]

The distinction is important: the continuous prediction includes the physical high-`k` tail, while the discrete prediction contains only the DFT modes actually present on that grid.

## 4. Primary resolution-convergence run (root-level runner)

### Exact command and environment

```powershell
python AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\run_broadband_audit.py --n-real 8 `
  > AUDIT\SUBAGENT_EXP0003_BROADBAND_20260924\full_run.log 2>&1
```

Recorded environment:

- Windows 10, Python 3.14.7;
- NumPy 2.5.3, SciPy 1.18.1;
- Intel64 Family 6 Model 158 Stepping 10;
- start `2026-09-23T18:17:50+00:00`, finish `2026-09-23T19:06:20+00:00`;
- elapsed `2910.819 s` (the long runtime is dominated by repeated high-resolution contour diagnostics);
- script SHA-256: `fa3b3333f20b3019eb3cad3558663dd58a91e8ec03092f5830b9c0be685a338c`.

The primary sweep used `N=32P`, a fixed physical box of 128 reference length units (32 central wavelengths), all nine requested values

`P={4,6,8,12,16,24,32,48,64}`,

all four widths, six seeds, and eight independent fields per seed. It produced 1,728 certified-route rows. A separate PCG64 validation route used four fields per seed (864 rows).

### Certified-route results

The complete table, with 95% intervals across six seed-block means, is in:

- `REPORT/EXP0003_BROADBAND_ROOT_RUN_TABLES.md`
- `our_primary_convergence.csv`

Selected full-spectrum ratios (winding density / continuous Kac–Rice prediction) are:

| sigma | P=4 | P=6 | P=8 | P=12 | P=16 | P=24 | P=32 | P=48 | P=64 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.01748 | 1.01203 | 1.00322 | 1.00142 | 0.99922 | 1.00040 | 1.00241 | 0.99933 | 0.99950 |
| 0.25 | 0.98895 | 0.99866 | 0.99948 | 0.99714 | 0.99966 | 1.00061 | 0.99972 | 1.00196 | 1.00301 |
| 0.50 | 0.90803 | 0.96773 | 0.97967 | 0.99073 | 0.99599 | 0.99827 | 0.99719 | 1.00083 | 1.00209 |
| 0.75 | 0.79507 | 0.92421 | 0.95743 | 0.98081 | 0.99318 | 0.99648 | 0.99900 | 0.99611 | 1.00161 |

For comparison, the same certified route's sampled-mode ratios at `P=4` were:

| sigma | ratio to sampled modes | ratio to full continuum |
|---:|---:|---:|
| 0.10 | 1.01748 | 1.01748 |
| 0.25 | 0.98895 | 0.98895 |
| 0.50 | 0.90936 | 0.90803 |
| 0.75 | 0.82679 | 0.79507 |

The `sigma=0.75` difference between the last two columns is the unresolved physical tail, not a changed hypothesis.

The independent PCG64 route gives the same pattern. Its `P=4,8,16,32,64` sampled-mode ratios are:

| sigma | P4 | P8 | P16 | P32 | P64 |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.01558 | 1.00387 | 1.00688 | 1.00224 | 1.00079 |
| 0.25 | 0.98723 | 0.99722 | 1.00059 | 1.00008 | 0.99924 |
| 0.50 | 0.91753 | 0.96908 | 0.99544 | 1.00078 | 0.99918 |
| 0.75 | 0.83086 | 0.92347 | 0.98605 | 0.99993 | 0.99946 |

The PCG64 route is an independent RNG/field stream, not a new detector implementation; that limitation is stated explicitly.

### Sigma-specific verdicts

- **`sigma=0.10`: no material deficit.** The P4 offset is a small positive finite-cell/phase-sampling bias; ratios are centered on one from P8 onward.
- **`sigma=0.25`: no material deficit.** P4 is about 1.1% low, then the ladder is flat around one.
- **`sigma=0.50`: robust but vanishing finite-resolution deficit.** P4 is about 9.2% low; P8 is about 2.0% low; P16 is within about 0.4% of one.
- **`sigma=0.75`: largest and clearly resolution-dependent deficit.** P4 is about 20.5% low versus the full continuum prediction (17.3% low versus the renormalized sampled-mode prediction); P8 is about 4.3% low; P16 is about 0.7% low; P32–P64 are within ordinary Monte Carlo scatter of one.

## 5. Mechanism controls

### 5.1 Spectral truncation and aliasing

The namespaced fixed-master control computed the fraction of physical power above each coarse axis-Nyquist limit. At `P=4` (`k_Nyquist=2*k0`) it found approximately:

| sigma | power above P4 Nyquist |
|---:|---:|
| 0.10 | `2.3e-55` |
| 0.25 | `3.9e-10` |
| 0.50 | `1.8e-3` |
| 0.75 | `3.99e-2` |

At P8 these fractions are effectively zero for all four widths. This independently predicts that the strongest deficit should be the broadest spectrum and should largely disappear after one resolution doubling.

The root runner independently gives continuous versus discrete predictions at P4 of approximately `0.329688` versus `0.317038` for sigma 0.75. The measured density is still well below the discrete prediction, so high-`k` truncation is a real secondary mechanism but **not the whole deficit**. In the root low-pass control, the sigma-0.75 P4 ratio to the *renormalized filtered prediction* was approximately 0.998, 0.980, 0.930, and 0.854 at cutoffs 0.25, 0.50, 0.75, and 1.00 times the axis Nyquist, respectively; at P8 the corresponding values were 0.997, 0.970, 0.954, and 0.956. Removing unresolved high-`k` content helps, but coarse phase sampling remains.

### 5.2 Exact derivative versus finite differences

The root runner's forward finite-difference prediction divided by the exact discrete spectral prediction was:

| sigma | P4 FD/discrete | P16 FD/discrete | P64 FD/discrete |
|---:|---:|---:|---:|
| 0.10 | 0.850 | 0.984 | 1.001 |
| 0.25 | 0.833 | 0.988 | 1.002 |
| 0.50 | 0.777 | 0.985 | 0.998 |
| 0.75 | 0.715 | 0.976 | 1.000 |

The namespaced runner's central differences show the same pattern (P4 approximately 0.524, 0.479, 0.378, 0.290; P64 approximately 1.005, 0.997, 0.995, 0.995). Finite differences are therefore badly biased on coarse grids, but they are not the cause of the winding-count deficit: the winding ratio is much closer to one than the FD estimate at P4, and both converge at high P. The exact DFT derivative is the appropriate diagnostic.

### 5.3 Winding versus contour detector

The root runner's contour/D1 sampled-mode ratios at selected points were:

| sigma | P4 D1 | P4 D2 | P16 D1 | P16 D2 | P64 D1 | P64 D2 |
|---:|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.0175 | 0.9854 | 0.9992 | 0.9998 | 0.9995 | 0.9981 |
| 0.25 | 0.9890 | 0.9521 | 0.9997 | 1.0016 | 1.0030 | 1.0017 |
| 0.50 | 0.9094 | 0.8611 | 0.9960 | 0.9941 | 1.0021 | 1.0038 |
| 0.75 | 0.8268 | 0.7554 | 0.9932 | 0.9922 | 1.0016 | 1.0012 |

D2 is slightly more undercounting at low resolution, so the effect is not unique to D1. The intentionally naive contour implementation overcounts by roughly 1.7–2.2 relative to the prediction, reproducing the already documented D2 implementation defect; it is not used for the verdict.

### 5.4 Fractional shifts, phase wrapping, and grid locking

D1 uses `np.angle` on each edge increment and never accumulates a globally unwrapped phase. Fractional Fourier shifts were small and resolution-dependent rather than a fixed grid-lock jump. In the root run, mean half-pixel changes were approximately 0.7%, 0.9%, 1.0%, and 1.5% for sigma 0.10, 0.25, 0.50, and 0.75 at P4; they fell below roughly 0.8% by P32. The namespaced controls found occasional individual broad-spectrum shifts up to about 4%, but no discontinuity or persistent offset.

The physical interpretation is subtle but important: principal edge increments are bounded by `pi`, so if a rapidly varying high-`k` component rotates the phase by more than `pi` between adjacent samples, the sampled edge cannot reveal all intermediate turns. That is a sampling/phase-wrap limitation, not a global-unwrapping coding error. A synthetic off-grid unit vortex was detected once by both D1 and D2; a vortex exactly on a sample vertex is an ill-posed edge case and was not counted.

### 5.5 Explicit band-limited interpolation

The namespaced independent control performed Fourier (sinc/zero-padded DFT) interpolation of the same periodic field at 2x and 4x spatial density, converting the refined density back to density per original cell. This is not bilinear upsampling.

For `sigma=0.75`, P4, the six-seed means were:

| representation | ratio |
|---|---:|
| original samples | 0.8197 |
| 2x Fourier interpolation | 0.9493 |
| 4x Fourier interpolation | 0.9786 |

For `sigma=0.50`, the corresponding values were approximately `0.9159`, `0.9846`, and `0.9958`. The corrected density-scaling implementation and the failed exploratory log are retained in the namespaced `COMMANDS_AND_RUNTIME.md` and `LOGS/`.

This directly supports the phase-topology/sampling mechanism: adding samples of the same field recovers much of the missing count without changing the physical spectrum.

### 5.6 One fixed continuous field across resolutions

The root runner generated a P64 reference field and exactly subsampled it at P=4,8,16,32,64; a separate P48 reference covered P=6,12,24,48. For sigma 0.75, the root full-spectrum ratios were approximately:

| P | ratio to continuum prediction |
|---:|---:|
| 4 | 0.8098 |
| 8 | 0.9552 |
| 16 | 0.9881 |
| 32 | 0.9954 |
| 64 | 0.9975 |

The namespaced corrected fixed-field control gave `0.8215, 0.9700, 1.0040, 1.0118` at P4,8,16,32. The small differences are consistent with field construction, box, and finite-seed choices; both rule out a changing-random-realization explanation.

### 5.7 Non-square/non-power-of-two grids, margins, and normalization

The namespaced controls at P8, sigma 0.75 gave six-seed means of approximately 0.9618 (square), 0.9651 (rectangular), and 0.9592 (non-power-of-two). Changing the ROI margin from 0.5 to 2 central wavelengths changed the P4 sigma-0.75 mean only from about 0.8230 to 0.8204. No rectangular-FFT or boundary defect was found.

Two historical implementation details were explicitly checked:

1. The historical Hermitian symmetrization treats self-conjugate DFT bins like ordinary paired bins. Those coefficients should be real Gaussian variables, so the historical route underestimates their variance. The affected power fraction is tiny for these spectra (order `1e-5` or smaller in the tested cases).
2. The historical `complex_field` passes `S/2` into a routine that itself applies `sqrt(S/2)`, yielding approximately half the requested total complex-field power. The independent calibration measured `0.5004 +/- 0.0092` relative to the requested power.

The normalization issue matters for absolute power calibration but cancels from `n_meas/n_pred` because a global amplitude multiplier leaves both numerator and denominator unchanged. The self-conjugate issue is likewise not material to the broadband ratio. A direct root-run sanity check measured historical power/target `0.49824` and corrected power/target `0.99350`; its same-stream field was bitwise identical and the self-conjugate power fraction was `4.42e-5`. These are implementation limitations worth recording, not the cause of the observed deficit.

### 5.8 Nyquist-mode interpretation

At P4, the central carrier `k0=pi/2` is itself represented by a DFT mode (for the reference N=512 cell, a quarter-grid mode). Thus the deficit is not simply “the carrier wavelength was absent.” The relevant issue is the high-`k` tail and the amount of phase variation *within* a pixel cell. At P8 and above the central carrier and nearly all important tail power are resolved, which is why the ratios rapidly approach one.

## 6. Literature and novelty search

A live targeted search was performed in parallel with the numerical work. The available generic search endpoint returned no results; direct Crossref/OpenAlex metadata and abstracts were reachable for selected records, while some publisher pages and Semantic Scholar were rate-limited. This is documented honestly in `LITERATURE_SEARCH.md`; it is not an exhaustive systematic review.

Primary/authoritative sources located include:

- Nye, J. F. & Berry, M. V. (1974), “Dislocations in wave trains,” *Proc. R. Soc. A* 336, 165–190. DOI: <https://doi.org/10.1098/rspa.1974.0012>.
- Berry, M. V. (1978), “Disruption of wavefronts: statistics of dislocations in incoherent Gaussian random waves,” *J. Phys. A* 11, 27–37. DOI: <https://doi.org/10.1080/0305-4470/11/1/007>.
- Berry, M. V. & Dennis, M. R. (2000/2001), “Phase singularities in isotropic random waves,” *Proc. R. Soc. A* 456, 2059–2079. DOI: <https://doi.org/10.1098/rspa.2000.0602>.
- Freund, I. (1994), “Optical vortices in Gaussian random wave fields: statistical probability densities,” *JOSA A* 11, 1644. DOI: <https://doi.org/10.1364/JOSAA.11.001644>.
- Shvartsman, N. & Freund, I. (1994), “Wave-field phase singularities: near-neighbor correlations and anticorrelations,” *JOSA A* 11, 2710–2718. DOI: <https://doi.org/10.1364/JOSAA.11.002710>.
- Azaïs, J.-M., León, J. R. & Wschebor, M. (2011), “Rice formulae and Gaussian waves,” *Bernoulli* 17, 170–193. DOI: <https://doi.org/10.3150/10-BEJ265>.
- Dalmao, F. et al. (2019), “Phase singularities in complex arithmetic random waves,” *Electron. J. Probab.* 24. DOI: <https://doi.org/10.1214/19-EJP321>.
- De Angelis, L. & Kuipers, C. (2021), “Effective pair-interaction of phase singularities in random waves,” *Optics Letters* 46, 2734. DOI: <https://doi.org/10.1364/OL.422910>.
- Shannon, C. E. (1949), “Communication in the Presence of Noise,” the canonical sampling/aliasing reference; an accessible overview is <https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem>.

The Kac–Rice/Nye–Berry law, Gaussian-wave phase singularities, and the need for careful local phase-singularity identification are established. The search did not locate a paper exactly matching this complete fixed-spectrum resolution/interpolation protocol, but absence from a targeted search is not evidence of novelty. No registry or hypothesis change is recommended.

## 7. Limitations and shared dependencies

- The root sweep and namespaced sweep use finite periodic boxes (32 and 24 central wavelengths respectively); a 128-wavelength validation at P4,8,16 reproduced the historical P4 ratios and the same trend.
- The primary sweep uses independent fields at each resolution; nested fixed-field controls address field identity, and the explicit interpolation control addresses within-field refinement.
- The winding and contour controls share the corrected field/detector implementation in the namespaced runner; the direct-complex construction is an independent field-construction check, not a wholly independent second detector.
- The root primary route uses the project's certified SHA-256-labelled RNG; the PCG64 route is separate. Same-stream reruns are determinism checks only.
- The experiment is an ideal isotropic complex Gaussian model. It does not test anisotropic, correlated, non-Gaussian, or experimentally measured fields.
- The finite-difference comparison is deliberately diagnostic; exact spectral differentiation is used for the theoretical reference.
- The literature search is targeted rather than exhaustive.

## 8. Flag for the main auditor

The main auditor should retain the established law and revise only the explanatory wording:

> At fixed physical spectrum, the coarse-grid broadband deficit is a combination of unresolved high-`k` spectral content/aliasing and sampling-induced loss of phase topology between pixels. Independent detectors show the effect, exact spectral prediction is valid, and the ratio converges to one under refinement.

The historical Hermitian self-mode and normalization imperfections should be recorded as implementation limitations, with the explicit note that they do not explain the ratio deficit. No persistent broadband anomaly or potentially novel physical effect was found.

## 9. Artifact index

### Root-level runner artifacts

- Code: `run_broadband_audit.py`
- Primary raw/summary: `primary_certified_raw.csv`, `primary_certified_summary.json`, `primary_pcg64_raw.csv`, `primary_pcg64_summary.json`
- Nested-field controls: `common_field_ref64_raw.csv`, `common_field_ref64_summary.json`, `common_field_ref48_raw.csv`, `common_field_ref48_summary.json`
- Other controls: `lowpass_raw.csv`, `lowpass_summary.json`, `nonstandard_raw.csv`, `nonstandard_summary.json`, `plane_wave_check_raw.csv`, `plane_wave_check_summary.json`
- Extra implementation/determinism checks: `extra_sanity_checks.py`, `extra_sanity_results.json`, `extra_sanity.log`
- Runtime/provenance: `run_environment.json`, `run_summary.json`, `full_run.log`, `OUR_ROOT_RUN_MANIFEST.json`
- Numerical table: `REPORT/EXP0003_BROADBAND_ROOT_RUN_TABLES.md`, `our_primary_convergence.csv`

### Namespaced independent-control artifacts

- Code: `CODE/run_broadband_convergence.py`, `CODE/summarize_audit.py`, `CODE/run_window_validation.py`
- Detailed report: `REPORT/SUBAGENT_REPORT.md`
- Main table: `RESULTS/convergence_table.md`, `RESULTS/main_summary.csv`
- Explicit interpolation/low-pass/fixed-field/detector/grid controls: `RESULTS/interpolation_controls.*`, `RESULTS/lowpass_controls.*`, `RESULTS/fixed_field_controls.*`, `RESULTS/detail_controls.*`, `RESULTS/non_square_controls.*`, `RESULTS/margin_controls.*`
- Sanity and implementation checks: `RESULTS/sanity_controls.json`, `RESULTS/construction_controls.*`
- Runtime record: `COMMANDS_AND_RUNTIME.md`, `RESULTS/final_environment.json`
- Collision/provenance: `COLLISION_NOTE.md`, `POST_AUDIT_REPAIR.md`

### Literature and safety

- Literature log: `LITERATURE_SEARCH.md`
- Canonical read-only hash snapshot: `CANONICAL_HASHES_NON_DESTRUCTIVE.json`
- Historical files modified: **none**.
