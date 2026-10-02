# Historical 2D percolation audit repair — N-04/N-05/N-19/N-21/N-22

This directory is an isolated, read-only repair area for the historical 2D
percolation findings **N-04, N-05, N-19, N-21, and N-22** only.

It does **not** modify or import the historical runners as generators. The
analysis reads frozen configs/results/caches, recomputes only estimands whose
inputs are present, and refuses to write into any historical path. No expensive
or production Monte Carlo was launched.

## Canonical files

- Scope and immutable evidence list:
  - `CONFIG/audit_scope.json`
  - `CONFIG/historical_evidence_baseline_post_n14.json` (the original
    `historical_evidence_baseline.json` is retained unchanged as the pre-N-14
    snapshot)
- Read-only analysis:
  - `CODE/run_read_only_audit.py`
- Focused tests:
  - `TESTS/test_read_only_audit.py`
- Machine-readable validation:
  - `RESULTS/READ_ONLY_VALIDATION_20260924_POST_N14/validation_report.json`
  - `RESULTS/READ_ONLY_VALIDATION_20260924_POST_N14/run_manifest.json`
- Dependency-aware report (current post-N-14 rerun):
  - `RESULTS/READ_ONLY_VALIDATION_20260924_POST_N14/validation_report.md`
  - `REPORT/VALIDATION_REPORT_20260924.md` (earlier pre-refresh rendering)

The original baseline snapshots exact bytes and SHA-256 hashes for 51 historical
inputs, including configs, results, NPZ/JSON caches, reports, registry rows,
result helpers, and the shared RNG dependency. After the intentional N-14
result-helper repair, the isolated post-N-14 baseline refreshes only that
shared dependency entry; the original baseline remains unchanged. The active
51-entry baseline is checked before and after every analysis.

## Corrected scope

- **N-04 / EXP-0006:** implements
  `p0 + (0.5-w0)*(p1-p0)/(w1-w0)`. Stored aggregate cells exactly regenerate
  the historical p50/FSS values. The current named runner still cannot generate
  the full historical result, and C1/C6 evidence unavailable from stored cells
  remains **INCONCLUSIVE**. No second estimator/control was invented.
- **N-05 / EXP-0007:** keeps requested and accepted counts separate. The p50
  bootstrap accepts 500/500 draws per L; the width bootstrap accepts 495/500.
  The FSS point estimate remains compatible with 0.5, but its SE is 0.03170745,
  3.17 times the 0.01 tolerance. Precision validation is **INCONCLUSIVE**.
- **N-19 / EXP-0009:** C7 is a **same-stream implementation check**, not fresh
  independent sampling.
- **N-21 / EXP-0009:** R3 is an **algebraically coupled internal consistency
  check** because `P_inf=M_max/L²` uses the same mass realizations as `D_f`.
- **N-22 / EXP-0010:** the pooled slope is exactly reproducible but is only an
  exploratory pooled result. The frozen file does not define an individual-size
  `D_f` estimator, and C7 is absent. EXP-0010 is **INCONCLUSIVE**; the historical
  `LATTICE_ARTIFACT` closure is not accepted.

## Focused validation

From the laboratory root:

```powershell
python -m pytest -q 03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/TESTS/test_read_only_audit.py
```

The tests lock every numerical correction:

1. the N-04 denominator and exact stored-cell p50/FSS regeneration;
2. EXP-0007 requested/accepted bootstrap counts and broad FSS uncertainty;
3. EXP-0009 exact raw-cache exponent regeneration and same-stream C7 role;
4. the EXP-0009 `P_inf`/R3 algebraic identity;
5. exact EXP-0010 pooled-slope regeneration and fail-closed individual-size/C7
   classification.

## Re-running the report

The writer refuses to overwrite outputs. A repeat must use a new result/report
path. Historical inputs must still match the baseline:

```powershell
python 03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/CODE/run_read_only_audit.py analyze `
  --output-json <new-validation.json> `
  --output-markdown <new-validation.md> `
  --output-manifest <new-run-manifest.json>
```

No command in this area generates a lattice realization or performs a width
scan. The only random numbers used are deterministic resampling/bootstrap
operations over already-stored cells.
