# Predictions — Q-P008 / EXP-0011 (pilot) and EXP-0013 (main run)

| # | measured | estimator | expected | tolerance |
|---|---|---|---|---|
| p_c (width) | width-curve crossing at L in {8,16,24} or {128,256,512} | probit MLE | 0.3116079 | ±0.001 (width), |dev| from lit documented |
| D_f | E[M_max] ~ L^{D_f} | bootstrap slope | 2.53 (Hsu 1990) | ±0.10 (pilot) / ±0.05 (main) |
| gamma/nu | chi(L) ~ L^{gamma/nu} | bootstrap slope | 1.40 | ±0.08 (pilot) / ±0.05 (main) |
| beta/nu | P_inf ~ L^{-(2-D_f)} | bootstrap slope | 0.41 | ±0.05 (pilot) / ±0.03 (main) |
| tau | cumulative rank [4, 1000] | weighted OLS | 2.19 (Fisher) | ±0.10 (pilot) / ±0.10 (main) |

## Scaling relations (report-only)

| Relation | formula | tolerance |
|---|---|---|
| R1 | tau = 1 + 2/D_f | report-only |
| R2 | 2*beta/nu + gamma/nu = 2 | report-only |
| R3 | D_f = 2 - beta/nu | report-only |

## Notes
- EXP-0011 (pilot, L=8/16/24) is a system test of 3D machinery.
- EXP-0013 (main, L=128/256/512) is the primary run. Results awaited.
- tau diagnostic at L=24 pilot had 0 tail clusters — sample size limitation.
