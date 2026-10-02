# Changelog — Q-M005 / Feigenbaum constants

## 2026-09-21 — EXP-0014 complete (z=2 validated)

- Created investigation directory `03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/`.
- Registered Q-M005 as unstarted (verified: no prior investigation exists).
- Created preregistration (prereg_EXP-0014.json) with frozen protocol.
- Created QUESTION.md, HYPOTHESIS.md, LITERATURE.md, PREDICTIONS.md, CONTROLS.md, EXPERIMENT_PLAN.md, README.md.
- Implemented feigenbaum_engine.py (superstable-cycle finder with period verification) and run_feigenbaum.py (orchestrator).
- **Ran EXP-0014**: For z=2, computed superstable parameters a_1..a_8 and delta_n for n=3..8.
  - delta_3 = 4.3857, delta_4 = 4.6009, delta_5 = 4.6551, delta_6 = 4.6661, delta_7 = 4.6685, delta_8 = 4.6691.
  - Converges to Feigenbaum constant 4.6692016091029 (deviation at n=8: 1.4e-4).
  - Control C1 (reproduction), C3 (seed variation), C6 (precision), C7 (independent check) PASS.
  - z=3,4: delta_3 computed; higher convergence needs refined bracketing.
- EXP-0014 status: PARTIAL — z=2 COMPLETE/SUPPORTED, z=3,4 IN PROGRESS.
- Next: refine z=3,4 superstable parameter search; write technical and plain reports.
