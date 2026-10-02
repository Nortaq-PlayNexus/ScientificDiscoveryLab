# CONTROLS — EXP-0008

Per RESEARCH_RULES §3, the minimum control set plus the C7 independent
replication required by the user directive and the experiment lifecycle:

- **C1 — Null / random control (matched):** generate n_b i.i.d. Exp(1)
  samples per block via rng("exp0008/c1/null", seed 42) and run the
  identical pipeline (sieve-equivalent binning + chi2 + KS + tail z).
  Expected: NO significant block after BH-FDR (calibration check).
- **C2 — Positive control (matched, one factor changed):** generate
  n_b i.i.d. gaps from Gamma(shape=0.5, scale=2) → mean = 1 but variance = 4
  (overdispersed relative to Exp(1)). Run the identical pipeline.
  Expected: the pipeline MUST flag a significant deviation after BH-FDR
  (proves the test has power; if it fails to detect this, the gates are
  invalid).
- **C3 — Seed variation:** run the primary bootstrap CI ladder over
  seeds {7, 123, 2023, 314159, 271828}; the H0/H1 verdict per block and
  overall must be identical across all five seeds.
- **C4 — Resolution variation:** recompute chi2 with J ∈ {8, 10, 12}
  exponential-quantile bins; the H0/H1 verdict per block must be identical
  across J.
- **C5 — Method variation:** per block, chi-square GOF (primary) and
  Kolmogorov–Smirnov vs fully-specified Exp(1) must give the same H0/H1
  verdict after BH-FDR at alpha = 0.01.
- **C6 — Residue-class conditioning:** split each block's gaps by lower
  prime mod 12 (only residues actually occurring for p >= 10^4: {1,5,7,11});
  within each block, require (a) the conditioned sub-blocks do not produce
  significant deviations after BH-FDR, AND (b) if any PRIMARY gate rejects,
  the rejection must still be observed in ≥ 2 disjoint ranges after
  conditioning (falsification robustness).
- **C7 — Independent implementation:** `REPLICATION/independent_check.py`
  uses a different prime source (sympy.primerange), a different binning
  scheme (equal-width bins instead of exponential-quantile), and a
  different statistical entry point (scipy.stats.chisquare + kstest with
  its own RNG label). Requirement: the H0/H1 verdict per block matches the
  primary pipeline AND the chi2/KS vectors match within recorded tolerance.
