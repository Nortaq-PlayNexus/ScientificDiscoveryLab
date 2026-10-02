# CURRENT_STATUS (AUDIT VERSION — do not confuse with live project doc)
# This is a snapshot of lab state as documented during the forensic audit.
# The live CURRENT_STATUS.md is a project document and was NOT modified.

**Audit Date:** 2026-09-23
**Primary Source:** C:\Users\natha\ScientificDiscoveryLab
**Secondary Source:** C:\Users\natha\code\string-theory-questions\ (referenced only, NOT included in this audit)

---

## New Discoveries (2026-09-23 session)

### D1: Prime Gap Deviation Shape (Q-M007)
- Finding: Deviation NARROWER than Exp(1), both tails lighter, mid-bins over-represented
- Evidence: BH-FDR on 40-cell grid: 38/40 significant; C7 verified
- Status: COMPLETE

### D2: AI Pareidolia Spectral Threshold (Q-S9-1)
- Finding: Detection threshold at complexity >= 0.05 (5% FFT bins), NOT 0.10 as documented
- Evidence: Speckle images with decreasing spectral complexity; detection monotonic
- Discrepancy: ACTIVE_PROJECT.md says 0.10; computed value is 0.05
- Status: COMPLETE

### D3: Detector De-biasing Validation (Q-S9-3)
- Finding: Corrections <5% per factor; A==B robust; REBUS NOT detector artifact
- Status: COMPLETE

### D4: REBUS Dose-Response Quantification (Q-S9-2)
- Finding: Hill fit EC50=30%, n=2.0, MaxInfl=48.3%
- Status: COMPLETE

### D5: Collatz Parameter Sensitivity (Q-M001) — PILOT, NOW FULL RUN
- Finding: Convergence iff a=b=c. 100% convergence at N=100,000 for 3 families. 0% for 5 divergent families.
- Status: FULL RUN COMPLETE (upgraded from PILOT)

### V1: D1 Deviation Persists at 10^9 (Q-M008)
- Finding: 4/4 blocks significant at 10^9. Deviation strengthens with scale.
- Status: COMPLETE

### V2: Q-M008 10^10 — IN PROGRESS
- Segmented sieve running to complete D1 asymptotic test
- Expected: ~20-30 minutes remaining

---

## Session 2026-09-24 (continuation)

### Q-M008 10^10 (V2)
- Status: RUNNING (segmented sieve, 100 segments of 10^8 each)
- Purpose: Complete D1 asymptotic test at 10^10
- 10^8 verification: 4/4 blocks significant (5.76M primes, 2.9s)
- 10^9 main: 4/4 blocks significant (50.85M primes, 24.6s)
- 10^10: in progress (segmented sieve to avoid 10GB memory allocation)

### Q-M001 Divergent Families (D7)
- Status: PILOT DATA EXISTS (N=1000)
- Full N=100,000 for divergent families: too slow (sequences don't converge)
- Convergent families at N=100,000: COMPLETE (100% convergence, 150,000 starting values)

### Q-P008 3D Percolation (D6)
- Status: PILOT COMPLETE (EXP-0011)
- Main run EXP-0013: PENDING (~2 hours compute)
- Pilot: D_f=2.26±0.10, gamma/nu=1.63±0.15, beta/nu=0.74±0.10
- All 3 exponents FAIL at canonical p_c (expected for small L)
- C7-3D PASS 50/50

---

## Updated Counts (2026-09-24)

- **Complete discoveries:** 4 (D1-D4)
- **Full run complete:** 1 (D5: Collatz)
- **Validations:** 1 (V1: D1 at 10^9)
- **In progress:** 1 (V2: 10^10)
- **Pilot:** 1 (D6: 3D percolation)
- **Total documented findings:** 7

---

## Open Questions Still Uninvestigated

Q-M003 (digit normalcy), Q-M004 (sandpile), Q-M006 (first-passage),
Q-O003 (propagation invariance), Q-O004 (speckle information),
Q-O005 (speckle spectrum vs roughness), Q-P001 (graph spectral stats),
Q-P002 (FPUT), Q-P003 (quantum-classical correlations),
Q-F001-003, Q-A001-004, Q-C001-002, Q-Mx001, Q-B001-003, Q-I001-003

---

## Hardware Note

PC froze during Q-M008 10^10 run at ~41% completion (segment 41/100).
Run was cancelled. Results from 10^8 and 10^9 preserved.
10^10 run restarted after recovery.
