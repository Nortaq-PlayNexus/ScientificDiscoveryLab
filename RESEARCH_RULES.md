# RESEARCH_RULES

The rules of conduct for every investigation in this laboratory. These rules exist
to make the lab honest, reproducible, and worth trusting.

## 1. Layers of claims

Every result is one of these, and may only be described at its highest *supported* layer:

1. **Instrument/measurement result** — what the computer produced.
2. **Statistical result** — whether the measurement is distinguishable from the null.
3. **Physical/scientific claim** — what the result means about the world/model.
4. **Novelty claim** — that something is new to science.

Movements between layers require the experiment lifecycle to be completed. The lab
never jumps from "interesting pattern" to "new discovery."

## 2. Experiment lifecycle (mandatory order)

```
QUESTION
  -> LITERATURE REVIEW
  -> KNOWN EXPLANATIONS
  -> HYPOTHESIS
  -> PREDICTION
  -> BASELINE
  -> CONTROL
  -> EXPERIMENT
  -> STATISTICAL ANALYSIS
  -> FALSIFICATION
  -> REPLICATION
  -> INDEPENDENT METHOD
  -> REPORT
```

Skipping steps is allowed only with an explicit written justification in the
investigation's CHANGELOG.

## 3. Controls (no exceptions)

Every experiment must implement at least the controls appropriate to its design.
Minimum set:

- **Null/random control** — random inputs with matched size/distribution.
- **Matched control** — same design with one factor meaningfully different.
- **Positive control** — where available, confirm the method detects known effects.
- **Seed variation** — repeat across independently chosen seeds.
- **Resolution variation** — repeat at different grid sizes/resolutions.
- **Method variation** — repeat with a different numerical algorithm where feasible.

If a result disappears when a control changes, record that honestly in RESULTS.

## 4. Anomalies

An anomaly is a statistically unusual result. It is NEVER automatically new physics.

Every anomaly gets an ID: `ANOM-####`.

States (from the master spec):

- `NEW`
- `INVESTIGATING`
- `KNOWN_EXPLANATION_FOUND`
- `FAILED_REPLICATION`
- `SURVIVED_INITIAL_CONTROLS`
- `REQUIRES_EXTERNAL_VALIDATION`

Never use `PROVEN NEW SCIENCE` unless overwhelming, independently verified evidence
warrants it (in practice: requires external replication and human scientific review).

## 5. The "Kill the Hypothesis" engine

Any interesting result must be attacked with at least these questions:

- Is this numerical error? / sampling? / aliasing? / floating-point behaviour?
- Is this a visualization artifact? / boundary artifact?
- Is this caused by parameter selection? / overfitting? / multiple testing?
- Is this a known physical phenomenon?
- Is this caused by the simulation method?
- Does changing algorithms remove it? / resolution? / random seeds?
- Does independently generated data reproduce it?
- Does a simpler model explain it?

Prefer finding the exciting hypothesis is WRONG over falsely confirming it.

## 6. Anti-self-confirmation (AI constraint)

- Preregister the experiment configuration before running (config file + ID).
- Experiment IDs are immutable once allocated.
- Parameter changes after seeing results are logged as hypotheses changes, not hidden.
- Holdouts / frozen test sets are used where applicable.
- Zeros: multiple-testing correction is applied when many things are compared
  (Benjamini-Hochberg FDR by default, alpha = 0.01 unless preregistered otherwise).
- The AI may not iterate until it gets a desired result without recording each change.

## 7. Literature checking

Before any novelty claim:

1. Has this exact question been answered?
2. Has the proposed effect been observed?
3. Is the proposed mechanism known?
4. Are the measurements standard?
5. Has someone performed a similar control?
6. Does the result reproduce established results?
7. What would actually be novel?

Never say "Nobody has done this before." Say: "I found no matching study in the
sources searched; this does not establish priority."

## 8. Evidence states (displayed in dashboard)

```
UNTESTED
INITIAL RESULT
CONTROLLED
REPLICATED
INDEPENDENTLY REPRODUCED
LITERATURE-CHECKED
EXTERNALLY VALIDATED
```

## 9. Outputs of every completed experiment

- **Technical summary**: methods, equations, parameters, statistics, confidence
  intervals, controls, limitations, reproduction instructions.
- **Plain English summary**: What did we test? What happened? Could it just be a
  computer artifact? What survived the controls? What does this NOT prove?
  What next?

## 10. Hardware awareness

- Experiments must respect machine limits (see `CURRENT_STATUS.md`/`REPRODUCIBILITY.md`).
- Long runs need: checkpointing, pause/resume, progress, cancellation,
  crash recovery, low-resource mode.
- If a run would risk freezing the machine, it does not run — it waits in a queue.

## 11. Data integrity

- Raw data is read-only.
- Every run records: seed, parameters, git/software versions, dataset hashes,
  result hashes (see `experiment.json` requirement in `04_SHARED_ENGINE`).
- Append-only logging for registries.

## 12. Honesty

- Unknown is written as `unknown`.
- Failed controls are recorded, not deleted.
- A null result is a result.
- The lab never fabricates a result to please a narrative.