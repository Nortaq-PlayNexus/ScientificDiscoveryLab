# EXP-0008 Mathematical Definition and Data Audit

## 1. Objects

Let `p_1=2, p_2=3, ...` be the primes. EXP-0008 defines a consecutive gap by

\[
d_i=p_{i+1}-p_i,
\qquad
\delta_i=\frac{d_i}{\log p_i}.
\]

The lower prime `p_i` is the normalization location. The project’s preregistration and `EXPERIMENT_PLAN.md` state that blocks are assigned by the lower prime.

The four canonical blocks are:

| Label | Lower-prime interval | Stored internal `n` |
|---|---|---:|
| B1 | `[10^4,10^5)` | 8,362 |
| B2 | `[10^5,10^6)` | 68,905 |
| B3 | `[10^6,10^7)` | 586,080 |
| B4 | `[10^7,10^8)` | 5,096,875 |

The stored total is 5,760,222 gaps.

## 2. Sieve and inclusion convention

The primary runner uses a deterministic NumPy sieve through `N_MAX=100,000,000`; no random prime generation is involved. It then selects primes in each block and forms differences between adjacent entries **within that selected slice**. This is a small implementation mismatch with the stated lower-prime convention: the gap whose lower prime is the final prime below an upper boundary is omitted. Four boundary gaps are omitted relative to the union of the four lower-prime intervals. A complete lower-prime reconstruction that includes the next prime beyond each boundary has one additional gap in B1–B3; the last gap below `10^8` is unavailable without sieving beyond the bound.

The mismatch is numerically negligible for the scientific conclusion, but it should be corrected in any successor protocol.

## 3. Histogram definition

For `J=10`, the internal edges are

\[
e_j=-\log(1-j/10),\quad j=1,\ldots,9,
\]

namely

```text
0.10536051565782628
0.22314355131420970
0.35667494393873245
0.51082562376599070
0.69314718055994530
0.91629073187415500
1.20397280432593600
1.60943791243410050
2.30258509299404600
```

The bins are `[0,e_1)`, `[e_1,e_2)`, …, `[e_9,infinity)`. Under a continuous `Exp(1)` law each has probability `0.1`, so each expected count is `n_b/10`. The code uses nine degrees of freedom per block (`J-1`) and sums the block chi-square values with 36 degrees of freedom for the combined statistic.

The expected counts are correct for the stated *operational* null. They are not automatically correct for a discrete wheel-conditioned prime process.

## 4. Deterministic support constraint

For every prime `p_i>3`, both endpoints are odd, so

\[
d_i\in\{2,4,6,\ldots\},
\qquad
\delta_i\ge \frac{2}{\log p_i}.
\]

All EXP-0008 lower primes satisfy `p_i<10^8`. Therefore

\[
\delta_i > \frac{2}{\log(10^8)}
=0.1085736205,
\]

whereas the first edge is `0.1053605157`. Equivalently, an even gap of 2 can enter the first bin only if

\[
p>\exp(2/e_1)=175,376,063.77.
\]

Thus the first bin is impossible for every observation in the experiment. The observed first-bin counts are exactly zero in B1–B4, while the continuous-exponential expected counts are 836.2, 6,890.5, 58,608.0, and 509,687.5.

This is not a floating-point or random fluctuation. It is a support incompatibility between an even-integer sequence and a continuous model.

## 5. Stored descriptive statistics

| Block | `n` | mean `delta` | sample SD | chi-square / 9 | KS D | nominal KS p |
|---|---:|---:|---:|---:|---:|---:|
| B1 | 8,362 | 1.002428 | 0.763163 | 261.9793 | 0.171668 | `6.15e-216` |
| B2 | 68,905 | 1.001326 | 0.803721 | 1,390.8532 | 0.150944 | underflow |
| B3 | 586,080 | 1.000359 | 0.832889 | 11,705.2966 | 0.137995 | underflow |
| B4 | 5,096,875 | 1.000081 | 0.850530 | 94,632.9846 | 0.128300 | underflow |

The combined nominal statistic is

\[
X^2=971,920.0236,\quad df=36,\quad X^2/df=26,997.7784.
\]

The stored p-value is displayed as zero because of floating-point underflow, not because the mathematical probability is exactly zero.

## 6. Gates and statistics

- **G1:** ten-bin chi-square goodness-of-fit versus `Exp(1)`, BH-FDR across four blocks.
- **G2:** i.i.d. percentile bootstrap CI for the mean.
- **G3:** binomial/normal-approximation tail tests at `t=1,2,3,4,5`, BH-FDR across 20 cells.
- **G4:** agreement between chi-square and KS rejection vectors, not a requirement that either test pass.
- **C1:** i.i.d. `Exp(1)` null surrogate.
- **C2:** mean-one, variance-four Gamma positive surrogate.
- **C3:** bootstrap seed ladder.
- **C4:** `J=8,10,12` resolution variation.
- **C5:** chi-square/KS method agreement.
- **C6:** lower-prime modulo-12 split with internally inconsistent pass/survival logic.
- **C7:** separate implementation cross-check.

The final mechanical decision is H1_SUPPORTED because G1 and G3 reject, the C6 survival count is 4, and C7 agrees. This does not mean that all controls passed: C6 is recorded as FAIL and G2 passes.

## 7. Scale and denominator consistency

Q-M008 is not a literal extension of this definition. Its code divides by the upper prime, uses different blocks, and does not implement the full EXP-0008 control suite. Q-M008 therefore cannot be used as a clean scale confirmation of the same statistic. Its first-bin behavior at `10^9` is consistent with the support threshold above, which is a useful diagnostic rather than evidence for a new law.

## 8. Correct formulation for a successor

A successor should state all of the following before looking at results:

1. lower-prime versus upper-prime normalization;
2. whether a gap crossing an upper boundary is included;
3. the arithmetic support and wheel modulus;
4. conditional endpoint/residue predictions;
5. the dependence unit for resampling;
6. a null that has positive probability in every bin;
7. exact/simulated p-value calibration rather than normal-tail underflow;
8. the primary effect size and its scale dependence.

The current EXP-0008 statistic is precisely defined as a computational pipeline, but its operational `Exp(1)` null is not a complete model of consecutive prime gaps.
