# QUESTION — Q-M002

## Question

Do prime gaps deviate from the Conrey–Goldston–Keating / Gallagher Poisson
model predictions in small-to-moderate ranges in a reproducible way?

## Background (from MASTER_CANDIDATES.md M2)

- Gallagher's model predicts that spacings between consecutive primes,
  scaled by the local mean spacing, follow an exponential (Poisson)
  distribution: P(δ > t) = e^{−t} with δ = (p_{i+1} − p_i) / ln(p_i).
- Conditioned on the Hardy–Littlewood conjectures this becomes the GPY
  heuristic; large gaps are well studied.
- What remains unknown: whether clean finite-range signatures match the
  random-Poisson prediction to expected sampling error, and where
  conditioning on residue classes matters.

## Scope

- Domain: mathematics (analytic / computational number theory).
- Feasibility: HIGH — fully self-computed; no external data; CPU-minutes.
- Machine-attackable on this machine: sieve up to 10^8 (< 1 s), statistic
  computation < 1 s, bootstrap ~10 s.
- Known outcome expected: reproduction of the Poisson model (a known
  result), with a fully specified falsification protocol in case a
  reproducible deviation exists.

## Known pitfalls (recorded)

- Nearby gaps are correlated (twin primes, small gaps) — handled by
  block/bootstrap design, not by assuming independence.
- Small-prime residue effects (p = 2, 3, 5, 7, 11) must be excluded from
  the residue-class conditioning test (handled by starting the first block
  at 10^4).
- Range effects: verdicts required to agree across disjoint ranges.
- Treating a significant FDR cell as discovery — forbidden; must survive
  residue-class conditioning + independent replication.
