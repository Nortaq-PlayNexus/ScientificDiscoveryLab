# CHANGELOG — vortex_density (EXP-0003)

Machine-readable log: `CONFIG/changelog.jsonl` (append-only).

## 2026-09-17
- Created the investigation, froze `CONFIG/prereg_EXP-0003.json`.
- First execution (naive contour detector for C2) flagged a detector defect:
  crossing/winding ratio ~2.5 because cells were counted when both zero-contours
  crossed a cell even if the segments did not intersect. Replaced with the certified
  `crossing_density` (segment-intersection test); the naive version is retained as
  `crossing_density_naive` for documentation. Re-ran; primary results (detector D1)
  unchanged.
- Independent replication (`REPLICATION/independent_check.py`) initially predicted
  the density with an FFT-moment estimator, which is biased (spectral leakage) for
  the off-grid plane-wave field (ratio ~0.89 at k0=pi/8). Replaced with the correct
  mode-weighted predictor; the biased value is retained in `independent_check.json`.
- Final: decision H0_SUPPORTED; evidence CONTROLLED.
