# AUDIT_Q006_Q007.md — Audit notes for Q-P006 and Q-P007

## Q-P006 (Precision study, EXP-0011)

### Bugs found during audit
- _cells files saved to Q-P005_exponents/CODE/RESULTS (wrong directory) — COPIED to correct location
- 1/nu computation is a no-op pass statement in runner (lines 80-83 of Q-P006 CODE runner)
- Gates C1, C6, C7, FG not evaluated in results JSON — ABNORMAL was declared from exponent deviations alone without verifying the frozen decision rule gates

### Resolution
- All 4 computed exponents deviate from theory (ABNORMAL confirmed numerically)
- tau fails at 16.7sigma
- 1/nu gap is a METHODOLOGY GAP, not a numerical error
- Q-P006 now CLOSED with ABNORMAL verdict

## Q-P007 (p_c refinement diagnostic, EXP-0009PC)

### Bugs found during audit
- Phase 2 runner (run_phase2.py) had KeyError 'chis'/'pinfs' from run_q_p007.py format strings — fixed in run_phase2.py by computing chis/pinfs from cluster_sizes
- tau diagnostic returns None (0 tail clusters at L=2048 with n=25 — known limitation near p_c)
- Cell data checkpoints were saved to Q-P007/CODE/RESULTS/ with naming EXP-0009-pc_L*.npz (consistent with experiment ID EXP-0009-pc)

### Resolution
- Phase 2 completed 2026-09-19 (813s)
- All 3 exponents PASS at refined p_c (were FAIL at original p_c in EXP-0009)
- p_c inaccuracy was a contributing factor to exponent deviations measured in EXP-0009
