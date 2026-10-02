# CONTROLS — Q-P005 (EXP-0009, frozen before execution)

Compatibility gates (mirror Q-P004/EXP-0007 discipline; expanded for stats):

- **C1 — Determinism**: rerun one full exponent cell (L=256, p_c) twice in the
  same session; the open-cluster census must agree bit-for-bit (sha256 of the
  serialized cluster-size arrays). Recorded as C1 hash equality, k cells
  identical over k = 1 full-cell reruns + all L-cells deterministic signature.
- **C6 — Seed ladder** (budget revision, pre-execution): rerun E[M_max](L=256),
  chi(L=256) (n=150/seed), and the L=128 p-scan W-curve at the 3 inner grid
  points (n=150/seed) with the OTHER five ladder seeds (7, 123, 2023, 314159,
  271828) vs the primary seed 42. Gate: each statistic within 3 joint-SE of
  the seed-42 value (joint SE = quadrature). Same seed family as EXP-0004/0007.
- **C7 — Independent implementation**: REPLICATION/independent_check_exp0009.py
  (pure-Python union-find; NO scipy.sparse) recomputes, on the IDENTICAL
  streams (same rng label + seed), a subsample (n=40 at each of L in
  {128, 256, 512}):
  - per-realization M_max and chi bit-identical vs the engine's census; and
  - D_f over the union-find subsample within 3 joint-SE.
- **C5 — Estimator variation (replaces old "second estimator" intent)**: at
  L=128 the cumulative-rank tau and the direct-histogram tau are both computed;
  |tau_cum - tau_hist| reported (diagnostic, not gated).
- **FG — Slope stability**: each log-log slope (D_f, gamma/nu) refit on the
  three inner sizes {256, 512, 1024}; gate |slope_inner - slope_full| <= 0.02
  (D_f) and <= 0.04 (gamma/nu). Catches one-size leverage.
- **PC1 — Statistical-power audit**: bootstrap SE (2000 draws) reported for
  every exponent; chi2_red of every log-log fit reported (n_eff >= 4 sizes,
  >= 4*fitted-params rule respected).

Non-gate rigor notes (contrast with Q-P004 where relevant):
- All random draws via G_LAB rng(label, seed): labels "exp9-<system>-L<L>-p<canonical>-<kind>",
  primary seed 42. Frozen before any draw.
- Every count in Python int / numpy int64 (Windows overflow lesson, EXP-0004).
- The open-cluster census drops closed-site singletons by construction
  (site_cluster_sizes; engine-internal check).
- p is set to the Ziff value 0.59274605079210(2) for exponent cells — the
  cohort-fallacy trap (using p = 0.5, the BOND anchor, for a SITE experiment)
  is pre-empted by naming each cell "p-canonical".
- No tuning of windows or fit ranges after execution (frozen in prereg).