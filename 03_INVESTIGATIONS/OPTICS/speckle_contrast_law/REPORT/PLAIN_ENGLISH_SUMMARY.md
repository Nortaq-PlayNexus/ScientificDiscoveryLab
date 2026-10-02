# PLAIN ENGLISH SUMMARY — EXP-0002 (Speckle contrast)

## What did we test?

Laser speckle is the grainy pattern you get when laser light scatters off a rough
surface. The textbook rule says: if you add up several *independent* speckle
patterns, the "graininess" (contrast) should fall as 1 divided by the square root
of how many patterns you added: C(M) = 1/sqrt(M).

We built the speckle patterns in a computer and checked that rule. We also asked
a practical question: does the rule still hold on small computer grids, and if it
drifts, does the drift go away when the grid gets finer?

## What happened?

- The rule held. Over the whole test, the measured value sat within 0–2% of the
  textbook prediction.
- On the biggest grid the result matched the prediction to about a tenth of a
  percent.
- On the smallest grids there was a small shortfall — the computed graininess was
  slightly *lower* than predicted. Crucially, that shortfall shrank as the grid
  got finer, which is exactly the signature of a **computer grid effect**, not a
  physics effect.
- A second, completely independent program (different method, different random
  generator) produced the same rule to better than 0.05%.
- A sanity check confirmed the single-speckle brightness follows the expected
  exponential distribution (a key assumption).

## Could it just be a computer artifact?

The small low-resolution shortfall looks like exactly that — an artifact of using
too coarse a grid — because it disappears as the grid is refined. That is why the
test was designed with a grid ladder. We report the artifact rather than hiding it.

## What survived the controls?

- The law C(M) = 1/sqrt(M) survived: it holds on large grids, across several
  random seeds, across full and interior regions, and in an independent
  implementation.
- The only flagged deviation (one low-resolution cell) is explainable as the grid
  effect above.

## What does this NOT prove?

- It does not prove anything new about the real world. This law is known textbook
  optics; we reproduced it.
- It says nothing about exotic optics claims. It only certifies that this lab's
  simulation + statistics machinery behaves correctly on a known case.
- It is not a discovery, and it is not evidence for anyone's unusual theory.

## What should we test next?

- The natural follow-on is the vortex-density law for random optical fields
  (Q-O002), which reuses this exact pipeline and where the previous sandbox work
  found a real numerical trap (a grid-locked counter). That is the honest place
  to look for a genuine, controlled anomaly — and to demonstrate the lab can kill
  a false one.

## Bottom line

The laboratory's first real experiment worked end-to-end, reproduced a known law,
found only the expected small grid artifact, and an independent implementation
agreed. Evidence state: **CONTROLLED** (reproduced with controls + independent
method) for the law's numerical validity. Nothing here is novel.