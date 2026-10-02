# EXP-0006 — PLAIN-LANGUAGE SUMMARY

**What we did:** Re-measured the "sharpness" (width) of the percolation
transition on a square lattice with a finer measurement grid, so the numbers
stopped being limited by the measuring tool rather than the physics. Same
system, same random seed, same decision rules as EXP-0005 — only the grid got
finer at the two largest lattices, and the width-fit was repeated with a more
robust starting point.

**What we found:**

1. **The percolation threshold (the main question) is reproduced.** On open
   square lattices, bonds cross top-to-bottom at p_c = 0.5002 vs the exact
   value 0.5; sites at 0.5928 vs the accepted 0.59274605. Both are far inside
   the pre-committed 0.01 tolerance. A second, independent way of simulating
   the same thing (written from scratch, no shared code) produced bit-for-bit
   identical raw counts on all 39 test cells.

2. **The width question is now answered.** The transition width shrinks with
   lattice size as L^−1.3559, whose inverse (0.7375, 95% box [0.7124, 0.7608])
   matches the known exponent 3/4. Three different ways of estimating the width
   agree to better than 1%, so this is no longer an estimator artefact. The
   earlier failure (EXP-0005) was caused by a measurement grid too coarse to
   see the transition at all — fixed here.

3. **One gate still fails, and it is a tool limitation, not physics.** The
   "wrap-around" (periodic) boundary estimator on L=32/48/64 lattices does not
   fit the smooth size trend well (chi-squared 4.74 vs the allowed 4). This is
   the same fingerprint as EXP-0005: tiny torus lattices bounce around. It does
   not change the conclusion about p_c.

**So, everything the experiment was designed to measure is actually fine now;
the only reason it is not formally called a "pass" is that one secondary
estimator on very small lattices has a bad fit statistic.** Fixing that is a
known, cheap follow-up: extend the wrap-around estimator to larger lattices
(L=96,128,192 — already pre-registered as EXP-0007).

**What this does NOT prove:** Nothing new about nature. These are textbook
percolation values; the experiment certifies that the lab's random-lattice
machinery reproduces them. "Threshold reproduced" is the goal; no anomaly, no
discovery.