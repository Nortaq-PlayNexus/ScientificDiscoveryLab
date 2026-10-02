# ScientificDiscoveryLab — Instrument Validation and Audit Findings

**Deposit type:** Dataset / Software
**Version:** 1.0.0
**Date:** 2026-09-28
**License:** MIT

---

## What this deposit contains

A self-audit of the measurement instruments used by an autonomous scientific
simulation laboratory. The laboratory's discipline is its real asset: frozen
preregistrations locked by SHA-256, hash-chained change logs, independent second
implementations, fail-closed runners, and an explicit "do not claim" register.

This deposit publishes the audit trail of a session in which **three genuine
defects were found in the laboratory's own instruments**, one of which had
previously been counted as a *pass*.

The most interesting result is not any physics. It is that in two of the three
cases the defect made the laboratory's own anomaly look **smaller** than it
really is, and in one case a defective test was being counted as calibrated.

## The three findings

### 1. A statistical test that was counting itself as calibrated

A PRNG battery test (`T03_runs`, NIST SP 800-22 §2.3) routed its statistic
through a helper that applies the *z-score* identity `erfc(|z|/√2) =
2(1−Φ(|z|))`. The helper is correct for the four other tests that genuinely pass
a z-score, but the runs statistic is already in `erfc` units, so a spurious `√2`
inflated every p-value.

Measured on 200 fresh seeds of the laboratory's own stream, evaluating both
implementations on **identical** bits:

| Stream length | Implementation | KS vs uniform | Rejections at α=0.01 |
|---|---|---|---|
| 2^18 | shared `t_runs` | **6.7e-06** | **0 / 200** |
| 2^18 | independent reference | 0.847 | 1 / 200 |
| 2^22 | shared `t_runs` | **9.1e-11** | **0 / 200** |
| 2^22 | independent reference | 0.106 | 1 / 200 |

Separately, the standard's own applicability precondition
`|π − ½| ≥ 2/√(n−1)` — which requires a ~4σ deviation in the bit balance — is
met by **0 of 200 seeds** at either length. The corrected status of record is
therefore `UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION`, and the accurate
per-test summary is **23 of 24 calibrated, 0 miscalibrated, 1 unresolvable**.

**No generator is certified by this work, and a previously withdrawn certificate
stays withdrawn.**

### 2. A power-law exponent that the laboratory's estimator biased downward

A production run reported a 2D percolation cluster-mass exponent of
**τ = 1.92009** against the Fisher value **187/91 = 2.054945**, and escalated it
as a deviation. Two follow-ups on the *already-stored* data, generating no new
Monte Carlo:

**(a) The deviation is not finite-size crossover.** The preregistered,
theory-derived prediction — a periodic box sits slightly disordered, so τ must
rise with L — is **violated**:

| L | realizations | tail clusters | τ | deviation from 187/91 |
|---|---|---|---|---|
| 256 | 100 | 188 921 | 1.90306 | −0.15189 |
| 512 | 100 | 740 653 | 1.88981 | −0.16513 |
| 1024 | 50 | 1 462 967 | 1.92009 | −0.13486 |

Slope dτ/dln L = **+0.0123**, 95% interval **[−0.0232, +0.0478]** — includes
zero. The deviation is nearly *size-independent*. A shrinking offset is the
crossover signature; a constant one is not.

**(b) The estimator itself is biased upward.** Building synthetic distributions
of a **known** exponent and measuring each estimator's error shows the frozen
cumulative estimator returns values **+0.11 to +0.35 too large**, reproducibly
across three independent constructions and two true exponents, while the
histogram estimator is unbiased to within 0.008.

| quantity | value |
|---|---|
| frozen production number (unedited) | 1.92009 |
| bias-corrected secondary estimate | ~1.81 |
| unbiased histogram estimator | 1.70277 |
| Fisher reference | 2.054945 |

All three are below Fisher, and the corrected values are **further** below it
than the reported one. So the instrument bug made the laboratory's own anomaly
look *smaller* than it is. The escalation **stands, strengthened**.

### 3. A reproducibility control that was inviting a false fix

A read-only audit pinned an append-only registry by whole-file SHA-256, so it
reported 10 test errors every time an experiment was registered. The tempting fix
— refreshing the immutable baseline — would have silently destroyed the control.

Instead the registry's **historical prefix** is now pinned byte-for-byte in a
frozen artifact whose digest is *required to equal* the baseline's whole-file
digest. That anti-laundering binding proves the frozen bytes are the originally
audited content rather than a re-freeze of today's file. Edits, reorderings,
deletions and prepends inside the audited region still fail closed; appends are
measured and reported.

**No baseline was refreshed.**

## Test suite

| | before | after |
|---|---|---|
| Full suite | 391 passed, **10 errors** | **495 passed, 0 errors** |

The registry append made at the end of the session did not reintroduce a single
error, which is the direct check that the pin repair works.

## Verification that nothing historical was altered

Every check below is re-runnable from the deposit:

- shared RNG battery byte-identical to the digest recorded in the production
  database (`5f53f3ea…`)
- the 60 MB percolation raw database byte-identical to its manifest digest
  (`9f421d06…`)
- the percolation production runner byte-identical to its manifest digest
  (`84761d2d…`)
- the 2026-09-24 evidence baseline byte-identical to its own historical run
  manifest (`8c154ab0…`)
- all 50 whole-file-pinned historical inputs unchanged
- the registry's audited historical prefix unchanged
- all 24 960 stored production p-value rows intact
- both hash-chained change logs intact

## Honest limitations

- **No physics discovery is claimed anywhere.** The strongest statement this
  work supports is "these instruments were defective, here is the evidence, and
  here is what we cannot conclude."
- The 2D percolation question **Q-P007 remains open**. The magnitude of its
  deviation is now untrusted and its direction is robust.
- `CROSSOVER_NOT_ESTABLISHED` is **not** crossover excluded. Three sizes spanning
  a factor of four cannot detect a slow drift.
- The empirical *detection* of the `T03_runs` defect is resolution- and
  seed-dependent; the classification rests on an exact algebraic identity, not on
  a significance test.
- Both preregistrations in this deposit are labelled **informed, not blind**, and
  each states exactly what had already been seen before it was frozen.
- Two preregistration-time hypotheses about the *mechanism* of the exponent bias
  were tested and **rejected** (a survivor-count off-by-one, and the residual
  weighting). The mechanism is still not established; only the magnitude is.

## Reproducing

```powershell
python -m pytest -q            # 495 passed
```

See `package/REPRODUCIBILITY.md` in the packaged deposit.

## Citation

See `CITATION.cff`. This work is **not** affiliated with, and does not supersede,
any other deposit from this group; see the note in `description.md`.
