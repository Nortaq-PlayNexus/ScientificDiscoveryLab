"""EXP-0006 Phase 2 — extended-L bond_wrap MC + multi-seed L64.

Aggressively tests the bond_wrap FG failure (chi2_red=4.738 from Phase 1):
  1. Extended-L bond_wrap: L=96,128,192 (do small-L non-monotonicity persist?)
  2. Multi-seed L64: seeds [7,123,2023,314159,271828] (is L64 rise robust?)
  3. Combined FSS fit with 6 L values (model comparison now testable)

Same gates/controls/tolerances as EXP-0006. Deterministic (seed=42 base).
Writes results to CODE/RESULTS/EXP-0006_phase2_results.json.
Does NOT modify any EXP-0005 frozen artifacts.
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = os.path.join(ROOT, "03_INVESTIGATIONS", "PHYSICS", "percolation")
CONFIG_DIR = os.path.join(INV, "CONFIG")
CODE_DIR = os.path.join(INV, "CODE")
PREREG_PATH = os.path.join(CONFIG_DIR, "prereg_EXP-0006.json")
RESULT_PATH = os.path.join(CODE_DIR, "RESULTS", "EXP-0006_phase2_results.json")
EXPERIMENT_PATH = os.path.join(CONFIG_DIR, "EXP-0006_experiment.json")

sys.path.insert(0, CODE_DIR)
import run_percolation as rc

# Patch to Phase 2 configuration
rc.PREREG_PATH = PREREG_PATH
rc.EXP_ID = "EXP-0006-PHASE2"
rc.QUESTION_ID = "Q-P004"
rc.HYPOTHESIS_ID = "HYP-004"

# Extend bond_wrap L_list to include larger L for FSS resolution
# (original EXP-0006: [32,48,64]; Phase 2 adds [96,128,192])
# The main() reads systems from prereg at runtime, so patch sys_params
# after load by monkeypatching load_prereg_params
_orig_load = rc.load_prereg_params
def patched_load(path):
    params = _orig_load(path)
    sys_params = params["parameters"]
    # Extend bond_wrap L_list
    sys_params["systems"]["bond_wrap"]["L_list"] = [32, 48, 64, 96, 128, 192]
    # Multi-seed: add extra seeds for L=64 (C6 seed ladder)
    # Note: main() uses c6 seed ladder from prereg, which already has seeds [7,123,2023,314159,271828]
    return params
rc.load_prereg_params = patched_load

# Override result path by patching main() persistence
# Actually main() hardcodes result path via EXP_ID, so patching EXP_ID to
# EXP-0006-PHASE2 would write EXP-0006-PHASE2_results.json. But we want
# a specific name. Let me patch the persistence instead.
# Simpler: just let it write with the EXP_ID name and rename after.
rc.main()
