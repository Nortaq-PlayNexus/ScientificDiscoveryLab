# REVISED DOSSIER: Q-O002 — Vortex Density

**Revised by:** Forensic Audit, 2026-09-23
**Original:** 03_INVESTIGATIONS/OPTICS/vortex_density/
**Changes:** Documented separately from original; original preserved

---

## 1. What This Investigation IS

A computational reproduction of the Kac-Rice/Nye-Berry vortex density formula for isotropic, zero-mean complex Gaussian fields, using two independent detectors and an independent implementation.

## 2. What This Investigation DOES NOT Prove

- **No new physics**: n_pred = Kac-Rice/Nye-Berry is established
- **No claim of novelty**: no literature search was performed programmatically
- **The broadband deficit** is characterised, not explained from first principles
- **Only isotropic spectra** were tested (the derivation requires isotropy)

## 3. Key Numbers (Reproduced)

| k0 (rad/px) | P (px) | n_meas/n_pred | 99% CI |
|---|---|---|---|
| π/32 | 64 | 0.9978 | [0.9931, 1.0026] |
| π/16 | 32 | 0.9952 | [0.9901, 1.0001] |
| π/8 | 16 | 0.9958 | [0.9932, 0.9984] |
| π/4 | 8 | 1.0011 | [1.0000, 1.0024] |
| π/2 (excluded) | 4 | 1.0137 | within ±3% but excluded a priori |

## 4. Near-Nyquist Failure Zone (C8)

| σ_k | Winding D1 | Contour D2 |
|---|---|---|
| 0.10 | 1.0160 | 0.9855 |
| 0.25 | 0.9898 | 0.9543 |
| 0.50 | 0.9130 | 0.8615 |
| 0.75 | 0.8287 | 0.7558 |

**Characterised as detector/grid resolution limit**, not a physics effect.

## 5. Controls Summary

C1✅ C2✅ (D2 fixed from 2.5× overcounting) C3✅ C4✅ (shift ≤2.1%) C5✅ C6✅ (independent: 0.992–0.999) C7✅ C8✅ (documented) C9✅ C10✅ — 10/10 documented

## 6. Known Issues

- **D2 detector bug**: Initial naive contour detector overcounted ~2.5×; replaced by certified intersection detector; naive version retained as documented negative
- **π/2 k0**: Worst-resolved; excluded from primary set a priori
- **FFT-moment predictor bias**: For off-grid plane-wave fields, biased by spectral leakage (~0.89 at k0=π/8); corrected with mode-weighted prediction
- **Charge-neutral**: |n+ − n−|/n ≤ 0.0024 for all cells

## 7. Differences from Original Report

| Aspect | Original | Revised |
|---|---|---|
| D2 overcounting | Mentioned | Emphasised as near-2.5× error; detector certification documented |
| Near-Nyquist zone | Noted | Explicitly characterised as detector limitation, NOT physics |
| FFT-moment bias | Not mentioned | Documented as potential future trap |
| π/2 exclusion | Listed | Explicitly stated as a priori exclusion |

## 8. Reproduction Status

- **Deterministic**: Yes, seed 42
- **Independent implementation**: PASS (independent_check.py)
- **Two independent detectors**: D1 (winding) + D2 (contour intersection)
- **Full instructions**: REPORT/TECHNICAL_SUMMARY.md

## 9. Recommended Wording

> For isotropic zero-mean complex Gaussian fields with narrow-band spectra at wavenumber k0, the measured phase-singularity density n_meas matches the Kac-Rice/Nye-Berry prediction n_pred = <|dE/dx|²>/(2π<|E|²>) within 0.5% for N ≥ 1024 (4 primary cells), confirmed by two independent detectors (plaquette winding and certified zero-contour intersection) and an independent plane-wave implementation. Broadband spectra at σ_k ≥ 0.50 show resolution-dependent deficits (up to 24%) attributed to detector/grid limitations, not physics.
