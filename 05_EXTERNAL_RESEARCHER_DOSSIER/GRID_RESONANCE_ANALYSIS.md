# Grid resonance analysis

## Historical conclusion retained

The old `z=+1280 µm` excess is not accepted as physical topology. The strongest
historical reasons are:

- the archived R14 scripts passed `1280` to a metre-based propagation API;
- the corrected EXP-0007 audit gives 176 DBS features at the true distance;
- fixed-FOV refinement gives a non-convergent 150/176/204/220 diagnostic;
- the old DBS output is not an independently validated complex-zero locator;
- historical shifts, padding, and grid probes showed strong grid dependence.

## New EXP-0015 test

The new program treats grid resonance as a measurement question. It records
count(z), bias(z), detector agreement, padding range, subpixel variation,
wavelength dependence, and direct-coarse versus oversample→downsample paths.
The exact output files are under
`ScientificDiscoveryLab/03_INVESTIGATIONS/OPTICS/discrete_vortex_bias/RESULTS/`.

A peak is not promoted if it:

1. occurs at only one grid size;
2. changes materially with padding;
3. moves with subpixel translation;
4. is produced by only one detector;
5. disappears in the independent implementation; or
6. is reproduced by a matched-spectrum/null field.

## Current status

The primary EXP-0015 well-separated matrix and 2048² reference/downsample
control are invariant at four features, so they do not reproduce a physical
count resonance. A separate rectangular-grid red-team found a 5–6 feature
local-contour result in selected direct coarse rows, but the 2048² reference
returned four; this is now classified as a direct-coarse-grid detector artifact.
The historical resonance remains a **known/expected numerical artifact with
unresolved physical-count semantics**, not a new physical length or topology.
