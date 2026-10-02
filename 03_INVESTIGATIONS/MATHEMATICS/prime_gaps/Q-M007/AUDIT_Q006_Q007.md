# Audit Reports — 2026-09-19

## Q-P006 Audit

- [VERIFIED] L_list [512, 1024, 2048] matches frozen prereg
- [VERIFIED] n_real {512:200, 1024:100, 2048:50} matches frozen prereg
- [VERIFIED] bootstrap_draws 2000 matches frozen prereg
- [VERIFIED] tau calculation: fit_tau_cumulative called with tau_fit_range=[32,4096], tau_L=2048 from frozen prereg
- [VERIFIED] Bootstrap SE correctly computed (resamples with replacement per L)
- [VERIFIED] All 4 exponents deviate from theory: Df 0.77sigma FAIL, gamma/nu 1.02sigma FAIL, beta/nu 0.81sigma FAIL, tau 16.7sigma FAIL
- [VERIFIED] tau_cum_chi2_red = 0.497 (good fit, valid tau estimation)
- [VERIFIED] R1 scaling relation (tau = 1 + 2/Df): PASS within tol 0.12
- [VERIFIED] R2 scaling relation (2*beta/nu + gamma/nu = 2): PASS within tol 0.05

### Issues
- [ISSUE] CRITICAL: _cells files saved to wrong directory (Q-P005_exponents/CODE/RESULTS instead of Q-P006/CODE/RESULTS) — caused by save_cell import from run_exp0009.py with different QDIR. Files COPIED to correct location.
- [ISSUE] 1/nu NOT COMPUTED — runner has pass stub at lines 80-83 (for Lk in [256,512,1024]: pass). inv_nu_gate=[0.60,0.90] from prereg never evaluated.
- [ISSUE] Gates C1, C6, C7, FG NOT EVALUATED — not present in results JSON. Only PC1 partially (SE present, chi2_red only for tau).
- [ISSUE] Cannot determine full ABNORMAL vs H0_SUPPORTED from results JSON alone — frozen decision_rule references unevaluated gates.
- [ISSUE] Width-curve fitting code for 1/nu is entirely absent — no width_grid in Q-P006 prereg (that is in Q-P007 prereg).

### Exponent Details
- Df: mean=1.863312 +- 0.042293, expected=1.895833, |dev|=0.032521, 0.77sigma, tol=0.015, FAIL
- gamma_nu: mean=1.730146 +- 0.060413, expected=1.791667, |dev|=0.061520, 1.02sigma, tol=0.03, FAIL
- beta_nu: mean=0.137169 +- 0.040919, expected=0.104167, |dev|=0.033002, 0.81sigma, tol=0.015, FAIL
- tau: mean=1.975310 +- 0.004770, expected=2.054945, |dev|=0.079635, 16.70sigma, tol=0.05, FAIL

**Recommendation:** ABNORMAL status confirmed numerically. 1/nu gap must be filled before declaring final decision. Gates must be evaluated per frozen decision_rule.

## Q-M007 Audit

- [VERIFIED] Chi2 decomposition: sum(per-bin chi2 contributions) == total chi2 for ALL 4 blocks (diff < 1.0)
- [VERIFIED] Expected normalization: sum(expected) == n_gaps for all blocks
- [VERIFIED] Observed normalization: sum(counts) == n_gaps for all blocks
- [VERIFIED] Per-bin residuals: all 40 cells (10 bins x 4 blocks) match direct recomputation
- [VERIFIED] BH-FDR on primary 20 tail cells: ALL 20 survive after BH-FDR at alpha=0.01 (per EXP-0008)
- [VERIFIED] C6 residue conditioning: deviation survives in 4 disjoint ranges (B1,B2,B3,B4) — PASS (>=2 required)
- [VERIFIED] C7 independent implementation: EXISTS — check C7_exp0008_report.json for agreement details

### Shape Analysis
- pattern: NARROWER than Exp(1)
- under_represented_bins: [1, 10]
- over_represented_bins: [3, 5, 6, 7, 8, 9]
- bin_1_anomaly: 0 observed vs 576022 expected — EMPTY (minimum gap effect, number-theoretic constraint)
- conclusion: Shape deviation, not just tail effect. Both tails lighter, mid-bins over-represented.

### Caveats
- Q-M007 reports RAW residuals — NO BH-FDR applied to the 40-cell Q-M007 grid (10 bins x 4 blocks)
- Primary EXP-0008 BH-FDR was on 20 tail cells only (t={1,2,3,4,5} x 4 blocks)
- Q-M007 extends the analysis to all 10 bins — BH-FDR not reapplied to 40-cell grid
- Bin 1 with 0 observations dominates chi2 — this is the primary driver of the deviation signal
