# Methods and Controls

> **AUDIT HOLD (2026-09-24): review control scope and raw-data provenance
> against `AUDIT_SUPERSESSION_NOTICE.md` before external use.**

- **Dossier:** Document 4 of 9
- **Companion:** `PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md` (§4), `EXPERIMENT_TIMELINE.md`

This document describes exactly how every number in this dossier was produced,
what controls exist, and which statistics are in force. It is written so that
the methods are reproducible without the original authors.

## 1. The simulation engine (sandbox)

Coherent scalar optics on a finite FFT grid:

- Field: complex scalar `E = A·exp(iφ)`; intensity `I = |E|²`.
- Grid 256 × 256, pixel 1 µm, aperture 256 µm.
- Default wavelength λ = 694.3 nm.
- Envelope: `0.55 + 0.45·exp(−r²/2σ²)`, σ = 0.42 × 256 px ≈ 107.5 µm.
- Propagation: angular-spectrum method (ASM), band-limited, deterministic.
- Numerics: ASM unitarity ~10⁻¹³; energy error ~3×10⁻¹⁶; independent numpy ASM
  gives NCC = 1.000000 with max |ΔI| ≤ 1.9e-13.

## 2. The structured vortex generator

- 8 columns × 6 rows = 48 unit-charge vortices; column pitch 32.0 µm, row pitch
  42.67 µm; alternating ±1 charge; total +24 / −24, net 0.
- Internal generator propagation: 2 × 160 µm ASM before the plane sweep.
- Plane sweep: z ∈ {0, 40, 80, 160, 320, 640, 1280} µm.
- FFT cycle length `z_cycle = L²/λ = 94,391 µm`; z = 1280 µm = 5.0 × 256 px
  (a clean multiple — flagged before testing).

## 3. Random number generation

- Seeded, reproducible RNG. Lab engine: sha256-derived labels
  (`engine.utilities.core.rng(label, seed)`); audit pre-registration fixed
  seeds {42, 7, 123, 2023, 314159, 271828}.
- Lab RNG certified in `EXP-0004` (`Q-I004`).

## 4. The null / surrogate framework

| Null | Construction | Role |
|---|---|---|
| D01 (circular Gaussian) | Matches lattice intensity statistics only | Broad sanity check; produces medians ≈ 843–853 |
| D02 (matched spectrum) | Matches the full 2D Fourier magnitude spectrum of the field | Primary surrogate; medians 42–45, q95 65–67 |

- Matched-spectrum null preserves the intensity and the spatial-frequency ESD
  while destroying topological structure — the standard approach for
  "is the topology real or an artifact" type questions.
- Significance: empirical p from surrogate distribution; multiple testing via
  BH-FDR at α = 0.01.

## 5. The pre-registered statistic (audit `EXP-2B`)

- Pre-registered **before** seeing results (`PREREGISTRATION_z1280.md`).
- Statistic: **S = median of purified feature count over 5 Fourier shifts**
  (±⅓ px and ±⅕ px), purified with the τ* = 0.2 detector threshold.
- Shift-mixing defeats single-grid pixelation: if a "count" is a numerical
  resonance pinned to the 256² lattice, shifting and re-locking collapses it.
- Observed S = 95; null q95 ≈ 66–67; d ≈ 4.2–4.5; 6/6 seeds ≤ 0.01.
- This is precisely why `EXP-2C` was then run: to decide whether S = 95 is
  physics or pixelation. It is pixelation (see below, §7).

## 6. Controls

| Control | Design | Status |
|---|---|---|
| Emergence-vs-inheritance | Compare input vs output features; does the 32 µm appear even when the generator does not contain it? | **32 µm inherited** from the 32.0 µm column pitch; not generated. |
| Random-input control | Propagate a phase-random field with matched intensity | Raw features ≈ 21,545 (no structure), i.e., the propagator does not self-organise structure. |
| Anti-cheat band-power | Experimenter-independent band-power controls: C-control ratio stability | **C-control INVALID (ratio 0.595)**; **B/H VALID**. The C-control failure is itself diagnostic (see negative results doc). |
| Blind coded-field analysis v2 | Detector-blind pass over coded field, 36 × 156 px, DEEP CODE 7 | **INFO CONFIRMED**; 0/2 control false positives — reproduced, then attributed to grid artifact. |
| Flat-amplitude control | Constant |A| with the same phase-only structure | Raw ≈ 21.9k features, **purified = 0** → no content in intensity-only data. |
| Shift-invariance | Half-pixel shifts of the counting method (lab `EXP-0003`) | ≤ 2.1% count change (valid until near-Nyquist, 17–24% failure mapped). |
| Wavelength sweep | 13/17 wavelengths produced "20–45 µm" spacing claims | Claim of spacing **AGAINST** (validator); no wavelength-invariant structure. |

## 7. The pixelation audit (audit `EXP-2C`)

- **PROBE A** (grid size): z = 1280 µm on 64/128/256/512², aperture fixed:
  obs/null {0.70, 1.43, 2.10, 1.22}, p {0.926, 0.058, 0.002, 0.24}. Only the
  256² grid survives. At 512² the observed count (68) is below the null q95 (85).
- **PROBE B** (plane): z = 640/960/1280/1475/1600/2622 µm. Only z = 1280 is
  significant at α = 0.05 after FDR; **nothing at α = 0.01**. Col-pitch
  half-Talbot (1475 µm) is marginal OUT* (p 0.036–0.050), row-pitch half-Talbot
  (2622 µm) is inside the envelope (p 0.898) → the effect is **not** Talbot
  self-imaging and **not** scale-invariant.
- Conclusion: the "topological excess" at z = 1280 µm is a resonance of the
  256² grid ("pixelation resonance"), specific to the one detector/one grid.
  Evidence level final = 1.

## 8. Feature counting method (the grid-lock caveat)

The winding feature counter operates on the FFT grid; its measurement of
"spacing" carries an 8-px floor (detector attribute), so all lattice pitches
(16/32/64/128 µm and the 21.33 µm wavelength sweep) produced the **same 8.0-px
autocorrelation lag**. This is an instrument property, not a physics door.
Purifying with the τ* = 0.2 threshold and removing the floor collapses the
apparent "32 µm" everywhere except where the generator placed a 32.0 µm pitch.

## 9. Lab engine methods (independent `ScientificDiscoveryLab`)

- Invoked via `sys.path.insert(0, "…/04_SHARED_ENGINE")` and `import engine`;
  explicit sha256-derived RNG; no pandas dependency.
- `EXP-0002/0003`: analytic-reproduction logic — generate surfaces/speckle,
  measure the statistic, compare with theory (C(M) = 1/√M; Kac-Rice vortex
  density) and record measured/predicted ratio.
- `EXP-0005/6/7`: bond/site percolation with wrap-around, C7-style 78/78
  repetition → clean H0-support.
- All lab experiments are registered append-only in the lab registry.

## 10. What is NOT in the method

- No real-optics measurement; all results computational.
- No AI output used as evidence; the single quoted AI output (Document 1, §1)
  is labelled *unverified observation report*.
- No chemical/symbolic-on-light claim; no semantic decoding.