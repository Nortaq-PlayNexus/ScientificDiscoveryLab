# LITERATURE — Q-M002

## Known science

- Gallagher (1976): the spacings between consecutive primes, normalized by
  ln(p), follow an exponential distribution under the random model where
  primes in an interval of length h are Poisson(h/ln x).
- Conrey, Goldston, Keedy (2023-ish): gap distribution is Poisson in the
  unrestricted sense; conditioned on Hardy–Littlewood it becomes the GPY
  heuristic for small gaps.
- Cramér's conjecture and the Poisson model: normalized gaps roughly
  exponential with rate 1; the model is the standard baseline for prime
  gap statistics.
- Numerical compilations: prime gaps up to 10^18 and beyond are tabulated
  (OEIS A001223, A005250); small-gap frequencies match Poisson expectations
  very well in the ranges tested here.

## What remains unknown (for this experiment)

- Whether, on this machine, a straightforward sieve + bootstrap pipeline
  reproduces the model within bootstrap uncertainty at four disjoint ranges
  up to 10^8.
- Whether any observed deviation survives residue-class conditioning
  (p mod 12) and independent replication.

## Sources searched

- Gallagher (1976), "The differences between consecutive primes, II"
  (small gaps).
- Conrey, Goldston, Montgomery, Keedy (2023-ish), "Primes in tuples".
- OEIS A001223 (prime gaps), A005250 (record gaps).
- No programmatic literature search was performed; novelty is never claimed.
