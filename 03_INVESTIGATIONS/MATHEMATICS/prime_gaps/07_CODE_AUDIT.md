# EXP-0008 Code and Reproducibility Audit

**Scope:** `CODE/run_prime_gaps.py`, `REPLICATION/independent_check.py`, Q-M007, Q-M008, configuration/registry handling, and related project conventions. No canonical source file was modified by this audit.

## 1. Findings by severity

| Severity | Finding | Consequence |
|---|---|---|
| Critical | The operational null assigns positive mass to an impossible first bin because all prime gaps are even and the scale is below the support threshold. | The chi-square rejection is not a Gallagher-model test. |
| High | G1/KS/tail p-values assume i.i.d. observations; the data are deterministic, lattice-valued, and serially/arithmetic dependent. | Nominal p-values are not calibrated scientific p-values. |
| High | C6 uses “no conditioned rejection” as pass and “conditioned rejection” as survival. | The control is logically inverted/ambiguous. |
| High | C7 does not use the preregistered `sympy.primerange`; it uses another custom sieve and the same SciPy KS routine. | Preregistered independent-source requirement is not met. |
| High | Q-M007 is post hoc and converts standardized residuals to p-values with an invalid Wilson–Hilferty implementation. | Its 38/40 cell claim is not valid confirmatory evidence. |
| High | Q-M008 changes the denominator and block structure, uses the old BH implementation, and omits the control suite. | It is not a valid scale replication of EXP-0008. |
| Medium | Tail p-values use a cancellation-prone normal expression and are stored as zero after underflow. | Numerical reporting is inaccurate even where decisions do not change. |
| Medium | The runner overwrites canonical outputs and appends the registry. | Reproduction is not side-effect free. |
| Medium | The “raw” output contains summaries, not record-level gaps. | Independent reanalysis requires rerunning the sieve. |
| Low | Four upper-boundary gaps are omitted despite lower-prime block wording. | Numerically negligible, but protocol inconsistency. |

## 2. Primary runner trace

`CODE/run_prime_gaps.py` implements the following broad sequence:

1. `sieve_primes` builds a deterministic boolean sieve through `10^8`.
2. `compute_block` selects each prime slice and computes `(upper-lower)/log(lower)` (around lines 590–603).
3. `chi2_goF` uses the nine exponential-quantile edges and equal expected count `n/10`.
4. `ks_test` calls the fully specified exponential KS routine.
5. `tail_tests` compares five exceedance counts with a normal/binomial approximation.
6. `bootstrap_means` samples individual gap indices.
7. Local BH code and controls C1–C6 produce the decision inputs.
8. C7 is launched/read through a sidecar.
9. Results, reports, configuration, and a registry row are written.

The arithmetic path is reproducible. The scientific interpretation is not secured by the code.

## 3. Specific implementation defects

### 3.1 Block slicing versus lower-prime assignment

The plan states that a gap belongs to the block containing its lower prime. Selecting `primes[(primes >= lo) & (primes < hi)]` and then taking adjacent entries internally omits the gap from the last prime below each upper boundary. A successor should construct the full prime sequence first, select by `lo <= p_i < hi`, and include `p_{i+1}` even when it lies above `hi`.

### 3.2 Histogram boundary handling

The histogram has no negative observations, so the lower boundary is harmless. The final bin includes all values above `e9`, as intended. Expected counts are exactly `n/10` for the continuous exponential, not for an even-lattice process. Any bin with zero model probability must be excluded or redesigned before inference.

### 3.3 Tail p-value precision

The affected routine uses a normal CDF subtraction for a two-sided p-value. For large `|z|`, subtraction from one loses all meaningful digits. Use `scipy.stats.norm.sf(abs(z))` and store `logp` or a high-precision survival function. The stored zeros are not mathematical zeros.

### 3.4 Bootstrap unit

`bootstrap_means` samples individual observations. It does not preserve:

- overlap of adjacent gaps;
- endpoint congruence;
- local prime-density variation;
- contiguous prime-free intervals.

The seed ladder changes random indices, not the dependence structure. A block bootstrap is a sensitivity analysis, not a replacement for a justified prime-process null.

### 3.5 BH implementation and chronology

The local BH routine was changed after the first run to correct a step-up/indexing issue. The pre-fix and final artifacts preserve different rejection vectors and an `INCONCLUSIVE` versus `H1_SUPPORTED` decision. The corrected implementation is preferable, but the project changelog does not fully record the change, and both registry rows point to the same mutable canonical result path.

A successor should use the shared corrected implementation, record source and result hashes, and make an immutable run directory before the first execution.

## 4. Controls

### C1 and C2

The documents say the identical chi-square/KS/tail pipeline is run, but the stored pass/fail logic is primarily based on chi-square p-values. C1 is an i.i.d. `Exp(1)` calibration check, not a prime-dependence calibration check. C2’s Gamma(shape=0.5, scale=2) is a gross positive control; it shows sensitivity to a large variance difference, not validity of the Gallagher null.

### C3

The seed ladder reruns bootstrap intervals, not the full H0/H1 decision. The primary seed is not cleanly included in the equality comparison. It does not address dependence.

### C4 and C5

Changing `J` and comparing chi-square/KS rejection vectors is useful implementation sensitivity, but all tests can agree while sharing the same wrong null. Agreement is not calibration.

### C6

The implementation computes conditioned chi-square tests by lower-prime residue. It sets `C6_pass` from the absence of conditioned rejection, but the H1 branch counts conditioned rejection as survival. In the final record all 16 conditioned cells reject, `C6_pass=false`, and `survives_in_ranges=4`. This is a semantic contradiction, not a robust residue model.

A proper successor should predefine either:

- a residue-aware null with expected probabilities for each class; or
- a heterogeneity statistic comparing residue effects, with a single direction and one decision rule.

### C7

The frozen preregistration requires `sympy.primerange`, a different binning scheme, and a separate statistical route. The actual file uses a pure-Python segmented sieve, uses `scipy.stats.chisquare`/`kstest`, and instantiates but does not use its claimed RNG label. The equal-width analysis is useful; the exact same-bin vector match is an arithmetic check using the same deterministic data, not an independent scientific replication. The referenced `state/EXP-0008_decisions.md` is absent.

## 5. Q-M007

`Q-M007/compute_bhfr_40cell.py` was written after the parent result and the per-bin pattern were already known. It forms a cell statistic from standardized residuals and then uses a purported one-degree-of-freedom chi-square conversion. The implementation uses an incorrect sixth-root Wilson–Hilferty expression rather than the one-degree-of-freedom transform; the exact one-df survival is available directly from `erfc(sqrt(chi2/2))`.

The 40 cells are nested multinomial histogram cells, not independent hypotheses. Equal-weight averaging of block residuals gives B1 the same nominal weight as B4 despite a 609-fold sample-size difference. The report’s “38/40 significant” result must be treated as exploratory, not confirmatory.

## 6. Q-M008

`Q-M008/CODE/run_exp0012.py` differs from EXP-0008 in at least four material ways:

1. the code divides by `log(upper_prime)` while the report says lower prime;
2. blocks are scaled nondecade intervals rather than the frozen four decade blocks;
3. BH code is the older non-step-up implementation;
4. C1–C7, bootstrap, residue conditioning, and the full decision protocol are absent.

At `10^9`, one reported block is effectively the same `10^7–10^8` data already used in EXP-0008 B4. There is no valid completed `10^10` result. Do not use Q-M008 to claim that a deviation persists asymptotically.

## 7. Output and provenance defects

The primary runner writes canonical result/report/config files and appends `CONFIG/registry.jsonl`. `EXP-0008_raw.json` stores computed summaries rather than individual gaps. The project reproducibility contract asks for dataset and result-file hashes, but the recorded result hash is a hash of a serialized result object, not an immutable file manifest. The project is not committed to git in a way that anchors the investigation.

A safe reproduction protocol must copy the investigation to a new directory, run there, preserve input/code hashes, and never append to the live registry.

## 8. Code-audit conclusion

The core arithmetic implementation is sufficiently transparent to reproduce and repair. The current code is not a reliable implementation of a Gallagher-model hypothesis test because it combines a continuous unconditioned null, an impossible bin, i.i.d. p-values, an individual bootstrap, and a contradictory residue control. Code correctness and scientific validity must be reported separately.
