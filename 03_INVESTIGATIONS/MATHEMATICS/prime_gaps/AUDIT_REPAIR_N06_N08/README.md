# Isolated audit repair: Q-M007/Q-M008 N-06/N-07/N-08

This directory is a new audit artifact. It does not edit or overwrite the
historical Q-M007/Q-M008 runners, configurations, results, or reports.

Scope is deliberately limited to the second-pass findings:

- **N-06:** lower-prime normalization, step-up BH, and log-survival tails;
- **N-07:** a segmented sieve whose first segment retains every prime through
  `10^8`;
- **N-08:** the Q-M007 one-degree-of-freedom survival arithmetic, retained
  only as an exploratory numerical screen.

The runner executes a matched smoke over the four EXP-0008 lower-prime decade
blocks through `10^8` (with a small overscan to retain the successor of the
last lower prime). It does **not** run `10^9` or `10^10`.

## Files

- `run_audit_repair.py` — isolated runner, strict config validation, segmented
  sieve, support-aware diagnostic, and exclusive output writer.
- `CONFIG/prereg_pga_audit_n06_n08_20260924.json` — frozen descriptive smoke
  configuration.
- `CONFIG/prereg_pga_audit_n06_n08_20260924.sha256` — freeze sidecar. The
  runner refuses a config whose exact bytes do not match.
- `tests/test_audit_repair.py` — focused numerical, sieve, boundary, and
  fail-closed tests.
- `RESULTS/MATCHED_1E8_20260924/` — created only by a successful run; contains
  raw counts/moments, derived diagnostics, a report, and an artifact manifest.

## Run focused tests

From the repository root:

```text
python -m pytest "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/AUDIT_REPAIR_N06_N08/tests/test_audit_repair.py" -q
```

## Run the descriptive smoke

```text
python "03_INVESTIGATIONS/MATHEMATICS/prime_gaps/AUDIT_REPAIR_N06_N08/run_audit_repair.py"
```

The output writer is exclusive: an existing raw/derived/report/manifest is a
hard failure. Missing or malformed frozen inputs, hash mismatches, changed
historical evidence, incomplete segment coverage, and a request involving the
`10^10` production limit all fail closed.

The parity-geometric calculation is a discrete **diagnostic surrogate**. It
retains the exact even-gap support of the declared local model, but it is not
a complete Gallagher/Hardy–Littlewood null: wheel, singular-series, endpoint,
and consecutive-pair dependence remain unresolved. The output is descriptive
only and makes no novelty or discovery claim.
