# Negative and Diagnostic Results

> **AUDIT HOLD (2026-09-24): diagnostic labels below predate the cross-project
> audit. See `AUDIT_SUPERSESSION_NOTICE.md` before reuse.**

- **Dossier:** Document 6 of 9
- **Companion:** `PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md` (§7, §10), `METHODS_AND_CONTROLS.md`

This document lists everything that did **not** survive and every diagnostic
that explains why. A negative result here is a positive for the integrity of
the project: it means the tooling was performing its falsification role.

---

## 1. Original vision-report claims — not reproduced

| Claim | Verdict |
|---|---|
| "~45 candidate dark/winding structures" | **AGAINST** (independent validator: 48 cores after classification fix) |
| "apparent ~32 µm spacing" | Spacing is real but **inherited** (generator 32.0 µm pitch), not emergent |
| "21/24 split" (asymmetric count) | **AGAINST** (true balance is +24 / −24, net 0) |
| "21,545 features" raw count | Raw count is a property of detector + grid; purified count with τ* = 0.2 collapses to 31/24/36/90 |

## 2. The phase-randomisation "phase-as-information" claim

- Claim: mean |ΔI| ≈ 0.13 meant "phase is information".
- Correction: `|A·e^{iφ}|² = A²` exactly; max relative difference **6.55e-16**
  at the same plane. The 0.13 difference is the propagation of a
  phase-incoherent vs. phase-coherent field through a *unitary* operator. It is
  textbook Fourier optics, not information theory.
- Post-propagation: NCC = 0.0564; vortex count 74 → 21,738 — expected
  propagation of randomised phase, not evidence.

## 3. The "32 µm autocorrelation" — instrument floor artifact

- Autocorrelogram spacing is **8.0 px** for *every* design pitch tested
  (16/32/64/128 µm and the 21.33 µm wavelength-sweep case).
- The DeepBeamScan winding detector imposes an 8-px floor.
- Median-nearest-neighbour tracking works (3/5 pitches within 15%) but the
  autocorrelation "spacing" reading is instrument-defined.
- Result: the "32 µm" reading is 8 px × 4 µm⁻¹-equiv quirks, not a stable,
  pitch-independent physics length.

## 4. z = 1280 µm excess — pixelation resonance, not topology

- Timeline: pre-registered `EXP-2B` found S = 95 vs null q95 ≈ 66–67,
  d ≈ 4.2–4.5, 6/6 seeds significant ≤ 0.01. This was the **only** surviving
  significant point after all corrections.
- `EXP-2C` PROBE A (grid size): obs/null {0.70, 1.43, 2.10, 1.22}, p
  {0.926, 0.058, 0.002, 0.24}; significant **only** at 256²; at 512² obs 68
  ≤ q95 85 → significance is grid-specific.
- `EXP-2C` PROBE B (plane): significant **only** at z = 1280 among
  640/960/1280/1475/1600/2622 µm (after FDR, nothing at α = 0.01); col-pitch
  half-Talbot 1475 µm marginal OUT* (p 0.036–0.050), row-pitch half-Talbot
  2622 µm inside envelope (p 0.898).
- Verdict: **pixelation resonance** of the 256² grid at z = 1280 µm
  (z = 5.0 × grid-pitch). Not Talbot, not scale-invariant topology.

## 5. Other nulls

| Null | Value |
|---|---|
| D01 circular-Gaussian null | median ≈ 843–853 per plane, lattice 24–90, p ≈ 1.0 at every plane |
| D02 matched-spectrum null | medians 42–45, q95 65–67; only z = 1280 ever exceeded (see §4) |
| BH-FDR α = 0.01 | z = 1280 fails FDR before the pixelation audit; nothing survives post-audit |

## 6. Controls that failed (and why that is diagnostic)

| Control | Result | Meaning |
|---|---|---|
| C-control (anti-cheat band-power) | ratio 0.595 **INVALID** | The control channel is not independent of the experiment — this *invalidated the control*, which is itself a finding: it says the pixel-counting instrument and the anti-cheat function share grid-dependent behaviour (consistent with the pixelation story). |
| Flat-amplitude run | raw ≈ 21.9k features, purified **0** | Phase-only structure disappears from a flat-amplitude intensity readout → no content carried in intensity alone. |

## 7. Near-Nyquist failure (documented limitation)

Lab `EXP-0003` counter is shift-invariant (half-pixel shift ≤ 2.1%) but
**fails near Nyquist by 17–24%** — a measured property of the counter, confined
to wavelengths/pitches close to the 2-px limit. It does not affect the
mid-band results used above.

## 8. Semantics / "code" in light — not found

- No symbolic, textual, or "code-like" content survives any control.
- The single digit "8.0 px" is a counter floor; "33.4 c/mm" and "41.66 c/mm"
  are Fourier features of the lattice; none are content. `CURRENT_OPEN_QUESTIONS.md`
  frames how one would, in principle, test the strongest *possible*
  semantic claim — and why it is currently **RULED OUT** (insufficient tests) —
  without implying it exists.

---

## What the negatives mean for the reviewer

The project now contains exactly one "exciting" number (S = 95 at z = 1280)
and a chain of controlled experiments showing that number is an instrument
resonance. That is the intended, honest endpoint of a falsification-first
audit.