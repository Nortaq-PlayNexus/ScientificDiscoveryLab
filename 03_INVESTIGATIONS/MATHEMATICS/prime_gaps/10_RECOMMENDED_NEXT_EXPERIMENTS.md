# Recommended Next Experiments after EXP-0008

These are prospective designs, not permission to edit the frozen EXP-0008 preregistration. Allocate a new experiment ID and hypothesis ID after checking the live registry; do not reuse or overwrite EXP-0008.

## Priority 0 — repair the evidence record

1. Preserve the current canonical files and the pre-BH-fix files as immutable artifacts.
2. Record a file manifest with SHA-256 hashes for source, preregistration, raw/derived data, and reports.
3. Add a formal decision trace showing G1=FAIL, G2=PASS, G3=FAIL, G4=PASS, C6=FAIL, C7=PASS.
4. Correct the report wording to “G1 and G3 rejected; G2 passed.”
5. Mark Q-M007 as post hoc and Q-M008 as exploratory/method-mismatched.
6. Do not describe a missing `10^10` run as a negative or positive result.

## Priority 1 — new wheel/singular-series experiment

### Question

Does the normalized consecutive-gap distribution agree with a finite-scale, residue-aware Gallagher/Hardy–Littlewood model after arithmetic support is built into the null?

### Model hierarchy

Run the same data through predeclared nulls:

- **M0:** i.i.d. continuous `Exp(1)` (diagnostic only).
- **M1:** parity-conditioned even-lattice renewal model.
- **M2:** fixed wheel model for `W=6,30,210,2310`.
- **M3:** growing-wheel Granville-style model.
- **M4:** endpoint-residue/singular-series model with consecutive-pair correction.

M0 must not be the primary scientific null because it assigns positive mass to impossible bins.

### Data and blocks

Use a new deterministic prime stream with a documented boundary convention. Start at a sufficiently large scale, and use fixed logarithmic windows such as `[10^k,2·10^k)`, `[2·10^k,5·10^k)`, and `[5·10^k,10^{k+1})`. Include the gap whose lower prime is in the window, even if its upper prime crosses the boundary.

### Predictions

Predeclare:

- mean and variance effects;
- histogram and tail effect sizes;
- endpoint-transition frequencies;
- convergence of standardized effect sizes with scale;
- the maximum absolute standardized residual across predeclared families.

### Controls

- independent i.i.d. null with matching sample sizes;
- parity-only positive control;
- wheel-model negative control;
- injected endpoint-residue bias with known effect size;
- detector/sieve integrity checks;
- seed variation only for stochastic components;
- separate C7 implementation using a genuinely different prime source, such as bounded `sympy.primerange` plus a segmented sieve.

### Dependence-aware inference

Use contiguous prime-index clusters as the primary resampling unit. Predeclare cluster lengths and sensitivity lengths. Store batch means, effective sample sizes, and cluster-level tail discrepancies. Do not use individual-gap bootstrap as the only uncertainty estimate.

### Decision rule

A new H1 claim should require:

1. a predeclared arithmetic-aware null with positive expected counts in every cell;
2. a residual effect that is not explained by the known support correction;
3. consistent direction and bounded effect size across at least two non-overlapping scale windows;
4. survival of cluster-level sensitivity;
5. agreement of the independent implementation;
6. no equivalent literature result found for the exact residual.

If the residual disappears or changes sign under M1–M4, classify the original result as a model artifact. If it persists, report it as a new **controlled anomaly** and escalate for mathematical review—not automatically as a discovery.

## Priority 2 — dependence calibration study

Use a stationary block or sieve-process null and simulate complete contiguous prime-index blocks. Compare:

- i.i.d. chi-square/KS p-values;
- cluster-calibrated p-values;
- block-bootstrap intervals;
- batch-means and spectral long-run-variance estimates.

The target is not to make the original p-values look favorable. The target is to determine whether any residual is larger than dependence-aware sampling variation.

## Priority 3 — boundary and scale study

At `10^9` and, only if a streaming design is ready, `10^10`:

- use the same lower-prime denominator as EXP-0008;
- use the same block definitions;
- stream aggregate counts and moments rather than retaining hundreds of millions of Python floats;
- checkpoint every segment and verify resume equivalence;
- record a segment checksum and the next prime above each segment boundary;
- predefine the minimum expected count per bin and the wheel cutoff.

No valid `10^10` result currently exists. A long run that freezes near a segment is an incomplete execution, not evidence.

## Priority 4 — Q-M007 correction

Do not repair Q-M007 in place. Create a new analysis with:

- record-level or reproducible raw gaps;
- exact multinomial/simulation p-values;
- predeclared cells and family definitions;
- no averaging that gives B1 and B4 equal weight;
- dependence-aware calibration;
- an independent implementation;
- a held-out scale or data split.

A post hoc descriptive residual plot is fine, but it must be labeled exploratory.

## Priority 5 — endpoint-residue and transition study

Use the matrix of pairs `(p_i mod q, p_{i+1} mod q)` for `q=6,12,30,210`, compare it with singular-series predictions, and test whether transitions explain the apparent C6 effect. This is more scientifically informative than conditioning only on the lower residue.

## Resource and safety rules

- Do not run the canonical runner in the investigation directory for validation.
- Copy the investigation to a new timestamped directory before any full rerun.
- Do not append to the live registry during reproduction.
- Use log-p values and exact survival functions.
- Save record-level gaps or a documented compressed representation with hashes.
- Keep the frozen EXP-0008 result immutable and annotate successor results separately.

## Expected value

Priority 1 is the decisive next step. It can distinguish a genuine residual law from the already-known arithmetic finite-scale correction. Priorities 2–5 are supporting diagnostics. Until Priority 1 is completed, the scientifically correct status is:

> **EXP-0008: operational-null rejection; scientific interpretation unresolved and artifact-dominated. No novelty claim.**
