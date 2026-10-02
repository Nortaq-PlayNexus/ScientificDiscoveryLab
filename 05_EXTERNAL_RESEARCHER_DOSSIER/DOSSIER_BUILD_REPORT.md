# DOSSIER_BUILD_REPORT

> **AUDIT HOLD (2026-09-24): this report documents the superseded 2026-09-18
> build. See `AUDIT_SUPERSESSION_NOTICE.md` before reuse.**

- **Built:** 2026-09-18
- **Folder:** `C:\Users\natha\ScientificDiscoveryLab\05_EXTERNAL_RESEARCHER_DOSSIER\`
- **Build method:** human + LLM-assisted; every number traced back to a source
  file in `DATA_INDEX.md`; no numbers invented.

## 1. Deliverables produced

| # | File | Status |
|---|---|---|
| 1 | `PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md` (12 sections) | DONE |
| 2 | `EXECUTIVE_SUMMARY.md` | DONE |
| 3 | `EXPERIMENT_TIMELINE.md` | DONE |
| 4 | `METHODS_AND_CONTROLS.md` | DONE |
| 5 | `KEY_RESULTS.md` | DONE |
| 6 | `NEGATIVE_AND_DIAGNOSTIC_RESULTS.md` | DONE |
| 7 | `CURRENT_OPEN_QUESTIONS.md` | DONE |
| 8 | `DATA_INDEX.md` | DONE |
| 9 | `FOLLOWUP_EMAIL.md` | DONE |
| 10 | `DOSSIER_BUILD_REPORT.md` | DONE (this file) |
| 11 | `figures\README.md` | DONE |

## 2. Source-verification pass (2026-09-18)

Numbers cross-checked against the source files listed in `DATA_INDEX.md` §1–§4.
Confirmed correct after fixes:

- ASM unitarity ~10⁻¹³; energy error 3.1e-16; independent ASM NCC = 1.000000,
  max |ΔI| ≤ 1.9e-13. *Source: FINAL_PHASE_REPORT / independent replication.*
- Same-plane phase identity max relative diff 6.55e-16. *Dossier §3.*
- Purified plateau 31/24/36/90 at z = 0/160/640/1280 µm. *Src: EXP-2_summary.*
- EXP-2B: obs S = 95, deltas [90,95,90,96,100]; D02 null med 43–44, q95 66–67;
  d ≈ 4.2–4.5; 6/6 seeds ≤ 0.01. *Src: EXP-2B_z1280_summary.json.*
- EXP-2C PROBE A: grids 64/128/256/512², obs/null {0.70,1.43,2.10,1.22},
  p {0.926,0.058,0.002,0.24}; only 256² survives; 512² obs 68 ≤ q95 85.
  *Src: FINAL_PHASE_REPORT §16, EXP-2C_probe_summary.json.*
- EXP-2C PROBE B: z = 640/960/1280/1475/1600/2622; obs {35,32,95,69,66,32};
  only z = 1280 survives α=0.05 post-FDR; nothing at α=0.01; 1475 µm marginal
  OUT* (p 0.036–0.050), 2622 µm IN (p 0.898). *Src: FINAL_PHASE_REPORT §16.*
- Fourier radial 41.66 c/mm; 2-D fundamental 33.4 c/mm; generator pitches
  32.0 / 42.67 µm. *Src: PROJECT_STATE, OPTICS_LITERATURE / NOVELTY_ASSESSMENT.*
- Lab: EXP-0002 r ∈ [0.984, 1.005]; EXP-0003 n_meas/n_pred 0.9952–1.0011,
  half-pixel shift ≤ 2.1%; EXP-0005/6/7 Q-P004 H0_SUPPORTED (bond_wrap p_c
  0.500687 ± 0.0317, FG χ² 4.738 → 2.239, C7 78/78). *Src: lab CURRENT_STATUS /
  percolation summaries.*

**Fixes applied during this pass:**

1. `z_cycle = L²/λ`: corrected **94,268 → 94,391 µm**
   (65536 / 0.6943 = 94391.47), matched against EXP-0020's recorded
   `fresnel_number = 0.0943914734`.
2. PROBE B: corrected the row "half-Talbot planes null-equivalent" — the
   col-pitch half-Talbot (1475 µm) is marginal OUT* (p 0.036–0.050), the
   row-pitch half-Talbot (2622 µm) is inside the envelope (p 0.898). Both are
   non-significant post-FDR; wording now matches §16.
3. Replaced the unverifiable "22-phase audit" description with the verified
   multi-agent audit structure (STEP 0 discovery → 9 scope-separated agents →
   coordinator battery → independent verification agent).

No claim of physical discovery is made anywhere in this dossier; the strongest
flagged anomaly is classified as a numerical artifact.

## 3. Data-hygiene flags (important)

- **Experiment-ID collision on EXP-0008 — RESOLVED 2026-09-18.** Two independent
  investigations in the lab both used the EXPERIMENT_ID **EXP-0008**:
  1. `03_INVESTIGATIONS\MATHEMATICS\prime_gaps` — Q-M002 / HYP-005 (prereg
     frozen 2026-09-17; registry row present: INCONCLUSIVE; a
     `CONFIG\registry.jsonl` row already exists under EXP-0008). **KEEPS EXP-0008.**
  2. `03_INVESTIGATIONS\PHYSICS\percolation\Q-P005_exponents` — Q-P005 /
     HYP-005 (scaffolded as EXP-0008, runner freshly edited, **not yet executed**).
     **RE-ISSUED AS `EXP-0009`** (prereg renamed `prereg_EXP-0009.json`,
     rerun id, rng labels `exp8-* → exp9-*`, `exp8-boot → exp9-boot`, runner
     `run_exp0009.py`, replication `independent_check_exp0009.py`, experiment
     json/results/summary paths all `EXP-0009`). Re-issue note recorded in the
     prereg's `note` field. Prime-gaps records untouched.
  **Next:** when Q-P005 executes it registers as EXP-0009 — no ID clash.
- The `VISUAL_PHENOMENON_LITERATURE.md` visibility-fields file is outside this
  dossier's scope; the optics dossier intentionally does not reference it except
  via the shared rule that semantic/"code"-content claims are ruled out.
- `percolation.rar` exists inside the lab (archive artifact, not opened).
  Informational only.

## 4. Open item — active research

As of build time, `Q-P005_exponents` (percolation critical exponents, EXP-0008
id — see the collision note) was **scaffolded and runner-edited but not yet
executed**. This dossier was written against the executed record as of
2026-09-18; if Q-P005 completes before delivery, add its status to
`CURRENT_OPEN_QUESTIONS.md`, `KEY_RESULTS.md`, and `DATA_INDEX.md`.

## 4. Post-build updates (2026-09-18)

- **EXP-0009 (Q-P005 percolation critical exponents) — COMPLETE.**
  Decision: ABNORMAL (all gates PASS, D_f/γ/ν/β/ν miss tolerances by
  ~1σ). Fully diagnosed by EXP-0010 (LATTICE_ARTIFACT — lattice-size
  discretization). Integrated into `KEY_RESULTS.md` and `DATA_INDEX.md`.
- **EXP-0008 (Q-M002 prime gaps) — COMPLETE (post-BH-FDR-fix).**
  Decision: H1_SUPPORTED (chi2_red 262→94,633, C7 perfect match).
  Integrated into `KEY_RESULTS.md` and `DATA_INDEX.md`.
- **Engine path flag (EXP-0009): RESOLVED.** `run_exp0009.py` correctly
  uses `ROOT\ENGINE` = `percolation\ENGINE`; verified by running both
  EXP-0009 and EXP-0010. No fix needed.

## 5. Verification checklist before sending

- [x] `FOLLOWUP_EMAIL.md` attachments chosen (EXECUTIVE_SUMMARY + dossier).
- [x] Post-build EXP-0008/EXP-0009 results integrated (§4).
- [x] Figures referenced by path in `figures\README.md` (no copies needed).
- [ ] Send: approved.