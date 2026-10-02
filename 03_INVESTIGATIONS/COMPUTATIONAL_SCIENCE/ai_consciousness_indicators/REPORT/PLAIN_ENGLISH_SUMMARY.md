# PLAIN ENGLISH SUMMARY — EXP-C001

## What did we test?

Whether you can build a *measuring instrument* for "how conscious might this AI
be" that behaves sensibly, before pointing it at any real AI.

Not: whether a particular AI is conscious. We did not test that, and this
investigation cannot answer it.

## The idea

Neuroscientists have theories about what the brain has to *do* to be conscious —
global workspace theory, recurrent processing, higher-order monitoring and so on.
In 2023 nineteen researchers, including Yoshua Bengio and David Chalmers,
converted those theories into 14 concrete "indicators": checkable properties a
computer could have.

The obvious thing is to score the 14 and count the ticks. **That is wrong**, and
this investigation refused to do it. Counting treats evidence from one theory
about one mechanism as several independent pieces of evidence, which inflates the
score. So the instrument first collapses each theory's indicators into a single
verdict, then combines theories.

## What happened?

The calibration stage is the real story. Before trusting the instrument we ran it
against six systems whose answers we think we know — a human, a lookup table, a
plain neural network, and three deliberately awkward cases.

**The instrument failed three times.**

- First attempt scored a plausible modern AI at **0.000**. It was treating each
  brain theory as a requirement, so one theory failing cancelled everything. But
  the source paper says some theories are *sufficient* — a system needs one, not
  all four.
- Fixed that, it scored a system with nothing actually established at **0.55**.
  Four weak results were adding up into false confidence. Vagueness isn't evidence.
- Fixed that, it scored a system with a genuine workspace architecture at
  **0.09**. The absence penalty was charging four times for the same fact.

All three were caught by the test systems, not by anything we'd written in
advance. That is the argument for the calibration stage existing at all: a
counting checklist would have shipped all three bugs without blinking.

Final state: all six reference systems correctly separated, 19 tests passing. The
adversarial case — a system that produces confident first-person talk about inner
experience but has no inner states — scores 0.107 against a ceiling of 0.15. So
the instrument is measuring structure, not eloquence.

## Could it just be a computer artifact?

Yes, and here's the specific way. **We chose the settings that made our own test
cases come out right.** The temperature constant was picked by sweeping until our
six invented reference systems landed in the ranges we ourselves assigned to them.

So passing the calibration shows the instrument is internally consistent with
our assumptions. It does **not** show the assumptions were right. Nothing inside
this investigation can detect that, because those assumptions are the only source
of truth being used.

This is written into the falsification file as an open problem, not buried.

## What did this NOT prove?

- Nothing about whether any AI is conscious.
- That the 14 indicators are the right ones.
- That these numbers measure anything in the absolute sense.
- Anything about whether a system "feels" anything. The framework itself draws
  that line: it measures what's accessible and reportable, not experience.

The 2023 authors say it plainly themselves — satisfying all 14 indicators would
still **not** mean a system is definitely conscious.

## So what's the point?

Two things.

**A number you can argue with is better than a yes/no you can't.** The instrument
returns a probability with a range, shows its working per theory, and lists which
indicators were never actually tested. A claim of "the AI is conscious" or "it's
just a program" isn't falsifiable. "This system satisfies 9 of 14 indicators and
here's which, here are my priors, here are my confidence bounds" is.

**It found real bugs in itself.** Three reasoning errors about what the source
paper actually claims, caught in days by a six-case calibration. That's the
method working.

## Next steps

- Reproduce the workspace finding on an open-weights model so GWT indicators come
  from measured internals rather than literature summaries.
- Get the calibration anchors from consciousness researchers who didn't build the
  instrument. That is the only thing that breaks the circularity.
- Test whether scores hold up under different weighting schemes, rather than one
  hand-chosen constant.