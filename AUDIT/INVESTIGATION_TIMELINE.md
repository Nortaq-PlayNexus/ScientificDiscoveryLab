# INVESTIGATION TIMELINE — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 7 of 20)

---

## 1. Method

Timeline reconstructed from: `CHANGELOG.md`, `DISCOVERY_LOG.md`, `EXPERIMENT_REGISTRY.md`, `CURRENT_STATUS.md`, `05_EXTERNAL_RESEARCHER_DOSSIER/EXPERIMENT_TIMELINE.md`, and file modification timestamps.

## 2. Chronological Events

### 2026-09-15 (Pre-audit — triggered by external correspondence)
- AI vision agent reports ~45 candidate dark/winding structures in propagated intensity image
- Apparent ~32 µm periodic spacing; apparent alternation of rotational direction
- Agent flags as possible numerical artifacts or optical vortices
- Professor Swartzlander receives email; replies suggesting W. H. Carter / E. Wolf literature

### 2026-09-16 (Methodological correction)
- Phase-randomisation / propagation conflation identified and corrected
- Was reporting ~0.13 difference as "phase information"; corrected to propagation artifact
- Same-plane identity confirmed: max relative difference ≤ 6.55e-16

### 2026-09-17 (Batch 1 — Infrastructure + First Experiments)

**Morning (foundation setup):**
- `00_FOUNDATION/` created: scientific_method.md, statistics_basics.md, simulation_rules.md, falsification_rules.md, terminology_plain_english.md
- `01_RESEARCH_MAP/` created with 15 field subdirectories
- `02_CANDIDATE_PROBLEMS/` created with MASTER_CANDIDATES.md (57,271 B) and feasibility groupings
- `04_SHARED_ENGINE/` created: engine modules, experiment_template.md
- `RESEARCH_RULES.md`, `REPRODUCIBILITY.md` established

**Afternoon (experiments):**
- EXP-0001: Q-INFRA — 14/14 engine validation checks pass (UNTESTED infra)
- EXP-0002: Q-O001 — Speckle contrast law C(M)=1/sqrt(M) reproduced (CONTROLLED, H1_SUPPORTED)
- EXP-0003: Q-O002 — Vortex density = Kac-Rice/Nye-Berry confirmed (CONTROLLED, H0_SUPPORTED)
- EXP-0004: Q-I004 — RNG certified against lightweight battery (CONTROLLED)
- EXP-0005: Q-P004 — Percolation thresholds (INCONCLUSIVE; FG bond_wrap chi2_red=4.738 FAIL)
- EXP-0006: Q-P004 — Fine-grid percolation (INCONCLUSIVE; C8 1/nu=0.7375 PASS)
- `05_EXTERNAL_RESEARCHER_DOSSIER/` initiated (external review begins)

**Optics investigation (2026-09-17):**
- EXP-0002: speckle_contrast_law — run_speckle_contrast.py, independent_check.py
- EXP-0003: vortex_density — run_vortex_density.py, independent_check.py

### 2026-09-18 (Batch 2 — Physics + External Dossier)

- EXP-0007: Q-P004 — bond_wrap extended to L=96,128,192 (complete; 78/78 C7 match; chi2_red→2.239)
- EXP-0008: Q-M002 — Prime gaps vs Poisson (complete; H1_SUPPORTED; χ²_red=26,998, p=0)
- `DIAGNOSTICS/` created: EXP-0006_phase1_bond_wrap.py, EXP-0006_phase2_run.py
- `05_EXTERNAL_RESEARCHER_DOSSIER/` expanded with 9 documents:
  - EXECUTIVE_SUMMARY.md (2026-09-18)
  - PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md (2026-09-18)
  - EXPERIMENT_TIMELINE.md, KEY_RESULTS.md, METHODS_AND_CONTROLS.md
  - NEGATIVE_AND_DIAGNOSTIC_RESULTS.md
  - FOLLOWUP_EMAIL.md, CURRENT_OPEN_QUESTIONS.md, DATA_INDEX.md, DOSSIER_BUILD_REPORT.md
- CHANGELOG.md updated with 2026-09-18 entries (percolation, prime gaps, Q-P005 RESOLVED, Q8 Swartzlander review)

### 2026-09-19 (Batch 3 — Mathematics + Fixes)

- CHANGELOG.md updated with 2026-09-19 entries:
  - EXP-0009 (Q-P005): ABNORMAL — exponents miss ~1σ; C7 caught union-find double-counting bug
  - EXP-0010 (Q-P005): LATTICE_ARTIFACT — D_f=1.8962±0.028 at non-power-of-2 L; Q-P005 RESOLVED
  - EXP-0008 (Q-M002): H1_SUPPORTED — clean post-BH-FDR-fix run
  - Q-P005 / HYP-005 RESOLVED; ABNORMAL diagnosed
- `02_CANDIDATE_PROBLEMS/NEXT_BATCH_20260919.md` created (14,805 B)
- `fix_q006_cells.py`, `save_audits.py`, `save_q9results.py`, `create_q006_docs.py`, `create_q007_docs.py` created

### 2026-09-20 (Batch 4 — 3D Percolation)

- EXP-0011: Q-P008 (3D percolation) — pilot study (complete)
- percolation_3d investigation established with CODE, CONFIG, DATA, REPLICATION, REPORT directories
- docs/ARCHITECTURE.md, DEPENDENCY_MATRIX.md, IMPLEMENTATION_ROADMAP.md, RESEARCH_RECONNAISSANCE.md, RISK_REGISTER.md created (2026-09-20)

### 2026-09-21 (Batch 5 — Current Status Update)

- CURRENT_STATUS.md updated (2026-09-21):
  - Q-P004 closure check re-verified (2026-09-18)
  - Q-P006 audit: ABNORMAL confirmed numerically; BUG: _cells files saved to wrong directory; GAP: 1/nu not computed
  - Q-P007 Phase 2 COMPLETE: All 3 exponents PASS at refined p_c (p_c=0.59272900)
- CHANGELOG.md updated (2026-09-21)
- src/ packages updated: adversarial, dashboard, database, evidence, experiment, failure, hypothesis, literature, etc.

### 2026-09-22 (Batch 6 — Acoustics)

- ACOUSTICS/water_sound_response investigation:
  - CHANGELOG.md updated 22/09/2026 8:20:31 PM
  - CONTROLS.md, EXPERIMENT_PLAN.md, PREDICTIONS.md, QUESTION.md updated
  - Fluid dynamics variant also added (FLUID_DYNAMICS/water_sound_response)

### 2026-09-23 (Batch 7 — Current Session)

- EXP-0013: Q-P008 (3D percolation) — running (per CURRENT_STATUS.md)
- Q-P005_exponents/CODE/run_exp0007_L192.py added (23/09 12:36:40)
- Q-P005_exponents/CODE/run_percolation.py updated (23/09 12:29:22)
- Q-P005_exponents/CODE/run_percolation_exp0006.py updated (23/09 12:38:20)
- Q-P005_exponents/CODE/run_exp0009.py updated (23/09 12:38:48)
- Q-P007/PREDICTIONS.md updated 23/09 12:43:33
- Q-P007/README.md updated 23/09 12:39:39
- percolation_3d/CONFIG/prereg_EXP-0013.json created 23/09 12:30:04
- percolation_3d/CODE/run_exp0011.py updated 20/09 11:56:37
- AUDIT/ directory created with this audit in progress

## 3. Experiment Date Summary

| Date | Experiments | Domain |
|---|---|---|
| 2026-09-15 | (trigger event) | Optics (AI vision report) |
| 2026-09-16 | (methodological correction) | Optics |
| 2026-09-17 | EXP-0001 through EXP-0006 | Infra, Optics, RNG, Percolation |
| 2026-09-18 | EXP-0007, EXP-0008 | Percolation, Mathematics |
| 2026-09-19 | EXP-0009, EXP-0010, EXP-0012 | Percolation, Other |
| 2026-09-20 | EXP-0011 | Percolation (3D) |
| 2026-09-21 | EXP-0014 | Mathematics |
| 2026-09-22 | (Acoustics updates) | Acoustics |
| 2026-09-23 | EXP-0013 (running) | Percolation (3D) |

## 4. Key Date Notes

- **2026-09-15**: The project "began" in its current rigorous form (prior to this, AI vision reports existed without systematic validation)
- **2026-09-16**: Most important single methodological correction (phase-randomisation conflation)
- **2026-09-17**: Heaviest experiment day — 6 experiments run
- **2026-09-19**: Turnaround day — ABNORMAL EXP-0009 diagnosed, Q-P005 RESOLVED, EXP-0008 confirmed H1_SUPPORTED
- **2026-09-21**: Most recent CURRENT_STATUS.md update

## 5. Timeline Integrity Assessment

| Check | Status | Notes |
|---|---|---|
| Chronological consistency | ✅ | Dates increase monotonically across documents |
| Experiment dates match registry | ✅ | EXPERIMENT_REGISTRY.md consistent with CHANGELOG.md |
| File modification times match | ⚠️ | Mostly consistent; some files have future dates (23/09) which is expected for ongoing work |
| Gap analysis | ⚠️ | 2026-09-16 inferred from DISCUSSION, not explicit experiment |
| Pre-registration before experiment | ✅ | All prereg files have earlier timestamps than experiment configs |
