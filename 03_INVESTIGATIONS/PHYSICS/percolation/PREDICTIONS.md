# PREDICTIONS — EXP-0005 (frozen before execution)

## Systems / grids / counts (frozen in CONFIG/prereg_EXP-0005.json — run script reads them)

### bond_span (PRIMARY — open square L x L, BOND percolation, vertical spanning)
- L in {64, 128, 256, 512}
- p-probe grid: L in {64,128} -> 0.38..0.62 step 0.02 (13 pts); L in {256,512} ->
  0.44..0.56 step 0.02 (7 pts)
- realisations per (L, p): {64:1500, 128:1500, 256:1200, 512:1000}
- primary seed 42 (label "perc-bond-span").

### bond_wrap (SECONDARY — torus BOND percolation, horizontal wrap, universal-cover strip with toroidal rows)
- L in {32, 48, 64}
- p-probe grid: all L -> 0.38..0.62 step 0.02 (13 pts)
- realisations per (L, p): {32:1200, 48:900, 64:600}
- primary seed 42 (label "perc-bond-wrap").

### site_span (SECONDARY/calibration anchor — open square L x L, SITE percolation, vertical spanning)
- L in {64, 128, 256}
- p-probe grid: 0.547746 + 0.015*k, k in {0..6} -> {0.547746, 0.562746, 0.577746,
  0.592746, 0.607746, 0.622746, 0.637746} (7 pts; centre = literature p_c)
- realisations per (L, p): {64:1500, 128:1200, 256:1000}
- primary seed 42 (label "perc-site-span").

### C6 (seed ladder) — bond_span L=64, all 13 p-points, seeds {7,123,2023,314159,271828}
### C7 (independent impl) — REPLICATION/independent_check.py re-runs bond_span
###   L in {64,128} and bond_wrap L=32 on identical streams with a pure-Python
###   union-find router (no scipy.ndimage)

## Fitting (frozen)

- p50(L): root of P(p) = 0.5 by linear interpolation of the two bracketing grid
  points; SE from 500-iteration parametric bootstrap (Binomial(k_i, P(p_i))
  resample, seeded rng "perc-boot-<system>", seed 42).
- FSS: p50(L) = a + b * L^(-3/4), weighted least squares, weights 1/SE^2, over all
  L with complete cells; a = p_c_ext. Fixed 1/nu = 3/4.
- Diagnostic free-1/nu: probit-scale crossing width s(L) from each L's (p, P)
  point set (MLE), log-log slope -1/nu against L (report; gate [0.60, 0.90]).

## Quantitative predictions

1. (P1, primary gate) bond_span: |p_c_ext - 0.5| <= 0.01.
2. (P2, gate) bond_wrap: |p_c_ext - 0.5| <= 0.01.
3. (P3, calibration gate) site_span: |p_c_ext - 0.5927460508| <= 0.01.
4. (C2) bond_span vs bond_wrap extrapolated p_c within 0.005 of each other.
5. (C4 / scale stability) dropping L in {64, 128} from bond_span FSS: |delta p_c_ext|
   < 0.005.
6. (C7 / independent impl) per-L p50 from REPLICATION/ within 0.005 of primary
   p50, and identical raw span/wrap counts on the same seeded streams (sampled
   cells: bond_span L in {64,128} all-p, bond_wrap L=32 all-p).
7. (FG / fit gate) reduced chi^2 of every FSS fit < 4.
8. (C8 diagnostic) 0.60 <= 1/nu_width <= 0.90.
9. (Corroboration, NOT a gate) bond horizontal-spanning p50 at L=512 within 0.02
   of 0.5.

## What we do NOT predict

- NOT a novel threshold, NOT a tighter-than-literature p_c, NOT a proof of any
  exponent. beta/nu and P_inf are out of scope (report-only, no gate).
- NOT "no small-L deviations": small-L p50 sits away from p_c by the b*L^-3/4 term
  even on the null; that IS the model.

## Registered outputs

- Per (system, L, p, seed): counts (span_vert k_v, span_horiz k_h, or wrap k) and n.
- Per system: p50(L)+SE, p_c_ext + bootstrap SE, chi2_red, 1/nu_width, C4 shift,
  C7 table, C6 table, decision label.