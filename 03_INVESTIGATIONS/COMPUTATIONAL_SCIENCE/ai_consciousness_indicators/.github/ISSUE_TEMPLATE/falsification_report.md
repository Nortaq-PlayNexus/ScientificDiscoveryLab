---
name: Falsification Report
about: Report a way to break the battery, or a bug in a gate
title: "[FALSIFY] "
labels: falsification
assignees: ""
---

## What You Tried

<!-- The attack on the battery, the test, or the verification gate. -->

## Location

- **File**: `[e.g. battery.py, perturbation.py, test_perturbation.py]`
- **Function**: `[name]`

## Observed

<!-- What happened. Numbers if you have them. -->

## Expected

<!-- What a correct instrument should have done. -->

## Is This a Design Error or a Bug?

<!--
Classification matters and is not rhetorical. The repo has five documented
defects of this exact class already:
  - per-indicator absence penalty (double-counting)
  - default argument binding at def-time
  - key-presence test where truthiness was meant
  - partial EXPECTED_ORDER reporting itself as falsification
  - all_gates_pass discarding a robust result

Pattern: reasons a gate fails that are NOT about the thing under test.
-->

- [ ] Gate/machinery defect (the test is broken, not the battery)
- [ ] Design error (the battery's logic is wrong)
- [ ] Scientific objection (the approach is misconceived)
- [ ] Unsure

## Did You Find It Before or After Running?

<!-- Honesty about your own process is welcome and not held against you. -->

## Reproduction

```
[exact commands]
```