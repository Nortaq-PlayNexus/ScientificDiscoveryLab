# Detector-size analysis — EXP-0015

**Source:** `03_INVESTIGATIONS/OPTICS/discrete_vortex_bias/RESULTS/detector_size_20260924_134854.json`

## What was varied

A known +1/−1 pair was sampled at grids 64–512, separations 2–48 µm,
subpixel shifts 0–0.75 px, and local-contour radii 1–5 px. The pair has two
continuous singularities, so count=2 is the known-topology target.

## Result

The detector does not have one monotone “minimum separation” independent of
its radius. At coarse grids, small radii can miss both cores, intermediate
radii can resolve them, and large radii can merge the pair or suppress one
member. For example:

- at 64², a 1.5–2 px contour resolves the pair for all shifts only from about
  12 µm separation, while a 4–5 px contour requires about 24 µm;
- at 256², a 1.5 px contour resolves from about 4 µm, a 2 px contour from about
  4 µm with occasional extra features, and larger radii have non-monotone
  errors;
- at 512², a 5 px contour resolves the 2 µm pair, while 1–2 px radii still
  produce misses/extra features at some shifts.

The full result contains 1,764 rows. The count error is therefore a joint
function of separation/pixel pitch, contour radius/pixel pitch, subpixel phase,
and local candidate selection. It is not legitimate to report a single
“8-pixel floor” without specifying the detector geometry.

## Interpretation

This is a reproducible numerical failure mode of the bounded local-contour
estimator. It is consistent with the discrete-topology literature, where
finite paths and finite differences make topological charge discontinuous
under perturbations. It is not a new physical phenomenon and has not passed
the independent-implementation/novelty gates.

## Next decisive test

Repeat the same radius/phase matrix with an independently written contour
locator and a 2048² reference, then test whether any residual error collapses
onto a single dimensionless variable such as `(separation/Δx)/(radius/Δx)`.
Do not promote a scaling law from this exploratory grid alone.
