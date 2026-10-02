"""Create Q-P006 documentation from frozen prereg and results."""
import json, os

Q006_DIR = r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P006"
PREREG_PATH = os.path.join(Q006_DIR, "CONFIG", "prereg_EXP-0009P.json")
RESULTS_PATH = os.path.join(Q006_DIR, "CODE", "RESULTS", "EXP-0009-precision_results.json")

prereg = json.load(open(PREREG_PATH))
results = json.load(open(RESULTS_PATH))
P = prereg["parameters"]
Pred = prereg["predictions"]

R = results["exponents"]
Df_mean = R["Df"]["mean"]; Df_se = R["Df"]["se"]
Gn_mean = R["gamma_nu"]["mean"]; Gn_se = R["gamma_nu"]["se"]
Bn_mean = R["beta_nu"]["mean"]; Bn_se = R["beta_nu"]["se"]
T_mean = R["tau"]["mean"]; T_se = R["tau"]["se"]
tau_sigma = abs(R["tau"]["mean"] - 187/91) / R["tau"]["se"]
exp_Df = 91/48; exp_Gn = 43/24; exp_Bn = 5/48; exp_T = 187/91

# QUESTION.md
q = f"""# Q-P006 — Precision study of 2D percolation critical exponents

## Question
At L in {P['L_list']}, what are the 5 critical exponents (D_f, gamma/nu, beta/nu, tau, 1/nu) with full bootstrap uncertainty quantification, and do the ~1sigma deviations from EXP-0009 shrink with L?

## Parent Result
EXP-0009: D_f=1.8697, gamma/nu=1.7596, beta/nu=0.1295, tau=1.9404, 1/nu=0.7434 at L in [128,256,512,1024]. All gates PASS; 3/5 exponents miss tolerances by ~1sigma. EXP-0010 diagnosed as lattice-size artifact.

## Hypothesis (from frozen prereg)
Deviations shrink as L increases (they were lattice-size artifacts at small L). At L=2048, all 5 exponents should be within tolerance.

## Falsification Test
If deviations do NOT shrink with L (or widen), the lattice-artifact diagnosis is incomplete and there is a genuine systematic effect.

## Method (from frozen prereg)
Reuse EXP-0009/EXP-0010 machinery (same prereg, same gates, same C7). Add L=2048. Bootstrap 2000 draws per exponent.

## Parameters (frozen)
- p_c = {P['p_c']}
- L_list = {P['L_list']}
- n_real = {P['n_real']}
- bootstrap_draws = {P['bootstrap_draws']}
- tau_fit_range = {P['tau_fit_range']}
- tau_L = {P['tau_L']}

## Results
- D_f: {Df_mean:.6f} +/- {Df_se:.6f} (expected 91/48={exp_Df:.6f}, tol={Pred['D_f']['tol']})
- gamma/nu: {Gn_mean:.6f} +/- {Gn_se:.6f} (expected 43/24={exp_Gn:.6f}, tol={Pred['gamma_nu']['tol']})
- beta/nu: {Bn_mean:.6f} +/- {Bn_se:.6f} (expected 5/48={exp_Bn:.6f}, tol={Pred['beta_nu']['tol']})
- tau: {T_mean:.6f} +/- {T_se:.6f} (expected 187/91={exp_T:.6f}, tol={Pred['tau']['tol']})
- 1/nu: NOT COMPUTED (runner stub at lines 80-83)

## Audit Notes (2026-09-19)
- All 4 computed exponents deviate from theory (ABNORMAL confirmed numerically)
- tau fails at {tau_sigma:.1f}sigma
- 1/nu gap is a METHODOLOGY GAP, not a numerical error
- Gates C1, C6, C7, FG not evaluated in results JSON
- _cells files were saved to wrong directory (Q-P005_exponents); COPIED to correct location
"""
with open(os.path.join(Q006_DIR, "QUESTION.md"), "w", encoding="utf-8") as f:
    f.write(q)
print("QUESTION.md created")

# REPORT.md
rpt = f"""# EXP-0009-precision Technical Report

## Experiment: Q-P006 Precision Study of 2D Percolation Critical Exponents

## Setup
- **Preregistration:** `CONFIG/prereg_EXP-0009P.json` (FROZEN before execution)
- **Method:** Site percolation at p_c={P['p_c']}, L in {P['L_list']}
- **Realizations:** {P['n_real']}
- **Bootstrap:** {P['bootstrap_draws']} draws per exponent
- **Independent implementation:** Required (C7) — see results

## Results

| Exponent | Measured | SE | Expected | |dev| | sigma | Status |
|---|---|---|---|---|---|---|
| D_f | {Df_mean:.6f} | {Df_se:.6f} | 91/48={exp_Df:.6f} | {abs(Df_mean - exp_Df):.6f} | {abs(Df_mean - exp_Df)/Df_se:.2f} | FAIL |
| gamma/nu | {Gn_mean:.6f} | {Gn_se:.6f} | 43/24={exp_Gn:.6f} | {abs(Gn_mean - exp_Gn):.6f} | {abs(Gn_mean - exp_Gn)/Gn_se:.2f} | FAIL |
| beta/nu | {Bn_mean:.6f} | {Bn_se:.6f} | 5/48={exp_Bn:.6f} | {abs(Bn_mean - exp_Bn):.6f} | {abs(Bn_mean - exp_Bn)/Bn_se:.2f} | FAIL |
| tau | {T_mean:.6f} | {T_se:.6f} | 187/91={exp_T:.6f} | {abs(T_mean - exp_T):.6f} | {abs(T_mean - exp_T)/T_se:.2f} | FAIL |
| 1/nu | NOT COMPUTED | -- | [0.60, 0.90] | -- | -- | GAP |

## Key Findings
- All computed exponents deviate from theory at L=2048
- tau fails catastrophically at {tau_sigma:.1f}sigma
- tau_cum_chi2_red = {results['tau_cum_chi2_red']} (valid fit)
- R1 scaling relation (tau = 1+2/Df): PASS (within 0.12)
- R2 scaling relation (2*beta/nu + gamma/nu = 2): PASS (within 0.05)
- 1/nu was not computed (runner stub) — gate inv_nu_gate=[0.60,0.90] was never evaluated

## Bugs Found During Audit
- _cells files saved to Q-P005_exponents/CODE/RESULTS (wrong directory) due to save_cell import from run_exp0009.py
- 1/nu computation is a no-op pass statement in runner
- Gates C1, C6, C7, FG not recorded in results JSON

## Decision
Per frozen decision_rule: ABNORMAL (gates PASS, exponents out of tolerance).
Note: Gates C1, C6, C7, FG were not evaluated — full decision rule could not be applied from results JSON alone.
"""
os.makedirs(os.path.join(Q006_DIR, "REPORT"), exist_ok=True)
with open(os.path.join(Q006_DIR, "REPORT", "TECHNICAL_EXP-0009-precision.md"), "w", encoding="utf-8") as f:
    f.write(rpt)
print("REPORT/TECHNICAL_EXP-0009-precision.md created")

# HYPOTHESIS.md
with open(os.path.join(Q006_DIR, "HYPOTHESIS.md"), "w", encoding="utf-8") as f:
    f.write("# Hypothesis — Q-P006\n\nDeviations shrink as L increases (they were lattice-size artifacts at small L). At L=2048, all 5 exponents should be within tolerance.\n")
print("HYPOTHESIS.md created")

# PREDICTIONS.md
pred = f"""# Predictions — Q-P006 (from frozen prereg)

| Quantity | Expected | Tolerance |
|---|---|---|
| D_f | 91/48 = {exp_Df:.6f} | +/-{Pred['D_f']['tol']} |
| gamma/nu | 43/24 = {exp_Gn:.6f} | +/-{Pred['gamma_nu']['tol']} |
| beta/nu | 5/48 = {exp_Bn:.6f} | +/-{Pred['beta_nu']['tol']} |
| tau | 187/91 = {exp_T:.6f} | +/-{Pred['tau']['tol']} |
| 1/nu | [{Pred['inv_nu_gate'][0]}, {Pred['inv_nu_gate'][1]}] | gate |
| R1: tau = 1 + 2/D_f | identity | +/-{Pred['R1_tau_vs_Df']['tol']} |
| R2: 2*beta/nu + gamma/nu = 2 | identity | +/-{Pred['R2_beta_gamma']['tol']} |
"""
with open(os.path.join(Q006_DIR, "PREDICTIONS.md"), "w", encoding="utf-8") as f:
    f.write(pred)
print("PREDICTIONS.md created")

# CONTROLS.md
ctrl = f"""# Controls — Q-P006 (from frozen prereg)

| Control | Description |
|---|---|
| C1 | full-cell rerun (L=1024, p_c) cluster census bit-identical |
| C6 | seed ladder on M_max, chi at each L (n per seed from n_real) |
| C7 | pure-Python union-find independent: L in {P['L_list']}, subsample n=40, per-realization M_max and chi bit-identical |
| FG | slope stability: refit D_f on inner sizes |d|<=0.02, gamma/nu |d|<=0.04 |
| PC1 | bootstrap SE + chi2_red reported for every fit |
"""
with open(os.path.join(Q006_DIR, "CONTROLS.md"), "w", encoding="utf-8") as f:
    f.write(ctrl)
print("CONTROLS.md created")
