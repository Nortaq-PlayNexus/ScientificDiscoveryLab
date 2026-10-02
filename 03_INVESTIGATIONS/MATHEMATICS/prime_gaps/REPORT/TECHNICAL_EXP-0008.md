# TECHNICAL_EXP-0008 — prime gaps vs Poisson/Gallagher (Q-M002, HYP-005)

Experiment: EXP-0008 | Question: Q-M002 | Hypothesis: HYP-005 | Decision: **H1_SUPPORTED**
Prereg: C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\MATHEMATICS\prime_gaps\CONFIG\prereg_EXP-0008.json (sha256 076667a54d12fa49...) | Seed: 42 | Alpha (BH-FDR): 0.01 | Run: 2248.53s

## Primary result

Normalized prime gaps `delta = (p_{i+1} - p_i) / ln(p_i)` in four disjoint ranges below 10^8 — null hypothesis H0 is Exp(1) (Gallagher/Poisson, 1976).

| block | range | n | mean(delta) | std | chi2_red | chi2_p | KS_p | CI95 mean |
|---|---|---:|---:|---:|---:|---:|---:|---|
| B1 | [10000, 100000) | 8362 | 1.002428 | 0.763163 | 261.9793 | 0 | 6.145e-216 | [0.98630, 1.01873] |
| B2 | [100000, 1000000) | 68905 | 1.001326 | 0.803721 | 1390.8532 | 0 | 0 | [0.99534, 1.00734] |
| B3 | [1000000, 10000000) | 586080 | 1.000359 | 0.832889 | 11705.2966 | 0 | 0 | [0.99822, 1.00251] |
| B4 | [10000000, 100000000) | 5096875 | 1.000081 | 0.850530 | 94632.9846 | 0 | 0 | [0.99934, 1.00082] |

Combined chi2 = 971920.0236 (dof 36, chi2_red = 26997.7784, p = 0).

## Every gate
- **G1**: FAIL
- **G2**: PASS
- **G3**: FAIL
- **G4**: PASS
- **C1**: PASS
- **C2**: PASS
- **C3**: PASS
- **C4**: PASS
- **C5**: PASS
- **C6**: FAIL
- **C7**: PASS

## Every control

- **C1_null_random**: PASS — no significant block (calibration)
- **C2_positive_control**: PASS — at least one significant block (validates gate power)
- **C3_seed_ladder**: PASS — identical per-block verdict across seeds
- **C4_resolution_variation**: PASS — identical verdict across J
- **C5_method_agreement**: PASS — chi2 vs KS agree after BH-FDR
- **C6_residue_conditioning**: FAIL — no significant deviation after conditioning
- **C7 independent replication**: PASS

## Tail survival P(delta > t) vs exp(-t) (BH-FDR across 20 cells)

| block | t | observed | expected | z | p | sig after FDR |
|---|---:|---:|---:|---:|---:|---|
| B1 | 1 | 3332 | 3076.2 | 5.801 | 6.604e-09 | True |
| B1 | 2 | 866 | 1131.7 | -8.493 | 0 | True |
| B1 | 3 | 205 | 416.3 | -10.625 | 0 | True |
| B1 | 4 | 39 | 153.2 | -9.310 | 0 | True |
| B1 | 5 | 13 | 56.3 | -5.794 | 6.88e-09 | True |
| B2 | 1 | 25966 | 25348.7 | 4.876 | 1.081e-06 | True |
| B2 | 2 | 7603 | 9325.3 | -19.180 | 0 | True |
| B2 | 3 | 2037 | 3430.6 | -24.408 | 0 | True |
| B2 | 4 | 521 | 1262.0 | -21.053 | 0 | True |
| B2 | 5 | 131 | 464.3 | -15.520 | 0 | True |
| B3 | 1 | 223727 | 215606.8 | 21.996 | 0 | True |
| B3 | 2 | 64392 | 79317.3 | -56.992 | 0 | True |
| B3 | 3 | 18824 | 29179.2 | -62.189 | 0 | True |
| B3 | 4 | 5287 | 10734.4 | -53.066 | 0 | True |
| B3 | 5 | 1427 | 3949.0 | -40.269 | 0 | True |
| B4 | 1 | 1951094 | 1875035.5 | 69.862 | 0 | True |
| B4 | 2 | 586417 | 689787.0 | -133.848 | 0 | True |
| B4 | 3 | 174682 | 253758.5 | -161.037 | 0 | True |
| B4 | 4 | 49257 | 93352.5 | -145.662 | 0 | True |
| B4 | 5 | 13963 | 34342.5 | -110.343 | 0 | True |

## Falsification result

G1/G2/G3 rejected and the deviation survives residue-class conditioning in 4 disjoint ranges; C7 agrees -> reproducible deviation.
Falsification protocol: FALSIFICATION/planning_checks.md.

## Separated diagnostics (report-only, not gates)

- primes found: 5,761,455; sieve time: 0.8938s (deterministic; RNG unused).
- prereg sha256: 076667a54d12fa495dee8ee7ee246203e92c59a35bd012bebb72ead075b24336
- C7 uses an equal-width GOF for its independent verdict and a same-binning (exponential-quantile) vector for the tabulated 1e-9 tolerance (see state/EXP-0008_decisions.md for the prereg-contradiction resolution).
- No evidence state above CONTROLLED; no novelty claimed.
