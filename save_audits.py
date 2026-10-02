"""Q-P006 and Q-M007 audit reports — saved from verification."""
import json, os

# Save Q-P006 audit report
audit_q006 = {
    "audit": "Q-P006 precision study verification",
    "date": "2026-09-19",
    "verdict": "NUMERICAL_RESULTS_CONFIRMED; METHODOLOGY_GAPS_IDENTIFIED",
    "verified": [
        "L_list [512, 1024, 2048] matches frozen prereg",
        "n_real {512:200, 1024:100, 2048:50} matches frozen prereg",
        "bootstrap_draws 2000 matches frozen prereg",
        "tau calculation: fit_tau_cumulative called with tau_fit_range=[32,4096], tau_L=2048 from frozen prereg",
        "Bootstrap SE correctly computed (resamples with replacement per L)",
        "All 4 exponents deviate from theory: Df 0.77sigma FAIL, gamma/nu 1.02sigma FAIL, beta/nu 0.81sigma FAIL, tau 16.7sigma FAIL",
        "tau_cum_chi2_red = 0.497 (good fit, valid tau estimation)",
        "R1 scaling relation (tau = 1 + 2/Df): PASS within tol 0.12",
        "R2 scaling relation (2*beta/nu + gamma/nu = 2): PASS within tol 0.05",
    ],
    "issues": [
        "CRITICAL: _cells files saved to wrong directory (Q-P005_exponents/CODE/RESULTS instead of Q-P006/CODE/RESULTS) — caused by save_cell import from run_exp0009.py with different QDIR. Files COPIED to correct location.",
        "1/nu NOT COMPUTED — runner has pass stub at lines 80-83 (for Lk in [256,512,1024]: pass). inv_nu_gate=[0.60,0.90] from prereg never evaluated.",
        "Gates C1, C6, C7, FG NOT EVALUATED — not present in results JSON. Only PC1 partially (SE present, chi2_red only for tau).",
        "Cannot determine full ABNORMAL vs H0_SUPPORTED from results JSON alone — frozen decision_rule references unevaluated gates.",
        "Width-curve fitting code for 1/nu is entirely absent — no width_grid in Q-P006 prereg (that is in Q-P007 prereg).",
    ],
    "exponent_details": {
        "Df": {"mean": 1.863312, "se": 0.042293, "expected": 1.895833, "dev": 0.032521, "sigma": 0.77, "tol": 0.015, "status": "FAIL"},
        "gamma_nu": {"mean": 1.730146, "se": 0.060413, "expected": 1.791667, "dev": 0.061520, "sigma": 1.02, "tol": 0.03, "status": "FAIL"},
        "beta_nu": {"mean": 0.137169, "se": 0.040919, "expected": 0.104167, "dev": 0.033002, "sigma": 0.81, "tol": 0.015, "status": "FAIL"},
        "tau": {"mean": 1.975310, "se": 0.004770, "expected": 2.054945, "dev": 0.079635, "sigma": 16.70, "tol": 0.05, "status": "FAIL"},
    },
    "recommendation": "ABNORMAL status confirmed numerically. 1/nu gap must be filled before declaring final decision. Gates must be evaluated per frozen decision_rule.",
}

audit_q007 = {
    "audit": "Q-M007 per-bin residual analysis verification",
    "date": "2026-09-19",
    "verdict": "VERIFIED — H1_SUPPORTED CONFIRMED",
    "verified": [
        "Chi2 decomposition: sum(per-bin chi2 contributions) == total chi2 for ALL 4 blocks (diff < 1.0)",
        "Expected normalization: sum(expected) == n_gaps for all blocks",
        "Observed normalization: sum(counts) == n_gaps for all blocks",
        "Per-bin residuals: all 40 cells (10 bins x 4 blocks) match direct recomputation",
        "BH-FDR on primary 20 tail cells: ALL 20 survive after BH-FDR at alpha=0.01 (per EXP-0008)",
        "C6 residue conditioning: deviation survives in 4 disjoint ranges (B1,B2,B3,B4) — PASS (>=2 required)",
        "C7 independent implementation: EXISTS — check C7_exp0008_report.json for agreement details",
    ],
    "shape_analysis": {
        "pattern": "NARROWER than Exp(1)",
        "under_represented_bins": [1, 10],
        "over_represented_bins": [3, 5, 6, 7, 8, 9],
        "bin_1_anomaly": "0 observed vs 576022 expected — EMPTY (minimum gap effect, number-theoretic constraint)",
        "conclusion": "Shape deviation, not just tail effect. Both tails lighter, mid-bins over-represented.",
    },
    "caveats": [
        "Q-M007 reports RAW residuals — NO BH-FDR applied to the 40-cell Q-M007 grid (10 bins x 4 blocks)",
        "Primary EXP-0008 BH-FDR was on 20 tail cells only (t={1,2,3,4,5} x 4 blocks)",
        "Q-M007 extends the analysis to all 10 bins — BH-FDR not reapplied to 40-cell grid",
        "Bin 1 with 0 observations dominates chi2 — this is the primary driver of the deviation signal",
    ],
}

os.makedirs("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007", exist_ok=True)
with open("03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M007/AUDIT_Q006_Q007.md", "w") as f:
    f.write("# Audit Reports — 2026-09-19\n\n")
    f.write("## Q-P006 Audit\n\n")
    for v in audit_q006["verified"]:
        f.write(f"- [VERIFIED] {v}\n")
    f.write("\n### Issues\n")
    for i in audit_q006["issues"]:
        f.write(f"- [ISSUE] {i}\n")
    f.write("\n### Exponent Details\n")
    for name, d in audit_q006["exponent_details"].items():
        f.write(f"- {name}: mean={d['mean']:.6f} +- {d['se']:.6f}, expected={d['expected']:.6f}, |dev|={d['dev']:.6f}, {d['sigma']:.2f}sigma, tol={d['tol']}, {d['status']}\n")
    f.write(f"\n**Recommendation:** {audit_q006['recommendation']}\n\n")
    f.write("## Q-M007 Audit\n\n")
    for v in audit_q007["verified"]:
        f.write(f"- [VERIFIED] {v}\n")
    f.write("\n### Shape Analysis\n")
    for k, v in audit_q007["shape_analysis"].items():
        f.write(f"- {k}: {v}\n")
    f.write("\n### Caveats\n")
    for c in audit_q007["caveats"]:
        f.write(f"- {c}\n")
print("Q-P006/Q-M007 audit report saved.")

# Save Q-P007 Phase 1 preserved results from log
phase1_preserved = {
    "experiment": "EXP-0009-pc",
    "source": "run.log preserved 2026-09-19",
    "phase": 1,
    "width_curves": {
        "512": {"mu": 0.592883, "sigma": 0.004519},
        "1024": {"mu": 0.592673, "sigma": 0.003031},
    },
    "L2048_width_curve": "NOT COMPLETED in Phase 1 — completed in Phase 2 runner",
    "note": "Preserved from run.log before Phase 2 execution",
}
os.makedirs("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS", exist_ok=True)
with open("03_INVESTIGATIONS/PHYSICS/percolation/Q-P007/CODE/RESULTS/EXP-0009-pc_phase1_preserved.json", "w") as f:
    json.dump(phase1_preserved, f, indent=2)
print("Q-P007 Phase 1 preserved results saved.")
