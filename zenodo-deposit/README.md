# ScientificDiscoveryLab — instrument validation and self-audit

This repository holds the code, documentation, tests and machine-readable
results behind three defects found by a self-audit of an autonomous simulation
laboratory. **No scientific discovery is claimed.**

| # | Finding | Status |
|---|---|---|
| 1 | A PRNG statistical test applies a spurious `sqrt(2)` to a statistic the standard already defines in `erfc` units | `ESTIMATOR_DEFECTIVE`; corrected cell status `UNRESOLVED_NOT_APPLICABLE` |
| 2 | A 2D percolation cluster-mass exponent rests on an estimator biased upward by +0.11 to +0.35 | `ESTIMATOR_BIASED`; deviation from Fisher **strengthened** |
| 3 | A reproducibility control pinned an append-only registry by whole-file hash | Repaired **without refreshing any baseline** |

Test suite: **495 passed, 0 errors** (was 391 passed / 10 errors).

## What is not in this repository

The 60 MB percolation raw SQLite database is **not committed**, to keep the
repository usable. It is attached to the GitHub release and deposited on Zenodo.
Its expected SHA-256 is recorded in `manifest.json`, so you can confirm the copy
you obtained is the right one:

    expected sha256 prefix: 9f421d06732d1d05

## Verify the claims yourself

```bash
python scripts/verify_historical_integrity.py
```

This re-computes SHA-256 digests and checks them against values recorded at the
time each artifact was written — from the laboratory's own manifests, not from
prose. It never writes anything. A missing bulk file is reported as `SKIP` with
its expected digest, not as a pass.

## Honest limitations

- Q-P007 remains **open**. The deviation's *direction* is robust under every
  estimator and window; its *magnitude* is not trusted.
- `CROSSOVER_NOT_ESTABLISHED` is not crossover excluded. Three sizes spanning a
  factor of four cannot see a slow drift.
- The *mechanism* of the exponent bias is **not established**, only its
  magnitude. Two hypotheses were tested and rejected; a third was not found.
- Both preregistrations are labelled **informed, not blind** and state exactly
  what had been seen before they were frozen.
- The statistical test's defect is provable as an exact algebraic identity, but
  its empirical *detection* is resolution- and seed-dependent.

## Layout

```
code/             analysis code for both findings
docs/             preregistrations, findings write-ups, lab record, do-not-claim
data/results/     machine-readable results and rendered reports
data/production/  the instruments and inputs the claims are about
data/chains/      hash-chained change logs
tests_reference/  byte-copies of the tests as run in the laboratory
scripts/          integrity verification
manifest.json     SHA-256 of every file in the full package
```

The files in `tests_reference/` are byte-copies for inspection. They are **not**
runnable here: they import from laboratory-relative paths. The authoritative
tests live in the laboratory tree.

## Scope note

This project is **unrelated** to DOI `10.5281/zenodo.22849652` (EXP-0007,
coherent optical vortex propagation). The two share no data, code, or
conclusions.

## License

MIT — see `LICENSE`.
