# REVISED DOSSIER: Q-M005 — Feigenbaum Universality

**Revised by:** Forensic Audit, 2026-09-23
**Original:** 03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/
**Changes:** Documented separately from original; original preserved

---

## 1. What This Investigation IS

A computation of Feigenbaum constants δ and α for higher-order 1D maps f_a(x) = 1 − a|x|^z, testing universality for extremum orders z ∈ {2, 3, 4}.

## 2. What This Investigation DOES NOT Prove

- **z=3,4 results are PARTIAL**: Overlapping period-4 roots complicate higher n; refined bracketing needed
- **Signed alpha_infty not computed**: Only |alpha| computed via spatial scaling; signed alpha requires RG fixed-point iteration
- **Does NOT prove** new universality classes — standard Feigenbaum universality confirmed for z=2

## 3. Key Numbers (z=2, VALIDATED)

| n | a_n | delta_n | Published δ_n | |dev| | Status |
|---|---|---|---|---|---|
| 3 | 1.3815... | 4.38568 | 4.7514 | 0.366 | early |
| 4 | 1.3969... | 4.60095 | 4.6562 | 0.055 | converging |
| 5 | 1.4003... | 4.65513 | 4.6687 | 0.014 | converging |
| 6 | 1.4010... | 4.66611 | 4.6692 | 0.003 | close |
| 7 | 1.4011... | 4.66855 | 4.6692 | 0.0007 | close |
| 8 | 1.4011... | 4.66906 | 4.6692 | 0.0001 | PASS |

δ_8 = 4.66906 vs published 4.6692016091029, dev = 1.4 × 10⁻⁴

## 4. Controls (z=2): 7/7 PASS

C1✅ (reproduction, dev 1.4e-4), C2✅ (monotonicity), C3✅ (5 seeds identical), C4✅ (Brentq vs Newton, diff<1e-6), C5✅ (resolution), C6✅ (xtol sensitivity), C7✅ (manual vs engine, diff<1e-10)

## 5. Known Issues

- **z=3,4 partial**: Higher n requires refined bracketing; overlapping period-4 roots
- **Alpha sign**: Only |alpha| computed; signed alpha_infty = -2.5029078750957 not computed
- **No RNG**: Deterministic root-finding; no random seeds

## 6. Differences from Original Assessment

| Aspect | Original (prior audit) | Revised |
|---|---|---|
| z=2 PASS | Listed | Confirmed 7/7 controls, dev 1.4e-4 |
| z=3,4 partial | Listed | More detail: overlapping period-4 roots |
| Alpha | Not discussed | Explicitly noted as unsigned only |

## 7. Reproduction Status

- **Deterministic**: Yes (Brent's method, no RNG)
- **Code available**: CODE/feigenbaum_engine.py + CODE/run_feigenbaum.py
- **C7**: Manual delta_4 vs engine diff < 1e-10
- **Full instructions**: REPORT/TECHNICAL_EXP-0014.md

## 8. Recommended Wording

> For the 1D map family f_a(x) = 1 − a|x|^z with extremum order z = 2, the Feigenbaum constant δ = 4.6692016091029 is approached by superstable-cycle delta_n values at n = 8 with deviation 1.4 × 10⁻⁴. Convergence is monotonic, confirmed by 7/7 controls including method variation (Brentq vs Newton, diff < 1e-6) and precision sensitivity (xtol). Results for z = 3, 4 are partial due to overlapping period-4 roots requiring refined bracketing. Only |alpha| is computed; signed alpha_infty requires RG fixed-point iteration.
