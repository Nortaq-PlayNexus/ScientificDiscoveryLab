# Independent audit artifact index — 2026-09-24

This directory contains non-destructive audit evidence. Historical experiment results remain in their original locations.

## Primary reports

- `../FINAL_SCIENTIFIC_AUDIT.md` — executive scientific verdict
- `../CLAIM_REGISTRY.md` — claim-by-claim classifications
- `../REPRODUCTION_MATRIX.md` — reruns and independent checks
- `../BUGS.md` — confirmed defects and repair recommendations
- `../NOVELTY_REVIEW.md` — literature/novelty assessment
- `../NEXT_EXPERIMENTS.md` — prioritized follow-up experiments
- `../PROJECT_INVENTORY.md` — filesystem/provenance inventory
- `../AUDIT_LOG.md` — command and decision log

## Machine-readable evidence

- `independent_static_results.json` — static/provenance checks and raw comparisons
- `independent_optics_results.json` — independent speckle/vortex tests
- `independent_percolation_results.json` — independent percolation sequences
- `percolation_reanalysis_results.json` — EXP-0009/0010/Q-P006/Q-P007/EXP-0007 reanalysis
- `paired_pc_effect_results.json` — paired p_c effect
- `corrected_tau_reanalysis_results.json` and `corrected_tau_raw_L*.npz` — corrected Q-P007-style tau analysis
- `prime_gap_reanalysis_results.json` — dependence and finite-range null diagnostics
- `independent_feigenbaum_reanalysis.py` / `independent_feigenbaum_results.json` — arbitrary-precision root audit
- `rng_calibration_audit.py` / `rng_calibration_results.json` — 80-seed dependence/calibration audit
- `broadband_controls_corrected.py` / `broadband_controls_corrected_results.json` — corrected EXP-0003 controls
- `current_inventory.json` — post-audit inventory
- `SUBAGENT_EXP0003_BROADBAND_20260924/` — parallel sub-agent raw sweep, literature search, logs, and failed first control run

## Important preservation note

The first sub-agent control run failed with exit 255 because its refined-density conversion divided by an extra `factor**2`; the failed output is preserved. The corrected audit-only script multiplies by `factor**2` and is the only interpolation result used in the final classification.
