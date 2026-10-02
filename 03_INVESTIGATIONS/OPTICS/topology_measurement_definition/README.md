# EXP-0016 — Topology-measurement definition experiment

## Question

Under what conditions do different discrete representations of an optical
phase field disagree about the number, charge, or identity of singularities?

This experiment follows the EXP-0015 finding that “vortex count” is not a
unique observable until the estimator and charge convention are specified. It
does **not** search for new optical physics and does not revive any historical
anomaly.

## Scope

Analytical scalar fields are constructed with known phase topology:

- charges −2, −1, +1, and +2;
- multiple separated vortices;
- close vortex/antivortex pairs;
- pairs propagated toward annihilation;
- singularities exactly on pixels, halfway between pixels, and at quarter-pixel
  offsets;
- reduced sampling across a fixed physical field of view.

Each detector receives the identical complex field. Results report several
different observables rather than one ambiguous count:

- singularity-location count;
- connected-component count;
- raw winding-cell count;
- absolute charge `Σ|q|`;
- signed charge `Σq`;
- charge-normalized count;
- false positives/negatives and localization error.

## Planned detectors

1. Raw plaquette phase winding.
2. Same-sign connected-component clustering.
3. Local-minimum circular contour winding with complex interpolation.
4. A local Jacobian/phase-gradient locator.
5. An independently written SciPy implementation for a subset.

## Promotion rule

This is a measurement-definition study. A result may be called a universal
failure law only if it survives exact-position controls, progressive sampling,
charge normalization, independent implementation, and a preregistered
dimensionless collapse. Otherwise it is reported as a detector-specific
numerical artifact.

## Reproduction

```powershell
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_topology_definition.py --stage calibration
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_topology_definition.py --stage phase_diagram
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_topology_definition.py --stage propagation
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\independent_topology_replication.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\validate_topology_results.py
```

Additional preregistered controls and final aggregation:

```powershell
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_reference_controls.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_boundary_controls.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\run_uncertainty.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\analyze_topology_results.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\make_figures.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\make_birdeye_error_map.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\make_experiment_summary.py
python 03_INVESTIGATIONS\OPTICS\topology_measurement_definition\CODE\make_manifest.py
```

The completed classification is **measurement-definition result / no novelty
claim**. The key result is that “vortex count” is estimator-dependent: raw
winding cells, connected components, estimated locations, and charge mass are
different observables. Historical EXP-0015 and sandbox files are not modified.
