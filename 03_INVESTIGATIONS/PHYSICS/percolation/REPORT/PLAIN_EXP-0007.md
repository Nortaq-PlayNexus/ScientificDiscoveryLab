# EXP-0007 — PLAIN-LANGUAGE SUMMARY

**What we did:** The last remaining failure in the percolation experiments was a
fit-quality problem with the "wrap-around" (torus) estimator on small lattices.
We measured that estimator at three bigger lattice sizes (96, 128, 192) so the
fit had six sizes to play with instead of three. Same method, same seeds, same
rules; only the new lattice sizes were measured fresh.

**What we found:**

1. **The wrap-around estimator now fits cleanly.** The poor fit statistic
   dropped from 4.74 to 2.24 (limit 4.0). The estimated percolation threshold is
   **0.5007**, versus the exact value 0.5 — a difference of 0.0007, far inside
   the promised 0.01 tolerance.

2. **The "wobble" was a small-lattice artefact, not something real.** The
   threshold still wobbles a little between sizes (about 0.003 of a unit), but
   with six sizes it is clearly just random sampling scatter around a smooth
   shrinking trend — the textbook behaviour.

3. **Every single check passed this time:** determinism (same answer when
   re-run), scale stability (dropping the two small sizes doesn't move the
   answer), seed ladder (six different random seeds agree), independent
   re-implementation (a from-scratch version of the code produced bit-for-bit
   identical raw counts on all 78 tested configurations), threshold tolerance,
   and the fit-quality check.

4. **Width diagnostics agree with theory.** The transition width shrinks with
   size at the expected rate (exponent 1/0.7255 ≈ 1.38, theory ~1.33), matching
   the clean bond_span result from EXP-0006 (0.7375). The uncertainty on this
   diagnostic is wider here because the measurement grid is coarser — noted
   honestly, not brushed under the rug.

**What changed:** Q-P004 is now **H0_SUPPORTED** — the lab's random-lattice
machinery reproduces the textbook percolation threshold within tolerance, with
all controls green and an independent implementation confirming the results.
It was the last outstanding failure from the earlier experiments (0005/0006).

**What this does NOT prove:** Nothing about nature. These are textbook values;
the experiment certifies the machinery. Three earlier experiments set the same
pattern: a controlled pipeline that reproduces known science and never claims
discovery on its own.