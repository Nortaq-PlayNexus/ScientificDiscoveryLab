"""Create Q-P007 documentation from frozen prereg."""
import json, os

Q007_DIR = r"03_INVESTIGATIONS\PHYSICS\percolation\Q-P007"
PREREG_PATH = os.path.join(Q007_DIR, "CONFIG", "prereg_EXP-0009PC.json")

prereg = json.load(open(PREREG_PATH))
P = prereg["parameters"]

# QUESTION.md
q = f"""# Q-P007 — p_c refinement diagnostic

## Question
Does refined p_c accuracy explain the exponent deviations measured in EXP-0009-precision (Q-P006)?

## Parent Result
Q-P006 measured D_f=1.863+/-0.042, gamma/nu=1.730+/-0.060, beta/nu=0.137+/-0.041, tau=1.975+/-0.005 at L in {P['width_L_list']}. tau fails at 16.6 sigma vs Fisher value 187/91=2.055.

## Hypothesis (from frozen prereg)
(H1) p_c is slightly inaccurate, causing systematic bias in all exponents measured in Q-P006. Width-curve crossing at L in {P['width_L_list']} will yield a p_c that, when used for exponent measurement, brings tau closer to the Fisher value 187/91=2.055.

(H2) Finite-size effects bias tau estimation independently of p_c accuracy.

## Falsification Test
If measurements miss tolerance at BOTH P2 and non-P2 L, it is a genuine finite-size correction.

## Method (from frozen prereg)
1. Measure p_c via width-curve crossing at L in {P['width_L_list']}
2. Extrapolate p_c to L infinity
3. Compare to Ziff's value p_c = {P['p_c']}
4. Re-measure exponents at refined p_c

## Parameters (frozen)
- width_L_list: {P['width_L_list']}
- width_grid: {json.dumps(P['width_grid'])}
- n_real: {P['n_real']}
- bootstrap_draws: {P['bootstrap_draws']}

## Current Status (2026-09-19)
- Phase 1: L=512, L=1024 width curves COMPLETE (preserved from run.log)
  - L=512: p_c=0.592883+/-0.004519
  - L=1024: p_c=0.592673+/-0.003031
- Phase 1: L=2048 width curve IN PROGRESS (Q-P007 Phase 2 runner running)
- Phase 2: Exponent remeasurement at refined p_c — PENDING
- p_c(L to infinity) from 2-point extrapolation: 0.59246300 (|dev| from Ziff: 0.00028305)
"""
os.makedirs(Q007_DIR, exist_ok=True)
with open(os.path.join(Q007_DIR, "QUESTION.md"), "w", encoding="utf-8") as f:
    f.write(q)
print("Q-P007 QUESTION.md created")

# HYPOTHESIS.md
hyp = f"""# Hypothesis — Q-P007 (from frozen prereg)

(H1) p_c is slightly inaccurate, causing systematic bias in all exponents measured in Q-P006. Width-curve crossing at L in {P['width_L_list']} will yield a p_c that, when used for exponent measurement, brings tau closer to the Fisher value 187/91=2.055.

(H2) Finite-size effects bias tau estimation independently of p_c accuracy.
"""
with open(os.path.join(Q007_DIR, "HYPOTHESIS.md"), "w", encoding="utf-8") as f:
    f.write(hyp)
print("Q-P007 HYPOTHESIS.md created")

# CONTROLS.md
ctrl = f"""# Controls — Q-P007 (from frozen prereg)

| Control | Description |
|---|---|
| C1 | width curve at L=1024 reproducible (sha256) |
| C7 | pure-Python union-find independent: L in {P['width_L_list']}, subsample n=30 |
| FG | slope stability of D_f on inner L values |
| PC1 | bootstrap SE + chi2_red reported |
"""
with open(os.path.join(Q007_DIR, "CONTROLS.md"), "w", encoding="utf-8") as f:
    f.write(ctrl)
print("Q-P007 CONTROLS.md created")
