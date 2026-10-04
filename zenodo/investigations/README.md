# Per-investigation deposits — 9 drafts, ready to publish

Created 2026-10-04. **All drafts. None published. No DOI minted.**

Each is one **investigation**, not one experiment. Q-P004 spans EXP-0005/0006/0007
and Q-P005 spans EXP-0009/0010, so splitting those across separate DOIs would
scatter one scientific answer across four identifiers.

Every archive is byte-reproducible — two independent builds give an identical
digest — and every upload was verified against Zenodo's stored copy: file count 1,
byte size matching.

Raw simulation output (362 MB of `.npz` / `.sqlite3`) is excluded from all nine.
It is regenerable from the seeds in each preregistration, and shipping it would
make the optics and percolation archives orders of magnitude larger for no gain in
verifiability. The code that consumes it is included; its inputs are not.

---

| # | Draft | Investigation | Exp | Size |
|---|---|---|---|---|
| 1 | [23132744](https://zenodo.org/deposit/23132744) | Speckle contrast law | EXP-0002 | 86 KB |
| 2 | [23132746](https://zenodo.org/deposit/23132746) | Vortex density in random wave fields | EXP-0003 | 150 KB |
| 3 | [23132748](https://zenodo.org/deposit/23132748) | Discrete optical-vortex detection bias | EXP-0015 | 309 KB |
| 4 | [23132753](https://zenodo.org/deposit/23132753) | Topology-measurement definition | EXP-0016 | 1.1 MB |
| 5 | [23132759](https://zenodo.org/deposit/23132759) | Laboratory RNG statistical certification | EXP-0004 | 251 KB |
| 6 | [23132761](https://zenodo.org/deposit/23132761) | Percolation thresholds and exponents | EXP-0005/6/9/10/17 | 547 KB |
| 7 | [23132763](https://zenodo.org/deposit/23132763) | Feigenbaum universality | EXP-0014 | 67 KB |
| 8 | [23132767](https://zenodo.org/deposit/23132767) | Prime gap statistics | EXP-0008 | 168 KB |
| 9 | [23132771](https://zenodo.org/deposit/23132771) | Water acoustic response simulator | — | 34 KB |

Total 2.7 MB across all nine.

## Subjects — add these in the web form

**Zenodo's deposition API accepts `subjects`, reports success, and stores none of
them.** All nine have zero. Each needs ~15 seconds.

Values are in `zenodo/investigations/<slug>.json` under `subjects`. Common ids:

| id | title |
|---|---|
| `mesh:D015203` | Reproducibility of Results |
| `mesh:D010825Q000379` | Physics/methods |
| `mesh:D012106Q000706` | Research/statistics & numerical data |
| `euroscivoc:805` | Statistical mechanics |
| `euroscivoc:1061` | Numerical analysis |

## Then

1. Publish each one.
2. Read it back: `https://zenodo.org/api/records/<id>` — confirm `subjects` is
   populated. **Do not assume.** Every v1 record so far published with zero
   subjects and nobody checked, because Zenodo reports success either way.
3. Add the DOIs to `zenodo/investigations/DEPOSITS.json` and to
   `RELEASE.md`.
4. Commit and push.

---

## Not published, deliberately

| | |
|---|---|
| **EXP-0008** (`code\EXP0008`) | On hold. `FALSIFICATION_RECORD.md` shows the headline claims are hand-authored — `restore_csvs.py` writes the results table as string literals. Publish the null results only. Note this is a *different* EXP-0008 from the lab's, which is prime gaps and is draft 23132767. |
| **EXP-0011** | INPROGRESS, preregistration FROZEN, no results. Nothing to publish. |
| `coherent-optical-ai-sandbox` | Already published: `10.5281/zenodo.22849652`. Do not re-upload. |
| `dmt-laser-s9-battery` | Already inside the laboratory record, audited as `SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE`. |
| AI-consciousness battery | Already published: `10.5281/zenodo.23111535`. Also present inside the laboratory record as EXP-C001. |

---

## Registry correction made while preparing these

`EXPERIMENT_REGISTRY.md` was found to be **incomplete as a record**:

- **EXP-0015, EXP-0016 and EXP-0017 had detail sections but no row in the summary
  table.** A reader consulting only the table would not know they existed.
- **EXP-0013 has neither a row nor a detail section.** It appears in prose only;
  no preregistration, results directory or config could be found. Recorded as
  `NOT REGISTERED` rather than silently omitted — an unexplained gap in an
  append-only registry is itself a defect.
- **EXP-0012 is skipped with no explanation.** The header says IDs are allocated
  in order and never reused, which makes a gap a record-keeping event. No
  allocation or cancellation note exists.

All three gaps predate the correction. Table rows were added and a note recorded;
**no detail section, result, or evidence level was altered.**

## Toolbox

| Script | Purpose |
|---|---|
| `tools/build_investigation_packages.py --stage --verify` | build the nine byte-reproducible archives |
| `tools/make_investigation_metadata.py` | derive metadata from each investigation's own files |
| `tools/upload_investigations.py --dry-run` | validate without sending |
| `tools/upload_investigations.py` | create and populate; records each draft id to `DEPOSITS.json` immediately, before uploading |

`DEPOSITS.json` is written before each upload, so an interruption cannot lose
track of what exists. `--reuse` resumes rather than creating a second deposit.

See `HANDOFF.md` at the repository root for the Zenodo API traps.