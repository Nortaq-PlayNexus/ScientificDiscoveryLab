# CHANGELOG — water_sound_response (EXP-0015)

Machine-readable log: `CONFIG/changelog.jsonl` (append-only).

## 2026-09-22

- Created the investigation with the lab's own scaffold
  (`engine.reproducibility.experiments.scaffold_investigation`) under the new
  field `ACOUSTICS`. Added `01_RESEARCH_MAP/acoustics/notes.md`.
- Allocated IDs: Q-AC001 (question), HYP-AC001 (hypothesis), EXP-0015
  (experiment). Verified none of these IDs existed anywhere in the lab before
  allocation.
- Wrote QUESTION, LITERATURE, HYPOTHESIS, PREDICTIONS, CONTROLS, EXPERIMENT_PLAN
  and FALSIFICATION/planning_checks before any registered execution.
- **Literature honesty note recorded in LITERATURE.md:** the design research used
  targeted web searches plus established textbook material; no structured
  bibliographic database (PubMed / Web of Science / Scopus / INSPEC) was queried
  programmatically. This limitation is disclosed rather than glossed.
- Offline planning checks (disclosed in FALSIFICATION/planning_checks.md) fixed
  the UNESCO coefficient transcription, the Mackenzie cross-check tolerance, the
  0.5 Hz resonance sweep step, the classical-absorption algebra, the Gorkov
  contrast factor, the Minnaert constant, the Faraday Gamma ladder and the
  vertical-grid convergence expectation. None of these numbers are registered
  results.
- **Design correction before the prereg was frozen:** the S3 gated band was
  moved from {100 kHz, 300 kHz, 1 MHz, 3 MHz} to {1, 3, 10, 30} MHz because
  alpha ~ f^2 makes the cell count for a fixed optical depth scale as 1/f — the
  original low-frequency cells would have needed ~10^7 cells each and sat in a
  band where absorption over any laboratory distance is unmeasurably small.
  The audio-band figure moved to characterisation. See
  FALSIFICATION/planning_checks.md "Cost check that moved the gated band".
- No code has been executed against the frozen preregistration yet; next entry
  records the run and any post-freeze changes.
