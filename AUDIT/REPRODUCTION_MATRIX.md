# REPRODUCTION MATRIX — Independent Audit 2026-09-24

**Reproduction policy:** deterministic same-code reruns establish reproducibility, not independent scientific validity. Independent implementations, raw-data reanalysis, and artifact controls are tracked separately. Historical outputs were copied to `C:\Users\natha\AppData\Local\Temp\opencode\ScientificDiscoveryLab_audit_20260924_0325` for runs that could overwrite files.

## Summary matrix

| ID / target | Historical artifact | Reproduction or independent method actually run | Key observed result | Status | Limitation / decision |
|---|---|---|---|---|---|
| Repository baseline | all source/config/results | `python -m pytest` | 287 passed, 411 warnings, 26.60 s | **REPRODUCED** | Software tests do not validate science |
| EXP-0002 speckle | `.../speckle_contrast_law/RESULTS/EXP-0002_results.json` | isolated same-code rerun; independent PCG64 Gaussian and pupil-FFT grids 255/256/257 and rectangular | `C*sqrt(M)` means near 1; independent ratios within sampling error | **REPRODUCED** | Known textbook law; simulated independent modes only |
| EXP-0003 vortex | `.../vortex_density/RESULTS/EXP-0003_results.json` | isolated same-code rerun; independent non-square/non-power tests; fixed-spectrum P=4…64 sweep; corrected controls | broad-band ratio P=4→64: sigma=.50 `0.915→0.997`; sigma=.75 `0.828→0.997` | **SUPPORTED, LIMITED** | Resolution conclusion is protocol-specific; first sub-agent interpolation helper had a normalization bug |
| EXP-0003 controls | same | winding vs contour, shifts, Hermitian routes, low-pass, direct complex FFT, corrected Fourier interpolation | corrected interpolation ratios return near 1; low-pass/direct routes reproduce convergence | **SUPPORTED AFTER CORRECTION** | Synthetic contour test with vertex zero is not diagnostic; initial control run exited 255 |
| EXP-0004 RNG | `.../rng_certification/RESULTS/EXP-0004_results.json` | static orchestration review; 80 fresh seeds x G_LAB/G_PCG/G_MT; exact historical battery | pooled KS looks acceptable, but p-values strongly dependent and marginal tests reject on controls too | **INVALID CERTIFICATE** | Cannot certify generator; no lab-specific RNG failure established |
| EXP-0005/0006/0007 thresholds | `.../percolation/CODE/RESULTS/EXP-0005_results.json`, `EXP-0006_summary.json`, `EXP-0007_results.json` | 51-file read-only audit; corrected p50 replay; bootstrap count reconstruction; C7 classification | EXP-0006 p50/FSS exact; EXP-0007 p_c `0.500687453`, SE `0.031707449`, width draws 495/500 | **SUPPORTED, LIMITED** | EXP-0006 C1/C6 missing; EXP-0007 is not ±0.01 precision validation and width CI is broad |
| EXP-0008 / Q-M007 | `.../prime_gaps/RESULTS/EXP-0008_results.json` | corrected lower-prime 1e8 support-aware smoke; exact parity support; corrected BH/log tails | first exponential bin structurally empty; 12 historical hashes unchanged | **DESCRIPTIVE ONLY** | Parity/geometric surrogate is incomplete; Pearson/BH cells are dependent and not confirmatory |
| Q-M008 1e8/1e9 | `.../Q-M008/RESULTS/` | corrected 1e8 audit; segmented-sieve first-segment control; no scale rerun | first segment retains 5,761,455 primes; old normalization/BH/p-values invalid; 1e10 path not run | **DESCRIPTIVE ONLY** | No corrected 1e9/1e10 persistence or calibrated null result |
| EXP-0009 | `.../Q-P005_exponents/CODE/RESULTS/EXP-0009_results.json` and NPZ cells | exact stored-cache replay; C7 stream audit; R3 algebra audit | Stored exponents reproduce exactly; C7 uses first 40 same-stream cells; `P_inf=M_max/L^2` couples R3 to D_f | **REANALYZED / LIMITED** | C7 is implementation checking; R3 is not an independent scaling-law test |
| EXP-0010 | `.../Q-P005_exponents/CODE/RESULTS/EXP-0010_results.json` | exact pooled-slope replay; prereg/C7 availability audit | pooled D_f `1.896198±0.028436` reproduces; individual-size estimator and C7 absent | **INCONCLUSIVE** | Historical LATTICE_ARTIFACT closure not accepted; pooled proximity is exploratory |
| Q-P006 | `.../Q-P006/CODE/RESULTS/EXP-0009-precision_results.json` | SHA-256 comparison to Q-P005 NPZ files; raw tau reanalysis | all three cited cell files are byte-identical to Q-P005 files | **INVALID “NO CELLS REUSED” CLAIM** | Copy/provenance error; not independent precision replication |
| Q-P007 / N-001 | `.../Q-P007/CODE/RESULTS/EXP-0009-pc_results.json` | static audit; independent paired reanalysis; isolated flat-array SQLite + realization-bootstrap smoke | historical nested tail empty; corrected smoke round-trips 18 paired tails and reports `scientific_result=null` | **INVALID HISTORICAL / REPAIR SMOKE ONLY** | No production tau or refined-p_c conclusion |
| EXP-0011 | `.../percolation_3d/CODE/RESULTS/EXP-0011_pilot_results.json` | same-stream boundary reproduction; dimension-aware engine tests; corrected union-find C7 smoke | historical z=0 slice counts 33/1000 vs opposite-z 327/1000 at L=8; corrected smoke C7 4/4 | **INVALID HISTORICAL WIDTH/p_c/C7** | Stored exponents are exploratory; no corrected production result |
| EXP-0013 | 3D main prereg/config | no corrected production completion; old runner disabled | nominal log stops at L=256; no `EXP-0013_results.json` | **NOT COMPLETE** | Requires a new immutable, probit-width production config and corrected C7 |
| EXP-0014 z=2 | `.../feigenbaum_constants/CODE/.../EXP-0014_results.json` | isolated same-code rerun; independent arbitrary-precision continuation | z=2 delta8 `4.669060660648...`; all periods verified | **REPRODUCED** | Known Feigenbaum reproduction; historical higher-order branches invalid |
| EXP-0014 z=3/z=4 | same stored file | independent 100-digit first-rightward-root continuation | z=3 delta8 `6.084672065631...`; z=4 delta8 `7.285086100551...`; monotone/period-verified | **CONTRADICTS STORED OUTPUT** | Stored C3/C4/C6 pass claims are hardcoded/invalid |
| Q-M001 Collatz | `.../collatz/RESULTS/Q-M001_full_results.json` | static code/result inspection | full file contains 3 convergent families, not 27; max-step paths are labeled cycles without repeated-state detection | **CONTRADICTED / INCOMPLETE** | No iff claim |
| Q-S9-1/2/3 | `save_q9results.py`, `dose_response.py`, S9 reports | static writer/data-flow inspection | Q-S9-1/3 values hardcoded; Q-S9-2 synthesizes data from assumed Hill parameters | **NOT EMPIRICALLY REPRODUCED** | No independent dose/perception data |
| SQLite/05_DATA/archive | `sovereign_biolab.db`, `05_DATA`, `percolation.rar` | SQL table/count query; directory inventory; archive inspection | 21 empty tables; data directories empty; archive is a duplicate snapshot | **PROVENANCE LIMIT** | No independent raw-data basis |

## Reproduction commands and locations

- Baseline: `python -m pytest` from `C:\Users\natha\ScientificDiscoveryLab`.
- EXP-0007: `python 03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0007.py` in the isolated temporary tree; log at `AUDIT/INDEPENDENT_AUDIT_20260924/runs/percolation_exp0007.log`.
- EXP-0003 sub-audit: `python AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE/run_broadband_convergence.py --realizations 4 --skip-controls` and `--skip-main` (the latter initially failed with exit 255; corrected controls were run separately).
- Feigenbaum: `python AUDIT/INDEPENDENT_AUDIT_20260924/independent_feigenbaum_reanalysis.py`.
- Corrected tau: `python AUDIT/INDEPENDENT_AUDIT_20260924/corrected_tau_reanalysis.py`.
- Prime-gap repair: `python -m pytest "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/AUDIT_REPAIR_N06_N08/tests/test_audit_repair.py" -q`.
- Historical 2D provenance: `python -m pytest -q -p no:cacheprovider 03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/TESTS/test_read_only_audit.py`.
- Q-P007 N-001 repair tests: `python -m pytest -q 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/TESTS/test_n001_runner.py`.
- 3D repair tests: `python -m pytest -q tests/unit/test_perc_engine.py tests/unit/test_perc3d_runner.py`.
- RNG calibration: `python AUDIT/INDEPENDENT_AUDIT_20260924/rng_calibration_audit.py`.
- Corrected broadband controls: `python AUDIT/INDEPENDENT_AUDIT_20260924/broadband_controls_corrected.py`.

## Interpretation

The matrix separates four notions that prior reports often conflated:

1. byte-level determinism;
2. same-method raw-data reproduction;
3. independent implementation agreement;
4. external/literature corroboration.

Only the first is established for many historical outputs. The strongest independent results in this audit are the speckle law, the narrow-band vortex law, the EXP-0007 threshold rerun, the corrected Feigenbaum roots, and the resolution-convergence controls. The strongest negative findings are the Q-P007 cache bug, the invalid Q-P006 independence claim, the unsupported lattice artifact, the hardcoded S9 outputs, and the invalid RNG certificate.
