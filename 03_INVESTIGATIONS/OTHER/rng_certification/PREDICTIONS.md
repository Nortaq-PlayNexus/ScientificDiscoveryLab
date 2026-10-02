# PREDICTIONS — EXP-0004 (frozen before execution)

## Stream and battery parameters (frozen)

- Master byte stream per (generator, seed): NBYTES = 2^15 bytes (32768) drawn by
  fixed sequential calls, giving 2^18 bits after unpackbits.
- Test grid: TEST_SET (15 families; some yield several p-values per run — see
  EXPERIMENT_PLAN.md) x SEEDS = {42, 7, 123, 2023, 314159, 271828}.
- Generators: G_LAB (engineering rng), G_PCG (raw PCG64), G_MT (MT19937 control).
- alpha = 0.01 per region; KS and binomial/FDR decisions per generator.

## Quantitative predictions

1. (Primary, H0-1) For G_LAB, the combined p-value multiset (all tests x all
   seeds) passes the one-sample KS test against Uniform(0,1) with p_KS > 0.01.
   Expected: PCG64 is well-tested; p_KS should be unremarkable (typ. 0.2-0.9).
2. (Primary, H0-2) For G_LAB, the number of p-values <= 0.01 is inside the exact
   95% central binomial band Bin(alpha=0.01, n=N_cells). With ~120 cells the band
   is approximately [0, 4]; the expected count is 1.2.
3. (Primary, H0-3) The BH-FDR (alpha=0.01) flagged count for G_LAB is within the
   same binomial band.
4. (S1) G_PCG and G_MT pass the same rule (H0-1..3) — i.e. the battery is
   well-calibrated on known-good generators.
5. (S2) Agreement of the independent replication battery (REPLICATION/):
   per-stream p-values from the independent implementation agree with the primary
   battery to < 2% root-mean difference (they are separate implementations of the
   same formulas on the same streams).
6. (Calibration) The median p across seeds for every individual test family lies
   in [0.25, 0.75] (a bare sanity check that no single test is systematically
   extreme; not part of the decision rule).

## What we do NOT predict

- Not "zero small p-values": at alpha=0.01 and ~120 cells, ~1 small p is normal.
- Not a NIST gold-stamp: this is a lightweight, reproducible, engine-local
  battery at lab stream lengths, following NIST formulas where stated.

## Registered outputs to record

- Per (generator, seed, test) p-value matrix + raw statistic names.
- Per-generator: KS p-value, small-p count + binomial band, BH-FDR flags + count.
- Determinism (C1) and label-independence (C2) hashes.
- Decision label per EXPERIMENT_PLAN.md (CERTIFIED / ABNORMAL / INCONCLUSIVE).

## Notes on planning checks (disclosed)

While writing the battery, throwaway sanity snippets (outside the lab; see
FALSIFICATION/planning_checks.md) confirmed: numpy Generator and RandomState
monobit p-values look uniform; the KS code and binomial bands produce the
expected counts on random p-value arrays; GF(2) rank code matches NIST's known
rank-probability asymptotics. None of these touched the lab RNG's registered
results.