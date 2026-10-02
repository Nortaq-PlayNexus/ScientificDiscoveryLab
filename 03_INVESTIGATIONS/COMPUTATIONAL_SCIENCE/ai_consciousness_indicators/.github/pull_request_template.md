## What does this pull request change?

<!-- One or two sentences. -->

## Type

- [ ] Bug fix (battery, gate, or test)
- [ ] New aggregator / alternative combination rule
- [ ] Calibration anchor change — **requires preregistration before the run**
- [ ] Documentation
- [ ] Infrastructure

## Claim discipline check

This repo scores **no AI systems** and makes **no claim about AI consciousness**.
Before merging, confirm your change does not:

- [ ] introduce an absolute credence presented as a measurement of consciousness
- [ ] present a literature summary as a white-box measurement
- [ ] re-tune a constant against the existing anchors without saying so

## If you changed a constant

- [ ] `CONFIG/prereg_EXP-C001.json` updated, or the change logged as a post-hoc
      hypothesis change rather than silently applied
- [ ] The circularity note in `FALSIFICATION/F00_F01_F02_F03_F04_kill_attempts.md`
      (F01) re-read and still accurate
- [ ] Calibration gate re-run and passing

## If you changed an aggregator

- [ ] Known-answer calibration still passes 6/6
- [ ] `test_fluent_liar_never_beats_human_under_any_perturbation` still passes
- [ ] Superseded design documented in `CHANGELOG.md` rather than deleted
- [ ] `perturbation.compare_regions` verdict recorded for the new design

## If you added an experiment

- [ ] Preregistered before running
- [ ] Controls implemented (see `CONTROLS.md`)
- [ ] Failures recorded, not deleted
- [ ] Both summaries written (`REPORT/`)

## Tests

```
pytest -q
```

- [ ] All pass
- [ ] New behaviour has a test
- [ ] New tests pass for the *right* reason (try breaking them deliberately)

## Result integrity

- [ ] `RESULTS/*.json` either unchanged, or re-run with the hash regenerated
- [ ] `python experiment_verify.py RESULTS/experiment.json RESULTS/experiment_C003.json` passes