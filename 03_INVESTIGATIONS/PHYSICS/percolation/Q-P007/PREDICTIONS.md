# Predictions — Q-P007 (from frozen prereg)

| # | measured | estimator | FSS model | expected | tolerance |
|---|---|---|---|---|---|
| P_c (width) | width-curve crossing at L in {512, 1024, 2048} | probit MLE | linear 1/L extrapolation | p_c = 0.5927460508 (Ziff) | tol_pc = 0.001 (width), |dev| from Ziff documented |

## Phase 2 predictions (at refined p_c)

| # | measured | estimator | expected | tolerance |
|---|---|---|---|---|
| D_f | E[M_max] ~ L^{D_f} | bootstrap slope | 91/48 = 1.8958 | ±0.015 |
| gamma/nu | chi(L) ~ L^{gamma/nu} | bootstrap slope | 43/24 = 1.7917 | ±0.03 |
| beta/nu | P_inf ~ L^{-(2-D_f)} | bootstrap slope | 5/48 = 0.1042 | ±0.015 |
| tau | cumulative rank [32, 4096] | weighted OLS | 187/91 = 2.0549 | ±0.05 |

## Scaling relations (internal consistency, report-only)

| Relation | formula | tolerance |
|---|---|---|
| R1 | tau = 1 + 2/D_f | ±0.12 |
| R2 | 2*beta/nu + gamma/nu = 2 | ±0.05 |
| R3 | D_f = 2 - beta/nu | ±0.015 |

## Notes
- Phase 2 used refined p_c = 0.59272900 from width-curve extrapolation (|dev| from Ziff: 0.000017).
- tau was N/A at L=2048 (0 tail clusters at n=25 — diagnostic limitation near p_c).
- Actual results: D_f=1.8818 (PASS), gamma/nu=1.7653 (PASS), beta/nu=0.1189 (PASS), tau=N/A.
