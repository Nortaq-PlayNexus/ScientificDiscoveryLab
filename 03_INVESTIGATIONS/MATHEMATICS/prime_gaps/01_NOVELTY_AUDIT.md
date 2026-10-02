# EXP-0008 / Q-M002 / HYP-005 — Independent Novelty and Literature Audit

**Audit date:** 2026-09-24  
**Scope:** EXP-0008, its preregistration, source, stored results, controls, C7 replication, Q-M007, and Q-M008.  
**Frozen inputs were not edited.** The canonical experiment was not rerun in place because the runner overwrites outputs and appends the live registry.

## Executive verdict

**Primary classification: D — statistical/modeling artifact or implementation issue.**

EXP-0008 robustly rejects its *operational* null of independent, continuous `Exp(1)` values. That is a real computational result. It does **not** establish a deviation from the Gallagher/Hardy–Littlewood prime-gap model. The most decisive reason is structural: for every lower prime used in EXP-0008, consecutive prime gaps are even and at least 2, while the first exponential-quantile bin is `[0, -log(0.9)) = [0, 0.1053605)`. Because all lower primes are below `10^8`, even the smallest possible normalized gap is

\[
\frac{2}{\log(10^8)}=0.1085736,
\]

so the first bin is mathematically empty. Its expected count under the unconditioned continuous exponential is nevertheless `n_b/10` in every block. The first bin alone contributes 576,022.2 of the reported combined chi-square of 971,920.0236 (59.28%).

The result is therefore best described as:

> **A reproducible rejection of an over-simplified i.i.d. continuous-exponential surrogate, dominated by finite-scale arithmetic support and accompanied by dependence and residue-model limitations; not a new prime-gap law or a novelty claim.**

The underlying asymptotic Poisson/Gallagher phenomenon is already known (Category A at that level). The normalized sequence itself is also prior art: Wolf (2014) studies \(D_n=(p_{n+1}-p_n)/\log p_n\) and its arithmetic oscillations. The exact EXP-0008 four-block histogram protocol is not identified as a named published result, but its ingredients and the relevant finite-scale oscillations are known. The **result as interpreted in EXP-0008** is Category D.

## Evidence ladder

| Layer | Finding | Evidence state |
|---|---|---|
| Instrument/computation | Prime counts, gaps, histogram counts, means, standard deviations, chi-square and KS statistics reproduce with an independent sieve. | **Supported** |
| Operational statistical result | The literal i.i.d. `Exp(1)` null is rejected in all four blocks by G1 and G3. | **Supported, with nominal p-values** |
| Mean claim | Mean normalized gaps are close to 1; G2 passes under the recorded bootstrap and independent cluster checks. | **Supported descriptively** |
| Full distribution vs continuous Exp(1) | Strong mismatch remains after removing the impossible first-bin support issue. | **Observed; not a valid Gallagher test** |
| Gallagher/Hardy–Littlewood model | Not tested with a scale-, residue-, pair-, and dependence-aware null. | **Unsupported claim / open** |
| C7 independent implementation | Arithmetic/statistical cross-check is useful, but it does not use the preregistered `sympy.primerange` source and does not independently validate the scientific null. | **Qualified** |
| Novelty | No controlled evidence for a previously unknown phenomenon. | **Not supported** |

## What was actually observed

The canonical internal-block sample sizes are 8,362; 68,905; 586,080; and 5,096,875. Means are 1.002428; 1.001326; 1.000359; and 1.000081. Standard deviations are 0.763163; 0.803721; 0.832889; and 0.850530. Thus the mean is stable while the variance and shape are not those of a continuous `Exp(1)` law.

The first-bin counts are `[0, 1019, 268, 745, 1641, 1066, 1136, 953, 984, 550]` for B1 and analogous records for B2–B4. The zero first-bin count is not a rare fluctuation: it follows from parity and the upper bound on the lower prime. The remaining histogram departures, serial correlations, and strong residue heterogeneity require a different null model; they cannot be interpreted as a new law merely because the original surrogate rejects.

## Why the H1 label is too strong

The frozen rule is a mechanical decision rule, not a claim hierarchy. It declares H1 when one or more primary gates reject, the C6 “survival” count is at least two, and C7 agrees. In the final run G1 and G3 reject, G2 passes, C6 is recorded as `FAIL` while its separate survival count is 4, and C7 passes. The report's sentence “G1/G2/G3 rejected” is inaccurate because G2 passed.

C6 is internally contradictory: its pass flag requires conditioned cells **not** to reject, while its survival count treats conditioned rejection as evidence that the deviation survived. Conditioning only on the lower prime modulo 12 also applies the same continuous-exponential expectation to arithmetic classes that should have different conditional predictions under a proper wheel/singular-series model.

C7 confirms that a second implementation sees the same deterministic prime sequence and rejects under both equal-width and exponential-quantile analyses. It does not establish that the null is scientifically appropriate, and its same-binning vector match is expected when the same deterministic data are re-read.

## Novelty decision

| Question | Answer |
|---|---|
| Is the normalized consecutive-prime-gap quantity known? | **Yes.** It is the standard local-spacing normalization in the Gallagher/Poisson literature. |
| Is an equivalent Poisson/Gallagher prediction known? | **Yes.** Gallagher gives Poisson counts in log-length intervals; Goldston–Ledoan gives a consecutive-gap refinement with a singular series. |
| Have arithmetic/period-six finite-scale deviations been reported? | **Yes.** Wolf and related numerical work explicitly discusses period-six oscillations, minimum gap constraints, and rescaling. |
| Is the exact four-block chi-square/KS/BH pipeline a published named statistic? | **No specific match was found.** This is a protocol detail, not evidence of novelty. |
| Did EXP-0008 identify a new distribution or mechanism? | **No.** No alternative model was identified, and the first-bin artifact alone accounts for most of the nominal chi-square. |
| Is a novel result potentially present after a correct null? | **Unresolved, but currently unestablished.** It requires a new preregistered scale/wheel/residue/dependence-aware experiment. |

## Approved replacement wording

> EXP-0008 deterministically reproduces a large mismatch between finite consecutive-prime gaps and an unconditioned i.i.d. continuous `Exp(1)` surrogate. The mismatch is confounded by the even-integer support of prime gaps, scale-dependent minimum gaps, serial dependence, and an inadequate residue-class null. The experiment does not falsify the Gallagher/Poisson heuristic and does not support a novelty claim.

## Literature basis

The principal references and their relation to EXP-0008 are detailed in `02_PRIOR_ART_MATRIX.md`. The most important anchors are Gallagher (1976), Goldston–Ledoan (arXiv:1111.3380), Lemke Oliver–Soundararajan (PNAS 2016, DOI 10.1073/pnas.1605366113), Wolf (Phys. Rev. E 89, 022922, which uses the same normalized spacing), Cohen (DOI 10.1080/10586458.2024.2362348), Maier (1985), and Banks–Ford–Tao (Invent. Math. 233, 1471–1518, 2023). The project’s “Conrey–Goldston–Keating” attribution could not be verified as a single identifiable source and should be qualified.

## Audit limitations

1. The project has no immutable commit history; internal preregistration evidence is strong but external immutability is not certified.
2. The stored `EXP-0008_raw.json` is aggregate output, not record-level raw gaps.
3. The alternative wheel and singular-series calculations in `04_NULL_MODEL_AUDIT.md` are exploratory independent checks, not preregistered replacements for EXP-0008.
4. No completed, valid `10^10` result exists; Q-M008 is exploratory and method-mismatched.
5. Literature searching cannot prove that no unpublished paper exists. The novelty conclusion is therefore “not supported by this evidence,” not a universal negative.

**Disposition:** retain EXP-0008 as a computational result; reclassify its scientific interpretation as an artifact-dominated operational-null rejection; do not promote Q-M007 or Q-M008 to a discovery without a new preregistration and corrected model.
