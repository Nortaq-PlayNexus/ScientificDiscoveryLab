# Data Index

> **AUDIT HOLD (2026-09-24): paths below are historical claims. Several source
> files are outside this tree or were not independently verified. Read
> `AUDIT_SUPERSESSION_NOTICE.md` before relying on this index.**

- **Dossier:** Document 8 of 9
- **Companion:** `PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md`, `EXPERIMENT_TIMELINE.md`

This file maps every number, figure, and source file used by the dossier to its
actual location, so an external reviewer can pull the raw material without
hunting.

> Base paths:
> - sandbox: `C:\Users\natha\code\coherent-optical-ai-sandbox`
> - lab: `C:\Users\natha\ScientificDiscoveryLab`
> - dossier: `C:\Users\natha\ScientificDiscoveryLab\05_EXTERNAL_RESEARCHER_DOSSIER`

## 1. Verdict and audit reports (sandbox)

| Content | Path | Used for |
|---|---|---|
| Final audit verdict, headline numbers, methodology correction | `research\FINAL_PHASE_REPORT.md` | Dossier §1–§7 |
| Condensed verdict | `research\EXECUTIVE_SUMMARY.md` | Executive-style reading |
| Audit state | `research\audit\PROJECT_STATE.md` | Framework description (multi-agent validation & novelty audit) |
| Control matrix | `research\controls\CONTROL_MATRIX.md` | Methods document §6 |
| Independent replication (validator battery) | `research\reproducibility\INDEPENDENT_REPLICATION.md` | EXP-1, PARTIALLY REPRODUCIBLE |
| Literature pass | `research\literature\OPTICS_LITERATURE.md` | Q1 (Carter/Wolf entry) |

## 2. Audit experiments (sandbox `research\next_phase`)

| Experiment | File | Key numbers |
|---|---|---|
| EXP-1 (independent replication) | `EXP-1_summary.json`, `EXP-1_summary.coordinator_original.json` | 48 cores, +24/−24; 45-feature/21-24-split AGAINST |
| EXP-2 (phase randomisation) | `EXP-2_summary.json` | Correction: identity 6.55e-16; NCC 0.0564; 74→21738 |
| EXP-2B (pre-registered z=1280) | `EXP-2B_z1280_summary.json`; design in `PREREGISTRATION_z1280.md` | S=95, d≈4.2–4.5, 6/6 seeds ≤0.01 |
| EXP-2C (probes) | `EXP-2C_probe_summary.json` | PROBE A: only 256² survives; PROBE B: only z=1280, not Talbot |
| EXP-4 (grid sweep) | `EXP-4_summary.json` | 48/73/90/97 counts; padding shifts 20.8–24.4% |
| EXP-5 (periodic spacing) | `EXP-5_summary.json` | 8.0 px autocorrelation for all pitches |
| Independent checks | `INDEPENDENT_VERIFICATION.md` | 6/6 PASS |
| Pre-registration | `PREREGISTRATION_z1280.md` | Statistic & seeds {42,7,123,2023,314159,271828} |
| Next experiments | `NEXT_EXPERIMENTS.md` | Proposed work |

## 3. Tool-specific reports and figures (sandbox)

| Content | Path |
|---|---|
| DeepBeamValidator 12-test battery | `reports\DeepBeamValidation_w694.3nm_s42.md` |
| Emergence-vs-inheritance control | `reports\DeepBeamEmergenceControl_w694.3nm_s42.md` |
| Dossier figure set (13 files) | `reports\figures\dossier\*.png` |
| Emergence-control figure set (6 files) | `reports\figures\emergence_control\*.png` |

Figure contents (referenced, not copied) and captions are in
`figures\README.md`.

## 4. Lab engine (`ScientificDiscoveryLab`)

| Content | Path |
|---|---|
| Lab status | `CURRENT_STATUS.md` |
| Discovery log | `DISCOVERY_LOG.md` |
| Experiment registry (EXP-0002 … 0007, Q-O001…Q-P004) | `EXPERIMENT_REGISTRY.md` |
| Hypotheses | `HYPOTHESES.md` |
| Questions | `QUESTIONS.md` |
| Candidate problems (Q-O003 at line 274) | `02_CANDIDATE_PROBLEMS\MASTER_CANDIDATES.md` |
| OPTICS integration plan (PLANNED, reference-not-copy) | `03_INVESTIGATIONS\OPTICS\INTEGRATION_PLAN.md` |
| Shared engine spec (import, RNG, BH-FDR) | `04_SHARED_ENGINE\README.md` |

## 5. Dossier deliverables

| File | Role |
|---|---|
| `PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md` | Document 1 (main, 12 sections) |
| `EXECUTIVE_SUMMARY.md` | Document 2 |
| `EXPERIMENT_TIMELINE.md` | Document 3 |
| `METHODS_AND_CONTROLS.md` | Document 4 |
| `KEY_RESULTS.md` | Document 5 |
| `NEGATIVE_AND_DIAGNOSTIC_RESULTS.md` | Document 6 |
| `CURRENT_OPEN_QUESTIONS.md` | Document 7 |
| `DATA_INDEX.md` | Document 8 (this file) |
| `FOLLOWUP_EMAIL.md` | Document 9 |
| `DOSSIER_BUILD_REPORT.md` | Build/verification record |
| `figures\README.md` | Figure index |

## 6. Registry-integrity note

Sandbox registry rows `EXP-0001`, `EXP-0002`, `EXP-0006`, `EXP-0007` are marked
FAILED (missing files / hash drift); the date-strip resolves the drift. Registry
is append-only; the failure rows are preserved deliberately (audit hygiene) and
are **not** physics results.

## 7. Post-draft lab activity (2026-09-18)

- **EXP-0009 (Q-P005 percolation critical exponents) — COMPLETE.**
  Decision: ABNORMAL (all gates PASS, D_f/γ/ν/β/ν miss tolerances by
  ~1σ). `percolation\Q-P005_exponents\CODE\RESULTS\EXP-0009_summary.json`.
- **EXP-0010 (Q-P005 lattice-artifact diagnostic) — COMPLETE.**
  Decision: LATTICE_ARTIFACT. D_f=1.8962 at non-power-of-2 sizes
  vs 1.8958 theory. Diagnosed EXP-0009 ABNORMAL as a lattice-size
  discretization artifact (same class as optical grid-locking at 256²).
  Q-P005 resolved.
- **EXP-0008 (Q-M002 prime gaps) — COMPLETE (post-BH-FDR-fix).**
  Decision: H1_SUPPORTED (chi2_red 262→94,633, C7 perfect match).
  `prime_gaps\RESULTS\EXP-0008_results.json`.
- Note: `run_exp0009.py` ENGINE path correctly uses
  `percolation\ENGINE` (verified by running EXP-0009 and EXP-0010).
  No fix needed; earlier flag was a false alarm.
- Percolation results integrated into `KEY_RESULTS.md` (R7, R8).