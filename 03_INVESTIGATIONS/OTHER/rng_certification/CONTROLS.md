# CONTROLS — EXP-0004 (lab RNG certification)

All controls are run in CODE/run_rng_cert.py or REPLICATION/. Any surprise
triggers the kill-the-hypothesis battery.

| # | Control | Implementation | Rule |
|---|---|---|---|
| C1 | Determinism across processes | generate the G_LAB master stream for seed 42 in a fresh subprocess; compare bytes | sha256 of the stream identical (bit-for-bit) |
| C2 | Label independence | G_LAB streams from two distinct labels, same seed, differ | sha256 of the streams differ |
| C3 | Control-generator calibration | run the battery on G_PCG (raw PCG64) and G_MT (MT19937) | both pass H0-1..3 with the same rule (if they do not, the battery is broken -> INCONCLUSIVE) |
| C4 | KS uniformity | one-sample KS of the p-value multiset vs Uniform(0,1) | p > 0.01 (per generator) |
| C5 | Expected rejection rate | count of p <= 0.01 vs exact 95% binomial band at rate 0.01 | inside [lo, hi] (per generator) |
| C6 | FDR supervision | BH-FDR flagged count (alpha=0.01) vs same binomial band | inside [lo, hi] (per generator) |
| C7 | Independent implementation | REPLICATION/independent_check.py re-implements the battery from the documented formulas | per-stream p-values agree with primary battery within stated tolerance |
| C8 | Length stability | re-run the battery on a 4x longer stream (2^20 bits) for seed 42, G_LAB | decision unchanged (spot check) |

## Definitive-falsifier (only if a deviation survives C1-C7)

- Is a flagged test specific to one seed or one stream slice? -> re-check with
  C8 length and additional slices; a seed-locked failure is different from a
  systematic one.
- Is it the battery? -> if G_PCG or G_MT also fails the same test, the test is
  over-rejecting; classify as a battery defect and fix it, NOT the RNG.
- Is it the label derivation? -> compare G_LAB vs G_PCG on identical seeds and
  stream positions (they differ only in seeding).
- Persisting LAB-only failure -> label H1 (genuine RNG defect), do NOT interpret,
  escalate (report only, red flag for the whole lab).