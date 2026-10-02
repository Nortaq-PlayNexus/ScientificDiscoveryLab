# CANDIDATE_DISCOVERY_DVB-002 — Contour-radius resolution non-monotonicity

**Status:** NEW / INVESTIGATING / LIKELY KNOWN NUMERICAL ARTIFACT  
**Observed:** 2026-09-24  
**Experiment:** EXP-0015 detector-size sweep

## Observation

For a known +1/−1 pair, the local-minimum contour detector's count error
changes non-monotonically with contour radius. In some grid/phase cells,
increasing the radius resolves a close pair; in others it merges the pair or
suppresses a core. The full matrix is
`RESULTS/detector_size_20260924_134854.json` (1,764 rows).

Examples from the raw data:

- 64²: radius 1.5–2 px resolves all tested shifts from roughly 12 µm, while
  radius 4–5 px requires roughly 24 µm;
- 256²: radius 1.5–2 px resolves from roughly 4 µm, but intermediate radii
  produce occasional extra features;
- 512²: radius 5 px resolves the 2 µm pair, while smaller radii remain
  shift-sensitive.

## Initial interpretation

The natural variables are not pixel pitch alone but the ratios
`separation/Δx` and `radius/Δx`, plus subpixel phase. A contour that is too
small can straddle interpolation branch cuts or fail to enclose a core; a
contour that is too large can enclose both members of a dipole or cross a
neighboring phase structure. This is a plausible discrete-topology failure
mode, not evidence for extra physical singularities.

## Required falsification tests

1. Independently implement the contour winding and candidate selection.
2. Use exact complex zeros and an oversampled reference as positional truth.
3. Sweep radius continuously and contour shape (circle, square, ellipse).
4. Compare complex-field interpolation with phase-angle interpolation.
5. Test whether the residual depends only on normalized ratios after padding,
   scale, and detector architecture converge.
6. Compare with raw plaquette and connected-component estimators.

## Exact-zero red-team update

`RESULTS/exact_zero_20260924_135547.json` repeated the pair control with an
exact complex-zero core (`floor=0`) and a finite floor (`0.03`). The raw,
clustered, and supported detectors return two in both cases at grids 64–512.
The local-contour detector returns 0/1/2 only at the coarsest 64² rows, with the
same qualitative failures for both floors. Thus the effect is not explained by
the amplitude floor alone; it is a contour/candidate-geometry failure.


**INCONCLUSIVE**, trending toward **KNOWN NUMERICAL ARTIFACT**. No Level 3+
claim is authorized. A single dimensionless scaling law has not been shown.
