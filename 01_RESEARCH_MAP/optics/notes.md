# OPTICS — research map

## Known (relevant to lab)
- Coherent propagation: angular spectrum method (ASM), Fresnel; unitary, energy
  conservation to machine precision on the sandbox engine (verified).
- Fully-developed speckle: exponential intensity stats, contrast C=1; summed
  independent speckles give C=1/sqrt(M). Vortex (phase singularity) density laws:
  Nye-Berry / Freund prefactors in terms of correlation length.
- Talbot / self-imaging conditions are exact and were ruled out at sampled planes in
  sandbox (first fractional plane beyond sampled z_max).
- Beams: LG, Bessel, structured fields — published invariants and their limits.

## Open / contested locally
- Corrected handling of discrete vortices: the sandbox's winding counter proved
  grid-locked; correct density estimation with ROI + boundary rules is unsolved
  cleanly here (that is the O2 project).
- Quantified decodable-information ceilings for speckle from structured phase masks
  (O4) — directly serves the DMT-laser dossier's decisive tests.

## Computable on this machine
- Anything the sandbox engine can do (speckle, ASM, interference, structured light),
  headless. Grid <= 1024^2 comfortable; 2048^2 possible but slow on CPU torch.

## Core references (visual)
- Goodman, "Statistical Optics" / "Speckle Phenomena in Optics".
- Nye & Berry (1974); Freund (1998); Berry (2007).
- Sandbox literature files: `code\coherent-optical-ai-sandbox\research\literature\*`.