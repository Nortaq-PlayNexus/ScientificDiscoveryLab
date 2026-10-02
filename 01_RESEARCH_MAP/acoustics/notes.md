# ACOUSTICS — research map

Field letter: `AC`. Questions are `Q-AC###`, hypotheses `HYP-AC###`.

## Known (established science this field starts from)

- **Speed of sound in water.** c(T, S, P) is a fitted empirical surface, not an
  ab-initio calculation. International standard = UNESCO algorithm (Chen & Millero
  1977; coefficients recast by Wong & Zhu 1995 for ITS-90). Validity:
  T 0–40 °C, S 0–40 PSU, P 0–1000 bar. Independent alternative: Mackenzie (1981)
  9-term T/S/D polynomial (valid 2–30 °C, 0–8000 m, error < 0.1 m/s in range).
  Anchors: c(0 °C, fresh) = 1402.388 m/s (UNESCO check value); c(20 °C, fresh)
  ≈ 1482 m/s; c(25 °C, fresh) ≈ 1497 m/s. The temperature curve is **non-monotonic
  in seawater** (salinity-driven maximum near 13 °C at S=35) but monotonic rising
  over 0–40 °C for fresh water.
- **Bounded-column (standing-wave) response.** A driven water column of length L
  resonates at f_n = n·c/(2L) for rigid-rigid (velocity nodes both ends) and
  f_n = (2n−1)·c/(4L) for rigid-free (free surface = pressure release). This is
  the standard organ-pipe / acoustic-resonator result.
- **Absorption.** Fresh-water absorption at 20 °C, 1 atm:
  α = 2.50 × 10⁻¹⁴ · f² Np/m (f in Hz) — equivalently 2.175 × 10⁻¹³ dB/m per Hz².
  Classical (viscosity + thermal conduction) theory alone predicts only
  α_cl/f² ≈ 1.1 × 10⁻¹⁴ s²/m at 280 K; the accepted high-frequency limit is
  2.5 × 10⁻¹⁴ s²/m. The factor ≈ 2.3 excess is attributed to **structural (bulk)
  relaxation** of the hydrogen-bond network (τ_R ≈ 3.5 ps at 4 °C → f_R ≈ 45 GHz,
  far above the audio/low-ultrasonic band, so no relaxation bump is visible there).
  Seawater adds MgSO₄ (~65 kHz) and boric-acid relaxation terms — Throp's,
  Schulkin-Marsh, Fisher-Simmons, Francois-Garrison, Ainslie-McColm formulas.
  Practical consequence: water is a **low-pass channel**; absorption ∝ f².
- **Acoustic radiation force / nodal patterning.** Gorkov's primary radiation force
  on a small compressible sphere in a standing wave:
  F = −(π p₀² V_p β_f / (2λ)) · φ · sin(4πx/λ),
  φ = (5ρ_p − 2ρ_f)/(2ρ_p + ρ_f) − β_p/β_f  (acoustic contrast factor).
  φ > 0 → particles collect at **pressure nodes** (spacing λ/2); φ < 0 → antinodes.
  Water: β_f = 4.6 × 10⁻¹⁰ Pa⁻¹, ρ_f = 998 kg/m³. Polystyrene:
  ρ_p = 1050 kg/m³, β_p = 2.16 × 10⁻¹⁰ Pa⁻¹ → φ ≈ +0.71 → nodes.
  Force ∝ a³, Stokes drag ∝ a ⇒ migration speed ∝ a². Competing effect: acoustic
  streaming (Eckart/boundary/Rayleigh) drag, which dominates below ~2 µm; radiation
  force dominates above ~5 µm for typical MHz standing waves.
- **Bubble dynamics (cavitation).** Minnaert (1933) linear resonance:
  f₀ = (1/2πR₀)·√(3κP₀/ρ) ⇒ **f₀·R₀ ≈ 3 Hz·m** for an air bubble in water
  (κ=1.4, P₀=1 atm). Surface-tension correction matters below ~100 µm. Free
  (transient) cavitation onset requires the local absolute pressure to fall to
  near vapour pressure — for a bubble in a sound field this happens once drive
  amplitude approaches P₀ (Blake threshold regime). Driven Rayleigh–Plesset is the
  standard model; bubbles smaller than resonance travel toward pressure antinodes,
  larger than resonance toward nodes (primary Bjerknes force).
- **Faraday instability / surface response to vertical vibration.** A liquid layer
  in a vertically oscillating container g(t) = g[1 + Γ cos ωt] develops standing
  surface waves above a threshold Γ_c. Linear dispersion (finite depth h):
  ω₀²(k) = (gk + σk³/ρ)·tanh(kh). Parametric resonance tongues at ω/ω₀ ≈ 2/n
  (Benjamin & Ursell 1954 Mathieu system); the n = 1 tongue is **subharmonic**:
  the surface responds at ω/2 (Faraday 1831). With linear damping rate μ the
  n=1 threshold is Γ_c ≈ 4μ/ω₀. Real thresholds are higher than inviscid/viscous
  theory predicts because of contact-line and meniscus dissipation.
- **Chladni / cymatics.** Grains on a vibrating plate accumulate at **nodal lines**
  (recent work: space-dependent diffusivity — grains random-walk faster where
  vibration is strong, so they pile up where it is weak). Water-surface analogues
  are Faraday patterns; pressure-node patterning in bulk water is the
  radiation-force mechanism above. "Cymatics" claims beyond standing-wave physics
  (e.g. water "storing" or "responding structurally" to sound) are **not** part of
  this map and are not treated as science here.

## Open / what a lab can honestly do here

- Reproduce the whole chain — c(T,P), resonance ladder, α ∝ f², node patterning,
  Minnaert scaling, Faraday subharmonic/wavelength selection — inside **one
  simulator**, with each module gated against its published anchor, a resolution
  ladder showing discretisation error shrinking, and an independent re-implementation.
- Characterise where the simulator stops being faithful: linearity limits, the
  classical-vs-actual absorption gap, the linear (non-saturating) Faraday model,
  the inviscid threshold underestimate.
- **No novelty is plausible.** Every target law is 1933–1998 textbook material.
  The deliverable is a *certified instrument* + an honest failure-zone map.

## Computable on this machine

- 1-D finite-difference Helmholtz solves (resonance, absorption): trivial CPU.
- Vectorised Rayleigh–Plesset sweeps: seconds.
- Gorkov particle integration: trivial.
- Linear free-surface spectral model (cosine modes in x/y, finite-difference
  vertical solve) for Faraday: seconds–minutes per Γ ladder.
- NOT computable: full molecular dynamics of cavitation (needs 10⁸–10¹¹ atoms /
  supercomputer), sonochemistry yields, real transducer calibration, 2-D nonlinear
  Faraday pattern selection (squares/hexagons need 4-wave nonlinear coupling).

## Realistic mode

Numerical-science certification project: reproduce published acoustic laws with
tight error bars, gate each module, publish the failure zone. Nothing here can
establish new physics; candidates would be flagged for external human review only.
