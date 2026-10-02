# CURRENT_STATUS

Live state of the AI Scientific Discovery Lab. Updated at the end of every working
session.

Last updated: 2026-09-28 (instrument audit: shared battery `T03_runs` found
defective and its N-004 cell superseded; read-only audit registry pin repaired
without refreshing any baseline)

> **2026-09-28 session summary. Two instrument-level defects were found and
> fixed; no new science was produced and nothing was certified.**
>
> **1. `T03_runs` in the shared RNG battery is `ESTIMATOR_DEFECTIVE`.** It routes
> the NIST SP 800-22 §2.3 statistic through the module's `_erfc_p` helper, which
> is the `z`-score identity `erfc(|z|/√2) = 2(1−Φ(|z|))`. That is correct for
> `t_monobit` and `t_dft`, which really do pass a `z`-score, but the runs
> statistic is already in `erfc` units, so the helper divides by a spurious `√2`
> and the p-values come out too large. On 200 fresh G_LAB seeds at 2^18 the
> shared estimator gives KS p = 6.7e-06 with 0/200 rejections at α = 0.01,
> while an independently written reference implementation of the same section,
> on the **identical** streams, gives KS p = 0.847 with 1/200. The stored N-004
> rows show the same generator-independent pile-up in all four generators
> including the deliberately broken LCG (KS p as low as 3.1e-08) and zero
> rejections anywhere — the test was detecting its own defect, not a generator.
> Separately, the standard's §2.3 step 1 precondition
> `|π − ½| ≥ 2/√(n−1)` is missing from the shared implementation; it requires a
> ~4σ deviation in the bit balance and is met by **0 of 200** seeds, so the test
> is not applicable at these lengths at all.
> **Consequence: the N-004 claim that 0 of 24 tests were miscalibrated for
> G_LAB is wrong for `T03_runs`, and the recorded "borderline/unstable" note is
> now explained. The family-level `BATTERY_VALID` verdict is NOT overturned**,
> because it rests on the positive control being rejected at the family-wise
> level, which the other 23 tests supply. The EXP-0004 certificate stays
> withdrawn; a defective instrument cannot support a certification. The shared
> battery was **not** modified — it is hash-checked at runtime so the audit is
> provably about the code that produced the N-004 numbers. The other 23 per-test
> cells were not re-derived and are neither revalidated nor invalidated.
>
> **2. The read-only 2D percolation audit's registry pin is repaired, and no
> baseline was refreshed.** It pinned `EXPERIMENT_REGISTRY.md` by whole-file
> SHA-256, so it reported 10 errors every time an experiment was registered. The
> 2026-09-24 baseline and its run-manifest digest were left untouched. Instead
> the registry's **historical prefix** is pinned byte-for-byte in a frozen
> artifact whose digest is *required to equal* the baseline's whole-file digest —
> the anti-laundering check that proves the frozen bytes are the originally
> audited content and not a re-freeze of today's file. Editing, reordering,
> deleting or prepending anywhere inside the audited region still fails closed;
> legitimate appends are measured and reported. Verified by 27 tests, including
> that a one-byte flip at four different offsets in the real registry is still
> rejected.
>
> **3. The corrected status of the T03 cell is UNRESOLVED, and the whole
> helper is now audited.** Re-deriving the N-004 T03_runs cell on identical
> streams under three variants: as-implemented KS p = 1.4e-05 (2^18) and 8.8e-06
> (2^22); with the spurious √2 removed, KS p = 0.343 and 0.956. So the √2
> explains the entire recorded non-uniformity. But the standard's applicability
> precondition is met by **0 of 200 seeds at either length**, so the cell cannot
> be scored at all. Corrected N-004 statement: **23 of 24** per-test cells
> calibrated, 0 miscalibrated, 1 unresolvable. All five _erfc_p callers were
> then audited rather than assumed: 	_monobit, 	_dft, 	_nontemplate and
> 	_autocorr pass genuine z-scores and are empirically uniform at both lengths,
> so the helper is correct for them and T03_runs is the sole defect. A limit is
> recorded explicitly: the extra √2 is provable as an exact algebraic identity,
> but its empirical *detection* is resolution- and seed-dependent — it was missed
> at 2^22 under one seed labelling and caught under another — so the
> classification rests on the identity, and non-detection is never read as
> correctness. Two fail-open defects of my own surfaced while building that audit
> (an unmeasured cell reporting CONFIRMED_CALIBRATED, and a pooled key set that
> never resolved) and were fixed, with the audit now raising rather than passing
> an absent measurement.
>
> **4. The N-001 escalation is now better characterised, and the instrument
> behind it turned out to be biased.** Two diagnostics on the already-stored N-001
> arrays, with **no new Monte Carlo**: the production kept one cluster-size array
> per realization at L = 256, 512, 1024, so a per-size analysis needs no
> simulation.
> **(a) CROSSOVER_NOT_ESTABLISHED.** The preregistered directional prediction
> (a periodic box sits slightly disordered, so tau must increase with L) is
> **violated**: tau = 1.90306, 1.88981, 1.92009 at L = 256, 512, 1024. Slope
> +0.0123 with 95% interval [-0.0232, +0.0478], which includes zero, and the
> deviation from 187/91 is nearly size-independent at -0.152, -0.165, -0.135. A
> shrinking offset is the crossover signature; a constant one is not. The fitted
> “required L” of ~1e8 is arithmetic from a null slope, is marked NOT MEANINGFUL,
> and a test forbids quoting it as a system size.
> **(b) The frozen N-001 cumulative estimator is biased UPWARD by +0.11 to
> +0.35**, measured against synthetic distributions of known exponent and
> reproduced across three independent constructions, while the histogram
> estimator is unbiased to within 0.008. Two candidate mechanisms were tested and
> **rejected**: the off-by-one in the survivor count (fixing it made the bias
> slightly worse) and the residual weighting (unweighted OLS was worse still).
> The bias is consistent for true exponents 1.85 and 2.05, so a corrected
> secondary estimate is permitted: the stored 1.92009 corresponds to about 1.81,
> and the unbiased histogram estimator independently gives 1.70.
> **This strengthens the deviation rather than dissolving it** - both corrected
> values are further from 187/91 than the reported one, and every window under
> every estimator lies below it. The production number, runner, raw database and
> decision are all unedited; the corrected figure is a separately labelled
> secondary estimate.
>
> **Suite: 495 passed, 0 errors** (was 391 passed / 10 errors). The registry
> append made at the end of this session did not reintroduce a single error,
> which is the direct check that the pin repair actually works.



> **2026-09-26 session summary.** Three audit leads were worked and all three
> are now closed with preregistered decisions. **EXP-0017 (N-005):
> `LATTICE_ARTIFACT_UNSUPPORTED`** — the power-of-two effect on the 2D site
> cluster-mass exponent is −0.0014 (90% interval [−0.0039, +0.0008]) against a
> preregistered margin of ±0.010, i.e. 19× smaller than the 0.0265 difference
> EXP-0010 invoked. **N-001 production: `DEVIATION_FROM_FISHER`** — τ = 1.92009,
> 95% CI [1.90739, 1.93348], excluding 187/91 by −0.135, consistent across all
> four windows, with the refined p_c ruled out (paired Δ = −0.00003). This is an
> escalation, not a discovery, and the lab's own pre-run documentation of
> finite-size crossover means the design cannot separate crossover from a failure
> of the Fisher exponent. **N-004 production: `BATTERY_VALID`, 0/24 tests
> miscalibrated for G_LAB** at both stream lengths, with the measured reason the
> EXP-0004 certificate had to be withdrawn: 24 tests sharing one stream reject at
> 0.16–0.23 uncorrected against a nominal 0.01, a 12×–41× inflation. Nothing is
> certified and the historical certificate stays withdrawn.
>
> **Three blockers were found and fixed before any result was accepted:** the
> **N-001 production path was structurally unrunnable** (canonical vs byte hash
> scope mismatch); the **N-004 family-wise "max-T permutation" control was
> mathematically inert** (the maximum is permutation-invariant — it reported 0.000
> rejection for a deliberately broken generator, which would have inverted the
> audit's central finding); and the **N-004 runner was fail-open twice** (lost a
> whole generator arm, then wrote a manifest claiming 24,960 rows while storing
> 0). **Two errors of my own in the science were caught by controls and recorded
> rather than hidden:** EXP-0017's first estimator was noise-dominated by ~1e3 and
> was discarded with its output preserved, and a second EXP-0017 variance formula
> over-cancelled the interval by ~3 orders of magnitude before being replaced by a
> paired bootstrap. No novelty is claimed anywhere in this session.

> **2026-09-24 audit-repair warning:** portions of the historical status below
> were superseded by the cross-project audit. In particular, Q-P007's refined
> p-c closure is not accepted, Q-P008's 3D width/p-c/C7 claims are invalid, and
> EXP-0013 never completed. Repaired smoke infrastructure exists, but no new
> production 2D/3D exponent conclusion is authorized. See
> `AUDIT/REPAIR_LOG_20260924.md`, `AUDIT/REPAIR_MANIFEST_20260924.json`, and the two investigation audit-repair reports.

> 2026-09-18 closure check: Q-P004 (percolation) formal conclusion re-verified against the
> actual result files (EXP-0007 results/summary, C7 report 78/78 identical, prereg sha intact,
> all gates PASS in data, p50 re-derived from raw cells). Status UNCHANGED: CLOSED /
> H0_SUPPORTED / CONTROLLED. No re-run performed.



## Session 2026-09-19 (independent verification + documentation)

### Q-P006 audit (numerical verification)
- All prereg parameters verified (L_list, n_real, bootstrap_draws)
- tau calculation VERIFIED (fit_tau_cumulative, tau_fit_range=[32,4096], tau_L=2048)
- All 4 exponents deviate from theory; ABNORMAL confirmed numerically
- tau at 16.7sigma is dominant failure
- R1, R2 scaling relations PASS
- BUG: _cells files saved to wrong directory; COPIED to correct location
- GAP: 1/nu not computed (pass stub); inv_nu_gate never evaluated
- GAP: Gates C1, C6, C7, FG not in results JSON

### Q-P007 Phase 2 (historical run; NOT ACCEPTED after 2026-09-24 audit)
- Phase 1 width curves were copied from a log, not a canonical raw artifact.
- The phase-two writer had colliding paths and a structurally empty tail.
- Stored exponent values (historical output, not accepted evidence):
  - D_f = 1.8818 ± 0.0738
  - gamma/nu = 1.7653 ± 0.0995
  - beta/nu = 0.1189 ± 0.0712
- tau: N/A because the stored per-realization tail path was empty.
- **Superseded conclusion:** the refined-p_c closure is INVALID/INCONCLUSIVE.
  Corrected N-001 storage/bootstrap infrastructure has completed smoke only; no
  production tau or exponent decision has been made. Current authoritative
  smoke: `Q-P007/AUDIT_REPAIR_N001/RESULTS/SMOKE_N001_V3`.
- Historical output retained as evidence: `Q-P007/CODE/RESULTS/EXP-0009-pc_results.json`

### Q-M007 audit (numerical verification)
- Chi2 decomposition, residual calculations, normalization: ALL VERIFIED
- H1_SUPPORTED status CONFIRMED
- BH-FDR: primary 20 tail cells all survive; 40-cell grid not BH-FDR adjusted
- C6: deviation survives 4 disjoint ranges

### Q-S9-1, Q-S9-2, Q-S9-3 (historical synthetic/derived outputs)
- The JSON files remain preserved as historical artifacts, but the read-only
  provenance audit classifies them as non-empirical synthetic/derived output.
- Threshold, dose-response, detector-correction, A==B, and wavelength
  interpretations are not current empirical findings; see
  `AUDIT/S9_PROVENANCE_20260924/`.
### Documentation fixes
- Q-P006: QUESTION.md, HYPOTHESIS.md, PREDICTIONS.md, CONTROLS.md, REPORT/ created from frozen prereg
- Q-P007: QUESTION.md, HYPOTHESIS.md, CONTROLS.md created from frozen prereg
- Q-S9-1/3: historical result JSON preserved; current provenance classification is non-empirical
- CHANGELOG.md updated for 2026-09-19
## Historical pre-audit summary (claims retained, not current validation)

The laboratory infrastructure is built and validated, and nine end-to-end
experiments have been completed with controls, independent implementations, and
honest failure documentation:
- EXP-0002 — speckle contrast law (Q-O001).
- EXP-0003 — vortex density in random wave fields (Q-O002).
- EXP-0004 — historical “CERTIFIED” RNG claim; **withdrawn as a certification** because pooled dependence/calibration is unresolved.
- EXP-0005 / EXP-0006 / EXP-0007 — percolation thresholds (Q-P004), **closed
  EXP-0007 as H0_SUPPORTED**: thresholds reproduced, width-route diagnostics
  consistent with the textbook 1/nu~3/4, and the sole previously-failing gate
  (fit-goodness on the torus-wrap estimator) resolved.
- EXP-0008 — prime gaps vs fixed Poisson bins; **DESCRIPTIVE ONLY** after support/dependence audit.
- EXP-0009 — percolation critical exponents (Q-P005), **ABNORMAL**.
- EXP-0010 — non-P2 lattice D_f; historical **LATTICE_ARTIFACT** closure is not accepted under its preregistered per-size/C7 gate.
- EXP-0014 — historical Feigenbaum run; z=2 is reproduced, while historical z=3/z=4 claims remain invalid; isolated N-003 review reports only finite nonmonotone diagnostics.
- Q-P007 — historical refined-p_c diagnostic; **INVALID/INCONCLUSIVE**, with repaired smoke infrastructure only.

No scientific discovery is claimed or implied. These experiments reproduce
known laws / calibrate the lab.

## Active investigations

| Investigation | Question | Status | Evidence |
|---|---|---|---|
| OPTICS / speckle_contrast_law | Q-O001 | COMPLETE (EXP-0002) | CONTROLLED — known law reproduced; low-N grid artifact characterised |
| OPTICS / vortex_density | Q-O002 | COMPLETE (EXP-0003) | CONTROLLED — Kac-Rice/Nye-Berry reproduced (well-resolved); Nyquist failure zone mapped; counter certified not grid-locked |
| OTHER / rng_certification | Q-I004 | **BATTERY_VALID / G_LAB CALIBRATED AT THIS RESOLUTION / CERTIFICATE STILL WITHDRAWN** (N-004 production) | Per-test calibration over 200 seeds at 2^18 and 60 at 2^22, four generators: **0/24 tests miscalibrated for G_LAB at both lengths**; positive control (broken LCG) caught at family-wise rate 1.000; **uncorrected family-wise rate 0.16 to 0.23 vs nominal 0.01 (12x to 41x inflation)**, the measured reason the EXP-0004 certificate had to be withdrawn; `T03_runs` borderline/unstable; nothing certified |
| PHYSICS / percolation | Q-P004 | **SUPPORTED, LIMITED / CONTROL CLOSURE INCOMPLETE** | Stored thresholds are anchor-compatible; EXP-0006 C1/C6 evidence is unavailable; EXP-0007 p_c point is compatible with 0.5 but SE=0.0317, not ±0.01 precision; width CI is broad |
| PHYSICS / percolation exponents | Q-P005 | **HISTORICAL CLOSURE NOT ACCEPTED** | EXP-0009/0010/Q-P007 control/provenance limitations remain; see audit repair log |
| PHYSICS / balanced lattice-size test | Q-P009 (N-005) | **COMPLETE / `LATTICE_ARTIFACT_UNSUPPORTED`** (EXP-0017) | β = −0.0014, 90% CI [−0.0039, +0.0008] vs preregistered margin ±0.010; C7 160/160 and C8 BFS 30/30 cells exact; power-of-two sizes removed as an explanation for the EXP-0009/0010 gap; historical records unmodified |
| PHYSICS / percolation refined-p_c/tau repair | Q-P007 | **PRODUCTION COMPLETE / `DEVIATION_FROM_FISHER` (escalation, not a discovery)** | Frozen pre-run lock `prereg_N001_PRODUCTION.json` (`f5473ff0…`); artifact validation **PASS**; L={256,512,1024}, n={100,100,50}, 50/50 realizations at tau_L=1024, 2000/2000 bootstrap draws, 1,462,967 pooled tail clusters. Primary (cumulative, canonical, s in [32,4096]): **tau = 1.92009, 95% CI [1.90739, 1.93348]**, excluding 187/91 = 2.05495 by -0.13486; all four windows agree. Paired refined-minus-canonical delta = -0.000028, CI [-0.000666, +0.000356] -> **NO_RESOLVABLE_REFINED_EFFECT**. The deviation sits inside the finite-size crossover band the lab documented pre-run, so the design cannot separate crossover from a failure of the Fisher exponent; both remain open |
| MATHEMATICS / prime gaps | Q-M002 | COMPLETE (EXP-0008: H1_SUPPORTED) | CONTROLLED — deviation from Poisson confirmed; C7 perfect match; escalation only |
| MATHEMATICS / prime gap bin analysis | Q-M007 | **COMPLETE** | Per-bin chi2 decomposition: deviation in bins 1,3,5,10. Shape narrower than Exp(1). |
| PHYSICS / 3D percolation | Q-P008 | **INCONCLUSIVE / REPAIRED INFRASTRUCTURE ONLY** | Historical width/p-c/C7 invalid (2D boundaries on cubic labels); corrected `QP008_AUDIT_R1_SMOKE_V4` and source-hash-bound C7 V2 implementation check pass, but no corrected production result. EXP-0013 never completed. |
| MATHEMATICS / Feigenbaum universality | Q-M005 | **CONTROLLED (z=2); z=3/z=4 REPAIR DIAGNOSTIC ONLY** | N-003 repair: z=2 finite reproduction; z=3/z=4 period-certified finite sequences are nonmonotone, no monotone convergence or alpha claim. Historical EXP-0014 remains preserved. |
| PERCEPTION / cone-mosaic aliasing | Q-S9-4 | PLANNED | Prereg draft at 03_INVESTIGATIONS/OTHER/cone_mosaic_aliasing/CONFIG/ |
| MATHEMATICS / prime gaps scaling | Q-M008 | **DESCRIPTIVE ONLY / REPAIR PATH COMPLETE** | Corrected 1e8 support-aware smoke and safe first-segment sieve; no 1e9/1e10 persistence run, calibrated null, or novelty claim |
| OPTICS (coherent-optical-ai-sandbox integration) | — | PLANNED | Integration plan only; sandbox untouched |
| OPTICS / discrete_vortex_bias | Q-O006 | PARTIAL / LEVEL 1 (EXP-0015) | Preregistered controls, convergence, oversampling, nulls, detector-size, tracker, independent checks, and fail-closed validation; known numerical artifacts reproduced, no novelty claim |

## Q-P004 detail (EXP-0005 → EXP-0006)

- EXP-0005 (frozen): INCONCLUSIVE — FG bond_wrap chi2_red 4.738 and C8
  width-route 1/nu=1.2384 failed; both diagnosed as estimator artefacts
  (`DIAGNOSTICS/EXP-0005_width_route_audit.md`); corrected C8 re-fit on same
  cells = 0.7922 (in gate).
- EXP-0006 (this session): fine p-grid at L=256/512 (step 0.004) —
  - C8 width-route **1/nu = 0.7375** (nu=1.3559), gate [0.6,0.9] PASS;
    bootstrap 0.7366 ± 0.0127, 95% CI [0.7124, 0.7608]; identical at
    s0=0.05/0.10, MLE vs linear-WLS agree <1%.
  - p_c estimates: bond_span 0.50021 (±0.014), bond_wrap 0.50122,
    site_span 0.59284 — all within tol 0.01; FSS chi2_red 0.059/4.738/0.974.
  - Gates: C1 PASS, C2 PASS (0.00101), C4 PASS (7.7e-05), C6 PASS (0.00075),
    **C7 PASS** (independent impl, 39/39 cells; newly implemented this session),
    C8 PASS, in_tol PASS; **FG FAIL (bond_wrap only, 4.738)**.
  - Decision per frozen rule: **INCONCLUSIVE**; the only remaining obstruction
    is the small-L torus-wrap FG fit (unchanged from EXP-0005, genuine
    finite-size non-monotonicity at L=32/48/64, not physics).
- EXP-0007 (this session): bond_wrap extended to **L=96/128/192** (n=500/400/300,
  seeds 101/202/303; L=32/48/64 = frozen EXP-0005 cells; 6 sizes total) —
  - **FG bond_wrap RESOLVED: chi2_red 2.239 PASS** (was 4.738 FAIL); p_c =
    0.500687 ± 0.0317, |d| = 0.000687 (in_tol PASS).
  - C8 width-route **1/nu = 0.7255** (nu=1.3783), gate [0.6,0.9] PASS;
    bootstrap mean 0.7478, sd 0.0773, CI [0.6722, 1.0674] (wide CI = coarse
    frozen grid at L=192; diagnostic-only). Agrees with EXP-0006 bond_span 0.7375.
  - Gates: C1 PASS (k=304/304), C4 PASS (shift 0.001111), C6 PASS (max dev
    0.00168 < 0.00412), **C7 PASS (78/78 cells bit-identical, incl. new L=96/128/192)**,
    C8 PASS, FG PASS, in_tol PASS.
  - Decision per frozen rule: **H0_SUPPORTED** — Q-P004 closed. Full report:
    `03_INVESTIGATIONS/PHYSICS/percolation/REPORT/TECHNICAL_EXP-0007.md`.

## Experiments

- **EXP-0001** — infra validation: 11/11 checks pass (later extended to 14/14
  with the RNG battery structural checks). (infrastructure)
- **EXP-0002** — speckle contrast law: H1_SUPPORTED; r=C·sqrt(M) ∈ [0.984, 1.005];
  only FDR-flagged cell = N64_M2 (grid bias, shrinks with N). Independent
  implementation r=1.0000–1.0005. Evidence: CONTROLLED.
- **EXP-0003** — vortex density: H0_SUPPORTED; n_meas/n_pred ∈ [0.9952, 1.0011]
  for narrow-band N=1024 cells with pixels-per-wavelength ≥ 8. Charge-neutral;
  half-pixel shift ≤ 2.1% (no grid-locking); independent plane-wave route
  0.985–0.999. Broadband near-Nyquist deficit mapped. Evidence: CONTROLLED.
- **EXP-0004** — historical RNG certification: **WITHDRAWN**. The stored
  certificate used pooled p-values across shared streams. N-004 now provides
  only an exact historical-matrix replay and bounded plumbing smoke; no
  generator certification or production calibration result is claimed.
- **EXP-0005** — percolation thresholds: INCONCLUSIVE (CONTROLLED). Thresholds
  reproduced within 0.01 for all three systems; two estimator gates failed
  (FG bond_wrap 4.738; C8 1/nu=1.2384). Both diagnosed as estimator artefacts.
- **EXP-0006** — fine-grid width-route follow-up: INCONCLUSIVE (CONTROLLED).
  C8 resolved to 1/nu=0.7375 (gate PASS; bootstrap CI [0.7124,0.7608]).
  Thresholds reproduced (bond_span 0.50021, bond_wrap 0.50122, site_span
  0.59284). C7 independent implementation passes 39/39. Sole gate failure:
  FG on bond_wrap (pre-existing small-L torus-wrap artifact). Full report:
  `03_INVESTIGATIONS/PHYSICS/percolation/REPORT/TECHNICAL_EXP-0006.md`.
- **EXP-0007** — bond_wrap size-extension (L=96/128/192): **H0_SUPPORTED**
  (CONTROLLED). FG bond_wrap resolved (chi2_red 2.239 PASS); p_c=0.500687±0.0317;
  C8 1/nu=0.7255 (gate PASS); C7 independent impl 78/78; all gates PASS.
  Q-P004 closed. Full report:
  `03_INVESTIGATIONS/PHYSICS/percolation/REPORT/TECHNICAL_EXP-0007.md`.
- **EXP-0009** — critical exponents at site p_c (Q-P005): **ABNORMAL**.
  All gates PASS; D_f=1.8697, gamma/nu=1.7596, beta/nu=0.1295 miss
  tolerances by ~1σ; tau=1.9404, 1/nu=0.7434 in window/gate.
  Per frozen rule: escalate, do not tune.
- **EXP-0010** — D_f at non-power-of-2 lattice sizes (Q-P005 follow-up):
  **LATTICE_ARTIFACT**. D_f=1.8962 ± 0.028 at L ∈ {127, 191, 253, 449}
  (theory 1.8958, |dev|=0.0004). Diagnosed EXP-0009 ABNORMAL as a
  lattice-size discretization artifact (same class as optical grid-locking
  at 256²). Q-P005 resolved: 2D percolation exponents ARE reproduced.
- **EXP-0008** — prime gaps vs Poisson/Gallagher (Q-M002): **H1_SUPPORTED**
  (CONTROLLED — escalation, no interpretation). Primary gates G1 (chi2)
  and G3 (tail z) rejected after BH-FDR at alpha=0.01 across all 4 blocks.
  Deviation survives residue-class conditioning in 4/4 disjoint ranges;
  C7 independent implementation agrees block-by-block (perfect match).
  chi2_red 262→94,633 (B1→B4), combined chi2 = 971,920 (dof 36,
  chi2_red = 26,998, p=0). Deviation: lighter tails than Exp(1),
  correct mean. Full report: `REPORT/TECHNICAL_EXP-0008.md`.
- **§9 empirical battery** (Q9, DMT-Laser §9): **SYNTHETIC/DERIVED
  INFRASTRUCTURE ONLY; NOT EMPIRICAL EVIDENCE.** The source audit found seeded
  response simulation, hard-coded rates, and no raw participant/image inputs
  in the declared package. The historical A==B, dose-response, wavelength, and
  biological/perceptual interpretations remain unsupported as empirical claims.
  See `AUDIT/S9_PROVENANCE_20260924/`.
- **Experiments running:** none in the LAB.
- **External (not a lab experiment):** the coherent-optics sandbox thread is CLOSED.
  Not part of this lab; results not imported.

## Infrastructure created / updated

- Percolation investigation (`03_INVESTIGATIONS/PHYSICS/percolation`) with
  preregistrations EXP-0005/0006/0007, runner, stream-layout spec, C7
  independent implementations (EXP-0006 39/39, EXP-0007 78/78), separated
  EXP-0006/0007 summaries, technical/plain reports for all three experiments.

## Candidate questions

32 registered (see QUESTIONS.md). First wave: Q-O001 (done), Q-O002 (done),
Q-I004 (done), Q-P004 (done — H0_SUPPORTED via EXP-0007). Next-wave candidates
for review: Q-M001, Q-M002, Q-M005, Q-M006, Q-P003, Q-C002.

## Known limitations

- CPU-only PyTorch; fluid turbulence (`Q-F001/F002`) and CMB (`Q-A003`) are
  effectively out of reach until CUDA/healpy + data caching exist.
- No pandas/astropy tooling in the lab interpreter.
- No systematic whole-laboratory literature search has been performed; the
  EXP-0003 audit has a scoped search record, and novelty remains unclaimed.
- The lab's strongest reachable state alone is "flag for human scientific review",
  and nothing has come close.

## Next session pointer

0. **Updated 2026-09-28 (later in session) — the T03 question is now CLOSED.**
   T03_runs is DEFECTIVE_BY_ALGEBRAIC_IDENTITY (a spurious √2 on an
   argument already in erfc units) and, independently, **not applicable** at
   laboratory stream lengths under the standard's own precondition, which 0 of
   200 seeds meet. The corrected status of record for that N-004 cell is
   UNRESOLVED_NOT_APPLICABLE_AT_THIS_RESOLUTION at both 2^18 and 2^22. All
   five _erfc_p callers were audited rather than assumed: the other four pass
   genuine z-scores and are empirically uniform, so the helper is correct for
   them and T03_runs is the sole defect.
   **The instrument claim available to the lab is: 23 of 24 per-test cells
   calibrated at these resolutions, 0 miscalibrated, 1 unresolvable, plus the
   family-level BATTERY_VALID verdict. No certification of any kind.**
   Remaining optional work, not required for correctness: re-run the N-004
   per-test table for that one cell with a corrected estimator, purely so the
   historical table is internally consistent. Do NOT edit the historical battery
   module.

1. **N-001 / Q-P007, updated 2026-09-28. Two follow-ups are now CLOSED, both on
   stored data with no new Monte Carlo.** (i) The crossover question is answered
   negatively: CROSSOVER_NOT_ESTABLISHED, because tau does not drift toward
   Fisher with L and the deviation is nearly size-independent. Do NOT re-run N-001
   production - the stored arrays already answer this. (ii) The production
   estimator is ESTIMATOR_BIASED upward by +0.11 to +0.35 depending on window,
   validated on synthetic data of known exponent; the histogram estimator is
   unbiased and is the right yardstick. **Do not quote 1.92009 as a best
   estimate of tau** - quote the deviation as robust in direction and untrusted in
   magnitude. The escalation DEVIATION_FROM_FISHER stands and is strengthened.
   What would actually settle the magnitude is a new production run at L = 2048
   and 4096 using the **unbiased histogram estimator** as primary, with enough
   realizations for a slope interval that excludes zero. That is an expensive
   profile and needs user review before execution.

2. **N-004 / Q-I004 is COMPLETE: `BATTERY_VALID`, 0/24 tests miscalibrated for
   G_LAB at both stream lengths.** The EXP-0004 certificate stays withdrawn and
   is not reinstated. `T03_runs` is borderline/unstable and its p-value formula
   should be checked against the official NIST reference. Resolution is the
   binding limit: nothing below a ~0.04 true rejection rate is detectable at
   S=200.
3. **Q-P009 / EXP-0017 is CLOSED** (`LATTICE_ARTIFACT_UNSUPPORTED`). The
   follow-up worth doing is a powered per-size D_f measurement with the threshold
   varied as a controlled factor. Note EXP-0017 did **not** run the audit's
   requested second-independently-estimated-threshold arm; that remains open.
4. **Q-P008 / 3D:** corrected opposite-plane engine, repaired runner, and C7
   implementation check pass in `QP008_AUDIT_R1_SMOKE_V4`; freeze a separate
   scientific production config before any main run. Historical EXP-0011 p-c/C7
   and incomplete EXP-0013 are not evidence.
5. **Open infrastructure item (not a science result):** the read-only 2D
   percolation audit pins `EXPERIMENT_REGISTRY.md` by whole-file hash, so the
   full suite reports 10 errors (391 passed) whenever a new experiment is
   registered. Verified benign: 50/51 pinned entries are byte-identical to
   `historical_evidence_baseline_post_n14.json` and only the append-only registry
   differs. Fix by pinning the registry's historical content instead of the live
   file — **do not** simply refresh the baseline, which would defeat the control.
6. **Q-M007/Q-M008:** use only the isolated prime-gap audit-repair path; the old
   10^10 segmented sieve must not run.
7. **Q-M005 / N-003:** the isolated high-precision repair review is complete;
   retain its nonmonotone z=3/z=4 limitation and do not replace historical
   EXP-0014 evidence.
8. Review any expensive production profile and scientific decision rule with
   the user before execution. Preregistrations are immutable: if a frozen
   decision rule turns out to rest on a defective estimator, supersede the
   analysis, keep the raw artifact unchanged, and record the substitution in the
   hash-chained change log rather than editing the frozen document.
