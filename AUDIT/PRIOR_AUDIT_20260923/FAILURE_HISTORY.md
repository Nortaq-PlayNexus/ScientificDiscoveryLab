# FAILURE HISTORY — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 6 of 20)

---

## 1. Philosophy

Per `RESEARCH_RULES.md` and `DISCOVERY_LOG.md`:
> "Failed controls and falsifications are logged with the same weight as positives."

This document catalogs every documented failure, bug, anomaly, and negative result.

## 2. Documented Failures and Anomalies

### 2.1 EXP-0005/0006: Percolation FG bond_wrap Chi-Square Failure

**Severity:** HIGH (could have invalidated a key result)

**What happened:**
- EXP-0005: Fisher-Gompertz (FG) goodness-of-fit for bond_wrap p50: chi2_red = 4.738 (gate: < 4 → FAIL)
- EXP-0006: Same failure persisted with fine grid
- C8 width-route: 1/nu = 1.2384 (gate: 0.6–0.9 → FAIL)

**Root cause (diagnosed):**
- Small-L finite-size kink (L48→L64 delta 0.00288) dominated the small-L-only fit
- The non-monotonicity was real but consistent with noise against a monotone L^−3/4 trend
- Per `DIAGNOSTICS/EXP-0005_width_route_audit.md`

**Resolution:**
- EXP-0007 extended to L=96,128,192: chi2_red improved 4.738 → 2.239 (PASS)
- C8 width-route on extended data: 1/nu = 0.7255 (PASS, gate 0.6–0.9)
- Corrected re-fit on same cells: 1/nu = 0.7922 (PASS)
- C7 independent implementation: 78/78 cells bit-identical

**Honest documentation:** FAILURE is recorded in EXPERIMENT_REGISTRY.md, DIAGNOSTICS/, and CHANGELOG.md

### 2.2 EXP-0009: Percolation ABNORMAL Decision

**Severity:** MEDIUM (resolved but escalated per rules)

**What happened:**
- D_f = 1.8697 (expected 91/48 = 1.8958, dev = 0.0261, ~1σ)
- γ/nu = 1.7596 (expected 43/24 = 1.7917, dev = 0.0321, ~1σ)
- β/nu = 0.1295 (expected 5/48 = 0.1042, dev = 0.0253, ~1σ)
- τ = 1.9404 (apparent window, gate TBD)
- 1/nu = 0.7434 (gate PASS: 0.6–0.9)
- R1 borderline FAIL (0.129 vs 0.12)

**Resolution:**
- Per frozen rule: ABNORMAL (escalate, do NOT tune)
- EXP-0010 measured at non-power-of-2 L: D_f = 1.8962 ± 0.028 (theory 1.8958, |dev| = 0.0004)
- Diagnosed as lattice-size discretization artifact (same class as optical grid-locking at 256²)
- Q-P005 RESOLVED

**Key lesson:** Lattice-size matters; power-of-2 lattices have specific artifacts

### 2.3 EXP-0002: BH-FDR Engine Bug

**Severity:** HIGH (affects all experiments using BH-FDR)

**What happened:**
- Bug found in engine's BH-FDR step-up indexing (flagged ALL cells as significant)
- Found by infra validation suite mid-session (EXP-0001)
- Fixed, covered by regression check, experiment re-run
- First run's FDR flags are superseded; both rows kept in registry

**Resolution:**
- Bug fixed in engine code
- EXP-0002 re-run with corrected BH-FDR
- `04_SHARED_ENGINE/` updated

### 2.4 EXP-0003: Detector D2 Overcounting Bug

**Severity:** MEDIUM (detected and corrected before reporting)

**What happened:**
- Initial naive contour detector (D2) overcounted ~2.5× because it did not verify contour intersection
- Original vision agent's "45 features" likely caused by this detector flaw

**Resolution:**
- Replaced by certified zero-contour intersection detector
- Naive D2 retained as documented negative in CONFIG/changelog.jsonl

### 2.5 Vortex Density: Near-Nyquist Failure Zone

**Severity:** MEDIUM (characterized, not claimed as physics)

**What happened:**
- Broad Gaussian spectra lose up to ~17% (winding) / ~24% (contour) of counts at σ_k = 0.75, k0 = π/2
- Both independent detectors show it

**Resolution:**
- Characterized as detector/grid resolution limit (unresolved high-k structure)
- NOT attributed to physics
- Narrow-band cells with P ≥ 8 show no such deficit

### 2.6 Prime Gaps: C6 Residue Conditioning Failure

**Severity:** MEDIUM (expected behavior, honestly documented)

**What happened:**
- C6_residue_conditioning: FAIL — no significant deviation after conditioning on residue classes
- This is expected for a true Poisson-like deviation (the deviation is in tail shape, not residue structure)

**Resolution:**
- Recorded as FAIL; not interpreted as invalidating the H1_SUPPORTED decision
- Deviation is in tail shape (lighter than Exp(1), correct mean)

### 2.7 EXP-0008: Pre-BH-FDR vs Post-BH-FDR Comparison

**Severity:** LOW (process documentation)

**What happened:**
- EXP-0008 run1_pre_bhfix variant preserved alongside final run
- C7_exp0008_report.run1_pre_bhfix.json also preserved

**Resolution:**
- Both versions documented; pre-fix results show what happens without BH-FDR correction

### 2.8 Phase-Randomisation / Propagation Conflation (optics project)

**Severity:** CRITICAL (was a major early false positive)

**What happened:**
- Original "phase randomization" statistic reported mean absolute difference ~0.13 between I(x) and I(rand)
- Was interpreted as "phase was information" (a discovery claim)
- Correct interpretation: |A·e^{iφ_rand}|² = A² (same-plane intensity unchanged exactly); the 0.13 difference is natural propagation of phase-incoherent vs phase-coherent field

**Resolution:**
- Corrected on 2026-09-16 (per PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md §3)
- Same-plane intensity difference: max relative difference ≤ 6.55e-16 (confirmed exact)
- After 160 µm propagation: NCC = 0.0564 (expected, not a discovery)

**Impact:** Explained a large fraction of early "positive" findings; corrected as first methodological correction

### 2.9 Lattice Artifacts in Percolation (EXP-0009→EXP-0010)

**Severity:** MEDIUM (diagnosed and resolved)

**What happened:**
- EXP-0009 ABNORMAL: exponents miss tolerances by ~1σ
- Initially unclear whether this was a real deviation or artifact

**Resolution:**
- EXP-0010: D_f = 1.8962 ± 0.028 at non-power-of-2 L (deviation: 0.0004)
- Diagnosis: power-of-2 lattice discretization artifact
- Same class as optical grid-locking at 256² in the sandbox

### 2.10 Prime Gap Independent Check (C7) Discrepancy

**Severity:** LOW (documented)

**What happened:**
- C7 uses equal-width GOF for independent verdict but same-binning (exponential-quantile) vector for 1e-9 tolerance
- Documented in state/EXP-0008_decisions.md (prereg-contradiction resolution)

**Resolution:**
- Prereg-contradiction resolution documented; both methods agree on final verdict

## 3. Known Limitations / Open Issues

| Issue | Status | Impact |
|---|---|---|
| 1/nu not computed for Q-P006 | GAP | inv_nu_gate never evaluated |
| Gates C1, C6, C7, FG not in Q-P006 results JSON | GAP | Incomplete gate reporting |
| _cells files saved to wrong directory (Q-P006) | BUG | Fixed; files COPIED to correct location |
| Real-optics confirmation | NOT YET TESTED | No physical experiment run |
| sovereign_biolab.db contents | UNKNOWN | 184 KB, unexamined |
| percolation.rar contents | UNKNOWN | 131 KB, unextracted |

## 4. Falsification Outcomes

Per `RESEARCH_RULES.md` §2, falsification is a mandatory step. Documented falsification outcomes:

| Claim | Result | Evidence |
|---|---|---|
| "45 features / 21–24 split" in propagated field | **RULED OUT** | Independent validator AGAINST |
| z = 1280 µm excess as topology | **RULED OUT** | Pixelation/grid-locked artifact |
| Symbolic/"code" content in light | **RULED OUT** | Flat-amplitude control: purified count 0 |
| Phase randomization as "phase information" | **RULED OUT** | Corrected: propagation artifact, not discovery |
| 32 µm structure as emergent physics | **RULED OUT** | Inherited from generator pitch (32.0 µm) |
| Forbidden-statistics / percolation (Q-P004) | **H0_SUPPORTED** (clean null) | EXP-0005/6/7 |

## 5. Failure Statistics

| Category | Count | Examples |
|---|---|---|
| Critical methodology corrections | 1 | Phase-randomisation conflation |
| Major result falsifications | 5 | 45 features, z=1280, code content, 32µm emergence, phase info |
| Engine bugs | 2 | BH-FDR indexing, D2 detector overcount |
| Experiment anomalies | 2 | EXP-0009 ABNORMAL, EXP-0010 LATTICE_ARTIFACT |
| Documented limitations | 5 | 1/nu gap, missing gates, wrong dir, etc. |
| Unexamined data | 3 | db, archive, 05_DATA dirs |

## 6. Lessons Learned (per CHANGELOG and DISCOVERY_LOG)

1. **Lattice size matters**: Power-of-2 lattices produce specific artifacts; test with non-power-of-2 sizes
2. **Independent detectors are essential**: D1/D2 dual detection caught the 2.5× overcounting
3. **Pre-registration prevents result manipulation**: Frozen preregs preserved through all corrections
4. **Controls must be matched**: The emergence-vs-inheritance control (C-control ratio 0.595 INVALID) proved 32µm structure is inherited
5. **ABNORMAL per frozen rule**: Never tune to fix anomalies; escalate instead
6. **Correct the method, not the result**: BH-FDR bug fixed and experiment re-run, not results selectively reported
7. **Honest framing**: Every result has a "what this does NOT prove" section
