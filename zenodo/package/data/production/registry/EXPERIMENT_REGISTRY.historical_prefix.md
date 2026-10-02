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
