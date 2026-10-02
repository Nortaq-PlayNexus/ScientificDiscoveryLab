# Cross-project numerical/statistical anomaly scan

**Date:** 2026-09-24  
**Scope:** `ScientificDiscoveryLab`  
**Mode:** read-only, disconfirming review; no historical experiment, registry, report, or result file was edited.

## Scope and method

I read the existing independent audit and then checked source/result/preregistration/report cross-consistency across prime gaps, 2-D and 3-D percolation, optics, Feigenbaum computations, S9 outputs, the shared RNG battery, and Collatz. The retained findings are concrete numerical, statistical, dependence, or provenance anomalies rather than generic advice.

The read-only reproduction helper is [`reproduce.py`](reproduce.py). A complete run was captured in [`reproduction.log`](reproduction.log), and the exact command list is in [`COMMANDS.md`](COMMANDS.md). The machine-readable record is [`findings.json`](findings.json); it contains 21 findings, each with exact locations, observed values, rationale, benign explanation, severity/confidence, a minimal command, and prior-claim impact.

## Executive summary

The most consequential new or sharpened findings are:

1. **The EXP-0008/Q-M007 first prime-gap bin is mathematically impossible.** Its edge is `0.10536051565782628`, while the tested odd-prime gaps satisfy `delta >= 2/ln(10^8) = 0.10857362047581294`. The apparent empty-bin anomaly is structural, not evidence for a novel distribution.
2. **Q-M007's p-values are not chi-square tail probabilities.** The stored first-cell p-value is `2.0502642278570707e-07`; the exact `chi2.sf(836.2,1)` is `7.273513898649874e-184`. The source uses a sixth-root Wilson-Hilferty-like transform and a two-sided normal expression.
3. **Q-M008 is not a matched EXP-0008 verification.** It changes the denominator from `ln(p_i)` to `ln(p_{i+1})` and changes all four block ranges, then reports 35 exact-zero p-values and uses a BH implementation without step-up.
4. **The percolation precision chain has several independent breaks.** Q-P006 raw cells are byte-identical to Q-P005 despite a no-reuse preregistration; Q-P007 truncates 100/50/25 samples to 25 per size, stores an unreconstructable tau cache, and extrapolates p_c from hard-coded literals.
5. **The 3-D percolation event is misdefined.** A synthetic opposite-z connection is rejected by the default `spanning_flags`; C7 copies the same z=0-plane logic. The main-named result is a semantic pilot copy, while the main log stops at L=256.
6. **S9 outputs are not empirical measurements.** Q-S9-1/3 are literal dictionaries, Q-S9-2 is generated from assumed Hill parameters, and `0.483` is inserted as an absolute increment while reports call it a relative percentage.
7. **RNG certification and Collatz claims fail their own evidence rules.** The battery reuses one stream for nominally disjoint tests (fresh-seed maximum p-correlation `0.994783937391`), and Collatz timeouts are labeled cycles while only 8 of 27 parameter families are present.

No result in this scan supports a new physical law, novel prime process, empirical S9 effect, 3-D closure, or certified RNG claim.

## Findings

### Prime gaps

#### PRIME-0008-STRUCTURAL-FIRST-BIN — high / high

- **Exact locations:** `03_INVESTIGATIONS/MATHEMATICS/prime_gaps/CODE/run_prime_gaps.py:599-602`; `RESULTS/EXP-0008_results.json` JSON paths `$.primary_results.blocks[*].edges[0]`, `.counts[0]`, `.expected[0]`; `Q-M007/q_m007_results.json:$.bin_summary["1"]`.
- **Observed:** first edge `0.10536051565782628`; first-bin counts are 0 in all four EXP-0008 blocks; Q-M007 records `0` observed versus `576022.2` expected. The structural lower bound is `2/ln(10^8)=0.10857362047581294`, above the edge by `0.003213104817986659`.
- **Anomaly:** the first bin cannot contain any tested odd-prime gap, so its large chi-square contribution is a deterministic support/edge mismatch. Q-M007's “minimum-gap effect” and 38/40 result are not a valid distributional test.
- **Benign explanation:** only a materially different prime population or gap definition could avoid this bound; the stated blocks exclude those cases.
- **Prior impact:** EXP-0008 `H1_SUPPORTED` and Q-M007's 38/40 evidence must not support a novel prime-gap process. The prior descriptive-only classification is strengthened.

#### PRIME-QM007-PVALUE — high / high

- **Exact locations:** `Q-M007/compute_bhfr_40cell.py:42-49`; `Q-M007/BHFR_40cell_results.json:$.cells[0]`, `$.significant_cells`.
- **Observed:** `chi2_cell=836.2000000000002` is stored with `p=2.0502642278570707e-07`; `scipy.stats.chi2.sf(...,1)=7.273513898649874e-184`. The source uses exponent `1/6` rather than the standard Wilson–Hilferty `1/3`, multiplies by the correction term instead of subtracting it, then uses `0.5*erfc` rather than a one-sided chi-square survival function.
- **Anomaly:** the stored p-value is about `2.82e176` times the exact tail probability and is not a calibrated chi-square p-value.
- **Benign explanation:** it could only be a differently named normal-score diagnostic, but the result schema and comments call it a chi-square survival p-value.
- **Prior impact:** the 38/40 cell-level p-value claim is not auditable as written; significance direction does not rescue the malformed values.

#### PRIME-QM008-METHOD-MISMATCH — high / high

- **Exact locations:** EXP-0008 `CODE/run_prime_gaps.py:599-602`; Q-M008 `CODE/run_exp0012.py:43-49,119-126`; EXP-0008 prereg `$.parameters.blocks`; `Q-M008/PLAN.md:21-30`.
- **Observed:** EXP-0008 uses `/ln(lower)` and blocks `[1e4,1e5)`, `[1e5,1e6)`, `[1e6,1e7)`, `[1e7,1e8)`. Q-M008 uses `/ln(primes[1:])` and `[1e6,1e7)`, `[1e7,5e7)`, `[5e7,8e7)`, `[8e7,1e8)` at the same nominal limit. Its stored B1 has `n=586080`, and its overall chi-square is `868281.0185213662`.
- **Anomaly:** both the estimand and the sample weights change, so Q-M008 is not a matched verification or a direct persistence test.
- **Benign explanation:** it may be intended as a new block design, but then the claim must be rescoped and recomputed under a common definition.
- **Prior impact:** the Q-M008 verification/cross-scale conclusion is withdrawn pending a matched reanalysis.

#### PRIME-QM008-PVALUE-BH — high / high

- **Exact locations:** `Q-M008/CODE/run_exp0012.py:62,91,100-113`; `Q-M008/RESULTS/Q-M008_1e8_results.json:$.overall`, `$.blocks`.
- **Observed:** all 35 stored `p_value` fields are exact `0.0`. For `chi2(1)=100`, `1-cdf=0.0` but `sf=1.5239706048320995e-23`; for `z=10`, `1-cdf=0.0` but `sf=7.61985302416047e-24`. Synthetic BH p-values `[.001,.008,.009]` give naive `[True,False,True]` versus proper step-up `[True,True,True]`.
- **Anomaly:** subtraction destroys avoidable tail precision and the BH implementation does not propagate the largest-k decision.
- **Benign explanation:** the largest stored statistics may underflow even with `sf`, and binary significance may remain; the p-values and general FDR algorithm still require correction.
- **Prior impact:** Q-M008 significance counts are not quantitative evidence for persistence.

### Percolation

#### PERC-QP006-DUPLICATE-CELLS — high / high

- **Exact locations:** `Q-P006/CONFIG/prereg_EXP-0009P.json:1,$.note`; `Q-P006/CODE/run_q_p006.py:50-58`; corresponding Q-P005/Q-P006 NPZ files.
- **Observed:** L512/n200 hashes are both `4c45319a...c3afd`; L1024/n100 both `c6ca3de9...8c0572`; L2048/n50 both `9fb582f2...260af`. The Q-P006 preregistration says “No cells from EXP-0009/EXP-0010 reused.”
- **Anomaly:** the raw cells are not independent evidence, and the no-reuse claim is contradicted at the artifact level.
- **Benign explanation:** identical deterministic streams/configuration could reproduce bytes, but that still fails the stated independence requirement unless documented.
- **Prior impact:** Q-P006 cannot be used as an independent precision replication.

#### PERC-QP007-SAMPLE-TRUNCATION — high / high

- **Exact locations:** `Q-P007/CONFIG/prereg_EXP-0009PC.json:1,$.parameters.n_real`; `Q-P007/CODE/run_phase2.py:124-129`; `Q-P007/CODE/RESULTS/EXP-0009-pc_results.json:$.n_real,$.exponents`.
- **Observed:** configured/result `n_real` is `{512:100,1024:50,2048:25}`, but `min_n=25` and every fit matrix is sliced to 25. Effective retained fractions are `0.25`, `0.50`, and `1.0`.
- **Anomaly:** the fit/bootstrap sample differs from the advertised preregistered sample without explanation.
- **Benign explanation:** common-size alignment can be legitimate if preregistered and reported; it is not here.
- **Prior impact:** Q-P007's refined exponent PASS is not a valid preregistered closure.

#### PERC-QP007-CACHE-TAU — high / high

- **Exact locations:** `Q-P007/CODE/run_phase2.py:39-55,141-147`; `Q-P007/CODE/RESULTS/EXP-0009-pc_results.json:$.exponents.tau,$.tau_raw`; cached `EXP-0009-pc_L*.npz`.
- **Observed:** caches contain `masses,chis,pinfs,sizes_n,sizes_n_total` and no `sizes` array. The result stores `tau.mean=null`, `tau.se=null`, and `total_tail_clusters=0`.
- **Anomaly:** aggregate counts/totals cannot reconstruct the cumulative tail statistic; the null is a cache/schema failure, not a measured zero-tail result.
- **Benign explanation:** a revised cache format could repair this, but the current loader and artifacts do not.
- **Prior impact:** Q-P007 tau remains invalid, as already stated by the prior audit.

#### PERC-QP007-PC-HARDCODED — high / high

- **Exact locations:** `Q-P007/CODE/run_phase2.py:61-73`; `Q-P007/CODE/RESULTS/EXP-0009-pc_results.json:$.p_c_measures,$.p_c_refined`; `Q-P007/CODE/run.log:1-7`.
- **Observed:** phase 2 hard-codes `p_c_measures={512:.592883,1024:.592673,2048:.592834}` and sigma literals, then reports `p_c_refined=.5927289999999997`. The intercept is exactly the fit to those rounded literals; sigmas are not propagated.
- **Anomaly:** the apparent refined p_c is an archival-input calculation, not an independently regenerated measurement, and its precision is unsupported.
- **Benign explanation:** the literals may preserve a legitimate earlier phase-1 run, but raw curve/hash/seed provenance is absent.
- **Prior impact:** the Q-P007 refined-p_c explanation for exponent deviations is not independently established.

#### PERC-3D-SPANNING-BOUNDARY — critical / high

- **Exact locations:** `percolation/ENGINE/perc_engine.py:153-173,226-251,329-360`; `percolation_3d/CODE/REPLICATION/independent_check_EXP0011.py:77-88`; `percolation_3d/REPORT/PLAIN_EXP-0011.md:3,20`.
- **Observed:** a synthetic L=4 z=0-plane connection returns `(True,False)`; a true z=0-to-z=3 connection returns `(False,False)`. The direct opposite-z face check returns true for the latter.
- **Anomaly:** the cubic lattice uses z-major flattened IDs, but default `spanning_flags` checks rows 0 and L−1 within the first z-plane. C7 copies the same logic, so its PASS does not validate 3-D opposite-face spanning.
- **Benign explanation:** this could be a deliberately borrowed 2-D crossing estimator, but then it is not the stated 3-D hypothesis.
- **Prior impact:** all 3-D width/exponent results and the prior “inconclusive” classification are strengthened; the pilot does not measure the claimed event.

#### PERC-3D-SAMPLE-REDUCTION — high / high

- **Exact locations:** `percolation_3d/CODE/run_exp0011.py:51-58,165-169`; pilot/main preregistrations `$.parameters.width_grid.*.n_each,$.parameters.n_real`.
- **Observed:** pilot width samples are effectively `30/20/10` rather than `300/200/100`; main samples are `4/4/4` rather than `10/5/10`. Exponent fits truncate to 50 (pilot) or 100 (main) observations per L.
- **Anomaly:** the runner silently changes the preregistered Monte Carlo budget before fitting.
- **Benign explanation:** resource-saving approximations are possible only if frozen and reported; the current metadata reports configured values instead.
- **Prior impact:** 3-D quantitative claims and uncertainty cannot be accepted from these runs.

#### PERC-3D-MAIN-RESULT-COPY — high / high

- **Exact locations:** `percolation_3d/CODE/RESULTS/EXP-0011_results.json:$.L_list`; `EXP-0011_pilot_results.json`; `CODE/LOG/run.log:3-7`; `CONFIG/prereg_EXP-0013.json:1,$.parameters.L_list`.
- **Observed:** the two result files are semantically identical after removing `elapsed`; both use `[8,16,24]`. The main log says `[128,256,512]` and stops at L=256.
- **Anomaly:** a pilot overwrite is presented under a main-result filename, so no main 3-D run artifact exists.
- **Benign explanation:** force-pilot mode may have been intentional, but the output path/status is misleading.
- **Prior impact:** EXP-0013 remains incomplete; no 3-D closure can be claimed.

#### PERC-EXP0007-DRAWS-PRECISION — medium / high

- **Exact locations:** `percolation/CODE/run_percolation_exp0007.py:145-160`; `CODE/RESULTS/EXP-0007_summary.json:$.estimator_diagnostics.width_route.bootstrap.n_draws,$.primary_results.fss_primary.se_a,$.primary_results.in_tol`; prereg `$.parameters.bootstrap.n_draws`; report `TECHNICAL_EXP-0007.md:64-76,120-127`.
- **Observed:** prereg/report request 500 draws, stored width bootstrap has 495; `se_a=.03170744877268775` versus `tol_pc=.01` (3.170745×), while the point deviation is only `.0006874530252671818`.
- **Anomaly:** a point estimate is compared with a tolerance much narrower than its reported uncertainty; skipped bootstrap draws are not disclosed.
- **Benign explanation:** the result can still be compatible with exact bond `p_c=1/2`, but not a precision measurement at the stated resolution.
- **Prior impact:** known-law reproduction remains; fine p_c/precision language is downgraded.

#### PERC-EXP0009-C7-SAME-STREAMS — medium / high

- **Exact locations:** `Q-P005_exponents/REPLICATION/independent_check_exp0009.py:1-8`; `REPLICATION/C7_exp0009_report.json:$.streams,$.per_L,$.D_f`; `CODE/RESULTS/EXP-0009_results.json:$.primary_results.gates.C7`.
- **Observed:** C7 explicitly uses identical G_LAB labels/seeds and the first 40 realizations; all Mmax/chi comparisons are bit-identical and the gate passes.
- **Anomaly:** the implementation is independent, but the data are not. A same-stream check cannot establish sampling independence, fresh reproducibility, or an independent exponent result.
- **Benign explanation:** this is a valid paired implementation unit test when used only for code correctness; it should not be counted as independent experimental evidence.
- **Prior impact:** C7 remains implementation evidence, but EXP-0009's exponent/R3 interpretation must not count it as a fresh sample.

#### PERC-R3-ALGEBRAIC-COUPLING — medium / high

- **Exact locations:** `Q-P005_exponents/CODE/run_exp0009.py:57-76,274-282,328-331`; prereg `$.predictions.R3_Df_beta`; result `$.primary_results.relations.R3_Df=2-bn`.
- **Observed:** `P_inf=M_max/N` is computed from the same mass realizations as D_f. Stored values give `D_f=1.869737723898956`, `beta/nu=.1295052403370289`, and R3 residual `.0007570357640149794`.
- **Anomaly:** R3 is algebraically coupled, not an independent physical scaling test, despite being a PASS gate.
- **Benign explanation:** the preregistration labels it an algebraic comparison; the issue is treating it as independent confirmation.
- **Prior impact:** prior finite-size interpretation is unchanged, but R3 must be labeled as an internal consistency check.

### Optics, Feigenbaum, S9, RNG, and Collatz

#### OPTICS-PVALUE-EPS-FLOOR — medium / high

- **Exact locations:** speckle `CODE/run_speckle_contrast.py:49-60`; vortex `CODE/run_vortex_density.py:184-220`; result JSON paths `$.cells.N64_M2.p_two_sided_null_r_eq_1` and eight vortex `p_two_sided_ratio_eq_1` paths.
- **Observed:** `2.220446049250313e-16` appears once in EXP-0002 and eight times in EXP-0003 after adding `np.finfo(float).eps` to zero-tail empirical bootstrap p-values.
- **Anomaly:** the floor is not the resolution of a finite bootstrap and artificially sharpens FDR inputs.
- **Benign explanation:** it avoids `log(0)` and practical CI-based decisions may remain valid; only quantitative p/FDR interpretation is affected.
- **Prior impact:** known speckle/vortex laws remain supported, but fine significance claims do not.

#### FEIGENBAUM-ROOT-SEQUENCE — high / high

- **Exact locations:** nested `CODE/.../RESULTS/EXP-0014_results.json:$.z3,$.z4`; `feigenbaum_engine.py:121-131,188-200`.
- **Observed:** z=3 has only two unique a-values across eight entries and six `Infinity` deltas; z=4 reverses from `a_6=1.5948686474115557` to `a_7=1.5822530451723789`, repeats a_7, and emits a negative delta then `Infinity`.
- **Anomaly:** higher-order sequences are not valid period-doubling convergence data.
- **Benign explanation:** z=2 remains internally monotone and valid; higher-order values can be retained only as failed diagnostics.
- **Prior impact:** confirms withdrawal of historical z=3/z=4 claims while preserving the z=2 known-law reproduction.

#### FEIGENBAUM-CONTROL-PREREG — high / high

- **Exact locations:** nested result `$.controls.C4`; `run_feigenbaum.py:103-116`; `CONFIG/prereg_EXP-0014.json:1`; report `TECHNICAL_EXP-0014.md:56-65`.
- **Observed:** stored C4 difference `.08955043987795008`, pass is the string `'False'`; current runner hard-codes C4 `pass=True`; the preregistration fails JSON parsing because it begins with a comment.
- **Anomaly:** a failed method comparison is reported as a pass in the current control path, and the frozen protocol cannot be machine-validated.
- **Benign explanation:** the stored result may be from an older runner, but that is an unresolved provenance/version mismatch.
- **Prior impact:** only independently supported z=2 should remain controlled.

#### S9-HARDCODED-SYNTHETIC-OUTPUTS — high / high

- **Exact locations:** `save_q9results.py:8-64`; `Q-S9-2/dose_response.py:27-45,52-58`; Q-S9-1 report `TECHNICAL_Q-S9-1.md:84-99`.
- **Observed:** Q-S9-1/3 are literal dictionaries; Q-S9-3 raw/unbiased arrays are equal at 10/11 doses; Q-S9-2 stored rates exactly match a generator using assumed parameters and seeded Gaussian noise.
- **Anomaly:** no image-analysis or measured dose/perception input supports the empirical S9 claims.
- **Benign explanation:** these can be illustrative synthetic fixtures, but not empirical findings.
- **Prior impact:** Q-S9-1/2/3 remain invalid/not reproduced; no S9 discovery claim survives.

#### S9-HILL-UNIT-MISMATCH — high / high

- **Exact locations:** `Q-S9-2/dose_response.py:23-25,32-35`; `cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-2.md:23-30`.
- **Observed:** the formula uses `baseline + max_inflation`; with `.205` and `.483`, saturation is `.688` and relative increase is `235.609756%`. A true 48.3% relative increase would saturate at `.304015`.
- **Anomaly:** relative and absolute units are mixed, changing the claimed effect size by `.383985` rate units.
- **Benign explanation:** `.483` could be intended as an absolute increment, but then the percent wording is wrong.
- **Prior impact:** Q-S9-2 magnitude/EC50 interpretation is invalid independently of its synthetic provenance.

#### RNG-POOL-DEPENDENCE — high / high

- **Exact locations:** `04_SHARED_ENGINE/engine/validation/rng_battery.py:19-20,372-400`; `rng_certification/CODE/run_rng_cert.py:104-130`; result `$.decision`.
- **Observed:** the documentation says disjoint slices, but every test receives the same arrays. A fresh 20-seed audit gives maximum absolute p-correlation `0.994783937391` (T03_runs/T15_ac1), while the stored decision is `CERTIFIED`.
- **Anomaly:** pooled KS, binomial, and BH calibration assumes independence that the implementation violates; C7 checks formulas, not joint dependence.
- **Benign explanation:** a fixed stream can be intentional, but the analysis must then be dependence-aware or use independent streams.
- **Prior impact:** RNG certification is withdrawn; this does not prove the generator itself is defective.

#### COLLATZ-TIMEOUT-AS-CYCLE — high / high

- **Exact locations:** `collatz/CODE/run_collatz_full.py:9-17,30-35,70-88`; result `Q-M001_full_results.json:$.results,$.divergent_pilot`; prereg `$.parameters`; report `TECHNICAL_Q-M001.md:16-19,63-81`.
- **Observed:** any max-step timeout is appended to `cycles_found`; the pilot records 470 “cycles” with `max_stopping_time=1000`. The full artifact has 3 full plus 5 pilot families, versus 27 preregistered combinations. A direct n0=55 `(3,3,1)` check finds no repeated state before the cutoff.
- **Anomaly:** timeout is not cycle detection, and eight tested families cannot establish an iff statement over 27.
- **Benign explanation:** the report discloses divergent-family pilots, but not in its headline iff/full-sweep language.
- **Prior impact:** Collatz iff/full-sweep remains not established, confirming the prior audit.

## Claim-classification changes

- **Prime gaps:** downgrade EXP-0008/Q-M007 from a positive distributional anomaly to a structurally contaminated descriptive result; withdraw Q-M008 as a matched verification pending reanalysis.
- **2-D percolation:** Q-P006 is not an independent precision replication; Q-P007 exponent, tau, and refined-p_c closure claims are not preregistered/reproducible as stored. EXP-0009 C7 is an implementation check on identical streams, not fresh sampling. EXP-0007 remains a known-law reproduction but not a precision claim.
- **3-D percolation:** no result is closed; the current code measures a z=0-plane event, the sample budget is changed, and the main artifact is a pilot copy.
- **Optics:** retain the prior known-law classifications, but do not use the floored p-values/FDR flags as quantitative evidence.
- **Feigenbaum:** retain z=2 as a controlled known reproduction; keep z=3/z=4 contradicted/invalid.
- **S9, RNG, and Collatz:** S9 empirical claims are not reproduced, RNG `CERTIFIED` is withdrawn, and the Collatz iff/full-sweep claim remains not established.

## Reproduction and preservation notes

The full command completed with return code 0 and no `CASE_ERROR` entries. The script only reads source/result artifacts and uses synthetic labels for the 3-D boundary test. No historical experiment was rerun through a writer, and no file outside `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/` was intentionally changed.
