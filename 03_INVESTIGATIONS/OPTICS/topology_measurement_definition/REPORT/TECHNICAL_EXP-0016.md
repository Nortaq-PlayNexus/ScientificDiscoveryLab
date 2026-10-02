# EXP-0016 — Technical report: topology-measurement definition

**Status:** COMPLETE / measurement-definition result / **NO NOVELTY CLAIM**  
**Question:** Q-O007 / HYP-OPT-TMD-001  
**Frozen protocol:** `CONFIG/prereg_EXP-0016.json`  
**Protocol SHA-256:** `c1935da7ac10d628386f313594a66e6a91c0466cb378da1ac1b02ca57895e54b`  
**Validation:** `RESULTS/validation_summary.json` = `PASS`

## 1. Question and scope

EXP-0016 asks a deliberately narrow question:

> Under what conditions do different discrete representations of an optical
> phase field disagree about the number, charge, or identity of singularities?

This is a mathematical and numerical measurement-definition study. It does not
search for new optical phenomena and does not revive the historical
`z=1280 µm`, `32 µm`, or 256² physical-topology claims.

The experiment uses analytical scalar complex fields with known phase winding,
not a historical detector output. It varies grid resolution, subpixel position,
charge, core width, pair separation, detector definition, and a modeled
propagation distance. The purpose is to identify exactly which observable each
estimator measures.

## 2. Definitions used in the result schema

A raw plaquette is not treated as a singularity location by default. Every row
therefore reports the following separately:

| Observable | EXP-0016 definition |
|---|---|
| `location_count` | Number of estimated singularity locations. For raw winding, same-sign connected components are used as the location proxy. |
| `component_count` | Number of connected estimator components or accepted records. |
| `winding_cell_count` | Number of nonzero plaquette winding cells. It is zero/not applicable for contour and Jacobian records. |
| `absolute_charge` | Sum of the absolute values of estimated charges. |
| `signed_charge` | Sum of estimated charges. |
| `charge_normalized_count` | `absolute_charge / max_truth_abs_charge`; this is a charge-mass unit, not a universal vortex count. |
| `joint_success` | Zero location-count error, absolute-charge error, and signed-charge error. |

This separation is the central result: “vortex count” is not a single
well-defined integer until the representation, estimator, and charge convention
are specified.

## 3. Methods

### 3.1 Analytical fields

For a vortex at `(x0,y0)` with integer charge `q`, the phase factor is
`exp(i q atan2(y-y0,x-x0))`. A finite-width positive amplitude depression
supplies a dark core while leaving a nonzero envelope away from the zero. The
field is multiplied over all prescribed vortices. The phase winding is therefore
analytically known before sampling.

The main amplitude model is a finite core depression,

```text
A_j(r) = 1 - 0.98 exp(-r_j² / (2 sigma²))
```

raised to a charge-dependent positive power for `|q|>1`, multiplied by a broad
Gaussian envelope. Exact-on-pixel samples are optionally set to complex zero.
Half- and quarter-pixel controls do not force a sampled zero. The first
amplitude implementation and the first candidate-selection implementation were
invalid for positive-control interpretation; both failures and corrections are
preserved in `CONFIG/changes.jsonl`.

### 3.2 Sampling and cases

The physical field of view is 64 µm. Grids are 32, 48, 64, 96, 128, 192, and
256 samples per side for the phase diagram. Single charges are −2, −1, +1, and
+2. Placement modes are exact pixel, half pixel, and quarter pixel. Core widths
are 1, 2, 4, and 8 µm.

Additional cases are:

- opposite-charge pairs with separations 2, 4, 6, 8, 12, and 16 µm;
- separated opposite-charge pairs with separations 4, 8, 16, and 32 µm;
- a four-vortex lattice with charges +1, −1, −1, +1;
- a seeded 96-trial randomized single-vortex subset.

The uncertainty subset samples grid, charge, core width, and independent x/y
subpixel shifts from seed 42. It intentionally covers the resolved regime
(minimum observed core-width/pixel ratio 1); it is not a substitute for the
low-resolution failure map.

### 3.3 Estimators

1. **Raw winding:** integer principal phase circulation on every plaquette.
2. **Clustered winding:** same-sign connected components of raw winding cells.
3. **Circular contour:** bilinear complex interpolation around dark-sample
   candidates, with a fixed two-pixel circular contour and deduplication.
4. **Jacobian locator:** local complex-linear/Jacobian zero fit followed by a
   local phase-winding check and deduplication.

The circular-contour and Jacobian methods are not assumed to be a physical
reference. They are independent numerical definitions whose agreement or
failure is measured.

### 3.4 Propagation and controls

The propagation subset uses scalar angular-spectrum propagation with a 694.3 nm
wavelength at z = 0, 160, 240, 280, 320, 400, 640, and 1280 µm. A modeled +1/−1
pair is tracked through the transition.

Controls include plane-wave and smooth no-vortex fields, a matched-amplitude
random-phase stress field, a 2048² analytical reference sampled at low-grid
centers, padding/cropping from 0 to 32 pixels, exact/subpixel placement,
progressive resolution, explicit edge-crossing translations with a full
padded-field comparison, and a separately written NumPy/SciPy implementation.

## 4. Results

### 4.1 Positive calibration

The final calibration contains 192 rows (four charges × three placements × four
grids × four estimators).

- Circular-contour and Jacobian rows matched the analytical location and both
  charge diagnostics in 96/96 calibration rows.
- Raw and clustered winding matched all diagnostics for the unit-charge cases in
  48/48 relevant rows.
- The four-vortex lattice matched in 28/28 estimator rows.
- The charge-two controls exposed the expected representation split: raw
  winding can represent one charge-two singularity as two or four unit winding
  cells, while contour/Jacobian estimators report one location with charge ±2.

A representative q=+2 case at a half-pixel placement gives:

| Estimator | Location proxy | Winding cells | Absolute charge |
|---|---:|---:|---:|
| raw winding | 2 | 4 | 4 |
| clustered winding | 2 | 4 | 4 |
| circular contour | 1 | not applicable | 2 |
| Jacobian locator | 1 | not applicable | 2 |

The raw and clustered signed charge remains +2 in this example. The discrepancy
is therefore in representation units and absolute-charge accounting, not a
failure of net-charge conservation.

### 4.2 Failure phase diagram

The phase diagram contains 1,652 rows. Across 413 grouped cases, at least one
estimator disagrees on location/component/charge semantics in 58 cases
(14.0%).

The disagreement rate by family is:

| Family | Cases | Disagreement rate |
|---|---:|---:|
| single | 336 | 13.7% |
| separated opposite pair | 28 | 14.3% |
| close opposite pair | 42 | 19.0% |
| four-vortex lattice | 7 | 0.0% |

For single vortices, the robust pattern is estimator-specific:

- raw and clustered winding agree with the truth for q=±1 across the tested
  grids and placements;
- for q=±2 at half-pixel placement, the raw/clustered representation splits
  into multiple unit cells even when the core spans many pixels; this is a
  charge-representation effect, not evidence for a resolution threshold;
- circular-contour and Jacobian rows are correct in the tested resolved cases,
  but both fail in the half-pixel, subpixel-core regime at observed
  core-width/pixel ratios 0.5 and 0.75;
- exact-pixel and quarter-pixel controls pass the tested single-vortex rows for
  contour/Jacobian, including q=±2.

For the close +1/−1 pair, raw, clustered, and contour estimators pass 41/42
cases. The Jacobian locator passes 33/42; its failures extend through the
low-separation bins and include one-location/one-charge outputs. The failure is
therefore not a universal pair threshold: it depends on the estimator's local
zero model and contour geometry.

The full machine-readable phase diagram is
`RESULTS/failure_phase_diagram.csv`. The plots in `FIGURES/` show the normalized
single-vortex, close-pair, and charge-two views.

### 4.3 Propagation subset

At z=0, the 128² and 256² exact-pixel controls report two locations and
absolute charge two. They remain at two through z=280 µm and report zero
locations/charge by z=400 µm. The 64² half-pixel control retains residual
features at z=320 µm for some estimators, while the 128²/256² controls do not.
This is a grid/placement sensitivity at the modeled annihilation transition,
not a new physical mechanism.

The z=1280 µm result is zero for the tested pair controls. It is not evidence
for the historical claim that a persistent physical topology appears at that
distance.

### 4.4 Nulls and stress fields

Plane-wave and smooth no-vortex fields return zero locations and zero charge for
all four estimators. A matched-amplitude random-phase field returns large raw
counts (for example, thousands of plaquettes at 256²); it is explicitly a
stress case, not a no-vortex null. Treating random phase as a zero-vortex null
would be invalid.

### 4.5 Independent implementation and reference controls

The independent NumPy/SciPy implementation covered 144 matched rows. It agreed
with the main implementation on record count, location count, absolute charge,
and signed charge in 144/144 comparisons.

The 2048² reference/downsample control contains 176 rows; the central-field
padding/crop control contains 160 rows. Central padding/cropping changed none
of the tested detector counts. The explicit edge-crossing control in §4.6 is a
separate finite-support test. The median relative field RMS difference between
the direct low-grid
field and the high-resolution reference sample was approximately `1.24e-4`.
Raw/clustered counts differed from the reference in 13.6% of the selected
reference rows, while contour/Jacobian location counts differed in 0% of those
rows. This reinforces that raw-cell semantics and exact-zero representation are
part of the measurement definition.

The seeded 96-trial uncertainty subset had 100% joint success for every
estimator, with bootstrap 95% intervals `[1.0,1.0]`. Its minimum observed
core/pixel ratio was 1, so it confirms robustness only in the resolved regime
and must not be used to dismiss the subpixel failure rows.

### 4.6 Boundary-crossing control

The explicit boundary-crossing stage contains 1,080 rows (three grids, two
charges, five sides, nine offsets, and four estimators). For singularities
strictly inside the original FOV but within one pixel of an edge, the full
padded field detects one location for the circular-contour and Jacobian
estimators, while the cropped field detects zero locations for contour and
0.067 locations on average for Jacobian. Raw and clustered winding average
0.8 locations in the cropped near-edge subset versus 1.05 in the full padded
field. For singularities outside the original FOV, the cropped field reports
zero while the full padded field reports one.

This is a finite-support and estimator-ROI effect. It is not evidence that a
physical singularity disappears at a pixel boundary. The boundary figure is
`FIGURES/boundary_crossing_control.png`; the machine-readable summary is
`RESULTS/boundary_summary.csv`.
## 5. Interpretation and hypothesis status

### Supported

- **H1 (semantic divergence): supported.** The same analytical q=+2 field can
  be reported as one charge-two location, two locations, or four unit winding
  cells depending on the estimator and placement.
- **H3 (independent reproduction): supported for the tested subset.** The
  independent implementation reproduces the main estimator outputs exactly on
  the registered comparison rows.
- **Charge normalization is necessary but not sufficient.** It repairs the
  q=+2 raw/cluster charge-mass comparison only when the estimator's location
  and component semantics are also specified.

### Not established

- **Universal failure law:** not established. The raw/clustered q=+2 behavior
  is phase-placement dependent across the full resolution range, while the
  contour/Jacobian boundary is concentrated near subpixel core widths. The
  tested data do not support one detector-independent dimensionless law.
- **Physical anomaly or new optics:** not supported. All observations are
  explainable by finite sampling, representation units, candidate selection,
  contour geometry, and modeled scalar propagation.
- **Complete dense/random regime map:** still incomplete; the EXP-0015 timeout
  limitations remain in force.

## 6. Limitations

1. The source fields are analytical scalar fields, not the historical
   DeepBeamScan field.
2. The pair field is a prescribed product of vortex factors; it is a controlled
   topology model, not a full Maxwell solution.
3. Circular-contour radius and candidate caps are fixed numerical choices.
   A future detector-geometry sweep is required before making a universal
   boundary claim.
4. The uncertainty subset is resolved-regime only and has 96 synthetic trials.
5. The 2048² reference is a reference sampling control, not an independent
   physical experiment.
6. Literature coverage is targeted rather than exhaustive. Search results and
   the existing matrix support the conclusion that measurement-definition and
   detector-choice issues are already well-motivated; they do not establish
   priority for this implementation.

## 7. Bird's-eye error view

A post-completion diagnostic dashboard is available at
`FIGURES/EXP-0016_birdeye_error_map.png`. It aggregates the frozen rows into
single-vortex core-scale, close-pair separation, boundary full-versus-crop, and
propagation-residual maps. The machine-readable hotspot list is
`RESULTS/birdeye_error_spots.csv`; the summary records 79 nonzero hotspot cells
(60 single-core-scale, 8 close-pair, and 11 boundary cells). These are error
fractions, not vortex counts, and the visualization introduces no new claim.

## 8. Reproduction

From `C:\Users\natha\ScientificDiscoveryLab`:

```powershell
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_topology_definition.py --stage all
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_reference_controls.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_boundary_controls.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_uncertainty.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\independent_topology_replication.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\analyze_topology_results.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\make_figures.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\make_birdeye_error_map.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\validate_topology_results.py
```

## 9. Final classification

**COMPLETE / measurement-definition result / NO_NOVELTY_CLAIM.**

The defensible contribution is a reproducible warning that “vortex count” is
ambiguous unless the representation unit and estimator are named. The data do
not support a new physical topology claim, and no historical anomaly is
revived.
