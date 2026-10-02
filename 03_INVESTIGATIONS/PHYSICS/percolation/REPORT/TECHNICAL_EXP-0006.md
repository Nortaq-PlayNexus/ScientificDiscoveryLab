# EXP-0006 — TECHNICAL SUMMARY

**Question:** Q-P004 (percolation thresholds reproduction)
**Hypothesis:** HYP-004
**Date:** 2026-09-17
**Prereg:** `CONFIG/prereg_EXP-0006.json` (sha256 `8b8c2aae…c679a0`)
**Raw results:** `CODE/RESULTS/EXP-0006_results.json`
**Separated summary:** `CODE/RESULTS/EXP-0006_summary.json`
**C7 independent implementation:** `REPLICATION/independent_check.py`, report `REPLICATION/C7_exp0006_report.json`
**Runner:** `CODE/run_percolation_exp0006.py` (patches EXP-0005 runner constants; deterministic, seed 42)

## Purpose

EXP-0006 re-measures the bond_span crossing width-route at L=256/512 with a
**finer p-grid** (step 0.004 vs 0.02) so that the physical width (~0.006) is
resolved, giving a definitive C8 (1/nu) estimate. It also separated physical
results from estimator diagnostics, per `DIAGNOSTICS/EXP-0006_proposal.md`.

## Systems (unchanged from EXP-0005)

| system | anchors | L | grid |
|---|---|---|---|
| bond_span (PRIMARY) | 0.5 | 64,128,256,512 | L<=128: step 0.02; L in {256,512}: step 0.004 |
| bond_wrap (SECONDARY) | 0.5 | 32,48,64 | step 0.02 (unchanged) |
| site_span (calibration) | 0.5927460508 | 64,128,256 | anchor ± 3×0.015 (unchanged) |

## Estimate

`p50(L) = a + b·L^(−3/4)` WLS (weights 1/SE²):

| system | a (p_c_ext) | b | chi2_red | |a − anchor| |
|---|---|---|---|---|---|
| bond_span | **0.5002095** ± 0.0140 | −0.00462 | 0.059 | 0.00021 |
| bond_wrap | **0.5012239** ± 0.0840 | −0.04550 | 4.738 | 0.00122 |
| site_span | **0.5928415** ± 0.0353 | −0.01003 | 0.974 | 0.00010 |

All three thresholds within the 0.01 tolerance; bond_span/site_span FSS are
excellent (chi2_red 0.059 / 0.974). bond_wrap retains the known small-L
non-monotonicity (FG fail, unchanged from EXP-0005).

## 1/nu (width-route, C8) — RESOLVED

Fine-grid widths (MLE probit, L-BFGS-B):

| L | width (s0=0.10) | width (s0=0.05) | linear-WLS width | ratio MLE/WLS |
|---|---|---|---|---|
| 64 | 0.01817 | 0.01817 | 0.01827 | 0.995 |
| 128 | 0.01080 | 0.01080 | 0.01087 | 0.994 |
| 256 | 0.00653 | 0.00653 | 0.00657 | 0.994 |
| 512 | 0.00391 | 0.00391 | 0.00394 | 0.993 |

**1/nu = 0.7375, nu = 1.3559** — gate [0.6, 0.9] **PASS**.
- Identical at s0=0.05 and s0=0.10: the fine grid eliminated the degenerate
  sigma→0 basin that corrupted EXP-0005's coarse-grid width at L=256/512.
- Deterministic parametric bootstrap (label `perc-boot-0006-width`, seed 42,
  500 draws): 1/nu = 0.7366 ± 0.0127, 95% CI **[0.7124, 0.7608]**.
- Width-route stability across L=256/512: widths 0.00653 → 0.00391 step cleanly
  (ratio 1.67 ≈ 2.00^(3/4)=1.68); log-log slope is a straight line. The C8
  question from EXP-0005 is answered: 1/nu ≈ 3/4 with the fine grid.

## Estimator diagnostics (separated, not physical results)

- s0=0.05 vs s0=0.10 give byte-identical widths → no starting-value sensitivity;
  the EXP-0005 degeneracy was entirely a coarse-grid artifact.
- MLE vs linear-WLS probit agree to within 0.7% at every L → width estimates
  are not optimizer artefacts.
- All L-BFGS-B fits converged.

## Controls / gates

| gate | rule | value | verdict |
|---|---|---|---|
| C1 determinism | identical re-run | both runs k_v=795, k_h=742 | **PASS** |
| C2 estimator/BC independence | \|span − wrap\| < 0.005 | 0.00101 | **PASS** |
| C4 scale stability | drop {64,128}, \|Δa\| < 0.005 | Δa = 0.000077 | **PASS** |
| C6 seed ladder | L=64 p50 across 6 seeds < 3×joint SE | max 0.00075 vs 0.00275 | **PASS** |
| C7 independent implementation | pure-Python union-find vs ndimage counts | 39/39 cells bit-identical | **PASS** (NEW, implemented+run here) |
| C8 width-route | 0.6 ≤ 1/nu ≤ 0.9 | 0.7375 | **PASS** |
| FG fit-goodness | chi2_red < 4 all systems | bond_span 0.059, site_span 0.974, **bond_wrap 4.738** | **FAIL** (bond_wrap only) |
| in_tol | all \|a−anchor\| < 0.01 | 0.00021 / 0.00122 / 0.00010 | **PASS** |

**Decision (frozen rule): INCONCLUSIVE** — FG fails on bond_wrap
(chi2_red 4.738 ≥ 4.0), the same pre-existing small-L torus-wrap
non-monotonicity as EXP-0005. Every other gate passes, including all p_c
threshold reproductions (H0-relevant content) and the now-definitive C8.

## Comparison with EXP-0005

| | EXP-0005 (frozen) | EXP-0005 (corrected diag) | EXP-0006 (this run) |
|---|---|---|---|
| grid step L=256/512 | 0.02 | 0.02 (same cells) | **0.004** |
| C8 1/nu | 1.2384 FAIL | 0.7922 PASS (s0=0.10) | **0.7375 PASS** |
| C8 n/a estimate | — | — | 0.7366 ± 0.0127 |
| bond_span chi2_red | 2.760 | 2.760 | **0.059** |
| bond_span a | 0.49882 | 0.49882 | **0.50021** |
| bond_wrap chi2_red | 4.738 | 4.738 | 4.738 (same cells) |
| widths L=256/512 (s0=0.05) | 0.00203/0.00182 (degenerate) | — | **0.00653/0.00391** (physical) |
| C7 independent re-implementation | not run | not run | **PASS (39/39)** |

EXP-0005's two estimator failures are both resolved or characterised:

1. **C8 width-route**: resolved definitively — with the fine grid the estimate
   is stable at 1/nu = 0.7375 (95% CI [0.7124, 0.7608]), consistent with 3/4.
   The EXP-0005 corrected re-fit (0.7922) pointed the same way; this run
   confirms it with adequately resolved widths.
2. **FG on bond_wrap**: reproduced unchanged (4.738) — a genuine small-L
   torus-wrap finite-size artifact, not a bug and not physics failure. It is
   the sole remaining gate failure and the sole reason the experiment is
   INCONCLUSIVE rather than H0_SUPPORTED.

## Verdict for Q-P004

- The physical content of Q-P004 (HYP-004 P1/P2/P3 thresholds) is reproduced:
  all three |a − anchor| ≤ 0.0013 with every applicable gate green, and a
  genuinely independent C7 implementation now confirms the counts.
- C8 (P4, diagnostic) is now in-gate with proper resolution.
- The only obstruction to H0_SUPPORTED is the secondary bond_wrap FG fit
  (small-L non-monotonic p50). A targeted fix exists: extend bond_wrap to
  L=96,128,192 (preregistered as EXP-0007) to give ≥4 monotone fitting points
  and re-run the bond_wrap FSS. That is a hygiene follow-up, not new physics.
- Evidence level state: Q-P004 remains **INCONCLUSIVE (procedure-suspect) at
  the lab-registry level**; content-wise it is strongly H0-supportive. Whether
  to clear it via EXP-0007 is a user decision.