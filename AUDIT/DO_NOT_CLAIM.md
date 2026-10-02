# DO_NOT_CLAIM — ScientificDiscoveryLab

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab`
**Auditor:** Automated forensic inventory (Phase 17 of 20)

---

> **2026-09-24 update:** this list remains a do-not-claim register, but several
> older audit statements are superseded. Historical 3D percolation p-c/C7 and
> Q-P007 refined-p-c closures are invalid; new repair artifacts use explicit
> exact-byte/canonical hashes; EXP-0004 is not RNG-certified; and historical
> Feigenbaum z=3/z=4 claims are not accepted. See
> `AUDIT/REPAIR_LOG_20260924.md`.

> **2026-09-28 (later) — N-001: the reported exponent is not a best estimate.**
> The frozen production value `tau = 1.92009` is **biased upward** by +0.11 to
> +0.35 depending on the fitting window, measured against synthetic
> distributions of known exponent. Therefore:
>
> - Do **not** quote 1.92009 as the measured or best-estimate cluster-mass
>   exponent. Quote it as the frozen production number that it is.
> - Do **not** quote the bias-corrected 1.81, or the histogram estimator's 1.70,
>   as *the* exponent either. They are secondary estimates whose mutual
>   disagreement (0.11) is larger than any uncertainty quoted alongside them.
> - Do **not** claim the deviation from the Fisher value 187/91 has been
>   resolved. It has not. It is robust in **direction** under every estimator and
>   window, and untrusted in **magnitude**.
> - Do **not** claim the deviation is explained by finite-size crossover. The
>   stored data contradict that: tau does not drift with L, and the deviation is
>   nearly size-independent.
> - Do **not** quote the extrapolated "required L" of about 1e8. It is arithmetic
>   from a slope statistically indistinguishable from zero and is marked
>   `extrapolation_is_meaningful: false`.
> - Do **not** claim the N-001 escalation was withdrawn. It stands, strengthened
>   in magnitude.

## 1. Purpose

Per the instruction document: "Generate a 'DO NOT CLAIM' document: what is NOT YET established."

This document lists everything that CANNOT be claimed based on current evidence in ScientificDiscoveryLab.

> **2026-09-28 update — add this to the list.** The shared RNG battery's
> `T03_runs` test is **`ESTIMATOR_DEFECTIVE`**: it applies a spurious `√2` to a
> statistic NIST SP 800-22 §2.3 already defines in `erfc` units, and it omits
> the standard's applicability precondition, which 0 of 200 seeds satisfy at the
> laboratory's stream lengths. Therefore:
>
> - Do **not** claim a single flat number of battery tests as unqualified truth. Do not say
>   “0 of 24 miscalibrated”, and do not say “24 of 24 calibrated”. After the
>   corrected re-derivation the accurate statement is **23 of 24 per-test cells
>   calibrated, 0 miscalibrated, and 1 (T03_runs) unresolvable** at these
>   resolutions, because SP 800-22 section 2.3 step 1 requires
>   |pi - 1/2| >= 2/sqrt(n-1) and **0 of 200 seeds** satisfy it. An unresolved
>   cell must never be reported as agreement.
> - Do **not** claim T03_runs is merely “disabled by a documented deviation”.
>   It is DEFECTIVE_BY_ALGEBRAIC_IDENTITY: a spurious sqrt(2) is applied to an
>   argument the standard defines directly in erfc units.
> - Do **not** claim the failure to detect that defect at 2^22 exonerates the
>   estimator. Detection is resolution- and seed-dependent; the defect is a
>   deterministic code property and non-detection is not evidence of correctness.
> - Do **not** claim the battery is validated, calibrated, or clean as a whole.
>   `BATTERY_VALID` remains the family-level verdict because the positive
>   control is rejected by other tests, and that verdict stands.
> - Do **not** claim the defect says anything about G_LAB. It is evidence about
>   the instrument. G_LAB is not implicated.
> - Do **not** claim the withdrawn EXP-0004 certificate is reinstated. A
>   defective instrument cannot support a certification.

## 2. Claims That Cannot be Made

### 2.1 Cannot Claim New Discoveries

| Claim | Why Not | What Could Change This |
|---|---|---|
| "We discovered the Kac-Rice/Nye-Berry formula for vortex density" | This is textbook (Nye & Berry 1974) | Nothing — this is a reproduction |
| "We discovered the speckle contrast law" | This is textbook (Goodman) | Nothing — this is a reproduction |
| "We discovered percolation critical exponents" | Standard results (Stauffer & Aharony) | Nothing — this is a reproduction |
| "We discovered the Feigenbaum constant" | Published in 1978 | Nothing — this is a reproduction |
| "We discovered prime gap statistics" | Known deviations from Poisson model | Escalation pending community review |
| "The 32 µm structure is a new physical phenomenon" | Inherited from generator design | Real-optics experiment needed |

### 2.2 Cannot Claim Physical Confirmation

| Claim | Status | Needed |
|---|---|---|
| "Simulation results match real laser experiments" | NOT YET TESTED | Real-optics experiment (ref: INTEGRATION_PLAN.md) |
| "The vortex lattice exists in physical optics" | Simulation only | Physical experiment |
| "Speckle contrast measured with real instrument" | Simulation only | Physical measurement |

### 2.3 Cannot Claim Computational Results Not Verified

| Claim | Status | Needed |
|---|---|---|
| "Historical result-file integrity confirmed by recorded hash" | Scope/serialization inconsistencies found; repaired artifacts now distinguish canonical-object and exact-byte hashes | Recompute and verify each current artifact with its declared scope |
| "sovereign_biolab.db contains experiment metadata" | Database unexamined | Query the database |
| "percolation.rar contains relevant data" | Archive unextracted | Extract and compare |
| "05_DATA/ contains required raw data" | Directories unexamined | Inspect contents |
| "S9/§9 battery establishes empirical perception, dose, or wavelength effects" | Read-only provenance audit finds synthetic response simulation, hard-coded rates, and no raw participant/image inputs in the declared package | Obtain consent-/privacy-reviewed raw data, immutable acquisition hashes, and a new empirical preregistration |
| "3D percolation exponents (Q-P008)" | Historical width/p-c/C7 invalid; no corrected production result | Freeze a new probit-width production config, run corrected pipeline/C7, then independently review |
| "Acoustics results" | Investigation early-stage | More data needed |
| "cone_mosaic aliasing characterization" | Minimal documentation | More detail needed |

### 2.4 Cannot Claim Universality

| Claim | Why Not |
|---|---|
| "Our RNG passes all standard batteries / is certified" | Pooled battery dependence and control-generator marginal failures invalidate certification; N-004 is smoke-only | A separately approved dependence-aware fresh-seed calibration against valid controls |
| "Our percolation results hold for all lattices" | Only square lattice tested (2D and 3D pilot) |
| "Our vortex results hold for all spectra" | Only isotropic spectra tested (per derivation requirement) |
| "Our speckle results hold for all apertures" | Only single aperture fraction (1/8) tested |
| "Our prime gap results extend to infinity" | Only ranges below 10^8 tested |
| "Feigenbaum universality holds for all z" | z=2 is reproduced; the isolated N-003 z=3/z=4 repair is period-certified but finite and nonmonotone, with no alpha or convergence claim | A separately approved, higher-resolution/production-quality convergence study |

### 2.5 Cannot Claim Novelty

| Claim | Why Not |
|---|---|
| "We found novel structure in propagated light fields" | 32 µm structure is inherited by construction |
| "We found novel charge patterns in vortices" | +24/-24 is by design |
| "We found novel prime gap deviations" | Known deviation in tail shape; escalation only |
| "We found novel phase information in light" | RULED OUT — propagation artifact |
| "We found novel symbols in light intensity" | RULED OUT — pixelation artifact |

### 2.6 Cannot Claim Beyond Scale/Resolution

| Claim | Why Not |
|---|---|
| "Vortex density holds at N < 256" | Low-N shows finite-grid deviations |
| "Percolation threshold accurate to 10⁻⁶" | Current SE ≈ 0.0317 for bond_wrap |
| "Feigenbaum constants for z > 4" | Not computed |
| "Prime gap statistics above 10⁸" | Only tested to 10⁸ |
| "Speckle contrast for M > 16" | Only tested M ≤ 16 |

### 2.7 Cannot Claim Causal Mechanisms

| Claim | Why Not |
|---|---|
| "The broadband deficit is a new physical resolution transition" | Fixed-spectrum/interpolation/low-pass controls support finite sampling and unresolved spectral content; novelty remains unresolved | No claim without a mechanistic model and independent external comparison |
| "The lattice artifact mechanism is Y" | Diagnosed, not mechanistically understood |
| "The prime gap tail shape has explanation Z" | Tail shape noted; explanation not provided |

## 3. Summary Statistics

| Category | Count |
|---|---|
| Cannot claim new discoveries | 6 |
| Cannot claim physical confirmation | 3 |
| Cannot claim unverified computational results | 7 |
| Cannot claim universality | 6 |
| Cannot claim novelty | 5 |
| Cannot claim beyond scale | 6 |
| Cannot claim causal mechanisms | 3 |
| **Total unclaimable items** | **36** |

## 4. What IS Establishes

For contrast, what CAN be claimed (see STRONGEST_DEFENSIBLE_CLAIMS.md):
1. Limited reproductions of established theory with explicitly scoped controls
2. Diagnostic characterizations of failure modes and artifacts
3. Auditable engineering repairs (dimension-explicit boundaries, immutable preregistration, exact-byte hashes)
4. Honest escalation of unresolved anomalies without novelty claims
5. Software test results, which are not evidence that a scientific model is correct

## 5. Recommendation for Future Work

To convert "DO NOT CLAIM" items to "CAN CLAIM":

1. **Run real-optics experiments** → converts simulation claims to physical confirmation
2. **Create a new Q-P008 production preregistration** → only a completed,
   corrected, independently checked run could support a 3D conclusion
3. **Verify declared artifact hashes** → integrity becomes confirmed for those
   artifacts, not retroactively for historical files
4. **Run dependence-aware RNG calibration** → possible test-specific conclusions
5. **Replace Q-M007/Q-M008 analysis and sieve** → only then can scale claims be
   reassessed
6. **Run approved Q-P007/N-001 production** → a real refined-p_c/tau comparison
7. **Develop causal theories for surviving anomalies** → mechanistic understanding
8. **Do not upgrade finite N-003 z=3/z=4 ratios to a convergence or alpha result**;
   the independent review is complete, but the claim gate remains closed.
