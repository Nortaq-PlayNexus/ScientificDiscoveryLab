# EXP-0006 Proposal — Fine-Grid Width-Route Follow-Up

**Status:** Prepared but **NOT EXECUTED** (2026-09-17). Awaiting user decision.

## Purpose

EXP-0005 audit (`DIAGNOSTICS/EXP-0005_width_route_audit.md`) found that the
width-route C8 estimate at L=256/512 is **grid-limited**: the frozen p-grid
step (0.02) exceeds the physical width (~0.006), so the estimator cannot
resolve the true crossing width even with the corrected sigma0=0.10 start.
EXP-0006 uses a finer p-grid near the anchor at L=256/512 for a definitive
C8 measurement.

## Key Differences from EXP-0005

| aspect | EXP-0005 (frozen) | EXP-0006 (proposed) |
|---|---|---|
| bond_span p-grid L=256/512 | `arange(0.44,0.57,0.02)` (7 pts) | `arange(0.47,0.53,0.004)` (13 pts, step 0.004) |
| bond_span p-grid L<=128 | `arange(0.38,0.63,0.02)` | unchanged |
| bond_wrap p-grid | `arange(0.38,0.63,0.02)` | unchanged |
| site_span p-grid | `0.547746+0.015*k, k=0..6` | unchanged |
| estimator sigma0 | 0.05 (frozen code; failed) | 0.10 (robust; avoids sigma->0 basin) |
| estimator comparison | not recorded | s0=0.05 recorded separately as diagnostic |
| seed | 42 | 42 (deterministic) |
| systems / anchors / n_real | bond_span, bond_wrap, site_span | identical |
| gates / tolerances | chi2_red<4.0, tol_pc=0.01, etc. | identical |
| controls | C1-C8, FG | identical |

## Validation Gates and Controls (identical to EXP-0005)

- **C1**: determinism (n_real=1500, repeat → pair_diff < tol_estimator_pair=0.005)
- **C2**: estimator/BC independence (|bond_span_a − bond_wrap_a| < 0.005)
- **C4**: scale stability (C4 shift < tol_c4_shift=0.005)
- **C5–C7**: RNG inheritance, seed ladder, independent implementation
- **C8**: width-route diagnostic — 0.60 <= 1/nu_width <= 0.90 (report-only, NOT in decision rule)
- **FG**: fit-goodness, chi2_red < 4.0 per system (decision-gating)
- **in_tol**: |p50_a − anchor| < tol_pc=0.01 per system

## Required Result JSON Structure — Estimator Diagnostics Separated

The EXP-0006 results JSON MUST separate physical results from estimator
diagnostics into distinct top-level keys:

- `primary_results`: all gate decisions (C1–C7, FG, in_tol), p_c estimates
  with SEs, FSS fits (a, b, chi2_red) per system. These are the physical
  measurements.
- `estimator_diagnostics`: C8 width-route measurements at multiple sigma0
  values (0.05 comparison + 0.10 primary), width scales per L, MLE vs
  linear-WLS ratios, convergence flags. These are estimator-procedure
  measurements, NOT physical observables.

This separation ensures that a future reader can see exactly which results
depend on estimator choice and which are physical.

## Files Required (not run; listed for implementer)

- `CONFIG/prereg_EXP-0006.json` — frozen prereg (created, not executed)
- `CODE/run_percolation_exp0006.py` — runner with PREREG_PATH override
  (created, not executed)
- `CODE/RESULTS/EXP-0006_results.json` — to be generated on execution
- `CODE/CONFIG/registry.jsonl` — append EXP-0006 row on execution
- `DIAGNOSTICS/EXP-0006_width_route_audit.md` — optional future audit

## Dependency on Frozen EXP-0005

EXP-0006 references EXP-0005 for the C8 comparison (corrected C8=0.7922
from frozen cells). It does NOT modify any EXP-0005 artifacts. All EXP-0005
frozen files (`prereg_EXP-0005.json`, `EXP-0005_results.json`,
`EXP-0005_experiment.json`, registry row) remain unchanged.

## Decision Required

Run EXP-0006 (fine p-grid, sigma0=0.10, deterministic) or accept EXP-0005
INCONCLUSIVE with the documented estimator correction.
