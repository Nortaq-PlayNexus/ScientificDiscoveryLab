# CLAIM_LANGUAGE_AUDIT — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 11 of 20)

---

## 1. Method

Every claim in the project's reports and documentation was evaluated against the 5-layer claim hierarchy from `RESEARCH_RULES.md`:

1. **Instrument/measurement result** — what the computer produced
2. **Statistical result** — whether the measurement is distinguishable from the null
3. **Physical/scientific claim** — what the result means about the world/model
4. **Novelty claim** — that something is new to science

Movements between layers require the experiment lifecycle to be completed. The lab never jumps from "interesting pattern" to "new discovery."

## 2. Claim Assessment

### 2.1 Claims at Layer 1 (Instrument/Measurement Result) — APPROPRIATE

| Claim | Source | Assessment |
|---|---|---|
| "r = C·sqrt(M) lies in [0.984, 1.005]" (EXP-0002) | REPORT/TECHNICAL_SUMMARY.md | ✅ CORRECT — statistical measurement |
| "n_meas/n_pred = 0.9952–1.0011" (EXP-0003) | REPORT/TECHNICAL_SUMMARY.md | ✅ CORRECT — statistical measurement |
| "bond_wrap p50 = 0.50021" (EXP-0005) | EXPERIMENT_REGISTRY.md | ✅ CORRECT — statistical measurement |
| "χ²_red = 26,998, p = 0" (EXP-0008) | REPORT/TECHNICAL_EXP-0008.md | ✅ CORRECT — statistical measurement |
| "δ_8 = 4.66906 vs 4.6692" (EXP-0014) | REPORT/TECHNICAL_EXP-0014.md | ✅ CORRECT — computational result |
| "D_f = 1.8962 ± 0.028" (EXP-0010) | CHANGELOG.md | ✅ CORRECT — computational result |
| "C7 78/78 cells bit-identical" (EXP-0007) | REPORT/TECHNICAL_EXP-0007.md | ✅ CORRECT — computational result |

### 2.2 Claims at Layer 2 (Statistical Result) — APPROPRIATE WITH QUALIFICATION

| Claim | Source | Assessment |
|---|---|---|
| "H1_SUPPORTED" (EXP-0002) | EXPERIMENT_REGISTRY.md | ✅ CORRECT — statistical conclusion |
| "H0_SUPPORTED" (EXP-0003) | EXPERIMENT_REGISTRY.md | ✅ CORRECT — statistical conclusion |
| "H1_SUPPORTED" (EXP-0008) | EXPERIMENT_REGISTRY.md | ✅ CORRECT but flagged as "escalation only" |
| "CERTIFIED" (EXP-0004) | EXPERIMENT_REGISTRY.md | ✅ CORRECT — statistical certification |
| "ABNORMAL" (EXP-0009) | CHANGELOG.md | ✅ CORRECT — escalated per frozen rule |
| "LATTICE_ARTIFACT" (EXP-0010) | CHANGELOG.md | ✅ CORRECT — diagnostic conclusion |

### 2.3 Claims at Layer 3 (Physical/Scientific Claim) — ACCEPTABLE

| Claim | Source | Assessment |
|---|---|---|
| "C(M) = 1/sqrt(M) reproduced" (EXP-0002) | REPORT/TECHNICAL_SUMMARY.md | ✅ ACCEPTABLE — explicitly stated as reproduction of known law |
| "Vortex density = Kac-Rice/Nye-Berry" (EXP-0003) | REPORT/TECHNICAL_SUMMARY.md | ✅ ACCEPTABLE — explicitly stated as reproduction of known theory |
| "2D percolation exponents ARE reproduced" (Q-P005 resolved) | CHANGELOG.md | ✅ ACCEPTABLE — stated as reproduction |
| "Lab RNG passes standard battery" (EXP-0004) | REPORT/TECHNICAL_SUMMARY.md | ✅ ACCEPTABLE — certification of method |
| "32 µm structure is real — because it is built in" (R1) | KEY_RESULTS.md | ✅ CORRECT — correctly characterized as inherited |
| "48-vortex lattice, +24/-24, net 0" (R2) | KEY_RESULTS.md | ✅ CORRECT — confirmed by independent validator |
| "Propagator is not dissipating energy" (R3) | KEY_RESULTS.md | ✅ CORRECT — unitarity verified |
| "Vortex density statistics match theory" (R4) | KEY_RESULTS.md | ✅ CORRECT — stated as strongest quantitative link |

### 2.4 Claims at Layer 4 (Novelty Claim) — PROPERLY SUPPRESSED

| Claim | Source | Assessment |
|---|---|---|
| No novelty claimed in EXP-0002 | REPORT/TECHNICAL_SUMMARY.md | ✅ CORRECT — "Nothing novel: the law is textbook (Goodman)" |
| No novelty claimed in EXP-0003 | REPORT/TECHNICAL_SUMMARY.md | ✅ CORRECT — "No new physics" |
| No novelty claimed in EXP-0008 | REPORT/TECHNICAL_EXP-0008.md | ✅ CORRECT — "Escalation only — no interpretation, no novelty claim" |
| "Discovery-neutral" (Executive Summary) | EXECUTIVE_SUMMARY.md | ✅ CORRECT — explicitly stated |

### 2.5 What the Project Does NOT Claim (Honest Framing)

Every major report contains "what this does NOT prove" sections:

| Experiment | Honest Disclaimers |
|---|---|
| EXP-0002 | "Nothing about real optical systems"; "Nothing novel"; "Does not certify future optics claims" |
| EXP-0003 | "No new physics"; "No claim of novelty"; "Only isotropic spectra tested" |
| EXP-0008 | "Escalation only"; "No interpretation" |
| EXP-0014 | "z=3,4 need refined bracketing"; "Alpha not signed" |
| All | "Deterministic computer simulation" (per Swartzlander dossier) |

## 3. Claim Language Issues Found

### 3.1 Minor Issues (No Correction Needed)

1. **EXP-0001 evidence state**: Listed as "UNTESTED (infra)" but status "complete" — slightly contradictory but self-explained
2. **EXP-0005/0006 status**: "INCONCLUSIVE" — appropriate for experiments with mixed gate results
3. **Q-M002 decision**: "H1_SUPPORTED" in EXPERIMENT_REGISTRY.md but "escalation only" in report — consistent if escalation is understood as not yet a formal discovery

### 3.2 No Overclaims Found

The lab's research rules (5-layer hierarchy) and culture ("honest framing") appear to have prevented overclaiming. All claims are properly classified.

## 4. Comparison with Prior Audits

### 4.1 string-theory-questions/AUDIT/ (Phases 0–7)

The prior audit at `code/string-theory-questions/AUDIT/` found:
- WGC formulation uses q instead of g
- Tower Hypothesis pass criterion κ≤10 ≠ standard κ=O(1)
- F=2π·M_Pl·m_soft does NOT produce claimed m_soft range
- 51/5000 violations at c₁=0.5 with AND condition

These findings do NOT apply to ScientificDiscoveryLab, which is a different project.

## 5. Claim Register Summary

| Layer | Count | Status |
|---|---|---|
| Layer 1 (Instrument) | 7 | ✅ All appropriate |
| Layer 2 (Statistical) | 6 | ✅ All appropriate with qualification |
| Layer 3 (Physical) | 8 | ✅ All acceptable |
| Layer 4 (Novelty) | 0 active claims | ✅ Properly suppressed |
| Overclaims | 0 | ✅ None found |
| Honest disclaimers | 4+ | ✅ Present in all major reports |

## 6. Recommendations

1. **No corrections needed** for claim language in existing documents
2. **Consider formalizing** the "escalation only" status of EXP-0008 to prevent misinterpretation
3. **Add explicit "NOT a discovery"** statement to the Acoustics investigation (when completed)
4. **Ensure** new claims follow the 5-layer hierarchy from RESEARCH_RULES.md
