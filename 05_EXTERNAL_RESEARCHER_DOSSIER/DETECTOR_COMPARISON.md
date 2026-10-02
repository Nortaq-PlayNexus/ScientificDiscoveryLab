# Detector comparison — EXP-0015

## Detectors

| Detector | Definition | What it can measure | Known failure mode |
|---|---|---|---|
| `raw_winding` | Principal phase differences around every 2×2 plaquette; nonzero integer winding is a feature | Discrete plaquette winding events | Counts one high-charge singularity as multiple unit cells; branch/interpolation and boundary artifacts |
| `clustered_winding` | 8-connected components of same-sign raw winding cells; component charge is summed | Spatially connected winding regions | Can merge nearby vortices or split one singularity across disconnected cells |
| `supported_clustered_winding` | Same as clustered, with a 4×4 ring/core intensity-support test | Winding regions with a local amplitude depression | Depends on core width, amplitude floor, ring definition, and propagation-induced filling |
| `local_minimum_contour` | Dark local minima followed by complex-field interpolation around a circular contour | A more independent localization/winding estimate | Depends on contour radius, interpolation, candidate selection, and boundary margins |

All four receive the identical complex field in each run. They are not assumed
to estimate the same mathematical object.

## Calibration evidence

For a single +1 vortex, a ±1 pair, and a four-vortex lattice, the four methods
agree on count over the tested grids and shifts. For a charge-+2 vortex, raw
winding returns 2–4 plaquettes while the component and contour methods return
one charge-two feature. This is the clearest current demonstration of
**detector-semantics-dependent count bias**.

The flat random-phase stress control returns zero supported/contour features
but thousands of raw/clustered features. Therefore raw feature count is not a
valid zero-vortex null and cannot be interpreted as a physical population
without an amplitude-aware detector and a matched null.

## Rectangular-grid red-team result

In the geometry control, the local-minimum contour detector returned 5–6
features for selected `(128,256)` and `(256,512)` rows at z=1280 µm and
subpixel shifts 0.25–0.75, while the other three detectors returned four. A
2048² reference/downsample check returned four for every detector and path;
the direct coarse path reproduced the 5–6 excess. A separately written SciPy
contour detector returned four in all 32 rectangular control rows, so the
failure is specific to the main local-minimum implementation. The candidate is
therefore closed as a **direct-coarse-grid implementation artifact**, not
evidence for extra physical vortices. This is recorded in
`CANDIDATE_DISCOVERY_DVB-001.md` and
`RESULTS/rectangular_reference_20260924_134643.json`.

## Close-pair tracker control

For an 8 µm +1/−1 pair, raw, clustered, and supported detectors transition from
two features to zero between z=240 and 320 µm. The 2048² reference/downsample
run reproduces that transition, so the main disappearance is a modeled physical
annihilation control. The local-minimum contour occasionally drops one feature
at z=160–240 for shifted fields, showing a detector error before the physical
transition. This is a useful example of why raw trajectories require a
reference, not a discovery claim.

The local-minimum detector is explicitly bounded: at most 500 candidate
minima are considered by default after the candidate-pool cap described in the
change log. This does not affect the four-site analytical controls, but it does
affect dense random-field counts. Therefore random-field counts from this
detector must be reported as detector outputs, not as physical vortex
censuses.


## Required comparison standard

A physical count claim requires position and charge agreement, not merely
similar totals. EXP-0015 records true-positive, false-positive,
false-negative, charge-correct, and localization-error fields for analytical
controls. Detector agreement is not assumed from equal integer counts.
