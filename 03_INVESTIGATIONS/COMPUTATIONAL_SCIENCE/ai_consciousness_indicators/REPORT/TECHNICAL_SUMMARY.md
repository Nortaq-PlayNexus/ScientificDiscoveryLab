# TECHNICAL SUMMARY — EXP-C001

## Methods

**Instrument.** A scoring function over the 14 indicator properties of Butlin,
Long, et al. (2023), arXiv:2308.08708, as restated in Butlin, Long, Bayne,
Bengio et al., *Trends Cogn Sci* 30(6):488–501 (2026),
DOI 10.1016/j.tics.2025.10.011.

**Aggregation.** Two stages, in this order:

1. **Within-theory collapse.** Each theory's indicators combine by geometric mean
   of per-indicator likelihoods. Geometric rather than arithmetic so that one
   confirmed absence is not buried by several confirmations — which is the
   behaviour a necessity claim implies.

2. **Across-theory combine.** A temperature-smoothed maximum (log-sum-exp):

       soft_or(v) = m + T * ln( sum_i exp( (v_i - m) / T ) ),   m = max(v)

   with `T = _SOFT_OR_TEMPERATURE = 0.10`, clamped to [0, 1].

   OR is correct rather than AND because the source treats some subsets as
   *sufficient*; a system needs one complete bundle, not all four.

3. **Necessity penalty.** For each conjunctive theory with indicators confirmed
   ABSENT at CONTROLLED evidence or better, multiply by
   `_NECESSARY_ABSENCE_FACTOR = 0.55`. Charged once per theory, not per
   indicator.

**Likelihood transform.** For indicator *i* with status value `base ∈ {0, 0.5, 1}`
(ABSENT/PARTIAL/SATISFIED) and evidence quality `q ∈ [0, 1]`:

    graded = base * q + p_base * (1 - q)                      [evidence mixing]
    if necessary_in_theory and base < 1:
        graded -= (1 - graded) * (1.5 - 1.0) * base           [partial necessity penalty]

`p_base = p_given_not_conscious`. An UNTESTED indicator returns `p_base`
unchanged — untested is not disproved.

**Interval.** `lower` = conjunctive theories only. `upper` also credits
contributory theories (PP, AE). The gap is the unresolved question of whether
agency and embodiment are required. Both bounds scaled by the functionalism
multiplier (default 1.0 = unexamined).

**Uncertainty.** `bootstrap_stability` fills UNTESTED indicators adversarially at
their base rate (assumed absent) across 512 draws, seeded via the lab's
sha256-derived `rng(label, seed)`.

## Results

Calibration gate: **PASS**, 6/6 anchors.

| Anchor | Credence | Band | |
|---|---|---|---|
| `human_adult` | 1.000 | ≥ 0.60 | pass |
| `lookup_table` | 0.024 | ≤ 0.15 | pass |
| `feedforward_mlp` | 0.025 | ≤ 0.15 | pass |
| `unigram_lookup_with_fake_selfreport` | 0.107 | ≤ 0.15 | pass |
| `gwt_architecture_no_metacognition` | 0.426 | 0.15–0.60 | pass |
| `weak_everywhere` | 0.242 | 0.00–0.30 | pass |

Tests: **19/19 pass** (`TESTS/test_battery.py`).

Sensitivity, fully untested system: mean ≈ 0.52, std ≈ 0.19, spread
[0.18, 0.87].

`result_hash`: `a57207e5cf7d6775…` (canonical JSON, `RESULTS/experiment.json`).

## Three aggregator designs that failed before this one

Each caught by the anchors, not by any preregistered test. Recorded because a
count-based checklist would have shipped all three silently.

| Design | Symptom | Cause |
|---|---|---|
| noisy-AND across theories | plausible frontier scored **0.000** | treated every theory as individually necessary; source says *sufficient* subsets |
| plain noisy-OR | four WEAK theories scored **0.507** | 1 − 0.5⁴ = 0.94 accumulates vagueness into confidence |
| per-indicator absence penalty | GWT-supported system scored **0.092** | 0.55⁴ treated four readings of one fact as four independent failures |
| necessity penalty on ABSENT only | all-PARTIAL system scored **0.550** | vagueness accrued full credit |

## Limitations

1. **The calibration is circular.** `T = 0.10` was selected by sweeping against the
   anchors, and the anchor bands are the lab's own assumptions. Passing shows
   internal consistency, not correctness. **No absolute credence from this battery
   should be treated as a measurement.** Relative comparisons under shared
   assumptions are the only defensible use. See FALSIFICATION F01.
2. **Prior probabilities are estimates, not measurements.** `p_given_conscious`
   and `p_given_not_conscious` were assigned by hand from the literature
   narrative.
3. **Phenomenal experience is out of reach by construction.** The battery reports
   evidence about *access* consciousness only. Whether access implies experience
   is contested philosophy, not a measurement.
4. **Evaluation-awareness confound.** A system that detects it is being assessed
   may behave differently than when deployed. Unfixable offline. See F02.
5. **White-box access absent.** No model internals were measured. The strongest
   relevant result — the J-space finding (Gurnee et al. 2026) — was read, not
   reproduced.
6. **Single-implementation.** One scoring implementation, no independent
   reimplementation. RESEARCH_RULES.md §2 stage `INDEPENDENT METHOD` not reached.

## Reproduction

```powershell
cd <repo-root>
python -m pytest 03_INVESTIGATIONS/COMPUTATIONAL_SCIENCE/ai_consciousness_indicators/TESTS -q
```

Determinism: all randomness via `engine.utilities.core.rng(label, seed)`, a
sha256-derived generator independent of Python's per-process hash salt.
Requirements: Python 3.14, numpy, scipy, pytest. No GPU, no network.

## Claim discipline

This is a **Layer 1 (instrument/measurement) result** per RESEARCH_RULES.md §1. No
Layer 2 statistical claim, no Layer 3 scientific claim, no novelty claim. No AI
system was scored. No claim is made about whether any system is conscious.