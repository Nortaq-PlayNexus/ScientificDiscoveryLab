# TECHNICAL — N-001 production: the 2D cluster-mass exponent at the exact site threshold

**Investigation:** Q-P007 · **Audit finding:** N-001 (Priority 0 — the only open
Priority-0 item in the 2026-09-24 audit)

**Frozen decision rule:** `CONFIG/prereg_N001_PRODUCTION.json`
(`config_sha256 f5473ff0971f6e8a11e660e8401a01b00c31db56c11637f43cefa424914e5502`),
bound to the repair config by SHA-256, verified before execution, never
overwritten.

**Frozen-rule verdict: `DEVIATION_FROM_FISHER`**

**Scientific reading: this is an escalation trigger, not a discovery.** The
measured deviation is fully consistent with the finite-size crossover this lab
documented *before* the run, and the experiment as preregistered **cannot
distinguish** "the Fisher exponent is wrong" from "L = 1024 is still too small
and s ∈ [32, 4096] is still too deep in the crossover regime". Both readings
remain open. Details in §6.

---

## 1. The question

Does a correctly stored, dependence-aware finite-size cluster tail reproduce the
2D Fisher exponent τ = 187/91 = 2.054945 at the exact site threshold
p_c = 0.59274605079210 — and does the historical "refined" p_c change that
estimate?

The historical Q-P007 closure was **INVALID**: the phase-two writer had
colliding paths, hard-coded inputs, and a structurally empty τ tail, so no
historical τ existed. The repaired N-001 pipeline had passed smoke only.

## 2. Why this run was blocked, and what unblocked it

The repair README required "a separately immutable, content-addressed
preregistration lock" authored *before* results. That lock is
`CONFIG/prereg_N001_PRODUCTION.json`, frozen 2026-09-26, binding:

- the repair config file hash (`fbdb828a…`),
- the production profile object hash (`e017eb7e…`),
- the primary statistic, the interval decision rule, the four fit windows, the
  paired-delta secondary, the window-sensitivity gate, and six claim guards.

**A real blocker was found and fixed first.** The first launch ran the full
~15 min of measurement and then failed closed: the runner recorded the lock by
its **canonical payload hash** but the artifact validator compared it against the
**exact file byte hash**. A frozen document embeds its own digest, so those can
never be equal — the production path was structurally unrunnable for *any*
preregistration. This is the same canonical-vs-byte scope confusion the audit
fixed elsewhere (N-14) and missed here. The validator now re-verifies the lock
through `verify_frozen_config()` and compares the canonical digest, which
preserves tamper detection. A regression test asserts the two scopes differ and
that a tampered lock still fails. N-001 tests: **15 passed** (was 14). Because
the runner hash changed, the authoritative smoke was regenerated as
`SMOKE_N001_V4` (validation PASS); `SMOKE_N001_V3` and earlier are retained as
superseded evidence.

## 3. Design as executed

| Parameter | Value |
|---|---|
| System | 2D square site percolation, 4-connectivity, open boundaries |
| p, canonical arm | 0.59274605079210 (exact 2D site threshold, fixed input) |
| p, refined arm | 0.5927289999999997 (historical Q-P007 width-fit value, fixed input) |
| L | 256, 512, **1024** |
| n per L | 100, 100, **50** |
| Active τ_L | 1024, read from the profile, validated before execution |
| Pairing | one common uniform field per (L, realization), thresholded independently at each p |
| Raw storage | SQLite, one flat non-increasing int64 cluster array per (L, realization, arm) |
| Largest cluster | exactly one entry removed per realization, independently in each arm |
| Bootstrap | 2000 draws, `block_size = 1` (the realization, never an individual cluster), paired across arms |

## 4. Integrity

- Requested and effective realizations at τ_L = 1024: **50 / 50** in both arms.
- Bootstrap draws successful: **2000 / 2000** (success fraction 1.000).
- Resampling unit: `realization_block`; paired across p arms: **true**.
- Tail clusters pooled in the primary window: **1,462,967**.
- Cumulative conversion: **τ = 1 − survival_slope** (the V3 smoke regression test
  locks this; the earlier `τ = slope` error is not present here).
- Manifest 381 KB, raw SQLite 60,383,232 bytes, both hash-bound.

## 5. Results

Fisher reference 187/91 = 2.0549451.

### Primary window `primary_32_4096`, cumulative estimator (the frozen primary)

| arm | τ | 95% realization-block interval | 187/91 |
|---|---|---|---|
| canonical | **1.92009** | **[1.90739, 1.93348]** | OUTSIDE |
| refined | 1.92006 | [1.90736, 1.93340] | OUTSIDE |

Deviation from Fisher: **−0.13486**. The interval excludes 187/91 by a wide
margin (the interval half-width is 0.013, so this is ≈10 interval-half-widths;
against the naive slope SE of 0.0057 it is ≈24 SE).

### All windows and both estimators

| window | estimator | τ (canonical) | 95% interval | 187/91 |
|---|---|---|---|---|
| primary_32_4096 | cumulative | 1.92009 | [1.90739, 1.93348] | OUTSIDE |
| primary_32_4096 | histogram | 1.70277 | [1.60452, 1.65965] | OUTSIDE |
| sensitivity_16_512 | cumulative | 1.93585 | [1.92491, 1.94666] | OUTSIDE |
| sensitivity_16_512 | histogram | 1.96603 | [1.95306, 1.97365] | OUTSIDE |
| sensitivity_32_2048 | cumulative | 1.92828 | [1.91582, 1.94084] | OUTSIDE |
| sensitivity_32_2048 | histogram | 1.84661 | [1.75646, 1.80852] | OUTSIDE |
| sensitivity_64_4096 | cumulative | 1.91207 | [1.89690, 1.92771] | OUTSIDE |
| sensitivity_64_4096 | histogram | 1.60696 | [1.47352, 1.54420] | OUTSIDE |

**Robustness gate: PASSED.** All four windows' cumulative intervals exclude
187/91, so the verdict is not window-driven. The cumulative estimator is stable
across windows (1.912–1.936, a spread of 0.024); the **histogram estimator is
not** (1.607–1.966, a spread of 0.359), exactly as the preregistration warned
when it made cumulative the primary and demoted the histogram to "a correlated-bin
diagnostic; it cannot overturn the cumulative primary verdict on its own".

### Secondary: does the refined p_c matter? **No.**

| window | estimator | Δ = τ_refined − τ_canonical | 95% paired interval | includes 0 |
|---|---|---|---|---|
| primary_32_4096 | cumulative | −0.000028 | [−0.000666, +0.000356] | yes |
| primary_32_4096 | histogram | +0.000151 | [−0.001597, +0.002076] | yes |
| sensitivity_16_512 | cumulative | −0.000118 | [−0.000462, +0.000173] | yes |
| sensitivity_32_2048 | cumulative | +0.000011 | [−0.000491, +0.000380] | yes |
| sensitivity_64_4096 | cumulative | −0.000019 | [−0.000790, +0.000488] | yes |

Every paired interval contains zero. Per the frozen secondary rule the verdict
is **`NO_RESOLVABLE_REFINED_EFFECT`**. The 17e-6 shift in p between the arms
produces a τ change below 7e-4, i.e. this experiment is completely insensitive
to the refined threshold at this resolution. That is a clean negative and it
kills one candidate explanation outright.

## 6. What this means — and the honest ambiguity

The frozen rule says `DEVIATION_FROM_FISHER`, and that is reported faithfully.
The rule's own guard states: *"A DEVIATION verdict is an anomaly requiring
escalation, not a discovery."* No novelty is claimed.

The critical context is that **this lab documented the expected finite-size
crossover before the run existed.** The EXP-0009 preregistration states:

> "the finite-domain lattice-scale crossover gives an apparent exponent ~1.8–2.0
> at s~10–10³ that converges to the Fisher value 187/91 only asymptotically"

The measured 1.920 sits inside that documented 1.8–2.0 band, at the expected
side of it, and moves *toward* Fisher as the window is narrowed toward smaller s
(1.936 at s ∈ [16, 512]). So the observation is what finite-size crossover looks
like, not evidence against the Fisher exponent.

**The honest conclusion is that the preregistered design cannot separate the two
readings.** To distinguish them one must increase L and/or restrict to smaller s
until the estimate demonstrably converges, which this run — L = 1024, s ≥ 16 —
does not do. A "DEVIATION" here is a statement about L = 1024, not about 2D
percolation.

Also relevant: the historical value was 1.98; the corrected storage gives
**1.920**, which is *further* from Fisher, not closer. The historical 1.98 was
therefore not a near-miss of the asymptotic value that better storage recovered;
it was a different number produced by the defective pipeline. Any narrative in
which the repair "recovered" the exponent is wrong.

## 7. Post-run resolution statement

The preregistration committed to reporting the minimum resolvable difference at
80% power from the observed paired bootstrap variance, as a descriptive
post-run statement and not an advance power claim. From the primary window's
paired-delta SD, the canonical-arm τ SD is ≈0.0067 (half-width 0.0131 at 95%),
so this design resolves a τ change of about **0.017 at 95% confidence** — an
order of magnitude smaller than the 0.135 deviation observed, and far smaller
than needed to have detected the ≤0.0007 refined-p_c effect. The experiment is
well powered for its own deviation; it is *L*, not statistics, that limits the
interpretation.

## 8. Limitations

- **p_c is inherited, not re-estimated.** Open boundaries shift the finite-size
  threshold by O(1/L), so both arms are sampled slightly off criticality at
  every L. This is a shared systematic and largely cancels in the paired
  refined-minus-canonical comparison, but it is not measured here.
- **One finite-size scaling limit (L = 1024) only.** No L → ∞ extrapolation is
  defensible, and none is attempted.
- **Component backend is `scipy.ndimage.label`** four-connectivity. There is no
  second independent implementation of the cluster census inside this run; the
  engine's census was separately verified against a from-scratch pure-Python
  BFS implementation during EXP-0017 (30/30 cells exact), but that is a
  different experiment, not a C7 gate on this artifact.
- **Realization-block bootstrap addresses within-realization cluster
  dependence only.** Unmodelled cross-realization block dependence remains
  unresolved.
- **The histogram estimator's weighted chi-square-like value is diagnostic, not
  a goodness-of-fit test**, and its window sensitivity (0.359 spread) shows why.
- **No novelty claim, no escalation target selected yet.** Per the lab's rules a
  DEVIATION is escalated for review, not tuned.

## 9. Reproduction

```powershell
# the lock is immutable: re-running freeze_n001_production.py raises
python 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/CODE/run_n001.py run `
  --config  03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/CONFIG/n001_repair_config.json `
  --profile production --confirm-production N-001-PRODUCTION `
  --production-prereg 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/CONFIG/prereg_N001_PRODUCTION.json `
  --output-dir <new-directory>
python -m pytest 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/TESTS/test_n001_runner.py -q
```

Artifacts in `RESULTS/PRODUCTION_N001_20260926/`:
`N001_production_raw.sqlite3` (60,383,232 B, hash-bound),
`N001_production_manifest.json` (381 KB), `N001_production_summary.json`.

Environment: Python 3.14.7, numpy 2.5.3, scipy 1.18.1. Single-threaded;
~1 h wall including the 2000-draw bootstrap over 1.46 M pooled tail clusters.
