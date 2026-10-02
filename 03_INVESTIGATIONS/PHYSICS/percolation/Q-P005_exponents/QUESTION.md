# QUESTION — Q-P005 (EXP-0009)

- QUESTION_ID: Q-P005
- FIELD: physics (statistical physics / percolation universality class)
- PARENT: Q-P004 (thresholds; CLOSED H0_SUPPORTED, EXP-0007). Q-P005 deepens
  the calibration into the *critical regime*: it does NOT rederive thresholds.
- QUESTION: In this lab's controlled Monte Carlo pipeline, at the known square
  site percolation critical point p_c = 0.5927460508, do the finite-size
  measurements of (i) largest-cluster mass, (ii) mean cluster size, (iii)
  cluster-size distribution, and (iv) crossing-width, reproduce the 2D
  percolation universality-class exponents D_f = 91/48, gamma/nu = 43/24,
  tau = 187/91, 1/nu = 3/4 — and their scaling relations
  (tau = 1 + d/D_f, 2*beta/nu + gamma/nu = d = 2, D_f = 2 - beta/nu)?
- WHAT SCIENTISTS ALREADY KNOW: Critical percolation in 2D is exactly solvable
  via Coulomb-gas / conformal field theory (Nienhuis 1982; Cardy). The
  universal exponents of the class are beta = 5/36, gamma = 43/18, nu = 4/3,
  tau = 187/91, D_f = 91/48. The scaling relations tau = 1 + d/D_f, beta/nu =
  2 - D_f, and 2*beta/nu + gamma/nu = d are textbook (Stauffer & Aharony).
  High-precision numerical determinations agree with these to ~1e-4.
- WHAT REMAINS UNKNOWN (for this lab): whether OUR estimators — graph-CSR
  connected-components, open-cluster census, unconstrained log-log FSS over 4
  self-similar sizes, rank/cumulative tau estimators, probit width route —
  reproduce the class exponents through the lab's pre-registered discipline.
  This is infrastructure calibration (evidence ceiling CONTROLLED), no novelty.
- CURRENT THEORIES: Conformal invariance (universality of exponents and of
  crossing functions); hyperscaling relations; Fisher's cluster-size exponent
  conventions (n_s(s) ~ s^{-tau} f(s / s_max), s_max ~ L^{D_f}).
- KNOWN METHODS: Newman-Ziff algorithm; histogram-leaning; moment bootstrap
  FSS; CFT-transfer matrix; last-passage / hull methods. Lab uses direct MC +
  FSS (slower than NZ but estimator-clean for sizes up to ~10^6 sites).
- AVAILABLE DATA: None needed — computed. Frozen EXP-0005/0006/0007 artifacts
  are thresholds cells, not used here (this experiment generates NEW streams).
- COMPUTATIONAL REQUIREMENTS: CPU-minutes to ~15 min wall on this machine
  (L up to 1024, N = 2*10^6 CSR's per realization for the largest size).
- POSSIBLE EXPERIMENT: Run fresh site-percolation cells at NC = p_c(site) on
  L in {128, 256, 512, 1024}; per realization record the full open-cluster
  census. Then: D_f from log-log slope of E[M_max] vs L; gamma/nu from slope
  of log chi vs log L; tau from the cumulative rank plot of the aggregated
  cluster-size distribution at L = 1024; beta/nu from P_inf = E[M_max]/L^2 =
  L^{-(2 - D_f)}; 1/nu from probit width of a p-scan on L in {256, 512}.
  Check the three scaling relations with pre-committed tolerances.
- NULL HYPOTHESIS (H0): All measured exponents are within tolerance of the
  exact class values AND the three scaling relations hold AND the gates
  (C1 determinism, C6 seed ladder, C7 independent implementation, FG slope
  stability) pass.
- ALTERNATIVE HYPOTHESIS: A reproducible, gate-consistent deviation. Not
  anticipated; if seen, escalate, do NOT interpret.
- FALSIFICATION TEST: Decision gates in EXPERIMENT_PLAN.md / prereg_EXP-0009.
- EXPECTED DIFFICULTY: Low-Moderate. Compute is cheap; the delicate parts are
  the open-cluster census (closed-site singletons must be excluded — fixed in
  ENGINE) and the tau estimator range selection (finite-size cutoff s_max).
- LIKELY COMPUTATIONAL COST: ~10-15 min wall.
- KNOWN PITFALLS: (1) running above/below p_c breaks FSS (site square pc is
  0.5927, NOT 0.5 — the 0.5 anchor is BOND only); (2) naive bincount(labels)
  includes closed-site singletons in the census (fixed via open-subset
  restriction); (3) tau FSS cutoff: fit must stay well below L^{D_f} (tail
  curvature) and above lattice-scale s (small-s corrections); (4) width route
  degenerate sigma0 basin (EXP-0005 lesson) — probit start s0 = 0.10; (5)
  integer overflow on Windows numpy (EXP-0004 lesson) — int64 census.
- RELEVANT PAPERS: Nienhuis J.Phys.A 15 (1982) 199; Cardy 1992; Stauffer &
  Aharony *Introduction to Percolation Theory*; Ziff PRL 117, 125703 (2016)
  [p_c(site) precision]; Newman & Ziff PRL 85, 4104 (2000) [NZ algorithm];
  Stauffer (1979) [tau/hyperscaling conventions].
- WHY AI COULD HELP: A controlled, bootstrapped, pre-registered estimator
  pipeline is exactly the reproducibility hygiene that prevents "exponent
  overclaiming" from under-powered FSS fits.
- WHAT WOULD COUNT AS A REAL RESULT: Every exponent within tolerance of the
  exact class values through green gates + the three scaling relations
  verified with pre-committed windows. Same epistemic posture as Q-P004:
  CONTROLLED reproduction, no novelty.