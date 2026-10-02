# Convergence results — EXP-0015

**Status: PARTIAL / NO PROMOTION.** This file is a live result record, not a
final discovery classification. See `RESULTS/` for machine-readable outputs
and `CONFIG/prereg_EXP-0015.json` for the frozen gates.

## Calibration completed (seed 42)

A self-contained NumPy/SciPy implementation tested four known-topology fields
at grids 32–512 and subpixel shifts 0–0.9 px. The fields use an exact analytic
phase winding with a finite 0.03 amplitude floor and a fixed 4 µm core
depression. This avoids undefined samples at a coincident grid point while
testing discrete phase topology; it is not a measurement of an exact optical
zero at the sample. The corrected calibration file is
`RESULTS/calibration_42_20260924_133910.json`.

| Case | Truth | Raw winding | Clustered | Supported clustered | Local-minimum contour |
|---|---:|---:|---:|---:|---:|
| single vortex | 1 | 1 | 1 | 1 | 1 |
| +1/−1 pair | 2 | 2 | 2 | 2 | 2 |
| charge +2 vortex | 1 topological site | 2–4 plaquettes | 1–2 components | 1–2 components | 1 |
| four-vortex lattice | 4 | 4 | 4 | 4 | 4 |

The +2 control is an immediate detector-semantics warning: a raw plaquette
counter can represent one charge-two singularity as two or four unit winding
cells, whereas a component/contour detector represents it as one charge-two
feature. This is a reproducible **detector-definition effect**, not evidence of
new physics.

A flat random-phase field produces thousands of raw winding cells but no
intensity-supported or local-minimum features, confirming that a random phase
map is a stress case rather than a zero-vortex null. A plane wave produces zero
features for all four detectors.

The first calibration run was discarded after a support-detector calibration
failure (a ring minimum was dominated by a neighboring off-centre core sample).
The correction and reason are permanently recorded in
`CONFIG/changes.jsonl`; the failed run is not used as evidence.

## Implementation check

`RESULTS/implementation_42_20260924_133041.json` records:

- ASM versus reverse ASM complex NCC ≈ 1;
- NumPy ASM versus torch FFT ASM complex NCC = 1 within the recorded run;
- energy preserved to floating-point precision;
- ASM versus Fresnel NCC recorded separately (small model difference, not a
  detector-count equivalence test).

Seed 7 and 123 calibration reruns completed with the same 1,408-row summaries
as seed 42: single, pair, and four-vortex controls are invariant, and the
charge-+2 split pattern is unchanged. This is expected for the deterministic
analytical fields and confirms that their reported differences are not random
seed selection.
## Primary convergence matrix completed (seed 42)

`RESULTS/convergence_42_20260924_134108.json` contains 2,424 measurements from
the preregistered well-separated four-vortex field (runtime 85.0 s). Across
grids 64–512, shifts 0–0.9 px, selected z planes, all 12 wavelengths, and
padding fractions 0–3, each of the four detectors returned exactly four
features in the tested summaries. The dense z sweep at grids 128 and 256 also
returned four features at every tested plane.

This is a **negative control result**, not evidence that discrete detectors
never fail. The field is well separated and the test was not close to the
sampling limit. It establishes that the historical-looking count changes are
not reproduced by this cleaner analytical control and that a harder regime map
is necessary.

The independently written SciPy replication
`RESULTS/independent_replication_20260924_134059.json` also returns the
same four raw-winding features for its sampled well-separated four-vortex
matrix. This is an implementation check; the separate close-pair and contour
files below provide the additional regime replication.

## Independent detector checks

`RESULTS/independent_replication_20260924_134059.json` reproduces the
well-separated raw-winding matrix with a separately written SciPy FFT
implementation. `RESULTS/independent_close_20260924_135514.json` reproduces
the close-pair transition. `RESULTS/independent_contour_20260924_141208.json`
returns four features in all 32 tested rectangular four-vortex rows, whereas
the main local-minimum detector produced selected 5–6 rows. The rectangular
candidate is therefore implementation-specific.

## Exploratory regime map

A reduced close-pair/high-order map completed in
`RESULTS/regimes_fast_20260924_140842.json` (1,040 rows). It confirms the
charge-representation and close-pair detector effects summarized in
`REGIME_FAST_ANALYSIS.md`. The attempted full dense/random map exceeded its
600-second budget and emitted no result; it is recorded as an incomplete run,
not as a negative result. The primary frozen matrix remains the authoritative
promotion evidence.

## Oversample→downsample completed for the well-separated control (seed 42)

`RESULTS/oversample_42_20260924_134458.json` used a 2048² periodic reference,
propagated it at seven z planes, and sampled grids 64–1024. For every detector,
the high-resolution-reference/downsample count and the direct coarse-grid
propagation count were both four at every tested grid and z. The subpixel
sample rows at grids 128, 256, and 512 were also invariant at four.

This is an important negative result: the well-separated field has no
detectable propagation-versus-downsampling count bias in this regime. It does
not establish convergence for close pairs, high-charge defects, random fields,
or the historical DBS field.

## Direct-space control status

The first direct Fresnel reference was invalid because its global prefactor
was omitted; a second version accidentally applied the prefactor twice. Both
failed outputs are preserved and logged. A corrected small-domain run
(`RESULTS/direct_reference_20260924_135940.json`) still differs substantially
from the periodic ASM because the finite-window/direct integral and periodic
FFT boundary conditions are not the same numerical problem. This control is
therefore **INCONCLUSIVE**, not evidence for or against a physical anomaly.
The independent SciPy/torch FFT checks and the 2048² reference remain the valid
propagation controls.
## Exact-zero control

`RESULTS/exact_zero_20260924_135547.json` compares a finite 0.03 amplitude
floor with an exact complex-zero core. For single and four-vortex controls all
four detectors return the known counts. For the 8 µm pair, raw, clustered,
and supported detectors return two at grids 64–512 for both floors; the
local-minimum contour returns 0/1/2 only in selected 64² rows. Thus the main
close-pair detector error is not caused by the amplitude floor and is localized
to the contour estimator at coarse sampling.
## Close-pair tracker and reference control

The dense tracker (`RESULTS/tracker_20260924_134940.json`) followed a +1/−1
pair separated by 8 µm. At coarse 256², all four detectors saw two features
through z=240 µm and zero from z=320 µm onward. A 2048² reference/downsample
run (`RESULTS/close_pair_reference_20260924_135217.json`) shows the same
transition for raw, clustered, and supported detectors at grids 128–512.
Thus the disappearance is consistent with ordinary modeled vortex–antivortex
annihilation, not a detector sampling artifact. The local-minimum contour has
additional path-dependent misses just before the transition, which are detector
errors layered on top of the physical/reference transition.

This is a known physical control, not a new discovery. It demonstrates why a
count trajectory cannot be interpreted without a high-resolution reference.

## Rectangular red-team control

The geometry stage found selected 5–6-feature local-contour results in direct
coarse rectangular rows. The independent 2048² reference/downsample check
(`RESULTS/rectangular_reference_20260924_134643.json`) returned four for every
detector and path, while reproducing the 5–6 direct-coarse result. This closes
that candidate as a detector/downsampling artifact; details are in
`CANDIDATE_DISCOVERY_DVB-001.md`.

