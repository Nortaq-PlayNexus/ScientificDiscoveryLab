# Q-P007 — p_c refinement diagnostic

## Question
Does refined p_c accuracy explain the exponent deviations measured in EXP-0009-precision (Q-P006)?

## Parent Result
Q-P006 measured D_f=1.863+/-0.042, gamma/nu=1.730+/-0.060, beta/nu=0.137+/-0.041, tau=1.975+/-0.005 at L in [512, 1024, 2048]. tau fails at 16.6 sigma vs Fisher value 187/91=2.055.

## Hypothesis (from frozen prereg)
(H1) p_c is slightly inaccurate, causing systematic bias in all exponents measured in Q-P006. Width-curve crossing at L in [512, 1024, 2048] will yield a p_c that, when used for exponent measurement, brings tau closer to the Fisher value 187/91=2.055.

(H2) Finite-size effects bias tau estimation independently of p_c accuracy.

## Falsification Test
If measurements miss tolerance at BOTH P2 and non-P2 L, it is a genuine finite-size correction.

## Method (from frozen prereg)
1. Measure p_c via width-curve crossing at L in [512, 1024, 2048]
2. Extrapolate p_c to L infinity
3. Compare to Ziff's value p_c = 0.5927460507921
4. Re-measure exponents at refined p_c

## Parameters (frozen)
- width_L_list: [512, 1024, 2048]
- width_grid: {"L512": {"grid": [0.588, 0.597, 0.001], "n_each": 200}, "L1024": {"grid": [0.589, 0.596, 0.0005], "n_each": 140}, "L2048": {"grid": [0.59, 0.595, 0.0005], "n_each": 100}}
- n_real: {'512': 100, '1024': 50, '2048': 25}
- bootstrap_draws: 2000

## Current Status (2026-09-19)
- Phase 1: L=512, L=1024 width curves COMPLETE (preserved from run.log)
  - L=512: p_c=0.592883+/-0.004519
  - L=1024: p_c=0.592673+/-0.003031
- Phase 1: L=2048 width curve COMPLETE (per run.log, 2026-09-19)
  - L=2048: p_c=0.592834+/-0.001828
- Phase 2: Exponent remeasurement at refined p_c — COMPLETE (2026-09-19, 813s)
  - D_f=1.8818 (PASS), gamma/nu=1.7653 (PASS), beta/nu=0.1189 (PASS), tau=N/A (0 tail clusters at L=2048 n=25 — diagnostic limitation)
- p_c(L to infinity) from linear 1/L extrapolation: 0.59272900 (|dev| from Ziff: 0.00001705)
