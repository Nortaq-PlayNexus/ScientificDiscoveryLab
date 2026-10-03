# Uploading this deposit to Zenodo

## STATUS: DONE. These instructions are historical.

**This deposit was published as `10.5281/zenodo.23109117` on 2026-10-02.**

Everything below describes the procedure that was followed, and is kept because
the steps and their ordering matter if a **new version** is ever needed. Zenodo
records are immutable, so no step here can be repeated against 23109117.

Current state, for reference:

| | |
|---|---|
| Published DOI | `10.5281/zenodo.23109117` |
| Archive | `ScientificDiscoveryLab-v1.0.0.zip`, 6,678,433 bytes |
| SHA-256 | `a0750bbc8619e4c807030be1e54a2303b5df2d8b02704d6c76a2995d1cdd0ddf` |
| MD5 as uploaded | `21e6429965d9a4943c023e0ddd916bbf` |
| Subjects in the published record | **zero** — see below |
| References in the published record | **zero** — see below |

### Two fields the API silently discarded

`subjects` and `references` were supplied, accepted, and not persisted. Zenodo's
deposit endpoint reports success and echoes neither back on read. Both must be
entered in the **web form**. The exact values are in `DEPOSIT_23109117.md`.

Correcting either requires a **new version**, and a new version cannot be created
through the deposition API — `conceptrecid` is accepted and then ignored, so a new
version lands on a different concept. Use the Zenodo web interface's **New
version** action. See `HANDOFF.md` in the repository root.

---

## Before you upload

1. **Verify the package is intact:**

   ```powershell
   python package/scripts/verify_historical_integrity.py
   ```

   All 15 checks must pass. If any fails, do not upload.

2. **Run the laboratory test suite** and confirm it still reports
   `543 passed, 0 failed`:

   ```powershell
   cd C:\Users\natha\ScientificDiscoveryLab
   python -m pytest -q
   ```

3. **Insert the real DOI.** In `CITATION.cff` and `metadata.json`, replace
   `10.5281/zenodo.XXXXXXX`. Zenodo assigns the concept DOI *before* the version
   DOI, so: create the deposit, copy the concept DOI Zenodo gives you, publish,
   then paste the version DOI.

   **Apply every metadata change BEFORE publishing.** A published record cannot be
   edited, so anything not set in advance needs a whole new version. See
   `HANDOFF.md` — this has already cost one retitle.

## Why this is a NEW deposit and not an edit to DOI 10.5281/zenodo.22849652

That record covers **EXP-0007**, a different project (coherent optical vortex
propagation). This session's work is ScientificDiscoveryLab instrument
validation. The two share no data, no code, and no conclusions.

Two hard constraints:

- **Zenodo records are immutable.** A published record cannot be edited. Any
  change to a published deposit must appear as a **new version** (new version
  DOI, same concept DOI), not as an edit.
- **Merging unrelated work into an existing record would be wrong** even if it
  were technically possible, because it would silently change what that DOI
  certifies. The EXP-0007 record already carries a 2026-09-24 erratum; adding
  unrelated percolation and RNG findings to it would make the record harder to
  interpret, not easier.

`metadata.json` lists 10.5281/zenodo.22849652 under `related_identifiers` with
`relation: isSupplementedBy` **and an explicit note that the boundary is
clarification, not amendment**. If you would rather not create any link at all,
delete that block — the two deposits are genuinely independent.

## Suggested metadata

| Field | Value |
|---|---|
| Upload type | Dataset |
| Title | ScientificDiscoveryLab: Three Instrument Defects Found by Self-Audit |
| Version | 1.0.0 |
| Publication date | 2026-09-28 |
| License | MIT (see `package/LICENSE`) |
| Creators | ScientificDiscoveryLab |
| Description | contents of `description.md` |
| Keywords | from `metadata.json` |

## How to upload

1. Go to <https://zenodo.org/upload>
2. Choose **New upload** → **Dataset**
3. Upload `package/` as a directory (or zip it first; zipping is friendlier to
   the web form)
4. Paste `description.md` into the description field
5. Paste the keywords
6. Publish, record the assigned DOIs

Optional but recommended: create a **GitHub release** alongside the deposit so
the code is browsable and citable per-commit. If you do, add the repository URL
to `CITATION.cff` under `repository-code`.

## Zipping

```powershell
Compress-Archive -Path package\* -DestinationPath ScientificDiscoveryLab-v1.0.0.zip
```

Check the archive size first. The package is ~63 MB, almost all of it the 60 MB
raw SQLite database that makes the integrity claims independently checkable. If
you need a smaller upload, the only honest option is to ship that database
separately as a second record and reference it — **do not** silently drop it,
because the deposit's central claim depends on it.

## After publishing

1. Paste the version DOI into `CITATION.cff` and `metadata.json` in the lab
2. Add an entry to `CHANGELOG.md` recording the DOI
3. Note that the next change to this deposit must be a **new version**
