# EXP-0008 Statistical Dependence and Calibration Audit

## 1. Dependence is part of the scientific model

Consecutive gaps share a prime endpoint. Even nonadjacent gaps are linked by the sieve and by congruence constraints. Therefore observations in a block are not i.i.d. draws from a continuous distribution. The project’s `QUESTION.md` acknowledges correlation, but the primary implementation does not use a dependence-aware goodness-of-fit null.

The following statements are distinct:

- the sample is deterministic given the primes;
- the gaps have serial and arithmetic dependence;
- the conventional chi-square, KS, and binomial p-values assume an i.i.d. sampling model;
- BH-FDR controls multiplicity only after p-values are calibrated.

BH cannot repair a misspecified dependence structure.

## 2. Observed serial dependence

Independent reconstruction gives these lag correlations of normalized gaps:

| Block | lag 1 | lag 2 | lag 3 | lag 5 | lag 10 |
|---|---:|---:|---:|---:|---:|
| B1 | -0.08949 | -0.04260 | -0.01345 | -0.03334 | -0.02555 |
| B2 | -0.05245 | -0.02251 | -0.01549 | -0.01337 | -0.00637 |
| B3 | -0.04538 | -0.02110 | -0.01642 | -0.00836 | -0.00661 |
| B4 | -0.03632 | -0.01793 | -0.01232 | -0.00703 | -0.00361 |

The correlations are modest in magnitude but not zero, and the sample sizes make them statistically detectable. The alternating prime residues and shared endpoints also create dependence not summarized by a single lag coefficient.

## 3. Dependence-aware mean sensitivity

Contiguous non-overlapping clusters of 100 prime gaps were used as an independent sensitivity analysis for the mean. The resulting approximate 95% intervals were:

| Block | cluster 95% interval for mean | Contains 1? |
|---|---|---|
| B1 | `[0.99283, 1.01203]` | Yes |
| B2 | `[0.99696, 1.00569]` | Yes |
| B3 | `[0.99867, 1.00205]` | Yes |
| B4 | `[0.99947, 1.00069]` | Yes |

Moving-block bootstrap checks at lengths 10, 100, and 1,000 gave the same qualitative conclusion. G2 is therefore robust as a mean statement. This does not validate the full exponential distribution.

For the tail indicators, contiguous 100-gap clusters produce discrepancies of the same direction but often larger magnitude than the i.i.d. binomial standard errors. The tail mismatch is not safely calibrated by the stored binomial tests.

## 4. Demonstration that marginal `Exp(1)` does not calibrate KS/chi-square

A controlled calibration simulation generated Gaussian AR(1) variables and applied the inverse normal CDF to give every observation an exactly `Exp(1)` marginal distribution, while retaining serial dependence. It then applied the same 10-bin chi-square and KS tests used by EXP-0008. There were 100 replicates per cell.

| Serial correlation | `n` | Chi-square rejection rate | KS rejection rate |
|---:|---:|---:|---:|
| 0.0 | 1,000 | 0% | 2% |
| 0.0 | 10,000 | 0% | 1% |
| 0.0 | 100,000 | 1% | 2% |
| 0.5 | 1,000 | 7% | 13% |
| 0.5 | 10,000 | 10% | 16% |
| 0.5 | 100,000 | 6% | 10% |
| 0.8 | 1,000 | 45% | 46% |
| 0.8 | 10,000 | 34% | 38% |
| 0.8 | 100,000 | 38% | 44% |

This is not a model of primes; it is a calibration proof that “each marginal is `Exp(1)`” is insufficient for the i.i.d. p-values. Prime-gap dependence is more structured, so the simulation does not supply a correction factor. It shows that C1’s i.i.d. random control cannot certify the scientific null.

## 5. Bootstrap audit

The primary `bootstrap_means` function samples individual gap indices with replacement. It preserves neither adjacent-gap relationships nor congruence patterns. A moving-block bootstrap is more appropriate for a contiguous prime sequence, but it still only quantifies uncertainty under an assumed resampling model; it cannot turn a wrong deterministic prime model into a correct null.

The G2 interval answers a narrow question: “is the mean near 1 under plausible resampling?” It does not answer “is the distribution exponential?”

## 6. BH-FDR and tail tests

The local BH implementation was corrected after the first run, and the pre-fix/final artifacts preserve the changed rejection vectors. The corrected step-up procedure is appropriate for a valid family of p-values, but the stored p-values are not valid family members for the full prime model because of dependence and support misspecification.

The tail routine also computes a two-sided normal p-value as `1 - norm.cdf(abs(z))` in the affected code path. This loses precision by cancellation and produces stored zeros for large `|z|`. The decision direction is unchanged, but reports should store `norm.sf(abs(z))` or log-p values. The nominal p-values should not be quoted as probabilities of being caused by chance.

## 7. Appropriate inference for a successor

A successor should prespecify one of the following:

1. a stationary block model with contiguous prime-index blocks and a block-length sensitivity ladder;
2. a parametric wheel/Hardy–Littlewood simulation that preserves local candidate-process dependence;
3. a permutation or randomization test whose exchangeability null is explicitly stated;
4. a cluster-level goodness-of-fit simulation in which the cluster, not the individual gap, is the sampling unit.

Report effective sample size, cluster length, discarded tails, and sensitivity to block length. Do not call a result “reproduced across independent seeds” when the seed only changes i.i.d. bootstrap indices.

## 8. Dependence conclusion

The data contain measurable serial dependence and the nominal p-values assume away it. The mean conclusion survives basic cluster checks, but the distributional and tail conclusions are not calibrated against a dependence-aware prime model. This is a central reason the H1 label cannot be promoted to a scientific discovery.
