# QUESTION — Does the lab RNG pass a standard statistical battery? (Q-I004)

- QUESTION_ID: Q-I004
- FIELD: computational_science / random-number infrastructure
- HYPOTHESIS_ID: HYP-003

## Question

The lab derives every random stream from `engine.utilities.core.rng(label, seed)`,
a numpy Generator seeded with `int(sha256(f"{label}:{seed}")[:16], 16)`
(PCG64 algorithm). Does this generator pass standard empirical statistical PRNG
test batteries (NIST SP 800-22 footprint; classic Knuth/Marsaglia tests) at lab
scales — i.e. can the lab safely attribute anomalies to science rather than to
the RNG?

## Why this question matters

- Every experiment (EXP-0001..0003 and all future ones) draws from this stream.
  A silent RNG defect would poison every p-value, every surrogate, and every
  bootstrap CI the lab has produced or will produce.
- The lab's determinism convention already proved RNG reproducibility across
  processes (EXP-0001). Statistical *quality* is a separate property that has
  never been tested.
- It is the cheapest high-value insurance item in the candidate shortlist
  (COMPUTATIONAL REQUIREMENTS: Low; COST: CPU-minutes; Q-I004 marked HIGH
  feasibility).

## What scientists already know

- numpy's `Generator` uses PCG64 (O'Neill 2014); PCG64 is extensively tested and
  is the recommended numpy generator. Mersenne Twister (legacy `RandomState`,
  MT19937, Matsumoto & Nishimura 1998) is the best-known older generator.
- NIST SP 800-22 (Rukhin et al. 2010) defines a standard battery of 15 test
  families for "random/non-random" classification of bit streams.
- DIEHARD (Marsaglia) and TestU01 (L'Ecuyer) are broader third-party suites.
- Passing batteries is a property of the *algorithm + seeding + stream*, not an
  absolute; batteries are statistical (expect ~α false rejections per test).

## What remains unknown

- Whether THIS generator, seeded via the lab's label+seed sha256 derivation, at
  the stream lengths the lab actually uses, passes a lightweight reproducible
  battery implemented inside the lab's own engine.
- Whether the battery itself behaves (does not over-reject or under-reject) when
  applied to known-good generators — a control that makes a "certified" verdict
  meaningful.

## Current theories / null hypothesis (H0)

The lab RNG passes the battery: its p-value distribution is consistent with
Uniform(0,1), individual rejections occur at the expected rate, and it behaves
indistinguishably from the raw numpy PCG64 generator and from a MT19937 control.
(Certification = calibration, NOT a discovery claim.)

## Alternative hypothesis (H1)

A systematic, reproducible failure mode that the known-good controls do not show
(genuine RNG defect -> red flag for the whole lab), OR a battery malfunction
(both controls fail too -> battery invalid, verdict INCONCLUSIVE).

## Falsification test

- Longer streams and more seeds than any single experiment needs.
- Cross-generator comparison (LAB vs raw PCG64 vs MT19937) so that battery
  artefacts are distinguishable from RNG defects.
- Re-implemented independent battery in REPLICATION/ that must agree per-stream.

## Expected difficulty

Low — the generator is a known-good PCG64; the work is honest, controlled,
reproducible execution of the battery.

## Likely computational cost

CPU-minutes. Streams <= 2^18 bits; ~16 test families; 6 seeds; 3 generators.

## Known pitfalls

- Under-powered or badly-chosen thresholds (use exact binomial/KS bands, not ad
  hoc "must pass 100%").
- Double-rejection misinterpretation: with ~100 p-values at alpha=0.01, a few
  sub-0.01 values are EXPECTED. Judge by binomial band + KS uniformity, not by
  "any p < 0.05 fails".
- Harvesting artefacts (testing the same stream with 1000 tweaks until it passes).
- Claiming "certified by NIST" when we run a lightweight in-lab approximation:
  we document exactly what the battery is and is not.

## Relevant papers

- NIST SP 800-22 Rev. 1a, "A Statistical Test Suite for Random and Pseudorandom
  Number Generators" (Rukhin et al., 2010).
- O'Neill, "PCG: A Family of Simple Fast Space-Efficient Statistically Good
  Algorithms for Random Number Generation" (2014).
- Matsumoto & Nishimura, "Mersenne Twister: A 623-dimensionally equidistributed
  uniform pseudorandom number generator" (1998).
- Knuth, TAOCP vol. 2 (Seminumerical Algorithms) ch. 3; Marsaglia, DIEHARD suite.

## Why an AI lab could help

- It can implement the whole battery deterministically in the engine, run it on
  fixed seeds, cross-check against known-good generators, and leave an append-only
  certificate record. Cheap, reusable, and self-falsifying.

## What would count as a real result

- A reproducible calibration certificate: p-value distributions per generator,
  exact binomial expectation bands, BH-FDR flags, KS uniformity, control-generator
  agreement, and independent re-implementation agreement. Evidence state:
  CONTROLLED (calibration, not discovery).