# T03_runs estimator audit — instrument defect in the shared RNG battery

**Date:** 2026-09-28 · **Audit finding:** N-004 · **Question:** Q-I004
**Preregistration:** `CONFIG/prereg_T03_FORMULA_AUDIT.json`
(`8ffc034dffdf4836…`, frozen before any calibration number existed)

## Verdict

**`ESTIMATOR_DEFECTIVE`.** The shared battery's `T03_runs` is not a valid
measurement instrument at the stream lengths this laboratory uses. The defect is
in the *test*, not in the generator it was measuring.

## What was wrong

NIST SP 800-22 Rev. 1a §2.3 (Runs) defines

```
P-value = erfc( |V_obs − 2nπ(1−π)| / (2·√(2n)·π(1−π)) )
```

`engine/validation/rng_battery.py::t_runs` routes that quantity through the
module's `_erfc_p` helper, which is the identity `erfc(|z|/√2) = 2(1−Φ(|z|))`.
That helper is **correct** for `t_monobit` and `t_dft`, which genuinely pass a
z-score. But the runs statistic is already in `erfc` units, so the helper
divides by an extra `√2` and the p-values come out systematically too large.

Second, the standard's §2.3 step 1 precondition — run the test only if
`|π − ½| ≥ 2/√(n−1)` — is missing entirely. That threshold is ≈0.0039 at 2^18
while a fair stream deviates ≈0.0008, i.e. it demands a ~4σ deviation in the bit
balance. **0 of 200 seeds satisfy it**, so the test is not applicable to these
streams at all.

## Evidence

Same 200 fresh `G_LAB` seeds, same bits, two implementations:

| Bits | Implementation | KS vs uniform | rejects @ α=0.01 | mean p |
|---|---|---|---|---|
| 2^18 | shared `t_runs` | **6.7e-06** | **0/200** | 0.603 |
| 2^18 | SP 800-22 reference | 0.847 | 1/200 | 0.493 |
| 2^22 | shared `t_runs` | **9.1e-11** | **0/200** | 0.632 |
| 2^22 | SP 800-22 reference | 0.106 | 1/200 | 0.526 |

Because the streams are identical, the difference is provably the estimator.

The stored N-004 rows show the pile-up is **generator-independent** — it appears
in the deliberately broken LCG too, and `T03_runs` rejects at α=0.01 for *none*
of the four generators:

| Generator | Bits | n | KS p | rejects@0.01 |
|---|---|---|---|---|
| G_LAB | 2^18 | 200 | 1.7e-03 | 0 |
| MT19937 | 2^18 | 200 | 1.6e-04 | 0 |
| PCG64_direct | 2^18 | 200 | 2.2e-06 | 0 |
| WEAK_LCG_BROKEN | 2^18 | 200 | **3.1e-08** | 0 |

The broken generator "failing" T03 was the test detecting its own defect.

## What this supersedes, and what it does not

- **Superseded:** the N-004 per-test claim that **0 of 24** tests were
  miscalibrated for `G_LAB`. `T03_runs` is miscalibrated.
- **Not overturned:** the N-004 family-level `BATTERY_VALID` verdict, which
  depends on the positive control being rejected at the family-wise level — the
  other 23 tests supply that.
- **Untouched:** the other 23 per-test cells, which were not re-derived here.
- **Unchanged:** the EXP-0004 certificate stays **withdrawn**. A defective
  instrument cannot support a certification; if anything this strengthens the
  withdrawal.

## Claim boundary

- Nothing here certifies any generator, or shows G_LAB to be defective. The
  opposite: the instrument was defective.
- No novelty, no physics. This characterises an instrument the rest of the lab
  depends on.

## Files

| Path | Role |
|---|---|
| `CONFIG/prereg_T03_FORMULA_AUDIT.json` | frozen design, decision rule, falsification |
| `CODE/runs_sp800_22.py` | independent reference implementation of §2.3 |
| `CODE/run_t03_formula_audit.py` | fail-closed runner; refuses to run if the shared battery hash moved |
| `CODE/log_change.py` | hash-chained change-log appender |
| `TESTS/test_t03_formula.py` | 22 conformance/regression tests |
| `RESULTS/T03_FORMULA_AUDIT_20260928/` | machine-readable report + rendering |
| `../AUDIT_REPAIR_N004_PRODUCTION/CONFIG/production_changes.jsonl` | supersession entry `559358ce…` |

Run:

```powershell
python -m pytest -q 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/TESTS/test_t03_formula.py
python 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_T03_RUNS_FORMULA/CODE/run_t03_formula_audit.py `
  --seeds 200 --output-json <new.json> --output-markdown <new.md>
```

The shared battery module is never modified — its SHA-256 is checked at runtime
against the digest recorded in the N-004 raw database, so this audit is provably
about the code that produced those results.

## Corrected status of record (follow-up, same session)

`CONFIG/prereg_T03_RECALIBRATION.json` (`3d03a118ff948b99…`) re-derives the
single N-004 cell under three variants, all on **identical** streams:

| Bits | as-implemented | √2-corrected | √2-corrected + applicability gate |
|---|---|---|---|
| 2^18 | KS p = **1.4e-05** | KS p = 0.343 | 0 scorable seeds |
| 2^22 | KS p = **8.8e-06** | KS p = 0.956 | 0 scorable seeds |

So the spurious `√2` explains the *entire* recorded non-uniformity. But the
standard's own precondition `|π − ½| ≥ 2/√(n−1)` is met by **0/200 seeds at
either length**: it demands a ~4σ deviation in the bit balance, while a fair
stream deviates 0.0008 at 2^18 against a 0.0039 threshold.

**Status of record: `UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION`** at both
lengths — not "calibrated". Per the N-004 preregistration's own rule, an
unresolved outcome must not be reported as agreement.

**Correction to the N-004 per-test claim:** *23 of 24* cells calibrated, *0*
miscalibrated, *1* unresolvable at these resolutions.

### An important limit, recorded deliberately

The extra `√2` is a deterministic property of the code — provable as an exact
algebraic identity and asserted to `rel=1e-12` by the test suite. But its
empirical **detection** is resolution- and seed-dependent: with 200 seeds it was
caught at 2^18 and *missed* at 2^22 under one seed labelling, then caught at both
under another. **Non-detection is not evidence of correctness.** The
classification therefore rests on the identity, not on the KS test.

## The other four `_erfc_p` callers — audited, not assumed

| Caller | Argument | Verdict |
|---|---|---|
| `T01_monobit` | z-score (S/√n, Var S = n) | CONFIRMED_CALIBRATED |
| `T06_dft` | z-score (standardised count deviation) | CONFIRMED_CALIBRATED |
| `T07_nontemplate` | z-score (normal approx; μ≈57) | CONFIRMED_CALIBRATED |
| `T15_ac1..ac8` | z-score (autocorrelation) | CONFIRMED_CALIBRATED |
| `T03_runs` | **already in erfc units** | **DEFECTIVE_BY_ALGEBRAIC_IDENTITY** |

`T07` remains a documented structural deviation from §2.7's χ² form, but its
normal approximation is sound at these lengths.

### Two fail-open defects of my own, caught and recorded

While building the caller audit I introduced — and fixed — two instances of the
exact fail-open class this lab has now hit twice in production runners:

1. The `T15` cell reported **`CONFIRMED_CALIBRATED` having measured zero
   p-values**, because an absent measurement was read as a pass.
2. The pooled key set for `T15` never resolved, so there was nothing to measure.

The audit now **raises** on a declared key that is not collected, and classifies
an unmeasurable cell as `UNRESOLVED_NO_MEASUREMENT`. Both are covered by tests.

## Recommended follow-up (not done here)

Re-derive `t_runs` without the extra `√2` and with the applicability gate, then
re-run the N-004 per-test table for that cell only. Every other cell should be
re-checked for the same `z`-versus-`erfc` confusion: `t_monobit` and `t_dft` were
verified correct here, but the helper makes the mistake easy to repeat.
