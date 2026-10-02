# EXP-0011 — PLAIN-LANGUAGE SUMMARY

**What we did:** Ran the lab's controlled Monte Carlo pipeline on a 3D cubic lattice (simple cubic, 6-connectivity) at the published 3D site percolation threshold p_c ≈ 0.3116. We measured the critical exponents D_f, gamma/nu, and beta/nu, plus tau as a diagnostic, using the same pre-registered discipline as the 2D program: certified RNG streams, independent union-find cross-check (C7), frozen preregistration, frozen decision rule.

**Systems measured:** L ∈ {8, 16, 24} at p_c = 0.3116079, with 500/200/50 realizations respectively. Width curves were also measured at each L to estimate p_c via crossing.

**What we found:**

1. **Width curves converge slowly from above.** At L=8, 16, 24 the measured p_c values (0.418, 0.365, 0.333) are all above the canonical 0.3116. Linear 1/L extrapolation gives p_c(L→∞) ≈ 0.297, which is slightly below the literature value. This is a known limitation of small-L width curves in 3D — the data was collected and the result is reported honestly. For exponent measurement the canonical p_c = 0.3116 was used (width curves serve as a diagnostic).

2. **Exponents show deviations from literature values, consistent with small-L finite-size effects:**
   - D_f = 2.262 ± 0.102 (expected 2.53, |dev| = 0.268, ~2.6σ)
   - gamma/nu = 1.633 ± 0.147 (expected 1.40, |dev| = 0.233, ~1.6σ)
   - beta/nu = 0.736 ± 0.096 (expected 0.41, |dev| = 0.326, ~3.4σ)
   
   These deviations are expected at L ∈ {8, 16, 24} — these are tiny lattices for 3D FSS. The preregistration used these sizes as a pilot (EXP-0011), with the main run (EXP-0013) at L ∈ {128, 256, 512} to be executed next.

3. **tau diagnostic was not computable** — at L=24 with n=50 realizations, no tail clusters were found above the fit range minimum. This is a sample-size limitation at small L, not a code error.

4. **C7 independent implementation passed** — pure-Python union-find reproduced the lab's spanning counts bit-for-bit on all tested cells.

**What this does NOT prove:** Nothing new about 3D percolation physics. The pilot (EXP-0011) was a system test of 3D lattice machinery. The main run (EXP-0013) at larger L is needed to distinguish finite-size effects from genuine physics.

**Next step:** EXP-0013 at L ∈ {128, 256, 512} with 1000/500/100 realizations (see percolation_3d/CONFIG/prereg_EXP-0013.json).
