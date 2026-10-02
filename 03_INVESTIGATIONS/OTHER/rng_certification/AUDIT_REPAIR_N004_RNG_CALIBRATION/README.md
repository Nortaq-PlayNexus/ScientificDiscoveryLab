# N-004 RNG calibration audit repair

This isolated area addresses the unresolved N-004 dependence/calibration
finding without modifying the historical EXP-0004 runner, preregistration,
results, C7 files, or shared battery.

## Scope

- Strictly replays the stored 80-seed × 24-test audit matrix and requires its
  summaries to match exactly within floating-point tolerance.
- Labels the battery stream as `historical_shared_arrays`: the same bit array
  feeds multiple tests, so pooled p-value independence is not assumed.
- Reports per-test marginals, Holm step-down family-wise diagnostics, and
  dependence/row-preserving smoke only.
- Performs a bounded generator plumbing check below production stream sizes;
  it does not run a production battery or infer generator quality.
- Verifies strict historical input hashes and refuses overwrite.

The historical EXP-0004 “CERTIFIED” conclusion remains withdrawn. This repair
cannot certify a generator or create a scientific result.

## Freeze and run

From the laboratory root:

```powershell
python 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_RNG_CALIBRATION/CODE/freeze_n004.py
python 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_RNG_CALIBRATION/CODE/run_n004_smoke.py `
  --output-dir 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_RNG_CALIBRATION/RESULTS/SMOKE_N004_20260924_V2
```

The freeze command is exclusive-create. The smoke output must contain
`status=INFRASTRUCTURE_SMOKE_ONLY`, `scientific_result=null`,
`certification_claim=false`, and `production_run_launched=false`, with no
`decision` field.

## Focused tests

```powershell
python -m pytest 03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_RNG_CALIBRATION/TESTS/test_n004_smoke.py -q
```

A separately approved production protocol would still require fresh seeds,
both `2^18` and `2^22` bit scales, a declared dependence model, and an
independent/full implementation. It is not provided here.
