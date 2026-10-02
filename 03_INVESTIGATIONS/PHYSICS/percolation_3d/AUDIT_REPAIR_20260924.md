# Q-P008 3D percolation audit repair — 2026-09-24

## Status

**Infrastructure repaired; scientific result remains INCONCLUSIVE.**

No corrected production exponent result or new physical claim is authorized.
The historical EXP-0011 pilot, incomplete EXP-0013 log, and old C7 artifacts
remain in place as evidence.

## N-01 — dimension-aware spanning corrected

`percolation/ENGINE/perc_engine.py` now requires an explicit topology dimension
for spanning:

- default `ndim=2` preserves the historical 2D row/column contract;
- `ndim=3` requires `N=L**3`;
- cubic `k_v` means one component intersects `z=0` and `z=L-1`;
- cubic `k_h` means one component intersects `x=0` and `x=L-1` across the full
  volume.

All cubic production/test callers must pass `ndim=3`; dimension is not inferred
from array length.

Regression tests lock four cases:

1. the 2D behavior is unchanged;
2. a fixed-x/y path through opposite z planes is a vertical span;
3. the old z=0 slice-row path is not a vertical span in 3D;
4. an x-directed path at an interior z plane is a horizontal span.

The same occupied-path integration test also confirms propagation through
`run_span_cell_edges`.

## N-02 — repaired runner contract

The canonical repaired runner is:

`CODE/run_audit_repair.py`

It fails closed unless given an explicit immutable config and a new output
directory. It:

- uses opposite 3D planes;
- runs exactly the configured width sample count, one realization at a time;
- keeps ragged exponent arrays rather than truncating all sizes to the minimum;
- validates `tau_L` before any Monte Carlo work;
- requires one flat cluster-size array per realization;
- removes one largest cluster per realization before tail analysis;
- bootstraps tau by realization rather than individual clusters;
- writes per-L compressed raw arrays and SHA-256 manifests;
- never substitutes an unbracketed width point;
- labels the 1/L threshold extrapolation diagnostic-only;
- writes final JSON atomically and refuses to overwrite result artifacts.

The old `run_exp0011.py` path is now a fail-closed stub. Its exact historical
source is preserved at
`CODE/LEGACY_DISABLED/run_exp0011_historical_invalid.py`, SHA-256
`9aed9b99edd0e65fcd0cfd921a48f4514ceed27a9dee558dcf3e9dece05ffb75`.

## Corrected C7 scope

`CODE/REPLICATION/independent_check_EXP0011.py` now uses a separate literal
union-find and plane construction. Its synthetic test proves:

- opposite-z path → `(k_v,k_h)=(1,0)`;
- old z=0 slice path → `(0,0)`;
- full-volume x path → `(0,1)`.

The smoke C7 compares the SciPy engine and union-find on identical repaired
config streams. It is therefore an **implementation cross-check**, not an
independent experimental replication. The current corrected smoke report is
`CODE/REPLICATION/C7_QP008-AUDIT-R1-SMOKE_V2_corrected_report.json`; it passes
4/4 same-stream cells and records that limitation explicitly.

## Smoke verification only

Immutable smoke config:

`CONFIG/prereg_QP008_AUDIT_R1_SMOKE.json`

Config SHA-256:
`ca4c14452a48c93ea6daa2b90c3356b77c4b7c81da3edead04d7ef3ff6abfd80`

Smoke output:

`CODE/RESULTS_AUDIT_REPAIR/QP008_AUDIT_R1_SMOKE_V4/`

The run used deliberately tiny `L={4,6}` samples. Its meaningless smoke
exponents and failed tau fit are retained to prove fail-closed behavior, not to
estimate physics. Final status is `INCONCLUSIVE`; because the required tau
analysis is incomplete, the runner returns a nonzero process status while still
publishing the staged, hash-authenticated result. `SMOKE_V4` is authoritative;
its stored config, runner, and engine hashes match the current files. The
earlier smoke directories are retained only as regeneration history.

The result includes a canonical result-object hash, a separate exact-byte
result sidecar, and raw per-size/width manifests. Focused verification:
**15 tests passed** across the engine, repaired runner, and C7 test suite.

## Still required before production

1. Freeze a separate scientific production config; do not promote the smoke
   config.
2. Revalidate width grids around the corrected finite-size crossings and use a
   preregistered probit fit, not only adjacent-linear diagnostics.
3. Pre-register scientifically justified sizes, realization counts, bootstrap
   draws, stopping/resource rules, and C7 scope.
4. Run the independent C7 over the exact production stream policy and ingest
   its hash/report into the final decision.
5. Preserve all raw arrays and failed/accepted bootstrap counts.
6. Treat incomplete or hash-mismatched artifacts as `INCONCLUSIVE`.

Until those steps are complete, the historical 3D `p_c`, width, and C7 claims
remain invalid/superseded and no 3D exponent conclusion should be announced.
