# PLAIN — EXP-0017: was the percolation result a power-of-two artifact?

## What did we test?

In 2018-era textbook numbers, 2D site percolation has a known cluster-mass
exponent D_f = 91/48 ≈ 1.8958. Back in September 2026 this lab measured D_f on
lattice sizes 128, 256, 512, 1024 — all exact powers of two — and got 1.8697,
about one standard deviation low. It then re-measured on sizes 127, 191, 253,
449 — none of them powers of two — got 1.8962, essentially perfect, and
concluded: "the first result was wrong because the lattice sizes were powers of
two."

A later independent audit of the whole lab said that conclusion was not properly
supported: its own acceptance rules were not met and a required independent
check was missing. So the claim was left hanging — neither accepted nor refuted.

**This experiment tested it properly.**

## How?

The trick is that "powers of two vs not" cannot be compared at the *same* lattice
size, so the lab compared sizes that differ by exactly one lattice unit:
128 against 127, 256 against 255, 512 against 511, 1024 against 1023. Those pairs
match in physical size to within 1/1024, and the same measuring code was used
for both.

Better still, each pair shares the same random numbers: one 1024×1024 random
field is generated, and the 1023×1023 sample is literally the same field with one
row and one column removed. This is a standard variance-reduction trick, and it
turned out to matter enormously — neighbouring sizes turned out to be
*extremely* well correlated.

We also added three safety nets:
- A second, independently written implementation of the cluster count, and a
  third written from scratch in plain Python. All three agreed **exactly** on
  every cell tested (190 cells, zero disagreements).
- A deliberate null: a comparison between two sizes that are *both* non-powers
  of two, where by construction no power-of-two effect can exist. This measures
  how much spurious signal the method produces on its own.
- A second full run with completely independent random numbers, sharing nothing.

## What happened?

The measured difference between powers of two and their neighbours was
**−0.0014**, with a confidence range of **[−0.0039, +0.0008]**.

For scale: the "artifact" would have had to be **0.0265** to explain the original
result. What we measured is about **one nineteenth** of that, and the entire
confidence range fits inside ±0.010 — a margin we set in advance specifically to
be smaller than the effect being explained.

**Verdict: the power-of-two lattice artifact is not supported.** The original
1.8697 vs 1.8962 difference cannot be blamed on lattice sizes being powers of two.

As a bonus, the pooled exponent over the whole balanced set was 1.8805, and the
textbook value 1.8958 sits comfortably inside its confidence range. So ordinary
2D percolation is reproduced.

## Could it just be a computer artifact?

That was the first question we asked ourselves, and the honest answer is: **the
first version of our own analysis was broken, and we caught it.**

We initially measured the exponent by comparing neighbouring sizes directly and
dividing by the tiny difference between them. That amplifies any random noise by
about a thousand times. Two things gave it away:

- Our own null check — a comparison that *cannot* contain a power-of-two effect
  — came out **larger** than the actual result we were trying to measure.
- The per-size numbers were self-contradictory, reporting confidently things like
  "1.106 ± 0.002" and "3.913 ± 0.055" for neighbouring sizes.

So we threw that analysis away, kept it on file as evidence of the mistake, and
rebuilt the estimator using the standard balanced method. We then **tested the
new estimator on fake data where we knew the answer in advance**: it correctly
returned zero when there was no effect, and correctly returned exactly ±0.0265
when we injected an effect of that size. Only then did we apply it to the real
data.

Notably, the broken analysis did not favour a desired conclusion — it returned
"inconclusive". The correction did not manufacture a result; it made a result
possible.

## What this does NOT prove

- It does **not** say EXP-0009 or EXP-0010 were right or wrong. Those records
  stay exactly as they are. This experiment only removes one candidate
  explanation for the gap between them.
- It does **not** explain why EXP-0009 landed 1σ low. That is still open, and the
  honest answer is that a ~1σ miss with a properly measured interval is not
  obviously a mystery at all.
- It is a test of a numerical method, not a discovery about physics. No novelty
  is claimed.
- The threshold p_c was assumed, not measured, so a small systematic remains that
  we did not quantify.
- The cross-check with fully independent random numbers is too small (40 runs) to
  confirm the main result by itself; it could neither confirm nor refute, and its
  point estimate pointed the other way. That is reported rather than buried.

## Status

**CONTROLLED** for the question "is there a power-of-two artifact?" — answered
no, with a pre-registered margin, pre-registered falsification rule, three
agreeing implementations, and a synthetic validation of the estimator itself.

This was audit finding N-005, Priority 1. It is now closed.

The lab's own standard is to prefer finding an exciting hypothesis to be wrong
over confirming it. This time, the exciting hypothesis was the lab's own.
