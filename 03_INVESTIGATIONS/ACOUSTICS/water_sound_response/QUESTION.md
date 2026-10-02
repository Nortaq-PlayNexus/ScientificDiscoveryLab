# QUESTION — How does water respond to sound across frequency?

- QUESTION_ID: Q-AC001
- FIELD: acoustics / fluid physics (water, sound, vibration)
- HYPOTHESIS_ID: HYP-AC001

## Question

Across the audio-to-low-ultrasonic band, does a single physically-parameterised
simulation of water reproduce, within preregistered tolerance, each of the
established quantitative laws governing its response to sound and mechanical
vibration?

Specifically, six sub-questions, each with its own published anchor:

1. **S1 — Bulk propagation speed.** Does the implemented equation of state for the
   speed of sound, c(T, S, P), reproduce the UNESCO (Chen–Millero; Wong–Zhu 1995
   coefficients) surface and the published anchors for fresh water — and do two
   *independent* formulations (UNESCO and Mackenzie 1981) agree to within 0.05 %
   over their common validity range?
2. **S2 — Bounded-column resonance.** Does a driven, damped 1-D water column show
   response peaks at f_n = n·c/(2L) when both ends are rigid and at
   f_n = (2n−1)·c/(4L) when the top is a free (pressure-release) surface — and do
   all peaks scale as 1/L when the column length changes?
3. **S3 — Absorption.** Does simulated propagation decay as e^(−αz) with
   α = 2.50×10⁻¹⁴ f² Np/m for fresh water at 20 °C, i.e. is the log-log slope of
   α vs f equal to 2, and how does the first-principles *classical* value
   (viscosity + thermal conduction, ≈1.1×10⁻¹⁴ s²/m) compare with the measured
   total (2.5×10⁻¹⁴ s²/m)?
4. **S4 — Pressure-node patterning.** Do small suspended particles in a standing
   wave migrate to **pressure nodes** with spacing λ/2 when their acoustic
   contrast factor φ > 0 (polystyrene in water), and to antinodes when φ < 0 —
   with migration speed scaling as a²?
5. **S5 — Bubble response.** Does an air bubble driven by a weak sinusoidal
   pressure field resonate at the Minnaert frequency f₀ = (1/2πR₀)·√(3κP₀/ρ),
   i.e. does f₀ scale as R₀⁻¹ with f₀R₀ ≈ 3 Hz·m, and at what drive amplitude
   does the response cease to be linear and the bubble begin transient
   (free) cavitation?
6. **S6 — Free-surface (Faraday) response.** Does the simulated free surface obey
   ω₀²(k) = (gk + σk³/ρ)·tanh(kh); does a vertically driven layer respond at
   **half** the drive frequency above a threshold (Faraday subharmonic); does the
   measured threshold match Γ_c ≈ 4μ/ω₀ with μ taken from an *independent* free-decay
   measurement; and is the selected surface wavelength the one satisfying
   ω/2 = ω₀(k)?

## Why this question matters

- It is the first question in this lab that asks a simulator to be *jointly*
  faithful to several coupled physical laws, rather than testing one estimator.
  A simulator that passes only S1 but fails S3 is not a usable model of "water
  responding to sound"; only the joint certificate is worth anything.
- Sound-in-water underpins sonar, ultrasound imaging, cleaning, sonochemistry,
  acoustic particle/cell manipulation, and the everyday cymatics demonstration.
  All of the underlying laws are old and well tested — which makes them ideal
  *gates* for an instrument we do not yet have.
- The lab has repeatedly discovered that its instruments fail in specific,
  characterisable ways (grid-locking in the optical vortex counter; lattice-size
  artefacts in percolation exponents). This investigation builds the failure-zone
  map for a wave-propagation simulator *before* anything depends on it.

## What scientists already know

- c(T,S,P) is a fitted empirical surface; the international standard algorithm is
  UNESCO's (Chen & Millero 1977, coefficients recast by Wong & Zhu 1995), valid
  0–40 °C, 0–40 PSU, 0–1000 bar. Mackenzie (1981) gives an independent 9-term
  polynomial in T, S, depth accurate to < 0.1 m/s over 2–30 °C, 0–8000 m.
  Fresh-water anchors: c(0 °C) = 1402.388 m/s (UNESCO check value), c(20 °C) ≈ 1482 m/s.
- A rigid–rigid tube resonates at n·c/2L; a rigid–free (open / free-surface) tube
  at odd multiples of c/4L. This is the classic organ-pipe result applied to a
  liquid column.
- Fresh-water absorption at 20 °C is α = 2.50×10⁻¹⁴ f² Np/m. Classical theory
  (shear viscosity + thermal conduction) predicts only ≈1.1×10⁻¹⁴ s²/m at 280 K;
  the ≈2.3× excess is the well-documented **structural relaxation** of the hydrogen
  bond network (τ_R ≈ 3.5 ps at 4 °C ⇒ f_R ≈ 45 GHz, so no relaxation feature is
  visible in the audio band — absorption simply looks like a clean f² law there).
  Seawater additionally has MgSO₄ and boric-acid relaxations (Thorp, Schulkin–Marsh,
  Fisher–Simmons, Francois–Garrison, Ainslie–McColm). Net effect: water is a
  low-pass channel.
- Gorkov's primary acoustic radiation force drives small spheres to pressure nodes
  or antinodes according to the acoustic contrast
  φ = (5ρ_p−2ρ_f)/(2ρ_p+ρ_f) − β_p/β_f. Polystyrene in water has φ ≈ +0.71 ⇒
  nodes. Force ∝ a³ while Stokes drag ∝ a, so migration speed ∝ a². Streaming
  drag dominates below a few µm; radiation force above ~5 µm at MHz frequencies.
- Minnaert (1933): f₀ = (1/2πR₀)√(3κP₀/ρ) ⇒ f₀R₀ ≈ 3 Hz·m for air in water.
  Transient cavitation requires the local absolute pressure to approach vapour
  pressure, so for a freely suspended bubble the drive amplitude must approach
  P₀ (Blake-threshold regime). Below/above resonance bubbles migrate toward
  antinodes/nodes respectively (primary Bjerknes force).
- Faraday (1831): a layer in a container oscillated vertically
  g(t)=g[1+Γcos ωt] develops standing surface waves above a threshold, responding
  at ω/2 (subharmonic, n=1 Mathieu tongue; Benjamin & Ursell 1954). Linear
  dispersion: ω₀² = (gk+σk³/ρ)tanh(kh). With linear damping μ, Γ_c ≈ 4μ/ω₀.
- Chladni/cymatics patterns are standing-wave nodal structures; recent work
  explains grain accumulation as space-dependent diffusivity (grains random-walk
  faster where the plate vibrates hardest).

## What remains unknown / what we test

- Not the laws themselves — they are settled. What is unknown is whether **our**
  implementation of them is faithful, and precisely where it stops being faithful:
  - discretisation error in the Helmholtz and free-surface solvers (does it shrink
    as dx²?);
  - the exact frequency at which the finite frequency grid misplaces a resonance peak;
  - the point at which the linear driven-bubble model departs from linearity;
  - the extent to which an *inviscid/linear* free-surface model underestimates the
    real Faraday threshold (real thresholds are raised by contact-line and meniscus
    dissipation, which we do not model).

## Known methods

- Finite-difference Helmholtz solve with a complex wavenumber (k + iα) for
  bounded and propagating 1-D problems.
- Complex-frequency / transfer-function peak finding with parabolic
  sub-grid interpolation.
- Analytic Gorkov force + Stokes drag integration (RK4).
- Explicit integration of the driven Rayleigh–Plesset equation.
- Linear potential-flow free surface: cosine (Neumann-wall) modes in the
  horizontal directions with a **finite-difference** vertical Laplace solve — so
  the vertical operator is computed numerically rather than assumed as tanh(kh),
  which keeps the dispersion test non-circular.

## Available data

None external. Everything is synthetic and reproducible from the lab RNG
(`engine.utilities.core.rng`) or fully deterministic. All reference constants are
published literature values quoted in LITERATURE.md.

## Possible experiment

See EXPERIMENT_PLAN.md: freeze a prereg, run six module cells plus controls
C1–C12 (null, positive, seed, resolution, method, boundary, linearity,
grid-shift, contrast-sign, damping, FDR, independent implementation), apply the
frozen decision rule, and write both mandatory reports.

## Null hypothesis (H0)

Each module's simulated output matches its published anchor within the
preregistered tolerance, and every residual shrinks under grid/time-step/step-size
refinement — i.e. the simulator is a faithful, certified model of water's
acoustic response in the stated regime, with residuals attributable to
discretisation.

## Alternative hypothesis (H1-dev)

At least one module shows a residual that (a) exceeds its tolerance and
(b) does **not** shrink under refinement. Such a result is not new physics: per
RESEARCH_RULES §5 it triggers the kill-the-hypothesis battery and is reported as a
controlled deviation or a model limitation — never interpreted.

## Falsification test

- Resolution ladders in every module: residuals must trend to zero as dx, dt, Δf
  shrink. A residual that plateaus is a bug or a model limit, not physics.
- Boundary-condition variation (S2): switching rigid↔free must move the peaks to
  the *predicted* new ladder, not merely shift them arbitrarily.
- Contrast-sign reversal (S4): flipping φ must move particles to the *other*
  set of extrema — a solver that always sends particles to nodes regardless of φ
  is broken.
- Independent vertical solve (S6): dispersion must agree with the numerical
  Laplace solve, not merely with the tanh formula that the code would otherwise
  be testing against itself.
- Independent re-implementation (C12) in REPLICATION/, written from the
  equations by a different route.

## Expected difficulty

Moderate. The physics is standard; the work is in building six modules that are
each individually certifiable and then certifying them jointly without tuning.

## Likely computational cost

CPU-minutes. 1-D Helmholtz solves (thousands of frequencies × ~10²–10⁴ cells),
vectorised Rayleigh–Plesset sweeps, and a small spectral free-surface model.
Nothing here needs CUDA.

## Known pitfalls

- **Circularity** — testing tanh(kh) against a code that computes tanh(kh). Avoided
  by solving Laplace vertically on a grid (S6) and by cross-checking two
  independent sound-speed formulae (S1).
- Peak-picking limited by the frequency step Δf (must be ≪ the resonance spacing;
  parabolic interpolation used and its error reported).
- Imposing α = 2.50×10⁻¹⁴ f² and then "measuring" it back would be circular. The
  measured-decay gate therefore tests **solver fidelity**, while the
  classical-vs-total comparison is reported as a *characterisation* against
  independent literature numbers.
- The linear free-surface model cannot saturate: Faraday amplitude grows without
  bound above threshold. Amplitude is therefore *not* gated — only onset,
  growth-sign, subharmonic ratio and selected wavelength are.
- Reporting an inviscid/νk² threshold as if it were an experimental water
  threshold. It is not: real Γ_c is higher because of contact-line dissipation.
  Disclosed in REPORT/ and in PREDICTIONS.md.
- Treating any of this as a discovery. It is not; see REPORT/.

## Relevant papers

- M. Faraday (1831), Phil. Trans. R. Soc. Lond. — surface patterns of vibrating
  fluids; subharmonic response.
- M. Minnaert (1933), Phil. Mag. 16, 960 — resonance of air bubbles in water.
- T. B. Benjamin & F. Ursell (1954), Proc. R. Soc. A 225, 505 — Mathieu stability
  of the vertically vibrated free surface.
- N. P. Fofonoff & F. J. Millard Jr. (1983), UNESCO Tech. Pap. Mar. Sci. 44 —
  algorithms for seawater properties (sound speed).
- C. T. Chen & F. J. Millero (1977), J. Acoust. Soc. Am. 62, 1129 — speed of
  sound in seawater at high pressures.
- G. S. W. Mackenzie (1981), J. Acoust. Soc. Am. 70, 1322 — 9-term equation for
  sound speed in sea water.
- R. E. Francois & G. R. Garrison (1982), J. Acoust. Soc. Am. 72, 896 / 1891 —
  sound absorption in seawater (pure water, MgSO₄, boric acid terms).
- M. A. Ainslie & J. G. McColm (1998), J. Acoust. Soc. Am. 103, 1671 — simplified
  absorption formula.
- L. D. Gorkov (1962), Sov. Phys. Dokl. 6, 773 — force on a small sphere in an
  acoustic field.
- T. G. Leighton, *The Acoustic Bubble* — bubble dynamics, Bjerknes forces,
  cavitation thresholds.
- M. V. Berry (2000) era material for random waves is *not* used here.

## Why an AI lab could help

- It can freeze a prereg spanning six coupled modules, run all of them plus a
  twelve-control battery and an independent re-implementation in one pass, and
  report the failure zones numerically instead of qualitatively — including the
  unglamorous result that a module failed.

## What would count as a real result

- A **joint certificate**: all six modules inside tolerance, every resolution
  ladder converging, all controls passing, and an independent re-implementation
  agreeing — together with a written, quantitative failure-zone map saying exactly
  where the simulator must not be trusted. That is instrument certification of a
  known-physics simulator, **not** a discovery about water.
