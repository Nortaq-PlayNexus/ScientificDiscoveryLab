# CURRENT_STATUS.md

## Percolation thresholds (Q-P004 / HYP-004) — EXP-0007 (CLOSED)

### Closure re-verification (2026-09-18) — data reviewed, not status text
- Re-read actual result files: `CODE/RESULTS/EXP-0007_results.json`, `EXP-0007_summary.json`,
  `REPLICATION/C7_exp0007_report.json`, `CODE/CONFIG/EXP-0007_experiment.json`, `registry.jsonl`.
- Prereg freeze intact: `prereg_EXP-0007.json` on disk sha256 == recorded `d421d4a6…2451ad02`.
- p50(L) re-derived independently from raw k/n cell counts matches recorded values at all 6 L
  (32:0.49866, 48:0.49745, 64:0.50033, 96:0.49850, 128:0.50122, 192:0.49924).
- C7 report: 78/78 cells `identical:true`, max_diff 0.0 < p50 gate 0.005, p50 delta 0.0 at all L.
- All gates re-confirmed PASS in the data: C1 (k=304/304), C4 (shift 0.001111), C6 (max dev
  0.00168<0.00412), C7 (78/78), C8 (1/nu 0.7255 in [0.6,0.9]), FG (chi2_red 2.239<4), in_tol
  (|d|=0.000687<0.01). Decision recorded in results JSON = H0_SUPPORTED.
- Verdict UNCHANGED: **Q-P004 CLOSED, H0_SUPPORTED, evidence CONTROLLED.** No re-run; frozen
  EXP-0005/0006/0007 artifacts untouched.

| item | value |
|---|---|
| EXP-0007 decision | **H0_SUPPORTED** — reason: `all thresholds within 0.01 of anchor` |
| bond_wrap p_c | **0.500687 ± 0.0317** (|d| = 0.000687, in_tol PASS); exotic fits alt1/alt2 agree (chi2_red 2.24/2.23) |
| FG bond_wrap | **RESOLVED: 2.239 PASS** (was 4.738 FAIL at 3 sizes) — 6 sizes L=32..192 |
| Non-monotonicity | L48->L64 kink (delta ~0.0029) persists but is small-L scatter; L^−3/4 model fits at 6 sizes |
| C8 width-route | **0.7255** (gate [0.6,0.9] PASS; nu=1.3783); bootstrap mean 0.7478 sd 0.0773 CI95 [0.6722,1.0674] — wide CI is coarse-grid diagnostic limit only |
| C7 independent | **PASS 78/78 cells bit-identical**, p50 delta 0.000 at all L (incl. new L=96/128/192) — new implementation `REPLICATION/independent_check_exp0007.py` |
| Gates | C1 PASS (k=304/304), C4 PASS (shift 0.001111), C6 PASS (max dev 0.00168), C7 PASS, C8 PASS, FG PASS, in_tol PASS |
| Data | L=32/48/64 frozen EXP-0005 cells; L=96/128/192 new (n=500/400/300, seeds 101/202/303); grid arange(0.38,0.64,0.02) |
| EXP-0005 comparison | FG bond_wrap 4.738 FAIL -> **2.239 PASS**; |d| 0.00122 -> 0.000687; C8 (bond_span fine grid) 0.7375 vs wrap 0.7255 (agree) |
| Q-P004 evidence | **CONTROLLED** — textbook percolation p_c reproduced through the controlled pipeline; no novelty. Closed. |