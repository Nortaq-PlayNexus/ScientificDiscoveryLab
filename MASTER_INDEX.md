# MASTER_INDEX

Index of everything in the AI Scientific Discovery Lab. This file is the first stop
when continuing work here.

## Entry points

| Document | Purpose |
|---|---|
| `README.md` | What this lab is and its ground rules |
| `RESEARCH_RULES.md` | The complete rules of conduct for any investigation |
| `CURRENT_STATUS.md` | Live state: what is running, waiting, done |
| `DISCOVERY_LOG.md` | Chronological log of every notable development |
| `QUESTIONS.md` | All candidate/open scientific questions |
| `HYPOTHESES.md` | All registered hypotheses and their states |
| `EXPERIMENT_REGISTRY.md` | Every experiment (ID, state, result summary) |
| `REPRODUCIBILITY.md` | Machine/config dependencies needed to reproduce runs |
| `CHANGELOG.md` | Change history for the lab itself |

## Directory map

### 00_FOUNDATION
`00_FOUNDATION/`
- scientific_method.md, statistics_basics.md, simulation_rules.md,
  falsification_rules.md, terminology_plain_english.md

### 01_RESEARCH_MAP
Per field (`astronomy/`, `cosmology/`, `physics/`, `optics/`, `mathematics/`,
`fluid_dynamics/`, `materials_science/`, `climate_science/`, `earth_science/`,
`biology/`, `neuroscience/`, `chemistry/`, `information_theory/`,
`computational_science/`). Each holds notes on known science, open questions,
and computable attack angles.

### 02_CANDIDATE_PROBLEMS
- `MASTER_CANDIDATES.md` — full registry of candidate questions.
- `HIGH_PRIORITY/`, `MEDIUM_PRIORITY/`, `LONG_SHOTS/` — feasibility groupings
  (feasibility, NOT "which question is more important").

### 03_INVESTIGATIONS
One folder per active investigation (`OPTICS/`, `PHYSICS/`, `MATHEMATICS/`,
`ASTRONOMY/`, `COSMOLOGY/`, `FLUID_DYNAMICS/`, `MATERIALS/`, `CLIMATE/`,
`BIOLOGY/`, `OTHER/`). Each investigation folder follows the universal template
(see `04_SHARED_ENGINE/experiment_template.md`).

### 04_SHARED_ENGINE
Reusable code + templates:
- `simulation/` — simulation utilities
- `statistics/` — statistical testing, multiple-testing correction
- `visualization/` — plotting helpers
- `hypothesis_testing/` — pre-registration, blind analysis, controls
- `reproducibility/` — metadata, hashing, config capture
- `datasets/` — dataset loaders/hashers
- `utilities/` — misc helpers

### 05_DATA
`raw/`, `processed/`, `generated/`, `external_sources/`. Data provenance rules in
`RESEARCH_RULES.md` and `REPRODUCIBILITY.md`. Never delete raw data.

### 06_RESULTS
`confirmed/`, `inconclusive/`, `falsified/`, `anomalies/`. Results move here only
after going through the experiment lifecycle.

### 07_REPORTS
`experiment_reports/`, `literature_reviews/`, `anomaly_reports/`, `final_reports/`.
Anomaly reports follow `ANOM-XXXX.md` naming.

### 08_REPLICATION
`independent_implementations/`, `parameter_sweeps/`, `seed_tests/`,
`cross_method_validation/`.

### 99_ARCHIVE
Finished or retired material. Nothing is ever deleted without explicit approval.

## IDs and naming

- Experiments: `EXP-####` (monotonic, assigned in `EXPERIMENT_REGISTRY.md`).
- Questions: `Q-####` (assigned in `QUESTIONS.md`).
- Hypotheses: `HYP-####` (assigned in `HYPOTHESES.md`).
- Anomalies: `ANOM-####` (assigned in anomaly reports; states defined in
  `RESEARCH_RULES.md`/`QUESTIONS.md`).

## Current focus

See `CURRENT_STATUS.md` for what is active right now.