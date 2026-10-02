# HYPOTHESIS — HYP-003 (lab RNG statistical certification)

Registered in the lab HYPOTHESES.md as HYP-003. Frozen under EXP-0004.

## Statement (the claim certified)

For the lab generator `G_lab = engine.utilities.core.rng(label, seed)` (numpy
Generator / PCG64 seeded by `int(sha256(f"{label}:{seed}")[:16], 16)`) and the
frozen battery of statistical tests in EXPERIMENT_PLAN.md with stream length
2^18 bits (256 KiB of 8-bit words equivalent), the p-value distribution across
the preregistered test x seed grid is statistically indistinguishable from
Uniform(0,1):

- (H0-1) The two-sample KS test comparing the battery's p-value multiset against
  the theoretical Uniform(0,1) has p > 0.01.
- (H0-2) The number of p-values <= 0.01 lies inside the exact 95% central
  binomial band for expected rate 0.01 over the total number of cells.
- (H0-3) The number of p-values flagged by BH-FDR at alpha=0.01 also lies inside
  that same binomial band (FDR over-rejection would therefore be flagged too).

## Secondary, characterising statements (no discovery value)

- S1 (generator equivalence): the same battery applied to the raw numpy PCG64
  `Generator` (no label derivation) and to the MT19937 control `RandomState`
  yields p-value distributions that pass H0-1..H0-3 by the same rule. If LAB
  fails where controls pass, that is a genuine RNG defect (H1).
- S2 (reliability of the battery): if a control generator also fails, the
  battery is over-rejecting; verdict becomes INCONCLUSIVE and the battery must
  be fixed, not the RNG. This is the crucial meaning of "certified".

## Distinction from the null

H0 is the *calibration claim*: the generator behaves like a good PRNG. H1 is a
*defect claim*: a reproducible failure attributable to the lab RNG specifically.
The interesting (unexpected) outcome would be H1. This is infrastructure
certification, NOT a claim about nature and NOT a claim of novelty.

## Prior expectation

PCG64 is a well-tested algorithm; we expect H0 to hold for LAB and for both
controls (evidence state CONTROLLED / calibration certificate). A holistic
failure (all three fail) would indicate a battery bug (S2), not three broken
generators.

## What would falsify H0 (and generate an HYP-003 FAILED / red flag)

- KS p <= 0.01 for the LAB multiset while at least one control passes H0.
- small-p count outside the binomial band for LAB while controls are inside.
- A reproducible per-test bias in LAB that no control shows, confirmed on longer
  independent streams (e.g. doubling to 2^20 bits) without threshold-tweaking.