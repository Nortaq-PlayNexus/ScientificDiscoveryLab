# REVISED DOSSIER: Q-O001 — Speckle Contrast Law

**Revised by:** Forensic Audit, 2026-09-23
**Original:** 03_INVESTIGATIONS/OPTICS/speckle_contrast_law/
**Changes:** Documented separately from original; original preserved

---

## 1. What This Investigation IS

A computational reproduction of Goodman's speckle contrast law C(M) = 1/sqrt(M) for summed speckle intensities, using a deterministic simulation pipeline with full controls and independent replication.

## 2. What This Investigation DOES NOT Prove

- **Nothing about real optical systems** beyond the idealised model
- **Nothing novel**: the law is textbook (Goodman)
- **It does not certify** that future optics claims are correct; only that the statistical + simulation pipeline behaves as specified for this case

## 3. Key Numbers (Reproduced)

| Metric | Value | Gate |
|---|---|---|
| r = C·sqrt(M), all 20 cells | [0.984, 1.005] | PASS |
| r at N=256 | [0.9968, 1.0003] | PASS |
| N=64 M=2 (FDR flagged) | r = 0.9840 | FAIL (but resolution-dependent) |
| KS test of intensity marginal | p = 0.27 | PASS |
| Independent implementation | r = 1.0000 ± 0.0012 | PASS |
| Seed ladder range | 0.0095 | PASS |

## 4. Controls Summary

C1✅ C2✅ C3✅ C4✅ C5✅ C6✅ C7✅ C8✅ — 8/8 controls PASS (with documented N=64 M=2 FDR flag)

## 5. Known Issues

- **BH-FDR engine bug**: Found and fixed during EXP-0001; EXP-0002 re-run. First run's FDR flags superseded; both rows in registry.
- **Low-N deviations**: N=32, N=64 show slight deficit — consistent with finite-grid sampling, shrinks with N
- **Single aperture fraction**: Only 1/8 tested; other fractions not verified
- **Single estimator family**: Only intensity-based contrast measured

## 6. Differences from Original Report

| Aspect | Original | Revised |
|---|---|---|
| BH-FDR bug | Not mentioned in original context | Explicitly documented; first run superseded |
| N=64 M=2 failure | Listed as gate failure | Contextualised as resolution-dependent; not a failure of the law |
| Scope | Implied generality | Explicitly limited to N ≥ 128 for reliable results |

## 7. Reproduction Status

- **Deterministic**: Yes, seed 42
- **Independent implementation**: PASS (independent_check.py)
- **Figure reproducible**: Yes (make_figure.py)
- **Full instructions**: REPORT/TECHNICAL_SUMMARY.md

## 8. Recommended Wording

> For simulated fully-developed speckle from a random-phase disk pupil, the summed-speckle contrast satisfies C(M) = 1/sqrt(M) within Monte Carlo error for M = 1–16 at grid resolution N ≥ 128, with r = C·sqrt(M) ∈ [0.9968, 1.0003] at N=256 (99% bootstrap CIs contain 1.0), confirmed by an independent implementation (r = 1.0000 ± 0.0012).
