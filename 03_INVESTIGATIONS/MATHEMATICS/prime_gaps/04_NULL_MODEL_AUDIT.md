# EXP-0008 Null-Model Audit

## 1. Nulls are not interchangeable

EXP-0008 calls the following statement H0:

> In each block, `delta_i` are i.i.d. `Exp(1)`.

That is an operational null for the code. It is not identical to the Gallagher statement, a Hardy–Littlewood pair model, a wheel-conditioned prime process, or a Cramér random set. The audit keeps these levels separate.

## 2. Null hierarchy

| Null | Mathematical content | Justification | Implemented in EXP-0008? | Audit result |
|---|---|---|---|---|
| N0: i.i.d. continuous `Exp(1)` | `P(delta>t)=exp(-t)` for every gap; independent observations. | Simple Poisson spacings and the project’s preregistration. | **Yes** | Rejected overwhelmingly, but structurally incompatible with even gaps. |
| N1: parity-conditioned local exponential | Candidate positions are odd; local prime probability is `2/log(p)`. A geometric number of odd steps gives an even gap with scale `log(p)`. | Basic mod-2 sieve constraint and local intensity. | No | Removes the impossible first bin; finite residual remains. |
| N2: wheel-conditioned process | Candidates are integers coprime to `W`; select candidates with probability `W/(phi(W) log(p))`; retain the discrete allowed offsets. | Finite sieve/wheel approximation to local prime density. | No | Exploratory simulations; materially closer than N0, not a complete Hardy–Littlewood model. |
| N3: Cramér random set | Include each integer independently with probability approximately `1/log(p)`. | Classical random-prime baseline. | No | Crude microscopic version produces gap 1/very small gaps and is not appropriate at these finite scales. |
| N4: Granville/sieve-survival model | Discard integers sharing factors with a growing wheel and select survivors with corrected probability. | Modern arithmetic-aware random model; Banks–Ford–Tao give a rigorous framework. | No | A scientifically appropriate direction, but not a ready-made EXP-0008 test. |
| N5: Hardy–Littlewood/Gallagher pair model | Weight gap values by the singular series for admissible even differences and impose the consecutive-pair condition. | Directly relevant conditional theory; Goldston–Ledoan refines Gallagher for consecutive gaps. | No | Closest theory-motivated alternative; requires a new implementation and prospective cells. |
| N6: empirical/block null | Preserve the observed local dependence or resample contiguous prime-index blocks. | Dependence sensitivity, not a theory of primes. | No (individual-gap bootstrap only) | Useful for uncertainty; does not itself validate `Exp(1)`. |

## 3. The first-bin contradiction

The first edge is `e1=-log(0.9)=0.1053605157`. Since all lower primes are below `10^8`, an even gap has

\[
\delta \ge 2/\log(p) > 2/\log(10^8)=0.1085736205.
\]

Thus N0 assigns positive probability to an interval that N1/N2/N3-like arithmetic processes cannot populate. The first-bin expected count is `n/10` in every block, but the observed count is zero. Its chi-square contribution is:

| Block | Expected first-bin count | First-bin contribution | Percent of block chi-square |
|---|---:|---:|---:|
| B1 | 836.2 | 836.2 | 35.5% |
| B2 | 6,890.5 | 6,890.5 | 55.0% |
| B3 | 58,608.0 | 58,608.0 | 55.6% |
| B4 | 509,687.5 | 509,687.5 | 59.8% |
| **combined** | **576,022.2** | **576,022.2** | **59.28% of 971,920.0236** |

The arithmetic explanation is exact for the sample, not an estimated post-hoc correction.

## 4. Exploratory alternative calculations

A separate, non-canonical audit used an independent odd-only sieve and generated simple discrete surrogates. These calculations were not preregistered and are not substitutes for a new experiment. They are included to show what changes when the null is made compatible with arithmetic.

### Parity/even-lattice surrogate

A geometric renewal process on even integer positions, with local success probability `2/log(p)`, was evaluated against the same bins. The resulting descriptive chi-square values were:

| Block | N0 stored chi-square | Even-lattice surrogate chi-square |
|---|---:|---:|
| B1 | 2,357.813 | 851.840 |
| B2 | 12,517.679 | 5,641.868 |
| B3 | 105,347.670 | 29,936.510 |
| B4 | 851,696.861 | 181,809.717 |

The large reduction diagnoses the support mismatch. It does not establish that the parity model is correct: residual discrepancies remain, and these chi-square values are not calibrated p-values against a dependence-aware prime model.

### Singular-series-weighted exploratory model

A rough pair-Poisson surrogate using even-gap singular-series weights and a small-prime exclusion (“special 24” in the temporary calculation) gave descriptive chi-square values of 1,366.080; 8,210.205; 50,843.669; and 99,777.464 for B1–B4. These are useful sensitivity calculations, not a validated implementation of Goldston–Ledoan. A successor must specify the exact singular series, consecutive-gap inclusion–exclusion, wheel cutoff, local density, and simulation error before using such values inferentially.

### Support-adjusted continuous check

Subtracting the pointwise parity lower bound and comparing the shifted observations with an i.i.d. truncated exponential still gives KS distances approximately 0.121861, 0.100791, 0.086696, and 0.074817 for B1–B4. This shows that the first bin is not the only reason the distribution differs from continuous `Exp(1)`; it does not identify the correct arithmetic null.

### Cramér warning

A naive geometric `1/log(p)` random set predicts many gap-1 and very small normalized gaps. In the exploratory B1 simulation it produced roughly 700 observations in the first bin, while the prime data produce zero. This is a useful diagnostic against using an unconditioned microscopic Cramér surrogate as the sole null.

## 5. Scale evidence

The first-bin impossibility persists until the upper scale makes `2/log(x)` smaller than the first edge. The threshold is approximately `1.7538e8`. The stored Q-M008 data show zero first-bin observations at `10^8` and about 2.7 million at `10^9`, consistent with this elementary support calculation. This is a scale-dependent model effect, not evidence that the deviation is scale-invariant or newly discovered.

## 6. What N5 must include

A defensible Gallagher/Hardy–Littlewood comparison should, at minimum:

1. condition on candidate residues and the pair of endpoint residues;
2. use the singular series for even gap `d` (and account for the “consecutive” condition);
3. use a wheel or growing sieve cutoff, not a fixed all-integer `Exp(1)`;
4. use local intensity based on `log x` or a suitable integral over each block;
5. calibrate uncertainty with contiguous prime-index blocks or a dependence-aware simulation;
6. use bins with nonzero model probability in every tested scale;
7. report exact or simulation-based p-values and log-p values.

None of these requirements was met by EXP-0008.

## 7. Null-model conclusion

The literal N0 rejection is valid as a computational statement. N0 is not robust: its support, lattice, residue, and dependence assumptions fail before any question of a new prime-gap law is reached. The correct scientific null remains untested. A successor should be preregistered as a new experiment, not retrofitted into the frozen EXP-0008 verdict.
