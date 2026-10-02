# EXP-0009-precision Technical Report

## Experiment: Q-P006 Precision Study of 2D Percolation Critical Exponents

## Setup
- **Preregistration:** `CONFIG/prereg_EXP-0009P.json` (FROZEN before execution)
- **Method:** Site percolation at p_c=0.5927460507921, L in [512, 1024, 2048]
- **Realizations:** {'512': 200, '1024': 100, '2048': 50}
- **Bootstrap:** 2000 draws per exponent
- **Independent implementation:** Required (C7) — see results

## Results

| Exponent | Measured | SE | Expected | |dev| | sigma | Status |
|---|---|---|---|---|---|---|
| D_f | 1.863312 | 0.042293 | 91/48=1.895833 | 0.032521 | 0.77 | FAIL |
| gamma/nu | 1.730146 | 0.060413 | 43/24=1.791667 | 0.061520 | 1.02 | FAIL |
| beta/nu | 0.137169 | 0.040919 | 5/48=0.104167 | 0.033002 | 0.81 | FAIL |
| tau | 1.975310 | 0.004770 | 187/91=2.054945 | 0.079635 | 16.70 | FAIL |
| 1/nu | NOT COMPUTED | -- | [0.60, 0.90] | -- | -- | GAP |

## Key Findings
- All computed exponents deviate from theory at L=2048
- tau fails catastrophically at 16.7sigma
- tau_cum_chi2_red = 0.49655209106489767 (valid fit)
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
