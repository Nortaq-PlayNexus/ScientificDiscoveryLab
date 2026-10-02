# CHANGELOG — prime gaps (Q-M002 / HYP-005)

## 2026-09-17 — EXP-0008 preregistration frozen

- Investigation folder `03_INVESTIGATIONS/MATHEMATICS/prime_gaps` created
  following `04_SHARED_ENGINE/experiment_template.md`.
- Full preregistration written in `CONFIG/prereg_EXP-0008.json`: research
  question, HYP-005 (null/alternative), dataset generation (sieve to 10^8),
  4 disjoint blocks, χ2/ KS/ binomial tail statistics, bootstrap (10000,
  rng "exp0008-boot", seed 42), BH-FDR alpha 0.01, controls C1–C7, decision
  rule, output schema, independent-replication requirement.
- Hash of the frozen preregistration recorded in `EXP-0008_experiment.json`.
- Runner `CODE/run_prime_gaps.py` implemented to read parameters from the
  frozen prereg; validation pending.
- Independent implementation `REPLICATION/independent_check.py` planned
  (separate prime source, separate binning, separate stats entry point).
- No results exist yet; no registry row appended. Frozen EXP-0005/0006/0007
  records untouched.
