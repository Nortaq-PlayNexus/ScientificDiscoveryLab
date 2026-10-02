# INTEGRATION_PLAN — coherent-optical-ai-sandbox -> 03_INVESTIGATIONS/OPTICS

Status: **PLANNED** (2026-09-17). No existing sandbox file has been modified.

## Source project

- Path: `C:\Users\natha\code\coherent-optical-ai-sandbox`
- Nature: standalone PySide6 app + research framework. Python 3.14.7, `.venv`.
- Research core: `research/` (registry `research/registry/experiments.jsonl`,
  agents, phase1, audit, controls, literature, reproducibility, next_phase).
- Physics modules: `app/optics/*.py` (propagation, diffraction, speckle,
  gaussian_beam, coherence, structured_light, polarization, phase_screen,
  simulation via torch CPU/GPU detected).
- Analysis: `app/analysis/metrics.py`.
- Current evidence base: 25-phase validation (EXP-0001..EXP-0025), then multi-agent
  novelty audit -> highest supported evidence level **1** (measurable designed
  structure). Claim withdrawal documented in `research/FINAL_PHASE_REPORT.md` and
  `DECISIONS.md`.

## Mandate

The master prompt (Desktop `New Text Document.txt`) says:

- The existing coherent optical sandbox is incorporated as `03_INVESTIGATIONS/OPTICS/`.
- Do NOT overwrite existing work.
- Create a migration/integration plan FIRST. This file is that plan.

## Decision: reference, not copy

Copying ~hundreds of files into the lab would duplicate the source of truth, risk
drift, and violate "do not overwrite existing work / keep it clean". Instead:

1. `03_INVESTIGATIONS/OPTICS/` becomes a **thin, pointer-based integration** that
   references the sandbox by absolute path and documents how to use it as an optics
   engine under lab rules.
2. Lab-native code in OPTICS keeps clear boundaries: small driver scripts that call
   the sandbox package on sys.path when present, plus lab-standard controls/stats
   from `04_SHARED_ENGINE`.
3. All lab claims produced from optics experiments flow through the lab lifecycle
   (pre-registration, controls, kill-the-hypothesis) and are recorded in the lab
   registries, NOT the sandbox's append-only registry.

## Migration/integration steps (ordered; each is a separate approval gate)

- [ ] **S1 — Pointer README.** Create `03_INVESTIGATIONS/OPTICS/README.md`
  describing the source path, how to activate the sandbox venv, how to import
  `app.optics` and `app.analysis`, and which sandbox tests cover physics validity
  (ASM unitary ~1e-13; energy err ~1e-16; independent ASM NCC=1.0; 10 pytest green).
- [ ] **S2 — Adapter module.** Add `03_INVESTIGATIONS/OPTICS/CODE/` with an
  `engine_adapter.py` that exposes the sandbox's strongest-validated kernels
  (angular spectrum propagation, speckle, matched amplitude/phase fields) through a
  lab-standard interface. Pure re-export + validation wrapper; never edits sandbox code.
- [ ] **S3 — Preregistered validation experiment.** Run `EXP-OPT-0001`: lab-standard
  wrapper reproduces a known result (e.g., propagation of a Gaussian/vortex through
  known distances matches analytic/tabulated result to declared tolerance) with the
  full experiment.json metadata and control suite.
- [ ] **S4 — Continuation of audit threads.** Port-as-lab-investigations only where
  they fit lifecycle rules:
  - EXP-3 position-permutation null (deferred in the sandbox audit).
  - Pre-registered single-plane z=1280 matched-spectrum null, N >= 4999.
- [ ] **S5 — Literature continuation.** Extend `LITERATURE.md` under OPTICS from the
  sandbox's `research/literature/` (OPTICS_LITERATURE, VISUAL_PHENOMENON_LITERATURE,
  NOVELTY_ASSESSMENT) — cite, do not copy verbatim.
- [ ] **S6 — Cleanup decision.** Decide whether the sandbox itself later moves under
  the lab, is kept as a UI product, or stays; no movement without user approval.

## Rules for anything derived from the sandbox

- Any sandbox numerical result reused MUST be re-derived or matched by a lab run with
  metadata (hash, seed, versions), never cited second-hand.
- Any sandbox metric whose meaning is contested (e.g., winding-count detector) is
  documented with its audit failure mode before being proposed again.
- Hypothesis changes after seeing results are logged in the lab CHANGELOG as changes.

## What integration does NOT do

- Does not modify/copy sandbox source.
- Does not move the sandbox.
- Does not import sandbox results into the lab without re-derivation.
- Does not resurrect withdrawn claims ("propagation generates order", the
  48->176 trajectory, wavelength invariance, "32 µm" invariant, arrangement info).

## Blockers / caveats

- The sandbox has its own `.venv`; lab code should run against the same interpreter
  or a venv with identical core versions (numpy 2.5.x, scipy 1.18.x, torch CPU).
- The sandbox UI (PySide6) is not needed for lab experiments; lab use is headless.
- `experiments.jsonl` in the sandbox is append-only there; the lab keeps its own
  append-only registry. Two registries, clearly separated.

## Approval

Executing S1..S6 requires user go-ahead per step. S1 (pointer README) is low-risk and
may be done in the next session unless the user objects.