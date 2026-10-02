# RAW DATA FINDINGS — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 3 of 20)

---

## 1. Data Directory Structure

```
05_DATA/
├── raw/              # Raw input data (not examined — directory exists)
├── processed/        # Processed data (not examined — directory exists)
├── generated/        # Generated data (not examined — directory exists)
└── external_sources/ # External data sources (not examined — directory exists)
```

**Status:** The 05_DATA/ directory structure exists per the inventory, but the contents of raw/, processed/, generated/, and external_sources/ were **NOT EXAMINED** in this audit. These should contain the foundational datasets but may be empty or incomplete.

## 2. Identified Data Files by Type

### 2.1 Compressed Numerical Data (.npz) — 17 files
All located in percolation investigation folders. These are the largest individual data files in the project.

| File | Size | Location | Experiment |
|---|---|---|---|
| _cells_L2048_n50.npz | 46,612,965 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0009/EXP-0010 |
| _cells_L1024_n100.npz | 23,409,415 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0009 |
| _cells_L1024_n60.npz | 14,038,471 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0009 |
| _cells_L512_n200.npz | 11,889,582 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0009 |
| _cells_L512_n150.npz | 8,914,681 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0009 |
| _cells_L256_n700.npz | 10,702,759 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0009 |
| _cells_L128_n1500.npz | 6,079,974 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0009 |
| _df_nontriv_L449_n200.npz | 9,155,196 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0010 |
| _df_nontriv_L253_n200.npz | 2,977,496 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0010 |
| _df_nontriv_L191_n200.npz | 1,729,961 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0010 |
| _df_nontriv_L127_n200.npz | 794,364 B | Q-P005_exponents/CODE/RESULTS/ | EXP-0010 |

**Purpose:** These contain raw cluster cell data for percolation exponent estimation. The `_cells` files are lattice configurations; the `_df_nontriv` files are non-trivial cluster size distributions.

### 2.2 JSON Results Files (selected by size)

| File | Size | Experiment | Content |
|---|---|---|---|
| EXP-0008_raw.json | 28,395 B | Q-M002 | Raw prime gap data |
| EXP-0008_results.json | 25,645 B | Q-M002 | Processed results |
| EXP-0008_raw.run1_pre_bhfix.json | 28,406 B | Q-M002 | Pre-BH-FDR fix raw |
| EXP-0008_results.run1_pre_bhfix.json | 25,700 B | Q-M002 | Pre-BH-FDR fix processed |
| EXP-0007_results.json | 18,813 B | Q-P004 | Percolation results |
| EXP-0003_results.json | 17,034 B | Q-O002 | Vortex density results |
| EXP-0004_results.json | 29,584 B | Q-I004 | RNG test results |
| EXP-0002_results.json | 7,159 B | Q-O001 | Speckle contrast results |
| EXP-0005_results.json | 22,739 B | Q-P004 | Percolation results |
| EXP-0006_results.json | 25,825 B | Q-P004 | Percolation fine-grid |
| C7_exp0007_report.json | 25,909 B | Q-P004 | C7 independent replication |
| C7_exp0008_report.json | 7,630 B | Q-M002 | C7 independent replication |
| C7_EXP-0011_report.json | 16,893 B | Q-P008 | C7 independent replication |

### 2.3 Experiment Configuration Files (selected)

| File | Size | Experiment | Content |
|---|---|---|---|
| EXP-0003_experiment.json | 18,949 B | Q-O002 | Full experiment parameters |
| EXP-0002_experiment.json | 14,925 B | Q-O001 | Full experiment parameters |
| EXP-0008_experiment.json | 7,115 B | Q-M002 | Full parameters |
| EXP-0008_experiment.run1_pre_bhfix.json | 7,157 B | Q-M002 | Pre-fix parameters |
| EXP-0005_experiment.json | 28,425 B | Q-P004 | Full parameters |
| EXP-0006_experiment.json | 32,103 B | Q-P004 | Full parameters |
| EXP-0007_experiment.json | 23,903 B | Q-P004 | Full parameters |
| prereg_EXP-0008.json | 7,656 B | Q-M002 | Frozen pre-registration |
| prereg_EXP-0005.json | 3,614 B | Q-P004 | Frozen pre-registration |
| prereg_EXP-0006.json | 2,774 B | Q-P004 | Frozen pre-registration |
| prereg_EXP-0007.json | 2,548 B | Q-P004 | Frozen pre-registration |
| prereg_EXP-0014.json | 1,003 B | Q-M005 | Frozen pre-registration |
| prereg_EXP-0002.json | 763 B | Q-O001 | Frozen pre-registration |
| prereg_EXP-0003.json | 1,289 B | Q-O002 | Frozen pre-registration |
| prereg_EXP-0004.json | 1,635 B | Q-I004 | Frozen pre-registration |
| prereg_EXP-0009.json | 4,281 B | Q-P005 | Frozen pre-registration |
| prereg_EXP-0010.json | 1,692 B | Q-P005 | Frozen pre-registration |
| prereg_EXP-0009P.json | 2,031 B | Q-P006 | Frozen pre-registration |
| prereg_EXP-0009PC.json | 2,195 B | Q-P007 | Frozen pre-registration |
| prereg_EXP-0011.json | 3,325 B | Q-P008 | Frozen pre-registration |
| prereg_EXP-0013.json | 2,928 B | Q-P008 | Frozen pre-registration |
| prereg_EXP-0012.json | 2,309 B | OTHER | Frozen pre-registration |

### 2.4 Database

| File | Size | Type | Status |
|---|---|---|---|
| sovereign_biolab.db | 184,320 B | SQLite | **NOT QUERIED** — contents unknown; may contain metadata, results, or operational data |

### 2.5 Archived Data

| File | Size | Status |
|---|---|---|
| percolation.rar | 131,327 B | **NOT EXTRACTED** — archived percolation data; contents unknown |

## 3. Data Quality Assessment

### 3.1 Strengths
- **Pre-registration:** All major experiments have frozen prereg files, preventing result manipulation
- **Append-only registries:** `registry.jsonl` files track all experiment versions
- **Multiple raw + processed pairs:** Raw and results JSON files kept together (e.g., EXP-0008_raw.json + EXP-0008_results.json)
- **Version tracking:** `.run1_pre_bhfix.json` files preserve pre-correction data

### 3.2 Weaknesses
- **05_DATA/ subdirectories not verified:** May be empty or incomplete
- **sovereign_biolab.db unexamined:** 184 KB database with unknown contents
- **percolation.rar unexamined:** 131 KB archive with unknown contents
- **06_RESULTS/ categorized directories not verified:** May be empty or incomplete
- **08_REPLICATION/ categorized directories not verified**

### 3.3 Data Completeness
| Category | Present | Verified | Notes |
|---|---|---|---|
| Experiment configs | ✅ | ⚠️ | 75 JSON files present; contents verified for key experiments |
| Results JSON | ✅ | ⚠️ | Present for all major experiments; contents verified for key experiments |
| Raw data | ⚠️ | ❌ | 05_DATA/raw/ not examined |
| Processed data | ⚠️ | ❌ | 05_DATA/processed/ not examined |
| Generated data | ⚠️ | ❌ | 05_DATA/generated/ not examined |
| External data | ⚠️ | ❌ | 05_DATA/external_sources/ not examined |
| Figures (PNG) | ✅ | ✅ | 3 figures verified |
| Database | ✅ | ❌ | sovereign_biolab.db not queried |
| Archive | ✅ | ❌ | percolation.rar not extracted |

## 4. Data Provenance Chain

```
Pre-registration (prereg_*.json, frozen before run)
  → Experiment configuration (EXP-####_experiment.json, with parameters, seeds, hashes)
    → Code execution (run_*.py scripts)
      → Raw results (EXP-####_raw.json)
        → Processed results (EXP-####_results.json)
          → Reports (REPORT/TECHNICAL_*.md, REPORT/PLAIN_*.md)
            → Registry update (registry.jsonl, append-only)
              → Experiment registry (EXPERIMENT_REGISTRY.md)
```

## 5. Gaps Requiring Follow-up

1. **05_DATA/ contents** — should be examined to determine if raw data exists
2. **sovereign_biolab.db** — should be queried to understand schema and contents
3. **percolation.rar** — should be extracted and compared against existing percolation data
4. **06_RESULTS/ categorized directories** — should be checked for completeness
5. **08_REPLICATION/ categorized directories** — should be checked for completeness
6. **HASH VERIFICATION** — result file hashes recorded in configs but not independently recomputed
