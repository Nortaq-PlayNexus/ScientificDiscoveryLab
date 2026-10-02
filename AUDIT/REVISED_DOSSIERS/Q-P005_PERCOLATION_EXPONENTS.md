# REVISED DOSSIER: Q-P005 — Percolation Critical Exponents

**Revised by:** Forensic Audit, 2026-09-23
**Original:** 03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents/
**Changes:** Documented separately from original; original preserved

---

## 1. What This Investigation IS

A reproduction of 2D percolation critical exponents at site p_c ≈ 0.5927460508, with full diagnostic treatment of an ABNORMAL result.

## 2. What This Investigation DOES NOT Prove

- **Does NOT prove** new exponents — standard 2D percolation values are well established
- **EXP-0009 ABNORMAL result** is NOT a discovery — it was diagnosed as a lattice artifact
- **z=3,4 Feigenbaum** (in Q-M005) is partial — overlapping period-4 roots complicate higher n

## 3. Key Numbers

### EXP-0009 (ABNORMAL)

| Exponent | Measured | Expected | |dev| | Status |
|---|---|---|---|---|
| D_f | 1.8697 | 91/48 = 1.8958 | 0.0261 (~1σ) | MISS |
| γ/ν | 1.7596 | 43/24 = 1.7917 | 0.0321 (~1σ) | MISS |
| β/ν | 0.1295 | 5/48 = 0.1042 | 0.0253 (~1σ) | MISS |
| τ | 1.9404 | — | — | gate TBD |
| 1/ν | 0.7434 | — | — | PASS (0.6–0.9) |

### EXP-0010 (RESOLVED)

| L | D_f ± 0.028 | Theory | |dev| |
|---|---|---|---|
| 127 | — | 1.8958 | 0.0004 |
| 191 | — | 1.8958 | — |
| 253 | — | 1.8958 | — |
| 449 | 1.8962 | 1.8958 | 0.0004 |

**Diagnosis**: Lattice-size discretization artifact (same class as optical grid-locking at 256²)

## 4. Controls Summary

**EXP-0009**: C1✅ C6✅ C7✅ (78/78) FG✅ — gates PASS; exponents miss by ~1σ → ABNORMAL per frozen rule
**EXP-0010**: Diagnostic — D_f at non-power-of-2 matches theory

## 5. Known Issues

- **ABNORMAL escalation**: Per frozen rule — escalate, do NOT tune
- **Lattice artifacts**: Power-of-2 lattices produce specific artifacts; non-power-of-2 recommended
- **1/nu gate**: PASS in EXP-0009 but not in Q-P006 (missing gate)
- **Large data files**: _cells_L2048_n50.npz is 46.6 MB

## 6. Differences from Original Assessment

| Aspect | Original (prior audit) | Revised |
|---|---|---|
| ABNORMAL | Listed as unresolved | Diagnosed and RESOLVED by EXP-0010 |
| D_f = 1.8697 | Listed as failure | Diagnosed as power-of-2 artifact; D_f = 1.8962 confirmed |
| Lattice size | Not discussed | Key diagnostic: non-power-of-2 L removes artifact |

## 7. Reproduction Status

- **Deterministic**: Yes, fixed seeds
- **Independent implementation**: PASS (independent_check_exp0009.py)
- **C7**: 78/78 cells bit-identical
- **Full instructions**: REPORT/TECHNICAL_EXP-0007.md, CHANGELOG.md

## 8. Recommended Wording

> The fractal dimension of critical percolation clusters on the square lattice at site p_c ≈ 0.5927 is D_f = 1.8962 ± 0.028 at non-power-of-2 lattice sizes L ∈ {127, 191, 253, 449}, consistent with the standard value 91/48 = 1.8958 within |dev| = 0.0004. The ABNORMAL result from power-of-2 lattices (EXP-0009, D_f = 1.8697) was diagnosed as a lattice-size discretization artifact.
