"""EXP-0006 runner — fine-grid width-route follow-up.

Patches EXP-0005-specific constants in run_percolation.py before
calling main(), so all paths and labels use EXP-0006 instead.

Key differences from a straight EXP-0005 run:
- PREREG_PATH -> prereg_EXP-0006.json (finer p-grid at L=256/512,
  robust estimator sigma0=0.10)
- EXP_ID -> EXP-0006 (results file EXP-0006_results.json,
  experiment file EXP-0006_experiment.json)

Frozen EXP-0005 artifacts are untouched. Deterministic: seed=42.

Run with: python CODE/run_percolation_exp0006.py
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVESTIGATION = os.path.join(ROOT, "03_INVESTIGATIONS", "PHYSICS", "percolation")
CONFIG_DIR = os.path.join(INVESTIGATION, "CONFIG")
CODE_DIR = os.path.join(INVESTIGATION, "CODE")
PREREG_PATH = os.path.join(CONFIG_DIR, "prereg_EXP-0006.json")

sys.path.insert(0, CODE_DIR)
import run_percolation as rc

rc.PREREG_PATH = PREREG_PATH
rc.EXP_ID = "EXP-0006"
rc.QUESTION_ID = "Q-P004"
rc.HYPOTHESIS_ID = "HYP-004"
rc.main()
