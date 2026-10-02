# Isolated audit repair — Q-M007/Q-M008 N-06/N-07/N-08

**Status: descriptive audit smoke only. No novelty or discovery claim.**

This run is isolated from the historical Q-M007/Q-M008 files. Historical configs and results were hash-checked and not modified. The planned 10^10 production sieve was not run.

## Numerical repairs

- Normalization is `(p_{i+1}-p_i)/ln(p_i)` with lower-prime block assignment `lo <= p_i < hi`; the successor is retained when it crosses the upper boundary.
- BH is the step-up procedure, with later qualifying ranks propagated backward.
- Chi-square and normal tails use log-survival calculations. A p-value below the representable float range is JSON `null` with its `log10_p_value`, never an artificial `0.0`.
- The parity-geometric diagnostic has support `delta=2K/ln(p)`, `K` geometric with `q=2/ln(p)`. It retains the exact even-gap lattice and exposes the structurally empty first bin.

## Segmented sieve control

- Sieve limit: `100,000,100`; segment size: `100,000,000`; segments are inclusive and non-overlapping.
- First segment `[0, 100,000,000)` retained `5,761,455` primes, including `2` and ending at `99,999,989`.
- The first-segment vector SHA-256 is `a7eead5377c738f5ecdd62fd01a0cedbcecee527cbf31739d4ecc1f3fae07766`; trusted small-limit comparisons and boundary checks are recorded in the raw summary.

## Matched 10^8-scale smoke

The four blocks match the historical EXP-0008 lower-prime decade ranges, but use corrected lower-prime normalization and boundary inclusion. These numbers are a numerical/descriptive smoke, not a scale replication or a Gallagher test.

| Block | n gaps | mean delta | SD | first-bin observed | first-bin parity expected | continuous chi2 (log10 p) | parity chi2 (log10 p) |
|---|---:|---:|---:|---:|---:|---:|---:|
| B1 | 8,363 | 1.002433090 | 0.763117637 | 0 | 0 | 2358.250 (1e-502.401) | 787.856 (1e-164.069) |
| B2 | 68,906 | 1.001332921 | 0.803716675 | 0 | 0 | 12517.823 (1e-2705.99) | 5248.624 (1e-1130.24) |
| B3 | 586,081 | 1.000359929 | 0.832888396 | 0 | 0 | 105347.656 (1e-22860.5) | 27734.302 (1e-6010.78) |
| B4 | 5,096,876 | 1.000081282 | 0.850529437 | 0 | 0 | 851697.027 (1e-184925) | 170712.896 (1e-37055.8) |

## Corrected BH screens

- Continuous Exp(1) operational family: largest qualifying rank `4/4`; this null is structurally misspecified.
- Parity-geometric diagnostic family: largest qualifying rank `4/4`; this is not a complete prime null.
- Q-M007 numerical 40-cell screen: corrected one-df survival arithmetic and step-up BH were recomputed for `40` nested cells, but the screen is exploratory and not confirmatory.

## Unresolved issues and limits

- The parity/geometric surrogate does not include wheel, singular-series, or consecutive-pair corrections.
- Prime gaps are serially/arithmetic dependent; Pearson chi-square p-values are not dependence-calibrated scientific p-values.
- The fixed-bin screen is exploratory and the bin edges themselves are scale-sensitive.
- No 10^9/10^10 scientific replication was run here; the planned 10^10 run was not executed.
- No novelty or mechanism claim follows from this audit repair.

The historical Q-M007 and Q-M008 outputs remain evidence artifacts only. No statement here upgrades their earlier persistence or 38/40 wording.
