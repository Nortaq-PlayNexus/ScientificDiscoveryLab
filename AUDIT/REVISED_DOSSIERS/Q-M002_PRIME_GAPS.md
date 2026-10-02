# REVISED DOSSIER: Q-M002 — Prime Gap Distribution

**Revised by:** Forensic Audit, 2026-09-23
**Original:** 03_INVESTIGATIONS/MATHEMATICS/prime_gaps/
**Changes:** Documented separately from original; original preserved

---

## 1. What This Investigation IS

A statistical test of whether normalized prime gaps deviate from the Poisson/Gallagher model prediction, using BH-FDR across multiple disjoint ranges.

## 2. What This Investigation DOES NOT Prove

- **No novelty claim**: explicitly labeled "Escalation only — no interpretation, no novelty claim"
- **Does NOT prove** prime gaps have new structure — deviation is in tail shape (lighter than Exp(1)), which is consistent with known Conrey-Goldston-Keating work
- **Does NOT prove** anything beyond ranges below 10⁸

## 3. Key Numbers

| Block | Range | n | mean(δ) | chi2_red | After BH-FDR |
|---|---|---|---|---|---|
| B1 | [10⁴, 10⁵) | 8,362 | 1.002428 | 261.98 | REJECTED (G1) |
| B2 | [10⁵, 10⁶) | 68,905 | 1.001326 | 1,390.85 | REJECTED |
| B3 | [10⁶, 10⁷) | 586,080 | 1.000359 | 11,705.30 | REJECTED |
| B4 | [10⁷, 10⁸) | 5,096,875 | 1.000081 | 94,632.98 | REJECTED |

Combined: χ² = 971,920 (dof 36, χ²_red = 26,998, p = 0)

## 4. Gates and Controls

| Gate/Control | Verdict | Notes |
|---|---|---|
| G1 (χ²) | FAIL | Expected — tests for deviation |
| G2 (KS) | PASS | |
| G3 (tail z) | FAIL | Expected — tests for deviation |
| G4 | PASS | |
| C1 null random | PASS | No significant block (calibration) |
| C2 positive control | PASS | Validates gate power |
| C3 seed ladder | PASS | Identical per-block verdict |
| C4 resolution | PASS | Identical verdict across J |
| C5 method agreement | PASS | χ² vs KS agree |
| C6 residue conditioning | FAIL | No deviation after conditioning (expected) |
| C7 independent | PASS | Perfect block-by-block match |

**C6 FAIL is expected**: The deviation is in tail shape, not residue-class structure.

## 5. Controls Summary: 6/10 PASS (6 functional PASS; C6 FAIL is expected)

## 6. Known Issues

- **C6 FAIL**: Deviation survives conditioning in 4/4 ranges but not on residue classes — this is the expected behavior for a tail-shape deviation
- **Prereg contradiction**: C7 uses equal-width GOF for verdict but same-binning for 1e-9 tolerance (documented in state/EXP-0008_decisions.md)
- **No pre-BH-FDR exclusion**: Both pre-fix and post-fix data preserved (run1_pre_bhfix variants)

## 7. Differences from Original Assessment

| Aspect | Original (prior audit) | Revised |
|---|---|---|
| H1_SUPPORTED | Listed without caveat | Explicitly labeled "escalation only" |
| C6 FAIL | Listed as failure | Contextualized as expected (tail shape, not residue) |
| χ²_red = 26,998 | Listed as anomaly | Contextualized as extremely significant but expected |

## 8. Reproduction Status

- **Deterministic**: Yes (sieve is deterministic; RNG unused for primes)
- **Independent implementation**: PASS (independent_check.py, C7 perfect match)
- **Prereg sha**: 076667a54d12fa49... (recorded)
- **Full instructions**: REPORT/TECHNICAL_EXP-0008.md

## 9. Recommended Wording

> Normalized prime gaps δ = (p_{i+1} − p_i)/ln(p_i) in four disjoint ranges below 10⁸ deviate from the Poisson/Gallagher model in tail shape (combined χ² = 971,920, dof = 36, χ²_red = 26,998, p = 0), with the deviation surviving BH-FDR at α = 0.01 across all 4 blocks. The deviation is in tail shape (lighter than Exp(1), correct mean), not in residue-class structure. This is an escalation for community attention; no novelty claim is made.
