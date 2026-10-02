# README — Percolation thresholds and exponents (Q-P004 / HYP-004 / EXP-0005..0007)

Status: **EXP-0007 H0_SUPPORTED — Q-P004 CLOSED (evidence CONTROLLED).**
EXP-0005 froze the pipeline (INCONCLUSIVE: two estimator-gate artefacts);
EXP-0006 resolved the width-route (bond_span fine grid, 1/nu=0.7375);
EXP-0007 resolved the sole remaining gate (bond_wrap fit-goodness, chi2_red
4.738→2.239) by extending to L=96/128/192. All thresholds reproduce published
anchors; width-route diagnostic consistent with textbook 1/nu = 3/4. Primary =
bond percolation threshold on the square lattice (anchor p_c = 1/2, exact);
secondary anchor = site percolation (p_c ~= 0.59274605, high-precision
numerical). Exponents (nu ~ 4/3, beta/nu ~ 5/48) reported as secondary checks.

Layout (lab template): QUESTION, LITERATURE, HYPOTHESIS, PREDICTIONS, CONTROLS,
EXPERIMENT_PLAN; CONFIG/ (frozen prereg + append-only registry), CODE/,
RESULTS/, FIGURES/, REPLICATION/, FALSIFICATION/, REPORT/.

Verdict is decided by the preregistered rule in EXPERIMENT_PLAN.md (H0_SUPPORTED /
ABNORMAL / INCONCLUSIVE) exactly as for EXP-0003/0004. No thresholds or test
inventories may be changed after the preregistration is frozen.

Field note: percolation is the classical statistical-physics model of connectivity
in random media; this is a HYGIENE/reproduction project (known values, controlled
pipeline) — not an attempt at novelty.