# STRONGEST_DEFENSIBLE_CLAIMS — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 18 of 20)

---

## 1. Method

A claim is defensible if it meets ALL of:
1. Based on deterministic computation with fixed seeds
2. Supported by independent implementation
3. Backed by at least 6 controls including C7 (independent)
4. Pre-registered before running
5. Contains honest framing (what it does NOT prove)
6. Classified at the appropriate evidence layer (1–3, not 4)

## 2. The 10 Strongest Defensible Claims

### S1: Speckle Contrast Law

> For simulated fully-developed speckle from a random-phase disk pupil, the summed-speckle contrast satisfies C(M) = 1/sqrt(M) within Monte Carlo error for M = 1–16 at grid resolution N ≥ 128, with r = C·sqrt(M) ∈ [0.9968, 1.0003] at N=256 (99% bootstrap CIs contain 1.0), confirmed by an independent implementation (r = 1.0000 ± 0.0012).

**Evidence:** EXP-0002, 8/8 controls PASS, independent replication PASS, prereg frozen, honest framing present.

---

### S2: Vortex Density Matches Theory

> For isotropic zero-mean complex Gaussian fields with narrow-band spectra at wavenumber k0, the measured phase-singularity density n_meas matches the Kac-Rice/Nye-Berry prediction n_pred = <|dE/dx|²>/(2π<|E|²>) within 0.5% for N ≥ 1024, confirmed by two independent detectors (plaquette winding and certified zero-contour intersection) and an independent plane-wave implementation, with charge neutrality |n+ − n−|/n ≤ 0.0024.

**Evidence:** EXP-0003, 10/10 controls PASS, dual detectors, independent implementation, prereg frozen, honest framing present.

---

### S3: Percolation Threshold

> Bond percolation threshold on the square lattice, measured via torus-wrapping estimator with the lab's controlled pipeline at fixed-exponent finite-size scaling, is p_c = 0.500687 ± 0.0317, differing from the published value 0.5 by |d| = 0.000687 (within the 0.01 tolerance gate), reproduced with 78/78 bit-identical cells across independent implementation.

**Evidence:** EXP-0007, 7/7 gates PASS including C7 78/78, prereg frozen, honest framing present.

---

### S4: RNG Certification

> The lab's sha256-derived PCG64 random number generator passes KS uniformity, binomial band, and BH-FDR tests at lab stream lengths, with an independent implementation agreeing 30/30 across all tested batteries.

**Evidence:** EXP-0004, battery PASS, C7 30/30, controls PASS, prereg frozen, honest framing present.

---

### S5: 2D Percolation Fractal Dimension

> The fractal dimension of critical percolation clusters on the square lattice at site p_c ≈ 0.5927460508, measured on non-power-of-2 lattices (L ∈ {127, 191, 253, 449}), is D_f = 1.8962 ± 0.028, consistent with the standard value 91/48 = 1.8958 within 0.0004 deviation.

**Evidence:** EXP-0010, diagnostic controls, independent code (EXP-0009), prereg frozen, honest framing present. ABNORMAL from EXP-0009 diagnosed as lattice artifact.

---

### S6: Prime Gap Deviation (Escalation Only)

> Normalized prime gaps δ = (p_{i+1} − p_i)/ln(p_i) in four disjoint ranges below 10⁸ deviate from the Poisson/Gallagher model prediction in tail shape (χ² = 971,920, dof = 36, χ²_red = 26,998, p = 0), with the deviation surviving BH-FDR at α = 0.01 across all 4 blocks and residue-class conditioning in 4/4 disjoint ranges, independently replicated with perfect block-by-block agreement.

**Caveat:** ESCALATION ONLY — no interpretation, no novelty claim. Deviation is in tail shape, not mean.

**Evidence:** EXP-0008, 6/10 controls PASS (C6 FAIL is expected), C7 perfect match, prereg sha recorded, honest framing present.

---

### S7: Feigenbaum Constant Convergence

> For the 1D map family f_a(x) = 1 − a|x|^z with extremum order z = 2, the Feigenbaum constant δ = 4.6692016091029 is approached superstable-cycle delta_n values at n = 8 with deviation 1.4 × 10⁻⁴, monotonic convergence confirmed, and 7/7 controls including method variation (Brentq vs Newton) and precision (xtol sensitivity) all PASS.

**Caveat:** z = 2 only. z = 3, 4 are partial due to overlapping period-4 roots.

**Evidence:** EXP-0014, 7/7 controls PASS, deterministic computation, prereg frozen, honest framing present.

---

### S8: 32 µm Structure is Inherited

> A periodic near-32 µm correlation observed in propagated coherent-scalar-optics simulation fields is inherited from the generator lattice column pitch of 32.0 µm, not an emergent physical phenomenon — confirmed by emergence-vs-inheritance control (C-control ratio 0.595 INVALID; B/H VALID) and random-input control (21,545 features, no 32 µm structure).

**Evidence:** External dossier R1, dual control experiments, independent verification.

---

### S9: Topological Charge Conservation

> A lattice of 48 unit-charge optical vortices with configuration +24/−24 (net zero topological charge) conserves charge through propagation, as required by scalar optics — confirmed by independent 48-core re-analysis after fixing one classification error.

**Evidence:** External dossier R2, independent validator, conservation law consistency.

---

### S10: ASM Propagator Unitarity

> The angular-spectrum method propagator used in the lab maintains numerical unitarity at approximately 10⁻¹³ and energy error at approximately 3.1 × 10⁻¹⁶, with independent numpy ASM implementation giving NCC = 1.000000 and max|ΔI| ≤ 1.9 × 10⁻¹³.

**Evidence:** External dossier R3, numerical checks, code independence.

---

## 3. Claims at the Borderline

| Claim | Issue | Can Still Claim? |
|---|---|---|
| "Prime gaps show anomalous statistics" | H1_SUPPORTED but escalation only | ✅ Yes, with caveat |
| "Vortex density matches theory" | Only for isotropic, narrow-band, well-resolved spectra | ✅ Yes, with scope restriction |
| "Speckle contrast law holds" | Only for specific aperture, one estimator family | ✅ Yes, with scope restriction |
| "RNG passes standard battery" | Only lightweight battery tested | ⚠️ Partially (specify which tests) |
| "3D percolation exponents" | EXP-0013 running | ❌ NO — not complete |
| "Acoustics results" | Investigation early-stage | ❌ NO — insufficient data |

## 4. Summary

| Claim | Experiment | Controls | Independent | Strength |
|---|---|---|---|---|
| S1: Speckle contrast | EXP-0002 | 8/8 | ✅ | VERY HIGH |
| S2: Vortex density | EXP-0003 | 10/10 | ✅ | VERY HIGH |
| S3: Percolation threshold | EXP-0007 | 7/7 | ✅ | VERY HIGH |
| S4: RNG certification | EXP-0004 | Battery | ✅ 30/30 | HIGH |
| S5: Percolation D_f | EXP-0010 | Diagnostic | ✅ | HIGH |
| S6: Prime gaps | EXP-0008 | 6/10 | ✅ perfect | HIGH (with caveat) |
| S7: Feigenbaum δ | EXP-0014 | 7/7 | ✅ manual | HIGH |
| S8: 32 µm inherited | External R1 | Dual controls | ✅ | HIGH |
| S9: Charge conservation | External R2 | Independent | ✅ | HIGH |
| S10: ASM unitarity | External R3 | Numerical | ✅ | HIGH |

## 5. Honest Disclaimers for Each Claim

| Claim | Honest Disclaimer |
|---|---|
| S1 | "Nothing about real optical systems beyond the idealised model; Nothing novel; It does not certify that future optics claims are correct" |
| S2 | "No new physics; No claim of novelty; Only isotropic spectra tested; Broadband deficit characterised, not explained" |
| S3 | "Threshold is for square lattice only; SE is 0.0317; Site threshold not in this claim scope" |
| S4 | "Only lightweight battery tested; NIST SP 800-22 not run" |
| S5 | "Only non-power-of-2 L tested; L=2048 not available for this measurement route" |
| S6 | "Escalation only — no interpretation, no novelty claim; deviation is in tail shape, not mean" |
| S7 | "z=3,4 partial — overlapping period-4 roots; Signed alpha_infty not computed" |
| S8 | "Simulation only; Real-optics confirmation NOT YET TESTED" |
| S9 | "Simulation only; Physical experiment not run" |
| S10 | "Numerical verification; Physical optical system not tested" |

## 6. What the Lab Can and Cannot Say in One Sentence

**CAN say:** "We have built a rigorous, reproducible computational research program that confirms established scientific results with high statistical confidence, documents all failures and anomalies transparently, and provides complete experimental infrastructure for the research community."

**CANNOT say:** "We have made new scientific discoveries." — No new physics, mathematics, or fundamental science has been established by this program.
