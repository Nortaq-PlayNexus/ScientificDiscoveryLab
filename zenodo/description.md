# A computational research laboratory that audited itself, and found four defects in its own instruments

## No-discovery statement

**No physics discovery is claimed anywhere in this deposit, and none should be
inferred from any file in it.** The contribution is evidence about measurement
instruments. Several experiments in this laboratory failed; those failures are
recorded as findings rather than deleted, and several results that once looked
like anomalies turned out to be instrument artifacts. The strongest statement
this deposit supports is: *these instruments were defective, here is the
evidence, and here is what we cannot conclude.*

## What this deposit is

Sixteen registered experiments across seven areas — percolation physics, optical
propagation, prime gaps, Feigenbaum constants, pseudorandom-number certification,
water-sound response, and AI-consciousness measurement methodology — run to a
written standard (`RESEARCH_RULES.md`): four claim layers, a mandatory experiment
lifecycle, a mandatory control suite, a kill-the-hypothesis requirement, evidence
grading E0–E6, append-only registries, read-only raw data, and fail-closed runners.

The physics is not the interesting part. The methodology is, and the
laboratory's own audit of that methodology is the substantive result.

## Finding 1 — a statistical test that was counting itself as calibrated

A PRNG battery test (`T03_runs`, NIST SP 800-22 §2.3) routed its statistic
through a helper applying the *z-score* identity `erfc(|z|/√2) = 2(1−Φ(|z|))`.
That helper is correct for the four other tests that genuinely pass a z-score
through it. But the runs statistic is **already in `erfc` units**, so a spurious
`√2` inflated every p-value.

Measured on 200 fresh seeds of the laboratory's own stream, both implementations
evaluated on identical bits:

| Stream length | Implementation | KS vs uniform | Rejections at α=0.01 |
|---|---|---|---|
| 2^18 | shared `t_runs` | **6.7e-06** | **0 / 200** |
| 2^18 | independent reference | 0.847 | 1 / 200 |
| 2^22 | shared `t_runs` | **9.1e-11** | **0 / 200** |
| 2^22 | independent reference | 0.106 | 1 / 200 |

The standard's own applicability precondition `|π − ½| ≥ 2/√(n−1)` — which
requires roughly a 4σ deviation in bit balance — is met by **0 of 200 seeds** at
either length. Corrected status: `UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION`.
Accurate summary: **23 of 24 calibrated, 0 miscalibrated, 1 unresolvable**.

**No generator is certified by this work, and a previously withdrawn certificate
remains withdrawn.**

## Finding 2 — a power-law exponent the laboratory's own estimator biased

A production run reported 2D percolation cluster-mass exponent **τ = 1.92009**
against the Fisher value **187/91 = 2.054945**, and escalated it as a deviation.

**(a) Not finite-size crossover.** The preregistered prediction — a periodic box
sits slightly disordered, so τ must *rise* with L — is violated:

| L | realizations | tail clusters | τ | deviation from 187/91 |
|---|---|---|---|---|
| 256 | 100 | 188 921 | 1.90306 | −0.15189 |
| 512 | 100 | 740 653 | 1.88981 | −0.16513 |
| 1024 | 50 | 1 462 967 | 1.92009 | −0.13486 |

`dτ/dln L = +0.0123`, 95% interval **[−0.0232, +0.0478]**, which includes zero. A
shrinking offset is the crossover signature; a constant one is not.

**(b) The estimator is biased upward.** Synthetic distributions of a *known*
exponent show the frozen cumulative estimator returning values **+0.11 to +0.35
too large**, reproducibly across three constructions and two true exponents,
while the histogram estimator is unbiased to within 0.008.

| quantity | value |
|---|---|
| frozen production number (unedited) | 1.92009 |
| bias-corrected secondary estimate | ~1.81 |
| unbiased histogram estimator | 1.70277 |
| Fisher reference | 2.054945 |

All three are below Fisher, and the corrected values are **further** below. The
instrument bug made the laboratory's own anomaly look *smaller* than it really is.
**The escalation stands, strengthened.**

## Finding 3 — a reproducibility control that was inviting a false fix

A read-only audit pinned an append-only registry by whole-file SHA-256, so it
reported 10 test errors every time an experiment was registered. The tempting fix
— refreshing the immutable baseline — would have silently destroyed the control.

Instead the registry's **historical prefix** is pinned byte-for-byte in a frozen
artifact whose digest is *required to equal* the baseline's whole-file digest.
That anti-laundering binding proves the frozen bytes are the originally audited
content rather than a re-freeze of today's file. Edits, reorderings, deletions and
prepends inside the audited region still fail closed; appends are measured and
reported.

**No baseline was refreshed.**

## Finding 4 — found while preparing this deposit for publication

Verifying the test suite before publishing turned up **7 failing tests**. All
asserted bit-exact float equality between values recomputed from stored cells and
the same values as persisted JSON, which cannot survive a round-trip and
resummation over a 24 960-row table.

Two were more than tolerance issues:

- **`bitwise_value_match_within_float_tolerance`** compared against a `5e-15`
  bound while the observed deltas were `1.5e-06` and `5.5e-04`. It could only ever
  read `False` — yet the stored artifact recorded `True`. The deposit was
  asserting a reproducibility match that its own runner could not reproduce.
- **A bootstrap confidence interval matched at its lower bound to 4e-16 and
  differed by 1.4e-03 at its upper bound.** A symmetric percentile cannot do that.
  It is the signature of a different *accepted draw set*: 5 of 500 draws were
  rejected for non-convergence, same count, same per-size distribution, but which
  5 depends on draw order. The stored artifact had already recorded the gap
  (`stored_mean_abs_delta = 7.1e-04`) — the laboratory knew, and the test asserted
  exact equality anyway.

Effect on claims: **none.** Classifications unchanged, verified by the suite.

A fifth class of problem surfaced during publication, when the suite was run on a
clean Linux checkout for the first time. Nine further defects were exposed, all of
which were invisible on the authoring machine:

1. 329 files failed the byte-level integrity check, because `core.autocrlf`
   rewrote line endings that the recorded digests depended on.
2. A nested `.gitattributes` silently overrode the byte-exact rule for nine files.
3. One CI job could not install its dependencies, because `numpy>=2.5.0` requires
   Python ≥3.12 and the matrix included 3.11.
4. The CI dependency set was guesswork; six packages imported at module scope were
   missing, breaking collection of 33 tests.
5. The curated deposit's reference test copies were being collected, because the
   exclusion list predated that directory.
6. **The CI integrity gate could not fail.** It grepped `FAILED` summary lines for
   exception text, but those lines contain only node identifiers. It reported
   success while all 20 real failures sat unexamined. A gate that cannot fail is
   worse than no gate, because it reads as a green light.
7. A verification script read its input as UTF-8 and therefore parsed zero lines
   when handed UTF-16 — which reads as a clean run.
8. A provenance audit hardcoded an absolute path under one user's home directory,
   making it unrunnable anywhere else.
9. That audit's stored report recorded absolute paths, so its file-existence
   assertions could only ever hold on the machine that produced it.

Defect 6 is the one worth dwelling on. It is the same failure mode this deposit
exists to document: a check that reports success without having checked anything.

Fixing defect 8 also forced a distinction worth stating. The provenance audit now
reports its source-marker fields as **unknown** rather than **absent** when the
external package is not present. "I did not look" and "I looked and found
nothing" are different claims, and reporting the first as the second records a
negative finding that was never made.

## The uncomfortable pattern

In two of the first three findings, **the bug made the laboratory's own anomaly
look smaller than it really was.**

A laboratory that reports only what confirms it drifts toward false confidence,
and the drift is invisible from inside, because each individual step looked
reasonable. That is why this deposit leads with the failures.

## Method

**Estimator validation on known exponents.** Real data cannot reveal an
estimator's bias, because the truth is unknown by construction. Every estimator
is therefore validated against synthetic distributions of a known exponent under
three independent constructions: exact integer counts with floor truncation below
0.1%, inverse-CDF sampling from a continuous Pareto law, and the same sample at
four times the size to confirm the error is not a noise artifact. A bias
correction may be applied **only** if it behaves identically for two different
true exponents; a companion test proves the rule refuses a correction when the
two disagree.

**Paired estimator comparison.** Two implementations of the same specification
are evaluated on identical bit streams, so any difference is provably a property
of the estimator rather than of the generator or the sample.

**Dependence-preserving resampling.** Bootstrap resampling operates on
realization blocks, never on individual clusters or samples, because items within
one realization share a seed and a threshold geometry.

**Honest preregistration.** Each preregistration records, in the frozen document
itself, which observations had already been made before it was written. Where a
preregistration could not be blind, it says so.

**Fail-closed readers.** Audit tooling refuses to run without the exact bytes it
was audited against, and reports an unavailability as a recorded condition rather
than substituting data. A copy that silently regenerated the input would defeat
the control it exists to provide.

## Reproducibility

The full test suite passes **543 tests, 0 failures** in the laboratory with
complete data. The published tree omits 377 MB of raw simulation output (`.npz`,
`.sqlite3`), regenerable from the seeds recorded in each preregistration; the
read-only audit suite reads some of it and therefore **fails closed**, which is
the control working as designed. Continuous integration asserts that the observed
failure set is *exactly* the recorded set of excluded-data failures — a new
failure fails the build, and so does a recorded failure that stops failing.

Every published file's SHA-256 is recorded in `manifest.json`, and the archive is
byte-reproducible: two independent builds produce an identical digest.

## Limitations

- **No physics discovery is claimed.**
- **Q-P007 remains open.** The magnitude of its deviation is untrusted; the
  direction is robust.
- **`CROSSOVER_NOT_ESTABLISHED` is not crossover excluded.** Three sizes spanning
  a factor of four cannot detect a slow drift.
- **The 3D percolation run (Q-P008) is unvalidated.** Its `p_c` and `C7`
  provenance are defective; corrected values have not been reproduced.
- **Several checks are `SAME_STREAM_IMPLEMENTATION_CHECK`** — same seed stream, so
  agreement is not independent validation.
- Two preregistration-time hypotheses about the *mechanism* of the exponent bias
  were tested and **rejected**. Only the magnitude is established.
- Bootstrap rejection is **order-dependent**, so bit-exact reproduction is not
  achievable for those quantities. This deposit says so rather than implying
  otherwise.
- The empirical detection of the statistical test's defect is resolution- and
  seed-dependent, even though the defect itself is provable algebraically.

## Ethical and integrity considerations

No human subjects, no sensitive data, no fabricated data. All historical results,
including those that failed, are preserved unchanged. Bugs found in the authors'
own code are published rather than quietly fixed, and all four defects
documented above were found by the laboratory's own controls. No baseline control
was ever refreshed to make a check pass.

## Related deposits — scope note

This deposit is **separate from and unrelated to** any other deposit by this
group. In particular, DOI `10.5281/zenodo.22849652` covers a different project
(coherent optical vortex propagation, EXP-0007) and is **not** amended, corrected,
or superseded here. The two share no data, no code, and no conclusions.

DOI `10.5281/zenodo.23101903` covers the AI-consciousness indicator battery, which
also exists as one investigation inside this laboratory record. Neither
supersedes the other; they are the same work at different scopes, and each should
be cited according to the question being asked.

Published Zenodo records are immutable. Any change to a published record must
appear as a **new version** (new version DOI, same concept DOI), never as an edit.

## License

MIT License — see the `LICENSE` file in the archive.
