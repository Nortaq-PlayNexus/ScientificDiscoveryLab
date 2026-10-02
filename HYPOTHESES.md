# HYPOTHESES

Master registry of hypotheses. IDs: `HYP-####`. Linked to questions (`Q-####`) and
experiments (`EXP-####`).

Status values:

- `FORMULATED` — hypothesis written but untested
- `PREREGISTERED` — test plan frozen before running
- `TESTING` — experiments running
- `SURVIVED_CONTROLS` — passed its stated controls, not yet independently reproduced
- `FAILED` — falsified by evidence
- `INCONCLUSIVE` — evidence so far does not decide
- `WITHDRAWN` — abandoned for written reasons

## Hypothesis table

| ID | Question | Hypothesis | Status | Evidence |
|---|---|---|---|---|
| HYP-INFRA | Q-INFRA | Shared engine behaves as specified (RNG/BH-FDR/surrogate/template) | SURVIVED_CONTROLS | EXP-0001 14/14 |
| HYP-001 | Q-O001 | C(M) = 1/sqrt(M) within MC error; deviations shrink with N | SURVIVED_CONTROLS | EXP-0002 (H1 supported) |
| HYP-002 | Q-O002 | Vortex density n = <|dE/dx|^2>/(2π<|E|^2>) (Kac-Rice/Nye-Berry) for well-resolved isotropic Gaussian fields; counter is shift-invariant | SURVIVED_CONTROLS | EXP-0003 (H0 supported; C6 independent route within 5%) |
| HYP-003 | Q-I004 | Lab RNG (sha256-derived PCG64) passes a lightweight standard battery at lab stream lengths; battery calibrated on known-good generators | SURVIVED_CONTROLS | EXP-0004 CERTIFIED (KS uniformity + binomial band + BH-FDR; C7 independent re-implementation agrees 30/30) |
| HYP-004 | Q-P004 | Bond and site percolation thresholds on the square lattice, measured with the lab's controlled pipeline (spanning + torus-wrap estimators, fixed-exponent FSS), match published anchors within tolerance | H0_SUPPORTED | EXP-0005+EXP-0006+EXP-0007: threshold reproduced across all three estimators (|d| ≤ 0.0013 for bond_span/bond_wrap/site_span); EXP-0007 resolved the sole failing gate (FG bond_wrap chi2_red 4.738→2.239) by extending to L=96/128/192; width-route diagnostic C8 consistent (1/nu 0.7375 bond_span, 0.7255 bond_wrap). C1/C4/C6/C7/C8/FG/in_tol all PASS. Evidence CONTROLLED. |
| HYP-OPT-DVB-001 | Q-O006 | Discrete optical-vortex count bias is a reproducible function of sampling, contour geometry, padding, propagation, and detector definition; it can be separated from propagation error by oversample→downsample | INCONCLUSIVE / LEVEL 1 | EXP-0015 primary controls, 2048² references, nulls, seed/detector-size sweeps, and independent implementations reproduce known numerical failure modes; no physical anomaly survives |
| HYP-M005 | Q-M005 | delta_n converges to z-dependent universal constants for maps f(x) = 1-a|x|^z | SURVIVED_CONTROLS (z=2) | EXP-0014: delta_n converges to 4.6692016091029 for z=2 (|dev| at n=8: 1.4e-4), all 7 controls PASS. z=3,4 partial. Evidence CONTROLLED. |

| HYP-C001 | Q-C001 | A theory-collapsed aggregator over the 14 Butlin et al. indicator properties can be built that ranks human > machine, is not materially raised by fluent self-report, returns a bounded credence with decomposable interval, and is measurable against reference systems before application | SURVIVED_CONTROLS | EXP-C001: calibration 6/6 anchors (human 1.000, lookup 0.024, adversarial fluent-liar 0.107 vs ceiling 0.15), 48/48 tests PASS (19 instrument + 11 robustness + 10 F08-F10 regression + 8 integrity). F1-F6 falsification conditions all satisfied. EVIDENCE IS L1 INSTRUMENT ONLY — no AI system scored, no claim about any system's consciousness. F01 (temperature chosen by sweep over own anchors) UNRESOLVED and disqualifies absolute credences as measurements. PRE-RELEASE REVIEW FIXED F08-F10 (calibration gate could not report failure; duplicate check unreachable; one perturbation family inert) - results regenerated, hashes now b953b817/1249a0ac, headline conclusions unchanged. PUBLISHED: github.com/Nortaq-PlayNexus/consciousness-indicator-battery, CI 7/7 green |

| HYP-C001-R | Q-C001 | Joint perturbation of all discretionary parameters leaves the battery's ordering and its fluency-vs-architecture separation intact, while absolute credences do not survive | PARTIALLY_CONFIRMED | EXP-C003 (1500 draws x 2 regions, seed 0). F-B (adversarial fluent-liar < human) = 1.0000 in BOTH regions, incl. temperatures 0.02-3.0 and evidence scales that invert CONTROLLED>REPLICATED. F-A exact ordering = 1.0000 plausible, 0.6413 aggressive. F-C absolute ceiling fails aggressive (0.7687); adversarial p05-p95 = [0.027, 0.506] straddles it. AUTHORISES RANKING under shared assumptions; does NOT authorise absolute probabilities. Conditional on lab-chosen anchor assignments — F01 OPEN. |

Notes: HYP-C001 is an INSTRUMENT claim, not a scientific claim about consciousness. Its calibration is self-consistent only: `_SOFT_OR_TEMPERATURE` was selected by sweeping the anchors it is then validated against, and the anchor bands are lab assumptions. Relative comparisons under shared assumptions are the only defensible output until F01 is resolved by independent elicitation.

Notes: HYP-C001-R is the one L2 (statistical) result in this investigation — "no parameter setting tried lets the fluent-liar anchor outscore the human" is falsifiable by exhibiting a counterexample. It is conditional on the anchor assignments, which remain lab assumptions, so it bounds F01's importance without resolving F01. Two gate bugs found while running it (F05 partial EXPECTED_ORDER reporting itself as falsification; F06 all_gates_pass discarding a robust result) — see FALSIFICATION/F05_F06_robustness.md.

Notes: HYP-002 is a reproduction claim about a known law, not a novelty claim. Its
secondary characterisation (near-Nyquist failure zone) is descriptive. Registration of
HYP-002 in QUESTIONS.md/HYPOTHESES.md predates EXP-0003 execution.

HYP-003 is a calibration certificate, not a discovery claim and not "certified by
NIST". Its statements, tests, and thresholds were frozen in
`CONFIG/prereg_EXP-0004.json` and the investigation's HYPOTHESIS.md/EXPERIMENT_PLAN.md
before execution; this top-level table row was added after execution.

## 2026-09-24 audit supersession

The historical EXP-0004/HYP-003 `CERTIFIED` row is withdrawn as a current
conclusion: its pooled decision depended on unsupported independence among
shared-stream p-values. The isolated N-004 repair at
`03_INVESTIGATIONS/OTHER/rng_certification/AUDIT_REPAIR_N004_RNG_CALIBRATION/`
is smoke-only and makes no certification or scientific claim.