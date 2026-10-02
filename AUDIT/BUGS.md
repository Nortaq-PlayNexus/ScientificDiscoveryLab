# BUGS AND METHOD DEFECTS — Independent Audit

**Audit date:** 2026-09-24  
**Policy:** historical files were not edited. Each entry identifies evidence, impact, and a repair recommendation for a future isolated branch.

## Confirmed defects

### B-001 — Q-P007 nested cluster-size cache destroys the tau sample

- **Location:** `03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/run_phase2.py:99–123, 141–145`
- **Mechanism:** each one-realization `perc_engine` call returns `cluster_sizes` as a list containing one array. The runner appends that entire list as one realization (`sizes_list.append(cl_sizes)`), then later evaluates `ss[1:]` as if `ss` were an array. For every realization `ss` has length one, so the tail is empty.
- **Evidence:** `percolation_reanalysis_results.json` records one stored array per realization; the current runner raises `KeyError: sizes` when asked to load its own cache.
- **Impact:** historical Q-P007 tau output is not a measurement of the cluster-size tail. Any `tau` comparison based on it is invalid.
- **Repair:** store `sizes_list.append(cl_sizes[0])` for one-realization cells, or preserve a list-of-lists with one entry per realization and flatten explicitly. Add a round-trip test asserting every stored realization has the expected number of clusters and a non-empty tail.

### B-002 — Q-P006 “no cells reused” is false

- **Location:** `03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/CODE/RESULTS/_cells_L*.npz`
- **Evidence:** SHA-256 values for L=512/n=200, L=1024/n=100, and L=2048/n=50 are byte-identical to the corresponding Q-P005 files.
- **Impact:** Q-P006 cannot be treated as an independent precision replication. The result is a copied-data rerun.
- **Repair:** regenerate under a new content-addressed label/seed namespace, record the generating command and hashes, and compare file hashes before analysis.

### B-003 — EXP-0014 root finder selects inherited or distant roots

- **Location:** `03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CODE/feigenbaum_engine.py:61–185`
- **Mechanism:** global sign-change scans over increasingly dense/wide intervals do not reliably isolate the first exact-period root. The fallback can return a lower-period root or a distant root. The z=3 stored sequence repeats the n=2 root; z=4 later values roll back to an earlier root.
- **Evidence:** independent arbitrary-precision continuation obtains strictly increasing, period-verified sequences for z=2,3,4. Historical C4 stored difference is `0.08955043987795008` and `pass=false`, while current code hardcodes a pass.
- **Impact:** historical z=3/z=4 constants and all associated alpha/control claims are invalid.
- **Repair:** use arbitrary-precision continuation from the preceding verified root, select the first sign-changing root to its right, verify every earlier return, and fail closed if no unique root is found.

### B-004 — EXP-0014 preregistration is not valid JSON

- **Location:** `03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/CONFIG/prereg_EXP-0014.json`
- **Evidence:** JSON parse fails at line 1, column 1; the stored result is nested under a duplicated `CODE/03_INVESTIGATIONS/.../RESULTS` path while the canonical `RESULTS` directory is empty.
- **Impact:** preregistration-before-execution and result-location claims cannot be independently established.
- **Repair:** freeze a valid UTF-8 JSON file with an immutable hash and write results to one canonical path.

### B-005 — EXP-0014 C3/C4/C6 pass fields are hardcoded

- **Location:** `feigenbaum_engine.py` control/reporting path and stored EXP-0014 result comparison
- **Evidence:** static audit finds current runner control records that assert pass independently of recomputation; stored C4 actually records `pass=false` and difference `0.08955043987795008`, contradicting the report’s “all 7 controls PASS.”
- **Impact:** control count is not an evidentiary result.
- **Repair:** calculate every control from raw numerical outputs and use a single validator that refuses inconsistent records.

### B-006 — Collatz max-step trajectories are mislabeled as cycles

- **Location:** `03_INVESTIGATIONS/MATHEMATICS/collatz/CODE/run_collatz.py` and `Q-M001_full_results.json` writer path
- **Mechanism:** a trajectory reaching `max_steps` is appended as a cycle without checking repeated states. The supplied full result contains only three convergent families, while the claim refers to a 27-family sweep.
- **Evidence:** static result/code audit in `independent_static_results.json`.
- **Impact:** “cycles found,” “convergence iff a=b=c,” and full-sweep language are unsupported.
- **Repair:** distinguish `reached_one`, `max_steps`, and `verified_cycle`; record all families actually run; never infer a cycle from a timeout.

### B-007 — Q-S9 outputs are hardcoded or synthetic

- **Location:** `save_q9results.py`, `03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-S9-2/dose_response.py`
- **Evidence:** Q-S9-1 and Q-S9-3 values are embedded in the writer; Q-S9-2 constructs observations from assumed Hill parameters and uses no measured dose data.
- **Impact:** threshold, EC50, Hill slope, and detector-bias claims are not empirical results.
- **Repair:** separate raw observations from derived summaries, hash inputs, and refuse to write a result when raw data are absent.

### B-008 — Historical RNG certificate pools dependent p-values

- **Location:** `04_SHARED_ENGINE/engine/validation/rng_battery.py:372–400`; `run_rng_cert.py:104–130`
- **Mechanism:** all bit-spectrum tests consume the same `bits` array; bytes/floats/words tests also reuse their arrays. The aggregate then applies KS, binomial, and BH rules as if all 24 p-values per seed were independent.
- **Evidence:** fresh 80-seed calibration shows maximum absolute p-value correlation around 0.99 and 18–20 correlated pairs per generator; test-specific uniformity failures occur for controls as well as G_LAB.
- **Impact:** “CERTIFIED” is an invalid decision even when the pooled numbers happen to pass.
- **Repair:** pre-register per-test marginal calibration over independent seeds, model dependence explicitly, and use a dependency-aware multiple-testing procedure. Do not call a generator certified from statistical tests alone.

## Confirmed statistical/design defects

### B-009 — Q-P007 p_c refinement omits threshold uncertainty

- **Location:** `run_phase2.py:61–73`
- **Mechanism:** three hard-coded p_c measures are linearly extrapolated without propagating their stated sigma values.
- **Evidence:** bootstrap intercept `0.592696±0.00325` is far wider than the claimed `1.7e-5` deviation from the canonical threshold.
- **Impact:** a tiny threshold shift cannot explain the exponent deviations.
- **Repair:** fit a noisy threshold model with covariance/propagated uncertainty and preregister the acceptance test.

### B-010 — “R3” hyperscaling check is algebraically tautological

- **Location:** `run_exp0009.py` analysis of `beta/nu` and `D_f`
- **Mechanism:** `P_inf = M_max/L²`, so `beta/nu = 2-D_f` follows from the same mass array by definition; the identity difference was reported as about `1.74` despite the algebraic relation.
- **Evidence:** `independent_static_results.json`, `R3_identity_check`.
- **Impact:** R3 is not an independent scaling-law check.
- **Repair:** compare independently measured observables, such as order-parameter susceptibility and cluster-mass exponents, with uncertainty and covariance.

### B-011 — Prime-gap iid/binomial null is misspecified for finite normalized gaps

- **Location:** EXP-0008/Q-M007/Q-M008 analysis
- **Evidence:** normalized gaps have lag-1/lag-2 dependence, variance changes across blocks, and the first bin is structurally impossible because the smallest odd-prime gap is 2/log x.
- **Impact:** enormous chi-square values against a fixed-bin Exp(1) null do not identify a new process.
- **Repair:** use a finite-range model respecting prime-gap constraints, block/bootstrap dependence, and asymptotic interval hypotheses; report power and simulation-based null calibration.

### B-012 — Q-P007 tau bootstrap treats clustered tail observations as iid clusters

- **Location:** `run_exp0009.py:118–165`
- **Mechanism:** the deterministic fit is over cluster sizes pooled across realizations; the bootstrap resamples individual cluster sizes without preserving realization-level dependence.
- **Impact:** reported bootstrap SE is optimistic or at least not a realization-level uncertainty.
- **Repair:** resample realizations/blocks first, then recompute the entire tail fit; use block bootstrap or hierarchical bootstrap.

## EXP-0003 sub-audit defects and controls

### B-013 — Parallel sub-agent interpolation normalization error

- **Location:** `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/CODE/run_broadband_convergence.py:309–314`
- **Mechanism:** refined winding density per refined cell was divided by `factor**2` a second time. The first run consequently reported ratios around 0.06 (2x) and 0.004 (4x), rather than near 1.
- **Evidence:** raw failed control log; corrected audit script multiplies by `factor**2` and recovers near-unity ratios.
- **Impact:** the first interpolation control is invalid; it must not be cited as evidence.
- **Repair:** use a unit-tested conversion from refined-cell density to original-cell density and retain the failed run as a control artifact.

### B-014 — Synthetic contour sanity test places the zero at a grid vertex

- **Location:** sub-agent `run_sanity_controls()`
- **Evidence:** exact linear vortex has Re/Im contour intersection at a vertex; contour detector returns zero. A regularized winding test detects one unit vortex.
- **Impact:** zero contour result is not evidence that the detector fails on random fields; the test geometry is degenerate.
- **Repair:** place a known vortex strictly inside a cell and test both detectors with a nonzero sub-cell zero.

### B-015 — Historical EXP-0003 real-field self-conjugate coefficients are symmetrized

- **Location:** `run_vortex_density.py:73–82`
- **Mechanism:** self-conjugate DFT coefficients are forced through a complex-pair average rather than drawn with the correct real Gaussian variance.
- **Evidence:** independent corrected and historical power comparison shows nearly identical aggregate power in the tested case, with a small self-conjugate fraction.
- **Impact:** likely negligible for the reported ratios but technically incorrect and should be corrected for precision work.
- **Repair:** explicitly make self-conjugate coefficients real with variance matched to the target component spectrum and add a power-law unit test.

## Infrastructure and provenance risks

### B-016 — Identifier collisions and ambiguous result paths

Examples: `EXP-0009` is shared by Q-P005/Q-P006/Q-P007; `EXP-0012`/`EXP-0013` collide with prime-gap filenames; Feigenbaum output is nested under a duplicated path. These make registry-based provenance and automated retrieval unsafe.

### B-017 — Empty raw-data/database locations

`05_DATA` directories and all 21 SQLite tables are empty. The RAR is a duplicate snapshot. Scientific claims therefore depend on generated outputs and scripts, not an auditable raw-data chain.

### B-018 — 3D runner configuration hazard

The default 3D runner selects the expensive EXP-0013 main configuration unless an explicit pilot flag/environment setting is supplied. A “pilot” invocation can therefore start a multi-hour main run. The main run timed out at L=256 and did not produce a completed result.

## Repair priority

1. Fix Q-P007 storage/tau and rerun from raw fields.
2. Fix Feigenbaum root selection and regenerate all controls from a valid preregistration.
3. Replace the RNG certificate with per-test, dependence-aware calibration.
4. Remove hardcoded/synthetic S9 result paths from empirical claims.
5. Add content-addressed provenance and immutable experiment IDs.
6. Run a production-scale 3D experiment only after a smoke-test guard and explicit configuration selection.
