# LITERATURE — Water acoustic response (Q-AC001 / EXP-0015)

Honesty rule: "no matching study found in sources searched" — never "novel".
No novelty is claimed anywhere in this investigation.

## Sources searched (as of 2026-09-22)

Targeted web searches were performed during design for each of the six modules:
acoustic cavitation / bubble dynamics; Faraday waves and the Faraday instability;
speed of sound in water (UNESCO / Chen–Millero); acoustic streaming and radiation
force in standing waves; sound absorption/attenuation in fresh water; and
Chladni/cymatics pattern formation. **No structured bibliographic database
(PubMed, Web of Science, Scopus, INSPEC) was queried programmatically.** The
references below are the specific, citable works surfaced by those searches plus
established textbook material. This limitation is recorded honestly: a formal
systematic search remains a pending lab task (see lab CURRENT_STATUS "Known
limitations").

---

## S1 — Speed of sound in water

- **N. P. Fofonoff & F. J. Millard Jr. (1983)**, *Algorithms for computation of
  fundamental properties of seawater*, UNESCO Technical Papers in Marine Science
  44. The UNESCO equation of state set.
- **C.-T. Chen & F. J. Millero (1977)**, "Speed of sound in seawater at high
  pressures", *J. Acoust. Soc. Am.* 62(5), 1129–1135. Original algorithm.
- **G. S. W. Wong & S. Zhu (1995)**, "Speed of sound in seawater as a function of
  salinity, temperature and pressure", *J. Acoust. Soc. Am.* 97(3), 1732–1736.
  ITS-90 recast of the coefficients used here.
- **G. S. K. Mackenzie (1981)**, "Nine-term equation for sound speed in the oceans",
  *J. Acoust. Soc. Am.* 70(3), 807–812. Independent method (C5 control).
- NPL acoustics technical guide, "Speed of sound in sea water" — cites UNESCO as
  the international standard and documents the validity ranges and the ongoing
  UNESCO-vs-Del Grosso accuracy debate.

**What the sources state:** c = C_w(T,P) + A(T,P)S + B(T,P)S^{3/2} + D(T,P)S²,
valid 0–40 °C, 0–40 PSU, 0–1000 bar. Fresh-water (S=0) check value c(0 °C, 0 bar)
= 1402.388 m/s. Pure-water/fresh-water at 20 °C, 1 atm ≈ 1482 m/s; at 25 °C ≈ 1497 m/s.

## S2 — Bounded-column resonance

- Standard organ-pipe / acoustic-resonator theory: pressure-release (open or
  free-surface) end at a pressure node, rigid end at a pressure antinode ⇒
  f_n = n c/2L (rigid–rigid) and f_n = (2n−1)c/4L (rigid–free).
- Underwater-acoustics propagation guides (e.g. VE7CNF "Underwater Acoustic
  Propagation"; NPL guides) for the distilled-water speed formula
  c = 1402.7 + 4.591T − 0.0482T² + 0.0135T³ + … (Mackenzie form) accurate to
  0.05 % over 0–30 °C, 0–200 bar.

## S3 — Absorption in water

- Fresh water at 20 °C, 1 atm: **α = f² × 2.50×10⁻¹⁴ Np/m = f² × 2.175×10⁻¹³ dB/m**
  (f in Hz). Textbook handbook value; the conversion is consistent
  (2.50×10⁻¹⁴ × 8.686 = 2.17×10⁻¹³).
- Classical theory (viscosity + thermal conduction) gives only
  **α_cl/f² ≈ 1.1×10⁻¹⁴ s²/m** for freshwater at 280 K
  (ν = 1.44×10⁻⁶ m²/s, Pr = 10.4, c = 1500 m/s); the accepted high-frequency limit
  is 2.5×10⁻¹⁴ s²/m. The excess is attributed to **structural relaxation** of the
  water hydrogen-bond network; τ_R ≈ 3.5 ps at 4 °C ⇒ f_R ≈ 45 GHz, far above the
  band used here, so absorption appears as a clean f² law with no relaxation bump
  in the audio/low-ultrasonic range. (*Attenuation of Sound*, Springer, ch. 14.)
- Seawater relaxations: **R. E. Francois & G. R. Garrison (1982)**, *JASA* 72(6)
  and 73(6) — pure-water + MgSO₄ + boric-acid decomposition, 400 Hz–1 MHz.
- **M. A. Ainslie & J. G. McColm (1998)**, *JASA* 103(3), 1671–1672 — simplified
  viscous + chemical absorption formula.
- **W. L. Thorp** (1967) empirical seawater formula; **Schulkin & Marsh (1962)**;
  **Fisher & Simmons (1977)** — all ∝ f² asymptotically with relaxation shoulders.

## S4 — Radiation force and nodal patterning

- **L. D. Gorkov (1962)**, *Sov. Phys. Dokl.* 6, 773 — potential on a small
  sphere in an acoustic field; the primary radiation force.
- **T. G. Leighton**, *The Acoustic Bubble*, ch. on Bjerknes forces —
  primary Bjerknes force, node/antinode migration of bubbles.
- "Acoustic Microfluidics", *Annu. Rev. Anal. Chem.* (2020) — review: primary ARF
  ∝ a³, drives particles to pressure nodes/antinodes by acoustic contrast; streaming
  drag ∝ a dominates below ~2 µm; the standard force law
  F = −(π p₀² V_p β_f/2λ) φ sin(4πx/λ), φ = (5ρ_p−2ρ_f)/(2ρ_p+ρ_f) − β_p/β_f.
- "Particle hydrodynamics in acoustic fields: Unifying acoustophoresis with
  streaming", Zhang, Minten & Rallabandi, *Phys. Rev. Fluids* (2024) —
  polystyrene in water (κ̃ ≈ 0.38, ρ̃ ≈ 1.05) accumulates at **pressure nodes**
  regardless of the viscous/inertial parameter δ; unifies inviscid acoustophoresis
  with viscous streaming.
- "Investigation into the Effect of Acoustic Radiation Force and Acoustic
  Streaming on Particle Patterning in Acoustic Standing Wave Fields", *Sensors*
  17(7), 1664 (2017) — ARF dominates for ≥3 µm, streaming for ~1 µm.
- "Primary Bjerknes forces", Southampton ISVR — small bubbles → antinodes, large
  bubbles → nodes; R₀ν₀ = 3 Hz·m.

## S5 — Bubble resonance and cavitation

- **M. Minnaert (1933)**, *Phil. Mag.* 16, 960 — f₀ = (1/2πR₀)√(3κP₀/ρ);
  the compact **R₀f₀ ≈ 3 Hz·m** for air in water.
- **F. G. Blake (1949)** — the Blake threshold for acoustic cavitation onset.
- **K. W. Commander & A. Prosperetti (1989)**, *JASA* 85, 738 — linear bubble
  oscillation and sound propagation in bubbly liquids (damping, resonance).
- **A. Yasui**, *Acoustic Cavitation and Bubble Dynamics* (Springer, 2017).
- "Nonlinear bubble dynamics of cavitation", *Phys. Rev. E* 85, 016305 (2012) —
  driven Rayleigh–Plesset / Keller–Miksis in a standing wave.
- 100-billion-atom MD study of ultrasonic cavitation (2026) — establishes the
  scale gap: molecular-scale cavitation requires supercomputers; our continuum
  Rayleigh–Plesset model is explicitly **not** that.
- **A. A. Doinikov** and **Plekasis et al.**, secondary Bjerknes inter-particle
  forces (context only).

## S6 — Faraday instability / free-surface response

- **M. Faraday (1831)**, *Phil. Trans. R. Soc. Lond.* 121, 299–318 — original
  account; waves at half the driving period.
- **T. B. Benjamin & F. Ursell (1954)**, *Proc. R. Soc. A* 225, 505–515 —
  Mathieu stability of the vertically vibrated free surface; uncoupled Mathieu
  equations; subharmonic/harmonic/superharmonic tongues.
- **J. W. Miles (1990)**, "Parametrically forced surface waves" — thresholds,
  subharmonic thresholds, higher thresholds (precession, modulation, chaos).
- **H. W. Müller, J. Miles, C. Wagner & J. Knorr (1997)**, *PRL* 78, 2357 —
  analytic stability theory and the harmonic surface response.
- University of Toronto / ComPADRE "Faraday Waves" advanced-lab write-ups —
  parametric oscillator model z'' + μz' + ω₀²[1+Γcos ωt]z = 0, tongues at
  ω/ω₀ ≈ 2/n, dispersion ω₀² = (gk + σk³/ρ)tanh(kh), Γ = Aω²/g.
- **Faraday instability and subthreshold Faraday waves** (Cambridge, JFM) and
  Shao/Batson-type work — meniscus/edge waves are *linear with no threshold* and
  can cloak the true onset; real thresholds exceed inviscid theory because of
  contact-line dissipation. Directly relevant to our disclosed limitation.

## Chladni / cymatics

- "Chladni patterns explained by the space-dependent diffusion of bouncing
  grains", *Phys. Rev. Research* 7, L032001 (2025) — grains accumulate at nodes
  because their effective diffusivity is low where the plate barely moves; the
  grain threshold for motion is a_{max}ω² > g.
- Tuan/Vicsek/Wang line of work on reconstructing Chladni figures from the
  inhomogeneous Helmholtz equation and maximum-entropy states; Kirchhoff–Love
  plate dispersion confirmed. Sub-0.1 mm grains can produce *inverse* Chladni
  patterns (antinodes).

**Honest scoping note:** claims sometimes grouped under "cymatics" — that water
*stores*, *remembers* or is *structurally altered* by sound/frequencies — are not
supported by any source found here and are **outside the scope of this lab's
simulator**. What is testable and tested is standing-wave and parametric-resonance
physics only.

## Position of this investigation

Reproduction and **instrument certification**, not novelty. The lab's contribution,
if any, is procedural: a preregistered, artifact-aware, six-module joint
certification with resolution ladders and an independent re-implementation. Any
claim of novelty is explicitly disallowed.
