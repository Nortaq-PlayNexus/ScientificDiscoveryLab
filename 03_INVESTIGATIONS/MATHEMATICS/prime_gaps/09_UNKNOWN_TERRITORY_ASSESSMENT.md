# EXP-0008 Unknown-Territory Assessment

This document separates what is known, what EXP-0008 measured, and what remains genuinely open. “Unknown” does not mean that a result is novel; it means the current evidence does not decide the question.

## Question matrix

| ID | Question | Current status | Evidence | What would resolve it |
|---|---|---|---|---|
| U1 | Do normalized consecutive gaps converge to `Exp(1)` as scale grows? | **Known asymptotic conjecture/conditional framework; finite residual untested.** | Gallagher and related theory; Wolf/Cohen discuss scale and moments. | A preregistered scale sequence with an admissible wheel/singular-series null. |
| U2 | Is the first-bin zero solely the even-gap support constraint? | **Mostly resolved for EXP-0008.** | Exact inequality `2/log(10^8)>e1`; zero count in all blocks. | No further experiment needed for the first bin; a corrected null should exclude it. |
| U3 | How much shape discrepancy remains after parity conditioning? | **Open.** | Even-lattice and exploratory pair surrogates reduce but do not explain the residual. | Prospective wheel-conditioned simulation with calibrated uncertainty. |
| U4 | What is the correct finite-scale distribution of gaps conditioned on residues? | **Open; theory exists asymptotically.** | Lemke Oliver–Soundararajan; Goldston–Ledoan; C6 is not a proper conditional null. | Endpoint-pair and singular-series model with held-out validation. |
| U5 | How much serial dependence remains after wheel conditioning? | **Open.** | Nonzero lag correlations and cluster sensitivity. | Dependence-aware simulation or a prime-index stationary model. |
| U6 | Does variance approach 1 with scale? | **Empirically partial; asymptotically open.** | Variance ratio rises 0.582→0.723 from B1 to B4. | Multiple decades with matched estimator and confidence intervals. |
| U7 | Are asymptotic moments exponential even if the finite distribution is not? | **Known distinction; specific limits open.** | Cohen’s theorem/qualification and Wolf’s moment work. | Rigorous/numerical moment study with exact normalization and error terms. |
| U8 | Does the mean remain one after conditioning on local density and wheel? | **Likely stable, not fully tested.** | Means near 1; cluster intervals contain 1. | Wheel/HL model with a prespecified mean estimand. |
| U9 | Are endpoint transition biases stronger than lower-prime residue effects? | **Known qualitatively; not measured by EXP-0008.** | Published PNAS residue-pair biases; C6 omits endpoint pairs. | Transition-matrix analysis with singular-series expectations. |
| U10 | Is the residual Q-M007 bin pattern reproducible in new data? | **Unestablished.** | Q-M007 is post hoc and uses invalid cell p-values. | New preregistered data split and exact multinomial calibration. |
| U11 | Does the discrepancy persist after `10^8` under the same definition? | **Not established.** | Q-M008 changes denominator/blocks; no valid `10^10` result. | Streaming, denominator-matched, fully controlled run. |
| U12 | Could a residual survive a correct wheel/HL null and be scientifically new? | **Possible in principle; no current evidence.** | No complete null has been tested; literature already covers much of the broad phenomenon. | New hypothesis, preregistration, independent implementation, and literature review of the exact residual. |

## What is known

- The normalized consecutive-prime-gap quantity is standard.
- Gallagher gives a conditional Poisson law for log-length prime counts under Hardy–Littlewood-type assumptions.
- Consecutive gaps have arithmetic weights; Goldston–Ledoan gives a singular-series refinement.
- Even-gap support, period-six oscillations, and residue biases are established facts/phenomena.
- Cramér/Granville/wheel models can differ from naive i.i.d. predictions.
- Mean agreement and distribution agreement are not equivalent.

## What EXP-0008 adds

- A reproducible local computation through `10^8`.
- A clear numerical demonstration that an unconditioned continuous exponential is incompatible with finite prime-gap support.
- Descriptive scale and residue diagnostics.
- A useful warning that G2 can pass while the distribution test fails.

These are useful scientific and computational results, but not a new law.

## What remains genuinely exploratory

The only plausible route to a novel result is a residual that remains large after all of the following are modeled prospectively:

1. lower/upper normalization fixed in advance;
2. boundary-crossing gaps handled correctly;
3. finite wheel/candidate support;
4. endpoint residues and singular-series weights;
5. consecutive-gap rather than all-prime-pair weighting;
6. local density variation;
7. contiguous dependence-aware uncertainty;
8. independent implementation and external literature comparison.

Until that experiment exists, the appropriate label is **open model-selection question**, not “new analytical finding.”

## Evidence labels used here

- **Observed:** directly recomputed from the stored or independently generated data.
- **Known:** supported by cited mathematics or established numerical literature.
- **Inferred:** follows from a model assumption but is not directly identified by EXP-0008.
- **Unknown:** not decided by the current evidence.
- **Unsupported claim:** a stronger statement than the data and controls justify.

## Territory verdict

EXP-0008 occupies **known model territory with an artifact-prone operational test**. Q-M007 is post-hoc exploratory territory. Q-M008 is an incomplete/method-mismatched scale check. No currently identified item qualifies as a demonstrated novel mathematical phenomenon.
