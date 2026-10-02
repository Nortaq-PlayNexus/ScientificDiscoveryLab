# PROJECT INVENTORY — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 1 of 20)

---

## 1. Top-Level Structure

```
ScientificDiscoveryLab/
├── AUDIT/                          # This audit directory
├── 00_FOUNDATION/                  # Ground rules & methods
├── 01_RESEARCH_MAP/                # Per-field research notes (15 fields)
├── 02_CANDIDATE_PROBLEMS/          # Candidate question registry
├── 03_INVESTIGATIONS/              # Active investigations (8 domains)
├── 04_SHARED_ENGINE/               # Shared computational engine
├── 05_DATA/                        # Raw/processed/generated data
├── 05_EXTERNAL_RESEARCHER_DOSSIER/ # External review documents (9 docs)
├── 06_RESULTS/                     # Categorized results (confirmed/anomalies/falsified/inconclusive)
├── 07_REPORTS/                     # Report categories
├── 08_REPLICATION/                 # Replication artifacts
├── 99_ARCHIVE/                     # Archived materials
├── CODE/                           # Standalone scripts
├── DIAGNOSTICS/                    # Diagnostic scripts
├── docs/                           # Documentation
├── src/                            # Source code packages (17 modules)
├── tests/                          # Unit tests
├── *.md, *.py, *.html, etc.        # Root-level files
```

## 2. Directory Inventory

### 2.1 Foundation (4 files, 2081–3501 bytes each, all dated 17/09/2026)
| File | Purpose |
|---|---|
| `scientific_method.md` | Scientific method framework |
| `statistics_basics.md` | Statistical methods primer |
| `simulation_rules.md` | Simulation governance |
| `falsification_rules.md` | Falsification protocol |
| `terminology_plain_english.md` | Terminology definitions |

### 2.2 Research Map (15 field subdirectories, each with notes.md)
Fields: acoustics, astronomy, biology, chemistry, climate_science, computational_science, cosmology, earth_science, fluid_dynamics, information_theory, materials_science, mathematics, neuroscience, optics, physics. Each contains `notes.md` (454–1457 bytes) describing known science, open questions, and computable attack angles. Plus `README.md` (689 bytes).

### 2.3 Candidate Problems (4 items)
| Item | Size | Date | Content |
|---|---|---|---|
| `MASTER_CANDIDATES.md` | 57,271 B | 17/09 | Full registry of ~30+ candidate questions with detailed profiles |
| `NEXT_BATCH_20260919.md` | 14,805 B | 19/09 | Next batch of candidates |
| `HIGH_PRIORITY/README.md` | 1,557 B | 17/09 | High feasibility group |
| `MEDIUM_PRIORITY/README.md` | 1,405 B | 17/09 | Medium feasibility group |
| `LONG_SHOTS/README.md` | 898 B | 17/09 | Long-shot candidates |

### 2.4 Investigations (8 domains, 5 active investigations)
| Domain | Investigation | Key files |
|---|---|---|
| OPTICS | speckle_contrast_law (Q-O001) | Full lifecycle: CODE, CONFIG, DATA, FALSIFICATION, FIGURES, REPLICATION, REPORT, RESULTS |
| OPTICS | vortex_density (Q-O002) | Full lifecycle (same structure) |
| PHYSICS | percolation (Q-P004) | Full lifecycle + Q-P005_exponents subfolder, Q-P006, Q-P007 subfolders |
| PHYSICS | percolation_3d (Q-P008) | CODE, CONFIG, DATA, REPLICATION, REPORT |
| MATHEMATICS | feigenbaum_constants (Q-M005) | Full lifecycle |
| MATHEMATICS | prime_gaps (Q-M002, Q-M007, Q-M008) | Full lifecycle + Q-M007, Q-M008, Q-S9-2 subfolders |
| ACOUSTICS | water_sound_response | Full lifecycle + FALSIFICATION |
| OTHER | rng_certification (Q-I004) | Full lifecycle |
| OTHER | cone_mosaic_aliasing | CODE, CONFIG, DATA, REPORT, RESULTS |

### 2.5 Shared Engine (17 Python modules)
Core engine: `engine/__init__.py`, datasets, hypothesis_testing, reproducibility, simulation, statistics, utilities, validation, visualization. Plus `tests/run_infra_validation.py` (6,192 B), `experiment_template.md`, `README.md`.

### 2.6 Data (5 subdirectories + external_sources)
- `raw/` — raw input data
- `processed/` — processed data
- `generated/` — generated data
- `external_sources/` — external data
- `05_EXTERNAL_RESEARCHER_DOSSIER/` — 9 documents + figures/ subdirectory

### 2.7 Results (4 categorized subdirectories)
- `confirmed/` — confirmed results
- `anomalies/` — anomalous results
- `falsified/` — falsified results
- `inconclusive/` — inconclusive results

### 2.8 Reports (4 categorized subdirectories)
- `experiment_reports/`
- `anomaly_reports/`
- `final_reports/`
- `literature_reviews/`

### 2.9 Source Code (17 packages under `src/`)
adversarial, dashboard, database, evidence, experiment, failure, hypothesis, literature, molecular, navigation, novelty, observation, plant, reaction, replay, scheduler, simulation, statistics, ui, utils

### 2.10 Tests (17 unit test files)
test_adversarial, test_dashboard, test_database, test_docking, test_evidence, test_experiment, test_failure, test_foundation, test_hypothesis, test_id_gen, test_literature, test_molecular, test_molecular_engine, test_navigation, plus more

### 2.11 External Researcher Dossier (9 documents)
CURRENT_OPEN_QUESTIONS.md, DATA_INDEX.md, DOSSIER_BUILD_REPORT.md, EXECUTIVE_SUMMARY.md, EXPERIMENT_TIMELINE.md, FOLLOWUP_EMAIL.md, KEY_RESULTS.md, METHODS_AND_CONTROLS.md, NEGATIVE_AND_DIAGNOSTIC_RESULTS.md, PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md, plus figures/ subdirectory

## 3. File Counts by Extension

| Extension | Count | Purpose |
|---|---|---|
| `.md` | 166 | Documentation, reports, specifications |
| `.py` | 124 | Python source code |
| `.json` | 75 | Configuration, results, metadata |
| `.npz` | 17 | Compressed numerical data (percolation cells) |
| `.jsonl` | 8 | Append-only registries |
| `.txt` | 5 | Plain text files |
| `.bat` | 4 | Windows batch scripts |
| `.log` | 4 | Log files |
| `.err` | 3 | Error logs |
| `.png` | 3 | Figures |
| `.html` | 1 | Dashboard |
| `.TAG` | 1 | Tag file |
| `.ini` | 1 | Config (pytest) |
| `.db` | 1 | SQLite database |
| `.rar` | 1 | Archived percolation data |
| (empty) | 2 | File entries |
| **Total** | **416** | |

## 4. Experiment Summary

From `EXPERIMENT_REGISTRY.md`:

| EXP | Date | Question | Status | Evidence | Result |
|---|---|---|---|---|---|
| EXP-0001 | 2026-09-17 | Q-INFRA | complete | UNTESTED (infra) | 14/14 engine validation checks pass |
| EXP-0002 | 2026-09-17 | Q-O001 | complete | CONTROLLED | speckle C(M)=1/sqrt(M) reproduced |
| EXP-0003 | 2026-09-17 | Q-O002 | complete | CONTROLLED | vortex density = Kac-Rice/Nye-Berry |
| EXP-0004 | 2026-09-17 | Q-I004 | complete | CONTROLLED | lab RNG CERTIFIED |
| EXP-0005 | 2026-09-17 | Q-P004 | INCONCLUSIVE | CONTROLLED | p_c reproduced; FG bond_wrap fails |
| EXP-0006 | 2026-09-17 | Q-P004 | INCONCLUSIVE | CONTROLLED | fine-grid width; C8 1/nu=0.7375 |
| EXP-0007 | 2026-09-18 | Q-P004 | complete | CONTROLLED | bond_wrap resolved; 78/78 C7 match |
| EXP-0008 | 2026-09-18 | Q-M002 | complete | CONTROLLED | H1_SUPPORTED (prime gaps) |
| EXP-0009 | 2026-09-18 | Q-P005 | complete | CONTROLLED | ABNORMAL (exponents miss ~1σ) |
| EXP-0010 | 2026-09-19 | Q-P005 | complete | CONTROLLED | LATTICE_ARTIFACT; D_f=1.8962±0.028 |
| EXP-0011 | 2026-09-20 | Q-P008 (3D) | complete | CONTROLLED | percolation_3d pilot |
| EXP-0012 | 2026-09-19 | cone_mosaic | complete | CONTROLLED | (details in OTHER) |
| EXP-0013 | 2026-09-23 | percolation_3d | running | - | (in progress) |
| EXP-0014 | 2026-09-21 | Q-M005 | complete | CONTROLLED | z=2 validated (Feigenbaum δ→4.6692) |

## 5. Key Questions and Their Status

| ID | Field | Question | Status |
|---|---|---|---|
| Q-M001 | mathematics | Generalized Collatz statistics | OPEN |
| Q-M002 | mathematics | Prime gap distribution vs Poisson | ANSWERED_LOCALLY (H1_SUPPORTED) |
| Q-M003 | mathematics | Constant digit normalcy scan | OPEN |
| Q-M004 | math/compsci | Abelian sandpile exponents | OPEN |
| Q-M005 | mathematics | Feigenbaum universality higher-order | ANSWERED_LOCALLY (z=2 validated) |
| Q-M006 | mathematics | First-passage universality | OPEN |
| Q-O001 | optics | Speckle contrast law C(M)=1/sqrt(M) | ANSWERED_LOCALLY |
| Q-O002 | optics | Vortex density in random fields | ANSWERED_LOCALLY |
| Q-O003 | optics | Propagation-invariance audit | OPEN |
| Q-P004 | physics | Percolation thresholds | ANSWERED_LOCALLY |
| Q-P005 | physics | Percolation critical exponents | RESOLVED |
| Q-P006 | physics | Percolation width-route | RESOLVED |
| Q-P007 | physics | Percolation p_c refinement | RESOLVED |
| Q-P008 | physics | 3D percolation | OPEN |
| Q-I004 | info_theory | RNG certification | ANSWERED_LOCALLY |
| Q-S9-2 | supplementary | Dose-response | OPEN |

## 6. Data Files

### 6.1 Large npz files (percolation cell data)
- `_cells_L1024_n100.npz` — 23.4 MB
- `_cells_L1024_n60.npz` — 14.0 MB
- `_cells_L2048_n50.npz` — 46.6 MB (largest)
- `_cells_L512_n200.npz` — 11.9 MB
- `_cells_L512_n150.npz` — 8.9 MB
- `_cells_L256_n700.npz` — 10.7 MB
- `_cells_L128_n1500.npz` — 6.1 MB
- Various `_df_nontriv_L*.npz` — 0.8–9.2 MB each

### 6.2 Large result JSON files (>10KB)
- EXP-0008 raw/results: 25–28 KB each (prime gaps)
- EXP-0003 results: 17 KB (vortex density)
- EXP-0002 results: 7.2 KB (speckle)
- C7 reports: 7.6–26 KB each

### 6.3 Figures (PNG)
- `EXP-0003_vortex_density.png` — 114 KB
- `EXP-0004_pvalue_distribution.png` — 100 KB
- `EXP-0002_contrast_law.png` — 67 KB

## 7. Missing Data / Gaps Identified

1. **99_ARCHIVE** — directory exists but contents not verified (may be empty)
2. **05_DATA/raw, processed, generated, external_sources** — directory structure exists but contents not verified
3. **06_RESULTS/{confirmed,anomalies,falsified,inconclusive}** — categorized result directories exist but contents not verified
4. **07_REPORTS/{experiment_reports,anomaly_reports,final_reports,literature_reviews}** — report subdirectories exist but contents not verified
5. **08_REPLICATION/{cross_method_validation,independent_implementations,parameter_sweeps,seed_tests}** — replication subdirectories exist but contents not verified
6. **percolation.rar** (131 KB) — archived percolation data, contents not examined
7. **sovereign_biolab.db** (184 KB) — SQLite database, not queried
8. **Some .pyc/__pycache__ files** — compiled Python, excluded from audit

## 8. Data Integrity Flags

- `CHANGELOG.md` notes: EXP-0009 ABNORMAL diagnosed; C7 caught a real union-find double-counting bug in EXP-0005
- `CURRENT_STATUS.md` notes: Q-P004 closure check re-verified 2026-09-18
- `EXPERIMENT_REGISTRY.md` shows EXP-0001 has evidence "UNTESTED (infra)" despite being "complete"
- `EXP-0005_width_route_corrected.json` exists as a separate corrected result file
