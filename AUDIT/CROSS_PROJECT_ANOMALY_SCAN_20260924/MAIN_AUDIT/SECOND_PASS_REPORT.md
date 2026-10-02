# Second-Pass Cross-Project Anomaly Report

**Audit date:** 2026-09-24  
**Scope:** whole repository, with emphasis on cross-project scientific logic, result provenance, controls, tests, and application-layer claims.  
**Policy:** historical experiment files were not edited. All reproductions below are isolated/read-only or use temporary paths.

## Executive conclusion

The first audit correctly found several isolated invalid claims. This second pass found a more fundamental pattern: **several “independent” controls reproduce the same implementation mistake, several decision rules are not actually wired to their controls, and several result files are not regenerable from the runner named in their reports.**

The most serious new finding is in 3D percolation:

> `perc_engine.spanning_flags()` is a 2D boundary routine used with 3D labels. It checks a `z=0` slice against a row inside that slice instead of checking opposite 3D planes. At `p=0.3116079`, the current code counted 33 vertical spans in 1,000 trials at `L=8`; a direct opposite-z-plane check on the same fields counted 327. The 3D width curves, p_c extrapolation, and the claimed C7 validation are therefore not valid 3D spanning measurements.

This does not prove the 3D exponents are wrong, but it invalidates the pilot’s p_c/control narrative and makes the 3D experiment decisively **inconclusive**, not merely “pending.”

## Finding table

| ID | Severity | Finding | Effect on prior claims |
|---|---|---|---|
| N-01 | **Critical** | 3D `spanning_flags()` uses 2D indices on `L^3` labels | 3D width/p_c and C7 claims invalid; C-009 remains inconclusive |
| N-02 | **High** | 3D runner silently reduces width samples, truncates exponent samples, hardcodes an absent tau size, and creates empty tau tails | Pilot/main 3D statistics not interpretable as reported |
| N-03 | **High** | `EXP-0011_results.json` is a semantic copy of the pilot; no completed main result exists | Main 3D result was never produced |
| N-04 | **High** | EXP-0006’s named runner contains a wrong p50 denominator and a literal C2 pass; stored result does not regenerate from it | EXP-0006 provenance/control claim contradicted; stored estimate not automatically disproved |
| N-05 | **Medium** | EXP-0007 reports 500 bootstrap draws but silently keeps only 495 converged draws; FSS SE is 3.17× the 0.01 gate | H0-compatible point estimate, not a precision validation |
| N-06 | **High** | Q-M008 uses upper-prime normalization, a non-step-up BH implementation, and `1-CDF` p-values | Q-M008 scale/“persistence” result is descriptive at best |
| N-07 | **High** | Q-M008 `run_1e10.py` drops primes in the first sieve segment | Planned 10^10 path would be catastrophically incomplete |
| N-08 | **High** | Q-M007’s 40-cell p-values use a wrong Wilson–Hilferty exponent and an extra factor 1/2 | Shape means remain descriptive; stored p-values/FDR evidence invalid |
| N-09 | **Medium/High** | Speckle and vortex bootstrap “p-values” have an artificial machine-epsilon floor and are not calibrated null tests | Core C(M) law can remain supported; FDR/p-value claims cannot |
| N-10 | **Medium/High** | Speckle report claims C6/C7/C8 controls that are omitted, mislabeled, or not connected to the decision | EXP-0002 control-completeness claim is overstated |
| N-11 | **High** | `freeze_config()` overwrites an existing “immutable” preregistration on every rerun | Before/after prereg provenance is not enforceable |
| N-12 | **Medium** | S9 reports are internally inconsistent: non-monotonic rates, assumed parameters stored as fitted values, and relative-vs-absolute inflation units | S9 remains invalid, with additional report-level errors |
| N-13 | **Medium** | Application code labels partial charge as formal charge, upgrades unknown reactions to E3 potential interactions, and has a broken 2D depiction call | Molecular/reaction outputs cannot be treated as reliable scientific measurements |
| N-14 | **Low/Medium** | `result_hash` fields do not provide a consistent artifact-byte integrity check | Metadata cannot independently prove which result object was hashed |
| N-15 | **Medium** | EXP-0015 is simultaneously claimed by two different water-response projects, and the advertised implementation/results are absent | Future automated retrieval cannot identify a real EXP-0015 artifact |
| N-16 | **Low/Medium** | The EXP-0003 sub-agent artifact hash manifest is malformed JSON because it ends with a literal `\\n` | The audit’s own completeness/integrity check is not fully valid |
| N-17 | **Medium** | The passing pytest suite mutates the persistent SQLite database | “Tests pass” is not a read-only integrity guarantee |
| N-18 | **Low/Medium** | Historical EXP-0003 complex-field construction carries a factor-of-two power normalization defect | Absolute field-power claims are invalid; density ratios are unchanged because amplitude cancels |
| N-19 | **Medium** | EXP-0009 C7 uses identical frozen streams and is an implementation check, not fresh sampling | Do not count C7 as independent experimental evidence |
| N-20 | **High** | EXP-0008/Q-M007’s first prime-gap bin is mathematically impossible under the stated normalization | The apparent empty-bin anomaly is structural, not a novel distributional effect |
| N-21 | **Medium** | EXP-0009 R3 is algebraically coupled to the same mass realizations used for D_f | R3 is an internal consistency check, not an independent scaling-law test |
| N-22 | **High** | EXP-0010 applies one pooled D_f fit to a preregistered all-non-power-of-two gate and omits C7 | The lattice-artifact claim cannot close under its own protocol |
| N-23 | **High** | Q-M007 has a hardcoded audit writer that contradicts the later 38/40 report | Q-M007 “verification” language is not self-authenticating |
| N-24 | **High** | Q-P007 has colliding writers, hardcoded phase-1 p_c inputs, and a no-op 1/nu branch | The refined-p_c closure is not independently reproducible |
| N-25 | **High** | Registry/status records, Git chronology, and the advertised central data stores are not authoritative | Completion/identity claims cannot be inferred from filenames or status files |

## Cross-cutting pattern: “independent” often means only a second code path

The most important birds-eye pattern is not a single arithmetic typo. It is a control-design mismatch:

- EXP-0006/0007 percolation C7 checks reimplement the **same seeded streams** and compares counts to the stored result. That is useful for catching implementation drift, but it is not an independent Monte Carlo sample.
- The 3D C7 checker repeats the same incorrect boundary convention as the primary engine, so agreement is guaranteed on the disputed quantity.
- EXP-0004 C7 recomputes only five of the 24 battery p-values, then substitutes them into the full pooled decision; it is not a full independent battery.
- EXP-0002’s independent direct-Gaussian route is not consumed by the primary decision.
- EXP-0003’s broadband sub-agent shares the corrected detector across most controls; only the direct-complex construction is a genuinely separate field route.

These controls should be labelled **implementation cross-checks** unless they also use independently generated streams, raw data, and a separately specified estimand. Treating them as independent scientific replications overstates the evidence.



**Code:** `03_INVESTIGATIONS/PHYSICS/percolation/ENGINE/perc_engine.py:226-251`

`spanning_flags()` creates `rows` and `cols` of length `L^2` and applies them to a label array of length `N=L^3` when used by the 3D runner. The selected “top” indices are the first `L` entries and the selected “bottom” indices are within the first `L^2` entries. They are not the two opposite z planes.

**Independent same-stream reproduction** (`MAIN_AUDIT/second_pass_evidence.json`):

| L | current slice vertical | correct opposite-z vertical | current slice horizontal | correct full-volume x |
|---:|---:|---:|---:|---:|
| 8 | 33/1000 | 327/1000 | 28/1000 | 316/1000 |
| 16 | 14/1000 | 287/1000 | 12/1000 | 284/1000 |
| 24 | 9/1000 | 288/1000 | 4/1000 | 290/1000 |

The independent 3D checker also says it checks only the `z=0` plane, so it repeats the same convention. Its bit-identical agreement is therefore **not** an independent validation of the intended 3D boundary.

**Impact:** width-curve crossings, the reported p_c values (`0.418`, `0.365`, `0.333`), the 1/L extrapolation (`0.297`), and “C7 passed” cannot be interpreted as 3D percolation results. Cluster-size exponent code does not use this boundary function, so the mass/chi estimates are not automatically invalid; they remain separately underpowered and sample-truncated.

**Repair:** make the spanning routine dimension-aware and test a known path connecting opposite z planes but not the slice-row boundary. Do not accept a C7 result until the checker uses the corrected boundary independently.

## N-02 — 3D runner sample and tau wiring defects

**Runner:** `03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py`

1. `width_curve_L()` uses `max(4, n_each // 10)` instead of the configured `n_each`:
   - pilot configured/effective width samples: L8 `300/30`, L16 `200/20`, L24 `100/10`;
   - main configured/effective: L128 `10/4`, L256 `5/4`, L512 `10/4`.
2. Exponent fitting truncates all sizes to `min_n`:
   - pilot `n_real={500,200,50}` is fitted using only 50 per size;
   - main would use only 100 per size instead of `{1000,500,100}`.
   The result JSON still reports the original `n_real`, hiding the effective sample size.
3. The main preregistration has `L={128,256,512}` but `tau_L=24`; the runner hardcodes `tL=24`, so a completed main run would index a missing `cells[24]`.
4. Each one-realization call returns `cluster_sizes=[array]`; the runner appends that list as one realization and later executes `ss[1:]`. Every tail is empty. The pilot’s stored tau is `null`, confirming the structural failure.

**Repair:** use configured sample counts, report effective aligned counts, derive `tau_L` from the active config, store one flat cluster-size array per realization, and add a nonempty-tail round-trip test.

## N-03 — 3D main result is a pilot copy

`CODE/RESULTS/EXP-0011_results.json` and `EXP-0011_pilot_results.json` are semantically identical after removing only the elapsed-time field. The nominal main log starts with `L_list=[128,256,512]` and stops during the L=256 width curve; no `EXP-0013_results.json` exists.

This is a provenance collision, not a completed main run. The plain report’s “main pending” status is directionally honest, but any automated consumer that sees `EXP-0011_results.json` can easily mistake the pilot copy for a main artifact.

## N-04 — EXP-0006 named runner cannot regenerate its stored result

**Runner:** `03_INVESTIGATIONS/PHYSICS/percolation/CODE/run_percolation_exp0006.py:51-64`

The interpolation denominator is literally `w1 - p0`; the correct denominator is `w1 - w0`. Re-evaluating the stored cells with the current expression gives, for example:

- bond-span L64: `0.79657` versus stored `0.49985`;
- bond-wrap L32: `0.60913` versus stored `0.49859`;
- site-span L256: `0.47934` versus stored `0.59247`.

The stored p50 values are consistent with a different/corrected calculation, not the named current runner. The runner also sets C2 to `pass=True` with `pair_diff=0.0` because it subtracts the same value from itself while explicitly not rerunning the second estimator (`run_percolation_exp0006.py:290-295`). In addition, its `run_cell()` raises for every system except `bond_span` while `main()` iterates all three configured systems, so the current file cannot be the complete generator of the stored three-system result.

**Classification:** the stored EXP-0006 estimate is not automatically falsified; its generation provenance and current reproducibility are defective. Re-run from raw cells with an explicit, versioned generator before citing it as a fresh result.

## N-05 — EXP-0007 silently drops bootstrap draws

The preregistration requests 500 width-bootstrap draws. `build_exp0007_summary.py:104-117` skips any draw for which a probit fit reports non-convergence and returns `n_draws=495` in `EXP-0007_summary.json`. The report still says “500 draws” (`TECHNICAL_EXP-0007.md:68-70`).

The stored FSS standard error is `0.031707`, while the decision tolerance is `0.01`; the point deviation is only `0.000687`. The current gate passes on the point estimate, but the uncertainty is more than three times the tolerance. The correct wording is “estimate compatible with 0.5 under a broad uncertainty,” not a precision reproduction at ±0.01.

## N-06/N-07 — Q-M008 numerical path

**Code:** `03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/CODE/run_exp0012.py`

- The report says gaps are normalized by the lower prime, but line 48 uses `log(primes[1:])` (upper prime). For `[3,5,7,11]`, the first code value is `1.24267`; lower-prime normalization gives `1.82048`.
- `bh_fdr()` marks each rank independently instead of propagating a later qualifying rank backward. The counterexample `[0.009,0.008]` is rejected by the implementation as `[True,False]` but correctly rejected by step-up BH as `[True,True]`.
- `chi2_goF()` computes `1 - chi2.cdf(...)`; at the stored 10^8 chi-square (`868281`, 9 df) the stored p-value is exactly `0.0`, while high-precision log-survival is about `-188526` in log10. Exact zero is a numerical/cancellation artifact, not a measured p-value.
- `run_1e10.py:55-64` marks the first multiple of every base prime starting at zero. It therefore marks the primes themselves in the first segment. A small test (`limit=1000`, one segment) returns 157 primes instead of 168. At the planned 10^10 scale this would discard the entire first 10^8-number prime segment.

The existing Q-M008 conclusion should remain **descriptive only**. The scale comparison, exact p-values, and planned 10^10 path all need replacement code and a fresh preregistered analysis.

## N-08 — Q-M007 p-values are malformed

`Q-M007/compute_bhfr_40cell.py:47-49` uses a Wilson–Hilferty-like exponent of `1/6`, multiplies by the correction term instead of subtracting it, and multiplies `erfc` by `0.5`. The standard transform uses a cube root (`1/3`) with the correction subtracted, and the chi-square upper tail is not represented by this two-sided-normal expression.

For cell (bin 1, block 1), the stored p-value is `2.05e-7`; the exact chi-square survival probability is about `7.27e-184`. Interestingly, an exact BH step-up calculation still happens to retain 38/40 cells, so the qualitative count is not automatically destroyed. The stored p-values, rankings, and any fine-grained significance interpretation are nevertheless invalid. The report’s per-bin mean residuals may remain descriptive; the “38/40 measured FDR result” wording is too strong.

## N-09/N-10 — Speckle and vortex statistics

### Bootstrap p-values are not calibrated p-values

Both optics runners use:

```text
p = 2 * min(bootstrap_tail_above_1, bootstrap_tail_below_1)
p = p + machine_epsilon
```

The empirical bootstrap has finite resolution; adding `2.22e-16` creates artificial exact-epsilon floors. The stored EXP-0002 result has one such floor and EXP-0003 has eight. A 2,000-dataset null calibration of the same formula at 32 blocks gives a nominal 0.01 rejection rate of about 0.021 and a nonuniform p-value distribution.

This does not erase the direct `C(M)=1/sqrt(M)` result, because the primary CIs and independent direct-Gaussian calculation support the core law. It does invalidate treating the p-values/FDR as calibrated inferential evidence.

### Controls are not all implemented or wired

- `run_speckle_contrast.py` freezes controls C1–C5 and C7, but the preregistration omits C6 and C8 even though `CONTROLS.md` and the report list all eight.
- The “C7 ensemble-vs-space” code computes an interior ROI contrast, not an ensemble-versus-space estimator.
- The independent replication result is not read by the decision rule.
- FDR flags are calculated but not part of the decision.
- The KS check samples 20,000 pixels from one spatially correlated speckle realization and treats them as an i.i.d. sample.

The core simulation result remains supported; the “all controls passed” statement must be downgraded to “several controls were run, with known scope/statistical limitations.”

## N-11 — “Immutable” preregistration is overwritten

`04_SHARED_ENGINE/engine/hypothesis_testing/prereg.py:27-46` says a config is immutable, but `freeze_config()` unconditionally opens the existing path with `"w"`. EXP-0002, EXP-0003, and EXP-0004 runners call it at the beginning of every run.

An isolated two-call demonstration changed the file hash and replaced parameters `{x:1}` with `{x:2}` while preserving the same path. This does not prove the historical parameters were changed, but it means the repository cannot enforce preregistration-before-results. A rerun can silently rewrite the preregistration and timestamp.

**Repair:** fail closed if the path exists; write a content-addressed preregistration once; require a signed/hash-locked change log for amendments.

## N-12 — S9 report-level contradictions

These findings do not rehabilitate S9; they show additional errors beyond the already confirmed hardcoded/synthetic provenance.

- The Q-S9-1 rates, sorted by increasing complexity, are `0.0517, 0.0517, 0.0617, 0.0567, 0.195`. The report says the relationship is monotonic, but 0.05 → 0.10 decreases.
- `dose_response.py` fits `popt`, but writes `TRUE_EC50`, `TRUE_HILL`, `MAX_INFL`, and `BASELINE` into the JSON. Fitting the stored synthetic points gives approximately `[32.608, 1.745, 0.513, 0.2005]`, not the stored assumed `[30, 2, .483, .205]`.
- The code treats `max_inflation=0.483` as an absolute rate increment, while the report calls it a 48.3% relative increase. With baseline 0.205, the formula saturates at 0.688, a 235.6% relative increase; a true 48.3% relative increase would saturate near 0.304.
- The Q-S9-1 report cites `q_s9_1_complexity.py`, but that reproduction script is absent.

## N-13 — Non-experiment application errors

These do not change the physics audit, but they matter to a whole-repository claim of validated software.

- `src/molecular/engine.py:76-83` returns `Descriptors.MaxAbsPartialCharge` under the field name `formal_charge`. Ethanol is reported as `0.3966637`; RDKit’s actual formal charge is `0`.
- `src/reaction/mixer.py:29-56` maps an `UNKNOWN`/E0 reaction analysis to `POTENTIAL_INTERACTION`/E3 for valid dissimilar molecules, inflating evidence without a reaction rule.
- `MoleculeInspector.get_2d_structure()` calls `GenerateDepictionMatching2DStructure(self.mol)` with a signature that fails on the installed RDKit; the call raises `Boost.Python.ArgumentError`.
- `tests/unit/test_plant_engine.py:49` contains `assert ... or True`, a tautology. No test covers the formal-charge, depiction, or evidence-escalation paths above.

## N-14 — Result hash semantics

`make_experiment_json()` hashes a serialized in-memory result object, not the exact result file bytes. For EXP-0002 and EXP-0003, the recorded hash matches neither the exact result-file SHA-256 nor the canonical hash of the loaded config result object. This may be rerun drift or serialization history, but it means `result_hash` is not currently a reliable artifact-integrity check without a documented canonicalization/version rule.

## N-15 — EXP-0015 is a phantom/colliding investigation

The repository contains two different water-response projects:

- `03_INVESTIGATIONS/ACOUSTICS/water_sound_response/` allocates `EXP-0015` to a six-module acoustics simulator, but the directory contains only planning documents and `experiment.json`; the README-advertised `CODE/`, `RESULTS/`, `CONFIG/`, and `REPLICATION/` artifacts are absent.
- `03_INVESTIGATIONS/FLUID_DYNAMICS/water_sound_response/` also calls itself `EXP-0015` and says its preregistration is frozen, but it contains only `README.md` and `QUESTION.md`.
- The root `EXPERIMENT_REGISTRY.md` has no EXP-0015 entry.

This is not evidence of a failed physical result; it is an incomplete/colliding project scaffold. It should be assigned a unique ID or explicitly marked as a proposal before any automated status or claim search treats it as an experiment.

## N-16 — New audit artifact manifest is malformed

`AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/RESULTS/artifact_hashes.json` parses as JSON up to the closing brace and then contains the literal two-character sequence `\\n` after it. `json.loads()` fails with “Extra data.” The scientific result files are still readable, but the sub-agent’s own artifact-integrity manifest is not a valid JSON document. This is a new audit-provenance defect, separate from the historical experiment files.

## N-17 — The green test suite mutates persistent state

Running `python -m pytest` changed `sovereign_biolab.db` from the baseline SHA-256 `e7dfc79c...` to `1d925f3b...`, even though every table was empty before and after. The database was restored from the preserved isolated baseline copy after the test run. The test suite therefore has a filesystem side effect (SQLite page/journal state) and is not a pure validation operation. A future test run can invalidate artifact hashes or contaminate a supposedly empty raw-data store.

## N-18 — EXP-0003 historical power normalization

The EXP-0003 sub-agent’s final calibration found that historical `complex_field()` passes `S/2` into a routine that itself applies another `sqrt(S/2)` factor. The measured complex-field power is about `0.5004` of the requested target. This is a genuine absolute-power defect, but global amplitude cancels from `n_measured/n_predicted`; it does not explain or rescue the broadband density result. The self-conjugate Hermitian-mode variance defect is also real but negligible for the tested spectra. These should be fixed before any future claim involving field intensity or power.

## N-19 — EXP-0009 C7 is not independent sampling

`Q-P005_exponents/REPLICATION/independent_check_exp0009.py` explicitly uses the identical G_LAB labels/seeds and first 40 realizations as the primary engine. Its union-find implementation is genuinely different, and the per-realization mass/chi comparisons are useful implementation checks, but the data are not fresh. The C7 PASS must not be counted as an independent exponent replication or used to remove shared-stream dependence.

## N-20 — The first EXP-0008 prime-gap bin is structurally empty

For the stated odd-prime blocks, every normalized gap obeys

```text
delta = (p[i+1] - p[i]) / log(p[i]) >= 2 / log(10^8)
       = 0.10857362047581294.
```

The first exponential-quantile edge is `0.10536051565782628`. Therefore the first bin cannot contain any tested gap, yet the Exp(1) reference assigns roughly one tenth of each sample to it. The resulting empty bin and enormous residual are a support/bin-edge mismatch, not evidence for a new prime process. This independently invalidates the Q-M007 “minimum-gap effect” and strengthens the descriptive-only classification of EXP-0008.

## N-21 — EXP-0009 R3 is not an independent scaling test

`P_inf = M_max/L^2` is computed from the same mass realizations used to fit `D_f`, and `beta/nu` is defined as the negative slope of that same `P_inf` sequence. The stored R3 residual (`~0.000757`) therefore tests algebraic consistency, not an independent observable or physical scaling relation. It should remain an internal diagnostic rather than a supporting exponent gate.


## N-22 — EXP-0010 does not execute its preregistered non-power-of-two gate

The EXP-0010 preregistration requires a D_f result within tolerance at the individual non-power-of-two sizes and requires C7. The current runner computes one pooled D_f slope, stores only C1, and leaves the preregistered 1/nu loop as a no-op. The historical “LATTICE_ARTIFACT” conclusion therefore cannot be accepted as a closed test; it is an exploratory pooled result.

## N-23 — Q-M007’s audit writer is hardcoded and contradictory

`save_audits.py` contains no JSON-loading dependency for the Q-M007 result. It writes a literal “VERIFIED — H1_SUPPORTED CONFIRMED” artifact and a literal caveat that the 40-cell BH-FDR was not applied, while the later technical report says 38/40 survived BH-FDR. The contradiction is preserved as evidence, not resolved by a supersession record.

## N-24 — Q-P007 has writer/cache collisions beyond the tau bug

There are two writers targeting the same result path. The first requests engine keys (`chis`, `pinfs`, `sizes`) that the engine does not return; the second uses literal phase-1 p_c values/uncertainties and leaves a preregistered 1/nu branch empty. This means the apparent refined-p_c resolution cannot be regenerated from one canonical pipeline.

## N-25 — Registry, Git, and central data stores are not authoritative

The claims/data scan found all 21 SQLite tables empty, the advertised central raw/result stores empty, zero Git commits with project files untracked, registry/status disagreements, and an external dossier pointing to a sandbox outside this tree. These are not proof that every local result is false, but they prevent completion, identity, or chronology claims from being inferred from registry text alone.

## What still stands after this pass

- The narrow-band EXP-0003 Kac–Rice/Nye–Berry result remains supported within the tested scope.
- The EXP-0002 speckle law remains a valid reproduction of the ideal independent-speckle model, with the p-value/control caveats above.
- EXP-0007’s threshold point estimate is compatible with 0.5, but its uncertainty is broad and the reported 500-draw bootstrap is actually 495 accepted draws.
- The historical Q-M007/Q-M008 prime-gap findings remain descriptive finite-range deviations, not evidence of a new process.
- EXP-0004 remains not certified; the second pass independently reproduces p-value correlations near 0.995.
- Collatz, Feigenbaum z=3/4, and S9 claims remain withdrawn/invalid for the reasons in the first audit, with the additional Q-M007/Q-M008/S9 defects here.

## Reproduction commands

```powershell
python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/MAIN_AUDIT/second_pass_evidence.py
python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py
python -m pytest
```

The repository test suite still reports **287 passed / 411 warnings**. That confirms the existing unit suite did not catch the findings above; it is not evidence that the scientific runners or controls are correct.

Machine-readable evidence:

- `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/MAIN_AUDIT/second_pass_evidence.json`
- `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py`
- `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance/verified_candidate_evidence.json`
- `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance/findings.json`
- `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/findings.json`
- `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verification_results.json`

## Repair order

1. Fix dimension-aware 3D spanning and add opposite-plane tests; invalidate all 3D p_c/C7 claims until rerun.
2. Repair 3D sample accounting, tau storage, active-config selection, and result naming.
3. Rebuild EXP-0006/0007 provenance and rerun with explicit generator versions; retain failed/accepted bootstrap counts.
4. Replace Q-M007/Q-M008 p-value and sieve code; do not use the 10^10 runner until first-segment tests pass.
5. Replace bootstrap p-values with calibrated null/parametric simulation or permutation tests; wire controls into decisions.
6. Enforce immutable, content-addressed preregistrations and artifact hashes.
7. Repair application evidence labels and add regression tests for every user-facing descriptor/control.
