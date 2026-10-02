# Experiment Timeline

> **AUDIT HOLD (2026-09-24): chronology below is historical and not an
> authoritative completion record. See `AUDIT_SUPERSESSION_NOTICE.md`.**

- **Dossier:** Document 3 of 9
- **Period covered:** 2026-09-15 → 2026-09-18
- **Companion:** `PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md`

> Numbering caveat: three numbering schemes coexist in the project.
> - **sandbox `EXP-####`** — the sandbox repository's original 25-phase registry;
> - **audit `EXP-1, EXP-2, EXP-2B, EXP-2C, EXP-4, EXP-5`** — the post-email
>   adversarial multi-agent audit;
> - **lab `EXP-0002 …`** — the independent `ScientificDiscoveryLab` engine
>   (problem labels `Q-O001`, `Q-O002`, `Q-I004`, `Q-P004`, `Q-O003`).

## 2026-09-15 — origin and first reply

| # | Event | Result |
|---|---|---|
| 1 | AI vision agent produces first unverified observation report | ~45 candidate dark/winding structures, apparent ~32 µm spacing, apparent alternating rotational direction, ±vortex/artifact hypothesis. Quoted verbatim in Document 1, §1. |
| 2 | Email to Professor Swartzlander forwarding the observation | Sent. |
| 3 | Professor Swartzlander replies | Points to W. H. Carter, possibly with E. Wolf, Google Scholar. Literature pass later rebuilt from this starting point. |
| 4 | DeepBeamValidator 12-test battery (independent, non-AI) | **PARTIALLY REPRODUCIBLE**: 48 cores after classification fix (+24 / −24); 45-feature claim **AGAINST**; 21/24 split **AGAINST**; 32 µm spacing real/periodic; step_um·pixel_size = 160 µm unit-coincidence kept as a NOTE. |

## 2026-09-16 — audit framework and controls

| # | Event | Result |
|---|---|---|
| 5 | Phase-1 framework built; multi-agent validation & novelty audit begins (STEP 0 discovery → 9 scope-separated agents → coordinator → independent verification) | Framework operational. |
| 6 | **Methodological correction 1** — phase-randomisation / propagation conflation identified | Same-plane identity max rel diff ≤ 6.55e-16; post-propagation NCC = 0.0564 (160 µm). The ~0.13 "phase-as-information" statistic is a propagation-vs-coherence effect, not information. |
| 7 | Blind coded-field analysis v2 | DEEP CODE 7, 36 × 156 px; **INFO CONFIRMED**; 0/2 control false positives. |
| 8 | Emergence-vs-inheritance control (`reports/figures/emergence_control/`) | 32 µm is **INHERITED**, not generated; random-input raw features ≈ 21,545; Fourier radial 41.7 c/mm ≠ 2D fundamental 33.4 c/mm; anti-cheat band-power: C-control ratio 0.595 = **INVALID**, B/H controls VALID. |

## 2026-09-17 — multi-agent validation & novelty audit (sandbox)

| # | Experiment | Result |
|---|---|---|
| 9 | Audit `EXP-1` — independent replication of the vision report | PARTIALLY REPRODUCIBLE: 48 cores (+24/−24); 45-feature and 21/24 split claims AGAINST; spacing real. |
| 10 | Audit `EXP-2` — propagation / phase-randomisation inner test | Methodology correction (see #6). |
| 11 | ASM numerical checks | Unitarity ~1e-13; energy error 3.1e-16; independent numpy ASM: NCC = 1.000000, max |ΔI| ≤ 1.9e-13. |
| 12 | Same-plane phase identity check | |A·e^{iφ}|² = A², max rel diff 6.55e-16 (identity confirmed, not evidence). |
| 13 | Audit `EXP-5` — periodic-spacing statistics | Constant 8.0-px autocorrelation lag for design pitches 16/32/64/128/21.33 µm; median-NN tracks design at 3/5 pitches within 15% → detector grid-lock artifact. |
| 14 | Audit `EXP-4` — resolution grid sweep | Purified counts at z = 1280 µm: 48/73/90/97 for 64/128/256/512²; padding 256²→768² shifts counts 20.8–24.4% per plane. |
| 15 | Audit `EXP-2` inner null — D01 (circular Gaussian) | Null median ≈ 843–853, lattice 24–90, p ≈ 1.0 at all planes — no significance. |
| 16 | Audit `EXP-2` inner null — D02 (matched spectrum) | Null median 42–45, q95 65–67; only z = 1280 exceeds (90 vs 67; d = 3.68, p = 0.003 @N=999 seed 42; d = 3.8, p = 0.0067 @seed 7 N=299); fails BH-FDR at α = 0.01. |
| 17 | Audit `EXP-2B` — **pre-registered** z = 1280 test (N = 5,000, 6 seeds {42, 7, 123, 2023, 314159, 271828}; statistic S = median purified count over 5 Fourier shifts) | Obs S = 95 (deltas [90, 95, 90, 96, 100]); D02 null med 43–44, q95 66–67, max 94–99; d ≈ 4.2–4.5; p ≈ 0.0002–0.0008; **6/6 seeds significant at α ≤ 0.01** → "topological excess survives" (scoped). |
| 18 | Audit `EXP-2C` PROBE A — grids 64/128/256/512² at z = 1280 | obs/null {0.70, 1.43, 2.10, 1.22}, p {0.926, 0.058, 0.002, 0.24}; only 256² survives; 512² obs 68 ≤ q95 85 → pixelation resonance at 256². |
| 19 | Audit `EXP-2C` PROBE B — planes z = 640/960/1280/1475/1600/2622 µm | Only z = 1280 significant at α = 0.05 post-FDR; nothing at 0.01; col-pitch half-Talbot 1475 marginal OUT* (p 0.036–0.050), row-pitch half-Talbot 2622 IN (p 0.898) → **not Talbot, not scale-invariant**. |
| 20 | Final audit verdict | Grid-locked detector/pixelation; original physical claims ruled out; evidence level 1. |
| 21 | Independent verification suite (`INDEPENDENT_VERIFICATION.md`) | 6/6 checks PASS. |

## 2026-09-17/18 — lab (`ScientificDiscoveryLab`, independent engine)

| # | Experiment | Result |
|---|---|---|
| 22 | `EXP-0002` — `Q-O001` speckle contrast | C(M) = 1/√M reproduced; r ∈ [0.984, 1.005]. |
| 23 | `EXP-0003` — `Q-O002` vortex density | Kac-Rice/Nye-Berry reproduced: n_meas/n_pred = 0.9952–1.0011; shift-invariant counter (half-pixel shift ≤ 2.1%); near-Nyquist failure 17–24% mapped. |
| 24 | `EXP-0004` — `Q-I004` lab RNG certification | **CERTIFIED PASS**. |
| 25 | `EXP-0005/6/7` — `Q-P004` percolation/forbidden-region | **H0 supported**: bond_wrap p_c = 0.500687 ± 0.0317; site_span 0.59284; FG χ² 4.738 → 2.239; C7 78/78. |
| 26 | `Q-O003` candidate — propagation-invariance audit | Registered as candidate, **OPEN** (guarded continuation). |

## 2026-09-18 — this dossier

| # | Event |
|---|---|
| 27 | Build of `05_EXTERNAL_RESEARCHER_DOSSIER/` (9 documents + build report + figures index). |

## Not executed / blocked

- Audit `EXP-3` (input-position predicate shuffle) — **NOT executed**; no density/results.
- Sandbox registry rows `EXP-0001/0002/0006/0007` reported FAILED (missing files / hash drift; date-strip resolves) — kept append-only, documented in `DATA_INDEX.md`.
- Physical laboratory experiment — **not performed**; only computational.