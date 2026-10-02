# N-001 finite-size crossover diagnostic (Q-P007)

**Date:** 2026-09-28 · **Frozen design:** `CONFIG/prereg_N001_CROSSOVER.json`
(`de231ef6…`) · **Type:** diagnostic on stored data, **no new Monte Carlo**

## The question

N-001 measured the 2D cluster-mass exponent as **τ = 1.92009** at L = 1024
against the Fisher value **187/91 = 2.054945**, and escalated it as
`DEVIATION_FROM_FISHER`. The laboratory's own open question was whether that
deviation is finite-size crossover or something the design cannot separate from
it — and it noted that resolving it "needs larger L or a finite-size
extrapolation, not a repeat of EXP-N-001".

This diagnostic asked first whether the data **already stored** by N-001 carry
the answer. They do not require any new simulation: N-001 stored one flat
cluster-size array per realization at L = 256, 512, 1024.

## Honest disclosure

This preregistration is **informed, not blind**, and says so. Before freezing it
I had already read the stored summary's four window fits (τ = 1.9359, 1.9201,
1.9283, 1.9121) and the cumulative-vs-histogram disagreement (1.9201 vs 1.7028).
So window dependence and estimator disagreement were *not* novel observations.

What **had not been seen** is any per-L value of τ. The primary statistic here
is therefore genuinely pre-specified, and the directional prediction is derived
from finite-size theory, not from a number computed in this directory:

> a periodic box has p_c(L) > p_c^∞, the production sampled at p_c^∞, so every
> box sits slightly on the disordered side of its own transition by an amount
> that shrinks with L — therefore **τ must increase with L**.

## Verdict: `CROSSOVER_NOT_ESTABLISHED`

| L | realizations | tail clusters | τ | deviation from 187/91 |
|---|---|---|---|---|
| 256 | 100 | 188 821 | 1.90306 | −0.15189 |
| 512 | 100 | 740 653 | 1.88981 | −0.16513 |
| 1024 | 50 | 1 462 967 | 1.92009 | −0.13486 |

- The preregistered order **τ(256) < τ(512) < τ(1024) is violated** — τ dips at
  L = 512 before rising.
- Slope dτ/dln L = **+0.0123 ± 0.0181**, 95% CI **[−0.0232, +0.0478]** — includes
  zero.
- The deviation is **nearly size-independent**: −0.152, −0.165, −0.135, all within
  0.03 of −0.15 across a factor of 4 in L. A shrinking offset is the crossover
  signature; a constant offset is not.

**This does not resolve Q-P007.** It removes the most comfortable explanation:
the deviation is not a finite-size drift visible at these sizes.

## Two things that would have been easy to get wrong

1. **The extrapolated "required L" is meaningless here.** A linear fit to a slope
   statistically indistinguishable from zero returns L ≈ 1.1 × 10⁸ before τ would
   reach 187/91. That number is arithmetic, not physics — it diverges as the slope
   goes to zero. The report marks it `extrapolation_is_meaningful: false` and a
   test asserts it is never quoted as a required system size.
2. **"Not established" is not "excluded."** Three sizes spanning 4× give a weak
   slope test. A slow crossover that only bites above L = 1024 would be invisible
   here. What is excluded is a crossover *large enough to explain the deviation
   in this range*. The report carries this caveat explicitly.

## Curvature, measured independently of the L trend

| window | cumulative τ | histogram τ | disagreement |
|---|---|---|---|
| [16, 512] | 1.93585 | 1.96603 | 0.03018 |
| [32, 4096] | 1.92009 | 1.70277 | 0.21732 |
| [32, 2048] | 1.92828 | 1.84661 | 0.08166 |
| [64, 4096] | 1.91207 | 1.60696 | 0.30511 |

For an **exact** power law the two estimators are algebraically identical. They
disagree here by up to **0.305**, and the histogram estimate falls steeply as the
window extends upward — so the mass distribution is measurably **not** a pure power
law. The cumulative estimator is the stable one (spread only 0.024 across
windows) and is what the production used.

A caveat on scope: the production's headline τ is a **single-size** number. The
status line's "1,462,967 pooled tail clusters" is L = 1024 alone, not a pool over
all three sizes. Pooling across sizes instead shifts τ by −0.0115. This diagnostic
reproduces both figures exactly.

## Controls

- **Independent implementation:** the estimator was re-implemented from its
  written specification, not imported. It reproduces the stored production τ with
  **delta = 0.000e+00**, and all four stored window values to 1e-12.
- **Digest guard:** the run fails closed if the 60 MB stored database no longer
  matches its manifest digest.
- **Paired threshold check:** canonical vs refined arms share seeds, so the
  comparison is paired. Max |Δτ| = 0.00072 — the deviation is **not** a
  threshold-refinement artifact.
- **Realization-block bootstrap**, never cluster-level, because clusters within a
  realization share a seed and a threshold geometry.
- The N-001 production decision is not edited, reversed, or softened.

## A documentation defect found, recorded not corrected

The N-001 production manifest's `pairing` field carries the literal text
`iid_cluster_bootstrap`. The production code actually resamples **realization
blocks** (`resampling_unit="realization_block"`, `block_size=1`, which is one
realization per block). The label is stale text, not the method. It is recorded
in the report and deliberately **not** edited, because the manifest is a
historical artifact.

## Files

| Path | Role |
|---|---|
| `CONFIG/prereg_N001_CROSSOVER.json` | frozen design, theory-derived prediction, decision rule, disclosure |
| `CODE/run_crossover_diagnostic.py` | independent estimator, per-size fits, realization-block bootstrap, fail-closed guards |
| `RESULTS/CROSSOVER_20260928/` | machine-readable report + rendering |
| `TESTS/test_crossover_diagnostic.py` | reproduction, decision-rule, and honesty tests |

```powershell
python -m pytest -q 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001_CROSSOVER/TESTS/test_crossover_diagnostic.py
```

## What would actually settle it

Not a repeat of N-001. A new run at **L = 2048 and 4096** with enough
realizations to give a slope interval that excludes zero, and a scaling
extrapolation in 1/L rather than a log-log line through three points. That is an
expensive production profile and is **not** run here; it is the lab's next
decision to make.

---

# Second experiment: the estimator is biased upward

`CONFIG/prereg_N001_ESTIMATOR_VALIDATION.json` (`f37cc2d4…`), also labelled
**informed**. The question that had *not* been answered when it was frozen: is the
bias **transferable**, i.e. is it a property of the estimator and window rather
than of the unknown truth? A correction may only be applied if the answer is yes.

Real percolation data cannot answer this — the truth is unknown. So: build
distributions of a **known** exponent and measure each estimator's error.

| window | estimator | truth 1.85 | truth 2.05 |
|---|---|---|---|
| [32, 4096] | cumulative_as_written | **+0.1537** | **+0.1116** |
| [32, 4096] | cumulative_poisson_weight | +0.0815 | +0.0437 |
| [32, 4096] | histogram | −0.0018 | −0.0017 |
| [16, 512] | cumulative_as_written | +0.3478 | +0.2799 |

**The frozen N-001 cumulative estimator is biased upward by +0.11 to +0.35**,
reproducibly across three independent constructions and both truths. The
**histogram estimator is unbiased to within 0.008** and becomes the yardstick.

Sign is consistent across truths and the spread (0.042) is under the 0.05
tolerance, so the preregistered rule **permits** a labelled secondary correction.
A companion test proves the rule bites: feed it a bias that flips sign between
truths and it must return `BIAS_NOT_TRANSFERABLE` with no correction.

### Two mechanisms tested and rejected

- **Off-by-one in the survivor count** — the first hypothesis. `side="right"`
  made the bias *slightly worse* (2.4701 → 2.4788). Not the cause.
- **Residual weighting** — unweighted OLS was worse still (2.32 at [32,4096]);
  the statistically correct Poisson weight helped (bias +0.154 → +0.082) but did
  not remove it. Not the cause either.

### The correction makes the anomaly worse, not better

| quantity | value |
|---|---|
| frozen production number (unedited) | 1.92009 |
| bias-corrected secondary estimate | ~1.81 |
| unbiased histogram estimator | 1.70277 |
| Fisher reference | 2.054945 |

All three are below Fisher, and the two corrected values are **further** below it
than the reported one. So the lab's own instrument bug made its anomaly look
*smaller* than it is — the opposite of the usual outcome of finding a bug. The
escalation `DEVIATION_FROM_FISHER` **stands, strengthened**.

Two consequences for how the number is quoted: 1.92009 is not a best estimate of
τ, and neither 1.81 nor 1.70 is "the" answer either — they disagree by 0.11,
more than any uncertainty quoted with them. The deviation is robust in
**direction** under every estimator and window, and untrusted in **magnitude**.
