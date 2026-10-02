# EXP-0004 — Plain-English Summary

**What we did.** The lab draws every random number from one generator:
numpy's PCG64 seeded from `sha256(label:seed)`. Before this check, the lab had
never verified that this generator is statistically *well-behaved* — only that
it is *reproducible*. So we ran a standard set of ~16 statistical tests (the
usual "is this stream random-looking?" checks from NIST SP 800-22 and Knuth's
book) on long streams, for six different seed values, and — critically — on
**three** generators: the lab's, a raw numpy generator, and the classic
Mersenne Twister, which are known to be good. If the battery is fair, those two
known-good generators should pass it. That's what makes "pass" and "fail"
meaningful.

**What we found.** The lab RNG **passes**. Its p-value distribution is uniform,
it flags only the expected number of "suspicious" tests (1, when ~1.4 is
expected at our settings), and the two control generators pass with the same
statistics. The controls also prove the test battery is not unfairly strict.

**The interesting detour.** The first full run failed badly — failed for *all
three* generators at once, in the same way. That cannot mean three different
good algorithms are all broken; it means the test *implementations* had bugs.
The control design caught exactly this. We found and fixed two genuine
implementation bugs (a sign error in one test's formula, and a binning mistake
in another), plus a Windows-specific integer-overflow quirk. After the fixes,
the fixed battery passes all three generators. No numbers were fudged; the only
thing changed was correcting the *test code itself*, and its correctness is now
shown by the controls passing.

**What this means for you.** When the lab reports an anomaly in a future
experiment, the random-number generator is now certified *not* to be the cause.
This is a calibration certificate ("the generator behaves like a good one at
the sizes we use"), **not** a claim about physics, and **not** a claim that
anything is "undetectably random". In particular, it does NOT change any
conclusions in the coherent-optical-ai-sandbox thread (which was already
resolved by its own grids logic).

**Caveats.** This is the lab's own lightweight battery at lab-sized streams —
it is a careful approximation of NIST SP 800-22, not the official NIST
certification, and no battery can prove "absolute randomness". It certifies the
*specific* generator + seeding + stream lengths the lab uses.