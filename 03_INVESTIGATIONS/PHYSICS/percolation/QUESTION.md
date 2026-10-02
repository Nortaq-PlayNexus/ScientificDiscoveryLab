# QUESTION — Q-P004 (EXP-0005)

- QUESTION_ID: Q-P004
- FIELD: physics (statistical physics / percolation)
- QUESTION: Do bond and site percolation thresholds and the correlation-length and
  order-parameter exponents on the 2D square lattice, measured in this lab's
  controlled Monte Carlo pipeline, reproduce the published values (p_c(bond) = 1/2
  exact; p_c(site) ~= 0.59274605; nu = 4/3; beta/nu = 5/48)?
- WHAT SCIENTISTS ALREADY KNOW: On the square lattice, bond percolation threshold is
  exactly 1/2 (Kesten 1982; Wierman). Site threshold is p_c = 0.59274605079210(2)
  to high numerical precision (Newman-Ziff method; Ziff). The model is in the 2D
  percolation universality class; Nienhuis/CFT give beta = 5/36 and nu = 4/3, and
  numerical determinations agree to ~1e-4. Exact embedding/proofs for thresholds
  have a rich history (dual-graph arguments).
- WHAT REMAINS UNKNOWN (for this lab): nothing of substance; the open question is
  how well OUR pipeline (PRNG-certified streams, union-find flood estimators,
  finite-size scaling) reproduces these anchors — i.e., an infrastructure
  calibration. Q-P004 explicitly does NOT claim novel thresholds.
- CURRENT THEORIES: Conformal invariance / universality (Cardy's crossing formula);
  percolation as exactly solved at p_c in 2D via Coulomb-gas/CFT; the island/
  hull Lovász-relation (~1/2) and dual lattices.
- KNOWN METHODS: Direct Monte Carlo (Newman-Ziff efficient algorithm, wrapping
  clusters), transfer-matrix / matching, high-precision percolation (PADS), series,
  exact results via topology.
- AVAILABLE DATA: None needed — computed.
- COMPUTATIONAL REQUIREMENTS: CPU-minutes (union-find on square grids L <= 512).
- POSSIBLE EXPERIMENT: Measure wrapping (torus) and spanning (open) probabilities
  for bond and site percolation; per-L crossing p50; extrapolate with finite-size
  scaling p50(L) = a + b L^(-1/nu), nu = 4/3; compare with anchors.
- NULL HYPOTHESIS (H0): Extrapolated p_c equals the published anchor within
  tolerance 0.01, and the compatibility gates (C2, C4, C7) hold.
- ALTERNATIVE HYPOTHESIS: A reproducible deviation from the published anchors that
  is consistent across estimators and scales (would be an unexpected finding). Not
  anticipated; if seen, escalate, do NOT interpret.
- FALSIFICATION TEST: The decision gates in EXPERIMENT_PLAN.md; INCONCLUSIVE if the
  procedure breaks (estimator/BC disagreement, C7 mismatch, fit instability, RNG
  issues), exactly as the S2 trip worked in EXP-0004.
- EXPECTED DIFFICULTY: Low (compute trivial); the tricky content is estimator hygiene
  (wrapping vs spanning, finite-size corrections, BC effects).
- LIKELY COMPUTATIONAL COST: CPU-minutes (about 5-15 min wall on this machine).
- KNOWN PITFALLS: (1) wrapping detection on the torus is subtle (naive "touches
  both boundary columns" overcounts) — mitigated by an explicit period-connect
  universal-cover detector AND an independent open-BC spanning path (C2); (2)
  finite-size corrections to the p50 extrapolation are multi-term (subleading
  exponent + log terms) — mitigated by C4 scale-stability and C8 free-exponent fit;
  (3) RNG quality — mitigated by EXP-0004 RNG certification; (4) uint8 overflow
  on Windows numpy (EXP-0004 lesson) — all counting done in Python int or int64.
- RELEVANT PAPERS: Kesten (1982) 1/2 theorem; Wierman; Newman & Ziff PRL 85, 4104
  (2000); Ziff PRL 117, 125703 (2016) / p_c(site) high-precision; Nienhuis (1982);
  Stauffer & Aharony; Grygiel & Prellberg; Weygand & Ziff (subleading corrections).
- WHY AI COULD HELP: A controlled estimator + finite-size-scaling pipeline with the
  lab's fixed-false-positive discipline is exactly the kind of reproducibility
  hygiene that prevents the "threshold vs estimator" overclaiming common in
  informal percolation scripts.
- WHAT WOULD COUNT AS A REAL RESULT: A clean reproduction: both thresholds within
  tolerance through a controlled pipeline, with diagnostics (free-nu fit, scale
  stability, independent estimator agreement) all green. This certifies the lab's
  random-lattice machinery for future connectivity-type questions.