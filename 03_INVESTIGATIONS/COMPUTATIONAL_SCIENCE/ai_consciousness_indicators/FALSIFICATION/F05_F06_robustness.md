# F05, F06, F07 — robustness of the EXP-C003 gates

These record the failures found while running the perturbation experiment and the
release tooling. All three concern the experiment's own gate and verification
machinery, not consciousness. F07 was found during publication preparation.

## F05 — `EXPECTED_ORDER` omitted an anchor (FIXED)

**Symptom.** Gate F-A, "full canonical order exact", read **0.0000** in every run
of the plausible region. That looked like a strong falsification: the battery's
ordering collapsed under mild perturbation.

**Actual cause.** `EXPECTED_ORDER` listed five systems. The scored set contains
six — `feedforward_mlp` was missing. The gate sorted all six and compared the
result against a five-element tuple, which can never match.

So F-A was reporting the gate's own structural defect as a falsification of the
battery. A gate that cannot distinguish "the thing failed" from "the test is
broken" is worse than no gate, because it manufactures confident negatives.

**Fix.** Two parts:

1. `EXPECTED_ORDER` corrected to all six systems, with the ordering *rationale*
   written out rather than implied.
2. `run_perturbation` now raises `ValueError` if `EXPECTED_ORDER` does not
   cover exactly the scored system set. A partial order is a hard error.

**Regression test.** `test_expected_order_covers_every_anchor` and
`test_partial_expected_order_raises_rather_than_silently_scoring`.

**After the fix**, F-A reads **1.0000** in the plausible region. The original
"collapse" was entirely an artefact of the broken gate.

**Why this is recorded rather than quietly fixed.** The same class of bug already
bit EXP-C001 three times (per-indicator penalty, default-argument binding,
key-presence test). A fourth instance in a *different* experiment suggests the
real problem is that gate logic is written without a way to check that the gate
itself runs. That is now asserted in both experiments.

## F06 — `all_gates_pass` conflated two different questions (FIXED)

**Symptom.** `compare_regions` returned
`"ORDERING DOES NOT SURVIVE — battery is an artefact of its constants"`.

**Actual cause.** The verdict keyed on `all_gates_pass`, which requires F-A, F-B,
F-C and F-D together. F-B — that a fluent self-reporting system never outscores
the human — held at **1.0000** in both regions. That is the claim the battery
exists to make, and it survived everything. But F-C (adversarial anchor below an
absolute ceiling) failed under aggressive perturbation, so `all_gates_pass` was
False and the summary reported total collapse.

That is misleading in the opposite direction: it discards a robust result in
favour of a fragile one, and would have led a reader to discard the whole
instrument.

**Fix.** The verdict is now computed from the load-bearing gate, with
calibration gates reported separately. Two distinct questions, two distinct
answers:

- **ORDERING / architecture claim** — F-B, robust in both regions.
- **ABSOLUTE calibration** — F-A and F-C, robust in the plausible region only.

**After the fix:**

```
ORDERING ROBUST IN PLAUSIBLE REGION; ABSOLUTES NOT ROBUST
  F-B (fluency cannot beat architecture) HOLDS [1.0000 / 1.0000]
  exact ordering holds under plausible perturbation [1.0000]
  absolute calibration DOES NOT hold under aggressive perturbation
```

`verdict_detail` now carries the conclusion, what it authorises, and what it does
not.

**Standing caveat.** This fix changes a *reported* conclusion, not a measurement.
The underlying numbers are identical in both versions. Recorded here because a
verdict string is part of a result and must not be edited to look better — the
numbers that disagreed are preserved above.

## F07 — clean-room verifier walked into its own staging area (FIXED)

**Found during publication preparation**, not during the science.

**Symptom.** `verify_clean_room.py` reported `CLEAN ROOM FAILED (1 step(s))` with
three collection errors, immediately after the Zenodo deposit tooling was added.

**Actual cause.** The verifier copied the whole tree into a temp directory. That
included `zenodo/package/`, which is a *generated copy of the same test modules*.
Duplicate module basenames in two directories made pytest collect them twice and
fail on import.

**Why it matters beyond the wasted cycle.** The failure was loud and completely
uninformative: it said nothing about the instrument, and a reader skimming CI
output could easily misread it as the battery breaking. That is precisely the
failure class F05 and F06 describe — a checker failing for a reason unrelated to
what it checks.

**Fix.** `zenodo/` added to the verifier's exclusion list, with a comment
recording why. Both this and the verifier's existence are now covered by CI.

**The pattern.** This is the sixth gate or verifier defect in the project and the
second of this exact kind:

| | Defect | Read as |
|---|---|---|
| 1 | per-indicator absence penalty | battery wrong |
| 2 | default argument bound at def-time | sweep inert |
| 3 | `if "key" in dict` where truthiness was meant | anchors mis-scored |
| 4 | necessity penalty skipped PARTIAL | vagueness counted |
| 5 | `EXPECTED_ORDER` missing an anchor (F05) | **ordering collapsed** |
| 6 | `all_gates_pass` discarding a robust result (F06) | **battery is an artefact** |
| 7 | clean-room verifier recursed into staging (F07) | **instrument broken** |

Five of the battery's six logic defects were found by the known-answer anchors.
All of the verifier defects were self-inflicted. The recurring lesson is that a
verification step must itself be verified: the question "does this checker run
correctly?" is separate from "what is it checking?", and in five cases the answer
to the second was confused with the first.

## What none of F05–F07 changes

F01 stands. The perturbation experiment bounds how much F01 matters; it does not
resolve it. Even the F-B result is conditional: it holds *given* the anchor
assignments, which are still lab assumptions. Independent expert elicitation
remains the only thing that would discharge F01.