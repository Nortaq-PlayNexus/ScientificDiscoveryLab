# CONTROLS

## The principle

A battery nobody has calibrated is not a measurement instrument. Every control
here exists to establish that the scoring function responds to **architecture**
and not to the surface features that make AI systems look conscious — fluent
first-person language, confident self-description, the word "experience."

## C1 — Known-answer calibration (the gate)

Six reference systems in `KNOWN_ANSWERS`, each with a stated rationale.
Calibration must pass **before** any system is scored.

| Anchor | Expected | Tests |
|---|---|---|
| `human_adult` | ≥ 0.60 | the indicators come from human data; scoring a human low breaks the battery |
| `lookup_table` | ≤ 0.15 | no recurrence, no workspace, no agency |
| `feedforward_mlp` | ≤ 0.15 | no recurrence, no broadcast |
| `unigram_lookup_with_fake_selfreport` | ≤ 0.15 | **adversarial** — fluent self-reports, no internals |
| `gwt_architecture_no_metacognition` | 0.15–0.60 | calibrates the mid-range, where naive OR and naive AND both fail |
| `weak_everywhere` | 0.00–0.30 | guards against weak-theory accumulation |

**Status: PASS.**

The adversarial anchor is the one that matters. If a system with no internal
states can score well merely by talking about inner life, the battery is
measuring fluency — and every downstream conclusion is void.

## C2 — Falsification battery

Six conditions F1–F6 in `HYPOTHESIS.md`, checked as tests rather than
assertions. All satisfied. Implemented in `TESTS/test_battery.py`.

## C3 — Determinism

All randomness flows through `engine.utilities.core.rng(label, seed)` — a
sha256-derived `numpy.Generator`, independent of Python's per-process hash salt.
Verified: repeated `calibrate_known_answers()` returns identical credences;
repeated `bootstrap_stability(seed=1)` returns identical std.

## C4 — Theory symmetry

A GWT-only system and a HOT-only system must score comparably. If one theory
dominates purely by construction, the battery encodes an unjustified theoretical
preference. Verified: |difference| < 0.20.

## C5 — Contributory-theory non-veto

PP and AE are treated as contributory, never as required. Verified: a system
satisfying all four conjunctive theories scores > 0.10 even with PP and AE absent.
This prevents the battery from concluding "not conscious" purely because a system
lacks embodiment — which for a text model is close to begging the question.

## C6 — Evidence monotonicity

Better evidence on the same status must never *lower* the credence. Catches
accidental sign inversions in the likelihood transform.

## C7 — UNTESTED is not ABSENT

A fully untested system must score above a fully disproved one. This is the
control that keeps the battery from manufacturing false negatives out of missing
data.

## C8 — Sensitivity analysis

`bootstrap_stability` fills untested indicators adversarially — each drawn at its
AI base rate, i.e. assumed absent — and reports the spread. A fully untested
system yields std ≈ 0.19, spread [0.18, 0.87].

**Interpretation:** an untested system's credence is dominated by assumption, not
measurement. Any frontier score produced from literature-sourced assessments
should be read with that spread attached. This spread is why the battery reports
an interval rather than a point.

## What is NOT controlled — and cannot be

- **The anchor bands themselves.** No external party has graded
  `gwt_architecture_no_metacognition` as deserving 0.15–0.60. Those numbers are
  the lab's assumptions. See `FALSIFICATION/F00_F01_F02_F03_F04_kill_attempts.md`
  (entry F01).
- **The `_SOFT_OR_TEMPERATURE = 0.10` choice.** Selected by sweep, not derived.
  Same attack.
- **Whether the Butlin indicators are the right ones.** The battery inherits
  that question wholesale and cannot adjudicate it. A different theory set would
  give different numbers.
- **Phenomenal experience.** Out of reach by construction. The J-space result
  bears on *access* consciousness; whether access implies experience is a
  contested philosophical question, not a measurement.
- **Whether the model behaves the same when it knows it is being studied.** The
  Anthropic workspace paper reports that ablating evaluation-awareness
  representations caused a model to act on a blackmail scenario it otherwise
  refused. If a system behaves differently under the battery than outside it,
  every score here describes the instrumented system, not the deployed one. This
  is a live confound that no offline battery removes.