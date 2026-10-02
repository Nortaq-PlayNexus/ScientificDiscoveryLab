# Q-P007 / N-001 audit repair area

**Finding:** Priority 0 `N-001` only (cluster-size storage and dependence-aware `tau`).  
**Status:** infrastructure repair and deterministic smoke only; no production `L={256,512,1024}` run was launched.  
**Historical evidence:** the files in `Q-P007/CODE` and `Q-P007/CODE/RESULTS` are read-only evidence and are not imported or overwritten by this runner.

## Historical evidence inspected before repair

The audit began by reading `Q-P007/CODE/run_q_p007.py`, `Q-P007/CODE/run_phase2.py`, `Q-P007/CODE/run.log`, the frozen historical config, `EXP-0009-pc_results.json`, and all three historical `EXP-0009-pc_L*_cells.npz` caches. The caches contain only `masses`, `chis`, `pinfs`, `sizes_n`, and `sizes_n_total`; their `sizes_n` values are one per realization and do not preserve the cluster-size arrays. Audit evidence inspected includes `AUDIT/NEXT_EXPERIMENTS.md` (`N-001`), `AUDIT/BUGS.md` (`B-001`, `B-009`, `B-012`), `AUDIT/AUDIT_LOG.md`, and `AUDIT/INDEPENDENT_AUDIT_20260924/corrected_tau_reanalysis.py` plus its result/evidence files.

A final comparison against `AUDIT/INDEPENDENT_AUDIT_20260924/file_manifest.json` checked all 17 pre-existing Q-P007 records: zero changed and zero missing. No historical Q-P007 file was rewritten.

## Canonical files

- Runner: `CODE/run_n001.py`
- Configuration (both guarded profiles): `CONFIG/n001_repair_config.json`
- Focused tests: `TESTS/test_n001_runner.py`

There is one runner and one configuration. The configuration's `smoke` profile is for infrastructure tests. The `production` profile records the N-001 design but is guarded by an explicit confirmation phrase.

## Raw-data contract

Each realization has an explicit ID (`L{L:04d}-r{index:06d}`) and one common uniform field. That field is thresholded separately at canonical and refined `p_c`, so the two arms are paired by realization ID.

The non-JSON raw artifact is a SQLite3 database with one `full_sizes` BLOB per `(L, realization_id, p_c arm)`. Every BLOB decodes to exactly one flat, non-increasing, little-endian `int64` cluster-size array. The largest entry is removed independently in each realization; the complete tail is exactly `full_sizes[1:]`. Full arrays, tail hashes, packed masks, common-uniform hashes, seed material, requested counts, and effective counts are retained.

The JSON manifest is not a substitute for the binary raw artifact. It records the SQLite SHA-256, schema, configuration SHA-256, profile, active `tau_L`, explicit realization IDs, mask hashes, and requested/effective sample counts. The validator rejects missing files, hash mismatches, malformed SQLite, unexpected schemas, duplicate or incomplete IDs, non-reproducible masks, non-flat arrays, wrong population sums, nested-array metadata, and empty stored tails.

## Analysis contract

Cumulative and histogram fits are recomputed from raw tails. Uncertainty uses paired contiguous realization-block resampling; with the configured `block_size=1`, the resampling unit is the independent realization, never an individual cluster. Canonical and refined arms use the same sampled realization indices in each replicate. Fit diagnostics and successful bootstrap counts are reported without an iid-cluster fallback.

The active `tau_L` is read from the selected profile. It is not hard-coded, and validation fails if it is absent from that profile's `L_list`.

## Deterministic smoke command

From the laboratory root:

```powershell
python 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/CODE/run_n001.py run `
  --config 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/CONFIG/n001_repair_config.json `
  --profile smoke `
  --output-dir 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/RESULTS/SMOKE_N001_V3
```

The runner refuses to overwrite an existing output directory. It stages output, validates the manifest and database, and renames only after success. The smoke summary has `scientific_result: null` by construction.

### Integration-review correction (2026-09-24)

The first smoke directory, `RESULTS/SMOKE_N001`, is retained as historical
evidence but its **cumulative `tau` conversion was wrong**: it reported the
survival slope instead of `1 - slope`. The raw SQLite arrays were not affected.
The cumulative model is `N_>(s) ~ s^{-(tau-1)}`, so the authoritative smoke is
now `RESULTS/SMOKE_N001_V3` (manifest schema `n001-qp007-manifest-v2`, summary
schema `n001-qp007-summary-v3`), where slope `-0.9018299824` maps to
`tau = 1.9018299824`. `SMOKE_N001_CORRECTED` and `SMOKE_N001_V2` are retained
as superseded repair evidence and must not be used for current numerical fits.
A dedicated synthetic-tail regression locks the conversion, and the V3
manifest is bound to the current canonical runner hash.

Focused test command:

```powershell
python -m pytest -q 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/TESTS/test_n001_runner.py
```

## Production guard (not run during this repair)

The following command records the intended design but is intentionally not part of the N-001 smoke execution:

```powershell
python 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/CODE/run_n001.py run `
  --config 03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/AUDIT_REPAIR_N001/CONFIG/n001_repair_config.json `
  --profile production `
  --confirm-production N-001-PRODUCTION `
  --output-dir <new-production-path>
```

## Unresolved scientific/statistical issues

- A deterministic smoke fit cannot estimate the production realization variance or power to distinguish the historical `1.98` discrepancy from `187/91`.
- `p_c` is a fixed historical refined input here; threshold uncertainty and re-estimation are outside this storage/`tau` repair.
- Histogram bins and cumulative survival estimates are correlated. The weighted chi-square-like value is diagnostic, not an independent goodness-of-fit test.
- Realization bootstrap addresses dependence among clusters from the same realization. Any cross-realization block dependence not represented by the configured contiguous blocks remains unresolved.
- The repair config is hash-bound into every manifest and later edits are
  detected, but it was authored during the audit repair rather than being a
  historical pre-results preregistration. A production run still requires a
  separately immutable, content-addressed preregistration lock.
- No scientific `tau` or refined-`p_c` conclusion follows from this infrastructure-only run.
