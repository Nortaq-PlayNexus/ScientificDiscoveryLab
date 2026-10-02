---
name: Reproduction Failure
about: Report that published results do not reproduce
title: "[REPRO FAILURE] "
assignees: ""
---

## What Failed

<!-- Which claim? -->

## Steps

1. Cloned at commit: `[hash]`
2. Ran: `[exact command]`
3. Expected: `[expected]`
4. Got: `[actual]`

## Environment

- **OS**:
- **Python**:
- **numpy / scipy**:
- **Install**: `pip install -r requirements.txt`?

## Integrity Check

```
python experiment_verify.py RESULTS/experiment.json RESULTS/experiment_C003.json
```

Paste the output. If this fails, the recorded results were edited after the run —
that is a different and more serious problem than a version mismatch.

## Notes

<!--
Note: the battery requires only numpy, scipy, pytest. No GPU, no network, no
model weights. If you needed any of those, something is wrong with your setup
rather than with the code.
-->