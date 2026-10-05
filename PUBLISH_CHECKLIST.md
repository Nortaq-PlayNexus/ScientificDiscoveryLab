# PUBLISH CHECKLIST — one record outstanding

**Everything in the 2026-10-04 batch is published.** Twelve records went live and
were verified by public-API read-back; see `PUBLICATION_VERIFICATION.md`. This
file previously listed three drafts awaiting a publish click, which was true when
written and stopped being true when the maintainer published them.

That batch also published with **zero subjects on all twelve records**. The web
form did not persist them either, and published records are immutable, so that is
permanent. Closing it means a new version of each record with subjects typed into
the form — a deliberate cost, not a defect to patch quietly.

## Still outstanding: battery v3.0.1

**https://zenodo.org/deposit/23137224** — `unsubmitted`, no DOI minted.

The only reason this version exists: **v3.0.0 does not rebuild byte-for-byte from
its repository. v3.0.1 does.** Two causes, not one — a CRLF working copy, and a
manifest generator whose output depended on the platform. No code, result, or
claim differs. v3.0.0 is not withdrawn; its own 41 digests verify.

Full instructions, verified digests, and the six subjects to paste:
**`zenodo/PUBLISH_v3_0_1.md`** in `consciousness-indicator-battery`.

This is the **last chance to attach subjects to this record**. If they are pasted
before publishing, the battery becomes the one project of the three with a
subject-indexed Zenodo record.

---

## Subjects, for the record

Kept because they will be needed again on any future version. Zenodo discards this
field on both API endpoints; it can only be entered in the web form.

| record | count | values |
|---|---|---|
| battery | 6 | `mesh:D003243` Consciousness · `euroscivoc:297` Artificial intelligence · `mesh:D009488` Neurosciences · `euroscivoc:307` Software · `euroscivoc:609` Philosophy · `mesh:D015203` Reproducibility of Results |
| ScientificDiscoveryLab | 8 | `mesh:D015203` Reproducibility of Results · `mesh:D010825Q000379` Physics/methods · `mesh:D010825Q000295` Physics/instrumentation · `mesh:D012106Q000706` Research/statistics & numerical data · `euroscivoc:805` Statistical mechanics · `euroscivoc:1061` Numerical analysis · `mesh:D012984` Software · `mesh:D012586Q000941` Science/ethics |
| phantom vision lab | 4 | `euroscivoc:307` Software · `mesh:D015203` Reproducibility of Results · `mesh:D012106Q000706` Research/statistics & numerical data · `euroscivoc:1061` Numerical analysis |

---

## Standing rules for any future publish

1. Read the record back from `https://zenodo.org/api/records/<id>`. **Do not trust
   a success response** — Zenodo reports success whether or not the right bytes
   arrived, and reports success for fields it discards.
2. Compare the stored `checksum` against the local build.
3. Record the DOI in `metadata.json`, `CITATION.cff`, the README badge and
   `RELEASE.md`. Commit, push, confirm CI green.
4. Create new versions with `POST /api/records/<id>/versions`, never the legacy
   deposit endpoint — that one accepts `conceptrecid` and ignores it, forking the
   concept. `zenodo/new_version.py` verifies linkage before uploading.
5. **Never send a partial metadata PUT.** It is a full replacement and will
   silently wipe every other field, including reverting the licence.
6. **Never delete a deposit.**

---

## Not part of this batch

| | |
|---|---|
| `C:\Users\natha\code\EXP0008` | On hold. `FALSIFICATION_RECORD.md` shows the headline claims are hand-authored, not computed. Publish the null results only — the Q7 refutation, EXP0010's 0/11, and the pooling attribution all reproduce. |
| `C:\Users\natha\code\string-theory-questions` | Never independently verified. |
| `coherent-optical-ai-sandbox` | Already published as `10.5281/zenodo.22849652`. Do not re-upload. |
| `dmt-laser-s9-battery` | Already inside the lab, audited as `SYNTHETIC_DERIVED_OUTPUT_NOT_EMPIRICAL_EVIDENCE`. |

See `HANDOFF.md` at the repository root for the API traps and standing rules.