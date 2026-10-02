# CHANGELOG — Q-C001

All entries honest about failures, per RESEARCH_RULES.md §12.

## 2026-10-02 — robustness arm (EXP-C003)

Added `CODE/perturbation.py` and `TESTS/test_perturbation.py`. Perturbs six
discretionary parameter families jointly (3000 draws across a plausible and an
aggressive region) to bound how much F01's arbitrariness actually matters.

**Result.** F-B (fluent-liar anchor never outscores the human) = **1.0000** in
both regions. Exact ordering = 1.0000 plausible / 0.6413 aggressive. Absolute
ceiling fails aggressive (0.7687); adversarial anchor p05–p95 = [0.027, 0.506]
genuinely straddles the 0.30 ceiling.

**Authorises ranking, not absolute probabilities.** Registered as HYP-C001-R at
PARTIALLY_CONFIRMED. Tests 19 → 30, all passing.

**Gate bug F05 (found and fixed).** `EXPECTED_ORDER` omitted `feedforward_mlp`,
so F-A compared a sorted six-element list to a five-element tuple and read
**0.0000** — reporting its own defect as a falsification of the battery. Fixed,
plus a `ValueError` guard on partial orders, plus two regression tests. After the
fix F-A reads 1.0000. This is the *fourth* gate-logic defect across two
experiments; the pattern itself is now asserted against.

**Gate bug F06 (found and fixed).** `all_gates_pass` drove the verdict and
discarded F-B = 1.0000 because the fragile calibration gate F-C failed, reporting
"battery is an artefact of its constants" and discarding a robust result. Verdict
now keyed to the load-bearing gate with calibration gates reported separately.
**Reported conclusion changed; measurements did not.**

Both recorded in `FALSIFICATION/F05_F06_robustness.md`. F01 remains OPEN — the
robustness result bounds how much F01 matters but does not resolve it, since F-B
is conditional on the same lab-chosen anchor assignments.

## 2026-10-02 — instrument construction and calibration (EXP-C001)

**Created.** Investigation folder from `scaffold_investigation`. 14 indicators
transcribed from Butlin et al. (2023) Table 1 with per-indicator priors.

**Iteration 1 — two-stage aggregation (FAILED, superseded).**
Within-theory geometric-mean collapse, then noisy-AND across theories.
Calibration result: a system with four WEAK gate theories scored **0.000**.
Cause: treating each theory as individually necessary contradicts the source,
which treats some subsets as *sufficient*. Superseded.

**Iteration 2 — noisy-OR (FAILED, superseded).**
Replaced AND with OR per the above. New failure: the same four-WEAK system scored
**0.507**. Cause: plain OR accumulates vagueness into confidence (1 - 0.5^4 =
0.94 in the limit). Superseded by a temperature-smoothed maximum.

**Iteration 3 — absence penalty charged per indicator (FAILED, superseded).**
`gwt_architecture_no_metacognition` scored **0.092**, below its 0.15 floor.
Cause: 0.55^4 for four absent HOT indicators treats four readings of one fact as
four independent failures — reintroducing the double-counting error that the
theory-level collapse exists to prevent, one level down. Fixed by charging once
per theory.

**Iteration 4 — necessity penalty skipped PARTIAL (FAILED, superseded).**
`weak_everywhere` scored **0.550**, above its 0.30 ceiling. Cause: partial
support accrued full credit, so vagueness looked like evidence. Fixed by scaling
the penalty by the status value.

**Iteration 5 — CLAMP BUG (fixed).**
Parameter sweep over `_SOFT_OR_TEMPERATURE` appeared flat above T=0.6. Cause:
`_soft_or` returned values >1.0 and was clamped at the call site, so saturation
was invisible in the sweep and looked like a responsive-but-flat curve. Fixed by
clamping inside the combiner.

**Iteration 6 — calibration harness bug (fixed).**
Sweep produced identical results at every temperature. Two causes: (a) `_soft_or`
took its temperature as a default argument, which binds at def time, so rebinding
the module global had no effect; now read via `globals()` at call time. (b) the
anchor checker tested key *presence* rather than truthiness
(`if "expect_low" in case`), sending the human anchor down the negative branch.
Fixed both.

**Iteration 7 — final.**
`_SOFT_OR_TEMPERATURE = 0.10`, selected by sweep over T in {0.1 ... 2.0} as the
only value satisfying all six anchors. Calibration **PASS 6/6**. Tests **19/19**.

**Recorded as an open problem, not a result:** the temperature was selected
against the same anchors used to validate it, and the anchor bands are lab
assumptions. Logged as F01 in
`FALSIFICATION/F00_F01_F02_F03_F04_kill_attempts.md` and echoed in the module
constant, `CONFIG/prereg_EXP-C001.json`, `HYPOTHESIS.md`, `CONTROLS.md`, and the
plain-English summary. No absolute credence from this battery should be reported
as a measurement.

## Registries updated

- `QUESTIONS.md`: Q-C001 added, status INVESTIGATING
- `HYPOTHESES.md`: HYP-C001 added, status SURVIVED_CONTROLS, L1 instrument only
- `pytest.ini`: TESTS path added to testpaths

## Skipped lifecycle steps (explicit justification)

`EXPERIMENT_PLAN.md` stages `REPLICATION` and `INDEPENDENT METHOD` are **not**
reached. One scoring implementation exists and no second has been written, so
the single-implementation limitation stands (TECHNICAL_SUMMARY §6). Stated rather
than skipped silently.