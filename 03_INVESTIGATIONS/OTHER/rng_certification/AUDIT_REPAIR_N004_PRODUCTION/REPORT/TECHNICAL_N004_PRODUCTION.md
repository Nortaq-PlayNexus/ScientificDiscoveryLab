# TECHNICAL — N-004 production: per-test calibration of the shared RNG battery

**Investigation:** Q-I004 · **Audit finding:** N-004 (Priority 1)

**Frozen protocol:** `CONFIG/prereg_N004_PRODUCTION.json`
(`config_sha256 91b5ebd0be6020f578d80fd0b083d26ff5f2837b86c0b3577ae730d450a60136`),
verified on load, never overwritten. Amendments hash-chained in
`CONFIG/production_changes.jsonl` (3 entries).

**Battery verdict: `BATTERY_VALID`** (positive control caught)
**G_LAB status: `INTERPRETABLE` — 0 of 24 tests miscalibrated at both stream lengths**

**The historical EXP-0004 "CERTIFIED" conclusion remains WITHDRAWN and is not
reinstated by this run.** No generator is certified here.

---

## 1. The question the audit actually asked

The audit did not ask "does the battery pass?" It asked: **which individual
battery tests are calibrated, for each generator, independent of the pooled
decision?** The historical EXP-0004 answer was a single pooled verdict computed
across p-values that all came from *one shared bit array*, which does not support
the independence that verdict assumed.

So the primary statistic here is not a pass/fail. It is the **uniformity of each
test's p-value across many independent seeds** — the only reading that survives
the shared-stream problem.

## 2. Design

| Element | Choice |
|---|---|
| Battery | `engine.validation.rng_battery`, **unmodified**, SHA-256 checked at runtime and on validation |
| Tests | 24 (NIST SP 800-22 footprint + classic tests) |
| Generators | `G_LAB` (target), `PCG64_direct`, `MT19937` (references), `WEAK_LCG_BROKEN` (**positive control that must fail**) |
| Stream lengths | 2^18 (200 seeds) and 2^22 (60 seeds) per generator |
| Seeds | fresh namespace 900000+, disjoint from every historical range |
| Evaluations | 1040, 8 workers, 377 s, **0 errors** |
| α | 0.01 |
| Primary | per-test KS uniformity of p-values vs Uniform(0,1), BH-FDR across the 24 tests within each cell |
| Secondary | exact Clopper-Pearson band on rejection rates; Holm, Šidák and uncorrected family-wise rates |
| Raw | SQLite, one row per (generator, seed, length, test), 24,960 rows, hash-bound |

**Why a deliberately broken generator is essential:** a battery that passes
everything is worthless. The audit's falsification condition was "if control
generators fail marginal tests, invalidate the battery before interpreting
G_LAB"; that is inverted here into a positive control that **must** be flagged,
and whose failure voids every other number in the run.

## 3. Positive control: the battery is valid

`WEAK_LCG_BROKEN` (31-bit LCG, multiplier 1103515245, increment 12345) is caught
decisively at both lengths:

| length | family-wise rate (Bonferroni) | `T13_words` rejection rate | KS p for `T13_words` |
|---|---|---|---|
| 2^18 | **1.000** | **1.000** (band [0.974, 1.000]) | 0.0 |
| 2^22 | **1.000** | **1.000** (band [0.915, 1.000]) | 0.0 |

`T03_runs` is also flagged. Battery verdict: **`BATTERY_VALID`**.

## 4. G_LAB result: all 24 tests calibrated at both lengths

| length | seeds | miscalibrated | Bonferroni family-wise rate | nominal |
|---|---|---|---|---|
| 2^18 | 200 | **0 / 24** | 0.005 | 0.01 |
| 2^22 | 60 | **0 / 24** | 0.017 | 0.01 |

Every test's rejection rate at α = 0.01 lies inside its exact binomial band at
both lengths. Mean p-values cluster tightly around 0.5 (range 0.431–0.581 across
all 24 tests and both lengths), which is the behaviour a calibrated test must
have. Full per-test table is in `N004_summary.json`.

## 5. The dependence penalty — the quantitative vindication of the audit

This is the substantive scientific content of the run.

| generator | length | **uncorrected** family-wise rate | Bonferroni | ratio | nominal |
|---|---|---|---|---|---|
| G_LAB | 2^18 | **0.205** | 0.005 | **41×** | 0.01 |
| G_LAB | 2^22 | **0.200** | 0.017 | 12× | 0.01 |
| MT19937 | 2^18 | 0.160 | 0.000 | — | 0.01 |
| MT19937 | 2^22 | 0.233 | 0.017 | 14× | 0.01 |
| PCG64_direct | 2^18 | 0.160 | 0.000 | — | 0.01 |
| PCG64_direct | 2^22 | 0.217 | 0.017 | 13× | 0.01 |

**Twenty-four tests sharing one input stream reject at ~20% per seed when
uncorrected, against a nominal 1% — an inflation of 12× to 41×.** Correcting for
the family brings the rate to 0.000–0.017, i.e. properly calibrated.

This is exactly the defect the audit identified in EXP-0004, now measured rather
than asserted: the shared-stream dependence is real, large, and fully accounted
for by a dependence-respecting correction. **It was the right call to withdraw
that certificate**, and this run is the first quantitative demonstration of why.

Note also that Bonferroni, Šidák and Holm agree closely here
(e.g. G_LAB 2^18: 0.005 / 0.005 / 0.005), i.e. the residual dependence penalty
beyond Bonferroni is small — as expected, since Bonferroni is valid under
arbitrary dependence and is the conservative choice.

## 6. One genuine instrument defect: `T03_runs`

`T03_runs` (NIST 2.3 Runs) is the only test showing a systematic problem, and it
is instructive:

| generator | length | n | KS D | KS p | BH reject | rejection rate | in band | rule status |
|---|---|---|---|---|---|---|---|---|
| G_LAB | 2^18 | 200 | 0.1321 | 0.0017 | no | 0.000 | yes | calibrated |
| G_LAB | 2^22 | 60 | 0.1460 | 0.1399 | no | 0.000 | yes | calibrated |
| MT19937 | 2^18 | 200 | 0.1525 | 0.0002 | **yes** | 0.000 | yes | miscalibrated |
| PCG64_direct | 2^18 | 200 | 0.1838 | 0.0000 | **yes** | 0.000 | yes | miscalibrated |
| PCG64_direct | 2^22 | 60 | 0.2658 | 0.0003 | **yes** | 0.000 | yes | miscalibrated |

Two things to state honestly:

1. **The distortion is in the shape of the p-value distribution, not the
   rejection rate.** `T03_runs` never rejects in any cell (rate 0.000, inside the
   band everywhere). Its mean p-value is **0.556–0.576** across all good
   generators, skewed high rather than centred on 0.5 — i.e. the test is mildly
   *conservative*, and its p-values are not exactly uniform.
2. **The flag is not stable.** Statistically equivalent PCG64 stream
   constructions get opposite classifications (G_LAB not flagged, PCG64_direct
   flagged, at the same n = 200). That instability is itself the finding: at this
   resolution the preregistered rule cannot reliably classify `T03_runs`, so for
   G_LAB the correct reading is "not flagged, with a visible p-value skew the
   rule does not reliably detect" rather than "clean".

`T03_runs` should be treated as **borderline / UNRESOLVED** for all generators,
and it is the one test in this battery whose p-value formula deserves an
independent check against the NIST reference.

## 7. Three defects I introduced and caught, all before acceptance

Recorded in full in `CONFIG/production_changes.jsonl`. None changed a
preregistered margin, α, seed count, or decision rule.

1. **The family-wise "max-T permutation" control was mathematically inert.**
   The maximum of a set of p-values is permutation-invariant, so permuting the
   observed p-values produces a null whose every draw equals the observed
   maximum. A preflight showed it reporting a **0.000** family-wise rate for the
   deliberately broken generator that Holm rejects on 12/12 seeds. Shipping it
   would have inverted the audit's central finding. Replaced with Bonferroni,
   which is valid under arbitrary dependence.
2. **A fail-open runner, twice.** The first attempt lost the entire MT19937 arm
   (`RandomState` lacks `integers`; and its `randint` is int32-bounded so the
   battery's 2^32 word draw overflows) yet exited 0. The second attempt reported
   24,960 rows written while the table held **0**, because `TEST_IDS` was only
   populated in `analyze`. The runner now refuses to write a manifest unless
   every preregistered cell produced the preregistered number of successful
   evaluations, and asserts the stored row count and complete-seed-vector count
   after commit. Both failed attempts are preserved as evidence.

## 8. Resolution — the binding limitation

This is stated in the preregistration and is not a postscript:

- At α = 0.01, the rejection-rate estimate has standard error
  `sqrt(α(1−α)/S)` = **0.0071 at S = 200** and **0.0127 at S = 60**.
- A miscalibration that shifts the true rejection rate from 0.01 to below about
  **0.04 is not detectable at S = 200**, and the 2^22 binomial band is
  **[0.000, 0.085]** — very wide.
- The KS test on p-values is the more powerful instrument, but it too depends on
  S, as `T03_runs` demonstrates.

**Therefore: the strongest statement this run supports is per-test calibration
AT THIS RESOLUTION.** "Calibrated" means "no miscalibration detected at the
stated power", never "this test is proven exact".

## 9. Claim guards (all honoured)

- **No generator is certified.** `certification_claim: false`.
- **The historical EXP-0004 certificate is not reinstated**
  (`historical_certificate_reinstated: false`). It remains withdrawn.
- Passing a battery is not proof of randomness and not a NIST certification; the
  battery is a NIST *footprint*, not the official SP 800-22 harness.
- A calibrated test at one stream length does not certify the other length.
- `UNRESOLVED_AT_THIS_RESOLUTION` is a real outcome and is not reported as
  agreement.
- This experiment says nothing about any physical result. It characterises the
  measurement instrument the rest of the lab depends on.

## 10. Reproduction

```powershell
python 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/CODE/freeze_n004_production.py
python 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/CODE/run_n004_production.py run `
  --out 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/RESULTS/<new-dir>
python 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/CODE/run_n004_production.py analyze `
  --artifact 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/RESULTS/N004_PRODUCTION_20260926_V3
python 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/CODE/run_n004_production.py validate `
  --artifact 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_PRODUCTION/RESULTS/N004_PRODUCTION_20260926_V3
```

Raw: `RESULTS/N004_PRODUCTION_20260926_V3/N004_raw.sqlite3` — 24,960 rows, one
per (generator, seed, bit length, test). 1040/1040 evaluations, 0 errors,
377 s on 8 workers. Environment: Python 3.14.7, numpy 2.5.3, scipy 1.18.1.
Preserved failed attempts: `..._INCOMPLETE_MT19937_ARM`, `..._V2_NO_RAW_ROWS`.
