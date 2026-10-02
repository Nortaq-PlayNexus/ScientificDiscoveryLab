# N-001 finite-size crossover diagnostic

- prereg `N001-CROSSOVER-DIAGNOSTIC` (`de231ef64d0dbf77`)
- stored raw database unmodified: True
- reproduction control: stored tau 1.920086094899 vs this implementation 1.920086094899 (delta 0.00e+00)

## Primary: tau at each size, window s in [32, 4096], canonical arm

| L | realizations | tail clusters | tau | 95% CI | deviation from 187/91 | chi2_red |
|---|---|---|---|---|---|---|
| 256 | 100 | 188821 | **1.90306** | [1.8748, 1.9322] | -0.15189 | 0.041 |
| 512 | 100 | 740653 | **1.88981** | [1.8718, 1.9090] | -0.16513 | 0.016 |
| 1024 | 50 | 1462967 | **1.92009** | [1.9063, 1.9326] | -0.13486 | 0.038 |

Fisher tau = 187/91 = 2.054945

## Trend in log L (pre-registered directional test)

- slope d(tau)/d(ln L) = **+0.01228** (SE 0.01812, 95% CI [-0.02324, +0.04781])
- monotonic increasing in the preregistered order: **False**
- interval excludes zero in the increasing direction: **False**
- extrapolated L where tau would reach 187/91: **108327912.83235885**
- crossing beyond L = 1024: **True**
- residual RMS around the log-log line: 0.01026

## Curvature diagnostics (independent of the L trend)

| window | cumulative tau | histogram tau | estimator disagreement |
|---|---|---|---|
| [16, 512] | 1.93585 | 1.96603 | 0.03018 |
| [32, 4096] | 1.92009 | 1.70277 | 0.21732 |
| [32, 2048] | 1.92828 | 1.84661 | 0.08166 |
| [64, 4096] | 1.91207 | 1.60696 | 0.30511 |

- cumulative spread across windows: **0.023777928979577867**
- max estimator disagreement: **0.30510883600492167**
- curvature present: **True**

## Paired threshold check (canonical vs refined, shared seeds)

| L | refined - canonical |
|---|---|
| 256 | -0.000720 |
| 512 | -0.000071 |
| 1024 | -0.000028 |

max |delta| = **0.0007204693940576767**

## Decision

**CROSSOVER_NOT_ESTABLISHED**

The finite-size-crossover explanation is not supported by the stored data, so the deviation is unexplained at these sizes and requires larger L than 1024, not a repeat of N-001.

## Disclosure

IMPORTANT AND NOT DISCLOSED-FREE. Before this preregistration was written I had already read the four window fits stored in N001_production_summary.json, whose cumulative tau values are 1.93585 (s in [16,512]), 1.92009 (s in [32,4096]), 1.92828 (s in [32,2048]) and 1.91207 (s in [64,4096]). I had also read that the cumulative and histogram estimators of the same window disagree, 1.92009 versus 1.70277. So the existence of some window dependence and of estimator disagreement was already visible. This preregistration is therefore INFORMED, not blind, and is labelled as such. What had NOT been seen, and is the genuinely pre-specified primary test here, is any per-L value of tau. The primary statistic below is therefore novel at the time of freezing, and the directional prediction in 'primary_prediction' is derived from finite-size theory rather than from any number computed here.

## Claim boundary

- No new physics is claimed. This is a diagnostic of whether an existing escalation can be attributed to finite-size crossover.
- A CROSSOVER_SUPPORTED result does not resolve Q-P007; it relocates the question to larger L and states what would be needed there.
- The N-001 production decision DEVIATION_FROM_FISHER is not edited, reversed, or softened by this diagnostic.
- No novelty claim, and nothing here bears on any other experiment in the laboratory.
- The Fisher value 187/91 is a two-dimensional known result and is used only as the reference to compare against.
- If the slope interval includes zero, the outcome is CROSSOVER_NOT_ESTABLISHED, and reporting that as convergence would be a false positive for the hypothesis this diagnostic was written to test.
