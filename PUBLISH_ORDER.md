# PUBLISH ORDER — 12 drafts

**Nothing has been deleted except one unusable draft. Every published record is
intact and resolving.** All twelve below are complete, verified, and waiting.

---

## Before you start: two things per record, ~20 seconds each

1. **Paste subjects** in the web form. Zenodo's API accepts the field, reports
   success, and stores none of it — tested against both endpoints on a live
   draft. All twelve currently have **zero subjects**.
2. **Publish.**

Then **read it back**: `https://zenodo.org/api/records/<id>` — confirm `subjects`
is populated. Do not assume. Every v1 record so far published with zero subjects
and nobody checked, because Zenodo reports success either way.

Subject values are in `zenodo/investigations/<slug>.json`.

---

# Group A — the umbrella records

Publish these first. The nine investigations cite the laboratory record, so a
reader arriving at any of them has a canonical parent to land on.

## 1. ScientificDiscoveryLab v2.0.0

**https://zenodo.org/deposit/23122787**

The master record: registries, governance rules, and the self-audit that found
four defects in the laboratory's own instruments. Adds 8 subjects + 6 references
to v1, which published with neither. Everything else already correct.

## 2. Consciousness Indicator Battery v3.0.0

**https://zenodo.org/deposit/23122664**

New version of `10.5281/zenodo.23111535`, same concept `10.5281/zenodo.23101902`.
Adds 6 subjects — the field v1 and v2 both lack — and applies the house title
style. No scientific change.

## 3. Phantom Vision Lab v2.0.0

**https://zenodo.org/deposit/23123095**

New version of `10.5281/zenodo.23112116`, same concept `10.5281/zenodo.23112115`.
Adds 4 subjects. No scientific change.

---

# Group B — the nine investigations

Ordered by experiment number, matching `EXPERIMENT_REGISTRY.md`, so a reader
following the registry lands in the same order.

Each cites `10.5281/zenodo.23109117` (laboratory v1) and the GitHub repository.

## 4. Speckle contrast law — EXP-0002

**https://zenodo.org/deposit/23132744** · 86 KB

## 5. Vortex density in random wave fields — EXP-0003

**https://zenodo.org/deposit/23132746** · 150 KB

## 6. Laboratory RNG statistical certification — EXP-0004

**https://zenodo.org/deposit/23132759** · 251 KB

Carries the T03_runs defect: a z-score conversion applied to a statistic already
in `erfc` units. Reads as `UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION`.

## 7. Percolation thresholds and exponents — EXP-0005/0006/0009/0010/0017

**https://zenodo.org/deposit/23132761** · 547 KB

The largest, and the one carrying the most: the biased exponent estimator, the
crossover refutation, and the pooling attribution. **Read this one carefully
before publishing** — it is where a reader is most likely to over-read the
results.

## 8. Prime gap statistics — EXP-0008

**https://zenodo.org/deposit/23132767** · 168 KB

*This is the laboratory's EXP-0008 (prime gaps). Unrelated to the separate
`code\EXP0008` project, which is on hold.*

## 9. Feigenbaum universality — EXP-0014

**https://zenodo.org/deposit/23132763** · 67 KB

## 10. Discrete optical-vortex detection bias — EXP-0015

**https://zenodo.org/deposit/23132748** · 309 KB

## 11. Topology-measurement definition — EXP-0016

**https://zenodo.org/deposit/23132753** · 1.1 MB

## 12. Water acoustic response simulator — no experiment ID

**https://zenodo.org/deposit/23132771** · 34 KB

A simulator with controls. No empirical claim.

---

# After each publish

1. Read it back and confirm subjects landed.
2. Confirm the stored `checksum` matches the local build.
3. Record the DOI: `zenodo/investigations/DEPOSITS.json`, `RELEASE.md`.
4. Commit and push; confirm CI green.

---

# Deleted

| Draft | Why |
|---|---|
| `23110728` | `[UNUSABLE DRAFT]` — 0 files, 0 keywords, 0 creators, licence reverted to `cc-by-4.0`, and concept `23110727` instead of `23101902`. My failed attempt at creating battery v2 through the legacy endpoint, whose `conceptrecid` is accepted then ignored. Never published, so nothing public was lost. Deleted on 2026-10-04 at the maintainer's instruction. |

Audited all thirteen pending deposits first. The other twelve all carried a file,
a full description, keywords, a creator and an MIT licence. This was the only
degenerate one.

---

# Not published

| | |
|---|---|
| `code\EXP0008` (DMT/psychedelic) | On hold. `FALSIFICATION_RECORD.md` shows the headline claims are hand-authored — `restore_csvs.py` writes the results table as string literals. Publish the null results only. |
| **EXP-0011** | INPROGRESS, preregistration FROZEN, no results. |
| `coherent-optical-ai-sandbox` | Already published: `10.5281/zenodo.22849652`. |
| `dmt-laser-s9-battery` | Already inside the laboratory record. |
| AI-consciousness battery | Already published: `10.5281/zenodo.23111535`. |

---

# Currently published — all verified resolving

| DOI | What |
|---|---|
| `10.5281/zenodo.23101903` | battery v1 (superseded on metadata, still citable) |
| `10.5281/zenodo.23111535` | battery v2 |
| `10.5281/zenodo.23109117` | ScientificDiscoveryLab v1 |
| `10.5281/zenodo.23112116` | Phantom Vision Lab v1 |
| `10.5281/zenodo.22849652` | EXP-0007, coherent optical vortex |