# EXP-0008 Independent Reproduction Report

## 1. Scope and safety

The audit reproduced the stored statistics without invoking the canonical runner. This avoided overwriting `RESULTS/`, reports, configuration, and the append-only registry. Independent scripts and intermediate JSON files were written only under:

```text
C:\Users\natha\AppData\Local\Temp\opencode
```

The stored preregistration was not modified.

## 2. Environment

| Item | Value |
|---|---|
| OS | Windows 10 Home 64-bit, 10.0.19045 |
| CPU | Intel Core i7-8700, 6 cores / 12 threads |
| RAM | approximately 24 GiB |
| Python | 3.14.7 |
| NumPy | 2.5.3 |
| SciPy | 1.18.1 |
| SymPy | 1.14.0 |
| Independent prime count through `10^8` | 5,761,455 |

## 3. Independent prime source

An odd-only bytearray sieve was implemented independently of the project’s NumPy boolean sieve and pure-Python segmented sieve. SymPy `primepi` and boundary checks gave:

| Boundary | `pi(x)` |
|---:|---:|
| 10,000 | 1,229 |
| 100,000 | 9,592 |
| 1,000,000 | 78,498 |
| 10,000,000 | 664,579 |
| 100,000,000 | 5,761,455 |

The last prime below `10^8` is 99,999,989; the next is 100,000,007. These values agree with the stored experiment.

## 4. Exact statistical reproduction

| Block | Stored `n` | Independent `n` | Stored mean | Independent mean | Stored SD | Independent SD | Stored chi-square | Independent chi-square |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B1 | 8,362 | 8,362 | 1.0024283204 | 1.0024283204 | 0.7631631469 | 0.7631631469 | 2,357.8134 | 2,357.8134 |
| B2 | 68,905 | 68,905 | 1.0013264433 | 1.0013264433 | 0.8037207091 | 0.8037207091 | 12,517.6792 | 12,517.6792 |
| B3 | 586,080 | 586,080 | 1.0003586722 | 1.0003586722 | 0.8328885509 | 0.8328885509 | 105,347.6695 | 105,347.6695 |
| B4 | 5,096,875 | 5,096,875 | 1.0000812869 | 1.0000812869 | 0.8505295200 | 0.8505295200 | 851,696.8614 | 851,696.8614 |

The combined chi-square is `971,920.0235703` with 36 degrees of freedom. Histogram counts and tail counts also match the stored result. The arithmetic implementation is therefore reproducible.

## 5. Independent lower-prime assignment check

A complete sequence-based lower-prime assignment produces one additional valid gap in each of B1–B3 relative to the stored internal-slice convention. The effect on means and chi-square is below `0.5` per affected block and has no scientific impact. It does confirm the small boundary-convention discrepancy described in `03_MATHEMATICAL_DEFINITION.md`.

## 6. Support reproduction

The independent run confirms:

- `e1 = 0.10536051565782628`;
- minimum raw gap = 2 in every block;
- minimum normalized gap values: 0.17371945, 0.14476526, 0.12408414, 0.10857364;
- zero first-bin observations in all four blocks;
- first-bin expected counts 836.2, 6,890.5, 58,608.0, and 509,687.5.

The support diagnosis is exact and reproducible without stochastic simulation.

## 7. Dependence and alternative diagnostics

The independent run found lag-1 correlations of -0.08949, -0.05245, -0.04538, and -0.03632. Non-overlapping 100-gap cluster intervals for the mean were `[0.99283,1.01203]`, `[0.99696,1.00569]`, `[0.99867,1.00205]`, and `[0.99947,1.00069]`. Thus the mean conclusion survives a basic dependence correction, while the full distribution remains mismatched.

A separate Gaussian-copula calibration simulation produced exact `Exp(1)` marginals with AR(1) dependence. At correlation 0.8, nominal KS rejection rates were 46%, 38%, and 44% for `n=1,000`, `10,000`, and `100,000`, respectively, despite correct marginals. This demonstrates why C1 and conventional p-values do not calibrate a dependent prime sequence.

## 8. C7 assessment

The stored C7 report shows zero same-bin vector difference and an independent equal-width rejection in all four blocks. This is a valid software cross-check of the deterministic prime sequence and basic arithmetic.

It is not a complete independent replication because:

- the preregistration specifically requested `sympy.primerange`, while the implementation uses a custom segmented sieve;
- the same deterministic data and the same SciPy KS routine are used;
- the sidecar supplies the primary verdicts;
- the C7 RNG is not used for the deterministic data;
- the referenced decision-resolution file is missing;
- C7 does not independently rerun the full C6, tail, dependence, or effect-size analyses.

The correct label is **qualified computational replication**, not independent scientific confirmation.

## 9. Reproduction commands

Non-destructive example:

```powershell
$src = 'C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\MATHEMATICS\prime_gaps'
$dst = 'C:\Users\natha\AppData\Local\Temp\opencode\prime_gaps_reproduction'
New-Item -ItemType Directory -Path $dst -Force
Copy-Item -Recurse -Force "$src\*" $dst
Set-Location $dst
python .\CODE\run_prime_gaps.py
```

Before any successor run, capture SHA-256 hashes for the preregistration, source, configuration, and output files. The canonical runner should not be used as a read-only validation command because it writes files and appends the registry.

## 10. Reproduction verdict

| Claim | Independent status |
|---|---|
| Stored counts and statistics | **Reproduced** |
| Literal i.i.d. `Exp(1)` rejection | **Reproduced** |
| Parity/support artifact | **Reproduced and mathematically proven** |
| G2 mean behavior under basic cluster sensitivity | **Supported** |
| C7 scientific independence | **Qualified / incomplete** |
| Gallagher model rejection | **Not tested** |
| Novelty | **Not supported** |
