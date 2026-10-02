# The Scientific Method (as used here)

Plain summary of how this laboratory reasons, and why the reasoning rules are strict.

## The cycle

1. **Observe / question** — Notice something. Ask a specific, answerable question.
2. **Research** — What is already known? What do standard explanations say?
3. **Hypothesis** — A specific, falsifiable claim that predicts an outcome.
4. **Predict** — "If the hypothesis is true, the measurement should be X."
5. **Base** — Measure the default/expected case (baseline).
6. **Control** — Measure against the same setup with the extra factor removed/shuffled.
7. **Experiment** — Measure the real case, exactly as preregistered.
8. **Analyse** — Compute statistics honestly (effect size, significance, CIs).
9. **Falsify** — Try hard to make the result disappear or be explained trivially.
10. **Replicate** — Repeat across seeds; ideally an independent implementation.
11. **Report** — Write down everything, including what it does NOT prove.

## Why the hard rules exist

- **Confirmation bias**: humans (and AIs directed by humans) tend to keep whatever
  agrees with the hypothesis. Controls and pre-registration fight this.
- **Noise is everywhere**: random data will produce patterns. Only a comparison
  against a well-matched control distinguishes pattern from noise.
- **Cool results are suspicious**: unusual results have more ways to be wrong, not
  fewer. They get extra scrutiny, never less.
- **Memory is unreliable**: you cannot verify a result you did not write down.
  This is why every run records its config, seed, software, and hashes.

## The ladder of claims

```
measured pattern          -> real (reproducible) -> meaningful -> novel
```

Each rung needs new evidence. You may not skip rungs.

## Golden rules

- Prefer falsification over confirmation. The best outcome of an experiment is
  usually learning you were wrong.
- A null result is a result. "Nothing unusual happened" is informative.
- Report the controls that failed, not just the ones that passed.
- When in doubt, write `unknown`.