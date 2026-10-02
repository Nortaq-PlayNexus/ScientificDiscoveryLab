# REVISED DOSSIER: Q-P004 — Percolation Thresholds

**Revised by:** Forensic Audit, 2026-09-23
**Original:** 03_INVESTIGATIONS/PHYSICS/percolation/
**Changes:** Documented separately from original; original preserved

---

## 1. What This Investigation IS

A computational reproduction of bond and site percolation thresholds on the square lattice, measured with the lab's controlled pipeline (spanning + torus-wrap estimators, fixed-exponent FSS), matching published anchors within tolerance.

## 2. What This Investigation DOES NOT Prove

- **Does NOT prove** a new percolation threshold — the standard value is exactly 0.5 (bond) and ≈0.5927 (site)
- **Does NOT prove** a new estimation method — standard estimators used
- **FG chi2_red = 4.738 failure** (EXP-0005/0006) was NOT a physics failure — it was an estimator artifact at small L

## 3. Key Numbers (Reproduced)

| Estimator | Value | |d| from published | Gate |
|---|---|---|---|
| bond_span (wrap) p50 | 0.50021 | 0.00021 | in_tol PASS (<0.01) |
| bond_wrap p50 | 0.500687 ± 0.0317 | 0.000687 | in_tol PASS |
| site_span p50 | 0.59284 | — | documented |
| C7: 78/78 cells | bit-identical | — | PASS |
| FG chi2_red (EXP-0007) | 2.239 | — | PASS (<4) |

## 4. Critical History (3 experiments)

| Experiment | Status | Key Finding |
|---|---|---|
| EXP-0005 | INCONCLUSIVE | FG bond_wrap chi2_red=4.738 FAIL; C8 1/nu=1.2384 FAIL |
| EXP-0006 | INCONCLUSIVE | Fine-grid; C8 1/nu=0.7375 PASS; FG failure persists |
| EXP-0007 | complete | bond_wrap chi2_red→2.239 PASS; 78/78 C7; 1/nu=0.7255 PASS |

## 5. Diagnosis of FG Failure

The FG chi2_red failure at EXP-0005/0006 was caused by:
1. **Small-L kink**: L48→L64 delta = 0.00288 (sub-0.5% wiggle inside joint SE)
2. **Small-L-only fit**: 3 sizes dominated by one kink
3. **Fixed-exponent FSS**: Requires ≥4 sizes; EXP-0007 extended to 6 sizes

EXP-0007 resolution: chi2_red dropped 4.738 → 2.239 with 6 fitting points.

## 6. Controls Summary (EXP-0007)

C1✅ (determinism k=304, n=600), C4✅ (scale stability), C6✅ (seed ladder), C7✅ (78/78), C8✅ (width 0.7255 in [0.6,0.9]), FG✅ (2.239<4), in_tol✅ (0.000687<0.01)

## 7. Known Issues

- **EXP-0005/0006 INCONCLUSIVE**: Mixed gate results; not a failure but not a clean pass
- **FG bond_wrap chi2_red**: Was 4.738 (FAIL), now 2.239 (PASS) with extended data
- **C8 width-route**: Had 1/nu=1.2384 FAIL in EXP-0005; now 0.7255 PASS in EXP-0007
- **1/nu diagnostic**: PASS in [0.6, 0.9] but bootstrap CI wide [0.6722, 1.0674]

## 8. Differences from Original Assessment

| Aspect | Original (prior audit) | Revised |
|---|---|---|
| FG failure | Listed as unresolved | Resolved by EXP-0007 extension |
| C8 failure | Listed as unresolved | Resolved; width-route validated |
| Experiment count | 2 (EXP-0005/0006) | 3 (+EXP-0007 resolves issues) |
| Status | INCONCLUSIVE | Complete (H0_SUPPORTED) per EXP-0007 |

## 9. Reproduction Status

- **Deterministic**: Yes, fixed seeds
- **Independent implementation**: PASS (C7: 78/78 bit-identical)
- **Multiple estimators**: bond_span, bond_wrap, site_span, width
- **Full instructions**: REPORT/TECHNICAL_EXP-0007.md

## 10. Recommended Wording

> Bond percolation threshold on the square lattice, measured via torus-wrap estimator with the lab's controlled pipeline at fixed-exponent finite-size scaling, is p_c = 0.500687 ± 0.0317, differing from the published value 0.5 by |d| = 0.000687 (within the 0.01 tolerance gate). The preliminary chi2_red failure (4.738 at small L) was resolved by extending to 6 lattice sizes (EXP-0007), yielding chi2_red = 2.239. C7 independent implementation reproduced 78/78 cells bit-identically.
