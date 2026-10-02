# Statistics Basics

The minimum statistics every investigation here must understand and use correctly.

## Core ideas

- **Effect size** — how big is the effect? (Standardised: Cohen's d = difference /
  pooled SD.) A tiny effect can be "significant" with enough samples and still mean
  almost nothing.
- **p-value** — probability that a result at least this extreme would appear if the
  null hypothesis were true. It is NOT "probability the hypothesis is true".
- **Significance threshold (alpha)** — this lab uses alpha = 0.01 preregistered by
  default (stricter than the common 0.05) because we search many things.
- **Confidence interval** — plausible range for the true effect. Report it, not just
  p.
- **Power** — chance the experiment would detect an effect if it exists. Small
  samples + small effects = no power, and a "null" result then proves nothing.
- **Multiple testing** — testing many hypotheses inflates false positives. This lab
  uses Benjamini-Hochberg FDR correction (alpha 0.01) whenever many comparisons are
  made.
- **Multiple testing correction (BH-FDR)** — sort p-values, accept those that are
  still significant after the false-discovery-rate adjustment. Used per the sandbox
  precedent in `DECISIONS.md`.

## Which test to use

| Situation | Test |
|---|---|
| Two groups, normal-ish, independent | Student's t (Welch by default) |
| Compare means while shifting location robustly | Mann-Whitney U (nonparametric) |
| One distribution vs another | KS / Anderson-Darling |
| Categorical contingency | chi-square / Fisher exact |
| Many continuous groups | ANOVA / Kruskal-Wallis |
| Regression slope | OLS + CI; bootstrap for robustness |
| Correlation | Pearson (linear) / Spearman (monotonic) |

Decision aid: if you are not sure the normality assumption is safe, use the
nonparametric companion or bootstrap. If the result flips between the two, report
that.

## Randomisation and seeds

- Use the lab RNG (`engine.utilities.rng(label, seed)`) so runs are reproducible.
- Report the seed in every experiment.json.
- Run several seeds; report the distribution of the outcome, not just one number.

## Common traps

- **p-hacking** — running analyses until one is significant. Banned via
  pre-registration.
- **Optional stopping** — collecting data until significance. Banned; N is fixed.
- **Cherry-picking controls** — choosing the control that makes you look good.
  Preregister the control.
- **Reporting only positives** — the registry is append-only and keeps failed runs.
- **Data dredging** — a pattern found by scanning many things without correction is
  a *candidate* pattern, not a finding.