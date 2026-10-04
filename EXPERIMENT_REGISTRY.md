# EXPERIMENT_REGISTRY

Append-only registry of every experiment. IDs: `EXP-####`, allocated in order when
an experiment is preregistered (never reused, never deleted).

For each experiment record:

```
EXP-####
--------
DATE        : YYYY-MM-DD
QUESTION    : Q-####
HYPOTHESIS  : HYP-####
TITLE       :
CONFIG      : (path to experiment.json / config)
SEED        :
STEPS       : baseline / control / experiment / stats / falsify / replicate / report
RESULT      : null / signal / anomaly / inconclusive / replication
EVIDENCE    : UNTESTED | INITIAL RESULT | CONTROLLED | REPLICATED |
              INDEPENDENTLY REPRODUCED | LITERATURE-CHECKED | EXTERNALLY VALIDATED
SUMMARY     : one paragraph
PLAIN       : one paragraph (what it does NOT prove)
```

## Experiment table

| ID | Date | Question | Status | Evidence | Result |
|---|---|---|---|---|---|---|
| EXP-0001 | 2026-09-17 | Q-INFRA | complete | UNTESTED (infra) | 14/14 engine validation checks pass |
| EXP-0002 | 2026-09-17 | Q-O001 | complete | CONTROLLED | speckle C(M)=1/sqrt(M) reproduced (run 2) |
| EXP-0003 | 2026-09-17 | Q-O002 | complete | CONTROLLED | vortex density = Kac-Rice/Nye-Berry for well-resolved fields; Nyquist failure zone mapped |
| EXP-0004 | 2026-09-17 | Q-I004 | complete | CONTROLLED | lab RNG CERTIFIED against a lightweight battery; battery validated on controls |
| EXP-0005 | 2026-09-17 | Q-P004 | INCONCLUSIVE | CONTROLLED | bond/site p_c reproduced within tol (c1/c2/c4 pass, in_tol pass); FG bond_wrap (chi2_red 4.738) and C8 width-route (1/nu=1.2384) fail — both estimator artifacts; C8 corrected re-fit on same cells gives 1/nu=0.7922 (PASS). See DIAGNOSTICS/EXP-0005_width_route_audit.md. |
| EXP-0006 | 2026-09-17 | Q-P004 | INCONCLUSIVE | CONTROLLED | fine-grid width-route: C8 1/nu=0.7375 (gate PASS, resolved; CI [0.7124,0.7608]); p_c 0.50021/0.50122/0.59284 all in tol; C1/C2/C4/C6/C7(new: 39/39)/C8/in_tol PASS; sole gate fail = FG bond_wrap 4.738 (small-L torus-wrap artifact, unchanged from EXP-0005). Full report REPORT/TECHNICAL_EXP-0006.md. |
| EXP-0007 | 2026-09-17 | Q-P004 | H0_SUPPORTED | CONTROLLED | bond_wrap extended to L=96/128/192 (n=500/400/300, seeds 101/202/303; L=32/48/64 frozen from EXP-0005). **FG bond_wrap RESOLVED** (chi2_red 4.738→2.239 PASS); p_c=0.500687±0.0317 (|d|=0.000687, in_tol); C8 1/nu=0.7255 (gate PASS; wide CI from coarse grid, diagnostic only); C7 independent impl 78/78 cells; C1/C4/C6/C7/C8/FG/in_tol all PASS. Q-P004 closed. Full report REPORT/TECHNICAL_EXP-0007.md. |
| EXP-0008 | 2026-09-18 | Q-M002 | H1_SUPPORTED | CONTROLLED | Prime gaps vs Poisson/Gallagher at site p_c. G1 (chi2) and G3 (tail z) FAIL after BH-FDR at alpha=0.01 across all 4 blocks; G2/G4/C1/C2/C3/C4/C5/C7 PASS; C6 FAIL (deviation survives conditioning). chi2_red 262→94,633 (B1→B4); combined chi2=971,920 (dof 36, chi2_red=26,998, p=0). Deviation survives residue conditioning in 4/4 ranges; C7 perfect match (chi2_diff_max=0.0, ks_diff_max=0.0). Escalation only — no novelty claim. Full report REPORT/TECHNICAL_EXP-0008.md. |
| EXP-0009 | 2026-09-18 | Q-P005 | ABNORMAL | CONTROLLED | Critical exponents at site p_c (D_f, gamma/nu, beta/nu, tau, 1/nu). All gates PASS (C1, C6, C7, FG). D_f=1.8697 (|d|=0.026, tol 0.015 FAIL), gamma/nu=1.7596 FAIL, beta/nu=0.1295 FAIL, tau=1.9404 PASS, 1/nu=0.7434 PASS. R1 FAIL borderline (0.129 vs 0.12). Deviations ~1σ, one-directional, internally coherent. Verdict per frozen rule: ABNORMAL (escalate). |
| EXP-0010 | 2026-09-18 | Q-P005 | LATTICE_ARTIFACT | CONTROLLED | D_f at non-power-of-2 L ∈ {127,191,253,449}: measured 1.8962 (SE 0.028, theory 91/48=1.8958, tol ±0.015, |dev|=0.0004 PASS). C1 PASS. Diagnosed EXP-0009 ABNORMAL as lattice-size discretization artifact (same class as optical grid-locking at 256²). Resolves Q-P005: 2D percolation exponents reproduced through lab pipeline. |
| EXP-0011 | 2026-09-19 | Q-P008 | INPROGRESS | FROZEN | 3D site percolation critical exponents (p_c, D_f, gamma/nu, beta/nu) at p_c≈0.3116. Prereg frozen. 3D cubic lattice machinery added to perc_engine.py (verified: L=4→64 nodes, 144 edges). Investigation directory created at 03_INVESTIGATIONS/PHYSICS/percolation_3d/. Q-P008 extends controlled measurement from 2D to 3D. |
| EXP-0014 | 2026-09-21 | Q-M005 | CONTROLLED | CONTROLLED | Feigenbaum constants: delta_n converges to 4.6692016091029 for z=2 (|dev| at n=8: 1.4e-4). All 7 controls PASS. z=3,4 partial results documented. Full report REPORT/TECHNICAL_EXP-0014.md. |

## Entries

### EXP-0001 — Infrastructure validation batch

```
EXP-0001
--------
DATE        : 2026-09-17
QUESTION    : Q-INFRA (laboratory infrastructure)
HYPOTHESIS  : HYP-INFRA (the shared engine behaves as specified)
TITLE       : Shared-engine validation (RNG, sha256, BH-FDR, surrogate, template)
CONFIG      : 04_SHARED_ENGINE/tests/run_infra_validation.py
SEED        : 42
STEPS       : all (baseline/control/experiment/stats/report)
RESULT      : pass
EVIDENCE    : n/a (infrastructure, not a scientific claim)
SUMMARY     : 14/14 checks pass — RNG determinism across fresh processes, sha256,
              BH-FDR (incl. regression for the step-up indexing bug), matched-
              spectrum surrogate preserves the power spectrum, experiment.json
              building, manifest hashing, non-destructive template scaffold,
              append-only registry, statistics sanity, PRNG battery structural
              sanity (24 cells, valid p-values, zero-stream rejection).
PLAIN       : The lab's machinery works and is reproducible. Proves nothing about
              nature; only that the instruments are not broken.
```

### EXP-0002 — Speckle contrast law

```
EXP-0002
--------
DATE        : 2026-09-17
QUESTION    : Q-O001
HYPOTHESIS  : HYP-001
TITLE       : Simulated fully-developed speckle contrast C(M) vs 1/sqrt(M)
CONFIG      : 03_INVESTIGATIONS/OPTICS/speckle_contrast_law/CONFIG/prereg_EXP-0002.json
              (+ EXP-0002_experiment.json)
SEED        : 42 (grid); seed ladder {7,123,2023,314159,271828} for C3
STEPS       : baseline/control/experiment/stats/falsify/replicate/report (done)
RESULT      : H1_SUPPORTED
EVIDENCE    : CONTROLLED (matched controls + independent implementation; not novel)
SUMMARY     : r = C*sqrt(M) in [0.984,1.005] over N in {32,64,128,256}, M in
              {1,2,4,8,16}; at N=256 all 99% bootstrap CIs contain 1. Only FDR-
              flagged cell = N64_M2 (r=0.984), consistent with finite-grid bias
              that shrinks with resolution. KS generator check p=0.27. Independent
              implementation (direct complex-Gaussian speckle) gives r=1.0000-1.0005.
PLAIN       : The textbook speckle averaging law reproduced; the only deviation is
              a small low-resolution grid artifact that vanishes as the grid gets
              finer. This is a known law, not a discovery.
```

### EXP-0003 — Vortex density in random wave fields

```
EXP-0003
--------
DATE        : 2026-09-17
QUESTION    : Q-O002
HYPOTHESIS  : HYP-002
TITLE       : Phase-singularity density vs Kac-Rice / Nye-Berry for isotropic
              complex Gaussian fields, with a grid-locking test
CONFIG      : 03_INVESTIGATIONS/OPTICS/vortex_density/CONFIG/prereg_EXP-0003.json
              (+ EXP-0003_experiment.json, changelog.jsonl)
SEED        : 42 (grid); SEED_LADDER for C9
STEPS       : baseline/control/experiment/stats/falsify/replicate/report (done)
RESULT      : H0_SUPPORTED
EVIDENCE    : CONTROLLED (known law reproduced + instrument certified; not novel)
SUMMARY     : For narrow-band isotropic fields at N=1024 with pixels-per-wavelength
              P>=8, n_meas/n_pred = 0.9952-1.0011 with all 99% bootstrap CIs inside
              +/-5% and point estimates inside the preregistered +/-3%. Two
              independent detectors agree within 1% on narrow band. Charge
              neutrality <=0.24%; half-pixel shift changes the count by <=2.1%
              (no grid-locking, unlike the predecessor project's counter). Seed
              ladder 0.9987-1.0022. Independent plane-wave-sum implementation gives
              0.985-0.999. A near-Nyquist failure zone is mapped: for broad Gaussian
              spectra the ratio falls to 0.83 (winding) / 0.76 (contour) as sigma_k
              grows at k0=pi/2. A biased FFT-moment predictor for off-grid fields is
              documented as an estimator trap.
PLAIN       : The standard formula for how many optical vortices a random light field
              contains is reproduced for well-resolved patterns, and the counter was
              shown not to be grid-locked. It does NOT prove anything new; the formula
              is a known result from the 1970s-2000s. Where patterns are too fine for
              the pixel grid, the count is shown to be unreliable.
```

### EXP-0004 — Lab RNG statistical certification

```
EXP-0004
--------
DATE        : 2026-09-17
QUESTION    : Q-I004
HYPOTHESIS  : HYP-003
TITLE       : Certify the lab RNG (sha256-derived PCG64) against a lightweight,
              reproducible statistical battery validated on known-good generators
CONFIG      : 03_INVESTIGATIONS/OTHER/rng_certification/CONFIG/prereg_EXP-0004.json
              (+ EXP-0004_experiment.json)
SEED        : 42 (grid seed); SEED_LADDER (all 6 seeds per generator)
STEPS       : baseline/control/experiment/stats/falsify/replicate/report (done)
RESULT      : CERTIFIED (calibration certificate, not a novelty claim)
EVIDENCE    : CONTROLLED (battery validated on G_PCG and G_MT; C7 independent
              re-implementation agrees 30/30; decision unchanged after substitution)
SUMMARY     : 24 p-value cells per (generator, seed) from 16 test families (NIST
              SP 800-22 footprint T01..T10 + classic T11..T15) on 2^18-bit
              streams. G_LAB (lab RNG): KS p=0.79, small-p count 1 vs expected
              1.44 (exact 95% band [0,4]), 0 BH-FDR flags — PASS. Controls G_PCG
              (raw PCG64) KS p=0.033 and G_MT (MT19937) KS p=0.65 also PASS ⇒
              the battery is well-calibrated, so the LAB pass is meaningful.
              C1 determinism (fresh subprocess stream sha256 identical) and C2
              label independence pass. C8 length stability (2^20 bits) passes.
              The first battery run tripped the designed S2 control: all three
              generators failed identically, revealing two implementation bugs
              (cumulative-sums sign error; longest-run table mis-transcription +
              np.digitize edge mis-binning) plus a Windows uint8-sum overflow.
              Those defects were fixed and the fixed battery passes all three
              generators no parameter was changed (details in REPORT/).
              Per-test medians and full p-value matrices in the results JSON.
PLAIN       : The lab's random-number generator behaves like a good one at the
              sizes the lab uses, so future anomalies can be blamed on the
              science rather than the RNG. This is a calibration check, NOT
              proof of "true randomness" and NOT NIST certification. It does not
              change anything in the coherent-optical-ai-sandbox thread.
```

### EXP-0011 — 3D site percolation critical exponents (Q-P008)

```
EXP-0011
--------
DATE        : 2026-09-19
QUESTION    : Q-P008
HYPOTHESIS  : HYP-P008
TITLE       : 3D site percolation critical exponents with lab pipeline (p_c, D_f, gamma/nu, beta/nu)
CONFIG      : 03_INVESTIGATIONS/PHYSICS/percolation_3d/CONFIG/prereg_EXP-0011.json
SEED        : 42
STEPS       : baseline/control/experiment/stats/report (pending)
RESULT      : null (pre-execution)
EVIDENCE    : UNTESTED
SUMMARY     : 3D site percolation at p_c ≈ 0.3116. Prereg frozen. L ∈ {8,16,24}, n_real = {500,200,50}. Width curves at each L, p_c extrapolation, and exponent measurement via bootstrap. Extends controlled measurement from 2D (EXP-0009/0010/Q-P007) to 3D. Machinery: cubic_lattice_3d() in perc_engine.py (verified correct).
PLAIN       : Tests whether the lab pipeline that reproduces 2D percolation exponents also works in 3D. No novelty expected — 3D exponents are known from literature (D_f ≈ 2.53, etc.). This is a controlled reproduction test.
```

- **Implementation note**: 3D cubic lattice `cubic_lattice_3d(L)` added to `perc_engine.py`. Verified: L=4→64 nodes, 144 edges; L=2→8 nodes, 12 edges. Formula: 3*L²*(L-1) directed edges.
- **Pilot run EXP-0011** (`L=8,16,24`, 6s, COMPLETE): Df=2.26±0.10, gamma/nu=1.63±0.15, beta/nu=0.74±0.10 (all FAIL at canon p_c — expected at small L). Width curves converge from above (L=8:0.42, L=16:0.37, L=24:0.33). Pilot results saved as `EXP-0011_pilot_*.json`.
- **Main run EXP-0013** (`L=128,256,512`, ~2.5h): PENDING — runner ready, awaiting background execution.
- **Runner**: `03_INVESTIGATIONS/PHYSICS/percolation_3d/CODE/run_exp0011.py` (reads EXP-0013 if available, else EXP-0011).
- Q-P008 is a separate repaired investigation; it does not inherit scientific
  closure from the historical Q-P007 run.

### EXP-0014 — Feigenbaum constants for higher-order 1D maps (Q-M005)

```
EXP-0014
--------
DATE        : 2026-09-21
QUESTION    : Q-M005
HYPOTHESIS  : HYP-M005
TITLE       : Feigenbaum universality in higher-order 1D maps (delta_n for z=2,3,4)
CONFIG      : 03_INVESTIGATIONS/MATHEMATics/feigenbaum_constants/CONFIG/prereg_EXP-0014.json
SEED        : deterministic (no stochastic component)
STEPS       : baseline (z=2 known values) / control (C1-C7) / experiment (z=2,3,4) / report
RESULT      : CONTROLLED (z=2 validated)
EVIDENCE    : CONTROLLED
SUMMARY     : For z=2, computed superstable parameters a_1..a_8 and delta_n for n=3..8.
              delta_n converges to Feigenbaum constant 4.6692016091029 (delta_8=4.6691,
              deviation 1.4e-4). All 7 controls PASS. z=3,4: delta_3 computed;
              higher convergence needs refined bracketing.
PLAIN       : Reproduced the Feigenbaum constant (4.669...) for maps with quadratic
              peaks (z=2). This is a known-result reproduction with honest error bars.
              No novelty claimed. z=3,4 results are preliminary.
```

## Notes

- EXP-0003 made two post-hoc analysis corrections, both logged in the
  investigation's `CONFIG/changelog.jsonl`: (1) the original naive contour detector
  overcounted ~2.5x and was replaced by a certified intersection test; (2) the
  independent replication's FFT-moment predictor was replaced by the correct
  mode-weighted predictor for off-grid fields. The primary detector D1 and all
  primary H0 results were unaffected (deterministic field generation and seeds).
- EXP-0002 was run twice in one session: the first run's FDR post-processing used a
  buggy BH step-up (flagged all cells). The bug was found by EXP-0001's validation
  suite, fixed with a regression check, and EXP-0002 re-run. The investigation's
  `CONFIG/registry.jsonl` is append-only and contains both rows; the second row is
  authoritative.
- EXP-0004 was also run twice for the same reason, and the protocol made the first
  verdict unambiguous: the pre-fix battery over-rejected all three generators
  (INCONCLUSIVE = battery defect, S2), the fixes were applied, and the second run
  CERTIFIED. The investigation's `CONFIG/registry.jsonl` is append-only and contains
  both rows; the second is authoritative. No thresholds or test inventories were
  changed to reach CERTIFIED (details: `EXP-0004    REPORT/TECHNICAL_SUMMARY.md`).
- EXP-0006 re-ran the prepared fine-grid width-route follow-up and, in addition,
  implemented and run the previously-missing C7 independent implementation
  (`REPLICATION/independent_check.py` under `03_INVESTIGATIONS/PHYSICS/percolation/`;
  39/39 sampled cells bit-identical). Its registry has two identical EXP-0006 rows
  (prior session + this fresh deterministic re-run), consistent with the append-only
  discipline; the separated result store is `EXP-0006_summary.json`
  (`primary_results` + `estimator_diagnostics`).
- EXP-0007 closed Q-P004: bond_wrap FSS fit-goodness resolved by extending to six
  sizes (L=96/128/192 new, independent seeds; L=32/48/64 frozen EXP-0005).
  A dedicated C7 for the new streams is `REPLICATION/C7_exp0007_report.json`
  (78/78 bit-identical, p50 delta 0.000 at all L). Two mechanical wrapper bugs in
  the pre-designed runner were fixed at execution time (nu_gate look-up path;
  `all()` on a single bool); no statistic, gate, or prereg value changed, and the
  fixes are logged in the investigation's CHANGELOG. Frozen EXP-0005/0006 results
  untouched (hashes preserved).
- No experiment has yet produced an ANOM-#### entry.

## 2026-09-24 audit supersession notes (append-only)

These notes do not rewrite historical rows. They record why older completion
language must not be used as current evidence.

- **Q-P007 / historical refined-p-c closure:** NOT ACCEPTED as a scientific
  closure. The cluster-tail storage was structurally invalid and the repaired
  N-001 pipeline has completed smoke/infrastructure validation only. No
  production tau or refined-p-c result exists.
- **EXP-0011 / Q-P008 3D pilot:** historical width, p-c, and C7 claims are
  INVALID because cubic labels were checked with 2D slice boundaries. The old
  runner is disabled. Corrected infrastructure smoke is INCONCLUSIVE and no
  corrected production 3D result exists.
- **EXP-0013:** NOT COMPLETE. The nominal main run stopped during the L=256
  width phase; no `EXP-0013_results.json` was produced.
- **EXP-0003 broadband audit:** the independent fixed-spectrum audit supports a
  finite-resolution interpretation and makes no novelty claim. Its historical
  absolute-power normalization defect remains documented; density ratios are
  unaffected by global amplitude.
- Repair evidence: `AUDIT/REPAIR_LOG_20260924.md`.

## EXP-0015 — Discrete optical-vortex detection bias (2026-09-24)

- **Question:** Q-O006 — when does discrete optical-vortex detection produce
  systematic count bias relative to known continuous topology?
- **Hypothesis:** HYP-OPT-DVB-001; frozen preregistration at
  `03_INVESTIGATIONS/OPTICS/discrete_vortex_bias/CONFIG/prereg_EXP-0015.json`.
- **Status:** PARTIAL / LEVEL 1 / no novelty claim.
- **Completed:** analytical calibration for known single, pair, charge-two,
  and four-vortex fields; primary grid/z/wavelength/padding convergence;
  2048² square and rectangular oversample→downsample controls; null and
  six-seed random controls; detector-size and exact-zero sweeps; tracker;
  independent SciPy raw-winding and contour checks; fail-closed validation.
  The first supported-detector calibration, direct-reference controls, and
  timed-out exploratory runs are explicitly logged in the investigation change
  log.
- **Result:** the clean well-separated control is invariant; the rectangular
  contour excess is an implementation/downsampling artifact; close-pair
  annihilation agrees with a high-resolution reference; detector count
  semantics and charge representation explain the remaining discrepancies.
- **Plain statement:** the historical `z=1280 µm` physical-topology claim is
  not revived; this experiment characterizes detector/sampling bias as a
  narrower numerical-science question and does not establish new physics.

## EXP-0016 — Topology-measurement definition experiment (2026-09-24)

- **Question:** Q-O007 — under what conditions do discrete representations of
  optical phase topology disagree about singularity count, charge, or identity?
- **Hypothesis:** HYP-OPT-TMD-001; frozen preregistration at
  `03_INVESTIGATIONS/OPTICS/topology_measurement_definition/CONFIG/prereg_EXP-0016.json`.
- **Status:** COMPLETE / measurement-definition result / no novelty claim.
- **Completed:** 1,652-row phase diagram; exact/subpixel controls; raw,
  clustered, circular-contour, and Jacobian estimators; close-pair and
  four-vortex controls; propagation/annihilation subset; plane-wave and
  smooth-phase nulls; matched random-phase stress; 96-trial uncertainty subset;
  2048² reference/downsample and padding controls; explicit boundary-crossing
  controls with full-padded/cropped comparison; independent NumPy/SciPy
  replication; fail-closed validation.
- **Result:** “vortex count” is not a representation-independent scalar. Raw
  winding cells, connected components, estimated locations, and charge mass
  diverge systematically for charge-two and close-pair cases. Contour/Jacobian
  failures concentrate in a subpixel-core regime; no universal detector-
  independent failure law or physical anomaly is established.
- **Validation:** `RESULTS/validation_summary.json` = `PASS`.
- **Report:** `03_INVESTIGATIONS/OPTICS/topology_measurement_definition/REPORT/TECHNICAL_EXP-0016.md`.
- **Promotion rule:** no result may be called a discovery without a surviving
  physical residual, preregistered dimensionless law, complete null program,
  independent implementation, and expert/laboratory review. Those gates are
  not met; the historical physical claims remain rejected.

## EXP-0017 - Balanced power-of-two vs non-power-of-two lattice test (2026-09-26)

- **Question:** Q-P009 / audit finding N-005 (Priority 1) — after matching
  physical size, estimator, and random-stream policy, is there a reproducible
  power-of-two effect on the 2D site cluster-mass exponent?
- **Hypothesis:** HYP-P009; frozen preregistration at
  `03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/CONFIG/prereg_EXP-0017.json`
  (`config_sha256 9de382eb7bba2853f1ab4cd33441595c5c5611cd2310563221046c3e3f27aa8e`).
- **Status:** COMPLETE / **LATTICE_ARTIFACT_UNSUPPORTED** / no novelty claim.
- **Design:** nested common-random-numbers pairs (one L x L field yields every
  sub-window size, so a power-of-two size and its neighbour share every random
  number); fully independent-stream cross-check; null contrast between two
  adjacent NON-power-of-two pairs; 2-adic ladder at bases 256 and 512;
  pre-registered equivalence margin 0.010, which is 2.65x smaller than the
  0.0265 historical deficit it would have to explain.
- **Gates:** all passed. C1 raw round-trip 36/36 bit-exact; C2 mass bounds;
  C3 nested monotonicity; **C7 second implementation 160/160 cells exact**;
  **C8 from-scratch BFS census 30/30 cells exact**; C9 exact-zero and all-open
  sanity fields; C10 realization counts as preregistered.
- **Result:** D_f over the power-of-two ladder {128,256,512,1024} = 1.882715;
  over the non-power-of-two ladder {127,255,511,1023} = 1.884116;
  **beta = -0.0014003**, 90% interval [-0.003890, +0.000797]. The whole 90%
  interval lies inside +/-0.010, so the frozen rule returns
  `LATTICE_ARTIFACT_UNSUPPORTED`. |beta| is 5.3% of the historical deficit.
  Pooled absolute D_f = 1.880462, 95% interval [1.851317, 1.911041], which
  contains the reference 91/48 = 1.895833.
- **Honest negatives:** the independent-stream arm is underpowered at n=40
  (beta = +0.014, 90% interval [-0.071, +0.102]), excludes nothing, and its point
  estimate has the opposite sign; per the pre-registered operational definition
  of "contradicts" it is recorded as underpowered, not contradictory. The
  corrected estimator has a measured sensitivity of about 0.009 per unit of
  shared quadratic log-log curvature. A second independently estimated threshold
  arm was NOT run and remains open.
- **Methodological error recorded, not hidden:** the first analysis used a local
  finite-difference slope estimator that divides by log(hi/lo) ~ 1e-3 at L=1024
  and so amplifies noise ~1e3. It was diagnosed by its own preregistered null
  control returning +0.313, LARGER than the primary contrast of -0.290, and by
  self-contradictory ladder slopes (1.106 +/- 0.002 vs 3.913 +/- 0.055). That
  analysis returned INCONCLUSIVE_BY_RESOLUTION, supported nothing, and is
  preserved as `EXP-0017_summary_v1_local_slope_SUPERSEDED.json`. The primary
  statistic was replaced with the standard balanced slope-functional contrast,
  validated on synthetic data BEFORE adoption (null -> 0.00000; injected
  +/-0.0265 -> +/-0.02650). No measured value was used to choose the estimator,
  the raw artifact was not modified, and no new data was collected for the
  change. Reasoning is hash-chained in `CONFIG/changes.jsonl` (5 entries).
- **What it does NOT do:** it does not modify, revive, or overturn EXP-0009 or
  EXP-0010. It removes power-of-two lattice sizes as a candidate explanation for
  the 1.8697 vs 1.8962 difference. Why EXP-0009 landed ~1 sigma low remains open.
- **Validation:** 25 focused tests pass; artifact `validate` returns PASS;
  change chain verified.
- **Report:** `03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/REPORT/TECHNICAL_EXP-0017.md`
  and `REPORT/PLAIN_EXP-0017.md`.

## N-001-PRODUCTION - 2D cluster-mass exponent tau at the exact site threshold (2026-09-26)

- **Investigation:** Q-P007 · **audit finding:** N-001 (Priority 0, the only
  open Priority-0 item).
- **Frozen decision rule:** `Q-P007/AUDIT_REPAIR_N001/CONFIG/prereg_N001_PRODUCTION.json`
  (`config_sha256 f5473ff0971f6e8a11e660e8401a01b00c31db56c11637f43cefa424914e5502`),
  bound to the repair config and to the production profile object by SHA-256.
- **Verdict under the frozen rule:** **`DEVIATION_FROM_FISHER`**. Escalation
  trigger, **not** a discovery. No novelty claimed.
- **Blocker found and fixed first:** the production path was structurally
  unrunnable. The runner recorded the preregistration lock by its CANONICAL
  PAYLOAD hash while the artifact validator compared it against the EXACT FILE
  BYTE hash; a frozen document embeds its own digest, so those can never match
  and every production run failed closed *after* completing all measurement work.
  Same canonical-vs-byte scope confusion the audit fixed elsewhere (N-14), missed
  here. Fixed to re-verify the canonical digest via `verify_frozen_config()`;
  regression test added; N-001 tests **15 passed** (was 14); authoritative smoke
  regenerated as `SMOKE_N001_V4` (PASS), with V3 and earlier retained as
  superseded evidence.
- **Design as executed:** 2D square site percolation, 4-connectivity, open
  boundaries; p = 0.59274605079210 (canonical) and 0.5927289999999997 (refined)
  as paired arms on one common uniform field per realization; L = 256/512/1024
  with n = 100/100/50; active `tau_L` = 1024; one flat non-increasing int64
  cluster array per (L, realization, arm) in SQLite; exactly one largest-cluster
  entry removed per realization per arm; 2000-draw realization-block bootstrap
  with `block_size=1`, paired across arms.
- **Integrity:** requested/effective realizations at `tau_L` 50/50 in both arms;
  bootstrap draws successful 2000/2000; pooled tail clusters 1,462,967; raw
  SQLite 60,383,232 B; manifest 381 KB; both hash-bound.
- **Result (primary = cumulative, canonical, window `primary_32_4096`, L=1024):**
  **tau = 1.92009**, 95% realization-block interval **[1.90739, 1.93348]**,
  excluding 187/91 = 2.0549451 by -0.13486.
- **Robustness gate: PASSED.** All four preregistered windows' cumulative
  intervals exclude 187/91 (1.912-1.936 across windows). The histogram estimator
  is far less stable (1.607-1.966), confirming the preregistration's decision to
  make cumulative primary and the histogram a correlated-bin diagnostic only.
- **Secondary, clean negative:** paired refined-minus-canonical delta =
  -0.000028, 95% paired interval [-0.000666, +0.000356]; **every** window's paired
  interval contains zero -> `NO_RESOLVABLE_REFINED_EFFECT`. The refined threshold
  is ruled out as an explanation at this resolution.
- **Honest ambiguity, stated in the report:** this lab documented *before* the run
  that finite-domain crossover yields an apparent exponent ~1.8-2.0 at s~10-10^3
  that converges to 187/91 only asymptotically (EXP-0009 preregistration). The
  measured 1.920 lies inside that band and rises toward Fisher as the window
  narrows to smaller s (1.936 at s in [16,512]). **The design cannot separate
  finite-size crossover from a failure of the Fisher exponent; both remain
  open.** A DEVIATION here is a statement about L=1024, not about 2D
  percolation. Larger L or a finite-size extrapolation is required.
- **Also recorded:** the historical value was 1.98 and the corrected value is
  1.920, i.e. *further* from Fisher. The repair did not "recover" the exponent;
  the historical 1.98 was an invalid number, and no narrative in which better
  storage recovered the asymptotic value is supported.
- **Post-run resolution:** the design resolves a tau change of about 0.017 at 95%
  confidence, so the observed 0.135 deviation is well resolved statistically.
  It is the single lattice size, not the statistics, that limits interpretation.
- **Reports:** `Q-P007/AUDIT_REPAIR_N001/REPORT/TECHNICAL_N001_PRODUCTION.md` and
  `REPORT/PLAIN_N001_PRODUCTION.md`.

## N-004-PRODUCTION - per-test dependence-aware RNG battery calibration (2026-09-26)

- **Investigation:** Q-I004 · **audit finding:** N-004 (Priority 1).
- **Frozen protocol:**
  `OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/CONFIG/prereg_N004_PRODUCTION.json`
  (`config_sha256 91b5ebd0be6020f578d80fd0b083d26ff5f2837b86c0b3577ae730d450a60136`).
- **Battery verdict: `BATTERY_VALID`. G_LAB status: `INTERPRETABLE` — 0 of 24
  tests miscalibrated at both stream lengths.**
- **The historical EXP-0004 "CERTIFIED" conclusion remains WITHDRAWN and is NOT
  reinstated.** `certification_claim: false`,
  `historical_certificate_reinstated: false`. No generator is certified.
- **Design:** the shared battery `engine.validation.rng_battery` (24 tests,
  SHA-256 checked at runtime and on validation, never modified); four generators
  — `G_LAB` (target), `PCG64_direct` and `MT19937` (references), and
  `WEAK_LCG_BROKEN` (a 31-bit LCG as a **positive control that must fail**);
  2^18 with 200 seeds and 2^22 with 60 seeds per generator; fresh seed namespace
  disjoint from all historical ranges; 1040 evaluations, 8 workers, 377 s,
  **0 errors**, 24,960 raw rows in SQLite.
- **Primary statistic (the audit's actual question):** per-test KS uniformity of
  p-values across INDEPENDENT seeds, BH-FDR across the 24 tests per cell — not a
  pooled pass/fail. Secondary: exact Clopper-Pearson band on rejection rates, and
  Holm / Šidák / uncorrected family-wise rates.
- **Positive control passed decisively:** `WEAK_LCG_BROKEN` family-wise rate
  **1.000** at both lengths; `T13_words` rejects **100%** of seeds (KS p = 0);
  `T03_runs` also flagged. The battery is therefore fit to interpret G_LAB.
- **G_LAB result:** **0/24 miscalibrated at 2^18 (n=200) and 0/24 at 2^22
  (n=60)**; every rejection rate inside its exact binomial band; mean p-values
  clustered in [0.431, 0.581] across all tests and both lengths.
- **Headline finding — the audit's criticism, now measured:** with 24 tests
  sharing one input stream, the **uncorrected** family-wise rejection rate is
  **0.160–0.233** per seed against a nominal 0.01, an inflation of **12× to
  41×** (G_LAB 2^18: 0.205 uncorrected vs 0.005 Bonferroni = 41×). Correcting for
  the family returns the rate to 0.000–0.017. The shared-stream dependence is
  real, large, and fully accounted for by a dependence-respecting correction.
  Withdrawing the EXP-0004 certificate was correct, and this is the first
  quantitative demonstration of why.
- **One genuine instrument defect, reported honestly:** `T03_runs` (NIST 2.3) is
  the only problematic test. It never rejects (rate 0.000, in band everywhere),
  but its p-value distribution is skewed high (mean 0.556–0.576 vs 0.5), i.e.
  mildly conservative, and the flag is **unstable** — statistically equivalent
  PCG64 constructions get opposite classifications (G_LAB not flagged,
  `PCG64_direct` flagged, at the same n=200). Correct reading: **borderline /
  UNRESOLVED** for all generators, and the one test whose p-value formula
  deserves an independent check against the NIST reference.
- **Binding resolution limit, preregistered:** rejection-rate SE is 0.0071 at
  S=200 and 0.0127 at S=60; the 2^22 binomial band is [0.000, 0.085]. A
  miscalibration shifting the true rate from 0.01 to below ~0.04 is undetectable
  here. "Calibrated" means "no miscalibration detected at this resolution",
  never "proven exact".
- **Three defects I introduced and caught before acceptance**, all hash-chained in
  `CONFIG/production_changes.jsonl` (3 entries): (1) the preregistered "max-T
  permutation" family-wise control was **mathematically inert** — the maximum is
  permutation-invariant, so permuting p-values makes the null equal the observed
  maximum, and a preflight caught it reporting 0.000 rejection for the broken
  generator that Holm rejects 12/12; replaced with Bonferroni, which is valid
  under arbitrary dependence. (2) and (3) two **fail-open** runner defects: the
  first attempt lost the entire MT19937 arm yet exited 0; the second reported
  24,960 rows written while the table held 0. The runner now refuses to write a
  manifest unless every preregistered cell is complete, and asserts stored row
  and complete-seed-vector counts after commit. Both failed attempts are preserved
  as `..._INCOMPLETE_MT19937_ARM` and `..._V2_NO_RAW_ROWS`.
- **Validation:** artifact `validate` returns PASS with
  `battery_verdict=BATTERY_VALID`.
- **Reports:** `AUDIT_REPAIR_N004_PRODUCTION/REPORT/TECHNICAL_N004_PRODUCTION.md`
  and `REPORT/PLAIN_N004_PRODUCTION.md`.


## EXP-A01 - T03_runs estimator audit (2026-09-28)

- **Question:** Q-I004 / audit finding N-004 follow-up. Is the shared RNG
  battery's `T03_runs` a valid instrument at the stream lengths this lab uses?
- **Verdict:** `ESTIMATOR_DEFECTIVE`. Defect: `t_runs` routes the NIST
  SP 800-22 Rev 1a section 2.3 statistic through the `_erfc_p` helper, which is
  the z-score identity `erfc(|z|/sqrt(2)) = 2(1-Phi(|z|))`. That helper is
  CORRECT for `t_monobit` and `t_dft` (both verified), but the runs statistic
  is already in erfc units, so the helper applies a spurious `sqrt(2)` and
  inflates every p-value. The standard's section 2.3 step 1 applicability
  precondition `|pi - 1/2| >= 2/sqrt(n-1)` is also absent; it requires a ~4
  sigma deviation in the bit balance and is met by 0 of 200 seeds.
- **Evidence:** paired comparison, identical streams, 200 fresh G_LAB seeds.
  At 2^18 shared KS p = 6.7e-06 with 0/200 rejections at alpha = 0.01 versus
  reference KS p = 0.847 with 1/200. At 2^22 shared 9.1e-11 / 0 of 200 versus
  reference 0.106 / 1 of 200. Stored N-004 rows show the pile-up in all four
  generators including the deliberately broken LCG (KS p = 3.1e-08) with zero
  rejections anywhere, so the test was detecting its own defect.
- **Supersedes:** the N-004 per-test claim that 0 of 24 tests were miscalibrated
  for G_LAB. 23 of 24 per-test cells are calibrated at these resolutions;
  `T03_runs` is not.
- **Does NOT overturn:** the family-level `BATTERY_VALID` verdict, which rests
  on the positive control being rejected at the family-wise level by other
  tests. The EXP-0004 certificate stays WITHDRAWN.
- **Controls:** frozen preregistration (`8ffc034d...`) with a falsification
  direction that reports a null result just as readily; independent reference
  implementation written from the published procedure; fail-closed runner that
  refuses to execute unless the audited battery still hashes to the digest
  recorded in the N-004 raw database; the audited module was NOT modified; raw
  artifacts, the 2026-09-24 baseline, and every stored p-value are unmodified;
  supersession hash-chained as `559358ce...` in the N-004 production change
  log; 22 conformance/regression tests.
- **Evidence:** INSTRUMENT CALIBRATION. Not a physical result. No generator is
  certified. A defective instrument is not evidence that G_LAB is defective; the
  reverse is the finding.
- **Reports:** `AUDIT_REPAIR_T03_RUNS_FORMULA/README.md` and
  `RESULTS/T03_FORMULA_AUDIT_20260928/`.

## INFRA-2026-09-28 - read-only 2D percolation audit registry pin repaired

- **Problem:** that audit pinned `EXPERIMENT_REGISTRY.md` by whole-file
  SHA-256, so it reported 10 pytest errors every time an experiment was
  registered, creating standing pressure to refresh the immutable baseline and
  thereby defeat the control.
- **Fix:** the registry's **historical prefix** is pinned byte-for-byte in a
  frozen artifact whose digest is REQUIRED to equal the baseline's whole-file
  digest, which proves the frozen bytes are the originally audited content and
  not a re-freeze of today's file. Appends are permitted, measured and reported;
  edits, reorderings, deletions and prepends inside the audited region still
  fail closed.
- **Not refreshed:** the 2026-09-24 baseline and its run-manifest digest; a test
  asserts this explicitly. 50 of 51 pinned inputs remain whole-file pinned.
- **Evidence:** INFRASTRUCTURE ONLY. All five corrected classifications are
  byte-for-byte unchanged. Suite 391 passed / 10 errors -> 418 passed / 0 errors.


## EXP-A02 - T03_runs corrected re-derivation + full _erfc_p caller audit (2026-09-28)

- **Question:** Q-I004 / N-004 follow-up. What should the N-004 T03_runs cell for
  G_LAB have recorded once the spurious sqrt(2) is removed and the standard's
  applicability precondition is enforced?
- **Design:** three variants evaluated on IDENTICAL bit streams (200 fresh G_LAB
  seeds at 2^18 and 2^22) - as-implemented, sqrt(2)-corrected, and
  sqrt(2)-corrected with the SP 800-22 section 2.3 step 1 applicability gate.
  Frozen preregistration `3d03a118...` with a decision rule that treats fewer
  than 5 applicable seeds as unresolvable.
- **Found:** the spurious sqrt(2) explains the ENTIRE recorded non-uniformity.
  As-implemented KS p = 1.4e-05 (2^18) and 8.8e-06 (2^22); sqrt(2)-corrected
  KS p = 0.343 and 0.956, with corrected mean p within 0.01 of the uniform mean.
- **Found:** even corrected the test is NOT SCORABLE at these lengths. The
  applicability condition `|pi - 1/2| >= 2/sqrt(n-1)` is met by **0 of 200
  seeds** at both lengths: it demands a ~4-sigma deviation in the bit balance
  while a fair stream deviates 0.0008 against a 0.0039 threshold.
- **Status of record:** `UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION` at both
  lengths. Corrected N-004 statement: **23 of 24** per-test cells calibrated,
  **0** miscalibrated, **1** unresolvable. An unresolved cell is reported as
  unresolved, never as agreement.
- **Full helper audit:** exactly one of the five `_erfc_p` callers passes an
  erfc-unit argument. `t_monobit`, `t_dft`, `t_nontemplate` and
  `t_autocorr` pass genuine z-scores and are empirically uniform at both
  lengths, so the helper is correct for them and `T03_runs` is the sole
  defect. `t_nontemplate` remains a documented structural deviation from
  section 2.7's chi-square form whose normal approximation is sound at these
  lengths (expected match count about 57).
- **Limit recorded on the finding itself:** the extra sqrt(2) is provable as an
  exact algebraic identity, but its empirical DETECTION is resolution- and
  seed-dependent - caught at 2^18 and missed at 2^22 under one seed labelling,
  caught at both under another. Non-detection is never read as correctness.
- **Two fail-open defects of my own, introduced and fixed during this work:**
  the caller audit first reported the autocorrelation cell
  `CONFIRMED_CALIBRATED` having measured zero p-values (an absent measurement
  read as a pass), and its pooled key set never resolved. The audit now raises on
  a declared key that is not collected and classifies an unmeasurable cell
  `UNRESOLVED_NO_MEASUREMENT`. Both covered by tests.
- **Controls:** preregistration frozen before execution with the falsification
  direction reportable; shared battery hash-checked at runtime and NOT modified;
  N-004 raw database opened read-only and unmodified; supersession hash-chained
  as `e06ce1d5...`; 39 tests in the repair area.
- **Not overturned:** the N-004 family-level `BATTERY_VALID` verdict. The
  EXP-0004 certificate stays WITHDRAWN.
- **Evidence:** INSTRUMENT CALIBRATION. Not a physical result. No generator is
  certified. A defective or inapplicable instrument is not evidence that G_LAB
  is defective; the reverse is the finding.
- **Reports:** `AUDIT_REPAIR_T03_RUNS_FORMULA/README.md` and
  `RESULTS/T03_RECALIBRATION_20260928/`.


## EXP-A03 - N-001 crossover diagnostic and tau estimator validation (2026-09-28)

- **Question:** Q-P007 follow-up. (i) Is the N-001 deviation from the Fisher
  exponent finite-size crossover? (ii) Is the production estimator that measured
  it trustworthy? Both answered on **already-stored data with no new Monte
  Carlo**: the production kept one cluster-size array per realization at
  L = 256, 512, 1024, totalling 2.39 million tail clusters.
- **(i) `CROSSOVER_NOT_ESTABLISHED`** (prereg `de231ef6...`, informed and
  labelled as such). The preregistered theory-derived prediction - a periodic box
  has p_c(L) above the infinite-volume value, so the sampled box sits slightly
  disordered and tau must rise with L - is **violated**:

  | L | realizations | tail clusters | tau | deviation from 187/91 |
  |---|---|---|---|---|
  | 256 | 100 | 188921 | 1.90306 | -0.15189 |
  | 512 | 100 | 740653 | 1.88981 | -0.16513 |
  | 1024 | 50 | 1462967 | 1.92009 | -0.13486 |

  Slope d(tau)/d(ln L) = **+0.0123**, 95% interval **[-0.0232, +0.0478]**
  includes zero. The deviation is nearly size-independent. A shrinking offset is
  the crossover signature; a constant offset is not. The extrapolated "required
  L" of ~1e8 is marked `extrapolation_is_meaningful: false` and a test forbids
  quoting it as a system size.
- **(ii) The production estimator is `ESTIMATOR_BIASED`** (prereg
  `f37cc2d4...`). Building synthetic distributions of a KNOWN exponent and
  measuring each estimator's error shows the frozen cumulative estimator returns
  values **+0.11 to +0.35 too large**, reproducibly across three independent
  constructions and both tested true exponents (1.85 and 2.05), while the
  **histogram estimator is unbiased to within 0.008** and is therefore the
  yardstick.
- **Two candidate mechanisms tested and REJECTED, both recorded:** the off-by-one
  in the survivor count (fixing it made the bias slightly worse) and the residual
  weighting (unweighted OLS worse still; the correct Poisson weight reduced but
  did not remove the bias).
- **The correction strengthens the deviation rather than dissolving it.** The bias
  is consistent across the two truths, so the preregistered rule permits a
  labelled secondary estimate: stored 1.92009 corresponds to about **1.81**, and
  the unbiased histogram estimator independently gives **1.70**. Both are
  **further** from 187/91 = 2.054945 than the reported value, and every window
  under every estimator lies below it. The lab's own instrument bug made its
  anomaly look *smaller* than it is.
- **Controls:** independent re-implementation of the estimator reproduces the
  stored production tau with delta = 0.000e+00 and all four stored window values
  to 1e-12; fail-closed digest guard on the 60 MB raw database; realization-block
  bootstrap, never cluster-level; paired canonical-vs-refined arms (max |delta|
  = 0.00072, so threshold refinement is not the cause); hash-chained as
  `f4f01ffc...`; 38 tests. The estimator correction was applied only because a
  preregistered two-truth test showed it transferable, and a companion test proves
  the rule refuses a correction when the two truths disagree.
- **Not edited:** the frozen production value 1.920086094899, the production
  runner, the raw database, and the production decision. The N-001 escalation
  `DEVIATION_FROM_FISHER` **stands, strengthened in direction and magnitude**.
- **Recorded, not corrected:** the production manifest's `pairing` field carries
  stale text `iid_cluster_bootstrap` although the code resamples realization
  blocks; and the status line's "1,462,967 pooled tail clusters" is the active
  L = 1024 size alone, with pooling across all three sizes shifting tau by
  -0.0115.
- **Evidence:** INSTRUMENT CHARACTERISATION plus a diagnostic of an existing
  escalation. No physics claim, no novelty claim, no new simulation. Q-P007
  remains open; the magnitude of its deviation is now untrusted and its direction
  is robust.


---

# APPENDED 2026-10-04 — registry completeness note

*Appended below the byte-pinned historical prefix, not inserted above it. See the
note on why that matters.*

## Three experiments had detail sections but no row in the summary table

A reader consulting only the table at the top of this file would not know these
existed:

| ID | state before this note |
|---|---|
| EXP-0015 | detail section present, no table row |
| EXP-0016 | detail section present, no table row |
| EXP-0017 | detail section present, no table row |

Their detail sections already state question, hypothesis, status and result.
They are recorded here rather than in the table because the table lies inside the
region this file's audit pins by digest, and editing that region is precisely what
the control exists to prevent.

## EXP-0013 has neither a row nor a detail section

The identifier appears in prose only. No preregistration, results directory, or
experiment config could be found for it. Recorded here as `NOT REGISTERED` rather
than silently omitted, because an unexplained gap in an append-only registry is
itself a defect: either an experiment was allocated and never run, or an
identifier was allocated in error. **Which of those is true is not recoverable
from these files**, and saying so is more useful than leaving a silent hole.

## EXP-0012 is skipped with no explanation

The header states identifiers are "allocated in order when an experiment is
preregistered (never reused, never deleted)", which makes a gap a record-keeping
event in its own right. No allocation or cancellation note exists for it.

## Why this note is appended rather than merged into the table

The read-only audit at
`AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924` pins the first 17,841 bytes of this
file by SHA-256 and fails closed on any change inside that region.

That control caught this very edit. Adding the three missing rows to the table
put a change inside the pinned prefix and the audit failed with:

    append-only evidence changed inside its audited region:
    EXPERIMENT_REGISTRY.md expected prefix sha256 888f11e1..., actual 2a44d1b2...

The change was reverted and re-applied here instead. **That is the control
working exactly as designed**, and it is worth recording: the first attempt to
"fix" an incomplete registry would have destroyed the guarantee that the registry
has not been rewritten. The tempting repair — re-freeze the baseline so the test
passes — would have laundered the modification. The whole point of the
append-only prefix pin is that a registry cannot be quietly edited, and that
includes edits made with good intentions.

## Scope of this note

Adds no experiment, revises no result, and changes no evidence level. It records
what the file does and does not contain. Three gaps are documented rather than
closed, because closing them requires knowing what happened, not just that
something is missing.
