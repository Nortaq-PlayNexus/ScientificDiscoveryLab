# PREDICTIONS — Speckle contrast law

## Quantitative predictions (pre-registered)

1. For each (M, N) in the grid below, the ratio r(M,N) = C_hat(M,N) * sqrt(M) has a
   bootstrap 99% CI containing 1.0.

2. If deviations exist, they shrink with N: width of the deviation band approx
   proportional to 1/N (grid-sampling hypothesis).

3. Estimator sanity: for M = 1, C_hat ~ 1.0 within estimator error (known, must
   reproduce; this is our positive control).

## Test grid (pre-registered)

- Grid sizes N: 32, 64, 128, 256
- Summed speckle count M: 1, 2, 4, 8, 16
- Independent realisations per (M, N): 32
- Seeds: lab SEED_LADDER (primary 42)
- alpha = 0.01; BH-FDR over the full 20-cell grid

## Number outputs to record

- C_hat, its bootstrap CI, r = C*sqrt(M), deviation vs N trend slope estimate.