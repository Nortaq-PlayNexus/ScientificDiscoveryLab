# ScientificDiscoveryLab: Instrument Validation and Self-Audit Findings

## Upload Type

Dataset / Software

## Title

ScientificDiscoveryLab: Three Instrument Defects Found by Self-Audit — A Defective Statistical Test, a Biased Exponent Estimator, and a Reproducibility Control That Invited a False Fix

## Subtitle

Preregistrations, paired re-implementations, hash-chained change logs, and the complete evidence that no historical artifact was altered

## Abstract

This deposit publishes the audit trail of a self-audit of an autonomous
simulation laboratory whose principal asset is methodological discipline rather
than results: preregistrations frozen by SHA-256, hash-chained change logs,
independent second implementations, fail-closed runners, and an explicit
"do not claim" register. Three genuine defects were found in the
laboratory's own measurement instruments.

**First**, a PRNG statistical test (NIST SP 800-22 §2.3) applied a *z-score*
conversion to a statistic the standard already defines in `erfc` units,
systematically inflating its p-values. On 200 fresh seeds of the laboratory's
own random stream, evaluating both implementations on identical bits, the
shared test gives a Kolmogorov–Smirnov p-value of 6.7e-06 with 0 of 200
rejections while an independently written reference implementation of the same
section gives 0.847 with 1 of 200. The standard's own applicability precondition
is met by 0 of 200 seeds at either stream length, so the corrected status is
`UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION`. A previously published claim
that "0 of 24 battery tests were miscalibrated" is superseded for this one
test: the accurate statement is 23 of 24 calibrated, 0 miscalibrated, 1
unresolvable. No generator is certified by this work and a previously withdrawn
certificate remains withdrawn.

**Second**, a 2D percolation cluster-mass exponent reported as τ = 1.92009
against the Fisher value 187/91 = 2.054945 was found to rest on a biased
estimator. Two follow-ups on already-stored data generated no new Monte Carlo.
The deviation is *not* finite-size crossover: the preregistered,
theory-derived prediction that τ rises with system size is violated
(1.90306, 1.88981, 1.92009 at L = 256, 512, 1024; slope +0.0123 with a 95%
interval of [−0.0232, +0.0478]) and the deviation is nearly size-independent.
Building synthetic distributions of a known exponent shows the frozen estimator
returns values +0.11 to +0.35 too large, reproducibly across three independent
constructions and two true exponents, while a histogram estimator is unbiased to
within 0.008. Correcting the bias moves τ to approximately 1.81, and the
unbiased estimator independently gives 1.70 — both *further* from the Fisher
value than the number originally reported. The escalation therefore stands and is
strengthened, while the numeric value is declared untrustworthy.

**Third**, a read-only reproducibility audit pinned an append-only registry by
whole-file hash, producing ten test errors on every experiment registration and
creating standing pressure to refresh an immutable baseline. The fix pins the
registry's audited historical prefix instead, in a frozen artifact whose digest
is required to equal the baseline's whole-file digest, so the control still
fails closed on any edit inside the audited region while legitimate appends are
measured. No baseline was refreshed.

The full test suite went from 391 passed with 10 errors to **495 passed with 0
errors**. Every historical artifact is verified byte-identical: the shared
battery, a 60 MB raw database, a production runner, the 2026-09-24 evidence
baseline, all 50 whole-file-pinned inputs, the registry's audited prefix, and
24 960 stored production p-value rows.

## No-discovery statement

**No scientific discovery is claimed, implied, or supported by this work.** The
laboratory's stated purpose is to reproduce known laws and to falsify its own
claims; its strongest reachable state is "flag for human scientific review".
What this deposit contributes is evidence about instruments, including three
cases where the laboratory's own bugs had been making its results look *better*
than they were.

## Included Materials

- Two frozen preregistrations, each labelled **informed, not blind**, each
  stating exactly what had already been seen before freezing, each with an
  explicit falsification direction
- Paired re-implementations compared on identical inputs
- Machine-readable results and rendered reports for every experiment
- Hash-chained change logs with verifiable link structure
- A do-not-claim register and a current-status record
- Complete test suite covering reproduction, decision rules, and honesty
  constraints
- A verification script that re-checks every historical artifact's hash

## Keywords

reproducibility research, measurement instrument validation, estimator bias,
statistical test calibration, NIST SP 800-22, percolation, cluster mass
exponent, Fisher exponent, finite-size scaling, preregistration, hash chaining,
fail-closed analysis, negative results, null results, self-audit, software
correctness, scientific integrity, percolation exponents, power-law fitting

## Method

### Estimator validation on known exponents

Real experimental data cannot reveal an estimator's bias, because the truth is
unknown by construction. This deposit therefore validates every estimator against
**synthetic distributions of a known exponent**, under three independent
constructions: exact integer counts with floor truncation below 0.1%, inverse-CDF
sampling from a continuous Pareto law (so the only error source is unbiased
Poisson noise), and the same sample at four times the size to confirm the measured
error is not a noise artefact. A bias may be applied as a correction **only** if
it behaves identically for two different true exponents; a companion test proves
this rule refuses a correction when the two disagree.

### Paired estimator comparison

Two implementations of the same specification are evaluated on **identical** bit
streams, so any difference is provably a property of the estimator rather than of
the generator or the sample. The implementations were written from the published
procedure rather than imported from the code under test, and the independent
implementation reproduces the stored production value with an absolute difference
of exactly 0.

### Dependence-preserving resampling

Bootstrap resampling always operates on realization blocks, never on individual
clusters or samples, because items within one realization share a seed and a
threshold geometry.

### Honest preregistration

Each preregistration records, in the frozen document itself, which observations
had already been made before it was written. Where a preregistration could not be
blind, it says so and identifies which statistic was genuinely novel at freeze
time.

## Limitations

Stated in full in the deposit README. Principal points: the 2D percolation
question Q-P007 remains open; `CROSSOVER_NOT_ESTABLISHED` is not crossover
excluded; the empirical detection of the statistical test's defect is
resolution- and seed-dependent even though the defect itself is provable
algebraically; and the *mechanism* of the exponent bias has not been
established, only its magnitude.

## Ethical and Integrity Considerations

No human subjects, no sensitive data, no fabricated data. All historical results,
including ones that failed, are preserved unchanged. Bugs found in the authors'
own code are published rather than quietly fixed, and three of the defects
documented here were found by the laboratory's own controls. Baseline controls
were never refreshed to make a check pass.

## Related deposits — important scope note

This deposit is **separate from and unrelated to** any other deposit by this
group. In particular, DOI `10.5281/zenodo.22849652` covers a different project
(coherent optical vortex propagation, EXP-0007) and is **not** amended,
corrected, or superseded by this deposit. The two share no data, no code, and no
conclusions. Published Zenodo records are immutable, so any change to a published
record must appear in a **new version** of that record rather than as an edit.

## License

MIT License — see the LICENSE file in the package.

## Contact

ScientificDiscoveryLab
