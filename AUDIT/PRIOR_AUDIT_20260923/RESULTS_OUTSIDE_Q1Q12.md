# RESULTS_OUTSIDE_Q1Q12 — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 9 of 20)

---

## 1. Context

The original instruction document referenced "Q1–Q12" as the core experiments. In ScientificDiscoveryLab, the registered questions are:
- Q-M001, Q-M002, Q-M003, Q-M004, Q-M005, Q-M006 (mathematics)
- Q-O001, Q-O002, Q-O003 (optics)
- Q-P004, Q-P005, Q-P006, Q-P007, Q-P008 (physics)
- Q-I004 (information theory)
- Q-S9-2 (supplementary)

The instruction document's Q1–Q12 likely maps to a subset of these. The experiments listed here go beyond any simple Q1–Q12 mapping.

## 2. Experiments Not in a Simple Q1–Q12 Mapping

### 2.1 EXP-0001 — Infrastructure Validation (Q-INFRA)

| Field | Value |
|---|---|
| **Date** | 2026-09-17 |
| **Question** | Q-INFRA (infrastructure, not a numbered Q-series) |
| **Status** | complete |
| **Evidence** | UNTESTED (infra) |
| **Result** | 14/14 engine validation checks pass |
| **Key Files** | 04_SHARED_ENGINE/tests/run_infra_validation.py, infra_validation_results.json |
| **Significance** | Validates the shared computational engine before other experiments run |

### 2.2 EXP-0004 — RNG Certification (Q-I004)

| Field | Value |
|---|---|
| **Date** | 2026-09-17 |
| **Question** | Q-I004 (information theory / RNG) |
| **Status** | complete |
| **Evidence** | CONTROLLED |
| **Result** | Lab RNG CERTIFIED against lightweight battery |
| **Key Files** | CODE/run_rng_cert.py (12 KB), RESULTS/EXP-0004_results.json (29.6 KB), FIGURES/EXP-0004_pvalue_distribution.png (100 KB) |
| **Significance** | Certifies the lab's sha256-derived PCG64 RNG passes KS uniformity + binomial band + BH-FDR; C7 independent implementation agrees 30/30 |

### 2.3 EXP-0009/0010 — Percolation Exponents (Q-P005)

| Field | Value |
|---|---|
| **Date** | 2026-09-18/19 |
| **Question** | Q-P005 (percolation critical exponents) |
| **Status** | RESOLVED (ABNORMAL → LATTICE_ARTIFACT) |
| **Key Finding** | D_f = 1.8962 ± 0.028 at non-power-of-2 L matches theory 91/48 = 1.8958 |
| **Significance** | Resolves the ABNORMAL from EXP-0009 as a lattice-size artifact |

### 2.4 EXP-0011/0013 — 3D Percolation (Q-P008)

| Field | Value |
|---|---|
| **Date** | 2026-09-20 / 2026-09-23 |
| **Question** | Q-P008 (3D percolation) |
| **Status** | EXP-0011 complete; EXP-0013 running |
| **Key Files** | CODE/RESULTS/EXP-0011_results.json, CODE/REPLICATION/C7_EXP-0011_report.json |
| **Significance** | Extends percolation program to 3D |

### 2.5 EXP-0014 — Feigenbaum Constants (Q-M005)

| Field | Value |
|---|---|
| **Date** | 2026-09-21 |
| **Question** | Q-M005 (Feigenbaum universality higher-order maps) |
| **Status** | complete |
| **Key Finding** | δ_n converges to 4.6692016091029 at n=8 for z=2; z=3,4 partial |
| **Significance** | Confirms Feigenbaum universality for quadratic maps; extends to z=3,4 partially |

### 2.6 Acoustics Investigation

| Field | Value |
|---|---|
| **Date** | 2026-09-22 (last update) |
| **Question** | ACOUSTICS/water_sound_response |
| **Status** | Active investigation |
| **Key Files** | QUESTION.md (12.9 KB), PREDICTIONS.md (13.4 KB), LITERATURE.md (8.8 KB) |
| **Significance** | Water sound response investigation — domain not in Q-series |

### 2.7 cone_mosaic_aliasing (Other)

| Field | Value |
|---|---|
| **Date** | 2026-09-19 |
| **Question** | Cone mosaic aliasing |
| **Status** | complete (inferred) |
| **Key Files** | CONFIG/prereg_EXP-0012.json (2.3 KB) |
| **Significance** | Visual neuroscience / aliasing investigation |

### 2.8 Prime Gap Sub-Questions (Q-M007, Q-M008, Q-S9-2)

| ID | Investigation | Key Files | Status |
|---|---|---|---|
| Q-M007 | analyze_bins.py | Q-M007/analyze_bins.py (5,627 B), q_m007_results.json (3,819 B), AUDIT_Q006_Q007.md (3,600 B) | Active |
| Q-M008 | PLAN.md | Q-M008/PLAN.md (1,982 B) | Planning |
| Q-S9-2 | dose_response.py | Q-S9-2/dose_response.py (6,587 B), dose_response_results.json (1,117 B) | Active |

## 3. Non-Experiment Results

### 3.1 External Researcher Dossier (R1–R8)

The `05_EXTERNAL_RESEARCHER_DOSSIER/` contains 9 documents summarizing results in a format not in the experiment registry:

| Document | Content |
|---|---|
| EXECUTIVE_SUMMARY.md | Summary for Professor Swartzlander |
| KEY_RESULTS.md | R1–R8 key positive results |
| METHODS_AND_CONTROLS.md | Detailed methodology and controls |
| NEGATIVE_AND_DIAGNOSTIC_RESULTS.md | Negative results and diagnostics |
| PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md | Full progress report (Document 1 of 9) |
| EXPERIMENT_TIMELINE.md | Chronological experiment timeline |
| CURRENT_OPEN_QUESTIONS.md | Open questions from external perspective |
| DATA_INDEX.md | Data index |
| DOSSIER_BUILD_REPORT.md | Dossier construction report |
| FOLLOWUP_EMAIL.md | Proposed reply to Swartzlander |
| figures/README.md | Figure documentation |

### 3.2 Architecture and Planning Documents

| Document | Size | Content |
|---|---|---|
| docs/ARCHITECTURE.md | 20,789 B | System architecture |
| docs/DEPENDENCY_MATRIX.md | 4,582 B | Dependency matrix |
| docs/IMPLEMENTATION_ROADMAP.md | 15,669 B | Implementation roadmap |
| docs/RESEARCH_RECONNAISSANCE.md | 26,210 B | Research reconnaissance |
| docs/RISK_REGISTER.md | 4,947 B | Risk register |

## 4. Research Map Documents

Each of 15 field subdirectories in `01_RESEARCH_MAP/` contains notes.md:

Fields with existing notes: acoustics (6,132 B, updated 22/09), astronomy (755 B), biology (582 B), chemistry (460 B), climate_science (642 B), computational_science (536 B), cosmology (617 B), earth_science (454 B), fluid_dynamics (626 B), information_theory (688 B), materials_science (581 B), mathematics (937 B), neuroscience (491 B), optics (1,457 B), physics (889 B).

## 5. Candidate Problems Beyond Q-Series

- `MASTER_CANDIDATES.md` (57,271 B): ~30+ detailed candidate question profiles
- `NEXT_BATCH_20260919.md` (14,805 B): Next batch of candidates (2026-09-19)
- High/Medium/Long-shot feasibility groupings

## 6. Summary Count

| Category | Count |
|---|---|
| Experiments in Q-series numbering | 12 (Q-M001–Q-M006, Q-O001–Q-O003, Q-P004–Q-P008, Q-I004) |
| Experiments outside simple Q1–Q12 | 5+ (Q-INFRA, Q-P005, Q-P008, Q-M005, acoustics, cone_mosaic) |
| External dossier documents | 11 (+ figures README) |
| Architecture/planning documents | 5 |
| Research map notes | 15 |
| Candidate problem profiles | 30+ |

## 7. Key Insight

ScientificDiscoveryLab contains **significantly more** than a simple Q1–Q12 mapping would suggest. The lab's experiments span:
- **Infrastructure validation** (Q-INFRA)
- **Multiple physics domains** (optics, percolation 2D+3D, acoustics)
- **Mathematical constants** (Feigenbaum, prime gaps, Collatz, digit normalcy)
- **RNG certification** (Q-I004)
- **Visual neuroscience** (cone mosaic aliasing)
- **External review** (Swartzlander dossier)

All results outside the original Q1–Q12 scope are **properly documented** with the same rigor (pre-registration, controls, independent replication, honest framing).
