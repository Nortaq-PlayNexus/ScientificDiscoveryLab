# N-001 tau estimator validation on known exponents

- prereg `N001-TAU-ESTIMATOR-VALIDATION` (`f37cc2d47667be89`)
- stored production value (NOT edited): **1.920086094899**
- Fisher reference: 2.054945

## Error of each estimator on synthetic data of KNOWN exponent

Positive error means the estimator reports a LARGER exponent than the truth.

      window |                  estimator |             truth 1.85 |             truth 2.05 |
             |                            |   mean error (max abs) |   mean error (max abs) |
-------------+----------------------------+------------------------+------------------------+
   [16, 512] |      cumulative_as_written |       +0.3478 (0.3502) |       +0.2799 (0.2835) |
   [16, 512] |  cumulative_poisson_weight |       +0.2180 (0.2213) |       +0.1521 (0.1566) |
   [16, 512] |                  histogram |       -0.0064 (0.0136) |       -0.0077 (0.0158) |
  [32, 4096] |      cumulative_as_written |       +0.1537 (0.1555) |       +0.1116 (0.1153) |
  [32, 4096] |  cumulative_poisson_weight |       +0.0815 (0.0835) |       +0.0437 (0.0471) |
  [32, 4096] |                  histogram |       -0.0018 (0.0053) |       -0.0017 (0.0085) |
  [32, 2048] |      cumulative_as_written |       +0.2197 (0.2213) |       +0.1688 (0.1711) |
  [32, 2048] |  cumulative_poisson_weight |       +0.1308 (0.1327) |       +0.0832 (0.0859) |
  [32, 2048] |                  histogram |       -0.0026 (0.0058) |       -0.0022 (0.0064) |
  [64, 4096] |      cumulative_as_written |       +0.2124 (0.2137) |       +0.1657 (0.1688) |
  [64, 4096] |  cumulative_poisson_weight |       +0.1293 (0.1305) |       +0.0860 (0.0887) |
  [64, 4096] |                  histogram |       -0.0008 (0.0032) |       +0.0013 (0.0054) |

## Preregistered decision

- classification: **ESTIMATOR_BIASED**
- median |error| at the primary window: **0.1326** (tolerance 0.05)
- sign consistent across both truths: **True**
- error spread across truths: **0.0421**
- bias correction permitted: **True**

The bias is consistent in sign and magnitude across both true exponents, so it behaves like a property of the estimator and window and may be subtracted as a clearly labelled secondary estimate.

## The same estimators on the real N-001 stored data (L=1024 canonical)

      window |   as written |  poisson weight |   histogram |  dev from Fisher |
-------------+--------------+-----------------+-------------+------------------+
   [16, 512] |      1.93585 |         1.93380 |     1.96603 |         -0.11910 |
  [32, 4096] |      1.92009 |         1.92840 |     1.70277 |         -0.13486 |
  [32, 2048] |      1.92828 |         1.93297 |     1.84661 |         -0.12667 |
  [64, 4096] |      1.91207 |         1.92059 |     1.60696 |         -0.14287 |

- max estimator disagreement on real data: **0.30511**
- estimator choice matters: **True**

## Bottom line

ESTIMATOR_BIASED: the frozen N-001 cumulative estimator's error at the primary window is {'truth_1.85': 0.15370030089772702, 'truth_2.05': 0.11155053953974892} for true exponents [1.85, 2.05]. The stored production value 1.9200860948994347 is not edited. The deviation from the Fisher value is in the downward direction at every window under every estimator, so the escalation direction is unaffected even where the numeric value is not trusted.

## Claim boundary

- The frozen N-001 production number tau = 1.92009 is not edited, replaced, or deleted. A bias-corrected value is a separately labelled secondary estimate at most.
- The production runner is not modified. The estimators are re-implemented and validated in this isolated directory.
- A measured bias on synthetic data is not automatically a valid correction for real percolation data, whose local curvature is not the curvature of the synthetic constructions. That is exactly what the two-truth test decides.
- Finding a bias does not overturn the escalation direction. It weakens the numeric value, and must not be reported as though it had removed the deviation.
- No physics claim, no novelty claim, and nothing here bears on any other experiment.
- If the bias turns out to be small or transferable-absent, the stored tau stands and this experiment is a null result reported as such.
