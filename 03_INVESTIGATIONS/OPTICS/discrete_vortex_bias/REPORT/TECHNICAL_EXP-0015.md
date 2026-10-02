# EXP-0015 — Technical report: discrete optical-vortex detection bias

**Run date:** 2026-09-24  
**Question:** Q-O006  
**Hypothesis:** HYP-OPT-DVB-001  
**Status:** PARTIAL / INCONCLUSIVE / NO NOVELTY CLAIM  
**Preregistration:** `CONFIG/prereg_EXP-0015.json`  
**Preregistration SHA-256:** `514f6d142528d38f0d7729dd5ea8b955a70024369ac5e2965fb4d637e552140e`

## 1. Scientific question

Under what combinations of sampling, propagation, boundary conditions, and
 detector definition does a discrete optical-vortex detector produce a
systematic count bias relative to a field with analytically known phase
topology?

The experiment is about measurement bias. It does not assume that the
historical 256²/z=1280 µm DBS result is a physical phenomenon.

## 2. Fields and numerical method

The primary control field is a scalar Gaussian-enveloped superposition

\[
E(x,y)=A(x,y)\exp\left(i\sum_j q_j\operatorname{atan2}(y-y_j,x-x_j)\right),
\]

with known positions and charges. The amplitude has a finite 0.03 floor and a
fixed 4 µm core depression so that samples at a coincident grid point remain
defined. An exact-zero control was also run. Therefore these tests validate
discrete phase-topology detection; they are not direct laboratory measurements
of exact complex zeros.

Propagation is a periodic, band-limited angular-spectrum propagator. All
distances are passed in metres. The independent implementation checks include
reverse propagation, a torch FFT implementation, a separately written SciPy
FFT/raw-winding implementation, and a separately written SciPy contour
implementation.

Four detectors receive identical fields:

1. raw 2×2 plaquette winding;
2. same-sign connected-component clustering;
3. intensity-supported component clustering; and
4. local-minimum detection followed by a complex-field circular-contour
   winding calculation.

Feature count, net charge, absolute charge, localization, and match fields are
recorded separately. A count is not treated as a physical census without a
reference.

## 3. Calibration and seed controls

The corrected seed-42 calibration contains 1,408 rows over grids 32–512 and
subpixel shifts 0–0.9 px. Seeds 7 and 123 were rerun with the same 1,408-row
structure and the same deterministic control results.

| Known case | Truth | Raw winding | Clustered | Supported | Local contour |
|---|---:|---:|---:|---:|---:|
| single +1 vortex | 1 | 1 | 1 | 1 | 1 |
| +1/−1 pair | 2 | 2 | 2 | 2 | 2 |
| charge +2 vortex | 1 site | 2–4 plaquettes | 1–2 components | 1–2 components | 1 |
| four-vortex field | 4 | 4 | 4 | 4 | 4 |

The charge-+2 result is a detector-semantics effect. Raw winding preserves net
charge while representing a charge-two defect as multiple unit cells. A plane
wave gives zero features. A flat random-phase field gives thousands of raw
winding cells but no supported/contour features, so it is a stress case, not a
zero-vortex null.

The first support-detector calibration was invalid because an off-centre core
sample dominated a ring minimum. It was discarded and the correction was
hash-chained in `CONFIG/changes.jsonl`.

## 4. Primary convergence and scale controls

`convergence_42_20260924_134108.json` contains 2,424 measurements:

- 216 dense-z rows at grids 128 and 256;
- 1,152 grid/shift/plane rows;
- 864 wavelength rows; and
- 192 padding rows.

For the well-separated four-vortex control, every detector returned exactly
four features throughout grids 64–512, shifts 0–0.9 px, the tested z planes,
all 12 wavelengths, and padding fractions 0–3. This is a negative control: the
historical-looking count change is not reproduced by a clean, well-separated
field.

`geometry_controls_20260924_134416.json` tested rectangular grids 128×256,
256×128, 256×512, and 512×256, plus 128/256/512 µm physical FOVs. A selected
local-contour excess appeared in direct coarse rows, but the independent
2048² reference/downsample run returned four. A separately written SciPy
contour detector returned four in all 32 tested rectangular rows. This closes
the candidate as an implementation/downsampling artifact, not physical
vortices.

## 5. Oversample→downsample

`oversample_42_20260924_134458.json` used a 2048² periodic reference, seven z
planes, and target grids 64–1024. For the well-separated control, every
high-resolution-reference/downsample count and direct coarse count was four.
The subpixel rows at grids 128, 256, and 512 were also invariant.

The targeted rectangular reference and close-pair reference controls are more
informative:

- rectangular reference: 128 rows, all high-resolution paths returned four;
- close-pair reference: 216 rows, raw/clustered/supported paths agreed with
  the direct paths through the physical transition.

Thus the clean control has no measurable propagation/detection separation, but
the harder controls do expose detector-specific errors.

## 6. Close-pair tracker

An 8 µm +1/−1 pair was tracked from z=0 to 1600 µm. At 256², all detectors
saw two features through z=240 µm and zero from z=320 µm onward. The 2048²
reference and independent raw-winding implementation show the same transition
at grids 128–512. This is consistent with ordinary modeled vortex–antivortex
annihilation, not a new physical effect. Local-contour misses before the
transition are detector errors layered on the modeled transition.

## 7. Detector-size and high-charge results

`detector_size_20260924_134854.json` contains 1,764 close-pair measurements
over contour radii 1–5 px, separations 2–48 µm, grids 64–512, and four shifts.
The local detector has no single monotone resolution threshold. Depending on
radius and grid, it misses, merges, or overcounts a close pair. The error rate
over the exploratory matrix is 17.9% at radius 1.5 px, 21.0% at 2 px, and
33.3% at 5 px; these are descriptive cell frequencies, not independent
hypothesis tests.

The reduced high-charge map shows raw winding counts of 2–4, 3–5, 4, and 6–10
for charges +2, +3, +4, and +6 respectively, while the contour detector
returns one component. Absolute/net charge diagnostics show why: this is
representation, not physical charge creation.

The exact-zero control shows the same close-pair contour failures with and
without the finite amplitude floor, so the main effect is not simply an
amplitude-floor artifact.

## 8. Nulls and random fields

The single-surrogate null file contains 256 measurements. At z=1280 µm, the
four-vortex target count is four, while matched-spectrum counts are roughly
12–28, matched-amplitude counts are much larger, and random-Gaussian counts
depend strongly on grid and detector. The target is not a high-count excess.

The six-seed random ladder contains 384 measurements. Within a fixed detector,
count CVs are generally below 10%; between detectors, means can differ by
orders of magnitude. This demonstrates seed stability of a detector-specific
statistic, not a detector-independent physical count.

A larger 50-surrogate matched-null run exceeded the 600-second budget without
emitting a result. It is not counted as a negative or positive experiment.
The attempted full dense/random regime map likewise timed out without an
artifact. The reduced fast map is explicitly exploratory.

## 9. Direct-space control

The first direct Fresnel control omitted the global prefactor; the next
accidentally applied it twice. Both failed outputs are preserved. A corrected
small-domain version still differs substantially from periodic ASM because
finite-window direct integration and periodic FFT propagation are different
boundary problems. This control remains **INCONCLUSIVE** and is not used to
support any candidate.

## 10. Fail-closed validation

`CODE/validate_results.py` passes all principal assertions: known single,
pair, and four-vortex controls; the primary grid/z convergence; square
reference path equality; rectangular reference convergence; independent
contour agreement; the close-pair transition; and exact-zero raw-pair counts.
The machine-readable result is `RESULTS/validation_summary.json`.


## 11. Classification

### Findings that survive

- Raw, clustered, supported, and contour detectors are not interchangeable.
- Charge-q representation and contour geometry create reproducible count
  differences on analytical controls.
- Direct coarse-grid contour artifacts can be killed by a high-resolution
  reference and independent implementation.
- The close-pair transition is consistent with known modeled pair annihilation.
- Random-field count distributions are detector-specific.

### Findings killed

- A new physical count anomaly in the clean well-separated control.
- A universal detector-independent count based only on the raw feature total.
- The rectangular local-contour excess as a physical-vortex claim.
- The historical 256²/z=1280 µm physical-topology claim.

### Level

**Level 1: known numerical artifact reproduced.** The strongest narrower
result is a useful characterization of detector/downsampling failure modes,
not a Level 3–5 discovery. No candidate is promoted.

## 12. Strongest next experiment

Run a preregistered charge-normalized contour study using exact-zero fields,
multiple contour shapes/radii, a 2048² reference, and an independently written
locator. Test whether any residual error collapses onto a preregistered
dimensionless variable rather than being explained by implementation-specific
candidate selection or interpolation. A physical laboratory phase measurement
would be required for any claim beyond numerical methodology.
