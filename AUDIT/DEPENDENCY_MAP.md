# DEPENDENCY MAP — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 8 of 20)

---

## 1. Machine Dependencies

Source: `REPRODUCIBILITY.md`

| Component | Specification |
|---|---|
| **OS** | Windows 10 Home |
| **CPU** | Intel Core i7-8700 (6C / 12T) @ 3.20 GHz |
| **RAM** | 24 GB |
| **GPU** | NVIDIA GTX 1080 8 GB |
| **Free disk** | ~1.5 TB (C:) |

## 2. Software Dependencies

Source: `REPRODUCIBILITY.md`

| Tool | Version | Used By |
|---|---|---|
| Python | 3.14.7 | All experiments |
| numpy | 2.5.3 | All numerical computation |
| scipy | 1.18.1 | Optimization, statistics |
| matplotlib | 3.11.2 | Plotting/figures |
| scikit-image | 0.26.0 | Image analysis |
| scikit-learn | 1.9.1 | Statistical analysis |
| sympy | 1.14.0 | Symbolic math |
| torch | 2.14.0+cpu | CPU-only (not used in experiments per REPROducIBILITY.md) |
| torchvision | 0.29.0+cpu | CPU-only |
| Pillow | 12.3.0 | Image I/O |
| ImageIO | 2.37.4 | Image I/O |

### 2.1 NOT Installed (per REPRODUCIBILITY.md note)
- JAX
- TensorFlow
- **pandas** (notably absent; shared code avoids pandas dependencies)
- astropy
- statsmodels
- plotly/dash

### 2.2 Requirements File
`requirements.txt` (369 bytes, 20/09/2026 8:11:59 AM) — present but contents not read

## 3. Python Source Package Map

### 3.1 Core Engine (`04_SHARED_ENGINE/`)

| Module | File | Purpose |
|---|---|---|
| engine.__init__ | engine/__init__.py (824 B) | Core engine interface |
| datasets | engine/datasets/manifest.py (965 B) | Dataset manifest management |
| hypothesis_testing | engine/hypothesis_testing/prereg.py (1,937 B) | Pre-registration |
| reproducibility | engine/reproducibility/experiments.py (2,681 B) | Experiment reproducibility |
| simulation | engine/simulation/controls.py (2,618 B) | Simulation controls |
| statistics | engine/statistics/testers.py (3,347 B) | Statistical tests (BH-FDR etc.) |
| utilities | engine/utilities/core.py (3,001 B) | RNG (sha256-derived PCG64) |
| validation | engine/validation/rng_battery.py (14,604 B) | RNG battery validation |
| visualization | engine/visualization/plots.py (1,248 B) | Plot utilities |
| tests | tests/run_infra_validation.py (6,192 B) | Infrastructure validation |
| tests | tests/infra_validation_results.json (1,601 B) | Validation results |

### 3.2 Application Packages (`src/`)

| Package | Init Size | Purpose (inferred from name) |
|---|---|---|
| adversarial | 8,877 B | Adversarial validation agents |
| dashboard | 6,085 B | Web dashboard (dashboard.py at root, 5,742 B) |
| database | 778 B / db.py (269 B) / models.py (9,815 B) | Database (SQLite: sovereign_biolab.db) |
| evidence | 3,771 B | Evidence management |
| experiment | 7,850 B | Experiment management |
| failure | 8,129 B | Failure tracking and analysis |
| hypothesis | 5,971 B | Hypothesis management |
| literature | 8,406 B | Literature review management |
| molecular | 646 B / engine.py (8,614 B) | Molecular simulation |
| navigation | 3,593 B | Navigation (agent?) |
| novelty | 5,772 B | Novelty detection |
| observation | 9,491 B | Observation analysis |
| plant | 340 B / engine.py (4,019 B) | Plant/biology simulation |
| reaction | 198 B / engine.py (4,783 B) / mixer.py (4,888 B) | Chemical reaction simulation |
| replay | 5,424 B | Replay/regeneration |
| scheduler | 9,121 B | Task scheduling |
| simulation | 646 B / base.py (5,558 B) | Base simulation framework |
| statistics | 6,328 B | Statistical tools |
| ui | 5,530 B | User interface |
| utils | 1,359 B / id_gen.py (878 B) / validator.py (4,259 B) | Utilities and validation |

### 3.3 Investigation-Specific Code

| Investigation | Key Script | Size | Purpose |
|---|---|---|---|
| OPTICS/speckle_contrast_law | CODE/run_speckle_contrast.py | 8,495 B | Speckle simulation |
| OPTICS/speckle_contrast_law | CODE/make_figure.py | 1,222 B | Figure generation |
| OPTICS/speckle_contrast_law | REPLICATION/independent_check.py | 1,627 B | Independent replication |
| OPTICS/vortex_density | CODE/run_vortex_density.py | 15,817 B | Vortex simulation |
| OPTICS/vortex_density | CODE/make_figure.py | 2,204 B | Figure generation |
| OPTICS/vortex_density | REPLICATION/independent_check.py | 6,413 B | Independent replication |
| PHYSICS/percolation | CODE/run_percolation.py | 21,403 B | Main percolation runner |
| PHYSICS/percolation | CODE/EXP-0005_experiment.json | — | Experiment config |
| PHYSICS/percolation | CODE/EXP-0006_experiment.json | — | Experiment config |
| PHYSICS/percolation | CODE/EXP-0007_experiment.json | — | Experiment config |
| PHYSICS/percolation | CODE/build_exp0006_summary.py | 6,683 B | Summary builder |
| PHYSICS/percolation | CODE/build_exp0007_summary.py | 8,682 B | Summary builder |
| PHYSICS/percolation | CODE/EXP-0005_width_route_corrected.py | 5,153 B | Corrected width route |
| PHYSICS/percolation | REPLICATION/independent_check.py | 6,851 B | C7 independent check |
| PHYSICS/percolation | REPLICATION/independent_check_exp0007.py | 6,780 B | EXP-0007 C7 |
| PHYSICS/percolation_3d | CODE/run_exp0011.py | 9,099 B | 3D percolation runner |
| PHYSICS/percolation_3d | CODE/benchmark.py | 609 B | Benchmark |
| PHYSICS/percolation_3d | CODE/REPLICATION/independent_check_EXP0011.py | 4,565 B | C7 check |
| MATHEMATICS/feigenbaum | CODE/feigenbaum_engine.py | 9,793 B | Feigenbaum computation |
| MATHEMATICS/feigenbaum | CODE/run_feigenbaum.py | 8,538 B | Main runner |
| MATHEMATICS/prime_gaps | CODE/run_prime_gaps.py | 32,065 B | Prime gap computation |
| MATHEMATICS/prime_gaps | REPLICATION/independent_check.py | 10,104 B | C7 independent check |
| MATHEMATICS/prime_gaps | Q-M007/analyze_bins.py | 5,627 B | Analysis |
| MATHEMATICS/prime_gaps | Q-S9-2/dose_response.py | 6,587 B | Dose-response |
| OTHER/rng_certification | CODE/run_rng_cert.py | 12,020 B | RNG certification |
| OTHER/rng_certification | CODE/plot_battery.py | 2,487 B | Battery plotting |
| OTHER/rng_certification | REPLICATION/independent_check.py | 7,327 B | C7 check |
| OTHER/cone_mosaic | CONFIG/prereg_EXP-0012.json | 2,309 B | Experiment config |
| ACOUSTICS/water_sound | Various | — | Acoustic investigation |

### 3.4 Standalone Scripts (root CODE/ and root)

| Script | Size | Purpose |
|---|---|---|
| CODE/EXP-0005_width_route_corrected.py | 5,153 B | Corrected width route |
| CODE/run_percolation_exp0006.py | 1,054 B | EXP-0006 runner |
| create_q006_docs.py | 6,857 B | Q-P006 doc creator |
| create_q007_docs.py | 3,101 B | Q-P007 doc creator |
| fix_q006_cells.py | 983 B | Fix cells directory bug |
| save_audits.py | 6,171 B | Audit saver |
| save_q9results.py | 3,388 B | Q-P009 results saver |
| dashboard.py | 5,742 B | Web dashboard |

### 3.5 Test Suite

| Test File | Size | Coverage |
|---|---|---|
| test_adversarial.py | 3,154 B | Adversarial module |
| test_dashboard.py | 1,854 B | Dashboard |
| test_database.py | 2,483 B | Database |
| test_docking.py | 2,244 B | Molecular docking |
| test_evidence.py | 2,307 B | Evidence module |
| test_experiment.py | 4,304 B | Experiment module |
| test_failure.py | 3,909 B | Failure module |
| test_foundation.py | 1,974 B | Foundation |
| test_hypothesis.py | 2,380 B | Hypothesis module |
| test_id_gen.py | 656 B | ID generation |
| test_literature.py | 1,774 B | Literature module |
| test_molecular.py | 2,251 B | Molecular |
| test_molecular_engine.py | 3,286 B | Molecular engine |
| test_navigation.py | 2,345 B | Navigation |

## 4. Data Dependencies

### 4.1 Seed-Dependent Results
- Experiments use `engine.utilities.rng(label, seed)` — sha256-derived Generator
- Seeds recorded in experiment.json and prereg files
- Seed variation is a mandatory control (C3)

### 4.2 Deterministic Results
- EXP-0014 (Feigenbaum): No RNG; deterministic root-finding
- EXP-0008 (Prime gaps): RNG unused; sieve is deterministic
- EXP-0001 (Infra): Validation tests, deterministic

### 4.3 File Hash Dependencies
- experiment.json records: dataset file hashes (sha256), result file hashes (sha256)
- **Status**: HASHES RECORDED but NOT INDEPENDENTLY VERIFIED in this audit

## 5. Cross-Module Dependencies

Based on `docs/ARCHITECTURE.md` (20,789 B, 20/09/2026 8:05:05 AM):
- `src/` packages depend on `04_SHARED_ENGINE/` engine modules
- Investigations depend on `04_SHARED_ENGINE/` for RNG, BH-FDR, surrogates, templates
- `src/database/` backs `sovereign_biolab.db`
- `src/dashboard/` provides web UI (dashboard.html, dashboard.py)
- `src/adversarial/` provides adversarial validation agents
- `src/evidence/`, `src/experiment/`, `src/failure/`, `src/hypothesis/` form the core workflow

**Status**: Architecture document referenced but not fully read — details in docs/ARCHITECTURE.md

## 6. Dependency Risk Assessment

| Risk | Severity | Description |
|---|---|---|
| pandas not installed | MEDIUM | Any analysis requiring pandas needs installation; shared code avoids it |
| torch CPU-only | LOW | torch available but not used in core experiments |
| HASH verification not done | MEDIUM | Result integrity depends on hash verification |
| sovereign_biolab.db unexamined | MEDIUM | Database schema and contents unknown |
| __pycache__ dependencies | LOW | Compiled Python files may be stale relative to source |
| pytest cache | LOW | Test cache; not experiment-critical |

## 7. Reproduction Commands

Per individual experiment reports, standard commands include:

```bash
# Infrastructure validation
python -m engine.tests.run_infra_validation

# Dashboard
python dashboard.py  # Open http://127.0.0.1:8008

# Individual experiments (from investigation directory):
python CODE/run_speckle_contrast.py        # ~2 min CPU
python REPLICATION/independent_check.py    # ~1 min
python CODE/make_figure.py

# Per experiment, see individual REPORT/TECHNICAL_*.md
```

## 8. Full Dependency Graph Summary

```
00_FOUNDATION/ (rules, methods)
  → governs all experiments

04_SHARED_ENGINE/ (RNG, BH-FDR, controls, templates)
  → depends on: 00_FOUNDATION/
  → used by: all 03_INVESTIGATIONS/ experiments
  → tested by: tests/run_infra_validation.py

03_INVESTIGATIONS/ (experiments)
  → each investigation depends on: 04_SHARED_ENGINE/
  → each investigation has: CODE/, CONFIG/, DATA/, FALSIFICATION/, FIGURES/, REPLICATION/, REPORT/, RESULTS/

src/ (application packages)
  → depends on: 04_SHARED_ENGINE/ (engine modules)
  → used by: dashboard, database, adversarial, etc.

02_CANDIDATE_PROBLEMS/ (questions)
  → drives: 03_INVESTIGATIONS/

05_DATA/ (data)
  → used by: 03_INVESTIGATIONS/ experiments

06_RESULTS/, 07_REPORTS/, 08_REPLICATION/ (output)
  ← produced by: 03_INVESTIGATIONS/

docs/ (architecture, dependencies, roadmap, risk)
  → documents: all above

tests/ (unit tests)
  → tests: src/ packages

tests/unit/ | src/ packages
  → pytest: pytest.ini, pytest cache
