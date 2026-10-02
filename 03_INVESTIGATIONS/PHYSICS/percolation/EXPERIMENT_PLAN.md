# EXPERIMENT_PLAN — EXP-0005 (percolation thresholds)

## Purpose

Calibrate the lab's random-lattice Monte Carlo machinery against EXACT/known
anchors: bond percolation p_c = 1/2 (square lattice, theorem), site percolation
p_c ~= 0.59274605 (high-precision numerics), diagnostic on nu = 4/3. Same
epistemic posture as EXP-0002/0003/0004: known-law reproduction / infrastructure
certification. Evidence ceiling: CONTROLLED.

## Systems

| system | lattice | estimator | boundaries | engine |
|---|---|---|---|---|
| bond_span (PRIMARY) | open L x L, bond | P(vertical spanning) | open | scipy.ndimage batched labeling |
| bond_wrap (SECONDARY) | L x L torus, bond | P(cluster wraps horizontally) | periodic | pure-Python union-find strip (toroidal rows) |
| site_span (calibration) | open L x L, site | P(vertical spanning) | open | scipy.ndimage batched labeling |

## Estimators (exact definitions)

- Vertical spanning (open): a cluster connects row 0 to row (L-1). Implemented with
  scipy.ndimage.label, 4-connectivity, over a (batch, L, L) bool stack; a layer
  spans iff any connected-component label appears in both its row-0 and row-(L-1)
  slices. Horizontal spanning (row-0..; col 0 to col L-1) is recorded for free as
  corroboration (not a gate).
- Torus wrap (pure-Python): bonds on an L x (2L) universal-cover strip; columns
  L..2L-1 are periodicates of 0..L-1 (same bond states). Row edges are toroidal
  (row L-1 connects to row 0). Horizontal wrap iff some component contains (r, c)
  and (r, c+L). Winding-number-correct — certified against naive boundary-column
  tests in planning checks.
- Site percolation: sites open w.p. p; nearest-neighbour adjacency of open sites;
  same spanning detector.

## Data generation

- Every random draw comes from G_LAB rng(label, seed): labels "perc-bond-span",
  "perc-bond-wrap", "perc-site-span" (+ per-cell sub-labels), seeds = SEED_LADDER.
  Primary seed 42; C6 uses the other five.
- Edge/site state: u ~ U(0,1); open iff u < p. Independent per (system, L, p, seed).
- Counts in Python int (Windows uint8-overflow lesson, EXP-0004).

## Analysis (frozen)

1. p50(L): P(p)=0.5 root by linear interpolation of bracketing grid points.
2. p50 SE: parametric bootstrap (500 draws), resampling k_i ~ Binomial(n_i, P(p_i)),
   seeded rng "perc-boot", seed 42.
3. FSS: p50(L) = a + b L^(-3/4); WLS (weights 1/SE^2); a = p_c_ext.
4. C4: refit without L in {64,128}.
5. Diag: probit-width s(L) MLE per L; log-log slope -> 1/nu (report; gate [0.6,0.9]).
6. C7: REPLICATION/independent_check.py (pure-Python union-find, no ndimage).

## Decision rule (exact, frozen)

Let dX = |p_c_ext(X) - anchor_X| for X in {bond_span, bond_wrap, site_span} with
anchors 0.5, 0.5, 0.5927460508.

- If FG fails (any chi2_red >= 4) OR C1 fails OR C2 conflict (|wrap - span| > 0.005)
  OR C4 shift >= 0.005 OR C7 mismatch -> **INCONCLUSIVE** (procedure suspect; fix
  per lab flow, re-run — do NOT tune the gate).
- Else if all dX <= 0.01 -> **H0_SUPPORTED** (evidence CONTROLLED; thresholds
  reproduced through a controlled pipeline).
- Else (some dX > 0.01 with gates green) -> **ABNORMAL**: a consistent, unexplained
  deviation from known physics; escalate, report only, do not interpret.

## Scripts

- CODE/run_percolation.py — generate, fit, decide; writes RESULTS/EXP-0005_results.json,
  CONFIG/EXP-0005_experiment.json, CONFIG/registry.jsonl (append-only).
- CODE/make_figure.py — EXP-0005 figure.
- REPLICATION/independent_check.py — C7.
- Reads parameters from CONFIG/prereg_EXP-0005.json (single source of truth).