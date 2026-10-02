# Curated Zenodo deposit (v1.0.0) — preserved

This subtree is the **curated Zenodo deposit**, version 1.0.0, as previously
published at `github.com/Nortaq-PlayNexus/ScientificDiscoveryLab`.

It is preserved here rather than deleted when the full laboratory record was
added to this repository, because it is a **different scope of the same work**,
not an older draft of it:

| | curated deposit | this repository (root) |
|---|---|---|
| files | 47 | 1,122 |
| contents | the three instrument defects, their preregistrations and controls, the hash-chained change logs, the registry | the whole laboratory: 16 experiments, 7 fields, every investigation folder, all audit directories, the shared engine, governance |
| test count | 495 passed (2026-09-28) | 543 passed (2026-10-02) |

Neither supersedes the other. Cite whichever matches your question — if you need
the instrument-defect evidence alone, the deposit is the tighter reference.

## Layout

```
code/            the six audit and diagnostic scripts
data/            production results, audit baselines, registry snapshots,
                 hash-chained change logs
docs/            the two findings, four preregistrations, the registry
                 append-only lock, and snapshots of CHANGELOG /
                 CURRENT_STATUS / DISCOVERY_LOG / DO_NOT_CLAIM as of 2026-09-28
scripts/         the deposit's own integrity verifier
tests_reference/ reference copies of the tests (not standalone-runnable)
manifest.json    the deposit's own record
```

## Integrity

```bash
python tools/verify_deposit_manifest.py
```

Expected: 46 of 47 verified, zero digest mismatches, one missing
(`N004_raw.sqlite3`), exit 0.

## The missing file, and a bookkeeping gap

`data/production/n004_production_20260926_V3/N004_raw.sqlite3` (1.9 MB) is
absent. It was **already absent from the published Git tree** — this is not
something the reorganisation caused.

But the deposit's manifest lists it in `files` while its `omitted_from_git` list
declares only the other bulk binary (the 57.6 MB N001 production database). So
the manifest claims a file it does not account for being absent. That gap is the
deposit's own bookkeeping, and it is reported rather than tolerated: an
unaccounted file is exactly the class of problem this laboratory exists to
surface.

Both databases are carried on Zenodo rather than in git, and remain in the
laboratory under `03_INVESTIGATIONS/PHYSICS/percolation/`.

## Test-suite count difference

The deposit records **495 passed, 0 errors** as of 2026-09-28. The laboratory
recorded **543 passed, 0 failed** as of 2026-10-02, after a pre-publication
verification pass repaired seven tolerance defects
(`CHANGELOG_TEST_TOLERANCE_REPAIR.md`, N-29).

The counts differ because the audit grew between the two dates. The seven
failures repaired are documented, not suppressed. Two were genuine findings: a
reproducibility flag whose `5e-15` bound could never pass yet was recorded
`True`, and a bootstrap confidence interval that matched at one bound to `4e-16`
while differing by `1.4e-03` at the other — the signature of a different
accepted draw set, which the stored artifact had already recorded.