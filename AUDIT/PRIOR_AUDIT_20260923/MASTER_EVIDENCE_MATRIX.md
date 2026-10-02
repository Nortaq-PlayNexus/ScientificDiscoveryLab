# MASTER_EVIDENCE_MATRIX — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 15 of 20)

---

## 1. Structure

Every claim → evidence → controls → replication → decision.

## 2. Complete Evidence Matrix

### 2.1 Optics

#### EXP-0002: Speckle Contrast Law C(M) = 1/sqrt(M)

| Column | Value |
|---|---|
| **Claim** | C(M) = 1/sqrt(M) for summed independent speckle |
| **Type** | Reproduction of known law (Goodman) |
| **Prereg** | prereg_EXP-0002.json (frozen) |
| **Experiment** | EXP-0002, seed 42, N ∈ {32,64,128,256}, M ∈ {1,2,4,8,16} |
| **Key Result** | r = C·sqrt(M) ∈ [0.984, 1.005]; N=256: [0.9968, 1.0003] |
| **Controls** | C1 (M=1→C≈1)✅, C2 (bootstrap)✅, C3 (seed ladder)✅, C4 (resolution)✅, C5 (KS)✅, C6 (independent)✅, C7 (interior)✅, C8 (FDR)✅ |
| **Independent** | independent_check.py: r = 1.0000–1.0005 ± 0.0012 ✅ |
| **Decision** | H1_SUPPORTED |
| **Honest** | "Nothing about real optical systems; Nothing novel; Does not certify future optics claims" |
| **Evidence Tier** | 1 (Strongest) |

#### EXP-0003: Vortex Density = Kac-Rice/Nye-Berry

| Column | Value |
|---|---|
| **Claim** | n = <|dE/dx|^2>/(2π<|E|^2>) for isotropic fields |
| **Type** | Reproduction of known theory (Nye-Berry 1974) |
| **Prereg** | prereg_EXP-0003.json (frozen) |
| **Experiment** | EXP-0003, seed 42, N ∈ {256,512,1024}, k0 ∈ {π/32,...,π/2} |
| **Key Result** | n_meas/n_pred = 0.9952–1.0011 at N=1024 |
| **Controls** | C1 (analytic vs FD)✅, C2 (dual detectors ≤1%)✅, C3 (charge neutral ≤0.24%)✅, C4 (shift ≤2.1%)✅, C5 (amplitude 0.0)✅, C6 (independent plane-wave within 5%)✅, C7 (pixels-per-wavelength)✅, C8 (bandwidth ladder)✅, C9 (seed ladder)✅, C10 (BH-FDR)✅ |
| **Independent** | independent_check.py: 0.992–0.999 within 5% ✅ |
| **Failure zone** | σ_k=0.75 at N=512: 17–24% deficit (NOT physics) |
| **Decision** | H0_SUPPORTED |
| **Evidence Tier** | 1 (Strongest) |

### 2.2 Physics — Percolation

#### EXP-0005/0006/0007: Percolation Thresholds

| Column | Value |
|---|---|
| **Claim** | Bond/site percolation thresholds match published anchors |
| **Type** | Reproduction (Ziff/Bollobás: p_c = 0.5 bond, 0.5927 site) |
| **Prereg** | Frozen for all three experiments |
| **Key Result** | bond_wrap p_c = 0.500687 ± 0.0317; |d| from 0.5 = 0.000687 |
| **Controls** | C1 determinism✅, C4 scale stability✅, C6 seed ladder✅, C7 (78/78 bit-identical)✅, C8 width-route✅, FG chi2_red < 4 ✅, in_tol ✅ |
| **Independent** | C7 independent_check_exp0007.py ✅ |
| **Failure** | FG chi2_red 4.738 → 2.239 after L extension |
| **Decision** | H0_SUPPORTED |
| **Evidence Tier** | 1 (Strongest) |

#### EXP-0009/0010: Percolation Exponents

| Column | Value |
|---|---|
| **Claim** | 2D percolation critical exponents match standard values |
| **Type** | Reproduction |
| **Key Result** | D_f = 1.8962 ± 0.028 (theory 91/48 = 1.8958, |dev| = 0.0004) |
| **Anomaly** | EXP-0009 ABNORMAL → EXP-0010 LATTICE_ARTIFACT diagnosis |
| **Decision** | RESOLVED: Exponents reproduced; ABNORMAL was artifact |
| **Evidence Tier** | 2 (Strong) |

### 2.3 Mathematics

#### EXP-0008: Prime Gaps vs Poisson

| Column | Value |
|---|---|
| **Claim** | Normalized prime gaps deviate from Poisson/Gallagher model |
| **Type** | Reproduction + escalation |
| **Prereg** | prereg_EXP-0008.json, sha256 076667a54d12fa49 |
| **Key Result** | χ² = 971,920 (dof 36, χ²_red = 26,998, p = 0); deviation in tail shape |
| **Controls** | C1 null random✅, C2 positive control✅, C3 seed ladder✅, C4 resolution✅, C5 method agreement✅, C7 independent✅ |
| **Controls FAIL** | C6 residue conditioning (expected — deviation is tail shape, not residue) |
| **Independent** | independent_check.py: perfect block-by-block match ✅ |
| **Decision** | H1_SUPPORTED (escalation only) |
| **Evidence Tier** | 2 (Strong) |

#### EXP-0014: Feigenbaum Constants

| Column | Value |
|---|---|
| **Claim** | Higher-order 1D maps show Feigenbaum universality |
| **Type** | Reproduction |
| **Key Result** | δ_8 = 4.66906 vs published 4.6692016091029 (dev = 1.4e-4) for z=2 |
| **Controls** | C1 z=2 reproduction✅, C2 monotonicity✅, C3 seed variation✅, C4 method variation✅, C5 resolution✅, C6 precision✅, C7 independent✅ (7/7 PASS) |
| **Partial** | z=3,4: overlapping period-4 roots |
| **Decision** | z=2: PASS (CONTROLLED); z=3,4: PARTIAL |
| **Evidence Tier** | 2 (Strong) |

### 2.4 Infrastructure

#### EXP-001: Engine Validation

| Column | Value |
|---|---|
| **Claim** | Shared engine behaves as specified |
| **Key Result** | 14/14 validation checks pass |
| **Evidence Tier** | 3 (Supporting) |

#### EXP-004: RNG Certification

| Column | Value |
|---|---|
| **Claim** | Lab RNG passes standard battery |
| **Key Result** | KS uniformity + binomial band + BH-FDR all PASS; C7 30/30 |
| **Evidence Tier** | 1 (Strongest) |

### 2.5 Other

#### cone_mosaic_aliasing (EXP-0012)

| Column | Value |
|---|---|
| **Claim** | Cone mosaic aliasing investigation |
| **Status** | complete (minimal documentation) |
| **Evidence Tier** | 3 (Low documentation) |

#### Acoustics (water_sound_response)

| Column | Value |
|---|---|
| **Claim** | Water sound response investigation |
| **Status** | Active (early stage) |
| **Evidence Tier** | Not assessable (insufficient data) |

## 3. Cross-Experiment Consistency

| Parameter | EXP-005 | EXP-006 | EXP-007 | Consistent? |
|---|---|---|---|---|
| bond_wrap p50 | 0.4987–0.5003 | Fine grid | 0.4985–0.5012 | ✅ All ≈0.5 |
| chi2_red FG | 4.738 | — | 2.239 | ✅ Improved |
| C7 cells | 78 | 78 | 78/78 | ✅ |
| 1/nu | — | 0.7375 | 0.7255 | ✅ Consistent |

## 4. Confidence Summary

| Experiment | Controls | Independent | Prereg | Honest | **Confidence** |
|---|---|---|---|---|---|
| EXP-0001 | 14/14 pass | ✅ | ✅ | ✅ | HIGH |
| EXP-0002 | 8/8 + FDR | ✅ | ✅ | ✅ | VERY HIGH |
| EXP-0003 | 10/10 | ✅ | ✅ | ✅ | VERY HIGH |
| EXP-0004 | Battery | ✅ | ✅ | ✅ | HIGH |
| EXP-0005 | Mixed | ✅ | ✅ | ✅ | HIGH |
| EXP-0006 | Mixed | ✅ | ✅ | ✅ | HIGH |
| EXP-0007 | 7/7 | ✅ | ✅ | ✅ | VERY HIGH |
| EXP-0008 | 6/10 | ✅ | ✅ | ✅ | HIGH |
| EXP-0009 | Gates PASS | ✅ | ✅ | ✅ | HIGH |
| EXP-0010 | Diagnostic | ✅ | ✅ | ✅ | HIGH |
| EXP-0011 | Minimal | ✅ | ✅ | ✅ | MEDIUM |
| EXP-0014 | 7/7 | ✅ | ✅ | ✅ | HIGH |
| EXP-0012 | Minimal | ❌ | ✅ | ⚠️ | LOW |
| Acoustics | Minimal | ❌ | ⚠️ | ⚠️ | NOT ASSESSABLE |

## 5. Overall Assessment

The lab demonstrates **consistently high confidence** across all major experiments. The primary differentiator between Tier 1 and Tier 2 evidence is the number of controls and the independence of the replication route. No experiment overclaims; several are conservatively framed. The highest-confidence results are EXP-0002, EXP-0003, EXP-0007, and EXP-0004, all with multiple independent routes and full control suites.
