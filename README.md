# ScientificDiscoveryLab

> **New to this repository, or picking up an interrupted session?**
> Read [\HANDOFF.md\](HANDOFF.md) first. It records what exists and where, the
> Zenodo API traps that cost real bugs here, the outstanding work, and the rule
> about never deleting a deposit.

**A computational research laboratory built to a preregistered standard — and a
self-audit that found four defects in its own instruments.**

> **No physics discovery is claimed anywhere in this repository.** Read
> `AUDIT/DO_NOT_CLAIM.md` and `CURRENT_STATUS.md` before summarising any of it.

| | |
|---|---|
| Experiments | 16 registered (`EXPERIMENT_REGISTRY.md`, append-only) |
| Areas | 7 — percolation, optics, prime gaps, Feigenbaum constants, PRNG certification, water-sound response, AI-consciousness methodology |
| Test suite | **543 passed, 0 failed** in the laboratory with full data |
| Claims | none |
| Zenodo | **[10.5281/zenodo.23122787](https://doi.org/10.5281/zenodo.23122787)** (v2.0.0) · [v1.0.0](https://doi.org/10.5281/zenodo.23109117) |

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23122787-blue)](https://doi.org/10.5281/zenodo.23122787)

---

## What this is

The physics is not the interesting part. **The methodology is.**

The laboratory runs to a written standard (`RESEARCH_RULES.md`): four claim
layers, a mandatory experiment lifecycle, a mandatory control suite, a
kill-the-hypothesis requirement, evidence grading E0–E6, append-only registries,
raw data that is never edited, and fail-closed runners.

Then it audited itself, and the audit found real defects in its own instruments.

---

## The three findings

### 1. A statistical test that was counting itself as calibrated

A PRNG battery test (`T03_runs`, NIST SP 800-22 §2.3) routed its statistic
through a helper applying the *z-score* identity `erfc(|z|/√2) =
2(1−Φ(|z|))`. That helper is correct for the four other tests that pass a z-score
through it — but the runs statistic is **already in `erfc` units**, so a spurious
`√2` inflated every p-value.

Measured on 200 fresh seeds, both implementations on identical bits:

| Stream length | Implementation | KS vs uniform | Rejections at α=0.01 |
|---|---|---|---|
| 2^18 | shared `t_runs` | **6.7e-06** | **0 / 200** |
| 2^18 | independent reference | 0.847 | 1 / 200 |
| 2^22 | shared `t_runs` | **9.1e-11** | **0 / 200** |
| 2^22 | independent reference | 0.106 | 1 / 200 |

Separately, the standard's own applicability precondition
`|π − ½| ≥ 2/√(n−1)` — requiring a ~4σ deviation in bit balance — is met by
**0 of 200 seeds** at either length.

Corrected status: `UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION`. Accurate
summary: **23 of 24 calibrated, 0 miscalibrated, 1 unresolvable**.

**No generator is certified. A previously withdrawn certificate stays
withdrawn.**

### 2. A power-law exponent the laboratory's estimator biased downward

A production run reported 2D percolation cluster-mass exponent **τ = 1.92009**
against the Fisher value **187/91 = 2.054945**, and escalated it as a deviation.
Two follow-ups on **already-stored** data, generating no new Monte Carlo:

**(a) Not finite-size crossover.** The preregistered prediction — a periodic box
sits slightly disordered, so τ must *rise* with L — is **violated**:

| L | realizations | tail clusters | τ | deviation from 187/91 |
|---|---|---|---|---|
| 256 | 100 | 188 921 | 1.90306 | −0.15189 |
| 512 | 100 | 740 653 | 1.88981 | −0.16513 |
| 1024 | 50 | 1 462 967 | 1.92009 | −0.13486 |

`dτ/dln L = +0.0123`, 95% interval **[−0.0232, +0.0478]** — includes zero. A
shrinking offset is the crossover signature; a constant one is not.

**(b) The estimator is biased upward.** Synthetic distributions of a *known*
exponent show the frozen cumulative estimator returns values **+0.11 to +0.35 too
large**, reproducibly across three constructions and two true exponents, while the
histogram estimator is unbiased to within 0.008.

| quantity | value |
|---|---|
| frozen production number (unedited) | 1.92009 |
| bias-corrected secondary estimate | ~1.81 |
| unbiased histogram estimator | 1.70277 |
| Fisher reference | 2.054945 |

All three are below Fisher, and the corrected values are **further** below. So
the instrument bug made the laboratory's own anomaly look *smaller* than it is.
**The escalation stands, strengthened.**

### 3. A reproducibility control that was inviting a false fix

A read-only audit pinned an append-only registry by whole-file SHA-256, so it
reported 10 test errors every time an experiment was registered. The tempting fix
— refreshing the immutable baseline — would have silently destroyed the control.

Instead the registry's **historical prefix** is pinned byte-for-byte in a frozen
artifact whose digest is *required to equal* the baseline's whole-file digest.
That anti-laundering binding proves the frozen bytes are the originally audited
content rather than a re-freeze of today's file. Edits, reorderings, deletions
and prepends inside the audited region still fail closed; appends are measured
and reported.

**No baseline was refreshed.**

---

## A fourth finding, from this publication

Verifying the suite before publishing turned up **7 failing tests**
(`CHANGELOG_TEST_TOLERANCE_REPAIR.md`, N-29). All asserted bit-exact float
equality between recomputed values and the same values as persisted JSON, which
cannot survive a round-trip and resummation over a 24 960-row table.

Two were more than tolerance issues:

- **`bitwise_value_match_within_float_tolerance`** used a `5e-15` bound against
  observed deltas of `1.5e-06` and `5.5e-04`. It could only ever read `False`,
  yet the stored artifact recorded `True`. **The artifact was asserting a
  reproducibility match its own runner could not reproduce.**
- **A bootstrap CI interval matched at its lower bound to 4e-16 and differed by
  1.4e-03 at its upper.** A symmetric percentile cannot do that. It is the
  signature of a different *accepted draw set*: 5 of 500 draws were rejected for
  non-convergence, same count, same per-size distribution, but which 5 depends on
  draw order. **The stored artifact already recorded this gap** —
  `stored_mean_abs_delta = 7.1e-04`.

Effect on claims: **none.** Classifications unchanged, verified by the suite.

---

## The uncomfortable pattern

Four defects. In two of the three original findings, **the bug made the
laboratory's own anomaly look smaller than it really was.**

A laboratory that only reports what confirms it drifts toward false confidence,
and the drift is invisible from inside because each individual step looked
reasonable. That is why this deposit leads with the failures rather than burying
them.

---

## Test suite

| | before | after |
|---|---|---|
| Full suite | 391 passed, **10 errors** | **543 passed, 0 errors** |

> **In a clean checkout, fewer.** Raw simulation data (`.npz`, `.sqlite3` —
> 377 MB, regenerable from the seeds in each preregistration) is excluded, and
> the read-only audit suite reads some of it. Those tests **fail closed** with
> `required historical evidence is missing`. That is correct behaviour, not a
> packaging defect: the audit refuses to run without the exact bytes it was
> audited against. CI asserts that every failure carries that cause and nothing
> else.

## Verification

```bash
python tools/verify_manifest.py         # every shipped file against manifest.json
python tools/verify_deposit_manifest.py # the preserved curated deposit
python -m pytest -q
```

## Honest limitations

- **No physics discovery is claimed.** The strongest supported statement is "these
  instruments were defective, here is the evidence, and here is what we cannot
  conclude."
- **Q-P007 remains open.** The magnitude of its deviation is now untrusted; the
  direction is robust.
- **`CROSSOVER_NOT_ESTABLISHED` is not crossover excluded.** Three sizes spanning
  a factor of four cannot detect a slow drift.
- **The 3D run (Q-P008) is unvalidated.** Its `p_c` and `C7` provenance are
  defective; the corrected values have not been reproduced.
- **Several checks are `SAME_STREAM_IMPLEMENTATION_CHECK`** — same seed stream,
  so agreement is not independent validation.
- Two preregistration-time hypotheses about the *mechanism* of the exponent bias
  were tested and **rejected**. The mechanism is still not established; only the
  magnitude is.
- Bootstrap rejection is **order-dependent**, so bit-exact reproduction is not
  achievable for those quantities. The deposit now says so.

## Repository layout

| Path | Contents |
|---|---|
| `RESEARCH_RULES.md` | the standard every experiment runs to |
| `MASTER_INDEX.md` | entry point for the whole laboratory |
| `EXPERIMENT_REGISTRY.md` | append-only, every experiment |
| `QUESTIONS.md` / `HYPOTHESES.md` | open questions and hypothesis states |
| `CURRENT_STATUS.md` | what is running, waiting, done |
| `CHANGELOG.md` | every change, including the ones that made things worse |
| `03_INVESTIGATIONS/` | per-investigation folders, universal template |
| `AUDIT/` | six audit directories, including the self-audit |
| `04_SHARED_ENGINE/` | RNG, hashing, BH-FDR, statistics, reproducibility |
| `99_ARCHIVE/` | superseded material, never deleted |
| `zenodo-deposit/` | the preserved curated v1.0.0 deposit |
| `tools/` | publish + integrity verification |

## Preserved: the curated v1.0.0 deposit

A smaller, curated version of this work (47 files: the three defects, their
preregistrations, the hash-chained change logs, the audit controls, the registry)
is **preserved** at [`zenodo-deposit/`](zenodo-deposit/README-PRESERVED.md)
rather than deleted. It is a different scope, not an older draft:

| | curated deposit | this repository |
|---|---|---|
| files | 47 | 1,123 |
| contents | the three defects and their controls | the whole laboratory |
| test count | 495 passed (2026-09-28) | 543 passed (2026-10-02) |

## Citation

See [`CITATION.cff`](CITATION.cff). Please cite this and read
`AUDIT/DO_NOT_CLAIM.md` alongside it.

## License

MIT — see [`LICENSE`](LICENSE).