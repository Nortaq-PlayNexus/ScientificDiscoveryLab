# QUESTION — Q-F004: How does a water surface respond to sound and vibration frequencies?

**Field:** fluid dynamics / acoustics / physics
**Question ID:** Q-F004
**Feasibility:** HIGH

## Question

When a body of water is subjected to periodic vertical vibration (a mechanical
proxy for sound-driven surface forcing) at drive frequency f, does the surface
break into stationary standing-wave patterns with:
- a response at the **subharmonic half-frequency** f/2 (Faraday waves), and
- a pattern wavelength λ = 2π/k governed by the **capillary-gravity dispersion
  relation** ω² = (g·k + (σ/ρ)·k³)·tanh(k·h) evaluated at ω = π·f,

reproducibly, within the lab's controlled spectral-simulation pipeline?

## What scientists already know

- **Faraday (1831):** a vertically-oscillated fluid layer forms subharmonic
  standing waves at half the driving frequency (classic, widely replicated).
- **Benjamin & Ursell (1954):** the linearised surface problem reduces, per
  Fourier mode k, to a damped **Mathieu equation**; subharmonic instability
  occurs when the drive Ω = 2πf is near 2·ω(k), i.e. ω(k) ≈ π·f.
- **Kumar & Tuckerman (1994):** full viscous analysis with Floquet theory;
  viscous damping shifts onset amplitudes and growth rates.
- **Dispersion:** deep/finite-depth capillary-gravity waves satisfy
  ω² = (g·k + (σ/ρ)·k³)·tanh(k·h), where g=9.81 m/s², σ≈0.0728 N/m (water-air,
  20 °C), ρ=1000 kg/m³, h=depth. Mean-field textbook result.
- Related "similar science domains" (see LITERATURE.md): cymatics / Chladni
  figures, capillary ripple speed, Minnaert bubble resonance, sound speed in
  water — all linked through the same surface/compressibility physics.

## What remains unknown (for the lab)

Nothing fundamental is unknown: this is a **reproduction/calibration** question.
The lab-specific unknowns are:
- whether the lab's spectral integrator recovers ω(k) to tolerance (C1/C5),
- whether the fastest-growing wavenumber k*(f) tracks the subharmonic dispersion
  root ω(k)=π·f across a frequency ladder (P2),
- whether the response frequency is f/2 as predicted (P3),
- whether an independent Floquet implementation (Method M2) agrees (C6/C7).

## Known methods

- Spectral integration of the damped parametric (Mathieu) surface equation
  (Method M1, this investigation).
- Floquet monodromy analysis of the same equation, independently implemented
  (Method M2, REPLICATION/).
- Root-finding of the dispersion relation for the predicted k*(f).

## Computational requirements

CPU, low. Vectorised RK4 across a k-ladder of a few hundred modes for a handful of
drive frequencies. No external data. Runtime ~seconds to minutes.

## Falsification test

If the measured k*(f) deviates from the dispersion-root prediction by more than the
preregistered tolerance (10% relative), or if the response frequency is not the
subharmonic f/2 within tolerance, the reproduction hypothesis HYP-F004 is falsified
for that condition. Controls (C2 null, C3 onset) must pass for any result to count.

## What would count as a real result

Reproduction of the Faraday subharmonic dispersion law with quantified error bars
across the frequency ladder, confirmed by (a) dispersion reproduction, (b) an
independent Floquet implementation, (c) seed and resolution variation. No novelty
claimed — this certifies the pipeline on a classic known law.