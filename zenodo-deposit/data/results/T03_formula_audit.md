# T03_runs estimator audit

- prereg: `T03-FORMULA-AUDIT` (`8ffc034dffdf4836`)
- shared battery sha256: `5f53f3eacdf38e8c` (unmodified since N-004: True)
- **verdict: ESTIMATOR_DEFECTIVE**
- defect: an extra sqrt(2) is applied to an argument the standard defines directly in erfc units, inflating p-values

## Stored N-004 T03_runs cells

| Generator | Bits | n | KS p | rejects@0.01 | mean p |
|---|---|---|---|---|---|
| G_LAB | 2^18 | 200 | 0.00168 | 0 | 0.5760 |
| G_LAB | 2^22 | 60 | 0.14 | 0 | 0.5556 |
| MT19937 | 2^18 | 200 | 0.000159 | 0 | 0.5970 |
| MT19937 | 2^22 | 60 | 0.137 | 0 | 0.5681 |
| PCG64_direct | 2^18 | 200 | 2.2e-06 | 0 | 0.6010 |
| PCG64_direct | 2^22 | 60 | 0.000312 | 0 | 0.6465 |
| WEAK_LCG_BROKEN | 2^18 | 200 | 3.09e-08 | 0 | 0.6265 |
| WEAK_LCG_BROKEN | 2^22 | 60 | 7.21e-05 | 0 | 0.6263 |

## Fresh-seed paired calibration (same streams, two implementations)

| Bits | Impl | KS p | rejects@0.01 | mean p | median p |
|---|---|---|---|---|---|
| 2^18 | shared t_runs | 6.73e-06 | 0/200 | 0.6026 | 0.6038 |
| 2^18 | SP 800-22 ref | 0.847 | 1/200 | 0.4928 | 0.4630 |
| 2^22 | shared t_runs | 9.14e-11 | 0/200 | 0.6317 | 0.6420 |
| 2^22 | SP 800-22 ref | 0.106 | 1/200 | 0.5259 | 0.5109 |

## SP 800-22 applicability

- condition: `abs(pi - 0.5) >= 2 / sqrt(n - 1)`
- applicable seeds at 2^18: **0/200**
- threshold tau = 0.003906

## Claim boundary

- that any generator is certified or random
- that the withdrawn EXP-0004 certificate is reinstated
- that G_LAB was shown to be defective; the opposite is true, the instrument was defective
