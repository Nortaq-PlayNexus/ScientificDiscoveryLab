# EXP-0008 Effect-Size Analysis

## 1. Why nominal chi-square is not an effect size

Pearson `chi2` grows with sample size when a fixed distributional discrepancy is present. Dividing by degrees of freedom still grows with `n`; it is not a scale-free discrepancy measure. EXP-0008’s `chi2_red` values 262, 1,391, 11,705, and 94,633 therefore cannot be read as evidence that a physical discrepancy strengthens with scale. The KS distance and histogram distances are more informative descriptive scales.

## 2. Descriptive effect sizes

The following values were independently recomputed from the canonical internal-block convention. TV is the total-variation distance between the ten-bin empirical distribution and the `Exp(1)` bin probabilities. W1 is an empirical-quantile-grid estimate of one-dimensional Wasserstein distance. Variance ratio is empirical variance divided by the `Exp(1)` variance, 1.

| Block | Mean shift `(mean-1)` | SD | Variance ratio | KS D | Histogram TV | W1 | Skew | Excess kurtosis |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 | 0.002428 | 0.763163 | 0.5823 | 0.171668 | 0.2131 | 0.1630 | 1.624 | 3.754 |
| B2 | 0.001326 | 0.803721 | 0.6460 | 0.150944 | 0.1539 | 0.1343 | 1.740 | 4.513 |
| B3 | 0.000359 | 0.832889 | 0.6937 | 0.137995 | 0.1504 | 0.1144 | 1.785 | 4.712 |
| B4 | 0.000081 | 0.850530 | 0.7234 | 0.128300 | 0.1450 | 0.1024 | 1.808 | 4.829 |

The mean shift is negligible relative to the standard deviation. The shape discrepancy is not negligible. The increasing skewness and kurtosis, together with variance below one, show that mean agreement is being used as if it were distribution agreement.

## 3. Quantiles

| Block | Empirical q01 | Exp q01 | Empirical median | Exp median | Empirical q99 | Exp q99 |
|---|---:|---:|---:|---:|---:|---:|
| B1 | 0.1749 | 0.0101 | 0.7756 | 0.6931 | 3.5776 | 4.6052 |
| B2 | 0.1459 | 0.0101 | 0.7809 | 0.6931 | 3.7782 | 4.6052 |
| B3 | 0.1250 | 0.0101 | 0.7650 | 0.6931 | 3.9105 | 4.6052 |
| B4 | 0.1094 | 0.0101 | 0.7294 | 0.6931 | 3.9725 | 4.6052 |

The lower tail is shifted upward by the even-gap constraint. The median is above the exponential median while the far upper quantile is below the continuous exponential quantile. This mixed shape is not adequately summarized by “the distribution is narrower” or “the deviation survives.”

## 4. First-bin contribution

| Block | First-bin share of block chi-square |
|---|---:|
| B1 | 35.5% |
| B2 | 55.0% |
| B3 | 55.6% |
| B4 | 59.8% |
| **combined** | **59.28%** |

The first bin is a structural zero. The remaining TV after removing it is approximately 0.1812, 0.1155, 0.1116, and 0.1056 for B1–B4 (renormalized to the remaining support). Thus the support issue is dominant but not the entire observed discrepancy.

## 5. Scale behavior

From B1 to B4:

- mean remains near 1;
- SD rises from 0.763 to 0.851;
- variance ratio rises from 0.582 to 0.723;
- KS D falls from 0.172 to 0.128;
- W1 falls from 0.163 to 0.102;
- the first bin remains empty below the support threshold.

This is partial movement toward the continuous exponential shape, not “the effect strengthens with scale.” Q-M008’s report’s use of growing chi-square as a strengthening effect is therefore misleading. The differing denominator and block definitions in Q-M008 make its cross-scale comparison unsuitable without correction.

## 6. Model-relative effect sizes

The effect size depends completely on the null:

- Against N0 (`Exp(1)`), TV is 0.145–0.213 and W1 is 0.102–0.163.
- Against a parity-conditioned discrete surrogate, the first-bin contribution disappears and the exploratory chi-square falls substantially.
- Against a singular-series-weighted pair surrogate, residuals remain but the comparison is not yet a calibrated test.
- Against a future scale/wheel/HL null, the residual effect size is unknown because that null has not been preregistered or fully implemented.

Therefore the only defensible effect-size statement is: **the empirical distribution differs materially from an unconditioned continuous exponential at the selected finite scales, with a large deterministic support component.**

## 7. Interpretation guardrails

1. Do not convert a large chi-square/dof into a physical effect size.
2. Do not use mean CIs as evidence of exponential shape.
3. Do not interpret a lower variance as a new law; it may reflect the even-integer lattice, residue structure, or finite scale.
4. Do not compare effect sizes across Q-M008 scales until denominator, blocks, null, and support are matched.
5. Report effect sizes with the model used and with a dependence-aware uncertainty interval.

**Bottom line:** the effect is real as a distributional comparison, but its scientific interpretation remains model-relative and currently dominated by arithmetic structure.
