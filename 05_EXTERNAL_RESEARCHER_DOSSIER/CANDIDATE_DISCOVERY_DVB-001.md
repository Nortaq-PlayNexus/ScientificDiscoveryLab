# CANDIDATE_DISCOVERY_DVB-001 — Rectangular-grid contour overcount

**Status:** CLOSED / REFUTED AS A PHYSICAL ANOMALY / ARTIFACT  
**Observed:** 2026-09-24  
**Experiment:** EXP-0015, exploratory geometry control

## 1. Observation

For the well-separated four-vortex analytical control, the raw, clustered, and
supported-clustered detectors return four features on the tested rectangular
grids. The independent local-minimum contour detector returns 5 or 6 features
for some subpixel shifts at z=+1280 µm in rectangular domains:

- `(128,256)`, shift 0.25 px: 5 features, net charge +1;
- `(128,256)`, shift 0.75 px: 6 features, net charge 0;
- `(256,512)`, shift 0.25 px: 5 features, net charge −1;
- `(256,512)`, shift 0.50 px: 6 features, net charge 0.

The square controls and the other three detectors remain at four features in
the corresponding rows. The stored `truth_match` fields at z>0 are not used as
truth here: the vortices can move under propagation, and matching them to their
initial z=0 coordinates is an invalid endpoint. A propagated high-resolution
reference is required before interpreting localization or false-negative
fields.
## 2. Exact reproduction command

```powershell
python 03_INVESTIGATIONS\OPTICS\discrete_vortex_bias\CODE\run_geometry.py
```

Raw output:

`03_INVESTIGATIONS/OPTICS/discrete_vortex_bias/RESULTS/geometry_controls_20260924_134416.json`

## 3. Seed and parameters

- Seed: deterministic 42 for the analytical field;
- physical FOV: 256 µm per axis;
- wavelength: 694.3 nm;
- z: 0, 640, 1280 µm;
- shifts: 0, 0.25, 0.5, 0.75 px;
- rectangular shapes: 128×256, 256×128, 256×512, 512×256;
- detector contour radius: 2 px; 32 contour samples.

## 4. Statistical observation

This is a deterministic estimator discrepancy, not an inferential p-value. The
relevant effect size is `count_local_contour − count_other_detectors = +1 or
+2` in 4 of 192 rectangular rows, concentrated in two shapes and nonzero
shifts. No multiplicity-adjusted novelty test is appropriate until the source
of the discrepancy is identified.

## 5. Initial interpretation

The result is consistent with a detector-specific interpolation/contour
failure or boundary/aspect-ratio interaction. It is not evidence that the
complex field contains extra physical vortices: the independent raw winding
estimator remains at the analytical truth, and the continuous field has known
charge-zero four-site topology.

## 6. Alternative explanations

1. The contour radius is too small after rectangular resampling.
2. Bilinear interpolation of a complex field near a phase branch cut creates a
   false winding.
3. Local-minimum candidate selection creates two minima for one core.
4. Periodic boundary wrap-around is being interpreted as an interior contour.
5. The physical field’s continuous topology changes under propagation (must be
   checked against a high-resolution reference).
6. The four-site analytical field is not the relevant historical field and the
   effect does not generalize.

## 7. Required controls

- rerun at 2048² oversampled reference and downsample;
- vary contour radius continuously (1.5, 2, 2.5, 3, 4 px);
- compare complex interpolation versus phase-angle interpolation;
- use circular and square contours;
- exclude a boundary band and repeat with an interior ROI;
- test all shifts on a fine 0.01-px grid;
- repeat with independent SciPy detector code;
- compare raw winding positions and complex-field local minima;
- run the same rectangular geometry on a close-pair/high-order control.

## 8. Falsification criteria

Close the candidate as an implementation artifact if the excess disappears
under a mathematically justified contour/interpolation change, is confined to
one detector, or is absent when the high-resolution reference is downsampled.
Promote only if the excess survives all controls, agrees across independent
detectors, and is linked to a reproducible dimensionless sampling variable.

## 9. Red-team result and closure

The decisive oversample→downsample control was run at 2048² for all four
rectangular shapes, shifts, and z=640/1280 µm:

`03_INVESTIGATIONS/OPTICS/discrete_vortex_bias/RESULTS/rectangular_reference_20260924_134643.json`

For the problematic rows, the high-resolution reference downsampled to the
coarse rectangle returns exactly four local-minimum features, while direct
coarse propagation returns 5 or 6. The path difference is therefore −1 or −2
features exactly where the candidate appeared. The raw, clustered, and
supported detectors return four on both paths.

An independently written SciPy circular-contour detector was also run on
the same rectangular controls (`RESULTS/independent_contour_20260924_141208.json`);
it returned four features in all 32 tested rows. Therefore the 5–6 result is
specific to the main local-minimum candidate/interpolation implementation, not
a universal property of circular contours. This makes the candidate even more
clearly an implementation artifact.


## 10. Current classification

**REFUTED as a physical anomaly / ARTIFACT.** This is a reproducible numerical
failure mode, not a new discovery. The strongest generalization still open is
whether close-pair and dense-field regimes follow a universal scaling law.

## 11. EXP-0016 cross-reference

EXP-0016 independently confirms the broader measurement-definition issue:
raw winding cells, connected components, contour locations, and charge mass
are distinct observables. It does not reopen DVB-001. The rectangular candidate
remains closed as a direct-coarse-grid implementation/downsampling artifact.
