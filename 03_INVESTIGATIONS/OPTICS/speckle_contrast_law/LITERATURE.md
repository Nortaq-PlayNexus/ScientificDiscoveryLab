# LITERATURE — Q-O001 speckle contrast

## Known science (what we cite)

- **Goodman, J.W., *Statistical Optics* (Wiley, 1985/2015); *Speckle Phenomena in
  Optics* (Roberts & Co., 2007).** Source for: fully-developed speckle intensity is
  exponentially distributed (contrast 1); summing M independent speckle intensities
  gives a gamma-distributed intensity with contrast 1/sqrt(M); finite detector
  pixel / grid correlations reduce effective independent modes and bend C(M) away
  from the ideal law.
- Standard undergraduate laser-physics treatments of speckle averaging.

## What we did NOT need to search

This is a textbook reproduction/validation task, not novelty-seeking. No claim of
novelty is made, so no priority search is relevant. Per RESEARCH_RULES.md we do not
say "nobody has done this"; we say this is a known law and we reproduced it.

## Local prior art (this machine)

- `code\coherent-optical-ai-sandbox`: has speckle generators
  (`app/optics/speckle.py`) and a validated angular-spectrum propagator, plus the
  sandbox's earlier audit lessons about grid-locked detectors that directly inform
  the follow-on Q-O002 (vortex density). No sandbox file was used or modified for
  EXP-0002 (independent implementation by design).

## Status

- Literature check: **not novelty-relevant** (known law).
- Gaps for future work: multi-aperture/finite-pixel covariance models for the
  observed low-N deficit (optional analytic cross-check).