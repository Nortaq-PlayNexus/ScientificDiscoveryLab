# Open problems — coherent optical field investigation

Updated 2026-09-24. These are deliberately framed as unanswered questions, not
claims that an effect exists.

## Blocking problems

1. **What is the true physical singularity count after propagation?**
   The corrected EXP-0007 DBS count at +1280 µm is 176, but the detector is
   non-convergent and is not independently validated as a zero locator.
2. **Which detector semantics are being measured?** EXP-0016 explicitly
   separates raw plaquette cells, connected components, estimated locations,
   and charge mass. Remaining work is to sweep contour/interpolation geometry,
   not to reinterpret these units as one count.
3. **Does oversample→downsample separate propagation error from detection
   error?** It is complete for the square, rectangular, and close-pair controls;
   the dense/random extension remains incomplete after its computational timeout.
4. **Are any residual effects convergent under padding, wavelength, scale,
   non-power-of-two grids, and subpixel shifts?** The tested EXP-0016
   reference/padding controls pass; a detector-geometry and dense/random sweep
   remains incomplete.
5. **Can a candidate survive an independently written propagation and detector
   implementation?** The registered single-vortex subset passes 144/144
   comparisons; a full second-architecture propagation study remains open.

6. **Exact-zero and boundary controls:** completed in EXP-0016 for exact,
   half-, and quarter-pixel placements plus explicit edge crossings with a
   full-padded versus cropped comparison. The remaining extension is a
   systematic interpolation/radius geometry sweep.

## Strongest remaining question

For a continuous complex field with known phase singularities, map the
probability of false positives, false negatives, charge errors, and
localization error as a function of pixels per core, contour radius,
interpolation order, candidate seeding, FFT period, padding, and propagation
distance. EXP-0016 maps the first generation of this question for fixed
estimator geometries and shows that raw/clustered and contour/Jacobian failure
regimes are not one universal boundary. A completed sweep across detector
geometries and a second independent architecture is still required before any
scaling law is claimed.

## Lower-priority but important

- Track individual singularities through z and distinguish physical pair
  creation/annihilation from detector crossings.
- Measure pair correlation, charge correlation, nearest-neighbour
  distributions, and boundary proximity after convergence.
- Test rectangular and non-square periodic domains deliberately.
- Determine whether a scale law exists for detector bias, rather than fitting
  many functions after the fact.
- Extend the literature audit with expert review of digital-topology and
  singular-optics detection papers.

## EXP-0016 resolution

The first topology-measurement definition experiment is complete. Its bounded
result is that count semantics must be reported as separate location,
component, winding-cell, absolute-charge, and signed-charge observables. This
closes the current search for a physical “extra vortex count” interpretation;
it does not close the broader detector-geometry scaling problem.


## Explicitly closed as current discovery targets

Unless new evidence contradicts the audits, do not revive: “laser contains
code,” the original ~45-feature claim, the 21/24 split, emergent 32 µm spacing,
phase-randomization as information, z=1280 µm as new topology, or the 256²
pixelation excess as physical topology.
