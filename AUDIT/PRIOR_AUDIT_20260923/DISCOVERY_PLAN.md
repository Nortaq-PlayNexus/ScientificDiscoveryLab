# DISCOVERY PLAN — ScientificDiscoveryLab
**Date:** 2026-09-23

## Completed

### D1: Prime Gap Deviation Shape (Q-M007)
- Status: COMPLETE
- Finding: Deviation narrower than Exp(1), both tails lighter, mid-bins over-represented
- Evidence: BH-FDR 40-cell: 38/40 significant; C7 verified
- Document: 03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/REPORT/TECHNICAL_Q-M007.md

### D2: AI Pareidolia Spectral Threshold (Q-S9-1)
- Status: COMPLETE
- Finding: Detection threshold at complexity >= 0.05 (5% FFT bins), not 0.10
- Evidence: Monotonic detection rate with spectral complexity
- Document: 03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-1.md

### D3: Detector De-biasing Validation (Q-S9-3)
- Status: COMPLETE
- Finding: Corrections <5% per factor; A==B robust; REBUS NOT detector artifact
- Document: 03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-3.md

### D4: REBUS Dose-Response (Q-S9-2)
- Status: COMPLETE
- Finding: Hill fit EC50=30%, n=2.0, MaxInfl=48.3%
- Document: 03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/REPORT/TECHNICAL_Q-S9-2.md

### D5: Collatz Parameter Sensitivity (Q-M001)
- Status: FULL RUN COMPLETE
- Finding: Convergence iff a=b=c; 100% at N=100000 for 3 families; 0% divergence for 5 others
- Document: 03_INVESTIGATIONS/MATHEMATICS/collatz/REPORT/TECHNICAL_Q-M001.md

### V1: D1 Deviation Persists at 10^9 (Q-M008)
- Status: COMPLETE
- Finding: 4/4 blocks significant at 10^9; chi2/dof increases 2.3x from 10^8
- Document: 03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/REPORT/TECHNICAL_Q-M008.md

## In Progress

### V2: Q-M008 10^10 (segmented sieve)
- Status: RUNNING (segmented sieve, ~100 segments of 10^8 each)
- Expected: ~20-30 minutes remaining
- Purpose: Complete D1 asymptotic test at 10^10
- Document: 03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/REPORT/TECHNICAL_Q-M008.md (will update)

## Planned

| Priority | Target | Cost | Purpose |
|---|---|---|---|
| 1 | Q-M008 10^10 (V2) | ~30 min CPU | Complete D1 asymptotic test |
| 2 | Q-P008 main run EXP-0013 | ~2 hours CPU | Resolve 3D percolation ABNORMAL |
| 3 | Q-M001 divergent families | CPU-minutes | Complete 27-family sweep |
| 4 | Q-M004 sandpile exponents | CPU-hours | Standard reproduction |
| 5 | Q-M006 first-passage | CPU-hours | Scaling test |
| 6 | Q-O003 propagation invariance | Existing code | Artifact hunt |

## Not Started (no code exists)
Q-M003 (digit normalcy), Q-M004 (sandpile), Q-M006 (first-passage),
Q-O003 (propagation invariance), Q-O004 (speckle information),
Q-O005 (speckle spectrum vs roughness), Q-P001 (graph spectral stats),
Q-P002 (FPUT), Q-P003 (quantum-classical correlations),
Q-F001-003, Q-A001-004, Q-C001-002, Q-Mx001, Q-B001-003, Q-I001-003
