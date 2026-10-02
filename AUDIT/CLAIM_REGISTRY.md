# CLAIM REGISTRY — Independent Scientific Audit

**Audit date:** 2026-09-24  
**Evidence rule:** historical reports are claims; a claim is upgraded only when its raw artifact, code path, controls, and an independent or isolated rerun are inspected.

## Classification key

- **REPRODUCED:** isolated rerun and/or independent implementation agrees with the stated result.
- **SUPPORTED, LIMITED:** direction is supported, but scope/uncertainty is narrower than the historical wording.
- **DESCRIPTIVE ONLY:** observed finite-sample statistic is real; mechanism, asymptotic claim, or novelty is not established.
- **CONTRADICTED:** independent evidence or a reproducible implementation defect conflicts with the claim.
- **INVALID:** the stored result cannot be regenerated or the estimator/data structure is structurally wrong.
- **INCONCLUSIVE:** evidence is insufficient or the planned scale was not completed.
- **NOT VERIFIABLE:** required source/raw data are outside the audited tree.

## Registry

| ID | Historical claim / target | Evidence examined | Classification | Defensible wording |
|---|---|---|---|---|
| C-001 | EXP-0001 shared engine behaves as specified; 14/14 infrastructure checks pass | `python -m pytest` 287 passed; infra report | **REPRODUCED (software only)** | The tested software routines are deterministic under the recorded environment; this is not evidence that scientific models are correct. |
| C-002 | EXP-0002 speckle contrast obeys `C(M)=1/sqrt(M)` | Historical result; independent PCG64 direct-Gaussian and pupil-FFT tests on 255/256/257 and rectangular grids; byte-identical isolated rerun | **REPRODUCED** | The textbook law is reproduced for the simulated fully developed independent-speckle model; it is not a claim about arbitrary real optical systems or a novel law. |
| C-003 | EXP-0003 vortex density equals Kac–Rice/Nye–Berry in resolved fields | Historical N=256/512/1024 cells; independent non-square/non-power-of-two tests; fixed-physical-spectrum P=4,6,8,12,16,24,32,48,64 sweep; corrected low-pass/interpolation/direct-complex controls | **SUPPORTED, LIMITED** | The prediction is recovered for resolved fields. The broad-band deficit is a finite-resolution/spectral-support/detector effect in the tested protocol; it is not evidence for a new physical density law. |
| C-004 | EXP-0004 lab RNG is “CERTIFIED” by the pooled battery | Static code review; 80 fresh seeds x 24 p-values for G_LAB, G_PCG, G_MT; marginal per-test calibration | **CONTRADICTED / METHOD INVALID** | The streams show no lab-specific failure in this audit, but the pooled KS/binomial/BH decision is not a valid certificate because p-values share the same bit stream and some test marginals fail on controls as well. No cryptographic or NIST certification follows. |
| C-005 | EXP-0005/0006/0007 2D bond/site thresholds agree with anchors | 51-file read-only provenance audit; stored EXP-0006 p50/FSS regenerate exactly; EXP-0007 p_c=0.500687453 with SE=0.031707449 | **SUPPORTED, LIMITED; control/provenance closure INCONCLUSIVE** | Aggregate threshold point estimates are recoverable and compatible with anchors. EXP-0006 lacks required C1/C6 evidence and a complete current runner; EXP-0007 is not ±0.01 precision validation and its width CI is broad. |
| C-006 | EXP-0010 proves a power-of-two lattice artifact | Independent sequences; exact pooled Df regeneration; preregistered per-size estimator and C7 are absent | **CONTRADICTED / INCONCLUSIVE closure** | The pooled non-power slope is exploratory. No accepted power-of-two lattice-locking mechanism or per-size closure is established. |
| C-007 | EXP-0009/0010 reproduce 2D exponents and resolve the anomaly | Exact NPZ exponent regeneration; C7 uses identical streams; R3 is algebraically coupled; EXP-0010 pooled fit only | **SUPPORTED, LIMITED / historical resolution NOT accepted** | Stored exponent estimates regenerate, but same-stream C7 and coupled R3 add no independent evidence. EXP-0010's preregistered closure and Q-P007 tau branch are unresolved/invalid. |
| C-008 | Q-P007 refined `p_c` explains tau/exponent deviations | Static nested-cache audit; `KeyError: sizes`; corrected independent paired p_c/tau reanalysis; N-001 flat-array/realization-bootstrap repair smoke | **INVALID historical result / INCONCLUSIVE refinement hypothesis** | The stored tau cannot be used. Corrected infrastructure smoke has `scientific_result=null`; no production Fisher-value or refined-p_c conclusion exists. |
| C-009 | EXP-0011/0013 validates 3D percolation exponents | Same-stream reproduction shows the 3D runner checked a z=0 slice rather than opposite z planes; sample counts/truncation/tau storage also fail; main EXP-0013 absent | **INVALID historical width/p_c/C7; exponents exploratory; overall INCONCLUSIVE** | Corrected opposite-plane infrastructure and C7 smoke pass, but no corrected production 3D p_c or exponent result exists. No 3D closure is supported. |
| C-010 | EXP-0008/Q-M007/Q-M008 prime gaps show a novel deviation from Poisson | Corrected lower-prime 10^8 smoke; exact parity support; corrected step-up BH/log tails; segmented-sieve controls; dependence limits | **DESCRIPTIVE ONLY** | The first fixed exponential bin is structurally empty. The remaining continuous/parity screens are not dependence-calibrated prime-process nulls; no novel mechanism is established. |
| C-011 | EXP-0014 z=2 Feigenbaum constant and higher-order z=3/4 claims | Invalid preregistration; historical runner root-selection failure; independent 100-digit continuation | **z=2 REPRODUCED; historical z=3/z=4 CONTRADICTED** | z=2 `delta_8≈4.66906` is reproduced. Correct period-verified values are z=3 `delta_8≈6.08467` and z=4 `delta_8≈7.28509`; the stored duplicate/reversed sequences and hardcoded C3/C4/C6 passes are invalid. |
| C-012 | Collatz convergence iff `a=b=c`; 27-family full sweep | Result file contains three convergent families plus five N=1000 pilots; code marks every max-step path as a cycle | **CONTRADICTED / INCOMPLETE** | The three tested equal-parameter families converge in the recorded run. The claimed iff statement and full 27-family sweep are not established by the supplied result/code. |
| C-013 | Q-S9-1 threshold, Q-S9-2 dose response, Q-S9-3 detector correction are empirical discoveries | `save_q9results.py` hard-codes Q-S9-1/3 values; Q-S9-2 synthesizes Hill data; no measured dose data | **INVALID / NOT REPRODUCED** | These are software-generated or assumed-parameter outputs, not independent empirical findings. |
| C-014 | Q-M008 deviation persists to 1e9 and proves a new prime process | Stored 1e8/1e9 outputs; corrected 1e8 support-aware audit; unsafe 1e10 sieve not run | **DESCRIPTIVE ONLY** | No corrected scale-persistence or scientific-null result exists. The old normalization/BH/p-value and segmented-sieve paths are not valid evidence. |
| C-015 | External dossier R1–R8 results are laboratory-verified | External source paths/results are referenced but absent from `ScientificDiscoveryLab` | **NOT VERIFIABLE** | No independent reproduction or provenance check is possible from the supplied tree. |
| C-016 | Historical registries and status files accurately represent completed work | File/ID inventory; empty data/database; identifier collisions; malformed/empty caches | **CONTRADICTED as a provenance record** | Registry labels are useful navigation, not authoritative evidence of execution, independence, or scientific validity. |

## Quantitative evidence highlights

### EXP-0003 resolution sweep

Using the sub-agent’s fixed physical spectrum and six seeds x four realizations per condition (`n=24` per cell), representative ratios to the discrete-mode Kac–Rice prediction are:

| `sigma_k` | P=4 | P=8 | P=16 | P=32 | P=64 |
|---:|---:|---:|---:|---:|---:|
| 0.10 | 1.0183 | 1.0091 | 1.0041 | 1.0027 | 0.9980 |
| 0.25 | 0.9935 | 0.9984 | 1.0007 | 1.0069 | 0.9975 |
| 0.50 | 0.9146 | 0.9854 | 1.0007 | 0.9957 | 0.9971 |
| 0.75 | 0.8285 | 0.9557 | 0.9865 | 0.9966 | 0.9966 |

The strongest deficit is therefore at broad width and low P. Corrected Fourier refinement no longer collapses the density (the sub-agent’s first implementation incorrectly divided refined density by `factor**2`); corrected low-pass and direct-complex controls support a finite spectral-support/sampling explanation. The synthetic winding sanity test detects one regularized unit vortex; the contour detector returns zero when the exact vortex zero lies on a grid vertex, so that particular contour sanity test is not diagnostic.

### EXP-0014 corrected roots

The independent arbitrary-precision run verifies exact first returns for every tested `n=2…8`:

- z=2: `delta_8=4.669060660648268...`
- z=3: `delta_8=6.084672065631017...`
- z=4: `delta_8=7.285086100551313...`

All three sequences are strictly increasing and all period checks pass. This directly contradicts the historical z=3 duplicate sequence and z=4 rollback.

### RNG fresh-seed calibration

Eighty fresh seeds per generator produced 1,920 p-values per generator. G_LAB pooled KS `p=0.3446`; G_PCG `p=0.5372`; G_MT `p=0.1120`. However, p-value correlation has maximum absolute off-diagonal correlation about `0.99` for each generator, with 18–20 pairs above 0.3. Several individual test marginals reject uniformity (for example G_LAB runs-test KS `p≈0.00041`; G_MT runs-test `p≈0.00173`). The result is a battery-method/dependence problem, not evidence that G_LAB is uniquely defective.

## Evidence files

- `AUDIT/INDEPENDENT_AUDIT_20260924/independent_static_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/independent_optics_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/independent_percolation_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/percolation_reanalysis_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/corrected_tau_reanalysis_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/independent_feigenbaum_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/rng_calibration_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/broadband_controls_corrected_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/prime_gap_reanalysis_results.json`
- `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/` (raw sweep, logs, literature search, and failed first control run)
