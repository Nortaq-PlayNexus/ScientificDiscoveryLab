# LITERATURE — Q-I004 (lab RNG certification)

Sources used to define the battery. The implementations in
`04_SHARED_ENGINE/engine/validation/rng_battery.py` follow the referenced
formulas; where a test uses the NIST statistical definitions we follow the
NIST SP 800-22 Rev. 1a equations. This is a **lightweight, in-lab
approximation**, not the official NIST tool (which requires its own harness,
specific stream-state handling and, for some tests, much longer streams). Scope
is declared precisely in REPORT/.

## References

- **Rukhin, A. L., et al.** (2010). *A Statistical Test Suite for Random and
  Pseudorandom Number Generators for Cryptographic Applications*. NIST SP 800-22
  Rev. 1a. https://csrc.nist.gov/publications/detail/sp/800-22/rev-1a/final
  — defines the 15 test families used as the backbone of the battery.
- **O'Neill, M. E.** (2014). *PCG: A Family of Simple Fast Space-Efficient
  Statistically Good Algorithms for Random Number Generation*.
  https://www.pcg-random.org/
  — PCG64 is the algorithm inside numpy `default_rng` / `Generator`.
- **Matsumoto, M. & Nishimura, T.** (1998). *Mersenne Twister: A
  623-dimensionally equidistributed uniform pseudorandom number generator*.
  ACM TOMACS 8(1):3-30.
  — MT19937 = legacy numpy `RandomState`, used here as a known-good control.
- **Knuth, D. E.**, TAOCP vol. 2 *Seminumerical Algorithms*, ch. 3
  ("Random Numbers"). Addison-Wesley.
  — classic tests referenced for gap / coupon-collector / collision families.
- **Marsaglia, G.**, *DIEHARD battery of tests*.
  https://web.archive.org/web/20150811021836/http://stat.fsu.edu/pub/diehard
  — independent third-party battery; cited for background, not executed here.

## Sources searched / not searched

- Searched: the formulas above, numpy generator documentation, NIST definitions.
- NOT searched programmatically in this session: full NIST SP 800-22 source,
  TestU01. The battery is self-contained in the engine and reproducible without
  external downloads (reproducibility priority).

## Honest note

"Passes the battery" here means: under the exact preregistered battery, stream
lengths, seeds, and alpha, the p-value distribution is uniform and the small-p
count is inside its binomial expectation band. It does NOT mean "certified by
NIST" or "proven random".