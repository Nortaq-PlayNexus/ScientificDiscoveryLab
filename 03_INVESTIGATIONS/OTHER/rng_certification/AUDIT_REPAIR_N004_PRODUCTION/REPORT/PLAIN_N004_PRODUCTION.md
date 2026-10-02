# PLAIN — N-004: is the lab's random number generator actually any good?

## What did we test?

Almost every experiment in this lab draws "random" numbers, and they all come
from one function. Back in September 2026 the lab ran 24 standard randomness
tests on it, got a good result, and wrote down "CERTIFIED".

Then an independent audit read how that verdict was computed and said: no. The
24 tests had all been run on **the same block of random numbers**, and then their
results were pooled together as if they were 24 independent chances to be wrong.
They are not independent — they are 24 different questions about one dataset.

An audit can *say* the reasoning is wrong. This experiment **measures** how wrong.

## How?

We ran the same 24 tests on **200 completely separate random streams** (and 60
more at a longer length), for four different generators:

- the lab's own stream,
- a plain reference PCG64,
- the older Mersenne Twister,
- and **a generator we deliberately broke** on purpose.

That last one is the important control. A test suite that passes everything is
worthless, so we included a bad generator that *must* get caught. If our methods
had failed to flag it, we would have thrown the whole run away and said so.

## What happened?

**The broken generator was caught immediately** — one of the tests rejected it on
100% of trials, at both stream lengths. So the test suite works, and what follows
can be trusted.

**The lab's own generator passed cleanly.** All 24 tests, at both stream lengths.
Not one showed a problem. On average, the tests gave p-values clustered tightly
around 0.5, which is exactly what a well-behaved test should do.

## The big finding: the audit was right, and here is the size of it

When you run 24 tests on one shared block of numbers and just count how often
something looks suspicious, you get a false alarm rate of about **20 in 100
trials**.

The correct rate is **1 in 100**.

So the naive analysis was wrong by a factor of **12 to 41 times**, depending on
the generator. Once you account for the tests sharing data, the rate drops back
to between 0 and 1.7 in 100 — right where it should be.

This is why the "CERTIFIED" claim was withdrawn, and now there is a number
attached to the reason. The lab's generator was probably fine all along. It was
the *analysis* that was broken, not the randomness. Withdrawing the certificate
was the right call, and this run is the evidence for why.

## One test is genuinely shaky

The "runs" test (does the number of long vs short streaks of bits look right?)
is the only one with a real problem, and it is worth flagging honestly:

- It **never** wrongly rejects — so it will not cause false alarms.
- But its p-values are consistently a bit too high (average ~0.56 instead of 0.5),
  meaning the test is a little too forgiving.
- And the verdict is **unstable**: two statistically identical ways of setting up
  the same generator got opposite answers.

So the honest verdict on that test is "borderline, unresolved" — not "fine", and
not "broken". It is also the one test here whose maths deserves checking against
the official reference implementation.

## What this does NOT prove

- **It does not certify anything.** Passing a test suite is not proof of
  randomness. Nobody can prove a computer's random numbers are random; these
  tests only fail to detect certain specific kinds of cheating.
- **The old "CERTIFIED" label stays withdrawn.** This run does not bring it back.
  What it gives instead is something more honest and more useful: a per-test
  statement, per generator, per stream length.
- **"No problem detected" is not "provably exact".** With 200 trials we can only
  spot a test that misbehaves badly. A test that is wrong in a subtle way — say it
  should flag 4% of the time but flags 2% — would slip through. The 2^22 results
  are weaker still: only 60 trials, so anything below about an 8.5% flag rate is
  invisible to us.
- These are the laboratory's *own* reimplementations of the standard tests, not
  the official NIST program.

## Status

**Battery validated, and the lab's generator shows no calibration problems in any
of the 24 tests at either stream length — at the resolution this experiment can
actually support.**

No certification. No novelty. The withdrawn certificate stays withdrawn, and the
audit that withdrew it was right to.
