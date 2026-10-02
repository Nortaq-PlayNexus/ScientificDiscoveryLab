# EXPERIMENT REGISTER — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 2 of 20)

---

## 1. Registry Overview

Source: `EXPERIMENT_REGISTRY.md` (last updated 2026-09-21 01:26:56)
Total experiments: **14** (EXP-0001 through EXP-0014)

The registry uses a strict append-only model: EXP IDs allocated in order, never reused, never deleted.

## 2. Complete Experiment Table

### 2.1 Infrastructure

| Field | Value |
|---|---|
| **EXP-0001** | Date: 2026-09-17 \| Q-INFRA \| HYP-INFRA \| complete \| UNTESTED (infra) \| 14/14 engine validation checks pass |
| **Purpose** | Validate the shared computational engine (RNG, BH-FDR, surrogate generation, template system) |
| **Evidence** | `04_SHARED_ENGINE/tests/run_infra_validation.py` (6,192 B), `infra_validation_results.json` (1,601 B) |
| **Key finding** | A bug in BH-FDR step-up indexing was found, fixed, regression-tested, and the experiment was re-run. First run's FDR flags are superseded; both rows kept in registry. |

### 2.2 Optics

| Field | EXP-0002 | EXP-0003 |
|---|---|---|
| **Date** | 2026-09-17 | 2026-09-17 |
| **Question** | Q-O001 | Q-O002 |
| **Hypothesis** | HYP-001 | HYP-002 |
| **Status** | complete | complete |
| **Evidence** | CONTROLLED | CONTROLLED |
| **Result** | speckle C(M)=1/sqrt(M) reproduced (run 2) | vortex density = Kac-Rice/Nye-Berry for well-resolved fields; Nyquist failure zone mapped |
| **Decision** | H1_SUPPORTED | H0_SUPPORTED |
| **Key files** | RESULTS/EXP-0002_results.json (7.2 KB), REPORT/TECHNICAL_SUMMARY.md | RESULTS/EXP-0003_results.json (17 KB), REPORT/TECHNICAL_SUMMARY.md |
| **Controls** | C1–C8 (8 controls, all PASS except N=64 M=2 FDR flag) | C1–C10 (10 controls, all PASS; C8 documented failure zone) |
| **What it does NOT prove** | Nothing about real optical systems; nothing novel (textbook Goodman) | No new physics; no novelty claimed |

### 2.3 Physics — Percolation

| Field | EXP-0005 | EXP-0006 | EXP-0007 |
|---|---|---|---|
| **Date** | 2026-09-17 | 2026-09-17 | 2026-09-18 |
| **Question** | Q-P004 | Q-P004 | Q-P004 |
| **Hypothesis** | HYP-004 | HYP-004 | HYP-004 |
| **Status** | INCONCLUSIVE | INCONCLUSIVE | complete |
| **Evidence** | CONTROLLED | CONTROLLED | CONTROLLED |
| **Result** | p_c reproduced within tol; FG bond_wrap chi2_red=4.738 fails; C8 width 1/nu=1.2384 fails | Fine-grid width-route; C8 1/nu=0.7375 PASS | bond_wrap resolved; 78/78 C7 cells bit-identical; chi2_red 4.738→2.239 |
| **Decision** | INCONCLUSIVE | INCONCLUSIVE | H0_SUPPORTED |
| **Key files** | CODE/RESULTS/EXP-0005_results.json (22.7 KB) | CODE/RESULTS/EXP-0006_results.json (25.8 KB) | CODE/RESULTS/EXP-0007_results.json (18.8 KB) |
| **Diagnosis** | FG bond_wrap failure = estimator artifact; corrected re-fit gives 1/nu=0.7922 PASS | Width-route validated via bootstrap CI [0.7124, 0.7608] | Non-monotonicity persists but consistent with noise |

| Field | EXP-0009 | EXP-0010 |
|---|---|---|
| **Date** | 2026-09-18 | 2026-09-19 |
| **Question** | Q-P005 | Q-P005 |
| **Hypothesis** | HYP-005 | HYP-005 |
| **Status** | complete | complete |
| **Evidence** | CONTROLLED | CONTROLLED |
| **Result** | Exponents at site p_c=0.5927: D_f=1.8697, γ/ν=1.7596, β/ν=0.1295, τ=1.9404, 1/ν=0.7434; 3 miss by ~1σ | D_f at non-power-of-2 L: 1.8962±0.028 (theory 91/48=1.8958, dev=0.0004) |
| **Decision** | ABNORMAL | LATTICE_ARTIFACT |
| **Diagnosis** | Lattice-size discretization artifact (same class as optical grid-locking at 256²) | Q-P005 resolved: 2D percolation exponents ARE reproduced through lab pipeline |
| **Key files** | Q-P005_exponents/CODE/RESULTS/EXP-0009_results.json (7.1 KB) | Q-P005_exponents/CODE/RESULTS/EXP-0010_results.json (1.4 KB) |

| Field | EXP-0011 | EXP-0013 |
|---|---|---|
| **Date** | 2026-09-20 | 2026-09-23 |
| **Question** | Q-P008 (3D percolation) | Q-P008 (3D percolation) |
| **Status** | complete | running |
| **Result** | 3D percolation pilot study | In progress |
| **Key files** | CODE/RESULTS/EXP-0011_results.json (1.1 KB) | — |

### 2.4 Mathematics

| Field | EXP-0008 | EXP-0014 |
|---|---|---|
| **Date** | 2026-09-18 | 2026-09-21 |
| **Question** | Q-M002 | Q-M005 |
| **Hypothesis** | HYP-005 | HYP-M005 |
| **Status** | complete | complete |
| **Evidence** | CONTROLLED | CONTROLLED |
| **Result** | Normalized prime gaps deviate from Poisson after BH-FDR in 4/4 ranges | δ_n converges to 4.6692016091029 at n=8 for z=2; z=3,4 partial |
| **Decision** | H1_SUPPORTED | CONTROLLED (z=2 validated; z=3,4 partial) |
| **Key files** | RESULTS/EXP-0008_results.json (25.6 KB), REPORT/TECHNICAL_EXP-0008.md | RESULTS/EXP-0014_results.json (4.7 KB), REPORT/TECHNICAL_EXP-0014.md |
| **Key finding** | Deviation survives residue-class conditioning in 4 disjoint ranges; C7 perfect match | z=2 reproduction within 1.4e-4 at n=8; 7/7 controls PASS |
| **Honest framing** | Escalation only — no interpretation, no novelty claim | z=3,4 need refined bracketing |

### 2.5 Acoustics

| Field | EXP-0012 (implied from CHANGELOG) |
|---|---|
| **Date** | ~2026-09-22 |
| **Question** | ACOUSTICS/water_sound_response |
| **Key files** | CHANGELOG.md (2.0 KB), CONTROLS.md (4.3 KB), EXPERIMENT_PLAN.md (7.1 KB), FALSIFICATION/planning_checks.md (7.1 KB), HYPOTHESIS.md (4.8 KB), LITERATURE.md (8.8 KB), PREDICTIONS.md (13.4 KB), QUESTION.md (12.9 KB) |

### 2.6 Other Investigations

| Investigation | Key Files | Status |
|---|---|---|
| rng_certification (Q-I004) | CODE/run_rng_cert.py (12 KB), RESULTS/EXP-0004_results.json (29.6 KB), FIGURES/EXP-0004_pvalue_distribution.png (100 KB) | complete, CONTROLLED; HYP-003 SURVIVED_CONTROLS |
| cone_mosaic_aliasing | CONFIG/prereg_EXP-0012.json (2.3 KB) | complete |

## 3. Experiment Lifecycle Compliance

Per `RESEARCH_RULES.md` §2, mandatory order:
QUESTION → LITERATURE REVIEW → KNOWN EXPLANATIONS → HYPOTHESIS → PREDICTION → BASELINE → CONTROL → EXPERIMENT → STATISTICAL ANALYSIS → FALSIFICATION → REPLICATION → INDEPENDENT METHOD → REPORT

### 3.1 Compliance Assessment

| Phase | Compliance | Notes |
|---|---|---|
| QUESTION | ✅ Full | All experiments linked to registered questions (Q-####) |
| LITERATURE REVIEW | ✅ Partial | LITERATURE.md present for most investigations; EXP-0001/0002/0003 explicitly state no novelty |
| HYPOTHESIS | ✅ Full | HYPOTHESIS.md / prereg files for all major experiments |
| PREDICTION | ✅ Full | PREDICTIONS.md present for all major experiments |
| BASELINE / CONTROL | ✅ Full | CONTROLS.md present; C1–C10 control frameworks documented |
| EXPERIMENT | ✅ Full | Deterministic code, frozen preregs, registry tracking |
| STATISTICAL ANALYSIS | ✅ Full | BH-FDR used throughout; bootstrap CIs standard |
| FALSIFICATION | ✅ Full | FALSIFICATION/planning_checks.md for major investigations |
| REPLICATION | ✅ Full | REPLICATION/ directory with independent implementations |
| INDEPENDENT METHOD | ✅ Full | Independent_check.py/py files in all major experiments |
| REPORT | ✅ Full | REPORT/TECHNICAL_*.md and REPORT/PLAIN_*.md for all major experiments |

### 3.2 Known Exceptions
- **EXP-0001**: Evidence marked "UNTESTED (infra)" despite "complete" status — this is self-described as the infra validation step before other experiments
- **EXP-0008 prereg contradiction**: C7 uses equal-width GOF for independent verdict but same-binning vector for 1e-9 tolerance (noted in results)
- **EXP-0009 ABNORMAL**: Escalation per frozen rule — no tuning, no result manipulation

## 4. Random Seed Registry

| Experiment | Seed(s) | RNG Source |
|---|---|---|
| EXP-0002 | 42 (+ ladder: 7, 123, 2023, 314159, 271828) | Lab RNG (sha256-derived PCG64) |
| EXP-0003 | 42 (+ seed ladder for C9) | Lab RNG |
| EXP-0004 | 42 | Lab RNG |
| EXP-0005/0006/0007 | Frozen from prereg | Lab RNG |
| EXP-0007 new streams | 101, 202, 303 | Lab RNG |
| EXP-0008 | 42 (+ run1_pre_bhfix variant) | Lab RNG |
| EXP-0009 | Per prereg | Lab RNG |
| EXP-0010 | Per prereg | Lab RNG |
| EXP-0014 | Deterministic (root-finding) | N/A (no random component) |

## 5. Dataset Hash Records

Per `REPRODUCIBILITY.md`, every experiment must record:
- Experiment ID
- Date/time (UTC ISO 8601)
- Python version
- Dependency versions
- Git commit (if in repo)
- Random seed
- Parameters
- Dataset file hashes (sha256)
- Result file hashes (sha256)

**Compliance:** The `experiment.json` files are present in all investigation folders (164–2976 bytes depending on complexity). Full hash verification would require recomputation — status: **NOT FULLY VERIFIED** (hashes exist in config but not independently recomputed in this audit).

## 6. Configuration Files

Each major experiment has:
- `prereg_*.json` — Frozen pre-registration (before running)
- `EXP-####_experiment.json` — Post-experiment configuration with full parameters
- `registry.jsonl` — Append-only experiment registry (8 entries across the lab)
- `experiment.json` — Simple one-line status marker (128–165 bytes)

Total config JSON files: **75** across the lab.
