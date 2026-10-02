# STRONGEST_EVIDENCE — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 12 of 20)

---

## 1. Method

Evidence strength ranked by:
- **Reproducibility**: Independent implementation agrees
- **Statistical rigor**: Bootstrap CIs, BH-FDR, controls
- **Controls**: Number and quality of controls
- **Pre-registration**: Frozen before running
- **Cross-verification**: Multiple independent detectors/routes

## 2. Evidence Inventory (Ranked)

### Tier 1: Strongest Evidence (Multiple independent routes, full controls)

#### R1: Vortex Density = Kac-Rice/Nye-Berry (EXP-0003, Q-O002)

| Metric | Value | Strength |
|---|---|---|
| n_meas/n_pred | 0.9952–1.0011 | Within 0.5% at N=1024 |
| Independent detector D2 | Agrees within 1% (max dev 0.6%) | Dual confirmation |
| Independent implementation | 0.992–0.999 within 5% | C6 PASS |
| Charge neutrality | |n+ - n-|/n ≤ 0.0024 | C3 PASS |
| Shift invariance | Half-pixel shift ≤ 2.1% | C4 PASS |
| Seed ladder | 0.9987–1.0022 | C9 PASS |
| Pixels-per-wavelength | Ratio → 1 for P ≥ 8 | C7 PASS |
| BH-FDR | Applied across all cells | C10 PASS |
| Pre-registration | Frozen | ✅ |
| **Confidence** | **VERY HIGH** | |

#### R2: Speckle Contrast Law C(M) = 1/sqrt(M) (EXP-0002, Q-O001)

| Metric | Value | Strength |
|---|---|---|
| r = C·sqrt(M) | [0.984, 1.005] all 20 cells | Full coverage |
| N=256 range | [0.9968, 1.0003] | Highest resolution confirmed |
| KS test | p = 0.27 (exponential not rejected) | C5 PASS |
| Seed ladder | [0.9947, 1.0042] range 0.0095 | C3 PASS |
| Independent implementation | r = 1.0000–1.0005 ± 0.0012 | C6 PASS |
| Interior vs full grid | Agree to ≲ 1% at N ≥ 128 | C7 PASS |
| Pre-registration | Frozen | ✅ |
| **Confidence** | **VERY HIGH** | |

#### R3: Percolation Threshold Reproduction (EXP-0007, Q-P004)

| Metric | Value | Strength |
|---|---|---|
| bond_wrap p_c | 0.500687 ± 0.0317 | |d| from 0.5 = 0.000687 |
| C7 independent | 78/78 cells bit-identical | Perfect replication |
| FG chi2_red | 4.738 → 2.239 (PASS) | Diagnostic improvement |
| C7 cross-experiment | Covered EXP-0005/0006 cells too | Broad coverage |
| C1 determinism | k=304, n=600 both runs | PASS |
| Pre-registration | Frozen | ✅ |
| **Confidence** | **VERY HIGH** | |

#### R4: RNG Certification (EXP-0004, Q-I004)

| Metric | Value | Strength |
|---|---|---|
| KS uniformity | PASS | Standard battery |
| Binomial band | PASS | Standard battery |
| BH-FDR | PASS | Standard battery |
| C7 independent | 30/30 agreement | Perfect replication |
| Controls | Battery validated on controls | C1/C2 PASS |
| **Confidence** | **HIGH** | |

### Tier 2: Strong Evidence (Independent replication, good controls)

#### R5: Prime Gaps Deviation from Poisson (EXP-0008, Q-M002)

| Metric | Value | Strength |
|---|---|---|
| χ²_red | 26,998 (dof 36, p = 0) | Extremely significant |
| BH-FDR | G1/G3 rejected in 4/4 blocks | Full coverage |
| C7 independent | Perfect block-by-block match | Perfect replication |
| Seed ladder | Identical verdict across seeds | C3 PASS |
| Method agreement | χ² vs KS agree after BH-FDR | C5 PASS |
| Pre-registration | Frozen, sha256 recorded | ✅ |
| Honest framing | "Escalation only" | ✅ |
| **Caveat** | **No novelty claimed** | |
| **Confidence** | **HIGH** (but explicitly not a discovery) | |

#### R6: Feigenbaum δ → 4.6692 (EXP-0014, Q-M005)

| Metric | Value | Strength |
|---|---|---|
| δ_8 | 4.66906 vs 4.6692016091029 | dev = 1.4e-4 |
| C7 independent | manual delta_4 vs engine diff < 1e-10 | Excellent |
| Convergence monotonicity | PASS | C2 PASS |
| Seed variation | 5 seeds identical | C3 PASS |
| Method variation | Brentq vs Newton diff < 1e-6 | C4 PASS |
| Precision | xtol sensitivity PASS | C6 PASS |
| **Confidence** | **HIGH** | |

#### R7: 32 µm Structure Inherited (External Dossier R1)

| Metric | Value | Strength |
|---|---|---|
| Generator column pitch | 32.0 µm | Design parameter |
| Autocorrelogram | Periodic near-32 µm correlation | Matches input |
| Emergence control | C-control ratio 0.595 INVALID; B/H VALID | Inherited, not emergent |
| Random-input control | 21,545 features, no 32 µm structure | Null control |
| **Confidence** | **HIGH** (but "inherited by construction") | |

#### R8: Topological Charge Conservation (External Dossier R2)

| Metric | Value | Strength |
|---|---|---|
| +24/-24 balance | Net 0 | By design |
| Independent 48-core validation | Reproduced balance | Independent confirmation |
| Charge conservation | Conserved after propagation | Physics consistency |
| "45 features" claim | AGAINST in validator battery | Falsified |
| **Confidence** | **HIGH** | |

### Tier 3: Supporting Evidence (Single experiment, fewer controls)

| Evidence | Experiment | Confidence | Notes |
|---|---|---|---|
| 3D percolation pilot | EXP-0011 | MEDIUM | Early-stage |
| Phase unitarity | External R3 | HIGH | ~10⁻¹³ numerical check |
| Near-Nyquist failure zone | EXP-0003 C8 | HIGH | Documented, not claimed as physics |
| Lattice artifact diagnosis | EXP-0010 | HIGH | D_f=1.8962±0.028 vs theory |
| Acoustic investigation | ACOUSTICS | LOW | Early-stage |
| Cone mosaic aliasing | OTHER | LOW | Minimal documentation |

## 3. Evidence vs Claims Matrix

| Claim | Evidence Tier | Does Evidence Support Claim? |
|---|---|---|
| "Vortex density = Kac-Rice/Nye-Berry" | Tier 1 | ✅ YES — strongest evidence |
| "Speckle contrast = 1/sqrt(M)" | Tier 1 | ✅ YES |
| "Percolation threshold reproduced" | Tier 1 | ✅ YES |
| "RNG passes standard battery" | Tier 1 | ✅ YES |
| "Prime gaps deviate from Poisson" | Tier 2 | ✅ YES (with escalation caveat) |
| "Feigenbaum constant confirmed" | Tier 2 | ✅ YES (z=2 only) |
| "32 µm structure is inherited" | Tier 2 | ✅ YES (by design, not emergent) |
| "48-vortex lattice +24/-24" | Tier 2 | ✅ YES |
| "2D percolation exponents reproduced" | Tier 2 | ✅ YES |
| "32 µm structure is new physics" | — | ❌ NO — falsified |
| "45 features in propagated field" | — | ❌ NO — falsified |
| "Phase is information" | — | ❌ NO — falsified |
| "z=1280 is topology" | — | ❌ NO — pixelation artifact |

## 4. Evidence Gaps

| Gap | Impact | Resolution |
|---|---|---|
| No real-optics experiment | Cannot confirm simulation results in physical system | Proposed in INTEGRATION_PLAN.md |
| Acoustics investigation thin | Limited evidence for water sound response | More data needed |
| sovereign_biolab.db unexamined | Unknown contents | Query recommended |
| Hash verification incomplete | Cannot verify data integrity in transit | Recompute SHA256 |

## 5. Summary

The lab's strongest evidence consists of **Tier 1 results** with:
- Multiple independent measurement routes (D1/D2 detectors, independent implementations)
- Full control suites (C1–C10)
- Frozen pre-registration
- Explicit "what this does NOT prove" framing

The lab's **most defensible single claim** is:
> "The Kac-Rice/Nye-Berry vortex density formula is reproduced for well-resolved narrow-band isotropic fields with n_meas/n_pred ∈ [0.9952, 1.0011], confirmed by two independent detectors and an independent implementation."
