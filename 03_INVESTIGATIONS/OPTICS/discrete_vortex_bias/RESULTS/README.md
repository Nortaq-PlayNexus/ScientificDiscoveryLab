# EXP-0015 result artifacts

This directory is append-only. Timestamped JSON files are raw result records;
they are not silently overwritten. `latest.json` is only the most recent stage
launch and is not a complete index.

Important records:

- `calibration_42_20260924_133226.json` — discarded detector-calibration failure.
- `calibration_42_20260924_133910.json` — corrected analytical calibration.
- `convergence_42_20260924_134108.json` — primary square convergence matrix.
- `oversample_42_20260924_134458.json` — 2048² square reference/downsample.
- `geometry_controls_20260924_134416.json` — rectangular controls.
- `rectangular_reference_20260924_134643.json` — rectangular red-team reference.
- `tracker_20260924_134940.json` and `close_pair_reference_20260924_135217.json` — close-pair trajectory/reference.
- `detector_size_20260924_134854.json` — contour-radius/separation sweep.
- `exact_zero_20260924_135547.json` — exact-zero versus finite-floor control.
- `independent_replication_20260924_134059.json` and `independent_close_20260924_135514.json` — independent SciPy checks.
- `seed_ladder_20260924_135627.json` and `nulls_42_20260924_140054.json` — random/null records.
- `direct_reference_20260924_135736.json`, `direct_reference_20260924_135839.json` — failed direct-reference controls; `direct_reference_20260924_135940.json` — corrected but still boundary-inconclusive.
- `regimes_fast_20260924_140842.json` — reduced close-pair/high-order regime map.
- `calibration_7_20260924_141216.json`, `calibration_123_20260924_141215.json` — deterministic seed reruns.
- `independent_contour_20260924_141208.json` — independent SciPy contour check.
- `validation_summary.json` — fail-closed assertions for the principal controls.
- `experiment.json` — hash-bound artifact manifest and change-log head.

Interpretation and promotion rules are in the sibling `REPORT/` and dossier
files. The investigation change log records every implementation correction,
aborted no-result run, and exploratory extension.
