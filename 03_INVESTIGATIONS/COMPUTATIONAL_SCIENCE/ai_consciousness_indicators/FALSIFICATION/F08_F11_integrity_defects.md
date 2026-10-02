# F08–F11 — integrity defects found in pre-release review and first CI run

Found during a full read-through immediately before publication (F08–F10), plus
three more caught by CI on the first push (F11).

F08–F10 are in the instrument's *guarantees* rather than its scoring logic, which
is what makes them more serious than typical lint: each one is a protection that
appeared to be working and was not. F11 is a set of environmental assumptions —
lint config in two places, dependency bounds that excluded two advertised Python
versions, and a CI assertion against a key that does not exist.

**None of the six changed the scientific conclusions.** Several would have changed
what a reader believed those conclusions were, which is the failure mode that
matters most for work whose entire claim is about not overstating.

---

## F08 — `calibration_passed` was unconditionally True

**The field.** Every `BatteryResult` carries `calibration_passed: bool`.

**The defect.** It was assigned

```python
calibration_passed = not require_calibration or True
```

`not X or True` is `True` for every `X`. The field could never report failure.

**Why it matters.** This is the calibration gate — the single mechanism the whole
project rests on, and the thing F01 exists to keep honest. A caller checking
`result.calibration_passed` before trusting a number would get false assurance
that the six known-answer anchors had passed, regardless of whether they had ever
been run. A status flag that cannot fail is worse than no flag, because it
converts "unknown" into "pass" without anyone noticing.

**Fix.** The field is now derived from `calibration_state()["passed"]`, which
actually runs (or reuses a memoized run of) the anchors. And `run_battery`
enforces the gate it previously only claimed to enforce:

```python
if require_calibration:
    state = calibration_state()
    if not state["passed"]:
        raise CalibrationNotEstablished(...)
```

`require_calibration=False` still works and still returns a number, but now
reports `calibration_checked=False` so a diagnostic figure cannot be mistaken for
a calibrated one.

**Subtlety worth recording.** The first fix attempt caused `RecursionError`:
`calibrate_known_answers` scores the anchors by calling `run_battery`, and
`run_battery` wanted the calibration state. Fixed with a reentrancy guard that
returns `passed=None` — meaning *not yet established* — while the anchors are
themselves being scored. Returning `True` there would have been a lie that is also
self-justifying.

**Regression tests.** `test_calibration_passed_is_computed_not_asserted`,
`test_gate_raises_when_calibration_has_not_passed`,
`test_uncalibrated_diagnostic_is_available_explicitly`,
`test_reentrant_calibration_reports_not_yet_established`.

---

## F09 — the duplicate-indicator check could never fire

**The code.**

```python
by_key = {a.key: a for a in assessments}
if len(list(by_key.values())) != len(set(by_key)):
    raise ValueError("duplicate indicator keys in assessments")
```

**The defect.** `by_key` is a dict keyed on indicator key. A dict cannot hold two
entries with the same key, so the dict comprehension has *already* discarded the
duplicate before the check runs. `len(list(by_key.values()))` and `len(set(by_key))`
are equal by construction. The condition was unreachable.

**Why it matters.** `run_battery` accepts a list of `Assessment` objects, so a
caller can legitimately pass two assessments for the same indicator — say
`GWT-1` SATISFIED at CONTROLLED evidence and `GWT-1` ABSENT at EXTERNAL
evidence. Those genuinely contradict each other. The old code silently kept the
last one, with no error, so a contradictory input set produced a confident number
with an arbitrary choice baked in. For an instrument whose entire purpose is to
refuse unwarranted confidence, silently resolving a contradiction is the exact
failure mode to avoid.

**Fix.** Duplicate detection now happens while building the mapping, so the
duplicate is seen before it can be discarded.

**Regression tests.** `test_duplicate_indicator_keys_are_rejected`,
`test_conflicting_duplicate_is_not_silently_resolved`,
`test_repeated_identical_key_still_rejected`. The last one asserts that even
*non*-contradictory duplicates are rejected: a repeated identical entry is
ambiguous about intent and has no correct interpretation.

---

## F10 — one of the six perturbation families perturbed nothing

**The context.** The robustness claim (EXP-C003) advertises six jointly
perturbed parameter families, P1 through P6, across 3,000 draws.

**The defect.** In `score_under_params`, family P4:

```python
conscious_rate = _clamp(ind.p_given_conscious + params.conscious_rate_shift[ind.key])
```

was computed and then never read. The `conscious_rate_shift` dictionary was
sampled for every draw, stored on `PerturbedParams`, serialized in `describe()`,
and documented in the module docstring — and discarded at the point of use.

**Why it matters.** This is the most consequential of the three, because it
affects a *scientific claim* rather than an internal guarantee. The robustness
result said "all six discretionary parameter families were perturbed jointly."
In fact five were. One advertised degree of freedom — how strongly a conscious
system is assumed to show each indicator — was held fixed across all 3,000 draws
while being reported as varying.

The headline numbers did not change materially once P4 was wired in (F-B still
1.0000 in both regions, F-A 1.0000 plausible, 0.6413 → 0.6680 aggressive, F-C
0.7687 → 0.7907). But the *claim* had to be corrected, and the recorded results
regenerated with new hashes, because for a while the repository was making a
robustness statement that was one parameter short of what it said.

**Fix.** `p_given_conscious` now caps how strongly a `SATISFIED` assessment can be
credited — even a conscious system only shows some indicators reliably, which is
exactly what that prior encodes:

```python
if a.status is Status.SATISFIED:
    likelihood = min(likelihood, max(conscious_rate, base_rate))
```

**Regression tests.** `test_conscious_rate_shift_actually_perturbs` and
`test_all_six_perturbation_families_reach_the_score`. The second tries each family
in **both directions** and requires at least one to move the score.

The two-direction requirement matters, and finding it was itself instructive. A
single-direction version of that test reported P1 and P3 as inert. They are not.
The combiner is monotone, so near a boundary a family can move the result downward
while clamping flat upward — absence of upward movement is not absence of effect.
The test also uses a partially-satisfied assessment rather than an all-SATISFIED
one, because a fully-satisfied system saturates at 1.0 and would make *every*
temperature perturbation look inert.

---

## Effect on recorded results

Both `RESULTS/*.json` files were regenerated with `tools/regenerate_results.py`,
which now carries the three fixes in a `fixes_in_this_record` field so the change
is visible inside the result record itself:

| | before | after |
|---|---|---|
| EXP-C001 `result_hash` | `a57207e5cf7d6775…` | `b953b8178354f048…` |
| EXP-C003 `result_hash` | `b96aaef11ef49e7b…` | `1249a0ac9091ec2d…` |

Unchanged: the calibration gate passes 6/6, F-B holds at 1.0000 in both regions,
and the ordering conclusion is identical. What changed is that the robustness
claim now matches the code that produces it.

`tools/regenerate_results.py` exists because a stale hash is the mechanism by
which a reader discovers the code moved under the numbers — which is exactly what
should happen, and exactly what the pre-fix hashes would have concealed.

---

## The pattern across F05–F10

| | Defect | Would be misread as |
|---|---|---|
| F05 | `EXPECTED_ORDER` missing an anchor | **the ordering collapsed** |
| F06 | `all_gates_pass` discarding a robust result | **the battery is an artefact** |
| F07 | clean-room verifier recursing into staging | **the instrument is broken** |
| F08 | `calibration_passed` always True | **the gate passed** |
| F09 | duplicate-key check unreachable | **contradictory inputs agree** |
| F10 | P4 perturbation family inert | **six families were perturbed** |

Six defects, and in four of them the failure mode was *manufactured confidence*
rather than lost confidence: a checker reporting a result that was never
computed. F05, F06, F08 and F09 all produce output that looks like a finding and
is manufactured by the machinery doing the looking.

F08 and F09 are the two that would have survived into publication most easily.
Neither crashes. Neither produces a warning. Both simply return confident,
plausible, wrong output.

The recurring lesson stands: **a verification step must itself be verified.** The
question "does this checker run correctly?" is separate from "what is it checking?"
and in these cases the second was consistently confused with the first.
---

## F11 � three defects found by CI on the first push, not by reading

**Worth its own entry because CI caught these on the first run after being pushed.
That is the system working � and also the first defect in this project found by a
machine rather than by reading.**

**F11a � the headline-claims job asserted on a key that does not exist.**

Symptom: `KeyError: 'gates'` on a clean checkout.

Cause:

```python
r = compare_regions(seed=0)
assert r["verdict_detail"]["load_claim_FB_holds_both"], r["gates"]
```

`compare_regions()` returns `verdict`, `verdict_detail`, `plausible_region`,
`aggressive_region`. There is no top-level `gates` key; the figures live inside
each region. Python evaluated `r["gates"]` to build the failure message and
raised before reaching the real assertion.

Why it matters: had the inner assertion also been false, this would have reported
`KeyError: 'gates'` instead of the actual gate values. Anyone reading CI would
conclude the battery's robustness claim had broken. It had not.

**F11b � lint config lived in two places.**

The workflow passed `--max-line-length=120` on the command line while local runs
used `setup.cfg`'s 125. One line at 124 characters passed locally and failed in
CI. Config in two places will disagree; lint config now lives only in
`setup.cfg`, and CI runs bare `flake8 .`.

**F11c � the advertised support matrix could not install.**

`requirements.txt` pinned `numpy>=2.4.0` and `scipy>=1.18.0`, which require
Python >=3.11 and >=3.12. The CI matrix started at 3.10, so two of four legs
could not install the project at all. The bounds were set from the development
machine, not from the oldest interpreter declared as supported. Relaxed to
`numpy>=2.2` / `scipy>=1.13`. Nothing in the code depends on 2.4-only behaviour.

All three are the same species as F05-F10: a check that fails for a reason
unrelated to what it checks, producing output that reads as a finding about the
instrument. Two of the three produced *confident wrong conclusions* rather than
plain errors.

**The asymmetry is the lesson.** F05-F10 were found by reading. F11 was found by
pushing and letting a clean environment disagree. Reading finds silent defects;
execution finds environmental assumptions. Neither method is sufficient alone,
and the failure modes are different enough that a project needs both.

Recorded result after the fix: all four pytest legs, hash integrity, headline
claims and lint pass on a clean checkout.

---

## Cross-reference: the full table

| | Defect | Would be misread as | Found by |
|---|---|---|---|
| F05 | `EXPECTED_ORDER` missing an anchor | the ordering collapsed | reading |
| F06 | `all_gates_pass` discarding a robust result | the battery is an artefact | reading |
| F07 | clean-room verifier recursing into staging | the instrument is broken | execution |
| F08 | `calibration_passed` always True | the gate passed | reading |
| F09 | duplicate-key check unreachable | contradictory inputs agree | reading |
| F10 | P4 perturbation family inert | six families were perturbed | reading |
| F11 | CI asserted a nonexistent key | the robustness claim broke | execution |

None changed the scientific conclusions. Several would have changed what a reader
believed those conclusions were, which is the failure mode that matters most for
work whose entire claim is about not overstating.
