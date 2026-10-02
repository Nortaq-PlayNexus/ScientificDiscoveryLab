# DO_NOT_CLAIM — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 17 of 20)

---

## 1. Purpose

Per the instruction document: "Generate a 'DO NOT CLAIM' document: what is NOT YET established."

This document lists everything that CANNOT be claimed based on current evidence in ScientificDiscoveryLab.

## 2. Claims That Cannot be Made

### 2.1 Cannot Claim New Discoveries

| Claim | Why Not | What Could Change This |
|---|---|---|
| "We discovered the Kac-Rice/Nye-Berry formula for vortex density" | This is textbook (Nye & Berry 1974) | Nothing — this is a reproduction |
| "We discovered the speckle contrast law" | This is textbook (Goodman) | Nothing — this is a reproduction |
| "We discovered percolation critical exponents" | Standard results (Stauffer & Aharony) | Nothing — this is a reproduction |
| "We discovered the Feigenbaum constant" | Published in 1978 | Nothing — this is a reproduction |
| "We discovered prime gap statistics" | Known deviations from Poisson model | Escalation pending community review |
| "The 32 µm structure is a new physical phenomenon" | Inherited from generator design | Real-optics experiment needed |

### 2.2 Cannot Claim Physical Confirmation

| Claim | Status | Needed |
|---|---|---|
| "Simulation results match real laser experiments" | NOT YET TESTED | Real-optics experiment (ref: INTEGRATION_PLAN.md) |
| "The vortex lattice exists in physical optics" | Simulation only | Physical experiment |
| "Speckle contrast measured with real instrument" | Simulation only | Physical measurement |

### 2.3 Cannot Claim Computational Results Not Verified

| Claim | Status | Needed |
|---|---|---|
| "Result file integrity confirmed by hash" | Hashes recorded, NOT recomputed | Independent SHA256 verification |
| "sovereign_biolab.db contains experiment metadata" | Database unexamined | Query the database |
| "percolation.rar contains relevant data" | Archive unextracted | Extract and compare |
| "05_DATA/ contains required raw data" | Directories unexamined | Inspect contents |
| "3D percolation exponents (Q-P008)" | EXP-0013 running, not complete | Complete EXP-0013 |
| "Acoustics results" | Investigation early-stage | More data needed |
| "cone_mosaic aliasing characterization" | Minimal documentation | More detail needed |

### 2.4 Cannot Claim Universality

| Claim | Why Not |
|---|---|
| "Our RNG passes all standard batteries" | Only lightweight battery tested; NIST SP 800-22 not run |
| "Our percolation results hold for all lattices" | Only square lattice tested (2D and 3D pilot) |
| "Our vortex results hold for all spectra" | Only isotropic spectra tested (per derivation requirement) |
| "Our speckle results hold for all apertures" | Only single aperture fraction (1/8) tested |
| "Our prime gap results extend to infinity" | Only ranges below 10^8 tested |
| "Feigenbaum universality holds for all z" | Only z=2 fully validated; z=3,4 partial |

### 2.5 Cannot Claim Novelty

| Claim | Why Not |
|---|---|
| "We found novel structure in propagated light fields" | 32 µm structure is inherited by construction |
| "We found novel charge patterns in vortices" | +24/-24 is by design |
| "We found novel prime gap deviations" | Known deviation in tail shape; escalation only |
| "We found novel phase information in light" | RULED OUT — propagation artifact |
| "We found novel symbols in light intensity" | RULED OUT — pixelation artifact |

### 2.6 Cannot Claim Beyond Scale/Resolution

| Claim | Why Not |
|---|---|
| "Vortex density holds at N < 256" | Low-N shows finite-grid deviations |
| "Percolation threshold accurate to 10⁻⁶" | Current SE ≈ 0.0317 for bond_wrap |
| "Feigenbaum constants for z > 4" | Not computed |
| "Prime gap statistics above 10⁸" | Only tested to 10⁸ |
| "Speckle contrast for M > 16" | Only tested M ≤ 16 |

### 2.7 Cannot Claim Causal Mechanisms

| Claim | Why Not |
|---|---|
| "The near-Nyquist failure is caused by X" | Characterized, not explained from first principles |
| "The lattice artifact mechanism is Y" | Diagnosed, not mechanistically understood |
| "The prime gap tail shape has explanation Z" | Tail shape noted; explanation not provided |

## 3. Summary Statistics

| Category | Count |
|---|---|
| Cannot claim new discoveries | 6 |
| Cannot claim physical confirmation | 3 |
| Cannot claim unverified computational results | 6 |
| Cannot claim universality | 6 |
| Cannot claim novelty | 5 |
| Cannot claim beyond scale | 6 |
| Cannot claim causal mechanisms | 3 |
| **Total unclaimable items** | **35** |

## 4. What IS Establishes

For contrast, what CAN be claimed (see STRONGEST_DEFENSIBLE_CLAIMS.md):
1. Reproductions of established theory with full controls and independent verification
2. Diagnostic characterizations of failure modes and artifacts
3. Methodological innovations in experimental pipeline (e.g., certified contour detector)
4. Honest escalations of interesting anomalies (e.g., prime gaps tail shape)
5. Engineering certifications (RNG, engine validation)

## 5. Recommendation for Future Work

To convert "DO NOT CLAIM" items to "CAN CLAIM":

1. **Run real-optics experiments** → converts simulation claims to physical confirmation
2. **Complete EXP-0013** → 3D percolation exponents become claimable
3. **Verify SHA256 hashes** → result integrity becomes confirmed
4. **Examine sovereign_biolab.db** → database contents become known
5. **Extend prime gap analysis** beyond 10⁸ → broader claims possible
6. **Full NIST battery** for RNG → universal RNG claim possible
7. **Develop causal theories** for observed anomalies → mechanistic understanding
