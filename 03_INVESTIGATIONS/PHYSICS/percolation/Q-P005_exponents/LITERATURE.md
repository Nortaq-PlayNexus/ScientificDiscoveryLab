# LITERATURE — Q-P005 (clusters, exponents, hyperscaling)

Status: consolidated from prior lab records (Q-P004 set) + standard references.
Exact values quoted with their derivation status. No new literature claims.

## Exact / near-exact values in the 2D percolation universality class

| quantity | value (exact or high-precision) | origin |
|---|---|---|
| beta | 5/36 = 0.1388889 | Nienhuis (1982) exact Coulomb-gas |
| gamma | 43/18 = 2.3888889 | Nienhuis (1982) exact |
| nu | 4/3 = 1.3333333 | Nienhuis (1982) exact |
| tau | 187/91 = 2.0549451 | tau = 2 + beta/(beta+gamma) = 1 + d/D_f |
| D_f | 91/48 = 1.8958333 | D_f = d - beta/nu = 2 - 5/48 |
| beta/nu | 5/48 = 0.1041667 | |
| gamma/nu | 43/24 = 1.7916667 | |
| 1/nu | 3/4 = 0.75 | |
| p_c(site square) | 0.59274605079210(2) | Ziff PRL 117, 125703 (2016) |

## Scaling relations used as internal checks

- tau = 1 + d/D_f  (Fisher) with d = 2: 187/91.
- 2*beta/nu + gamma/nu = d = 2.
- D_f = 2 - beta/nu.
- P_inf(L) = E[M_max]/L^2 ~ L^{-beta/nu}  (order parameter in a box).

## Where the lab's Q-P004 calibration landed

- bond thresholds reproduced within |d| < 0.01 (exact 1/2); site within 0.01 of
  Ziff's value (EXP-0007 decision H0_SUPPORTED, all gates green).
- width-route estimate 1/nu = 0.7255-0.7375 (gate [0.6,0.9]) — consistent with
  3/4 at this precision, motivating a dedicated exponent measurement (Q-P005).

## Methodological notes (curve-pinned)

- tau measurement is fragile; two estimators are pre-committed (cumulative-rank
  primary, direct histogram secondary). Fit range stays well below L^{D_f}.
- The open-cluster census must exclude closed-site singletons (ENGINE fix).