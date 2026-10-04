# PUBLICATION VERIFICATION — 2026-10-04

Twelve records published by the maintainer. This file records what was checked,
what passed, and the three defects that publication did not fix.

Nothing here is asserted from a publish click. Zenodo reports success whether or
not the right bytes arrived, so every claim below comes from querying the public
API and comparing against a local build.

---

## Result

| check | outcome |
|---|---|
| records published | **12 / 12** |
| DOIs resolve through `doi.org` | **17 / 17** (5 pre-existing + 12 new) |
| concept DOIs resolve | **3 / 3** |
| investigation archives byte-identical to local build | **9 / 9** |
| umbrella archives byte-identical to local build | **2 / 3** — battery failed, see D1 |
| concept linkage correct (no forked concepts) | **12 / 12** |
| licences correct (`mit-license`) | **12 / 12** |
| published archive internally self-consistent | battery v3 verified: 41/41 manifest digests |
| **subjects populated** | **0 / 12** — see D2 |
| search-indexed by DOI | 10 / 12 — see D3 |

New DOIs, all `mit-license`:

| DOI | record |
|---|---|
| `10.5281/zenodo.23122664` | battery v3.0.0 |
| `10.5281/zenodo.23122787` | ScientificDiscoveryLab v2.0.0 |
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

---

## D1 — battery v3 is not byte-reproducible from the repository

**The only genuine integrity failure found.**

| | bytes | md5 |
|---|---|---|
| published `23122664` | 115,050 | `371e3447554ac602794b10517c0750b6` |
| rebuilt from repo HEAD | 116,863 | `00d84b0dbaa604f13f2cf105096bb85d` |

Diagnosed to the byte. Entry-by-entry comparison of the published archive
against a fresh build:

```
ONLY IN PUBLISHED (0)
ONLY IN REBUILT  (1)   PUBLISH_CHECKLIST.md
SIZE CHANGED     (11)
```

The content of `battery.py` is byte-for-byte identical in both — zero differing
lines. The difference is line endings:

```
published   37140 bytes  LF 859  CRLF 858  -> CRLF
repo HEAD   36282 bytes  LF 859  CRLF   0  -> LF
```

858 CRLF pairs against 859 lines. The published archive was built from a working
copy with CRLF endings; the repository now carries `.gitattributes` with
`* text=auto eol=lf`, which normalises to LF.

**Cause.** That archive was built in the earlier session from a working copy in
`%TEMP%\cib-clean`, which was lost when Windows cleared the temp directory, and
the repository was re-cloned afterwards. The re-clone has `.gitattributes`; the
lost copy predates it. `core.autocrlf` is `true` on this machine, which is what
produced the CRLF working tree in the first place.

**Severity: low, and it is not corruption.** The published archive verifies
against itself:

```
manifest declares file_count: 41
actually verified   : 41
failures            : 0
```

Every one of the 41 SHA-256 digests in the published `manifest.json` matches the
file beside it. A reader who downloads the archive can confirm it is intact. What
is broken is narrower and precise: **a reader who clones the repository and
rebuilds gets different bytes than the archive contains.** For an artifact whose
subject is reproducibility, that gap is worth closing.

The other eleven archives show no such drift. The laboratory and phantom archives
match their local builds exactly, and all nine investigation archives are
byte-identical.

**Remedy.** Publish battery v3.0.1 from the current LF-normalised tree, so the
repository and the artifact agree. Nothing else needs to change — no code differs.

---

## D2 — all twelve records published with zero subjects

Zenodo's API accepts `subjects`, returns success, and stores nothing. Tested on
2026-10-04 against **both** endpoints:

| endpoint | subjects | version_note |
|---|---|---|
| `PUT /api/deposit/depositions/<id>` | accepted, **0 stored** | accepted, **0 stored** |
| `PUT /api/records/<id>/draft` | accepted, **0 stored** | accepted, **0 stored** |

Not a payload-shape problem. The fields are discarded server-side. They can only
be entered in the web form, and **published Zenodo records are immutable**, so
this is now permanent for all twelve.

Consequence: none of these records will surface in a Zenodo subject browse. The
values that should have been applied are in `zenodo/investigations/<slug>.json`
and in `PUBLISH_ORDER.md`.

Closing it means a new version of each record with subjects typed into the form.
That is a deliberate cost, not an oversight to patch quietly — recorded here so
the decision is made rather than inherited.

---

## D3 — the two battery records are not search-indexed

| record | resource type | DOI search | title search |
|---|---|---|---|
| `23109117` laboratory v1 | dataset | found | found |
| `23112116` phantom v1 | dataset | found | found |
| `23101903` battery v1 | software | **0 hits** | **0 hits** |
| `23111535` battery v2 | software | **0 hits** | **0 hits** |

Not indexing lag. The dataset records published on the same days indexed fine. The
split is exactly along resource type: both `software` records are unindexed, both
`dataset` records are indexed.

Both remain live and citable — `doi.org` resolves them. This only affects
discoverability through search, and it affects the artifact most likely to be
searched for. Worth watching on v3.0.1; if it persists, the fix is outside Zenodo's
API and worth raising with Zenodo support.

---

## What was checked, and how

- **Publication state** — `GET /api/deposit/depositions/<id>`, all `done`.
- **What a reader sees** — `GET /api/records/<id>`, unauthenticated. Not the draft
  endpoint, because the draft view is not the public view.
- **Byte integrity** — stored `filesize` and `md5:` checksum compared against
  `md5sum` of the local build. Nine of twelve matched exactly.
- **Archive self-consistency** — every SHA-256 in the published `manifest.json`
  recomputed against the extracted archive. 41/41 for battery v3.
- **Concept linkage** — each published record and its pending draft compared; all
  twelve resolve to the correct parent concept, so no concept was forked.
- **DOI resolution** — `curl -L` through `doi.org` for all seventeen DOIs.

### Two measurement errors, both mine

Recorded because both initially looked like Zenodo defects:

1. **Subject and reference counts read as 1 when empty.** `@($null).Count` is `1`
   in PowerShell. The fields were genuinely empty; the counter was wrong. Claiming
   "subjects = 1" from that would have been a false all-clear.
2. **All seventeen DOIs read as HTTP 302.** That is `curl` declining to follow the
   redirect, not a resolution failure. With `-L`, all seventeen return 200.

Neither changed a conclusion, and neither would have been caught without the
read-back that produced them.

---

## Reproducing this

```
python tools/record_publication.py
```

Queries the live API and compares each stored file against the local build by
size and MD5. Records that cannot be verified are marked `UNVERIFIED` rather than
assumed good. Re-runnable — it holds no hardcoded DOIs, so a later version is
recorded the same way.