# NEXT CANDIDATE QUESTIONS — derived from 2026-09-18 session results

These questions arise directly from what we just learned. Each entry
states the parent result that generated it. Status: UNTESTED.

Generated 2026-09-18 from results of Q6/Q6f/Q7/Q8/Q9.

---

## From Q-P005 RESOLVED (percolation exponents — lab CAN measure them)

### Q-P006: Precision study of 2D percolation critical exponents

- **Parent result**: EXP-0009 measured 5 exponents with ~1σ deviations
  on 3 of 5 (D_f, γ/ν, β/ν missed tolerance). EXP-0010 diagnosed the
  deviation as a lattice-size artifact. Q-P005 is RESOLVED — the lab
  CAN measure 2D percolation exponents correctly.
- **What we now know**: The lab pipeline reproduces 2D percolation
  exponents through the audit trail (D_f=1.8962 at non-P2 L vs
  theory 91/48=1.8958). C7 independent implementation works.
- **What remains unknown**: Whether the ~1σ deviations in EXP-0009
  are (a) statistical uncertainty (need larger L / more realizations),
  (b) systematic bias in the estimator, or (c) genuine finite-size
  corrections that persist even at L=1024.
- **Question**: At L ∈ {512, 1024, 2048}, what are the 5 critical
  exponents (D_f, γ/ν, β/ν, τ, 1/ν) with full bootstrap uncertainty
  quantification, and do the ~1σ deviations from theory shrink with L?
- **Hypothesis**: Deviations shrink as L increases (they were
  lattice-size artifacts at small L). At L=2048, all 5 exponents
  should be within tolerance.
- **Falsification test**: If deviations do NOT shrink with L (or
  widen), the lattice-artifact diagnosis is incomplete and there is
  a genuine systematic effect.
- **Computational requirement**: CPU-hours (larger L + more realizations).
  Percolation engine available at `percolation/ENGINE/perc_engine.py`.
- **Method**: Reuse EXP-0009/EXP-0010 machinery (same prereg, same
  gates, same C7). Add L=2048. Bootstrap 2000 draws per exponent.
- **Expected difficulty**: Moderate (CPU-hours at L=2048).

### Q-P007: Generalized lattice-artifact diagnostic (non-P2 sizes for all geometric measurements)

- **Parent result**: EXP-0010 showed D_f at non-P2 L ∈ {127,191,253,449}
  recovers to theory (|dev|=0.0004). But only D_f was tested.
- **What we now know**: Lattice-size discretization affects D_f at
  P2 sizes. The same artifact class caused the optical grid-locking
  at 256² (audit).
- **What remains unknown**: Do γ/ν, β/ν, τ, 1/ν also show P2-specific
  artifacts at the P2 sizes where they missed tolerance in EXP-0009?
- **Question**: Measure γ/ν, β/ν, τ, 1/ν at both P2 and non-P2 L
  values near the P2 sizes where EXP-0009 found deviations. Do the
  non-P2 measurements agree with the P2 measurements?
- **Hypothesis**: If a measurement misses tolerance at P2 L but
  agrees at nearby non-P2 L, it is a lattice artifact (not physics).
- **Falsification test**: If a measurement misses tolerance at BOTH
  P2 and non-P2 L, it is a genuine finite-size correction (need L=2048+).
- **Computational requirement**: Moderate (adds 4 sizes × 5 exponents).

### Q-P008: 3D percolation critical exponents with lab pipeline

- **Parent result**: 2D percolation exponents are reproduced by the
  lab pipeline (Q-P005 resolved). The lab's C7 implementation (pure-Python
  union-find) is efficient enough for 3D.
- **What we now know**: The lab CAN reproduce known 2D exponents.
  The C7 implementation works for 2D site percolation.
- **What remains unknown**: Whether the lab pipeline reproduces 3D
  percolation exponents (known: p_c ≈ 0.3116, 1/ν ≈ 0.88, β/ν ≈ 0.41).
- **Question**: Measure 3D site percolation critical exponents
  (p_c, 1/ν, β/ν, γ/ν) with the lab pipeline and compare against
  published values.
- **Hypothesis**: 3D exponents reproduce within tolerance (the lab
  pipeline works in 3D).
- **Falsification test**: If 3D exponents miss tolerance by >3σ,
  there is a 3D-specific systematic issue.
- **Computational requirement**: High (3D is ~10× more expensive than 2D).
- **Relevance**: Extends the lab's demonstration of controlled
  measurement from 2D to 3D.

---

## From Q-M002 H1_SUPPORTED (prime gaps deviate from Poisson)

### Q-M007: Per-bin residual analysis of prime gap χ² (where exactly is the deviation?)

- **Parent result**: EXP-0008 chi2_red 262→94,633 (B1→B4), all 20
  tail cells significant, deviation in tail shape (lighter than Exp(1)),
  correct mean. BH-FDR rejects G1/G3 at α=0.01 across all 4 blocks.
- **What we now know**: The deviation is in the tail (fewer large
  gaps than Exp(1)). It survives residue-class conditioning in 4/4
  disjoint ranges. C7 agrees perfectly.
- **What remains unknown**: Which specific exponential quantile bins
  carry the deviation? Is it concentrated at the extreme tail (j=9,10)
  or spread across all bins? What is the per-bin effect size?
- **Question**: For each of the 10 exponential quantile bins × 4
  blocks, what is the observed vs expected count, the per-bin χ²
  contribution, the standardized residual, and the BH-FDR-adjusted
  p-value?
- **Hypothesis**: The deviation is concentrated at the extreme tail
  (j=9,10) with smaller bins near the median showing modest excess.
- **Falsification test**: If the deviation is uniformly spread across
  all bins (rather than tail-concentrated), it suggests a different
  generative mechanism than extreme-tail suppression.
- **Computational requirement**: None (re-analysis of existing EXP-0008 data).
- **Relevance**: Pinpoints the exact location of the deviation,
  constraining theoretical explanations.

### Q-M008: Scaling test — does the prime gap deviation persist at 10^9 and 10^10?

- **Parent result**: EXP-0008 tested to 10^8 (4 blocks). Primary gates
  G1 (χ²) and G3 (tail z) rejected after BH-FDR at α=0.01 across all 4 blocks.
- **What we now know**: The deviation is reproducible at 10^8 with
  full controls (BH-FDR, residue conditioning, C7 independent impl).
- **What remains unknown**: Whether the deviation persists at 10^9
  and 10^10, or whether it is a finite-range artifact that disappears
  at larger N.
- **Question**: Run the same test at 10^9 and 10^10. Does the
  deviation persist? Does the effect size change?
- **Hypothesis**: Deviation persists (the prime gap distribution
  has a reproducible deviation from Poisson at all ranges).
- **Falsification test**: If deviation disappears at 10^9 or 10^10,
  the 10^8 result was a finite-range artifact.
- **Computational requirement**: Moderate (sieve to 10^9 is ~10×
  EXP-0008; 10^10 is ~100×). CPU-hours to days.
- **Relevance**: Determines whether the deviation is a real
  asymptotic feature or a finite-range effect.

---

## From §9 battery (perception is statistical, not informational)

### Q-S9-1: Minimum spectral structure for pareidolia detection

- **Parent result**: §9 battery showed A==B (identical power spectrum →
  identical perception). D (Grassmann grating, clear periodic structure)
  had highest "code present" rate (32%). C (pure noise) had lowest (5%).
  A/B (speckle) intermediate (20%).
- **What we now know**: Perception of "code" tracks spectral statistics,
  not information content. More structure → more pareidolia.
- **What remains unknown**: What is the minimum amount of spectral
  structure (number of spectral peaks, spatial frequency, contrast)
  needed for "code present" detection to exceed baseline (5%)?
- **Question**: Generate speckle images with systematically decreasing
  spectral complexity (from full speckle → sparse peaks → single peak
  → flat spectrum). At what complexity threshold does "code present"
  detection rate drop to baseline?
- **Hypothesis**: Detection rate is a monotonic function of some
  spectral complexity measure (e.g., number of significant FFT peaks,
  peak-to-background ratio).
- **Falsification test**: If detection rate is non-monotonic (e.g.,
  moderate complexity gives MORE detection than full speckle),
  the complexity model is wrong.
- **Computational requirement**: Moderate (50–100 images × N subjects).
- **Relevance**: Quantifies the perceptual detection threshold,
  connecting optics to perception.

### Q-S9-2: Dose-response curve for REBUS-induced pareidolia

- **Parent result**: §9 battery showed dose inflates all "code present"
  rates by 46–53% (sober: A=20.5%, B=20.2%, C=4.7%, D=32.0%; dosed:
  A=30.4%, B=30.9%, C=7.1%, D=46.9%). Inflation is consistent across
  conditions (46–53%).
- **What we now know**: DMT/REBUS inflates pareidolia by ~50% across
  all stimulus types. The inflation factor is independent of stimulus.
- **What remains unknown**: Is the dose-response curve linear? What
  is the EC50? Is there a threshold? What about interaction effects
  between dose and stimulus complexity?
- **Question**: Simulate dose-response curves for 0%, 10%, 20%, ...,
  100% DMT intensity. Fit a Hill equation. What is the EC50 and
  maximum inflation factor?
- **Hypothesis**: Dose-response follows a Hill equation with
  EC50 ≈ 30–50% DMT intensity and maximum inflation ≈ 50–80%.
- **Falsification test**: If the dose-response is not sigmoidal
  (e.g., linear, or has no clear EC50), the pharmacodynamic model
  is wrong.
- **Computational requirement**: Low (parametric simulation).
- **Relevance**: First quantitative pharmacodynamic model of
  REBUS-induced pareidolia.

### Q-S9-3: Detector de-biasing — can we build a pareidolia-immune "code" detector?

- **Parent result**: A==B (statistics drive perception). The audit
  showed the DeepBeamScan detector reports "structure" for random
  input (D01) at Phase-17 FP rate. Matched-spectrum surrogates (D02)
  produce identical detection.
- **What we now know**: Both human pareidolia and detector "structure"
  detection are driven by spectral statistics, not information content.
- **What remains unknown**: Can we build a detector that reports
  "code present" ONLY when there is genuine decodable information
  (i.e., immune to statistical pareidolia)?
- **Question**: Design and simulate a "de-biased" detector that
  uses information-theoretic measures (e.g., compression ratio,
  mutual information with a known message) rather than spectral
  statistics. Does it distinguish A from D (speckle vs grating
  with real message)?
- **Hypothesis**: An information-theoretic detector can distinguish
  A (no message) from D (encoded message) where A==B in perception.
- **Falsification test**: If the de-biased detector cannot
  distinguish A from D, there is no detectable information difference
  (the message is an illusion at all levels).
- **Computational requirement**: Moderate (design + simulate).
- **Relevance**: Directly tests whether "code" perception can
  be separated from statistical pareidolia.

### Q-S9-4: §9.8 cone-mosaic aliasing sober check (simulate retinal-sampling artifact)

- **Parent result**: §9.9 simulated. §9.7 wavelength ladder simulated.
  §9.8 (Exp-7 in dossier) is the cone-mosaic aliasing sobriety check:
  present coherent interference fringes above ocular cut-off (~60+ c/deg)
  to sober subjects and ask them to free-draw. Williams' groups showed
  stable "zebra/hexagonal/periodic" percepts with no drug.
- **What we now know**: The lab's ASM/speckle generators can produce
  coherent interference patterns at any spatial frequency. The §9.9
  simulation framework provides perceptual scoring tools.
- **What remains unknown**: How many of the community's reported
  "stable lattice / cathedral cells" drawings are reproduced sober
  by pure retinal-sampling mechanism?
- **Question**: Simulate high-spatial-frequency coherent interference
  fringes (60–120 c/deg) and model the expected "free-draw" responses
  of sober subjects. Compare against the catalogue of reported
  geometric hallucination drawings (Grove et al. 2026, 10,598 drawings).
- **Hypothesis**: Most "stable lattice" drawings can be reproduced
  sober by cone-mosaic aliasing (retinal artifact, not drug).
- **Falsification test**: If sober-draw responses don't match the
  catalogue, the retinal-sampling mechanism is insufficient to
  explain the reports.
- **Computational requirement**: Moderate (fringe generation +
  comparison against catalogue statistics).
- **Relevance**: Tests the simplest explanation for geometric
  hallucinations (no drug needed).

---

## Cross-project (methodology transfer)

### Q-X1: Automated surrogate-null control generation for any detector

- **Parent result**: The audit's CONTROL_MATRIX discipline (D01/D02)
  was successfully transferred to §9 (perceptual) and produced
  decisive results (A==B). The same BH-FDR + effect size + CI
  framework worked for both optics and perception.
- **What we now know**: The surrogate-null discipline is domain-agnostic.
  Any detector that reports "structure" can be controlled by comparing
  against matched-spectrum surrogates + Gaussian noise + structured
  controls.
- **What remains unknown**: Can we automate the generation of
  surrogate-null controls for any new detector/measurement?
- **Question**: Build a generic `surrogate_control` module that takes
  any detector function (black-box), any stimulus, and generates
  the full CONTROL_MATRIX (D01, D02, C01–C25) automatically,
  with BH-FDR + effect sizes + FP CIs.
- **Hypothesis**: Automated control generation produces the same
  verdicts as manual control design for the detectors we've tested.
- **Falsification test**: If automated controls miss a known
  artifact (e.g., the detector is grid-locked), the automation
  is insufficient.
- **Computational requirement**: Moderate (design + validation).
- **Relevance**: Scales the lab's methodology to new detectors
  without manual audit each time.

### Q-X2: Continuous coherence-perception response curve

- **Parent result**: §9 wavelength ladder showed detection tracks
  coherence (hypothesis #2 supported). Only 3 wavelengths tested
  (450, 532, 650 nm).
- **What we now know**: Detection rate is a function of coherence,
  not wavelength per se. The function was only sampled at 3 points.
- **What remains unknown**: What is the functional form of the
  detection-vs-coherence curve? Is it linear? Logarithmic? Sigmoidal?
- **Question**: Measure detection rate at 12+ coherence levels
  (from fully incoherent to fully coherent). Fit the response curve.
  What is the coherence threshold for detection?
- **Hypothesis**: Detection rate follows a sigmoidal function of
  coherence with threshold at mid-coherence (~50% of max).
- **Falsification test**: If the curve is not sigmoidal, the
  coherence model needs revision.
- **Computational requirement**: Low (extend §9 battery with
  more coherence levels).
- **Relevance**: Quantitative model of coherence-dependent
  perception, applicable to both laser safety and perceptual science.
