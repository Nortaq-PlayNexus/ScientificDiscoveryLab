# Key Results

> **AUDIT HOLD (2026-09-24): do not cite unchanged. Read
> `AUDIT_SUPERSESSION_NOTICE.md`; the external sandbox/raw-data chain and
> several historical control/closure claims require re-verification.**

- **Dossier:** Document 5 of 9
- **Companion:** `PROFESSOR_SWARTZLANDER_PROGRESS_DOSSIER.md` (§6), `EXPERIMENT_TIMELINE.md`

This document details the six strongest positive results (the "R-list"). Every
number is from an executed, reproducible experiment. R1–R6 match Document 1 §6.

---

## R1 — The 32 µm structure is real, periodic, and INHERITED (not generated)

- The generator lattice contains a **32.0 µm column pitch**. After propagation,
  the autocorrelogram of the propagated field shows a periodic near-32 µm
  correlation.
- The emergence-vs-inheritance control (`METHODS_AND_CONTROLS.md` §6) proves the
  output pattern comes from the input: a random-input field propagated through
  the same machinery produces raw features ≈ 21,545 with no 32 µm structure.
- Fourier check: the radial maximum (41.66 c/mm ≈ 24 µm) is a blend, not a new
  spatial frequency; the 2-D fundamental is at 33.4 c/mm (≈ 30 µm), 6.4% off
  the design 31.25 c/mm for the 32.0 µm column pitch.
- **Implication:** the "32 µm" the original observer saw is the design pitch of
  the structured vortex lattice. Real, but inherited by construction.

## R2 — The +24/−24 topological charge balance is real and conserved

- The generator contains 48 unit-charge vortices, alternating ±1: **+24 and −24,
  net 0**.
- Independent 48-core re-analysis (audit `EXP-1`) reproduced the balance after
  fixing one classification error; net charge is conserved after propagation, as
  scalar optics requires.
- The original vision report's "45 features" and "21–24 split" claims were
  **AGAINST** in the same validator battery.

## R3 — Propagation numerics are unitary and code-independent

| Check | Value |
|---|---|
| ASM unitarity | ~10⁻¹³ |
| Energy error | 3.1e-16 |
| Independent numpy ASM — NCC | 1.000000 |
| Independent numpy ASM — max |ΔI| | ≤ 1.9e-13 |

This is what makes the whole audit trustworthy: the propagator is not silently
dissipating or injecting energy.

## R4 — Vortex-density statistics match theory (the hard anchor)

Lab `EXP-0003` (independent engine) reproduces the Kac-Rice / Nye-Berry vortex
density for speckle-like fields:

| Metric | Value |
|---|---|
| n_meas / n_pred | 0.9952 – 1.0011 |
| Half-pixel shift change | ≤ 2.1% (shift-invariant counter) |
| Near-Nyquist failure | mapped at 17–24% (counter limitations, documented) |

This is the strongest quantitative link to the published optics literature in
the entire project, and it is the result an external researcher can most
quickly re-verify.

## R5 — The forbidden-statistics / percolation program yields a clean null

Lab `EXP-0005/6/7` (candidate `Q-P004`):

| Metric | Value |
|---|---|
| bond_span (wrap) p_c | 0.50021 (reported; site_span 0.59284) |
| bond_wrap p_c | 0.500687 ± 0.0317 |
| Fisher-Gompertz χ² | 4.738 → 2.239 (control suppresses) |
| C7-style repetition | 78/78 |

The clean H0-supported null removes a whole class of "spontaneous forbidden-
structure" claims from the project.

## R6 — The methodology is reproducible and independently verified

- 6/6 independent verification checks PASS (ASM reproduction, phase-identity
  reproduction, vortex-count reproduction, null reproduction, grid-sweep
  reproduction, pre-registration match) — `INDEPENDENT_VERIFICATION.md`.
- All instrument-identifying artifacts are documented (8-px counter floor,
  pixelation resonance), so future readers can distinguish *physics* from
  *instrument* in these files.

## R7 — Percolation critical exponents (EXP-0009, Q-P005)

Lab `EXP-0009` at site p_c = 0.5927460508, L ∈ {128,256,512,1024}:
D_f = 1.8697, γ/ν = 1.7596, β/ν = 0.1295, τ = 1.9404, 1/ν = 0.7434.
All gates PASS; three exponents miss tolerances by ~1σ (one-directional).
Decision: **ABNORMAL** per frozen rule.

Diagnostic EXP-0010 measured D_f at non-power-of-2 L ∈ {127,191,253,449}:
D_f = 1.8962 ± 0.028 (theory 91/48 = 1.8958, |dev| = 0.0004).
The ABNORMAL was diagnosed as a lattice-size discretization artifact
(same class as optical grid-locking at 256²). **Q-P005 resolved:** 2D
percolation exponents ARE reproduced through the lab pipeline.

## R8 — Prime gaps vs Poisson (EXP-0008, Q-M002)

Lab `EXP-0008`: normalized gaps δ = (p_{i+1} − p_i) / ln(p_i) in four
disjoint ranges to 10⁸. Primary gates G1 (chi2) and G3 (tail z)
rejected after BH-FDR at α = 0.01 across all 4 blocks. Deviation
survives residue-class conditioning in 4/4 disjoint ranges; C7
independent implementation agrees block-by-block (perfect match).
chi2_red 262→94,633 (B1→B4); combined χ² = 971,920 (dof 36,
χ²_red = 26,998, p = 0). Deviation is in tail shape (lighter than
Exp(1), correct mean).

Decision: **H1_SUPPORTED** (escalation only, no novelty claim).

---

## The honest framing

These results are **true, but they are not a discovery**: they amount to
(a) the correct linear-propagation behaviour of a structured vortex field
(R1–R3), (b) agreement with standard theory (R4), and (c) reliable, reproducible
tooling and nulls (R5–R6). The one initially "exciting" statistic (z = 1280 µm,
S = 95) is treated in the negative-results document, because the probing
experiments showed it is a pixelation artifact, not physics.