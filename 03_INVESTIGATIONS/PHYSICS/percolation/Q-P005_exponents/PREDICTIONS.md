# PREDICTIONS — Q-P005 (frozen before execution)

Frozen in CONFIG/prereg_EXP-0009.json. Values and windows committed BEFORE any
execution stream is drawn.

| # | measured | estimator | FSS model | expected | tolerance |
|---|---|---|---|---|---|
| P1 | D_f | mean largest-cluster mass E[M_max] | E[M_max] ~ a L^{D_f} | 91/48 = 1.895833 | ± 0.015 |
| P2 | gamma/nu | chi(L) = (sum_c s_c^2)/(occ N) | chi ~ a L^{gamma/nu} | 43/24 = 1.791667 | ± 0.03 |
| P3 | beta/nu | P_inf = E[M_max]/L^2 | P_inf ~ a L^{-(2 - D_f)} | 5/48 = 0.104167 | ± 0.015 |
| P4 | tau (direct) | cumulative rank N_>(s) ~ s^{-(tau-1)} @ L=1024 | range s in [32, 4096] | 187/91 = 2.054945 (asymptotic) | apparent window [1.885, 2.225] AND rising-toward-2.055 trend over L (shared range [32,2048], L 256->512->1024) |
| P5 | 1/nu | probit width sigma(L), log-log slope | sigma ~ L^{-1/nu} | 3/4 | in [0.60, 0.90] |
| R1 | tau vs D_f | direct tau_meas vs 1 + 2/D_f_meas (independent routes) | | equal | ± 0.12 |
| R2 | 2 beta/nu + gamma/nu | from P3 + P2 | | 2 | ± 0.05 |
| R3 | D_f vs beta/nu | P1 vs 2 - beta/nu | | equal | ± 0.015 |

Conventions:

- n_s(s) ~ s^{-tau} f(s / s_max); s_max ~ L^{D_f}; at p_c the bulk part
  s << s_max is a pure power law. Cumulative: E[#clusters of size >= s] ~
  s^{-(tau - 1)}.
- **Tau crossover note (pre-registration rationale):** the raw Fisher exponent
  187/91 is only reached asymptotically (s -> s_max); measured apparent tau at
  lattice-to-moderate s in finite L-boxes sits ~1.8-2.0 (documented crossover)
  and rises toward 2.055 with L. The direct gate is therefore an apparent
  window (stronger than a no-test but honest about the crossover) plus a
  monotone L-rise check at fixed log-size range. The PRECISE tau test is R1
  against 1 + 2/D_f measured (deterministic hyperscaling identity).
- chi defined over ALL open clusters (largest included) as
  (sum_c s_c^2)/(occ * N) with occ = fraction of open sites; the density
  factor cancels in the log-log slope and only the exponent is used.
- beta/nu is measured two ways as a built-in check: slope of log P_inf (fitted
  as -(2 - D_f_meas)) and the algebraic 2 - D_f_meas; P3 reports the fitted
  slope value, R3 checks the algebraic identity.

Additional reported, NOT gated: P(vertical spanning) at p_c per L (universal
constant region; corroboration only), chi2_red of each log-log fit, bootstrap
CIs (2000 draws) for every slope.