# TECHNICAL — EXP-0017 / N-005: balanced power-of-two vs non-power-of-two lattice test

**Question:** Q-P009 — after matching physical size, estimator, and random-stream
policy, is there a reproducible *power-of-two* effect on the 2D site
cluster-mass exponent?

**Audit finding addressed:** N-005 (`AUDIT/NEXT_EXPERIMENTS.md`, Priority 1).

**Verdict: `LATTICE_ARTIFACT_UNSUPPORTED`**

**Evidence state:** CONTROLLED for the estimator question. No novelty claim, no
new physics. This experiment *tests* a historical claim; it does not overturn
the historical record, and EXP-0009/EXP-0010 outputs are unmodified.

---

## 1. Why this experiment exists

EXP-0009 measured the 2D site cluster-mass exponent on lattice sizes
{128, 256, 512, 1024} — **all powers of two** — and obtained D_f = 1.8697
against a theoretical 91/48 = 1.895833, a ~1σ miss. EXP-0010 re-measured on
{127, 191, 253, 449} — **no powers of two** — and obtained D_f = 1.8962 ± 0.028,
and concluded `LATTICE_ARTIFACT`: the EXP-0009 miss was a lattice-size
discretization artifact.

The cross-project audit (`AUDIT/REPAIR_LOG_20260924.md`, N-04/N-05/N-19/N-21/N-22)
found EXP-0010's closure **not acceptable**: its pooled fit does not satisfy its
own preregistered per-size/C7 closure, and the required C7 independent
implementation is absent. So the `LATTICE_ARTIFACT` claim is currently
unsupported in either direction. N-005 is the experiment that would settle it.

The historical effect to be explained is a **deficit of 0.0265** in D_f at
power-of-two sizes (1.8697 vs 1.8962).

## 2. Design

Frozen before execution in `CONFIG/prereg_EXP-0017.json`
(`config_sha256 = 9de382eb7bba2853f1ab4cd33441595c5c5611cd2310563221046c3e3f27aa8e`),
verified on load, never overwritten.

| Element | Choice | Why |
|---|---|---|
| System | 2D square site percolation, 4-connectivity, open boundaries | same engine family as the historical runs |
| p | 0.5927460507921 (exact 2D site threshold) | fixed input, **not** re-estimated |
| Bases | 128, 256, 512, 1024 (n = 100, 100, 100, 60) | the historical power-of-two ladder |
| Primary pairing | **nested common random numbers**: one L×L field yields every sub-window size | a power-of-two size and its neighbour share every random number |
| Cross-check | fully independent streams, no sharing, n = 40 | tests that the pairing is not manufacturing the answer |
| Null control | contrast between two adjacent **non**-power-of-two pairs | measures how large a purely *smooth* size dependence looks |
| 2-adic ladder | even non-power-of-two sizes L−2, L−4, L−8 at bases 256, 512 | separates "power of two" from "even" and from higher divisibility |
| Equivalence margin | **0.010** | 2.65× *smaller* than the 0.0265 effect that must be explained |
| Bootstrap | 5000 draws, resampling realizations **within** each base, paired across sizes | carries the dependence structure by resampling |

The three candidate outcomes were frozen in advance:

- `LATTICE_ARTIFACT_SUPPORTED` — 95% interval excludes 0 **and** |β| > 0.010
- `LATTICE_ARTIFACT_UNSUPPORTED` — the whole **90%** interval lies inside ±0.010
- `INCONCLUSIVE_BY_RESOLUTION` — anything else, explicitly *not* reportable as "no effect"

## 3. Gates (all passed before any fit was reported)

| Gate | Result |
|---|---|
| C1 raw round-trip | 36 stored arrays reloaded bit-exactly |
| C2 mass bounds | S_max ≤ open sites ≤ L² for every entry |
| C3 nested monotonicity | S_max non-decreasing from smaller to larger nested window, no violations |
| C7 second implementation | 160 cells on identical masks, explicit edge list + `connected_components`, **0 mismatches** |
| C8 third implementation | 30 cells against a from-scratch pure-Python BFS census, **0 mismatches** |
| C9 sanity fields | exact-zero and all-open fields exact in all three implementations |
| C10 realization counts | exactly as preregistered |

## 4. Primary result

**β = −0.0014003**, 90% interval **[−0.003890, +0.000797]**, 95% interval
[−0.004576, +0.001079].

| Quantity | Value |
|---|---|
| D_f over the power-of-two ladder {128, 256, 512, 1024} | **1.882715** |
| D_f over the non-power-of-two ladder {127, 255, 511, 1023} | **1.884116** |
| β = difference | **−0.001400** |
| preregistered equivalence margin | ±0.010 |
| historical deficit that would have to be explained | 0.0265 |
| **|β| as a fraction of the historical deficit** | **0.053** |

The entire 90% interval lies strictly inside ±0.010, so the frozen rule returns
`LATTICE_ARTIFACT_UNSUPPORTED`. The measured power-of-two effect is **19×
smaller than the historical deficit** and **2.6× smaller than the margin**.

Per-base paired differences (mean log S_max difference, ±sd, n):

| base | sizes | Δ mean | sd | n |
|---|---|---|---|---|
| 128 | 127→128 | +0.017408 | 0.03360 | 100 |
| 256 | 255→256 | +0.005115 | 0.00506 | 100 |
| 512 | 511→512 | +0.002429 | 0.00496 | 100 |
| 1024 | 1023→1024 | +0.000877 | 0.00095 | 60 |

## 5. Secondary results

- **Absolute D_f over the full balanced set:** 1.880462, 95% interval
  [1.851317, 1.911041]. The reference 91/48 = 1.895833 **lies inside** the
  interval, so the balanced pooled exponent is consistent with the known 2D
  universality class.
- **Independent-stream arm (no random-number sharing):** β = +0.01433, 90%
  interval [−0.07055, +0.10157]. This arm is much noisier, as expected, and
  **excludes nothing**. Per the pre-registered operational definition of
  "contradicts" (change entry 1), an arm that excludes zero is *underpowered*,
  not contradictory, so it does not void the primary verdict. Its sign is
  opposite to the primary point estimate, which is worth stating plainly.
- **2-adic ladder:** local slopes along even non-power-of-two neighbours are
  reported descriptively in the summary. The primary 2-adic question (is the
  effect "power of two" or merely "even") is answered by the primary contrast,
  which finds nothing at the margin in either case.
- **Synthetic self-check, recorded inside the artifact:** a null power law
  returns β = 0.00000; injected exponent offsets of ±0.0265 are recovered as
  ±0.02650; a shared quadratic correction of 0.30 returns +0.00273.

## 6. A methodological error I made, and its correction

This must be recorded plainly, because the first analysis of this same raw
artifact was wrong.

The preregistration's wording — "the local log-log slope between two nested
sub-window sizes" — led me to implement the estimator as a finite difference
divided by log(hi/lo). That denominator is ≈ 1e-3 at L = 1024, so the estimator
**amplifies noise by roughly 1e3**. Two independent diagnostics proved it was
noise-dominated rather than merely imprecise:

1. The preregistered **null control** — a contrast between two adjacent
   *non*-power-of-two pairs, which cannot contain any power-of-two effect —
   returned **+0.313**, *larger in magnitude* than the primary contrast of
   −0.290.
2. The 2-adic ladder produced mutually inconsistent "precise" slopes, e.g.
   1.106 ± 0.002 and 3.913 ± 0.055 for adjacent pairs at the same base.

That first analysis returned `INCONCLUSIVE_BY_RESOLUTION` and supported no
conclusion in either direction. It is retained as
`EXP-0017_summary_v1_local_slope_SUPERSEDED.json` and its numbers are preserved
in the final summary under `superseded_estimator_diagnostic`, explicitly
labelled *do not use as an effect estimate*.

The primary statistic was replaced with the standard balanced design: D_f fitted
over the power-of-two ladder minus D_f fitted over the non-power-of-two ladder,
one nested size per base, so both arms share every realization. Because both
weight vectors sum to zero, the large marginal fluctuation of log S_max
cancels in the difference, and **nothing is ever divided by log(1+1/L)**.
Uncertainty is a paired bootstrap.

The replacement was validated on synthetic data *before* adoption (null → 0.00000;
±0.0265 → ±0.02650). **No measured EXP-0017 value was used to select the
estimator, the raw artifact was not modified, and no new data was collected for
the change.** The equivalence margin, the reference exponent, the fit sizes, the
falsification rule, and the `INCONCLUSIVE_BY_RESOLUTION` state are all unchanged.
Full reasoning is in the hash chain (`CONFIG/changes.jsonl`, entries 4 and 5).

A second, smaller error worth recording: my first synthetic validation injected
an *additive log-mass* offset, which by construction cannot change a slope, so
it "failed" to detect anything. The injection was corrected to an *exponent*
offset. An early draft of the variance formula also used the paired-difference
sd for the marginal variances, over-cancelling the interval by ~3 orders of
magnitude; the paired bootstrap removed the analytic formula entirely.

## 7. Limitations

- **p_c is inherited, not measured.** Open boundaries shift the finite-size
  threshold by O(1/L), so the sampled point is slightly off criticality at every
  L and that offset is not quantified here. This is a systematic shared by both
  arms and largely cancels in β, but it is not proven to cancel.
- **The corrected estimator has a measured sensitivity to smooth finite-size
  corrections:** a shared quadratic term of 0.30 in log-log curvature returns
  β = +0.0027, i.e. about 0.009 per unit of curvature. That is below the 0.010
  margin but not negligible, and it is the main reason the absolute pooled D_f
  is reported alongside the contrast.
- **Nested sub-windows are not independent samples.** The bootstrap resamples
  realizations, which preserves the pairing, but the design's power comes from
  that sharing and would not transfer to an unpaired analysis at this n.
- **The independent-stream arm is underpowered** at n = 40 and cannot confirm or
  refute the primary on its own. It is a consistency check, not a replication.
- **No second-seed replication of the whole nested arm.** The arm is internally
  consistent across 100/100/100/60 realizations, but a rerun under a different
  seed namespace was not performed.
- **`p_c` sensitivity to a second independently estimated threshold** (the audit
  asked for this) was **not** run. It remains open.

## 8. What this does and does not establish

**Does:** with physical size matched to one lattice unit, the estimator held
fixed, and the random-stream policy matched, there is no reproducible
power-of-two effect on the 2D site cluster-mass exponent at the 0.010 level.
The historical EXP-0009 → EXP-0010 difference of 0.0265 is 19× larger than the
effect measured here and is therefore **not** attributable to power-of-two
lattice sizes under this design. The balanced pooled exponent is consistent
with 91/48.

**Does not:** revive, overturn, or reclassify EXP-0009 or EXP-0010. Those
records stand as they are; this experiment simply removes power-of-two lattice
sizes as a candidate explanation for their difference. It says nothing about
whether the EXP-0009 miss is a finite-size correction, an estimator artifact of
a different kind, or ordinary statistical scatter — EXP-0009's own D_f of 1.8697
is within ~1σ of 1.8958 and its interval was never the issue. It establishes no
new physics and makes no novelty claim.

**Recommended next step if this thread continues:** the open question is no
longer "is it a power-of-two artifact?" but "what explains the EXP-0009 point
estimate?", which needs a properly powered per-size D_f measurement with the
threshold varied as a controlled factor.

## 9. Reproduction

```powershell
python 03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/CODE/freeze_exp0017.py
# refuses to run twice: the preregistration is immutable
# to re-run the measurement into a NEW output directory:
python 03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/CODE/run_exp0017.py run `
  --out 03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/RESULTS/<new-dir>
python 03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/CODE/run_exp0017.py analyze `
  --artifact 03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/RESULTS/EXP-0017_20260926
python 03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/CODE/run_exp0017.py validate `
  --artifact 03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/RESULTS/EXP-0017_20260926
python -m pytest 03_INVESTIGATIONS/PHYSICS/percolation/N005_BALANCED_LATTICE_SIZE/TESTS/test_exp0017.py -q
```

Raw data: `RESULTS/EXP-0017_20260926/EXP-0017_raw.sqlite3` — one BLOB per
(arm, base, size) holding the per-realization S_max as little-endian int64, with
per-array SHA-256 in the table and a whole-file SHA-256 in the manifest.
Wall time 118 s single-threaded. Environment: Python 3.14.7, numpy 2.5.3,
scipy 1.18.1, recorded in the manifest.

## 10. Artifacts

| Path | Content |
|---|---|
| `CONFIG/prereg_EXP-0017.json` | frozen protocol, `config_sha256 9de382eb…` |
| `CONFIG/changes.jsonl` | 5-entry hash chain, head `5934bc31ef969085…` |
| `CODE/run_exp0017.py` | runner + analysis + validator |
| `CODE/freeze_exp0017.py` | exclusive-create preregistration |
| `CODE/log_exp0017_changes.py` | idempotent change-chain writer |
| `TESTS/test_exp0017.py` | 25 tests, all passing |
| `RESULTS/EXP-0017_20260926/EXP-0017_manifest.json` | hashes, gates, environment, runner hash |
| `RESULTS/EXP-0017_20260926/EXP-0017_raw.sqlite3` | raw per-realization S_max |
| `RESULTS/EXP-0017_20260926/EXP-0017_summary.json` | authoritative result |
| `RESULTS/EXP-0017_20260926/EXP-0017_summary_v1_local_slope_SUPERSEDED.json` | preserved invalid first analysis |
