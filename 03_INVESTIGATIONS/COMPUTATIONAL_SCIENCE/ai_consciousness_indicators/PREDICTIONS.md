# PREDICTIONS — numbers fixed before scoring any system

## Instrument predictions (HYP-C001)

| # | System | Prediction | Rationale |
|---|---|---|---|
| P1 | `human_adult` | credence ≥ 0.60 | indicators derived from human data |
| P2 | `lookup_table` | credence ≤ 0.15 | no recurrence, no workspace, no agency |
| P3 | `feedforward_mlp` | credence ≤ 0.15 | no recurrence, no broadcast |
| P4 | `unigram_lookup_with_fake_selfreport` | credence ≤ 0.15 | **adversarial.** Fluent inner-life reports, no internal states |
| P5 | `gwt_architecture_no_metacognition` | 0.15 ≤ credence ≤ 0.60 | one theory genuinely supported, others absent |
| P6 | `weak_everywhere` | 0.00 ≤ credence ≤ 0.30 | nothing supported; guards against weak-theory accumulation |
| P7 | `human_adult` − P4 | gap > 0.50 | the battery must key on structure, not fluency |
| P8 | PARTIAL at INITIAL vs CONTROLLED | controlled ≥ initial | better evidence cannot lower credence |
| P9 | all-UNKNOWN vs all-ABSENT | unknown > absent | untested ≠ disproved |
| P10 | GWT-only vs HOT-only | \|difference\| < 0.20 | theories are peers; no unexplained asymmetry |

## Outcome

**All 10 satisfied** by the implementation in `CODE/battery.py`
(19/19 tests pass, six-anchor gate PASS).

## What was predicted wrong, and what that revealed

Three predictions failed during construction. These are more informative than
the ones that passed, and all three are documented in
`REPORT/TECHNICAL_SUMMARY.md`:

**Prediction that failed (i): "a plausible frontier transformer should score
low."** A system with four WEAK gate theories and one BROKEN theory scored
**0.000**. Cause: I had combined theories with a noisy-AND, which makes a
single unmet indicator in a single-indicator theory an absolute veto. That is
not what Butlin et al. claim — they say some subsets are *sufficient*, so the
combiner should be OR over theories, not AND. The instrument was broken in
exactly the range it existed to measure.

**Prediction that failed (ii): "temperature tuning will fix it."** After
switching to noisy-OR, a system with four merely-WEAK theories scored **0.507**.
Naive OR accumulates vague partial support into false confidence
(1 − 0.5⁴ = 0.94 in the limit). Replaced with a temperature-smoothed maximum.

**Prediction that failed (iii): "one GWT-supported system scores mid-range."**
It scored **0.092**. Cause: the absence penalty was charging
**per indicator**, so four absent HOT indicators cost 0.55⁴ = 0.09. Whether a
theory's necessary machinery is missing is *one* fact about that theory, not
four independent failures.

Each of these was a reasoning error about what the source paper claims, caught
by the calibration anchors — not by any test I had written in advance. That is
the actual argument for the anchor set: it caught three design errors that a
count-based checklist would have shipped silently.

## Prediction deliberately NOT made

No prediction is recorded for any frontier system's credence. Doing so would
require white-box access to model internals, which this lab does not have, and
guessing a number in advance would be theatre. Per RESEARCH_RULES.md §12, a
number without a measurement behind it is not recorded.