# Discovery status

**As of 2026-09-24 — EXP-0016 / Q-O007 complete as a measurement-definition study; no discovery claim**

## What we knew before

- Scalar angular-spectrum propagation is unitary for propagating components.
- Well-resolved random-field vortex density reproduces Kac–Rice/Nye–Berry.
- A discrete winding detector can produce grid-, phase-, and
  implementation-dependent features.
- The historical `32 µm` structure is inherited, and the historical
  `z=1280 µm` physical-topology claim is not established.
- Free-space propagation can physically create/annihilate vortex pairs in
  suitable fields; that established fact does not validate the historical DBS
  count.

## What was newly established in EXP-0016

Nothing has been promoted as a new physical discovery. EXP-0016 establishes a
bounded **measurement-definition result**: the phrase “vortex count” is
ambiguous unless the representation unit is named. In matched analytical
fields, a charge-+2 singularity can appear as one charge-two location, two
same-sign components, or four unit winding cells. Contour and Jacobian
estimators have a separate subpixel-core failure regime, while raw winding has
a phase-placement/charge-splitting regime. The two failure regimes do not
collapse to one detector-independent law in the tested data.

The rectangular-grid red-team candidate from EXP-0015 remains closed as a
known direct-coarse-grid detector artifact. A close +1/−1 pair disappears near
z=240–320 µm in the modeled controls and is zero by z=400 µm in the converged
128²/256² exact-pixel subset; this is consistent with ordinary modeled pair
annihilation and is not novel.

## What was independently reproduced

The new NumPy implementation reproduces ASM reversibility, energy conservation,
and agreement with a separately written torch FFT implementation. A separate
SciPy raw-winding implementation reproduces the close-pair transition, and a
separate SciPy circular-contour implementation returns four in all tested
rectangular rows, closing the local-contour excess as implementation-specific.
For EXP-0016, the independently written NumPy/SciPy estimator agrees with the
main implementation on all 144 registered comparison rows for record count,
location count, absolute charge, and signed charge.

## What was killed by controls

- Plane waves produce zero features.
- Flat random phase is a dense raw-winding stress case, not a zero-vortex null.
- The first supported-detector calibration was invalid because of a local ring
  statistic; it is logged and excluded.
- The rectangular local-contour excess disappears under a 2048² reference and
  is absent in an independent contour implementation.
- The clean four-vortex target is not a high-count excess against matched or
  random nulls.
- The historical physical interpretation of the 256²/z=1280 result remains
  killed by unit, grid, detector, and provenance audits.
- EXP-0016 exact/subpixel, four-vortex, null, propagation, 2048² reference,
  padding, explicit boundary-crossing, uncertainty, and independent-
  implementation controls pass their fail-closed validation. Boundary losses
  are finite-support/ROI effects, not physical disappearances. The observed
  disagreement is estimator-specific, not a surviving physical residual.

The fail-closed result validator passes all principal assertions in
`03_INVESTIGATIONS/OPTICS/discrete_vortex_bias/RESULTS/validation_summary.json`
and the EXP-0016 validator passes in
`03_INVESTIGATIONS/OPTICS/topology_measurement_definition/RESULTS/validation_summary.json`.
The attempted full dense/random regime map and 50-surrogate matched-null run
were not completed within their declared budgets; they are not counted as
negative evidence.

## What remains unexplained

Whether the corrected EXP-0007 +1280 µm field has 48, 176, or another number
of physical singularities remains unresolved. EXP-0016 also does not establish
a universal detector-bias scaling law across contour radii, interpolation
schemes, independent architectures, dense random fields, and experimental
calibration regimes.

## What literature already explains

Continuous vortex topology, random-field vortex statistics, FFT aliasing and
windowing, contour/sampling limitations, and genuine free-space vortex-pair
dynamics. The targeted matrix is in `LITERATURE_NOVELTY_MATRIX.md`.

## What appears absent from the literature

No matching study was located for the exact historical implementation and
parameter combination. This is **not located in searched literature**, not a
novelty claim.

## Strongest current contribution

At most: a controlled, implementation-independent warning that finite-grid
optical-vortex measurements mix location, component, winding-cell, and
charge-mass semantics. EXP-0016 supports this as a **measurement-definition
result**, not as a novelty candidate. The appropriate classification is
**known numerical/detector semantics**, not Level 3–5 evidence.

## Evidence supporting the bounded result

Analytical known-topology controls expose charge representation differences;
the 1,652-row phase diagram separates detector units; exact/subpixel and
charge controls rule out a simple “one count” interpretation; 2048² reference,
padding, null, propagation, uncertainty, and independent-implementation
controls are complete and pass validation.

## Evidence against a broader claim

The effect is explained by standard finite differences, contour geometry,
candidate selection, and FFT/downsampling semantics. The raw/clustered charge-
two failure does not follow one monotone resolution law, and the contour/
Jacobian failure is concentrated in a different subpixel regime. The full
dense/random regime map and multi-seed matched-null run remain incomplete.
No residual survives as a physical anomaly.

## Confidence level

**High confidence** that the historical material does not justify a new-physics
claim. **High confidence** that count units must be explicitly named in this
controlled analytical setting. **Moderate confidence** that the detailed
failure boundaries generalize beyond the tested estimator geometries. **No
confidence** in a physical or novel discovery claim.

## Exact next experiment

The next computational extension, if pursued, is a preregistered detector-
geometry sweep over contour radius, interpolation order, candidate seeds, and
charge normalization, followed by a completed dense/random regime map and a
matched-spectrum null program. It should test whether any boundary is stable
across independent architectures; it should not be framed as a search for a
new physical vortex population.

## What would constitute a real discovery

A reproducible residual bias that remains after grid, padding, subpixel,
detector, seed, wavelength, null, and independent-implementation controls, is
predicted by a preregistered dimensionless variable, and is independently
checked by a second architecture. It would still require expert/laboratory
review.

## What would falsify the candidate

Disappearance under any one of those controls, detector disagreement, a
matched-spectrum null explanation, or a result that is only a unit/branch-cut
or boundary artifact. Such an outcome closes the candidate as a known
numerical failure mode.
