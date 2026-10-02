# DISCOVERY_LOG

Chronological log of notable developments in this laboratory.

Rules:

- Every entry is a fact about what the lab did or found, never a hype claim.
- Interesting results are logged with their current evidence state, not as discoveries.
- Failed controls and falsifications are logged with the same weight as positives.

Format:

```
## YYYY-MM-DD — short title

- What was done
- What was found
- Evidence state
- What remains / next step
```

---

## 2026-09-17 — Second real experiment (EXP-0003, Q-O002 vortex density)

- Ran the vortex-density experiment end-to-end: preregistration -> narrow-band k0
  ladder (N in {256,512,1024}) + Gaussian bandwidth ladder -> two independent
  detectors -> bootstrap CIs -> BH-FDR -> shift/charge/amplitude/seed controls ->
  independent plane-wave implementation.
- Found: the Kac-Rice/Nye-Berry prediction n = <|dE/dx|^2>/(2π<|E|^2>) is reproduced
  for well-resolved narrow-band isotropic fields (n_meas/n_pred in [0.9952, 1.0011]
  at N=1024 with ≥8 px/wave; 99% CIs inside ±5%). Charge-neutral; half-pixel shift
  ≤2.1% (no grid-locking). Independent plane-wave route 0.985–0.999.
- Found (characterisation): a near-Nyquist failure zone — broad Gaussian spectra lose
  up to ~17% (winding) / ~24% (contour) of counts at σ_k=0.75, k0=π/2. Both detectors
  show it; attributed to under-resolved high-k structure.
- Process notes (both logged in the investigation's CONFIG/changelog.jsonl):
  (1) the original naive contour detector overcounted ~2.5× (did not verify contour
  intersection) and was replaced by a certified test; (2) the independent
  replication's FFT-moment predictor was biased by spectral leakage for off-grid
  fields and was replaced by the correct mode-weighted predictor. Primary results
  unaffected.
- Evidence state: **CONTROLLED**. No anomaly. No novelty. Known law (Nye & Berry
  1974; Berry 2000; Kac-Rice) plus instrument certification.

## 2026-09-17 — Note: external sandbox run observed (not a lab experiment)

- At session close, two processes were found running the coherent-optics sandbox's
  deferred pre-registered matched-spectrum null:
  `research\next_phase\exp2b_checkpoint_runner.py --null D01 --seed 123 --n 5000`
  (sandbox .venv; started 14:09). This lab did not start it and did not touch the
  sandbox. Recorded here for honesty about "experiments running" on the machine.
  Its results (if any) are the sandbox's, not this lab's, and must not be imported
  without a lab-standard re-derivation (see OPTICS INTEGRATION_PLAN).

## 2026-09-17 — First real experiment (EXP-0002, Q-O001)

- Ran the speckle contrast law end-to-end: preregistration -> measurement grid
  (N in {32,64,128,256}, M in {1,2,4,8,16}) -> bootstrap CIs -> BH-FDR -> KS
  generator check -> seed ladder -> independent implementation.
- Found: C(M)=1/sqrt(M) reproduced (r in [0.984,1.005]); at N=256 all 99% CIs
  contain 1. A single low-resolution cell (N64_M2, r=0.984) is FDR-flagged and is
  consistent with a finite-grid artifact that shrinks with resolution. Independent
  route gives r=1.0000–1.0005.
- Process note: the engine's BH-FDR step-up had an indexing bug (flagged all
  cells); the infra validation suite caught it, it was fixed with a regression
  check, and EXP-0002 was re-run. Both registry rows kept (append-only).
- Evidence state: **CONTROLLED**. No anomaly. No novelty. This is a known law.

## 2026-09-21 — Feigenbaum constants (EXP-0014, Q-M005)

- Created investigation `03_INVESTIGATIONS/MATHEMATICS/feigenbaum_constants/` with preregistration, controls, plan, and code.
- Ran EXP-0014: superstable parameters a_1..a_8 for z=2 via period-verified Brent's method.
- **z=2: CONTROLLED (SUPPORTED)**. delta_n converges to 4.6692016091029:
  - delta_3=4.3857, delta_4=4.6009, delta_5=4.6551, delta_6=4.6661, delta_7=4.6685, delta_8=4.6691
  - |delta_8 - 4.6692016091029| = 1.4e-4
  - All 7 controls PASS (reproduction, monotonicity, seed variation, method variation, resolution variation, precision, independent check)
- z=3,4: delta_3 computed; higher convergence needs refined bracketing (overlapping period-4 root).
- Evidence: CONTROLLED. No anomaly. No novelty. Known-result reproduction (Feigenbaum 1978).
- Reports: REPORT/TECHNICAL_EXP-0014.md, REPORT/PLAIN_EXP-0014.md.

## 2026-09-17 — Laboratory bootstrap

- Created the full folder structure and core documents (README, MASTER_INDEX,
  RESEARCH_RULES, QUESTIONS, HYPOTHESES, EXPERIMENT_REGISTRY, REPRODUCIBILITY,
  CHANGELOG, CURRENT_STATUS scaffolding).
- Wrote 00_FOUNDATION foundations (scientific method, statistics, simulation rules,
  falsification, plain-English terminology).
- Registered 32 candidate questions with full profiles
  (02_CANDIDATE_PROBLEMS/MASTER_CANDIDATES.md) + feasibility groupings.
- Planned integration of the existing coherent-optics sandbox
  (`code\coherent-optical-ai-sandbox`) as `03_INVESTIGATIONS/OPTICS/` —
  integration plan in 03_INVESTIGATIONS/OPTICS/INTEGRATION_PLAN.md (no existing
  files modified).
- Built 04_SHARED_ENGINE `engine` package (utilities, statistics,
  hypothesis_testing, simulation, reproducibility, datasets, visualization).
- Built the dashboard (dashboard.py -> dashboard.html, console report).
- Ran infrastructure validation (EXP-0001): 11/11 checks pass.
- Evidence state: none of this constitutes any scientific claim.

## 2026-09-24 — EXP-0015 discrete-vortex discovery phase started

- Created a preregistered, lab-native investigation at
  `03_INVESTIGATIONS/OPTICS/discrete_vortex_bias/` with analytical known-topology
  controls, four detector definitions, grid/z/padding/wavelength controls,
  matched nulls, and a planned 2048² oversample→downsample test.
- Built a hashable cross-project evidence map and a targeted literature matrix.
  Historical claims remain on audit hold and are not reclassified.
- Calibration exposed a reproducible detector-semantics effect: a charge-+2
  vortex is represented as multiple unit plaquettes by raw winding but as one
  charge-two feature by clustering/contour detectors.
- The first supported-detector calibration was invalid because of a ring-statistic
  implementation defect; the failure and correction are recorded in the
  investigation change log and the failed output is excluded.
- Evidence state: **IN PROGRESS / INCONCLUSIVE**. No novelty or physical claim.

## 2026-09-24 — EXP-0015 partial results and closure of artifact candidate

- Primary square convergence (2,424 rows) and 2048² square oversample→downsample
  controls were invariant for the well-separated four-vortex field.
- A rectangular local-contour excess was killed by a 2048² reference and an
  independently written SciPy contour detector; classified as an implementation
  artifact.
- A close +1/−1 pair's z≈240–320 µm disappearance was reproduced by coarse and
  high-reference paths; classified as consistent with known modeled pair
  annihilation.
- Charge-q and close-pair detector discrepancies were reproduced across
  deterministic seed reruns, exact-zero controls, detector-size sweeps, and
  independent raw-winding checks.
- Six-seed random-field count CVs were generally <10% within a detector, but
  detector means differed strongly; counts are not detector-independent.
- The full dense/random regime map and 50-surrogate matched-null run exceeded
  practical budgets without emitting artifacts; neither is counted as evidence.
- Fail-closed validation passed all principal assertions. Evidence state:
  **LEVEL 1 / known numerical artifact reproduced; no novelty claim.**

## 2026-09-26 — EXP-0017: the power-of-two lattice artifact is not supported

- Ran EXP-0017 (Q-P009, audit finding N-005) end-to-end: preregistration ->
  balanced nested measurement -> three independent cluster-census
  implementations -> null control -> 2-adic ladder -> independent-stream
  cross-check -> pre-registered equivalence test.
- Found: the power-of-two effect on the 2D site cluster-mass exponent is
  **β = −0.0014003**, 90% interval **[−0.003890, +0.000797]**, against a
  pre-registered equivalence margin of ±0.010. D_f is 1.882715 on the
  power-of-two ladder and 1.884116 on the non-power-of-two ladder. The pooled
  absolute D_f is 1.880462 with the textbook 91/48 = 1.895833 inside its 95%
  interval.
- This is **19× smaller than the 0.0265 difference** that EXP-0010 invoked to
  declare a `LATTICE_ARTIFACT`, so power-of-two lattice sizes are removed as an
  explanation for the EXP-0009 vs EXP-0010 gap.
- Found (methodological, self-inflicted, and recorded): the FIRST analysis of
  this same data was invalid. Its local finite-difference estimator divided by
  log(hi/lo) ≈ 1e-3, amplifying noise ~1e3. It was detected by its own
  preregistered null control returning a LARGER value (+0.313) than the primary
  contrast (−0.290), and by ladder slopes that were precise and mutually
  inconsistent (1.106 ± 0.002 vs 3.913 ± 0.055). That analysis returned
  INCONCLUSIVE_BY_RESOLUTION and supported nothing; it is preserved as
  superseded evidence. The replacement estimator was validated on synthetic data
  before adoption, and no measured value was used to select it.
- What remains / next step: this does NOT explain why EXP-0009 landed ~1σ low,
  and does not modify either historical record. The open question is no longer
  "power-of-two artifact?" but "what explains the EXP-0009 point estimate?",
  which needs a powered per-size D_f measurement with the threshold varied as a
  controlled factor.
- Evidence state: **CONTROLLED** for the estimator question. No novelty claim.

## 2026-09-26 — infrastructure blockers found and fixed before any result

- **N-001 production path was structurally unrunnable.** The audit repair runner
  recorded the production preregistration lock by canonical payload hash but
  validated it against the exact file byte hash. Since a frozen document embeds
  its own digest, those can never match, so production failed closed *after*
  doing all the measurement work. Fixed to re-verify the canonical digest;
  regression test added; 15/15 N-001 tests pass; smoke regenerated as
  `SMOKE_N001_V4` (PASS).
- **N-004 family-wise control was mathematically inert.** A "max-T permutation"
  control on p-values can never reject, because the maximum is
  permutation-invariant. A preflight caught it reporting 0.000 family-wise
  rejection for a deliberately broken generator that Holm rejects 12/12. Had it
  shipped, the run would have concluded a blatantly broken generator was fine —
  inverting the audit's central finding. Replaced with Bonferroni (valid under
  arbitrary dependence) before any production data existed.
- Both fixes were made pre-execution and hash-chained. Neither changed a
  preregistered margin, alpha, seed count, or decision rule.
- Evidence state: infrastructure only. No scientific claim.

## 2026-09-28 — the RNG battery's runs test was measuring itself, not the generator

- Audited `T03_runs` in `04_SHARED_ENGINE/engine/validation/rng_battery.py`
  against NIST SP 800-22 Rev. 1a §2.3, prompted by N-004's own note that the
  test was "borderline/unstable".
- Found: the test routes the standard's statistic through `_erfc_p`, the helper
  implementing the `z`-score identity `erfc(|z|/√2) = 2(1−Φ(|z|))`. The helper
  is right for `t_monobit` and `t_dft`, which pass a real `z`-score, but the runs
  statistic is already in `erfc` units, so the helper applies a spurious `√2` and
  inflates every p-value.
- Measured, on 200 fresh G_LAB seeds at 2^18, same streams both ways: shared
  estimator KS p = 6.7e-06 with 0/200 rejections at α=0.01; independent
  reference implementation of the same section KS p = 0.847 with 1/200. At 2^22
  the split is 9.1e-11 / 0 of 200 versus 0.106 / 1 of 200.
- Found: the standard's applicability precondition `|π − ½| ≥ 2/√(n−1)` is
  absent from the shared implementation. It needs a ~4σ deviation in the bit
  balance and is satisfied by 0 of 200 seeds, so the test is not applicable at
  these stream lengths independently of the formula error.
- Found in the stored N-004 data: the p-value pile-up is generator-independent.
  It is present in the deliberately broken LCG (KS p = 3.1e-08), and `T03_runs`
  rejects at α = 0.01 for none of the four generators. The broken generator's
  apparent "detection" was the test noticing its own defect.
- Superseded: the N-004 per-test statement that 0 of 24 tests were miscalibrated
  for G_LAB. Not overturned: the family-level `BATTERY_VALID` verdict, which
  depends on the positive control being rejected by other tests. The EXP-0004
  certificate stays withdrawn.
- Process: the shared battery module was **not** edited, and the audit fails
  closed unless its SHA-256 still matches the digest recorded in the N-004 raw
  database. Raw artifacts, the 2026-09-24 baseline, and every historical registry
  row are unmodified; the supersession is a hash-chained entry
  (`559358ce…`) appended to the N-004 production change log.
- Evidence state: **instrument calibration, not a physical result.** No
  generator is certified. A defective instrument is not evidence that G_LAB is
  defective; the reverse is the finding.
- Also this session: the read-only 2D percolation audit's whole-file pin on
  `EXPERIMENT_REGISTRY.md` was replaced by a frozen historical-prefix pin whose
  digest must equal the baseline's whole-file digest. No baseline was refreshed.
  Suite went from 391 passed / 10 errors to **440 passed / 0 errors**, with 27
  tests proving the replacement control still fails closed on a one-byte change
  anywhere in the audited region.

## 2026-09-28 (later) — the T03 cell re-derived, and the whole helper audited

- Re-derived the single N-004 T03_runs cell for G_LAB under three variants,
  all evaluated on **identical** bit streams so the differences are properties of
  the estimator and not of the generator.
- Found: the spurious sqrt(2) explains the **entire** recorded non-uniformity.
  As-implemented KS p = 1.4e-05 at 2^18 and 8.8e-06 at 2^22; with the sqrt(2)
  removed, KS p = 0.343 and 0.956, and the corrected mean p sits within 0.01 of
  the uniform mean.
- Found: even corrected, the test is **not scorable** at these lengths. The
  standard's applicability precondition |pi - 1/2| >= 2/sqrt(n-1) is met by
  **0 of 200 seeds** at both 2^18 and 2^22, because it demands a roughly
  four-sigma deviation in the bit balance while a fair stream deviates 0.0008
  against a 0.0039 threshold.
- **Corrected status of record:**
  UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION at both lengths. Corrected
  N-004 statement: **23 of 24** per-test cells calibrated, 0 miscalibrated, 1
  unresolvable. Not “calibrated”, and explicitly not reported as agreement.
- Found (by auditing rather than assuming): exactly one of the five _erfc_p
  callers passes an erfc-unit argument. 	_monobit, 	_dft, 	_nontemplate and
  	_autocorr pass genuine z-scores and are empirically uniform at both lengths,
  so the helper is correct for them and T03_runs is the sole defect.
- Recorded a limit on my own finding: the extra sqrt(2) is provable as an exact
  algebraic identity, but its empirical **detection** is resolution- and
  seed-dependent. With 200 seeds it was caught at 2^18 and missed at 2^22 under
  one seed labelling, then caught at both under another. Non-detection is never
  read as correctness, and the classification rests on the identity.
- Two fail-open defects of my own, introduced and fixed during this work and
  recorded rather than hidden: the caller audit first reported the
  autocorrelation cell CONFIRMED_CALIBRATED while having measured zero
  p-values, because an absent measurement was read as a pass, and its pooled key
  set never resolved. The audit now raises on a declared key that is not
  collected and classifies an unmeasurable cell UNRESOLVED_NO_MEASUREMENT.
- Evidence state: **instrument calibration, not a physical result.** No generator
  certified; the EXP-0004 certificate stays withdrawn; the N-004 family-level
  BATTERY_VALID verdict is untouched.

## 2026-09-28 (later) — the N-001 deviation is not finite-size drift, and the estimator that measured it is biased upward

- Two diagnostics on the already-stored N-001 production arrays, generating **no
  new Monte Carlo**. The production kept one cluster-size array per realization at
  L = 256, 512 and 1024, so the per-size question never needed a simulation.
- **Found: the deviation is not finite-size crossover.** The preregistered,
  theory-derived prediction (a periodic box has p_c(L) above the infinite-volume
  value, so the sampled box sits slightly disordered and tau must rise with L) is
  **violated**: tau = 1.90306, 1.88981, 1.92009 at L = 256, 512, 1024. The fitted
  slope is +0.0123 per ln L with a 95% interval [-0.0232, +0.0478] that includes
  zero, and the deviation from 187/91 is nearly size-independent at -0.152, -0.165
  and -0.135. A shrinking offset is the crossover signature; a constant offset is
  not. Classification **`CROSSOVER_NOT_ESTABLISHED`**. This does not resolve
  Q-P007, but it removes the most comfortable explanation.
- **Found: the production estimator is biased.** Building synthetic distributions
  of a known exponent and measuring each estimator's error shows the frozen N-001
  cumulative estimator returns values **+0.11 to +0.35 too large**, reproducibly
  across three independent constructions and both tested true exponents, while the
  histogram estimator is unbiased to within 0.008. The histogram estimator is
  therefore the yardstick.
- **Two candidate mechanisms tested and rejected, both recorded.** The off-by-one
  in the survivor count was the first hypothesis; fixing it made the bias slightly
  *worse*, so it is not the cause. The residual weighting was the second;
  unweighted OLS was worse still, and the statistically correct Poisson weight
  reduced but did not remove the bias. Neither was quietly adopted.
- **The correction strengthens the deviation.** The bias is consistent for true
  exponents 1.85 and 2.05, so the preregistered rule permits a clearly labelled
  secondary estimate: the stored 1.92009 corresponds to about **1.81**, and the
  unbiased histogram estimator independently gives **1.70**. Both are **further**
  from 187/91 = 2.054945 than the reported value, and every window under every
  estimator lies below it. So the lab's own instrument bug made its anomaly look
  *smaller* than it is — the opposite of the usual outcome of finding a bug.
- **Not edited:** the frozen production value 1.920086094899, the production
  runner, the 60 MB raw database, and the production decision. The corrected
  figure is a secondary estimate only, and the escalation `DEVIATION_FROM_FISHER`
  stands with its direction strengthened and its magnitude untrusted.
- **Recorded, not corrected:** the production manifest's `pairing` field carries
  stale text `iid_cluster_bootstrap` although the code resamples realization
  blocks; and the status line's "1,462,967 pooled tail clusters" is the active
  L = 1024 size alone, with pooling across all three sizes shifting tau by -0.0115.
- Evidence state: **instrument characterisation plus a diagnostic of an existing
  escalation.** No physics claim, no novelty claim, no new simulation.

## Next steps

- Q-O002 (vortex density law) with matched-spectrum surrogate nulls.
- User review of the candidate shortlist.