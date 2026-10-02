# README — How water responds to sound and vibration frequencies (Q-F004)

Status: **EXP-0015 preregistration frozen.**

Purpose: Reproduce, with the lab's controlled pipeline, the classic **parametric
(Faraday) response of a water surface to vertical vibration** — the pattern
wavelength selected at a given drive frequency, the **subharmonic half-frequency
response**, and the **capillary-gravity dispersion law** that links them. This is a
known-result reproduction for laboratory calibration, not a search for new physics.

## The phenomenon in one sentence

Shake water up and down at frequency f and the surface forms standing-wave patterns
that slosh at f/2, with a wavelength given by the capillary-gravity dispersion
relation ω² = (gk + σk³/ρ)·tanh(kh) evaluated at ω = Ω/2 = π·f (Faraday 1831;
Benjamin & Ursell 1954; Kumar & Tuckerman 1994).

## Layout

| Path | Meaning |
|---|---|
| `CONFIG/prereg_EXP-0015.json` | frozen preregistration (single source of truth) |
| `CODE/faraday_engine.py` | primary surface-wave/Mathieu integrator (Method M1) |
| `CODE/run_exp0015.py` | orchestrator: baseline/controls/experiment/stats/report |
| `REPLICATION/floquet_analysis.py` | independent implementation (Method M2: Floquet monodromy) |
| `RESULTS/` | raw outputs + separated summary |
| `REPORT/` | technical + plain-language summaries |
| `FALSIFICATION/` | kill-the-hypothesis planning |
| `DATA/` | local data notes (no raw datasets needed) |

## Conventions inherited

- BH-FDR alpha 0.01 unless preregistered otherwise.
- Append-only registry (`CONFIG/registry.jsonl`).
- All randomness from `engine.utilities.rng(label, seed)` (lab RNG).
- All results labelled as computational reproductions — never experimental facts.