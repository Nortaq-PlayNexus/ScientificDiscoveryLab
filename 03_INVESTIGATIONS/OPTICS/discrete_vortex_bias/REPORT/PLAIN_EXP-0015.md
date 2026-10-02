# EXP-0015 — Plain-language report

## What did we test?

We built a clean computer test with a known number of optical-vortex-like phase
singularities. We then changed the grid, shifted the field by fractions of a
pixel, changed propagation distance and wavelength, added padding, tried
several detectors, and compared coarse calculations with a 2048² reference.

## What happened?

The easy, well-separated four-vortex test stayed at four features in every
detector. That is a useful negative control: the old “more structures appear”
result does not appear in a clean test.

We did find important measurement effects:

- A charge-+2 vortex can appear as two or four unit winding cells in a raw
  counter, while another detector reports one charge-+2 object. The charge is
  not necessarily wrong; the meaning of “count” is different.
- A contour detector can miss or overcount close vortices depending on contour
  size and subpixel position.
- A rectangular-grid contour excess disappeared when the field was propagated
  at very high resolution and then sampled down. It was a detector artifact.
- A close vortex–antivortex pair disappeared at the same propagation distance
  in coarse and high-resolution calculations. That agrees with ordinary
  vortex-pair annihilation, not a new discovery.
- Different detectors can report very different counts for the same random
  field even when each is stable across random seeds.

## What was independently checked?

The propagation passed reversibility, energy, NumPy/torch, and separate SciPy
checks. A separately written contour detector did not reproduce the
rectangular-grid excess.

## What does this prove?

It shows that “how many vortices?” is not one well-defined computer number
unless the detector, sampling, contour, and boundary rules are specified. It
does **not** show new physics, symbolic content, or a new universal law.

## What is still unknown?

The old 256²/z=1280 µm simulation still does not tell us the physical number of
complex-field zeros. We would need a better high-resolution locator and, for a
real physics claim, a laboratory phase measurement.

## Bottom line

No new physical discovery was established. The honest result is a carefully
controlled numerical failure-mode study: some apparent “new vortices” were
created or removed by the measuring procedure, while one modeled pair
annihilation survived the high-resolution check.
