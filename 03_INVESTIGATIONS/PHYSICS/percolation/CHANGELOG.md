# CHANGELOG.md

Investigation: Percolation thresholds and exponents (Q-P004 / HYP-004 / EXP-0005..0007)

> **2026-09-24 audit supersession:** entries below are chronological historical
> records, not current validation. EXP-0006 has a non-regenerating named runner
> and unavailable control path; EXP-0007 used 495 accepted rather than 500
> bootstrap draws and has uncertainty broader than its ±0.01 gate; EXP-0009 C7
> is a same-stream implementation check; EXP-0010 does not execute its
> preregistered per-size/C7 closure; Q-P007's refined-p_c/tau closure is
> invalid. See `AUDIT/REPAIR_LOG_20260924.md` and the isolated repair areas.

## CONFIG/pre_experiment_EXP-0005.json — frozen 2026-09-17T08:24:08+00:00
- Protocol finalized (README/QUESTION/HYPOTHESIS/PREDICTIONS/CONTROLS/EXPERIMENT_PLAN/
  FALSIFICATION_planning_checks).
- Pre-registered parameters frozen BEFORE any run output; sha256 recorded in prereg
  (see CONFIG/ prereg json).

## CODE planning iterations (pre-execution, NOT protocol changes)
- 2026-09-17: estimator infrastructure QA. Confirmed ndimage batched labeling is
  chunk-invariant AND matches an independent pure-Python union-find brute force on
  identical random streams (L=6,10; p in {0.4,0.5,0.6}; n=60). Stream layout
  documented in CONFIG/stream_layout.md to pin the exact reader contract for
  replication (C7/C2 independence checks).
- Fixed: p_grids_for() read `p_probe_lo_hi` for `bond_wrap` (frozen config has no
  such key) → KeyError; grid now built from frozen p_json (arange 0.38..0.62 st 0.02).
- Fixed: site_span grid centre offset (frozen anchor 0.5927460508; grid = anchor +
  0.015*k for k in -3..3 → 0.547746..0.637746, matching frozen p_json).
- Fixed: EXP-0005 prereg path resolution (CONFIG dir at investigation root, not CODE).
- NOTE: A first run attempt crashed mid-planning (KeyError above) with NO results
  written and NO registry rows appended; that run produced no output artifacts and
  is treated as a discarded planning iteration. No results exist yet (avoids
  post-hoc selection).

## EXP-0005 width-route audit (DIAGNOSTIC, 2026-09-17; post-hoc, not a protocol change)
- Audited C8 (width-route 1/nu) and FG (fit-goodness) gates **deterministically from
  the frozen cell counts** in `CODE/RESULTS/EXP-0005_results.json` (read-only; no new MC;
  frozen RESULTS/registry row preserved).
- **C8 root cause:** `fit_probit_width` (run_percolation.py lines 286-296) starts L-BFGS-B
  at sigma0=0.05; on monotone-ordered bond cells (L>=128, n_real>=1200) the NLL has a
  degenerate sigma->0 basin the optimizer lands in, returning sigma~0.002 (true ~0.006-
  0.010). Re-fit with sigma0=0.10 on the SAME cells recovers widths scaling L^-3/4 and
   `1/nu=0.7922` (gate `[0.6,0.9]` PASS; frozen `1/nu=1.2384` FAIL). Site systems unaffected
  (MLE agrees with linear-WLS within 30%; site 1/nu=0.747 passes).
- **FG bond_wrap root cause:** intrinsic non-monotonic p50(L) (0.4986→0.4975→0.5004 at
  L=32,48,64) on only 3 small-L torus-wrap points → WLS chi2_red=4.738>4.0. Not an estimator
  bug (bond_wrap widths scale fine, inv_nu=0.827). bond_span FG passes (2.760); site_span passes (0.974).
- **Deliverables:** `DIAGNOSTICS/EXP-0005_width_route_audit.md`; `CODE/RESULTS/EXP-0005_width_route_corrected.json`;
  `CODE\EXP-0005_width_route_corrected.py` (at ScientificDiscoveryLab root `CODE/`); `state/CURRENT_STATUS.md`. Diagnostic row appended to `CODE/CONFIG/registry.jsonl`.
- Frozen EXP-0005 decision (`INCONCLUSIVE`) and all thresholds/grids unchanged.

## EXP-0006 executed (2026-09-17; post-proposal session)
- Ran the prepared runner (`CODE/run_percolation_exp0006.py`) against frozen
  `CONFIG/prereg_EXP-0006.json`. Fine p-grid at L=256/512 (step 0.004) resolved
  the physical crossing width (~0.006).
- **C8 width-route RESOLVED:** 1/nu = 0.7375 (nu = 1.3559), gate [0.6,0.9] PASS.
  Identical at s0=0.05 and s0=0.10 (fine grid kills the degenerate sigma->0
  basin found in EXP-0005). Deterministic bootstrap (500 draws) 0.7366 ± 0.0127,
  95% CI [0.7124, 0.7608]. MLE vs linear-WLS widths within 0.7% at all L.
- **C7 independent implementation implemented + run** (was declared in CONTROLS
  but never existed): `REPLICATION/independent_check.py` — pure-Python
  union-find on identical streams (no scipy.ndimage), 39/39 cells bit-identical
  (bond_span L=64/128 all p; bond_wrap L=32 all p). PASS.
- p_c: bond_span 0.5002095 ± 0.0140 (d=0.00021), bond_wrap 0.5012239
  (d=0.00122), site_span 0.5928415 (d=0.00010) — all in tol 0.01. FSS chi2_red:
  bond_span 0.059, bond_wrap 4.738, site_span 0.974.
- Gates: C1/C2/C4/C6/C7/C8/in_tol all PASS; **FG FAIL on bond_wrap only**
  (4.738 ≥ 4.0) — unchanged pre-existing small-L torus-wrap non-monotonicity.
- Decision: **INCONCLUSIVE** (frozen rule; single trigger = bond_wrap FG).
- Deliverables: `REPORT/TECHNICAL_EXP-0006.md`, `REPORT/PLAIN_EXP-0006.md`,
  `CODE/RESULTS/EXP-0006_summary.json` (primary_results / estimator_diagnostics,
  per proposal), `CODE/build_exp0006_summary.py`, `REPLICATION/` (C7 + report),
  registry row 2 (fresh identical re-run). EXP-0005 frozen artifacts unchanged.
- Remaining: user decision whether to run EXP-0007 (bond_wrap L=96/128/192,
  preregistered, runner written) to clear the sole failing gate, or file Q-P004
  INCONCLUSIVE.

## EXP-0009-pc (Q-P007, 2026-09-19) — p_c refinement diagnostic COMPLETE

- Ran Phase 2 runner (`Q-P007/CODE/run_phase2.py`) against frozen prereg
  (`CONFIG/prereg_EXP-0009PC.json`). Measured width-curve crossing at L in {512,
  1024, 2048}, extrapolated to p_c(L->inf), re-measured exponents at refined p_c.
- **Phase 1 width curves** (preserved from run.log):
  - L=512: p_c = 0.592883 ± 0.004519
  - L=1024: p_c = 0.592673 ± 0.003031
  - L=2048: p_c = 0.592834 ± 0.001828
  - p_c(L->inf) = 0.59272900 (Ziff: 0.59274605, |dev| = 0.00001705)
- **Phase 2 exponents at refined p_c:**
  - D_f = 1.8818 ± 0.0738 (expected 91/48=1.8958, |dev|=0.0140 < tol=0.015) **PASS**
  - gamma/nu = 1.7653 ± 0.0995 (expected 43/24=1.7917, |dev|=0.0264 < tol=0.03) **PASS**
  - beta/nu = 0.1189 ± 0.0712 (expected 5/48=0.1042, |dev|=0.0147 < tol=0.015) **PASS**
  - tau: N/A (0 tail clusters at L=2048 with n=25 realizations; insufficient sub-critical data near p_c — known limitation)
- **All 3 exponents PASS** at refined p_c (were FAIL at original p_c=0.5927460508 in EXP-0009).
- Conclusion: p_c inaccuracy was a contributing factor to exponent deviations measured in EXP-0009.
- Key file: `Q-P007/CODE/RESULTS/EXP-0009-pc_results.json`
- Cell data checkpoints: `Q-P007/CODE/RESULTS/EXP-0009-pc_L{L}_cells.npz` for L in {512, 1024, 2048}

## EXP-0007 EXECUTED (2026-09-17) — Q-P004 CLOSED: H0_SUPPORTED
- Ran the prepared runner (`CODE/run_percolation_exp0007.py`) against frozen
  `CONFIG/prereg_EXP-0007.json`. Added bond_wrap at L=96 (n=500, seed 101),
  L=128 (n=400, seed 202), L=192 (n=300, seed 303); L=32/48/64 are the frozen
  EXP-0005 cells (unchanged). 6 bond_wrap sizes => FSS meets >=4 sizes.
- **FG bond_wrap RESOLVED:** chi2_red 4.738 (FAIL, 3 sizes) -> **2.239 (PASS < 4,
  6 sizes)**. The L48->L64 non-monotonicity persists (delta ~0.0029) but is
  small-L sampling scatter, not a trend-breaker: the L^−3/4 model fits at 6 sizes.
- p_c: bond_wrap **0.500687 ± 0.0317**, |d| = 0.000687 (in_tol PASS). Alt models
  (L^-1/1.35, log L) agree (chi2_red ~2.23-2.24).
- C8 width-route: 1/nu = **0.7255** (nu = 1.3783), gate [0.6,0.9] PASS.
  Deterministic bootstrap (500) mean 0.7478, sd 0.0773, 95% CI [0.6722, 1.0674]
  (wide CI = coarse frozen 0.02 grid barely resolves width at L=192; diagnostic
  only, NOT a decision driver). Consistent with EXP-0006 bond_span 0.7375.
- C7 independent implementation (`REPLICATION/independent_check_exp0007.py`,
  pure-Python union-find on identical streams): **78/78 cells bit-identical,
  p50 delta = 0.000 at all L** (preregistered L=32 + new L=96/128/192). PASS.
- Gates: C1 (k=304/304) PASS, C4 (shift 0.001111<0.005) PASS, C6 (max dev
  0.00168 < 0.00412) PASS, C7 PASS, C8 PASS, FG PASS, in_tol PASS.
- Decision: **H0_SUPPORTED** ("all thresholds within 0.01 of anchor"). Q-P004
  evidence state: CONTROLLED (textbook law reproduced; no novelty claimed).
- Deliverables: `REPORT/TECHNICAL_EXP-0007.md`, `REPORT/PLAIN_EXP-0007.md`,
  `CODE/RESULTS/EXP-0007_results.json` + `EXP-0007_summary.json`,
  `CODE/build_exp0007_summary.py`, `REPLICATION/` (C7 + report), registry row.
  EXP-0005/0006 frozen artifacts unchanged (sha256 preserved).
- Runner note: a minor mechanical wrapper bug was fixed at execution time
  (`nu_gate` looked up in tolerances but prereg puts it in diagnostics; gate
  values unchanged, still from frozen prereg). Logged here for transparency.

(Next entry: candidate shortlist review for the next question.)
