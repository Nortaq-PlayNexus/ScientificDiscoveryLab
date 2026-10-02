# ScientificDiscoveryLab — release record

## Verified state at time of writing

| | |
|---|---|
| GitHub | `Nortaq-PlayNexus/ScientificDiscoveryLab`, public, CI green 5/5 on every push |
| CI jobs | pytest on Python 3.12, 3.13, 3.14; publishable-manifest verify; curated-deposit verify |
| Test suite | **543 passed, 0 failed** in the laboratory with complete data |
| Published tree | 543 collected; 20 failures, exactly the recorded excluded-data set |
| Zenodo deposit | **23109117**, published 2026-10-02 |
| DOI | **[10.5281/zenodo.23109117](https://doi.org/10.5281/zenodo.23109117)** |
| Archive | `ScientificDiscoveryLab-v1.0.0.zip`, 1,185 files, 6,678,433 bytes |
| SHA-256 | `a0750bbc8619e4c807030be1e54a2303b5df2d8b02704d6c76a2995d1cdd0ddf` |
| MD5 (as uploaded) | `21e6429965d9a4943c023e0ddd916bbf` |

The archive is byte-reproducible. Two independent builds produce an identical
digest, which matters because Zenodo files are immutable after publication: there
is no way to check afterwards whether what was uploaded is what was intended.

```powershell
python zenodo/build_zenodo_package.py --tree <published-tree> `
       --out zenodo/ScientificDiscoveryLab-v1.0.0.zip --verify
```

Expected output ends with `ARCHIVE VERIFIED: two independent builds are byte-identical`.

## Publication status

**Published 2026-10-02 as `10.5281/zenodo.23109117`.** The uploaded archive was
verified against Zenodo's own copy before and after: 6,678,433 bytes, md5
`21e6429965d9a4943c023e0ddd916bbf`, identical on both sides.

### Two fields are missing from the published record

The published record carries **zero subjects and zero references**. Zenodo's
deposition API accepts both fields without error and then silently discards them,
and neither is echoed back on read, so the upload reported success and the
verification read showed zero with nothing warning. The web form did not have them
either.

The correct values are recorded in `zenodo/DEPOSIT_23109117.md` and were used to
populate the repository at
`C:\Users\natha\AI_RESEARCH\ScientificDiscoveryLab`. Correcting the published
record requires a **new version**, which cannot be created through the legacy
deposit API — `conceptrecid` is accepted and then ignored, so a new version lands
on a different concept. Use the Zenodo web interface's **New version** action.

**Any change after publication must be a new version (new version DOI, same
concept DOI), never an edit.** Published Zenodo records are immutable.

## The four instrument defects

1. A PRNG battery test (`T03_runs`, NIST SP 800-22 §2.3) applied a z-score
   conversion to a statistic already in `erfc` units, inflating every p-value.
   KS 6.7e-06 with 0/200 rejections where an independent implementation gives
   0.847 with 1/200. No generator is certified; a withdrawn certificate stays
   withdrawn.
2. A 2D percolation exponent estimator biased **+0.11 to +0.35 too large**. The
   reported anomaly of τ = 1.92009 against Fisher's 2.054945 was made *smaller*
   by the bug, so the escalation stands strengthened.
3. An append-only registry pinned by whole-file digest was inviting a false fix —
   refreshing an immutable baseline to silence a failing test. Replaced with a
   prefix pin whose digest must equal the baseline's, so a re-freeze cannot
   launder itself.
4. Found at publication (N-29): seven tests asserted bit-exact float equality
   across a JSON round-trip. Two were genuine findings — a reproducibility flag
   whose `5e-15` bound could never pass yet was recorded `True`, and a bootstrap
   CI that matched at one bound to 4e-16 while differing by 1.4e-03 at the other.
   The stored artifact had already recorded that gap.

In two of the first three, **the bug made the laboratory's own anomaly look
smaller than it really was.**

## Nine further defects, found by publishing

All were invisible on the authoring machine and surfaced only when the suite was
run on a clean Linux checkout.

1. 329 files failed the byte-level integrity check — `core.autocrlf` rewrote the
   line endings the recorded digests depended on.
2. A nested `.gitattributes` silently overrode the byte-exact rule for nine files.
3. A CI job could not install: `numpy>=2.5.0` requires Python ≥3.12, matrix had
   3.11.
4. The CI dependency set was guesswork; six module-scope imports were missing,
   breaking collection of 33 tests.
5. The curated deposit's reference test copies were collected, because the
   exclusion list predated that directory.
6. **The CI integrity gate could not fail.** It grepped `FAILED` summary lines for
   exception text; those lines contain only node ids. It reported success while
   all 20 real failures sat unexamined. A gate that cannot fail is worse than no
   gate, because it reads as a green light.
7. A verification script read its input as UTF-8 and parsed zero lines from
   UTF-16 — which reads as a clean run.
8. A provenance audit hardcoded an absolute path under one user's home directory.
9. That audit's stored report recorded absolute paths, so its file-existence
   assertions could only hold on the machine that produced it.

Defect 6 is the same failure mode this laboratory exists to document.

## What this does not claim

**No physics discovery is claimed anywhere.** Q-P007 remains open: the magnitude
of its deviation is untrusted, the direction robust. `CROSSOVER_NOT_ESTABLISHED`
is not crossover excluded. The 3D run is unvalidated. Several checks are
`SAME_STREAM_IMPLEMENTATION_CHECK` and so are not independent validation. The
*mechanism* of the exponent bias was tested and rejected; only its magnitude is
established.

## Related

DOI `10.5281/zenodo.23101903` — the AI-consciousness indicator battery, also
present as one investigation inside this record. Neither supersedes the other.
