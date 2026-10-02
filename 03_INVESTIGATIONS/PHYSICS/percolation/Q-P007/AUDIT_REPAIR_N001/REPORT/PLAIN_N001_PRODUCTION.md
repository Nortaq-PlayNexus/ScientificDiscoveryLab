# PLAIN — N-001: what is the 2D percolation cluster-size exponent, really?

## What did we test?

For 2D site percolation, the number of clusters of size *s* should follow a power
law with an exponent τ whose exact value, 187/91 ≈ 2.0549, is known. In
laboratory language, if you make the lattice bigger, the big cluster grows a
little faster than the small ones, and τ says how much faster.

The lab had claimed to measure τ = 1.98 back in September 2026. When an
independent audit looked at how that number was produced, it found the storage
code was broken: the list of cluster sizes it saved was literally **empty** for
the measurement that mattered. So the number 1.98 had no valid data behind it.

This run redid the measurement properly, storing every single cluster size of
every one of 50 large lattices, and fitting τ with an uncertainty method that
treats clusters from the same lattice as related (they obviously are — you can't
pretend 30,000 clusters from one lattice are 30,000 independent facts).

## What happened?

**τ = 1.9201, with a confidence range of [1.9074, 1.9335].**

The textbook value is 2.0549. That is *outside* our range, and not by a little —
the gap is 0.135, about ten times the width of our uncertainty.

So the pre-registered decision rule fired: **DEVIATION**.

## Now the important part: what that does NOT mean

It does **not** mean the textbook value is wrong. It does not mean new physics.

Here is why, and it is the whole point of this write-up. Before this experiment
was ever designed, the lab had already written down the following, in the
preregistration of the earlier attempt:

> "the finite-domain lattice-scale crossover gives an apparent exponent ~1.8–2.0
> at s~10–10³ that converges to the Fisher value 187/91 only asymptotically"

In plain terms: at any lattice you can actually build on a computer, you are not
seeing the true infinite-system exponent yet. You see something a bit lower, and
it only creeps up toward the true value as you make the lattice bigger and look at
smaller clusters.

**Our answer, 1.920, sits inside that predicted 1.8–2.0 band.** And it behaves
the way the prediction says it should: when we narrowed the fit to smaller
clusters, the estimate rose from 1.912 to 1.936 — moving *toward* the textbook
value, exactly as expected.

So the honest summary is: **we measured what finite-size crossover predicts, and
this experiment is not able to tell "crossover" apart from "the exponent is
wrong."** The verdict `DEVIATION` is a true description of our numbers at
lattice size 1024. It is not a claim about 2D percolation.

To actually settle it you would need much larger lattices, or a way of
extrapolating to infinite size — and this run does neither.

## One clean negative result

The old analysis had claimed that nudging the critical threshold slightly
("refined p_c") explained the discrepancy. We tested that directly by running
both thresholds on the *same* random numbers, so the comparison is as clean as it
can be.

Difference in τ: **−0.00003**, confidence range [−0.00067, +0.00036].

That range contains zero, in every one of the four fit windows we preregistered.
**The refined threshold makes no difference at all.** One candidate explanation is
dead. That is a genuine, useful result.

## Another thing worth flagging

The old number was 1.98. Our corrected number is 1.920 — **further** from the
textbook value, not closer.

So the story "we fixed the storage bug and recovered the true exponent" would be
wrong. The old 1.98 was simply a different, invalid number. We replaced a broken
measurement with a valid one, and the valid one is not closer to the textbook
value. We are recording that because it would be easy to spin it the other way.

## How solid is this?

- All 50 planned lattices, both arms, completed: 50/50.
- All 2000 bootstrap resamples succeeded.
- 1,462,967 cluster sizes in the primary fit.
- Four different fit windows were preregistered; **all four agree** the textbook
  value is excluded, so the finding is not an artefact of picking a convenient
  range.
- We used a different, more reliable way of fitting (counting clusters bigger than
  a threshold) as the primary method, exactly as preregistered. The alternative
  method we also ran is much jumpier — 1.61 to 1.97 depending on the range —
  which is why it was designated a diagnostic only.

## Status

**DEVIATION — escalated for review, not a discovery.**

The lab's own rules say a deviation gets escalated, not tuned, and certainly is
not a discovery. No novelty is claimed. The next step is a larger-lattice or
finite-size-extrapolation study, not a re-run of this one.

Honest limitation: the critical point was assumed rather than measured, and this
run used a single largest lattice size (1024), so no extrapolation to infinity is
possible from it.
