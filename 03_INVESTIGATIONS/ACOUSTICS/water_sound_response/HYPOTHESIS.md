# HYPOTHESIS — HYP-AC001 (water acoustic response simulator)

Registered in the lab HYPOTHESES.md as HYP-AC001. Frozen under EXP-0015.

## Statement

A single simulator that uses published water parameters
(ρ = 998.2 kg/m³, σ = 0.0728 N/m, μ = 1.002×10⁻³ Pa·s, ν = 1.003×10⁻⁶ m²/s,
β_f = 4.6×10⁻¹⁰ Pa⁻¹, P₀ = 101325 Pa, P_vap = 2339 Pa, κ = 1.4,
c = c_UNESCO(T,P)) reproduces **all six** established laws below within their
preregistered tolerances, and every residual attributable to discretisation
shrinks under the corresponding refinement (dx, dt, Δf → 0).

Jointly, and only jointly:

- **H1 (S1, sound speed).** c_UNESCO(T,P) reproduces the published fresh-water
  anchors to ≤ 0.05 %, and agrees with the independent Mackenzie (1981) formula
  to ≤ 0.05 % over 0–30 °C at 1 bar.
- **H2 (S2, bounded-column resonance).** A driven damped column exhibits response
  peaks at f_n = n·c/(2L) (rigid–rigid) and f_n = (2n−1)·c/(4L) (rigid–free),
  each within 1 % of prediction, and all peaks scale as 1/L when L doubles.
- **H3 (S3, absorption).** The measured decay constant of a propagated pulse
  matches α = 2.50×10⁻¹⁴ f² Np/m to ≤ 5 % at every test frequency, and the
  log-log slope of α vs f is 2.00 ± 0.05.
- **H4 (S4, nodal patterning).** Particles with φ > 0 converge to pressure nodes
  spaced λ/2 to within 2 % of λ/2, while a matched φ < 0 control converges to
  pressure antinodes; the time to reach 90 % of final position scales as a⁻².
- **H5 (S5, bubble response).** The driven-bubble resonance frequency obeys
  f₀ ∝ R₀⁻¹ with log-log slope −1.00 ± 0.05, and f₀R₀ ∈ [3.0, 3.5] Hz·m.
- **H6 (S6, Faraday surface).** The simulated free surface obeys
  ω₀² = (gk + σk³/ρ)tanh(kh) to ≤ 1 %; a vertically driven layer responds at
  exactly half the drive frequency above threshold and decays below it; the
  measured threshold matches Γ_c ≈ 4μ/ω₀ (μ from an independent free-decay
  fit) to within 25 %; and the selected wavenumber satisfies ω/2 = ω₀(k) to
  ≤ 5 %.

## Secondary statements (characterisation, not gates)

- **S-a (absorption decomposition).** The first-principles classical value
  α_cl/f² computed from water's shear viscosity and thermal conductivity lands
  near the literature 1.1×10⁻¹⁴ s²/m, and the ratio to the imposed total
  (2.5×10⁻¹⁴ s²/m) is ≈ 2.3 — the documented structural-relaxation excess.
- **S-b (linearity boundary of the bubble).** Below a drive amplitude the driven
  Rayleigh–Plesset response is proportional to drive; above it, harmonics appear
  and unbounded growth (transient cavitation) sets in near |p| ≈ P₀.
- **S-c (Faraday threshold realism).** The simulated Γ_c is a property of the
  *imposed* linear damping model (μ = νk²) and is **lower than** experimentally
  observed thresholds for water, which are raised by contact-line and meniscus
  dissipation that this model does not contain. Recorded as a model limit.
- **S-d (failure zone).** Residuals grow with frequency at fixed grid for S2 and
  S6; a stated safe operating region (points per wavelength, points per period)
  is published in REPORT/.

## Distinction from the null

- **H0** is the conjunction above: every module inside tolerance with residuals
  that vanish under refinement ⇒ the simulator is certified in the stated regime.
- **H1-dev** is: some module outside tolerance **and** its residual does *not*
  shrink under refinement (a genuine implementation defect or an unmodelled
  physical effect). Per RESEARCH_RULES §5 this triggers the kill-the-hypothesis
  battery and is reported as a controlled deviation or a documented model
  limitation — never interpreted as new physics.

Passing H0 certifies an **instrument**, not a theory. Failing one module does not
invalidate the others; it localises the defect.

## Prior expectation

H0 is expected. All six target laws are established (1831–1998). Offline planning
checks (disclosed in FALSIFICATION/planning_checks.md) found the modules landing
on their anchors, which is exactly why the tolerances were set where they are.
**These planning numbers are not the registered result.**

## What would falsify H0

- A resonance ladder whose peaks do not move to the predicted positions when the
  boundary condition or L changes.
- An absorption slope ≠ 2 that persists as dx → 0.
- Particles migrating to nodes even when φ < 0 (a solver that ignores contrast).
- f₀R₀ outside [3.0, 3.5] Hz·m, or a slope ≠ −1 in the f₀ vs R₀ log-log fit.
- A Faraday response at ω (not ω/2), or a threshold that does not converge toward
  4μ/ω₀ as dt and the Γ-ladder step shrink.
- Any of the above surviving the C1–C11 controls and the C12 independent
  re-implementation.
