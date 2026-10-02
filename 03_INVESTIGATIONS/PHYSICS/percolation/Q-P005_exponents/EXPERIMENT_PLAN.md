# EXPERIMENT_PLAN — Q-P005 / EXP-0009 (frozen before execution)

## Purpose

Reproduce the 2D percolation universality-class critical exponents and their
hyperscaling relations through the lab's controlled pipeline, at the exact
square-site critical point. Evidence ceiling: CONTROLLED (no novelty).

## System

Square lattice site percolation, open BC, p = p_c = 0.59274605079210(2)
[Ziff PRL 117, 125703 (2016)]. Fresh streams (these cells were never drawn
in EXP-0005/0006/0007).

| L | n_real | purpose |
|---|---|---|
| 128 | 1500 | D_f, gamma/nu, beta/nu, tau(hist cross-checks), width route |
| 256 | 700 | D_f, gamma/nu, beta/nu, width route |
| 512 | 150 | D_f, gamma/nu, beta/nu, tau-trend, width route |
| 1024 | 60 | D_f, gamma/nu, beta/nu, tau (primary, cumulative + hist) |

(BUDGET REVISION, pre-execution, 2026-09-18: measured per-real costs on this
machine (0.09 s @L=256, 2.75 s @L=1024) made the original n_real
{1500,700,300,100} too heavy; trimmed 512->150 and 1024->60. All bootstrap SEs
stay far below gate tolerances at these sizes. Nothing executed before this
revision.)

Width route (probit): site square at L in {64, 128, 256} with per-L grids
that resolve sigma(L) (step <= ~0.7 sigma): L=64 arange(0.53,0.65,0.01)
n=1200; L=128 arange(0.55,0.63,0.01) n=800; L=256 arange(0.57,0.622,0.008)
n=400. sigma(L) ~ L^{-1/nu}, slope over 3 sizes. (L=512 sigma ~
0.007 < 0.01 grid step and would be under-resolved — deliberately dropped.)

## Estimators (exact definitions)

- Open-cluster census: per realization, from the CSR component labels
  restricted to the open subset (closed-site singletons excluded by
  construction — `site_cluster_sizes` in ENGINE/perc_engine.py).
- M_max = max cluster size; chi = (sum_c s_c^2)/(occ*N) over ALL open clusters;
  P_inf = M_max/N with N = L^2.
- D_f: slope of log E[M_max] vs log L (4 sizes), SE by 2000 bootstrap draws
  over realizations (resample-within-L, refit).
- gamma/nu: slope of log E[chi] vs log L, same bootstrap.
- beta/nu: slope of log E[P_inf] vs log L (built-in check vs 2 - D_f).
- tau: aggregate ALL open clusters from the L=1024 cell (excluding the largest
  per realization); primary = cumulative-rank fit log N_>(s) = c + (1-tau) log s
  over s in [32, 4096] (apparent window [1.885, 2.225] gate); crossover trend
  tau over the SHARED range [32, 2048] at L in {256, 512, 1024} must rise
  toward 2.055 (L=512 >= L=256 - se, L=1024 >= L=512 - se). Precise tau test:
  R1 vs 1 + 2/D_f, tol 0.12.
- 1/nu: probit MLE width sigma(L) per L (start s0 = 0.10, EXP-0005 lesson);
  log-log slope of sigma vs L over {64, 128, 256}.

## Data generation

random streams: rng(label, seed); seed 42 primary; ladder {7,123,2023,314159,271828}
for C6. Labels follow "exp9-<system>-L<L>-p<pcanon>-<kind>"; the canonical p
token is "p0592746". Streams are NOT shared with any prior experiment.

## Analysis (frozen)

1. Exponent fits via weighted log-log OLS (weights 1/SE^2 from bootstrap).
2. Bootstrap: 2000 draws, G_LAB seeded "exp9-boot", seed 42.
3. tau fits on deterministic sorted aggregates (no bootstrap needed; report fit
   SE by weighted OLS on 250 equispaced log-size points).
4. Probit width via engine probit_fit (s0=0.10), slope via 2-point log-log.
5. C6: seed-ladder comparison; C7: REPLICATION/independent_check_exp0009.py.

## Decision rule (exact, frozen)

- If C1, C6, C7, FG all PASS:
  - P1-P4 in tolerance AND R1-R3 in tolerance AND P5 in [0.6, 0.9] ->
    **H0_SUPPORTED** (evidence CONTROLLED; exponents + relations reproduced).
  - else -> **ABNORMAL** (green gates but missed windows; escalate, do not
    interpret).
- If any gate FAILS -> **INCONCLUSIVE** (procedure suspect; fix per lab flow,
  re-run; do NOT tune windows).

## Scripts

- CODE/run_exp0009.py — draws cells, computes statistics, fits, runs gates,
  writes RESULTS/EXP-0009_results.json + EXP-0009_summary.json,
  CONFIG/EXP-0009_experiment.json, CONFIG/registry.jsonl (append-only).
- REPLICATION/independent_check_exp0009.py — C7 (pure-Python union-find).
- Reads parameters from CONFIG/prereg_EXP-0009.json (single source of truth).