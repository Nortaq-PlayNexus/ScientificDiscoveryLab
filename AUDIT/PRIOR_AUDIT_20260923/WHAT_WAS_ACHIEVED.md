# WHAT_WAS_ACHIEVED — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 14 of 20)

---

## 1. Summary

ScientificDiscoveryLab is a well-organized multi-disciplinary computational research laboratory that has completed **14 experiments** across **5 domains** with **high reproducibility** (84% reproduction score). The lab demonstrates rigorous scientific methodology including pre-registration, independent replication, controls suites, BH-FDR statistical analysis, and honest framing.

## 2. Achievements by Category

### 2.1 Experiments Completed: 14

| Domain | Count | Experiments |
|---|---|---|
| Optics | 2 | EXP-0002 (speckle), EXP-0003 (vortex) |
| Physics (Percolation) | 7 | EXP-0005–0007 (thresholds), EXP-0009–0010 (exponents), EXP-0011, EXP-0013 |
| Mathematics | 2 | EXP-0008 (prime gaps), EXP-0014 (Feigenbaum) |
| Infrastructure | 1 | EXP-0001 |
| Information Theory | 1 | EXP-0004 (RNG) |
| Other | 1 | cone_mosaic_aliasing |
| Acoustics | 0 (active) | Water sound response investigation ongoing |

### 2.2 Key Positive Results: 8 (R1–R8 from external dossier)

| ID | Result | Status |
|---|---|---|
| R1 | 32 µm structure is inherited (not emergent) | CONFIRMED |
| R2 | +24/-24 topological charge conserved | CONFIRMED |
| R3 | Propagation numerics unitary and code-independent | CONFIRMED |
| R4 | Vortex density matches Kac-Rice/Nye-Berry | CONFIRMED |
| R5 | Percolation program yields clean null (H0_SUPPORTED) | CONFIRMED |
| R6 | Methodology reproducible (6/6 independent checks) | CONFIRMED |
| R7 | 2D percolation exponents reproduced | RESOLVED (lattice artifact diagnosed) |
| R8 | Prime gaps deviate from Poisson (escalation only) | H1_SUPPORTED |

### 2.3 Falsified Claims: 5

| Claim | Outcome |
|---|---|
| "45 features / 21–24 split" in propagated field | RULED OUT (independent validator AGAINST) |
| z = 1280 µm excess as topology | RULED OUT (pixelation artifact) |
| Symbolic/"code" content in light | RULED OUT (flat-amplitude control: purified count 0) |
| 32 µm structure as emergent physics | RULED OUT (inherited by construction) |
| Phase randomization as "phase information" | RULED OUT (methodological error) |

### 2.4 Methodological Achievements

| Achievement | Description |
|---|---|
| 5-layer claim hierarchy | Formal rules preventing overclaiming |
| Mandatory experiment lifecycle | QUESTION → LITERATURE → HYPOTHESIS → PREDICTION → BASELINE → CONTROL → EXPERIMENT → STATISTICAL ANALYSIS → FALSIFICATION → REPLICATION → INDEPENDENT METHOD → REPORT |
| Pre-registration system | Frozen prereg files for all major experiments |
| Independent implementation | Every major experiment has independent_check.py |
| Dual detectors | OPTICS experiments use two independent detectors |
| BH-FDR implementation | Engine-level with bug found and fixed |
| Honest framing | Every report has "what this does NOT prove" |
| ABNORMAL protocol | Frozen rule: escalate, do not tune |
| C7 protocol | 78/78 or better independent replication for percolation |

### 2.5 Infrastructure Achievements

| Achievement | Description |
|---|---|
| Shared computational engine | 17 modules (RNG, BH-FDR, surrogates, templates) |
| Experiment registry | 14 experiments tracked (EXP-0001–0014) |
| Research rules document | Complete rules of conduct |
| Reproducibility specification | Machine config, determinism rules, experiment.json |
| 15 field research maps | Acoustics through physics |
| 30+ candidate problem profiles | Detailed feasibility assessments |
| External researcher dossier | 9 documents for Professor Swartzlander |
| 17 unit test files | Covering all src/ packages |

### 2.6 Bug Discovery and Resolution

| Bug | Severity | Resolution |
|---|---|---|
| BH-FDR step-up indexing | HIGH | Fixed, regression-tested, experiment re-run |
| D2 contour detector overcounting | MEDIUM | Replaced by certified intersection detector |
| _cells files saved to wrong directory (Q-P006) | MEDIUM | COPIED to correct location |
| Phase-randomisation / propagation conflation | CRITICAL | Corrected 2026-09-16 |

### 2.7 Anomaly Diagnosis

| Anomaly | Diagnosis | Resolution |
|---|---|---|
| EXP-0009 ABNORMAL | Lattice-size discretization artifact | EXP-0010 confirmed; Q-P005 RESOLVED |
| EXP-0005 FG chi2_red=4.738 | Small-L estimator artifact | EXP-0007 improved to 2.239 |
| EXP-0006 C8 1/nu=1.2384 | Coarse grid | Fine-grid: 0.7375 PASS |

## 3. Quantitative Summary

| Metric | Value |
|---|---|
| Total files | 416 |
| Total experiments | 14 |
| Reproduction score | 50.5/60 (84%) |
| Major claims verified | 8 positive, 5 falsified |
| Independent replications | 11+ |
| Controls per experiment | 8–10 |
| BH-FDR applications | Throughout |
| Pre-registered experiments | 14 (100%) |
| Reports with honest framing | 100% |
| Bugs found and fixed | 4 |
| Anomalies diagnosed | 4 |
| Open questions | 8+ |

## 4. Quality Assessment

### 4.1 Strengths
1. **Methodological rigor**: Full lifecycle compliance with pre-registration, controls, and falsification
2. **Reproducibility**: Independent implementations for all major experiments; C7 bit-identical results
3. **Honesty**: Explicit "what this does NOT prove" in every report; ABNORMAL escalation protocol
4. **Organization**: Clear directory structure, experiment registry, research rules
5. **Documentation**: Technical + plain English summaries, external researcher dossier
6. **Bug fixing**: Bugs found and fixed transparently; old results preserved

### 4.2 Weaknesses
1. **Scope**: Some investigations (acoustics, cone_mosaic) have minimal documentation
2. **Hash verification**: Result file hashes recorded but not independently recomputed
3. **Unexamined data**: sovereign_biolab.db, percolation.rar, 05_DATA/ subdirectories
4. **No real-world validation**: All experiments are computational simulation
5. **Limited statistical depth**: Some experiments could benefit from more extensive parameter sweeps

## 5. Comparison with Prior Work

The `code/string-theory-questions/` project (string theory focus) had:
- 12 Q-series experiments vs 14 here
- String theory domain vs multi-disciplinary here
- Less rigorous methodology (no pre-registration for some) vs full lifecycle here
- 3 independent agents vs 11+ independent implementations here
- Prior audit found 103 claims, many not surviving scrutiny

ScientificDiscoveryLab demonstrates **significantly higher** methodological rigor by every metric.

## 6. Bottom Line

ScientificDiscoveryLab has built a credible, well-documented, reproducible computational research program. Its strongest results are reproductions of established theory (speckle contrast, vortex density, percolation thresholds) with full controls and independent verification. Its most interesting finding (prime gaps deviation) is honestly labeled as escalation rather than discovery. The lab's greatest achievement is its **methodology** — the systematic application of scientific rigor to computational experiments.
