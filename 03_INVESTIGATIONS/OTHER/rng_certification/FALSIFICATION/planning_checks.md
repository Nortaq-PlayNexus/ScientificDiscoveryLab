# FALSIFICATION / planning checks — EXP-0004 (disclosed, pre-execution)

Planning-time sanity checks that informed the design. These were run as
throwaway snippets before registration; none of them are the registered result
and none tuned the decision threshold after seeing the real battery's output.

## Disclosed checks

1. **KS code sanity**: feeding 10,000 `np.random.default_rng(0).random` values to
   the same kstest('uniform') used here returns a large p (no implementation bug
   apparent). Feeding a folded non-uniform array (e.g. beta(0.5,0.5)) returns a
   tiny p (the test has power).
2. **Binomial band sanity**: with N=138, alpha=0.01, `binom.ppf` gives [0, 4];
   the expected count 1.38 sits inside comfortably. A 5% band check on the same
   formula reproduces textbook values.
3. **Monobit sanity**: a 2^18-bit stream from numpy Generator gives a
   well-behaved monobit p (order 0.3-0.9), and a deliberately biased stream
   (bytes AND 0x3) gives p -> ~0. The formulas are directional.
4. **GF(2) rank asymptotics**: the 32x32 rank probabilities used in T05 coincide
   with NIST's published P(rank=32)=0.2888, P(31)=0.5776, P(<=30)=0.1336 when
   computed on the closed form (checked analytically, not by simulation).
5. **Slice independence**: disjoint slices of a Generator stream are uncorrelated
   in the sense that a correlation scan across slice boundaries shows nothing
   anomalous for PCG64 (spot check).

## What these checks do NOT do

- They do not pre-run the registered battery on the registered seeds and choose
  thresholds to make it pass. The rules (KS > 0.01; binomial band; BH-FDR) were
  fixed in EXPERIMENT_PLAN.md/PREDICTIONS.md before the code ran the grid.
- No stream length, no seed, and no test family was added or removed after the
  first full battery run.

## Kill-the-hypothesis battery (if a LAB-only deviation appears)

1. Re-run C8 (4x length) and an additional fresh seed (e.g. 314159 with a
   different label).
2. Swap the label derivation (different label, same seed) -> if the failure is
   reproducible across labels, it is generator-level, not label-level.
3. Compare G_LAB vs G_PCG holding stream positions identical (they differ only
   in the seed value actually used).
4. Escalate only if (1)-(3) all reproduce the deviation.