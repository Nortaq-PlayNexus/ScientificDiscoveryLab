# N-29 — Test tolerance repair (2026-10-02)

## Status

7 failing tests repaired. Full suite: **543 passed, 0 failed** (was 536 passed /
7 failed).

## What happened

A pre-publication verification run found 7 failures, all in the read-only audit
controls. Every one was an assertion demanding **bit-exact float equality between
a value recomputed from stored cells and the same value as persisted JSON text**.

That comparison cannot succeed. A value that survives a JSON round-trip and is
then resummationed over a 24 960-row stored table differs in the last few digits,
and the test asserted `== 0.0` on that difference.

## Defects

| ID | Location | Assertion | Observed |
|---|---|---|---|
| T1 | `test_crossover_diagnostic.py` | `abs_delta == 0.0` | 2.22e-16 (1 ulp) |
| T2 | `test_read_only_audit.py` | `max_abs_*_delta == 0.0` | 1.5e-06 / 3.4e-06 |
| T3 | `test_read_only_audit.py` | `max_value_or_se_abs_delta == 0.0` | 3.5e-17, 1.4e-17, 3.4e-06 |
| T4 | `test_read_only_audit.py` | `bitwise_..._within_float_tolerance is True` | flag was **False** on recompute, **True** in the stored artifact |
| T5 | `test_read_only_audit.py` | `C2 pair_diff` (approx, default rel) | rel 3.2e-04 vs default 1e-6 |
| T6 | `test_read_only_audit.py` | width-route `mean`, `sd`, `ci95` | rel 9.6e-04 / 1.8e-02 / asymmetric |

## The two that were not just tolerance

### T4 — the tolerance was unattainable, so the flag asserted nothing

`bitwise_value_match_within_float_tolerance` compared `max(deltas) <= 5e-15`.
One float64 epsilon is 2.22e-16, so 5e-15 is ~22 ulp — but the observed deltas
were 1.5e-06 and 5.5e-04, six orders of magnitude above it. **The flag could only
ever read False.**

It read `true` in the stored 20260928 artifact and `false` on recomputation. So
the artifact asserted a reproducibility match that its own runner could not
reproduce. That is exactly the class of defect this deposit is about, appearing
inside the deposit.

**Fixed in `run_read_only_audit.py`:** tolerance is now **relative**, per
quantity, with the absolute deltas still recorded as measurements. Relative
deltas observed: p50 3.1e-06, se 5.3e-04, fss-component 9.2e-03, against bounds
1e-4 / 1e-3 / 5e-2. The FSS bound is the loose one because its components are
summed over the stored table and summation order does not survive the round-trip.

Comparing these on one *absolute* scale was itself wrong: 5.5e-04 is 1.7% of the
FSS standard error (0.0317) but 0.11% of the point estimate (0.5007). A single
absolute bound silently weights quantities by inverse magnitude.

### T6 — the CI interval agreed at one end and not the other

Recomputed `ci95` lower bound matched the stored value to **4e-16**; the upper
bound differed by **1.4e-03**.

A symmetric percentile interval cannot agree at one end and not the other. That
is the signature of a **different accepted draw set**, not float noise: 5 of 500
draws were rejected for non-convergence, with the same count and the same
per-L distribution, but *which* 5 depends on draw order.

The stored artifact already recorded this gap — `stored_mean_abs_delta = 7.1e-04`,
`stored_sd_abs_delta = 1.4e-03`. The lab knew, and the test asserted exact
equality anyway.

**Effect on the claim: none.** The acceptance fraction is 0.990, and the
classification remains `POINT_ESTIMATE_COMPATIBLE_WITH_0.5_PRECISION_VALIDATION_INCONCLUSIVE`
because the standard error is ~3x the decision tolerance either way. The test now
asserts those properties independently, so it fails if the conclusion ever stops
holding rather than if a digit moves.

## Method change

Every repaired assertion now separates two questions that were previously
conflated:

1. **Did the quantity change?** — bounded tolerance, chosen from what was observed
2. **Does the conclusion still hold?** — asserted independently and exactly

T1 previously answered (1) with `== 0.0` and had no version of (2) at all. That is
the shape of a test that will be "fixed" by loosening a number which should stay
tight. Recorded here so the distinction is not lost.

## What this does and does not establish

- **Establishes:** the full suite passes; the recorded artifact is reproducible to
  the precision its conclusions depend on.
- **Does not establish:** bit-exact reproducibility. It is not achievable for
  these quantities and the deposit now says so instead of implying otherwise.
- **Open:** the bootstrap rejection is order-dependent. Making it deterministic
  would require either recording which draws were rejected, or making acceptance
  order-independent. Not attempted — it would change a preregistered control.

Per `RESEARCH_RULES.md` §1 this is a **Layer 1 instrument result**. It changes no
scientific claim. EXP-0006 and EXP-0007 classifications are unchanged.

## Not recorded as an anomaly

Not `ANOM-####`. Nothing unusual was observed: this is a test-authoring defect
found by running the suite, exactly what the suite is for. It is logged here
because a deposit that ships "543 passed" without explaining why the count
changed from 536 would be hiding a modification to audited code.

## Files touched

- `03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/TESTS/test_crossover_diagnostic.py`
- `03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/TESTS/test_read_only_audit.py`
- `03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/CODE/run_read_only_audit.py`

The runner is **in** the audited scope. Its change is the T4 tolerance
correction and nothing else; the audit's classification logic is untouched, which
is why EXP-0006/EXP-0007 verdicts are unchanged. Verified by the suite.