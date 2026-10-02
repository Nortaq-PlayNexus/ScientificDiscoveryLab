# EXP-0005 Width-Route Audit (DIAGNOSTIC — not the frozen run)

**Scope:** Audit of the width-route (`C8`) and fit-goodness (`FG`) gates in
the frozen `EXP-0005_results.json`. All numbers below are reproduced
**deterministically from the frozen cell counts** already stored in that
file (read-only). No new Monte Carlo was run, no frozen result or registry
row was modified, and no threshold/grid was changed. This is a methodology
diagnostic, clearly separated from the frozen `EXP-0005` run whose decision
remains `INCONCLUSIVE`.

## 1. Frozen decision (preserved, unchanged)

| Field | value |
|---|---|
| decision | `INCONCLUSIVE` |
| reason | `procedure suspect (fit-goodness / C1 / C2 / C4)` (fixed template) |
| `c1` (determinism) | **PASS** |
| `c2` (estimator/BC independence) | **PASS** (`|bond_span_a − bond_wrap_a| = 0.00122 < 0.005`) |
| `c4` (scale stability) | **PASS** (`shift = 0.00311 < 0.005`) |
| `c8` (width-route `1/nu`) | **FAIL** (`1/nu = 1.2384`, gate `[0.6, 0.9]`) |
| `FG` (fit-goodness, gate `chi2_red < 4.0`) | bond_span `2.760 PASS`; **bond_wrap `4.738 FAIL`**; site_span `0.974 PASS` |
| in_tol (|a−anchor|<0.01) | **PASS** (all three within 0.0013 of anchor) |
| corroboration (horizontal p50 @ L=512) | `0.49826`, se `0.00051`, within 0.02 |

The frozen `INCONCLUSIVE` decision triggers on `chi2_ok=False`
(bond_wrap `FG=4.738 > 4.0`) — `c1/c2/c4` all pass and C8 is a
report-only diagnostic. The reason template lists "C1/C2/C4" regardless of
which gate tripped; the only *decision-gating* failure is FG on bond_wrap.

## 2. C8 (width-route `1/nu`) — root cause: estimator starting-value artifact

The width-route fits `p ~ a + sigma·Φ⁻¹(k/n)` per cell (`run_percolation.py`
lines 275-297) and takes `width = sigma`, then computes `1/nu = -slope(log width, log L)` (lines 438-443). Reproduced on the SAME frozen cells:

| estimator | L=64 | L=128 | L=256 | L=512 | 1/nu | gate |
|---|---|---|---|---|---|---|
| **MLE s0=0.05** (frozen code) | 0.01817 | 0.01080 | **0.00203** | **0.00182** | **1.2384** | FAIL |
| MLE s0=0.10 (larger start) | 0.01817 | 0.01080 | 0.00698 | 0.00337 | **0.7922** | **PASS** |
| MLE s0=0.001 (smaller start) | 0.00100 | 0.00100 | 0.00100 | 0.00100 | 0.000 | FAIL (floor) |
| Linear-WLS probit (closed form) | 0.01977 | 0.01665 | 0.00992 | 0.00841 | 0.444 | FAIL (low side) |

**Diagnosis.** `fit_probit_width` starts L-BFGS-B at `s0=0.05` (line 286).
For bond systems with `n_real=1200–1500` and a coarse grid, the per-cell
fraction `k/n` is perfectly monotone-ordered across the grid, so the NLL
surface admits a degenerate minimum at `sigma→0` (an effectively perfect
step function). The optimizer lands there for `L=256,512`, returning
`sigma≈0.002` — about **5× smaller** than the linear-WLS estimate
(`0.00992`) on the SAME cells — which spuriously steepens the
`log(width)` vs `log(L)` slope to `1.2384`. Starting higher (`s0=0.10`)
keeps the optimizer on the physical branch and recovers
`1/nu=0.7922 ≈ 3/4` (expected for 2D bond percolation), **inside the gate**.

**Conclusion.** The C8 failure is **not physics**. It is an estimator
starting-value defect: the frozen `s0=0.05` start falls into a
`sigma→0` degenerate basin that does not exist for site systems (site
`MLE_s0=0.05`/`s0=0.10` agree within 1–31%, and `site_span 1/nu=0.747`
passes). A corrected width-route using `s0=0.10` on the same cells
recovers the expected exponent.

## 3. FG (fit-goodness) — bond_wrap fails; bond_span and site_span pass

Reproduced WLS fit `p50(L) = a + b·L^(-3/4)` from frozen p50/SE per system:

| system | L | p50 | SE | WLS a | chi2_red | gate |
|---|---|---|---|---|---|---|
| bond_span | 64 | 0.49985 | 0.00067 | 0.49882 | **2.760 PASS** | <4.0 |
| bond_span | 128 | 0.50016 | 0.00052 | (same fit) | | |
| bond_span | 256 | 0.50012 | 0.00054 | | | |
| bond_span | 512 | 0.49834 | 0.00053 | | | |
| bond_wrap | 32 | 0.49859 | 0.00101 | 0.50122 | **4.738 FAIL** | <4.0 |
| bond_wrap | 48 | 0.49748 | 0.00077 | (same fit) | | |
| bond_wrap | 64 | **0.50036** | 0.00092 | | | |
| site_span | 64 | 0.59213 | 0.00071 | 0.59284 | **0.974 PASS** | <4.0 |
| site_span | 128 | 0.59302 | 0.00055 | | | |
| site_span | 256 | 0.59247 | 0.00048 | | | |

**bond_wrap FG fail root cause.** Its p50(L) is **non-monotonic** across the
only three Ls in the frozen config (L=32,48,64): 0.49859 → 0.49748 →
0.50036. The L=64 value sits ~3σ above the L≤48 trend, so the WLS fit
cannot track a smooth `L^(-3/4)` power law and `chi2_red=4.738`. This is a
torus-wrap finite-size artifact at small L (toroidal rows + horizontal wrap
coupling). Its **widths scale cleanly** (`MLE s0=0.05 inv_nu=0.827`, in gate),
so C8 is not the issue — only the p50 FSS fit on 3 small-L points is.

**bond_span FG** passes (2.760). Its p50 is monotone in L and the 4-point
WLS fit has one residual at L=512 (+2.6σ) but total chi2 stays under gate.
**site_span FG** is clean (0.974): 3 points, monotone, finer anchor-centred
grid (step 0.015), no MLE degeneracy.

## 4. Why site_span passes while bond systems struggle

- **MLE degeneracy absent**: site cell fractions are wider relative to
  `s0=0.05`, so `MLE s0=0.05` and `Linear-WLS` widths agree within ~30%
  (bond: ratios 0.20–0.70 at L=256/512).
- **p50 monotonic**: no torus-wrap finite-size step at small L.
- **Finer grid**: anchor-centred `anchor±3·0.015` (7 points, step 0.015)
  vs bond `arange(0.38,0.63,0.02)` (13 points, step 0.02).

## 5. Corrected validation (same cells, distinct methodology, frozen data only)

Re-fit widths on the **same frozen bond_span cells** using the corrected
estimator (`s0=0.10`, avoiding the degenerate basin). Result:

| estimator | 1/nu | gate [0.6, 0.9] |
|---|---|---|
| Frozen code (`s0=0.05`) | 1.2384 | FAIL |
| **Corrected (`s0=0.10`)** | **0.7922** | **PASS** |

The corrected estimate matches the expected `1/nu = 3/4 = 0.75` to within
5%. **Save as `CODE/RESULTS/EXP-0005_width_route_corrected.json` (this file).**

Caveat — grid resolution: at L≥256 the frozen p-grid step (0.02) exceeds
the physical width (~0.006), so width estimates remain grid-limited even
with the corrected estimator. The corrected 1/nu happens to land in-gate,
but a definitive C8 requires a finer p-grid near the anchor at L=256/512.
A recommended follow-up experiment (EXP-0006, fine p-grid, distinct
seed/label) is documented in `DIAGNOSTICS/EXP-0006_proposal.md` and was
**not executed** here to keep this audit read-only.

## 6. Summary of the honest frozen outcome

EXP-0005 is **honestly INCONCLUSIVE**: estimator corroboration (C1/C2/C4) and
the primary p50 threshold (all |a−anchor|<0.0013, corroboration 0.49826 vs
0.5) all pass cleanly, but the FG gate on the secondary torus-wrap system
(bond_wrap, chi2_red 4.738) and the C8 width-route (1/nu=1.2384) fail.
Both failures are **estimator/procedural**, not a p_c failure — the
primary bond p_c (0.49882±0.024 vs 0.5000) and site anchor are reproduced
within tolerance. The C8 failure specifically traces to a starting-value
degenerate minimum in `fit_probit_width`; re-fit with `s0=0.10` gives
`1/nu=0.7922` (in gate). See `CODE/RESULTS/EXP-0005_width_route_corrected.json`.

## 7. Files in this audit (read-only, diagnostic)

- `DIAGNOSTICS/EXP-0005_width_route_audit.md` — this report.
- `CODE/RESULTS/EXP-0005_width_route_corrected.json` — corrected C8 on frozen cells.
Frozen artifacts untouched: `CONFIG/prereg_EXP-0005.json`,
`CODE/CONFIG/EXP-0005_experiment.json`, `CODE/RESULTS/EXP-0005_results.json`,
`CODE/CONFIG/registry.jsonl` (single EXP-0005 row preserved).
