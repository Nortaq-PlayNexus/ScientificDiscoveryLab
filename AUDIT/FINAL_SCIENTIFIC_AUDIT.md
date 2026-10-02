# FINAL SCIENTIFIC AUDIT — ScientificDiscoveryLab

**Audit date:** 2026-09-24  
**Source:** `C:\Users\natha\ScientificDiscoveryLab`  
**Auditor mode:** independent, disconfirming, non-destructive  
**Historical preservation:** prior audit copied to `AUDIT/PRIOR_AUDIT_20260923/`; historical experiment outputs were not intentionally overwritten. Runs capable of writing results used an isolated temporary tree.

## Executive verdict

The laboratory contains a substantial amount of deterministic software and several useful controlled reproductions, but the prior audit’s overall confidence language is too strong. The evidence supports **reproductions of known laws and a small number of methodological findings**, not a portfolio of new discoveries.

The defensible conclusions are:

1. **Speckle contrast:** EXP-0002 reproduces the textbook `C(M)=1/sqrt(M)` law under the simulated independent-speckle model.
2. **Vortex density:** EXP-0003 reproduces the Kac–Rice/Nye–Berry prediction for resolved fields. A fixed-physical-spectrum convergence sweep shows that the broad-band deficit is strongly resolution/spectral-support dependent and shrinks toward one as pixels per wavelength increase.
3. **2D percolation thresholds:** EXP-0007 is byte-identically reproducible and compatible with the exact bond threshold, but its coarse uncertainty does not justify a precision claim.
4. **2D exponents:** the “power-of-two lattice artifact” diagnosis is not supported by independent, matched-size simulations. EXP-0009’s deviations are finite-sample/estimator deviations, not a new universality class.
5. **Q-P007:** the stored tau result is invalid because the cache is structurally nested and the tail is discarded. A corrected independent reanalysis finds only a tiny paired p_c effect at the tested sizes.
6. **3D percolation:** only a small pilot exists; the main run did not complete. No 3D result is closed.
7. **Prime gaps:** finite normalized gaps show strong dependence and scale-dependent variance. Rejection of a fixed-bin Exp(1) null is descriptive, not evidence of a novel process.
8. **Feigenbaum:** z=2 is reproduced. The historical z=3/z=4 sequences are invalid root selections; independent arbitrary-precision continuation produces period-verified monotone sequences.
9. **RNG:** the `CERTIFIED` decision is withdrawn. The pooled p-value calibration rule assumes independence that the implementation violates; fresh control-generator tests also show marginal calibration problems.
10. **Collatz and S9:** the broad “iff” Collatz claim is not established, and the S9 perception/dose outputs are hardcoded or synthetic rather than empirical findings.

No result in the audited tree supports a defensible claim of a new physical law or novel mechanism. The EXP-0003 resolution protocol is a potentially useful control study, but its exact novelty remains unresolved.

## Audit method

- Read the authoritative task file at `C:\Users\natha\Desktop\New Text Document.txt`.
- Preserved and treated prior reports as claims rather than ground truth.
- Inventoried files, JSON, Python, hashes, IDs, data directories, database tables, and archive contents.
- Ran the full test suite: `python -m pytest` → **287 passed**, 411 warnings, 26.60 s.
- Verified preservation by comparing 433 non-`AUDIT` baseline-file SHA-256 hashes: 0 changed and 0 missing.
- Re-ran selected experiments in an isolated copy and compared SHA-256/semantic outputs.
- Reanalyzed raw NPZ/prime/percolation data with independent NumPy/SciPy implementations.
- Ran artifact controls, negative controls, alternate detectors, and dependence diagnostics.
- Queried Crossref/OpenAlex/NIST metadata for literature and novelty checks.
- Logged commands, failures, environment, decisions, and discrepancies in `AUDIT/AUDIT_LOG.md`.

## Evidence grading

- **High:** independent implementation, raw-data reanalysis, and controls agree.
- **Medium:** deterministic rerun agrees but implementation is shared or sample size is limited.
- **Low:** documentation/report only, malformed cache, synthetic input, incomplete run, or missing provenance.
- **Invalid:** result cannot be regenerated or conflicts with a direct structural check.

## Findings by area

### A. Optics

#### EXP-0002 — supported reproduction

The independent direct complex-Gaussian and random-phase-pupil FFT tests over 255/256/257 and rectangular grids recover the square-root contrast law with ratios consistent with one. This is a known fully developed speckle result. It does not validate arbitrary optical systems, finite pixels, or correlated modes.

#### EXP-0003 — supported with a corrected resolution interpretation

Historical EXP-0003 reported narrow-band agreement and a broad-band near-Nyquist deficit. The isolated rerun is byte-identical. The independent broadband sub-audit held a physical Gaussian spectrum fixed while changing pixel pitch and tested P={4,6,8,12,16,24,32,48,64}, sigma={0.10,0.25,0.50,0.75}, six seeds, and four realizations per condition.

Representative ratios to the discrete-mode prediction:

| sigma | P=4 | P=8 | P=16 | P=32 | P=64 |
|---:|---:|---:|---:|---:|---:|
| .10 | 1.018 | 1.009 | 1.004 | 1.003 | .998 |
| .25 | .994 | .998 | 1.001 | 1.007 | .997 |
| .50 | .915 | .985 | 1.001 | .996 | .997 |
| .75 | .828 | .956 | .986 | .997 | .997 |

The broad-band deficit is therefore a finite-resolution effect in this protocol. Corrected direct-complex and low-pass controls reproduce the same direction. The sub-agent’s first interpolation control divided refined density by an extra factor of `P²`; after correcting that audit-only bug, refined ratios are near one. A synthetic winding test detects a regularized unit vortex; a contour test with the zero exactly on a grid vertex is degenerate and is not counted as a failure of random-field detection.

**Classification:** known-law reproduction plus a useful resolution/control result; not a confirmed novel physical effect.

### B. Percolation

#### Thresholds

EXP-0007’s isolated rerun is byte-identical (`a09e4f...52553b`). It yields a bond-wrap intercept `0.5006874530252672` with reported scale `0.03170744877268775`, p50 values from `0.49745` to `0.50122`, and C8 `1/nu=0.7255`. This is compatible with exact bond `p_c=1/2` but not a precision measurement.

#### Exponents and lattice artifact

Independent non-power-of-two and matched parity sequences give overlapping estimates around the known 2D exponent. The power/non-power contrast is about 0.97 SE, not evidence of lattice locking. EXP-0009’s raw reanalysis gives `D_f=1.8701±0.0223`, `gamma/nu=1.7594±0.0327`, and `beta/nu=0.1299±0.0223`; these are finite-sample deviations, not a new universality class.

Q-P006’s three raw cell files are byte-identical to Q-P005 despite the claim that no cells were reused. Q-P007’s cache stores nested arrays and cannot be reloaded (`KeyError: sizes`). Corrected independent tau reanalysis gives size-dependent values around 1.81–1.93 in small/medium boxes and only a `3.0e-5` paired p_c change at L=512. The historical tau conclusion is invalid.

#### 3D

The EXP-0011 pilot at L={8,16,24} is too small to validate 3D exponents. The main EXP-0013 run timed out at L=256 after the default runner selected the expensive configuration. No 3D closure is supported.

### C. Prime gaps

The 1e8 and 1e9 stored results reproduce semantically when runtime fields are ignored, and the C7 implementation agrees exactly. Independent reanalysis finds:

- lag-1/lag-2 dependence;
- variance changing across scales;
- a structurally impossible first normalized-gap bin;
- block-bootstrap and iid standard errors that differ materially.

The exact fixed-bin chi-square rejection is therefore a statement about a misspecified finite-range null. It is not evidence against the asymptotic Gallagher/PNT picture and is not a novel prime process.

### D. Feigenbaum constants

The z=2 sequence reproduces `delta_8≈4.669060660648268`. The independent 100-digit continuation verifies exact periods for z=2,3,4 and obtains:

- z=3 `delta_8≈6.084672065631017`;
- z=4 `delta_8≈7.285086100551313`.

The stored z=3 duplicate sequence and z=4 rollback are root-selection errors. The preregistration is invalid JSON, the canonical result directory is empty, and C3/C4/C6 pass fields are hardcoded or inconsistent. Higher-order historical claims are withdrawn; the corrected sequences are known-universality reproductions.

### E. RNG, Collatz, and S9

The RNG battery reuses the same stream arrays across many tests and then applies pooled KS/binomial/BH rules that assume independence. An 80-seed-per-generator audit found maximum p-value correlations near 0.99 and test-specific uniformity failures in both lab and control streams. The correct conclusion is “battery calibration unresolved,” not “generator bad” or “generator certified.”

The Collatz full file contains three convergent families, not a 27-family sweep, and the code labels max-step trajectories as cycles without repeated-state detection. The iff claim is not established.

Q-S9-1 and Q-S9-3 outputs are hardcoded by a writer; Q-S9-2 synthesizes observations from assumed Hill parameters. These are not empirical findings.

## Data and provenance conclusion

The SQLite database has 21 empty tables. `05_DATA` directories are empty. The RAR archive is a duplicate snapshot, not independent evidence. The repository has no commits and all files are untracked. Current SHA-256 manifests establish present bytes, not authorship or historical independence. External dossier claims cannot be checked from the supplied tree.

## Final claim disposition

| Area | Disposition |
|---|---|
| Speckle law | **Supported known-law reproduction** |
| Narrow-band vortex law | **Supported known-law reproduction** |
| EXP-0003 broadband deficit | **Finite-resolution artifact supported; novelty unresolved** |
| 2D bond/site thresholds | **Reproduction supported at finite precision** |
| 2D “lattice artifact” | **Not supported** |
| Q-P007 tau/refinement | **Historical result invalid; hypothesis unresolved** |
| 3D percolation | **Inconclusive** |
| Prime-gap deviation | **Descriptive finite-range result; no novel mechanism** |
| Feigenbaum z=2 | **Supported reproduction** |
| Feigenbaum z=3/z=4 historical output | **Contradicted; corrected independent sequence supplied** |
| RNG certification | **Withdrawn as invalid method claim** |
| Collatz iff/full sweep | **Not established** |
| S9 empirical claims | **Not reproduced; synthetic/hardcoded** |
| External R1–R8 | **Not verifiable from supplied files** |

## Required next action

Do not expand the claim registry or announce discoveries from the current tree. First execute the Priority 0 repairs in `NEXT_EXPERIMENTS.md`, beginning with Q-P007 storage/tau and Feigenbaum root selection. Preserve failed controls and raw outputs just as this audit preserved the original laboratory files. Treat a passing result as provisional until its raw-data chain, independent implementation, and dependence-aware uncertainty are documented.

### Repair progress — 2026-09-24

Q-P007 N-001 and the 3D opposite-plane/C7 infrastructure now have isolated,
fail-closed smoke repairs; neither authorizes a production scientific claim.
EXP-0003's 38 listed audit artifacts validate, preregistration/result-hash
infrastructure is hardened, application evidence-label defects are repaired,
and pytest no longer mutates the persistent database. The isolated prime-gap
repair now corrects normalization/BH/tail arithmetic and the segmented-sieve
first-segment bug, while retaining a descriptive-only classification. The
isolated Feigenbaum repair review is complete for finite period-verified
sequences; z=3/z=4 remain nonmonotone diagnostics and no alpha or convergence
claim is authorized. Canonical details are in
`AUDIT/REPAIR_LOG_20260924.md` and
`AUDIT/REPAIR_MANIFEST_20260924.json`.

## Primary audit outputs

- `AUDIT/PROJECT_INVENTORY.md`
- `AUDIT/CLAIM_REGISTRY.md`
- `AUDIT/REPRODUCTION_MATRIX.md`
- `AUDIT/BUGS.md`
- `AUDIT/NOVELTY_REVIEW.md`
- `AUDIT/NEXT_EXPERIMENTS.md`
- `AUDIT/REPAIR_LOG_20260924.md`
- `AUDIT/AUDIT_LOG.md`
- `AUDIT/INDEPENDENT_AUDIT_20260924/independent_static_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/independent_optics_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/independent_percolation_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/percolation_reanalysis_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/corrected_tau_reanalysis_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/independent_feigenbaum_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/rng_calibration_results.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/broadband_controls_corrected_results.json`
- `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/`
- `03_INVESTIGATIONS/OPTICS/vortex_density/REPORT/AUDIT_ADDENDUM_EXP-0003_20260924.md`
