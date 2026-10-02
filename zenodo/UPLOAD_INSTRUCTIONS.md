# Uploading this deposit to Zenodo

## Before you upload

1. **Verify the package is intact:**

   ```powershell
   python package/scripts/verify_historical_integrity.py
   ```

   All 15 checks must pass. If any fails, do not upload.

2. **Run the laboratory test suite** and confirm it still reports
   `495 passed, 0 errors`:

   ```powershell
   cd C:\Users\natha\ScientificDiscoveryLab
   python -m pytest -q
   ```

3. **Insert the real DOI.** In `CITATION.cff` and `metadata.json`, replace
   `10.5281/zenodo.XXXXXXX`. Zenodo assigns the concept DOI *before* the version
   DOI, so: create the deposit, copy the concept DOI Zenodo gives you, publish,
   then paste the version DOI.

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
