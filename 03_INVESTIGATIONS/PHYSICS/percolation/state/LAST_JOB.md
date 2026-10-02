# LAST_JOB.md — Percolation Investigations

## 2026-09-19 — Phase 2 completion, Q-P006 audit, Q-P008 setup

### What was done
- **Q-P007 Phase 2 — COMPLETE**: Fixed 3 bugs in run_phase2.py (KeyError 'chis'/'pinfs' from pe.run_span_cell_edges, format strings `:.12d`→`:.12f`, added per-L .npz checkpoint caching). Ran successfully in 813s. p_c(L→∞)=0.592729 (|dev| from Ziff: 0.000017). All 3 exponents PASS at refined p_c: D_f=1.8818, gamma/nu=1.7653, beta/nu=0.1189. tau=N/A (diagnostic limitation). Results in Q-P007/CODE/RESULTS/. Cell checkpoints saved for L in {512,1024,2048}.
- **Q-P006 audit**: Numerical verification complete. All 4 exponents deviate. Bugs and gaps documented in AUDIT_Q006_Q007.md. Q-P006 now CLOSED.
- **Q-P008**: Investigation directory created at 03_INVESTIGATIONS/PHYSICS/percolation_3d/. Prereg frozen (EXP-0011). 3D cubic lattice implemented in perc_engine.py (verified correct).
- **Q-M007 audit**: Chi2 decomposition, residuals, normalization all verified. H1_SUPPORTED confirmed.
- **Documentation**: Updated CURRENT_STATUS.md, QUESTIONS.md, CHANGELOG.md, state/LAST_JOB.md, EXPERIMENT_REGISTRY.md, run.log, run.err.

### Key numbers
- Q-P007 p_c(L→∞): 0.59272900
- Q-P007 exponents at refined p_c: D_f=1.882 (PASS), gamma/nu=1.765 (PASS), beta/nu=0.119 (PASS)
- Q-P006 exponents: D_f=1.863, gamma/nu=1.730, beta/nu=0.137, tau=1.975
- 3D lattice verified: L=4→64 nodes, 144 edges; L=2→8 nodes, 12 edges

### What failed
- Q-P007 Phase 2 bugs (fixed): KeyError 'chis'/'pinfs', format strings, no caching
- tau diagnostic: returns None (0 tail clusters at L=2048 with n=25 — known limitation near p_c)

### What remains
- Q-P008: write runner script (Q-P008/CODE/run_exp0011.py)
- Q-M008: plan prime gap scaling test at 10^9/10^10 (PLAN.md created)
- Q-S9-4: cone-mosaic aliasing check setup (prereg draft ready)
