# CHANGELOG.md

Investigation: Lab RNG statistical certification (Q-I004 / HYP-003 / EXP-0004)

## 2026-09-17

- Scaffolded the investigation (16 template paths + experiment.json).
- Wrote protocol docs: README, QUESTION, LITERATURE, HYPOTHESIS (HYP-003),
  PREDICTIONS, CONTROLS (C1-C8), EXPERIMENT_PLAN, FALSIFICATION/planning_checks.
- Added `04_SHARED_ENGINE/engine/validation/rng_battery.py` (battery + stream
  conventions) and structural infra checks (suite now 14/14).
- Preregistration frozen to `CONFIG/prereg_EXP-0004.json` before the first run.
- Run 1 -> INCONCLUSIVE. All three generators failed identically (KS ~0.008-0.016,
  ~20 rejections each) — the designed S2 signature (battery defect, not RNG).
  Diagnosed and fixed:
  1. T10 cumulative sums: NIST 2.11 formula is p = 1 - sum1 + sum2; the second
     sum was accumulated with the wrong sign, collapsing every cusum p to ~0.
  2. T04 longest run of ones: (a) the published category-probability vector was
     mis-transcribed (it did not match the exact per-block distribution); replaced
     with exact probabilities from the run-limited recurrence
     A(m,l) = sum_j A(m-j,l), brute-force-verified on small m; (b) np.digitize
     with edges (0,4,5,6,7,8,9,inf) mis-bucketed values equal to an edge;
     corrected edges to (-inf,5,6,7,8,9,10,inf).
  3. Windows-only numpy uint8 sum overflow in monobit (and in the independent
     implementation's runs test).
  No stream length, seed, test family, or decision threshold was changed.
- Run 2 -> CERTIFIED (see REPORT/TECHNICAL_SUMMARY.md). G_LAB KS p=0.79,
  small-p 1 vs expected 1.44 (95% band [0,4]), 0 FDR flags; G_PCG KS p=0.033 and
  G_MT KS p=0.65 also pass -> battery well-calibrated, LAB pass meaningful.
  C1 determinism and C2 label independence pass; C8 length stability passes.
- C7 independent re-implementation (`REPLICATION/independent_check.py`):
  30/30 per-stream comparisons agree (max |log10 diff| < 1e-4 across the
  independently recomputed tests) and the decision is unchanged after
  substitution.
- Wrote REPORT/TECHNICAL_SUMMARY.md, REPORT/PLAIN_ENGLISH_SUMMARY.md and
  FIGURES/EXP-0004_pvalue_distribution.png.
- Registry rows appended to CONFIG/registry.jsonl (append-only; row 1 =
  INCONCLUSIVE pre-fix, row 2 = CERTIFIED authoritative).