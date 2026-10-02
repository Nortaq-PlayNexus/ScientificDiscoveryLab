# EXECUTION PLAN — 11 Next-Batch Questions (2026-09-19)

Derived from 2026-09-18 session results (Q6/Q6f/Q7/Q8/Q9).
All 9 original questions (Q1-Q9) are COMPLETE.
11 new candidate questions registered in QUESTIONS.md.

---

## Organization

- **Group A**: Do NOW in this session (can start immediately, all dependencies satisfied)
- **Group B**: Set up now, execute this session or next (setup possible, computation may span sessions)
- **Group C**: Plan for next session (heavy compute or complex setup that needs Group A/B outputs first)

---

## Group A — Do NOW in this session

---

### Q-M007: Per-bin residual analysis of EXP-0008 prime gaps (HIGH, zero compute)

**What needs to be done**
- Read EXP-0008 results (`03_INVESTIGATIONS/MATHEMATICS/prime_gaps/RESULTS/EXP-0008_results.json`)
- Extract per-block chi2 counts, edges, expected values (already in JSON under `primaryResults.blocks[].counts`, `.edges`, `.expected`)
- For each of 10 exponential quantile bins x 4 blocks, compute:
  - Per-bin χ² contribution: (observed - expected)² / expected
  - Standardized residual: (observed - expected) / sqrt(expected)
  - BH-FDR-adjusted p-value (from existing tail data, extend to all 10 bins)
- Compare to hypothesis: deviation concentrated at extreme tail (j=9,10) vs spread across all bins

**Files/directories to create**
- `03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/` (new sub-investigation folder)
  - `QUESTION.md` — question spec (from NEXT_BATCH_20260919.md §Q-M007)
  - `CODE/analyze_bins.py` — analysis script (reads EXP-0008 JSON, outputs per-bin table)
  - `RESULTS/Q-M007_perbin_analysis.json` — full per-bin results
  - `REPORT/Q-M007.md` — report

**Dependencies**
- None (zero compute). Uses existing EXP-0008 results only.
- Must read EXP-0008 data structure first (already done here).

**Estimated compute time**
- ~1 second (pure analysis, no re-computation)

**Dependencies on other questions**
- None. Q-M007 output may inform Q-M008 interpretation but is not a hard dependency.

**Immediate next action**
- Create `Q-M007/` folder + `QUESTION.md` + `analyze_bins.py`, run it against EXP-0008 JSON.

---

### Q-S9-2: REBUS dose-response curve (MEDIUM, low compute)

**What needs to be done**
- Use `code/dmt-laser-s9-battery/perceptual_sim.py` as base (already has sober/dosed rates for A/B/C/D)
- Extend to dose levels: 0%, 10%, 20%, ..., 100% DMT intensity
- For each dose level, simulate N subjects x n_trials per condition (A/B/C/D)
- Fit Hill equation: f(dose) = baseline + (max_inflation - baseline) * dose^n / (EC50^n + dose^n)
- Report EC50, Hill coefficient, max inflation factor
- Test hypothesis: EC50 ≈ 30-50%, max inflation ≈ 50-80%

**Files/directories to create**
- `code/dmt-laser-s9-battery/dose_response.py` (NEW — dose-response simulator + Hill fitter)
- `code/dmt-laser-s9-battery/RESULTS/dose_response.json` (NEW — fit results)
- `code/dmt-laser-s9-battery/FIGURES/dose_response_curve.png` (NEW — visualization)

**Dependencies**
- `perceptual_sim.py` (exists, use as base)
- `analysis.py` (exists, use for BH-FDR + effect sizes)
- No other Q dependencies

**Estimated compute time**
- Minutes (parametric simulation: 11 dose levels x 4 conditions x 30 subjects x 50 trials = 66,000 trials)

**Dependencies on other questions**
- None independent. Results feed into Q-S9-1 (spectral complexity threshold) and Q-S9-3 (detector de-biasing).

**Immediate next action**
- Write `dose_response.py` extending the simulator, run, fit Hill equation.

---

### Q-X2: Continuous coherence-perception response curve (MEDIUM, low compute)

**What needs to be done**
- Use `code/dmt-laser-s9-battery/wavelength_ladder.py` as base (already tested 450/532/650 nm)
- Extend to 12+ coherence levels (from fully incoherent to fully coherent)
- At each coherence level, measure detection rate (same framework as §9 battery)
- Fit response curve (test linear, log, sigmoidal hypotheses)
- Report coherence threshold for detection

**Files/directories to create**
- `code/dmt-laser-s9-battery/coherence_curve.py` (NEW — extended wavelength/coherence ladder)
- `code/dmt-laser-s9-battery/RESULTS/coherence_curve.json` (NEW — response data + fit)
- `code/dmt-laser-s9-battery/FIGURES/coherence_response.png` (NEW — plot)

**Dependencies**
- `wavelength_ladder.py` (exists, reuse framework)
- `stimulus_gen.py` (exists, for stimulus generation at various coherence levels)
- `analysis.py` (exists, for stats)

**Estimated compute time**
- ~30 min (12+ coherence levels x 4 wavelengths x 30 subjects x 50 trials)

**Dependencies on other questions**
- None independent. Informs Q-S9-1 (minimum spectral structure).

**Immediate next action**
- Write `coherence_curve.py`, extend §9 battery to 12 coherence levels, run.

---

### Q-S9-4: §9.8 cone-mosaic aliasing sober check — simulate fringe stimuli (MEDIUM, moderate compute)

**What needs to be done**
- Simulate high-spatial-frequency coherent interference fringes (60-120 c/deg) using sandbox ASM/speckle generators
- Model expected "free-draw" responses of sober subjects (use §9 perceptual_sim framework + existing catalogue statistics)
- Compare simulated sober-draw distribution against catalogue of reported geometric hallucination drawings (Grove et al. 2026, 10,598 drawings)
- Test hypothesis: most "stable lattice" drawings can be reproduced sober by cone-mosaic aliasing

**Files/directories to create**
- `03_INVESTIGATIONS/OPTICS/cone_mosaic_aliasing/` (new investigation folder, or use `code/dmt-laser-s9-battery/` extension)
  - `QUESTION.md` — question spec
  - `CODE/fringe_simulator.py` — generates fringe stimuli at 60-120 c/deg
  - `CODE/draw_model.py` — models sober free-draw response distribution
  - `CODE/compare_catalogue.py` — compares against Grove 2026 catalogue stats
  - `RESULTS/aliasing_sober_check.json`
  - `REPORT/Q-S9-4.md`

**Dependencies**
- `code/coherent-optical-ai-sandbox` — ASM/speckle generators (for fringe creation)
- `code/dmt-laser-s9-battery/perceptual_sim.py` — response model framework
- Grove et al. 2026 catalogue statistics (need to define format; reference: 10,598 drawings, geometric categories)
- §9.9 simulation framework (already built)

**Estimated compute time**
- 1-2 hours (fringe generation across spatial frequency band + simulation + comparison)

**Dependencies on other questions**
- None hard. May share infrastructure with Q-S9-1 (spectral structure threshold).

**Immediate next action**
- Design fringe stimulus specification (60-120 c/deg range, 10-15 frequency steps), write `fringe_simulator.py`, run initial batch.

---

## Group B — Set up now, execute this session

---

### Q-P006: Precision study of 2D percolation critical exponents (MEDIUM, CPU-hours)

**What needs to be done**
- Reuse EXP-0009/EXP-0010 machinery (same prereg gates, same C7 independent implementation)
- Run percolation at L ∈ {512, 1024, 2048} with significantly more realizations
- Bootstrap 2000 draws per exponent for full UQ
- Measure all 5 exponents (D_f, γ/ν, β/ν, τ, 1/ν) at each L
- Test hypothesis: deviations from theory shrink with L (lattice artifact)
- Falsification: if deviations don't shrink, systematic effect exists

**Files/directories to create**
- `03_INVESTIGATIONS/PHYSICS/percolation/Q-P006/` (new sub-investigation folder)
  - `QUESTION.md`, `HYPOTHESIS.md`, `PREDICTIONS.md`, `CONTROLS.md`, `LITERATURE.md`
  - `CODE/run_exp0011.py` — runner (modeled on `run_exp0009.py` but for L={512,1024,2048})
  - `CODE/RESULTS/` — cell persistence files (`_cells_L*.npz`)
  - `CONFIG/prereg_EXP-0011.json` — prereg (frozen before execution)
  - `CONFIG/EXP-0011_experiment.json`
  - `REPLICATION/C7_exp0011.py` — independent implementation
  - `REPORT/` — reports
  - `RESULTS/EXP-0011_results.json`, `_summary.json`

**Dependencies**
- `percolation/ENGINE/perc_engine.py` — core engine (exists)
- EXP-0009 results as reference (for comparison to theory)
- EXP-0010 methodology (non-P2 sizes proven reliable)
- `04_SHARED_ENGINE/engine/reproducibility/` — registry functions
- C7 independent implementation required (per lab discipline)

**Estimated compute time**
- CPU-hours: L=2048 is 4x L=1024, ~16x L=512. With n_real scaling and 2000 bootstrap draws, estimate 8-24 hours total across 3 sizes.
- Use background execution (`Start-Process -NoNewWindow`) to avoid timeout.

**Dependencies on other questions**
- Q-P007 benefits from Q-P006 infrastructure (same sizes, same methodology)
- Q-P008 (3D) uses same engine but is independent

**Immediate next action**
1. Create Q-P006 folder + QUESTION.md + prereg (freeze before first computation)
2. Write `run_exp0011.py` adapted from `run_exp0009.py` with L={512,1024,2048}, n_real={2000,4000,8000}, bootstrap=2000
3. Start background run; verify first cells appear correctly
4. Periodically check progress (cell persistence files)

---

### Q-P007: Generalized lattice-artifact diagnostic — all geometric measures (MEDIUM, CPU-hours)

**What needs to be done**
- Measure γ/ν, β/ν, τ, 1/ν at both P2 and non-P2 L values near the P2 sizes where EXP-0009 found deviations
- Specifically: at P2 sizes where EXP-0009 missed tolerance (L=128,256,512,1024), compare with nearby non-P2 sizes
- Per Q-P005 EXP-0010 precedent: non-P2 L ∈ {127,191,253,449} for D_f; extend to all 5 exponents
- Test hypothesis: if a measurement misses tolerance at P2 but agrees at nearby non-P2, it is a lattice artifact
- Falsification: if a measurement misses at BOTH P2 and non-P2, genuine finite-size correction

**Files/directories to create**
- `03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/` (new sub-investigation folder)
  - `QUESTION.md`, `HYPOTHESIS.md`, `PREDICTIONS.md`, `CONTROLS.md`
  - `CODE/run_exp0012.py` — runner
  - `CONFIG/prereg_EXP-0012.json` — frozen prereg
  - `CONFIG/EXP-0012_experiment.json`
  - `REPLICATION/C7_exp0012.py`
  - `RESULTS/EXP-0012_results.json`, `_summary.json`

**Dependencies**
- `percolation/ENGINE/perc_engine.py` (exists)
- EXP-0009 results (identify which exponents missed tolerance at which P2 sizes)
- EXP-0010 methodology (proven non-P2 approach)
- Q-P006 infrastructure (can share L values and cell data if planned together)

**Estimated compute time**
- CPU-hours: adds ~4 non-P2 sizes x 5 exponents. ~8-16 hours depending on realization counts.
- Can run concurrently with Q-P006 if cells are persisted.

**Dependencies on other questions**
- Q-P006 should be planned first (Q-P007 can reuse Q-P006 cell data at overlapping L values)
- Q-P008 is independent

**Immediate next action**
1. After Q-P006 prereg is drafted, draft Q-P007 prereg in tandem (coordinated L sizes)
2. Write `run_exp0012.py` using same framework as Q-P006
3. Can start after Q-P006 cells are at L=512 (reuse data for L=512 P2 vs non-P2 comparison)

---

### Q-M008: Scaling test — prime gap deviation at 10^9 and 10^10 (MEDIUM, CPU-hours-days)

**What needs to be done**
- Run the same EXP-0008 test protocol at N = 10^9 and N = 10^10
- Same gates: chi2 GOF (10 bins), KS vs Exp(1), BH-FDR at α=0.01, tail z at t={1,2,3,4,5}, residue-class conditioning
- Same 4 blocks (scaled: B1=[10^8,10^9), B2=[10^9,10^10), etc.)
- Test hypothesis: deviation persists at all scales
- Falsification: if deviation disappears at 10^9 or 10^10, 10^8 result was finite-range artifact

**Files/directories to create**
- `03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/` (new sub-investigation folder)
  - `QUESTION.md`, `HYPOTHESIS.md`, `PREDICTIONS.md`, `CONTROLS.md`
  - `CODE/run_exp0013.py` — runner (sieve to 10^9, 10^10)
  - `CONFIG/prereg_EXP-0013.json` — frozen prereg
  - `CONFIG/EXP-0013_experiment.json`
  - `REPLICATION/C7_exp0013.py` — independent implementation
  - `RESULTS/EXP-0013_results.json`, `_raw.json`
  - `REPORT/Q-M008.md`

**Dependencies**
- EXP-0008 methodology (exact same protocol — reuse `CODE/run_prime_gaps.py` as template)
- EXP-0008 CONFIG (same blocks, bins, gates — adapt N ranges)
- `CODE/run_prime_gaps.py` — prime gap runner (read and adapt)
- Sieve of Eratosthenes for 10^9 (~10x EXP-0008), 10^10 (~100x EXP-0008)

**Estimated compute time**
- 10^9: ~10x EXP-0008 = ~6 hours (sieve ~9s at 10^8 → ~90s at 10^9; full analysis pipeline ~10x ~22 hours? Need to check actual compute)
- 10^10: ~100x EXP-0008 = ~5-7 days for full pipeline
- Realistically: run 10^9 first (hours), 10^10 as separate long job (days)

**Dependencies on other questions**
- Q-M007 (per-bin analysis) informs what to look for at larger N
- None hard dependencies

**Immediate next action**
1. Create Q-M008 folder + prereg (freeze before computation)
2. Write `run_exp0013.py` adapted from `run_prime_gaps.py` for N=10^9 and 10^10
3. Start 10^9 run first (validate pipeline, then commit to 10^10)

---

### Q-X1: Automated surrogate-null control generation (MEDIUM, moderate)

**What needs to be done**
- Build generic `surrogate_control` module that takes:
  - Any detector function (black-box callable)
  - Any stimulus (data array)
  - Generates full CONTROL_MATRIX automatically:
    - D01: null surrogate (Gaussian random noise matched to basic stats)
    - D02: matched-spectrum surrogate (preserves |FFT2|)
    - C01-C25: structured controls (phase-scrambled, rotated, shifted, etc.)
  - Computes BH-FDR + effect sizes + FP CIs for each control vs detector output
- Validate against known detectors (DeepBeamScan, prime gap chi2 gate, percolation p50 estimator)
- Test hypothesis: automated controls produce same verdicts as manual design
- Falsification: if automation misses a known artifact, it's insufficient

**Files/directories to create**
- `04_SHARED_ENGINE/engine/simulation/surrogate_control.py` (NEW — generic module)
- `04_SHARED_ENGINE/tests/test_surrogate_control.py` (NEW — validation tests)
- `03_INVESTIGATIONS/OTHER/surrogate_control_validation/` (NEW — validation investigation)
  - `QUESTION.md`, `CODE/`, `RESULTS/`, `REPORT/`

**Dependencies**
- Audit CONTROL_MATRIX discipline (D01/D02 from coherent-optical-ai-sandbox `research/controls/CONTROL_MATRIX.md`)
- §9 battery A==B result (proves the framework works for perception)
- EXP-0008 C6 (residue conditioning — can be automated)
- DeepBeamScan detector specs (from sandbox audit)

**Estimated compute time**
- Moderate: design + validation runs. ~1-4 hours for validation suite.

**Dependencies on other questions**
- Q-S9-3 (detector de-biasing) can use Q-X1 output as infrastructure
- Q-P006/P007 validation controls could use Q-X1 automation

**Immediate next action**
1. Study `research/controls/CONTROL_MATRIX.md` from sandbox for the manual template
2. Design `surrogate_control.py` API and control generation logic
3. Validate against DeepBeamScan (known detector with known artifacts)

---

## Group C — Plan for next session

---

### Q-P008: 3D percolation critical exponents (HIGH, CPU-days)

**What needs to be done**
- Extend lab pipeline to 3D site percolation
- Measure critical exponents: p_c, 1/ν, β/ν, γ/ν
- Compare against published 3D values (p_c ≈ 0.3116, 1/ν ≈ 0.88, β/ν ≈ 0.41, γ/ν ≈ 1.80)
- Use same `perc_engine.py` infrastructure (generalized to 3D lattices)
- Implement 3D lattice generators (simple cubic, possibly BCC/FCC)
- Run with sufficient L range for FSS analysis
- Implement C7 independent 3D implementation (pure-Python union-find in 3D)

**Files/directories to create**
- `03_INVESTIGATIONS/PHYSICS/percolation/Q-P008/` (new sub-investigation folder)
  - `QUESTION.md`, `HYPOTHESIS.md`, `PREDICTIONS.md`, `CONTROLS.md`, `LITERATURE.md`
  - `CODE/` — 3D lattice generators, runner, FSS analysis
    - `lattice_3d.py` — 3D lattice construction (simple cubic + BCC)
    - `run_exp0014.py` — 3D percolation runner
  - `CONFIG/prereg_EXP-0014.json` — frozen prereg
  - `REPLICATION/C7_exp0014.py` — independent 3D union-find
  - `RESULTS/EXP-0014_results.json`, `_summary.json`

**Dependencies**
- `percolation/ENGINE/perc_engine.py` — core engine (exists; 2D only, needs 3D extension)
- Q-P005/Q-P004 methodology (2D percolation pipeline as template)
- Q-P006/Q-P007 results (validate 2D precision before moving to 3D)
- 3D FSS literature (Lygmantas-Veremyev exponents, etc.)

**Estimated compute time**
- CPU-DAYS: 3D is ~10x more expensive than 2D per L. Even L=32-128 range will take significantly longer.
- Conservative estimate: 2-5 days for a complete run with FSS at 4-6 sizes.
- Plan: L ∈ {24, 32, 48, 64, 96, 128} at minimum (6 sizes per FSS requirement).

**Dependencies on other questions**
- Hard: Q-P006/Q-P007 (validate 2D pipeline at L=512/1024/2048 first — proves precision)
- Soft: Q-P005 (resolved, proves concept)

**Immediate next action**
1. Draft Q-P008 QUESTION.md and HYPOTHESIS.md (spec now, before 2D precision results)
2. Design 3D lattice generators in `lattice_3d.py` (prototype with L=24 to verify connectivity)
3. Wait for Q-P006 to confirm 2D precision (then extend engine to 3D)
4. Freeze prereg before any 3D computation

---

### Q-S9-1: Minimum spectral structure for pareidolia detection (MEDIUM, moderate)

**What needs to be done**
- Generate speckle images with systematically decreasing spectral complexity:
  - Full speckle (A) → sparse spectral peaks → single peak → flat spectrum
  - Parametrize by: number of FFT peaks (e.g., 5, 10, 25, 50, 100, all), peak-to-background ratio, spatial frequency
- For each complexity level, measure "code present" detection rate (use §9 battery framework)
- Find threshold where detection drops to baseline (~5%, stimulus C rate)
- Test hypothesis: monotonic function of spectral complexity measure
- Falsification: non-monotonic detection rate invalidates complexity model

**Files/directories to create**
- `03_INVESTIGATIONS/OTHER/spectral_complexity/` (new investigation folder) or extend `code/dmt-laser-s9-battery/`
  - `QUESTION.md`, `HYPOTHESIS.md`, `PREDICTIONS.md`, `CONTROLS.md`
  - `CODE/spectral_sweep.py` — generates stimuli at varying complexity levels
  - `CODE/perceptual_sweep.py` — runs perceptual scoring at each level
  - `RESULTS/spectral_complexity.json`
  - `REPORT/Q-S9-1.md`

**Dependencies**
- `code/dmt-laser-s9-battery/stimulus_gen.py` (base stimulus generation)
- `code/dmt-laser-s9-battery/perceptual_sim.py` (response model)
- `code/dmt-laser-s9-battery/analysis.py` (stats framework)
- §9 battery results (calibration: C=5%, D=32%, A/B=20%)

**Estimated compute time**
- Moderate: 6-10 complexity levels x 4 stimulus variants x 30 subjects x 50 trials ≈ 36,000-90,000 simulated trials
- ~1-3 hours simulation + analysis

**Dependencies on other questions**
- Q-S9-2 (dose-response) provides baseline inflation factors
- Q-S9-3 (detector de-biasing) tests whether spectral complexity alone explains detection

**Immediate next action**
1. After Q-S9-2 dose-response is fit, define complexity levels relative to EC50
2. Write `spectral_sweep.py` with controlled complexity parameterization
3. Validate that generated stimuli span the full complexity range

---

### Q-S9-3: Detector de-biasing — pareidolia-immune "code" detector (MEDIUM, moderate)

**What needs to be done**
- Design a detector using information-theoretic measures instead of spectral statistics:
  - Compression ratio (Lempel-Ziv or similar)
  - Mutual information with a known message
  - Kolmogorov complexity proxy
  - Decodability score (can a known message be recovered?)
- Test against stimuli A (speckle, no message) vs D (Grassmann grating, encoded message)
- Test hypothesis: information-theoretic detector distinguishes A from D where A==B in perception
- Falsification: if de-biased detector cannot distinguish A from D, no detectable information difference

**Files/directories to create**
- `03_INVESTIGATIONS/OTHER/detector_debiasing/` (new investigation folder)
  - `QUESTION.md`, `HYPOTHESIS.md`, `PREDICTIONS.md`, `CONTROLS.md`
  - `CODE/info_detector.py` — information-theoretic detector
  - `CODE/surrogate_controls.py` — control matrix for new detector (use Q-X1 module when available)
  - `RESULTS/detector_debiasing.json`
  - `REPORT/Q-S9-3.md`

**Dependencies**
- Q-X1 (automated control generation — can provide CONTROL_MATRIX)
- §9 battery results (A==B established, D differs from A)
- `code/dmt-laser-s9-battery/stimulus_gen.py` (stimuli A/B/C/D)
- Compression library (Python `zlib` or `lzma` for compression ratio)

**Estimated compute time**
- Moderate: detector design + simulation. ~1-4 hours.

**Dependencies on other questions**
- Q-X1: ideally use automated controls, but can run manual controls in parallel
- Q-S9-1: results inform whether complexity alone drives detection

**Immediate next action**
1. Draft information-theoretic detector specification (which metrics, thresholds)
2. Implement `info_detector.py` with compression + mutual information routes
3. Run against A/B/C/D stimuli, compare detection rates to spectral detector

---

## Summary Table

| ID | Priority | Compute | Group | Est. Time | Key Dependency |
|---|---|---|---|---|---|
| Q-M007 | HIGH | zero | A | 1 second | None (read EXP-0008) |
| Q-S9-2 | MEDIUM | low | A | Minutes | perceptual_sim.py |
| Q-X2 | MEDIUM | low | A | ~30 min | wavelength_ladder.py |
| Q-S9-4 | MEDIUM | moderate | A | 1-2 hours | fringe generators + catalogue |
| Q-P006 | HIGH | CPU-hours | B | 8-24 hours | perc_engine.py, EXP-0009 |
| Q-P007 | MEDIUM | CPU-hours | B | 8-16 hours | Q-P006 (shared L data) |
| Q-M008 | MEDIUM | CPU-hrs-days | B | 6h + 5 days | run_prime_gaps.py |
| Q-X1 | MEDIUM | moderate | B | 1-4 hours | CONTROL_MATRIX discipline |
| Q-P008 | HIGH | CPU-days | C | 2-5 days | perc_engine.py 3D ext, Q-P006 |
| Q-S9-1 | MEDIUM | moderate | C | 1-3 hours | spectral_sweep design |
| Q-S9-3 | MEDIUM | moderate | C | 1-4 hours | Q-X1 (controls) |

---

## Cross-Question Dependency Graph

```
Q-M007 (zero compute) ──→ informs Q-M008 interpretation
Q-S9-2 (dose-response) ──→ informs Q-S9-1, Q-S9-3
Q-X2 (coherence curve) ──→ informs Q-S9-1
Q-X1 (automated controls) ──→ used by Q-S9-3, Q-P006/P007 validation
Q-P006 (2D precision) ──→ enables Q-P007 (shared data), Q-P008 (validates pipeline)
Q-P007 (artifact diagnostic) ──→ validates Q-P006 findings
Q-P008 (3D exponents) ──→ depends on Q-P006 confirmation
```

---

## Session Execution Order (Group A first, then Group B starts)

1. **Q-M007** — 1 second, get it done immediately
2. **Q-S9-2** — 10 minutes, parametric simulation
3. **Q-X2** — 30 minutes, extend coherence ladder
4. **Q-S9-4** — 1-2 hours, fringe simulation
5. **Q-P006** — create folder + prereg + runner, start background execution
6. **Q-M008** — create folder + prereg + runner, draft and validate on 10^8 data, prepare 10^9 run
7. **Q-X1** — design module + validate against known detectors
8. **Q-P007** — draft prereg in tandem with Q-P006, prepare runner
9. **Q-S9-1, Q-S9-3, Q-P008** — plan and draft specs for next session
