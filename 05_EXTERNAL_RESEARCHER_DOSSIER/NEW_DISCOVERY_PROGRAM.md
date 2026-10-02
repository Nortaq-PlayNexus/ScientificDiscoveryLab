# New discovery program — EXP-0015

## Objective

Determine whether discrete optical-vortex detectors create reproducible
count bias, and if so whether the bias is a detector-specific failure,
a sampling/downsampling effect, a propagation/boundary effect, or a genuinely
unexplained phenomenon.

The program does **not** assume that the historical DBS result is interesting.
The corrected historical target-distance audit is a lead and a control, not a
positive control for new physics.

## Frozen design

The preregistration is
`03_INVESTIGATIONS/OPTICS/discrete_vortex_bias/CONFIG/prereg_EXP-0015.json`
(SHA-256 recorded inside the file). The primary endpoint is detector-count bias
relative to analytically known topology. Promotion requires all of:

1. grid convergence;
2. padding convergence;
3. subpixel-shift robustness;
4. detector independence;
5. seed robustness;
6. wavelength/scale behavior;
7. independent implementation;
8. suitable null rejection; and
9. literature review.

## Stages and information gain

| Stage | Question | Primary falsifier | Status |
|---|---|---|---|
| Calibration | Do independent detectors recover known single, pair, double, and four-vortex fields? | Known-topology controls and plane wave | **COMPLETE for seed 42; corrected detector calibration logged** |
| Convergence | Do counts stabilize with grid, z, wavelength, and physical sampling? | Resolution and padding changes | **RUNNING** |
| Oversample→downsample | Is error introduced by propagation or by sampling/detection? | Difference between direct coarse propagation and high-resolution reference downsampling | **COMPLETE for square/rectangular/close-pair controls; dense/random extension incomplete** |
| Nulls | Does the effect exceed matched-spectrum/matched-amplitude/random-field baselines? | Matched-spectrum null and FDR | **PARTIAL**: single-surrogate null + six-seed random ladder complete; 50-surrogate matched-null run timed out |
| Independent replication | Does a separately written implementation agree? | SciPy FFT/raw-winding and SciPy contour replication | **COMPLETE for tested controls** |
| Red team | What simple explanation kills the candidate? | Shift, padding, precision, seed, detector, and implementation swaps | **COMPLETE for identified candidates; direct-reference remains inconclusive** |

## Candidate handling

Any unexpected result receives a separate candidate file with observation,
command, seed, raw path, statistic, alternatives, controls, and falsification
criteria before it is expanded. No candidate is promoted merely because its
p-value is small after scanning many cells.

## Current honest conclusion

The historical physical-topology claims remain rejected or unresolved. The
new program has now reproduced a narrower, defensible result: finite discrete
optical-vortex measurements have detector- and geometry-dependent failure
modes. The rectangular excess was killed by high-resolution and independent
controls; the remaining charge/close-pair discrepancies are classified as
known numerical representation effects. The full dense/random map and a
50-surrogate null run exceeded their practical budgets, so no broader scaling
claim is made.
