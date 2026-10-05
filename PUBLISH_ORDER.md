# PUBLISH ORDER — completed 2026-10-04

> **This file is a record of what was published, in the order it was published.
> It is not a to-do list.** It previously read as twelve live instructions with
> deposit links and a "paste subjects, then Publish" step per record. All twelve
> are published and verified. `PUBLICATION_VERIFICATION.md` carries the
> verification; this file carries the order and the reasoning.

**Nothing was deleted except one unusable draft. Every published record is intact
and resolving.**

> **Subjects: 0 of 12.** The paste step below did not work. The web form did not
> persist the field either, and published records are immutable, so this is
> permanent for all twelve. It is recorded as D2 in
> `PUBLICATION_VERIFICATION.md` rather than quietly dropped.

---

## Before you start: two things per record, ~20 seconds each

1. ~~**Paste subjects** in the web form.~~ **Did not take.** Zenodo's API accepts
   the field, reports success, and stores none of it — tested against both
   endpoints on a live draft. The web form did not persist it either.
2. **Publish.** Done, all twelve.

Read-back is still the rule: `https://zenodo.org/api/records/<id>`. Every v1
record published with zero subjects and nobody checked, because Zenodo reports
success either way. This time it was checked, and the zero was found.

Subject values are in `zenodo/investigations/<slug>.json`.

---

# Group A — the umbrella records

Published first. The nine investigations cite the laboratory record, so a reader
arriving at any of them has a canonical parent to land on.

## 1. ScientificDiscoveryLab v2.0.0 — PUBLISHED

**`10.5281/zenodo.23122787`** (was draft 23122787)

The master record: registries, governance rules, and the self-audit that found
four defects in the laboratory's own instruments. References landed (6 of 6).
Subjects did not (0 of 8 attempted).

## 2. Consciousness Indicator Battery v3.0.0 — PUBLISHED

**`10.5281/zenodo.23122664`** (was draft 23122664)

New version of `10.5281/zenodo.23111535`, same concept `10.5281/zenodo.23101902`.
House title style applied. No scientific change.

**This is the record with defect D1**: it does not rebuild byte-for-byte from the
repository. Remedy staged as v3.0.1, draft `23137224`, not yet published.

## 3. Phantom Vision Lab v2.0.0 — PUBLISHED

**`10.5281/zenodo.23123095`** (was draft 23123095)

New version of `10.5281/zenodo.23112116`, same concept `10.5281/zenodo.23112115`.
No scientific change.

---

# Group B — the nine investigations

Published in experiment-number order, matching `EXPERIMENT_REGISTRY.md`, so a
reader following the registry lands in the same order. Each cites
`10.5281/zenodo.23109117` (laboratory v1) and the GitHub repository.

All nine verified `BYTE_IDENTICAL` against the local build.

| # | Investigation | DOI | Size |
|---|---|---|---|
| 4 | Speckle contrast law — EXP-0002 | `10.5281/zenodo.23132744` | 86 KB |
| 5 | Vortex density — EXP-0003 | `10.5281/zenodo.23132746` | 150 KB |
| 6 | RNG statistical certification — EXP-0004 | `10.5281/zenodo.23132759` | 251 KB |
| 7 | Percolation thresholds and exponents — EXP-0005/0006/0009/0010/0017 | `10.5281/zenodo.23132761` | 547 KB |
| 8 | Prime gap statistics — EXP-0008 | `10.5281/zenodo.23132767` | 168 KB |
| 9 | Feigenbaum universality — EXP-0014 | `10.5281/zenodo.23132763` | 67 KB |
| 10 | Discrete optical-vortex detection bias — EXP-0015 | `10.5281/zenodo.23132748` | 309 KB |
| 11 | Topology-measurement definition — EXP-0016 | `10.5281/zenodo.23132753` | 1.1 MB |
| 12 | Water acoustic response simulator — no experiment ID | `10.5281/zenodo.23132771` | 34 KB |

Two of these carry caveats a reader can easily miss:

- **#6 RNG certification** carries the T03_runs defect: a z-score conversion
  applied to a statistic already in `erfc` units. Reads as
  `UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION`.
- **#7 Percolation** is the one carrying the most: the biased exponent estimator,
  the crossover refutation, and the pooling attribution. **It is where a reader
  is most likely to over-read the results.** Pair it with
  `AUDIT/DO_NOT_CLAIM.md`.

**#8 is the laboratory's EXP-0008 (prime gaps).** Unrelated to the separate
`code\EXP0008` project, which is on hold.

**#12** is a simulator with controls. No empirical claim.

---

# Deleted

| Draft | Why |
|---|---|
| `23110728` | `[UNUSABLE DRAFT]` — 0 files, 0 keywords, 0 creators, licence reverted to `cc-by-4.0`, and concept `23110727` instead of `23101902`. Failed attempt at creating battery v2 through the legacy endpoint, whose `conceptrecid` is accepted then ignored. Never published, so nothing public was lost. Deleted on 2026-10-04 at the maintainer's instruction. |

Audited all thirteen pending deposits first. The other twelve all carried a file,
a full description, keywords, a creator and an MIT licence. This was the only
degenerate one.

---

# Not published

| | |
|---|---|
| `code\EXP0008` (DMT/psychedelic) | On hold. `FALSIFICATION_RECORD.md` shows the headline claims are hand-authored — `restore_csvs.py` writes the results table as string literals. Publish the null results only. |
| **EXP-0011** | INPROGRESS, preregistration FROZEN, no results. |
| battery v3.0.1 | Staged as draft `23137224`, unsubmitted. Closes D1. Not science. |
| `coherent-optical-ai-sandbox` | Already published: `10.5281/zenodo.22849652`. |
| `dmt-laser-s9-battery` | Already inside the laboratory record. |

---

# Currently published — all verified resolving

| DOI | What |
|---|---|
| `10.5281/zenodo.23101903` | battery v1 (superseded on metadata, still citable) |
| `10.5281/zenodo.23111535` | battery v2 |
| `10.5281/zenodo.23122664` | battery v3.0.0 — see D1 |
| `10.5281/zenodo.23109117` | ScientificDiscoveryLab v1 |
| `10.5281/zenodo.23122787` | ScientificDiscoveryLab v2.0.0 |
| `10.5281/zenodo.23112116` | Phantom Vision Lab v1 |
| `10.5281/zenodo.23123095` | Phantom Vision Lab v2.0.0 |
| `10.5281/zenodo.23132744` | Speckle contrast law |
| `10.5281/zenodo.23132746` | Vortex density |
| `10.5281/zenodo.23132748` | Discrete vortex detection bias |
| `10.5281/zenodo.23132753` | Topology-measurement definition |
| `10.5281/zenodo.23132759` | RNG certification |
| `10.5281/zenodo.23132761` | Percolation thresholds and exponents |
| `10.5281/zenodo.23132763` | Feigenbaum universality |
| `10.5281/zenodo.23132767` | Prime gap statistics |
| `10.5281/zenodo.23132771` | Water acoustic response |
| `10.5281/zenodo.22849652` | EXP-0007, coherent optical vortex |

**17 DOIs, all resolving.**