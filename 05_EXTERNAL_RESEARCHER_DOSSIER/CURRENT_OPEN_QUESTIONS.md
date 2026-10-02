# Current Open Questions

> **AUDIT HOLD (2026-09-24): this list predates the cross-project audit.
> `AUDIT_SUPERSESSION_NOTICE.md` adds provenance, registry, and control-
> classification questions that block external reuse.**

- **Dossier:** Document 7 of 9
- **Companion:** `PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md` (§11, §12), `DATA_INDEX.md`

This document lists what is still unknown, uncertain, or untested. It is the
precise definition of "investigation open at these points". Questions are
grouped by whether they block, gate, or merely inform the next step.

---

## Q1 — Literature (blocks the next step: we need the citations)

- **The reply named W. H. Carter, possibly with E. Wolf, via Google Scholar.** The
  project's literature pass was rebuilt from that starting point. What is still
  unknown is the **exact canonical references** (primary source papers, their
  dates, and the modern vortex-density lineage) that the professor considers the
  correct entry point.
- Status: **OPEN, items requested in §12.5 of the main dossier.**
- Data affected: `OPTICS_LITERATURE.md`, citations in the dossier.

## Q2 — Kac-Rice / Nye-Berry constants for the reviewer (informs; gates R4)

- Lab `EXP-0003` matched theory with n_meas/n_pred = 0.9952–1.0011 (within
  0.5%). Before any further claim is built
  on R4, an optics researcher should verify the specific coefficient used in the
  warp-free counter (documented in the lab script) against the standard form.
- Status: **OPEN; low risk — the reproduction is strong (6/6 checks PASS), but
  the constant deserves an expert eye.**

## Q3 — Pixelation-resonance interpretation (near-closed, not yet independent)

- Audit `EXP-2C` explains z = 1280 µm as a pixelation resonance of the 256² grid.
  The mechanism is *consistent* with PROBE A/B, but has not been independently
  reproduced outside the project tooling.
- Status: **LIKELY CLOSED; one independent reproduction (PROBE A on a different
  renderer) would close it formally.**
- If that reproduction fails, Q3 reopens as "what is z = 1280 µm?" — so it is
  the honest trigger for restarting the anomaly.

## Q4 — Counter floor (informs; partially closed)

- The 8-px autocorrelation floor was demonstrated on 5 pitches. Whether the
  floor is exactly 8 px (rather than, e.g., pitch/4), and where it breaks, is
  still a candidate for one analytic landmark replay.
- Status: **OPEN but low priority; `03_INVESTIGATIONS/OPTICS/INTEGRATION_PLAN.md`**
  (see Q7).

## Q5 — Semantic / "code"-in-light (RULED OUT only by controls, not by a bounded search)

- Controls rule out: content in intensity-only readouts; spontaneous structure;
  wavelength-invariant spacing. But the strongest *semantic* question — "can an
  optical field carry an explicitly encoded message that the original observer
  called 'code'?" — was **NOT** tested as a positive experiment (no message was
  ever embedded by the project).
- Status: **NOT TESTED as a positive claim; no evidence either way.** It is
  listed out of completeness and *must not* be read as a suggestion that such
  content exists. See Document 1 §11 (semantics row).

## Q6 — Physical (real-optics) confirmation

- Every result is computational.
- Status: **NOT YET TESTED.** An interested lab could run the
  reference-not-copy experiment plan (exact parameters in Document 1 §4).

## Q7 — `Q-O003` propagation-invariance audit (next candidate)

- Registered candidate: "does the surviving signal depend on the propagation
  mid-step (2 × 160 µm)?" Explicitly guarded against re-claiming the z = 1280
  result.
- Status: **REGISTERED, OPEN**, tentatively next after Q1.

## Q7b — Lab items that moved after this dossier was drafted (2026-09-18)

- **EXP-0009 (Q-P005 percolation critical exponents) — COMPLETE 2026-09-18.**
  Decision: ABNORMAL (all gates PASS, D_f/γ/ν/β/ν miss tolerances by ~1σ).
  See `percolation\Q-P005_exponents\CODE\RESULTS\EXP-0009_summary.json`.
  EXP-0009 results integrated into KEY_RESULTS.md and DATA_INDEX.md.
- **EXP-0010 (Q-P005 follow-up — lattice-artifact diagnostic) — COMPLETE 2026-09-18.**
  Decision: LATTICE_ARTIFACT (D_f=1.8962 at non-P2 sizes vs 1.8958 theory, |dev|=0.0004).
  Diagnosed EXP-0009 ABNORMAL as a lattice-size discretization artifact (same
  class as optical grid-locking at 256²). Q-P005 resolved.
- **EXP-0008 (Q-M002 prime gaps) — COMPLETE 2026-09-18 (post-BH-FDR-fix run).**
  Decision: H1_SUPPORTED. chi2_red 262→94,633 (B1→B4), combined χ²=971,920 (dof 36).
  C7 perfect match (0.0 diff). See `prime_gaps\RESULTS\EXP-0008_results.json`.
- **⚠️ ENGINE path flag was a FALSE ALARM (2026-09-18):**
  `run_exp0009.py` correctly sets `ENGINE = os.path.join(ROOT, "ENGINE")` where
  ROOT = parent of QDIR = `percolation`, giving `percolation\ENGINE` — which
  exists and contains `perc_engine.py`. The import works (verified by running
  EXP-0009 and EXP-0010). Flag removed.
- Scope note: extended-generalisation of the optics dossier's lab anchors
  (EXP-0002/0003) may be refreshed when percolation results are integrated
  (now complete — EXP-0009 ABNORMAL + EXP-0010 LATTICE_ARTIFACT).

## Q8 — Registry hygiene (informational)

- Sandbox registry rows `EXP-0001/0002/0006/0007` show FAILED (missing files /
  hash drift); the date-strip resolves the drift. Append-only, documented, not a
  physics question.
- Status: **CLOSED as a data-integrity item**; `DATA_INDEX.md` records it.

---

## Priority order for external discussion

1. Q1 (literature) — directly asked in the reply.
2. Q2 (constants) — protects R4, the only hard anchor.
3. Q3 (pixelation closure) — one independent reproduction would finalise it.
4. Q7 (propagation invariance) — the natural next internal experiment.
5. Q4, Q5, Q6 — informational; none block the above.