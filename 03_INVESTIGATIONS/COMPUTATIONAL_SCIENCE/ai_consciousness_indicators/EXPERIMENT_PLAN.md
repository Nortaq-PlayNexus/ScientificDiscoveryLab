# EXPERIMENT_PLAN — EXP-C001

## Scope

Build and validate a scoring instrument. **No frontier system is scored in this
experiment.** Scoring a real model requires white-box access to internals that
this lab does not have, and publishing a number without a measurement behind it
would violate RESEARCH_RULES.md §12.

## Phase 1 — Instrument construction

1. Transcribe the 14 indicators from Butlin et al. (2023) Table 1 verbatim, with
   per-indicator priors `p_given_conscious` and `p_given_not_conscious`.
2. Classify each indicator: necessary-in-theory, gating (necessary AND
   conjunctive), contributory.
3. Implement two-stage aggregation: within-theory collapse, then across theories.
4. Implement evidence grading: UNTESTED → EXTERNALLY_VALIDATED, sub-linear.

## Phase 2 — Calibration (the gate)

Run `calibrate_known_answers()` over six reference systems. **Gate: all six must
pass before Phase 3 is permitted.**

## Phase 3 — Falsification

Execute F1–F6 (`HYPOTHESIS.md`) as executable assertions.

## Phase 4 — Sensitivity

`bootstrap_stability` with adversarial fill of untested indicators.

## Frozen decision rules

Fixed before execution:

- `alpha = 0.01` (lab default, RESEARCH_RULES §6)
- Calibration band for `human_adult`: >= 0.60
- Calibration ceiling for negative anchors: <= 0.15
- Calibration band for intermediate anchors: 0.15-0.60 and 0.00-0.30
- `_NECESSARY_ABSENCE_FACTOR = 0.55`
- `_NECESSITY_ABSENCE_PENALTY = 1.5`
- `_SOFT_OR_TEMPERATURE = 0.10` — **selected by sweep against the anchors; see
  F01. Recorded here as a known circularity, not hidden.**

## Result

Phases 1-4 complete. Calibration PASS. 19/19 tests pass.
Result hash and full output in `RESULTS/`.

## What would come next

- **EXP-C002:** score a specific open-weights model with Jacobian-lens J-space
  measurements feeding GWT-2/3/4. Requires `torch` + `transformers` + the
  `anthropics/jacobian-lens` repo. Not run here: no GPU verified, and the
  repository is a single-commit reference implementation explicitly marked
  "not maintained and not accepting contributions."
- **EXP-C003:** sensitivity of scores to alternative indicator weights, using
  Dirichlet perturbation instead of a single hand-chosen temperature.

## Explicit non-goals

- Not testing whether the authors of a system are conscious.
- Not a Turing test. The framework rejects that route explicitly.
- Not computing Phi/IIT. Excluded by the source framework and independently
  contested.
- Not producing a moral conclusion about any system.