# EXPERIMENT_PLAN — EXP-0004 (lab RNG statistical certification)

Preregistered protocol. Frozen before execution; any later change is appended to
CONFIG/changelog.jsonl via engine.hypothesis_testing.prereg.log_change.

## Model

Random streams are drawn from labelled generators. The primary object is

    G_lab = engine.utilities.core.rng(label, seed)
    bytes = G_lab.integers(0, 256, NBYTES, dtype=np.uint8)   # sequential draws

plus a float stream `G_lab.random(NF)` and a 32-bit-word stream
`G_lab.integers(0, 2**32, NW, dtype=np.uint32)` drawn from the same generator for
the tests that need those forms. Other generators use the identical call
sequence through an adapter, differing only in how they are seeded:

- G_PCG = np.random.default_rng(seed)          (raw PCG64, no label derivation)
- G_MT  = np.random.RandomState(seed)          (MT19937 control)

NBYTES = 2^15 (= 2^18 bits), NF = 2^15 floats, NW = 2^13 uint32 words.

## Test battery (engine/validation/rng_battery.py)

Each test consumes a fixed disjoint slice of the bit/float/word streams.
Formulas follow NIST SP 800-22 Rev. 1a where named; deviations are explicit.

| ID | Test | Family (NIST) | Form | p-values |
|---|---|---|---|---|
| T01 | Monobit frequency | 2.1 Monobit | bits | 1 |
| T02 | Block frequency (M=128) | 2.2 BlockFreq | bits | 1 |
| T03 | Runs | 2.3 Runs | bits | 1 |
| T04 | Longest run of ones (M=128) | 2.4 LongestRun | bits | 1 |
| T05 | Binary matrix rank (32x32) | 2.5 Rank | bits | 1 |
| T06 | DFT spectral | 2.9 DFTtest | bits | 1 |
| T07 | Non-overlapping template (m=9) | 2.7 (lightweight) | bits | 1 |
| T08 | Serial (m=3) | 2.13 Serial | bits | 2 |
| T09 | Approximate entropy (m=3) | 2.12 ApEn | bits | 1 |
| T10 | Cumulative sums (fw/bw) | 2.11 Cusum | bits | 2 |
| T11 | Byte chi-square (256 bins) | classic | bytes | 1 |
| T12 | Float chi-square (32 bins) | classic | floats | 1 |
| T13 | Word-bucket chi-square (256 by top byte) | classic | u32 words | 1 |
| T14 | Gap test (base-10 digits) | Knuth | floats->digits | 1 |
| T15 | Bit autocorrelation (lags 1..8) | classic | bits | 8 |

Roughly 23 p-values per (generator, seed); over 6 seeds = ~138 cells per
generator (exact count recorded at runtime and frozen in the preregistration).

## Steps

1. Freeze preregistration to CONFIG/prereg_EXP-0004.json.
2. Generate master streams for G_LAB/G_PCG/G_MT x SEEDS; run the battery.
3. C1 determinism (fresh subprocess), C2 label independence.
4. C3 controls (same battery on G_PCG and G_MT).
5. Aggregate per-generator: KS p, small-p count + binomial 95% band, BH-FDR flags.
6. Decision per the frozen rule; write RESULTS/EXP-0004_results.json and
   CONFIG/EXP-0004_experiment.json; append a registry row.
7. C7 REPLICATION/independent_check.py (independent re-implementation).
8. C8 length stability spot check (2^20 bits, seed 42, G_LAB).
9. REPORT/TECHNICAL_SUMMARY.md and REPORT/PLAIN_ENGLISH_SUMMARY.md + figure.

## Definition of the aggregate statistics

- p-multiset M_G = all p-values from battery(G) across all seeds.
- KS: `scipy.stats.kstest(M_G, 'uniform')` -> p_KS.
- binomial band: `[binom.ppf(0.025, N, 0.01), binom.ppf(0.975, N, 0.01)]` for the
  count of M_G values <= 0.01 (N = |M_G|; expected count = N*0.01).
- FDR: `engine.statistics.testers.bh_fdr(M_G, alpha=0.01)` -> flag count.

## Decision rules (frozen)

- **CERTIFIED** (H0 supported) for G_LAB iff all of: p_KS > 0.01; small-p count
  in [lo, hi]; BH-FDR flag count in [lo, hi]; AND the same rule passes for at
  least one control generator (G_PCG or G_MT) - proving the battery itself is
  not over-rejecting.
- **ABNORMAL, LAB-SPECIFIC (H1)** iff G_LAB fails the rule while at least one
  control passes BOTH the battery and this rule: genuine RNG red flag.
- **INCONCLUSIVE** iff G_LAB fails AND no control introspects cleanly either
  (battery malfunction suspected). Also INCONCLUSIVE if C1/C2 fail.
- **CONTROLS (S2) - report-only**: if all three generators fail consistently,
  the battery over-rejects; the certificate is INCONCLUSIVE and the battery is
  fixed rather than the RNG.

## Evidence-state intent

If CERTIFIED: evidence state CONTROLLED (calibration certificate; reproduction of
"PCG64 family passes standard statistical tests"; independent re-implementation
in REPLICATION raises to REPLICATED if it agrees). Not a novelty claim.