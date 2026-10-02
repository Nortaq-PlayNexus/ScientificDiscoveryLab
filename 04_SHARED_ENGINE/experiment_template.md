# Universal Experiment Template

Every investigation folder under `03_INVESTIGATIONS/<AREA>/<NAME>/` is generated
with this shape (see `engine/reproducibility/experiments.py`):

```
investigation/
├── README.md          overview + pointers
├── QUESTION.md        the scientific question (Q-####)
├── LITERATURE.md      known science + what we cite
├── HYPOTHESIS.md      the falsifiable claim (HYP-####)
├── PREDICTIONS.md     the numbers we expect if true/false
├── CONTROLS.md        the control suite that will be run
├── EXPERIMENT_PLAN.md preregistered protocol
├── CONFIG/            frozen configs (experiment.json + prereg JSON)
├── CODE/              source for this investigation
├── DATA/              local data (raw/processed/generated)
├── RESULTS/           numeric outputs
├── FIGURES/           figures
├── REPLICATION/       replication + parameter/seed sweeps
├── FALSIFICATION/     kill-the-hypothesis attempts + outcomes
├── REPORT/            technical + plain-English summaries
└── CHANGELOG.md       every change, with reason and timestamp
```

Every experiment run writes machine-readable metadata

`experiment.json`

containing: experiment ID, date/time, software version, Python version,
dependencies, git commit (where relevant), random seed, parameters, dataset hashes,
machine info, result hashes (see `REPRODUCIBILITY.md`).

## Two summaries are mandatory for every completed experiment

- **TECHNICAL SUMMARY** — methods, equations, parameters, statistics, CIs, controls,
  limitations, reproduction instructions.
- **PLAIN ENGLISH SUMMARY** — What did we test? What happened? Could it just be a
  computer artifact? What survived controls? What does it NOT prove? Next test?

## Lifecycle reminder

QUESTION -> LITERATURE -> KNOWN EXPLANATIONS -> HYPOTHESIS -> PREDICTION ->
BASELINE -> CONTROL -> EXPERIMENT -> STATISTICS -> FALSIFICATION -> REPLICATION ->
INDEPENDENT METHOD -> REPORT. Never jump from pattern to discovery.