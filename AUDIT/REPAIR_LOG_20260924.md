# Science audit repair log — 2026-09-24

This log records implementation repairs only. Historical experiment outputs
remain evidence and are not retroactively converted into valid results.

The machine-readable handoff is `AUDIT/REPAIR_MANIFEST_20260924.json`
(SHA-256 `ab3ca4115cc935e93f06f10a61d0a05c16aa12e197a95dce6d60a4fb0ab4383e`); it
records strict hashes, validation statuses, test counts, and explicit claim
guards.

## Completed infrastructure repairs

### N-06/N-07/N-08 — corrected prime-gap audit path

- Added isolated repair:
  `03_INVESTIGATIONS/MATHEMATICS/prime_gaps/AUDIT_REPAIR_N06_N08/`.
- Uses lower-prime normalization, true step-up BH, and log-survival tails;
  underflow is JSON `null` plus `log10_p_value`, never artificial `0.0`.
- The first exponential bin is structurally empty because its upper edge
  `0.1053605` is below every admissible parity floor in the four decade
  blocks. A parity-geometric surrogate retains the even-gap lattice but is
  explicitly non-scientific and omits wheel/singular-series/dependence terms.
- Corrected segmented sieve retains all 5,761,455 primes in `[0,10^8)` and
  matches trusted small-limit/non-aligned-boundary controls.
- Twelve historical evidence hashes verify unchanged. No `10^9`/`10^10` run,
  persistence claim, mechanism, or novelty claim was made.
- Focused verification: **14 passed**.

### N-04/N-05/N-19/N-21/N-22 — historical 2D percolation provenance

- Added isolated read-only audit:
  `03_INVESTIGATIONS/PHYSICS/percolation/AUDIT_REPAIR_N04_N05_N19_N21_N22_20260924/`.
- A 51-file before/after SHA-256 baseline confirms no historical input changed.
  The original baseline is retained unchanged; an isolated post-N-14 baseline
  refreshes only the intentionally repaired shared result helper and is used
  for the current read-only validation. The post-refresh validation is in
  `RESULTS/READ_ONLY_VALIDATION_20260924_POST_N14/`.
- EXP-0006 stored p50/SE/FSS values regenerate exactly with denominator
  `w1-w0`; required realization-level C1 and extra-seed C6 evidence are absent,
  so complete provenance/control closure remains INCONCLUSIVE.
- EXP-0007 reproduces 500/500 p50 draws and 495/500 width draws. Its point
  estimate is compatible with 0.5, but FSS SE=0.03170745 is 3.17× the 0.01
  tolerance; ±0.01 precision validation is rejected.
- EXP-0009 C7 is labelled a same-stream implementation check; R3 is labelled
  algebraically coupled because `P_inf=M_max/L^2` uses the D_f mass data.
- EXP-0010's pooled D_f is exactly reproducible but exploratory; the frozen
  individual-size gate is not identifiable from available raw quantities and
  required C7 is absent. Historical `LATTICE_ARTIFACT` is not accepted.
- Focused verification: **10 passed**.

### N-001 — Q-P007 cluster-tail/tau pipeline

- Added isolated repair area:
  `03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/`.
- Raw cluster arrays are one flat non-increasing `int64` array per realization
  and p-c arm in SQLite; full arrays and exact tails are retained.
- Canonical/refined masks are paired through common uniform fields.
- Bootstrap resamples realization blocks, not individual clusters.
- `tau_L` is config-driven and validated before execution.
- Production profile is confirmation-guarded and was not launched.
- Integration review found and corrected the cumulative conversion:
  `tau = 1 - slope`, not `tau = slope`.
- Authoritative smoke: `RESULTS/SMOKE_N001_V3` (manifest schema v2; summary schema v3);
  `SMOKE_N001`, `SMOKE_N001_CORRECTED`, and `SMOKE_N001_V2` are retained
  as superseded evidence only.
- The authoritative cumulative smoke slope is `-0.9018299824`, mapped with
  `tau = 1 - slope` to `1.9018299824`; this is infrastructure output, not a
  scientific result.
- Focused verification: **14 passed**. A sequential rerun completed in 4.6s;
  the earlier 300-second timeout was not reproduced (no concurrent pytest run
  was used for the final check).

No production tau or refined-p-c conclusion is supported yet.

### N-01/N-02/N-03 — 3D percolation

- Added explicit `ndim=2/3` spanning semantics; cubic callers use opposite 3D
  planes rather than 2D slice rows.
- Added 2D compatibility, opposite-z, old-slice rejection, full-volume-x, and
  real graph integration tests.
- Added a fail-closed repaired runner with exact sample counts, ragged arrays,
  active `tau_L`, flat tails, realization bootstrap, raw hashes, and no
  unbracketed-width substitution.
- Archived the invalid historical runner and replaced its old path with a
  refusing stub.
- Rebuilt C7 with an independent union-find/plane implementation. The current
  smoke C7 report (`C7_QP008-AUDIT-R1-SMOKE_V2_corrected_report.json`) passes
  4/4 same-stream cells and is explicitly labelled an implementation
  cross-check, not independent experimental replication.
- Current authoritative smoke output: `CODE/RESULTS_AUDIT_REPAIR/QP008_AUDIT_R1_SMOKE_V4`;
  it is a deliberately tiny `INFRASTRUCTURE_SMOKE_PARTIAL` with exact-result
  sidecar and per-realization width/raw manifests. The runner returns a nonzero
  status for incomplete smoke and the result remains `INCONCLUSIVE`.
- Repair report: `03_INVESTIGATIONS/PHYSICS/percolation_3d/AUDIT_REPAIR_20260924.md`.
- Focused verification: **15 passed**.

No corrected production 3D p-c or exponent result exists.

### N-002 — EXP-0003 broadband audit integration

The completed independent fixed-spectrum audit supports a finite-sampling and
spectral-resolution interpretation, not a novel physical transition. A
non-destructive validator confirmed all **38/38** original manifest entries.
The malformed source manifest was preserved; valid sidecars and validation
evidence are in `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924/`.

### N-003 — Feigenbaum z=3/z=4 repair integration review

- The isolated high-precision repair at
  `03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/AUDIT_REPAIR_N003_FEIGENBAUM/`
  was independently reviewed against its frozen protocol and historical-artifact
  isolation rule.
- All seven focused tests pass. The 100-digit, period-certified finite
  sequences are retained in the repair result/report; z=2 is a known-limit
  reproduction, z=3 has a final finite decrease at n=9→10, and z=4 decreases
  after n=6. No monotone convergence claim is made for z=3/z=4.
- No alpha estimate is reported because no spatial scaling variable is defined.
  The historical EXP-0014 artifacts remain untouched and are not promoted to
  repaired evidence.
- Focused verification: **7 passed**.

### N-004 — dependence-aware RNG calibration smoke

- Added isolated repair:
  `03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_RNG_CALIBRATION/`.
- The historical EXP-0004 “CERTIFIED” conclusion remains withdrawn. The repair
  exactly replays the stored 80×24 audit matrices, labels the shared-array
  dependence, and uses per-test/row-preserving diagnostics without pooled-p
  inference.
- A bounded stream-plumbing smoke is recorded at
  `RESULTS/SMOKE_N004_20260924_V2`; it performs no production battery analysis,
  emits no decision field, and sets `scientific_result=null`. The first
  `SMOKE_N004_20260924` directory is retained as superseded smoke evidence.
- Historical runner, preregistration, result, C7, shared battery, and audit
  hashes are checked before execution. No production RNG calibration run was
  launched.
- Focused verification: **9 passed**.

### N-009 / S9 provenance classification

- Added isolated read-only audit:
  `AUDIT/S9_PROVENANCE_20260924/`.
- The external battery source and in-tree Q-S9-1/Q-S9-3 JSON files were read
  without importing or executing the package. The audit found simulated
  response models, hard-coded rates, no raw empirical loaders, and zero raw
  image/data files in the declared package.
- Classification is `SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE`; A==B,
  dose-response, wavelength, and biological/perceptual interpretations are
  not supported as empirical findings.
- External and historical/in-tree files were not modified. The machine-readable
  report is `S9_PROVENANCE_20260924/RESULTS/provenance_report.json`.
- Focused verification: **3 provenance tests passed; read-only run PASS**.

### N-11 — immutable preregistrations

- `freeze_config()` now uses exclusive file creation and fails rather than
  overwriting a frozen protocol.
- Frozen documents contain a canonical SHA-256 and load-time integrity check.
- Amendments use a separate SHA-256 hash-chained change log.
- Seven focused tests cover overwrite refusal, tamper detection, payload
  mismatch, nonfinite rejection, and change-chain verification.

### N-13 — user-facing scientific metadata

- Formal charge now uses `Chem.GetFormalCharge`; partial charge has a separate
  field.
- Molecular 2D depictions return valid PNG bytes.
- Unknown/unmodeled reaction interactions remain E0 `INSUFFICIENT DATA` rather
  than being upgraded to E3 interaction claims.
- A tautological plant test was replaced with exact assertions.
- Focused application tests: **44 passed**.

### N-14 — result provenance

- Canonical JSON result hashes now have an explicit scope and reject nonfinite
  values.
- Exact result-file byte hashes are stored separately when `result_path` is
  supplied, with a verifier for both scopes.
- Four focused provenance tests pass.

### N-17 — pytest database isolation

- Database URLs are environment-configurable.
- Pytest now imports into a process-specific temporary SQLite database before
  test modules load.
- Full suite after adding isolated repair tests: **375 passed / 411 warnings**.
- Persistent `sovereign_biolab.db` SHA-256 remained unchanged:
  `e7dfc79cdb696b39ae3578e4427b0a026b107655a1a359c5562edc2d46b087b9`.

### N-15/C-015 — collision and external-dossier hold

Both water-response scaffolds now contain explicit
`PROPOSAL_NOT_REGISTERED.md` notices. Neither `EXP-0015` label is treated as an
authoritative experiment until a unique ID and immutable preregistration are
allocated.

The 2026-09-18 external researcher dossier is placed under an audit hold.
Every document now points to `05_EXTERNAL_RESEARCHER_DOSSIER/AUDIT_SUPERSESSION_NOTICE.md`;
it must not be sent unchanged because its external sandbox/raw-data chain and
related historical claims were not fully verified in this tree.

## Still unresolved

- No production Q-P007 tau run. Its repair config is manifest-hash-bound but
  was authored during the audit, so production still needs a separate
  immutable pre-run preregistration lock.
- No preregistered production 3D run.
- EXP-0003 exact novelty remains unresolved and no novelty is claimed.
- Preregistration change logs are internally hash-chained, but there is no
  external signature/anchor yet; a wholesale valid-chain rewrite remains
  possible.
- Feigenbaum z=3/z=4 integration review is complete for the finite repaired
  sequences, but a production-quality convergence claim remains unsupported;
  the finite scans do not prove that unresolved sign changes are absent.
- A production-scale dependence-aware RNG calibration remains unresolved; the
  N-004 smoke is infrastructure-only. A dependence-calibrated finite-range
  prime-gap null, missing EXP-0006 C1/C6 evidence, and historical registry
  chronology remain unresolved. S9 provenance is now classified as
  synthetic/derived; empirical reclassification still requires new raw data and
  a new preregistration.
- Do not launch the old 3D runner or the planned 10^10 prime-gap sieve.
