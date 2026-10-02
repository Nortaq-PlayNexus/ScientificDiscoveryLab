# CONTROLS — EXP-0005 (percolation thresholds)

All controls run in CODE/run_percolation.py or REPLICATION/. Any surprise triggers
the decision machinery (INCONCLUSIVE if the procedure is broken, per EXPERIMENT_PLAN).

| # | Control | Implementation | Rule |
|---|---|---|---|
| C1 | Determinism | re-run the (bond_span, L=64, p=0.50, seed=42) cell a second time from the same frozen stream | identical span counts (bit-for-bit) |
| C6 | Seed ladder | compute bond_span p50(L=64) for seeds {7,123,2023,314159,271828} (all p-points) and compare with primary seed 42 | p50 within 3x joint SE of the primary-seed p50 |
| C2 | Estimator / BC independence | bond torus wrap (pure-Python strip, toroidal rows) vs bond open spanning (scipy.ndimage) extrapolated p_c | both within 0.01 of 0.5 and within 0.005 of each other |
| C4 | Scale stability | drop L in {64,128} from the bond_span FSS fit and refit | \|delta p_c_ext\| < 0.005 |
| C7 | Independent implementation | REPLICATION/independent_check.py: pure-Python union-find router (no scipy.ndimage) on identical seeded streams; stream layout pinned in CONFIG/STREAM_LAYOUT.md | raw counts identical on the sampled cells and per-L p50 within 0.005 |
| C8 | Free-exponent diagnostic | probit-width log-log slope -> 1/nu (report; coarse grid) | 0.60 <= 1/nu <= 0.90 |
| FG  | Fit-goodness gate | reduced chi^2 of each FSS fit | < 4; else INCONCLUSIVE (procedure suspect) |
| C5 | RNG certification (inherited) | all streams from G_LAB, certified CONTROLLED in EXP-0004 | documented in RESULTS; no new RNG beliefs assumed |

## Definitive-falsifier (only if a deviation survives C2/C4/C7/FG)

- Is only one estimator (wrap vs span) alone off? -> C2 conflict; INCONCLUSIVE until
  the estimator is re-audited, do not interpret the number.
- Is only one system (bond vs site) off? -> run C7 on that system; if C7 agrees with
  primary, the deviation is REAL and consistent -> ABNORMAL, escalate (report only).
- Are bond AND site both high/low together? -> check C6 seed-ladder and C1
  determinism first (RNG/stream pathology), then C7 (implementation pathology).
  INCONCLUSIVE until fixed.
- Persisting, consistent, reproducible deviation -> label ABNORMAL, do NOT interpret.