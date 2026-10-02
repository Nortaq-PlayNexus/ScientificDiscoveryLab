# POTENTIAL_DISCOVERIES — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 13 of 20)

---

## 1. Philosophy

Per `RESEARCH_RULES.md` §1:
> "The lab never jumps from 'interesting pattern' to 'new discovery.'"

This document identifies results that could potentially be developments, were it not for the lab's rigorous honesty framework.

## 2. Evaluated Candidates

### 2.1 Vortex Density Statistics (EXP-0003) — Not a Discovery

**What was found:** Vortex density matches Kac-Rice/Nye-Berry theory for well-resolved fields
**Why not a discovery:** This is established theory (Nye & Berry 1974; Berry 1978, 2000). The experiment is a **reproduction**, not a discovery.
**What IS interesting:** The near-Nyquist failure zone characterization (17–24% deficit) is a new characterization of detector limitations, not physics.
**Honest assessment:** R4 in external dossier — "the strongest quantitative link to published optics literature" — explicitly stated as agreement with standard theory.

### 2.2 Prime Gaps Deviation (EXP-0008) — Escalation, Not Discovery

**What was found:** Normalized prime gaps deviate from Poisson model after BH-FDR in 4/4 disjoint ranges below 10^8
**Why not a discovery:** 
- Known that Gallagher's Poisson model is not exact for finite ranges
- Explicitly labeled "H1_SUPPORTED" with "escalation only, no interpretation, no novelty claim"
- Deviation survives conditioning but is in tail shape (lighter than Exp(1)), not in mean
**What IS interesting:** Reproducible deviation across disjoint ranges; C7 perfect match; pre-registered
**Honest assessment:** Escalation for community attention; NOT a formal discovery

### 2.3 Feigenbaum δ Convergence (EXP-0014) — Reproduction

**What was found:** δ_n converges to 4.6692016091029 at n=8 for z=2 maps
**Why not a discovery:** This IS the Feigenbaum constant — the experiment reproduces a known universal constant
**What IS interesting:** Partial results for z=3,4; convergence diagnostics
**Honest assessment:** z=2 is CONTROLLED reproduction; z=3,4 are PARTIAL

### 2.4 32 µm Structure (External Dossier R1) — Inherited, Not Emergent

**What was found:** 32 µm periodic correlation in propagated field
**Why not a discovery:** The generator contains a 32.0 µm column pitch; the pattern is **inherited by construction**
**Evidence against emergence:** C-control ratio 0.595 INVALID; B/H VALID; random-input control shows no 32 µm structure
**Honest assessment:** "Real, but inherited by construction" (KEY_RESULTS.md)

### 2.5 Phase-Randomisation "Phase Information" — Falsified

**What was found:** ~0.13 difference between I(x) and I(rand) after propagation
**Why not a discovery:** Phase-randomisation preserves intensity exactly (|A·e^{iφ}|² = A²); the difference after propagation is natural for phase-incoherent vs coherent fields
**When it was flagged:** 2026-09-16, corrected before reporting
**Honest assessment:** Methodology error; explained many early "positive" findings

### 2.6 2D Percolation Exponents (EXP-0009/0010) — Reproduction

**What was found:** D_f = 1.8958 (theory 91/48) confirmed at non-power-of-2 lattices
**Why not a discovery:** Standard percolation theory result
**What IS interesting:** ABNORMAL from EXP-0009 was diagnosed as a lattice artifact — this is a methodological finding
**Honest assessment:** "2D percolation exponents ARE reproduced through the lab pipeline"

### 2.7 RNG Certification (EXP-0004) — Certification, Not Discovery

**What was found:** Lab RNG passes KS uniformity + binomial band + BH-FDR
**Why not a discovery:** This is a quality assurance certification, not a new result
**What IS interesting:** C7 independent implementation agrees 30/30
**Honest assessment:** CERTIFIED

### 2.8 Percolation Threshold (EXP-0007) — Reproduction

**What was found:** bond_wrap p_c = 0.500687 (|d| from 0.5 = 0.000687)
**Why not a discovery:** Standard percolation threshold for square lattice is exactly 0.5
**What IS interesting:** 78/78 C7 cells bit-identical; non-monotonicity resolved
**Honest assessment:** H0_SUPPORTED (threshold matches theory)

## 3. What WOULD Count as a Discovery

Per `RESEARCH_RULES.md`, a discovery requires movement from Layer 2 → Layer 3 → Layer 4 through the full experiment lifecycle. For ScientificDiscoveryLab, the bar is:

1. **A reproducible deviation from established theory** (not a confirmation of known theory)
2. **Surviving all controls and falsification attempts**
3. **Surviving independent replication by a different method**
4. **Being new to science** (not previously published)
5. **Having a full experiment lifecycle documented** (QUESTION → REPORT)

### 3.1 Closest Candidate

**EXP-0008 (Prime Gaps)** is the closest to a discovery:
- Reproducible deviation from Poisson model in 4 disjoint ranges
- Survives residue-class conditioning
- Independent C7 implementation agrees perfectly
- BUT: explicitly labeled "escalation only" and no novelty claim made
- The deviation IS in the tail shape (lighter than Exp(1)), which is known to exist from Conrey-Goldston-Keating work

**Assessment:** This is a high-quality reproduction/confirmation with an interesting anomaly (tail shape), but does NOT meet the discovery bar.

## 4. Unexplored Territories That Could Yield Discoveries

| Area | Current Status | Potential |
|---|---|---|
| Real-optics validation | NOT TESTED | Could confirm/correct simulation results |
| 3D percolation (EXP-0013) | Running | Unknown |
| Q-M001 (Collatz statistics) | OPEN | Could yield interesting statistics |
| Q-M003 (Digit normalcy) | OPEN | Very likely null |
| Q-M004 (Sandpile exponents) | OPEN | Standard reproduction |
| Q-M006 (First-passage universality) | OPEN | Could yield scaling results |
| Q-O003 (Propagation invariance) | OPEN | Audit vs surrogate nulls |
| Q-P008 (3D percolation) | Active | Extends known results to 3D |
| ACOUSTICS/water_sound | Active | Novel domain |
| cone_mosaic_aliasing | complete | Could yield aliasing characterization |

## 5. Summary

| Assessment | Count | Examples |
|---|---|---|
| Clear reproductions (known theory confirmed) | 5 | Speckle, vortex, percolation threshold, Feigenbaum δ, RNG |
| Escalations (interesting anomalies) | 1 | Prime gaps tail shape |
| Falsified claims | 5 | 32µm emergence, 45 features, phase info, z=1280 topology, code content |
| Potential future discoveries | 0 (currently) | Several open questions |
| Novel findings | 1 | Near-Nyquist failure zone characterization |

The lab's strongest **novel** finding is the **characterization of the near-Nyquist failure zone** in vortex density detection (EXP-0003 C8) — a documented limitation of computational vortex counting at high spatial frequencies, not a physics discovery but a useful methodological result.
