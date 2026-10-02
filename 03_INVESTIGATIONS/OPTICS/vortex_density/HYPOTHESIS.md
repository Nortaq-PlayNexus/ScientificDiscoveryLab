# HYPOTHESIS — HYP-002 (vortex density in random wave fields)

Registered in the lab HYPOTHESES.md as HYP-002. Frozen under EXP-0003.

## Statement

For zero-mean, statistically isotropic complex Gaussian random fields E with power
spectrum S(k), the measured phase-singularity number density n_meas equals the
Kac-Rice prediction

    n_pred = <|dE/dx|^2> / (2 * pi * <|E|^2>)

to within 3% relative for fields whose energy is concentrated at wavelengths well
above the grid Nyquist limit, i.e. for pixels-per-wavelength P = 2*pi/k0 >= 8, with
99% bootstrap CIs contained in +/-5%.

Special case (frozen sub-prediction): for a narrow-band isotropic field of
wavenumber k0, n_pred -> k0^2 / (4*pi).

## Secondary statements (characterisation)

- S1 (charge neutrality): the signed counts of +1 and -1 vortices are equal within
  Monte-Carlo error for every tested spectrum.
- S2 (no grid locking): n_meas is invariant (within 3%) under a half-pixel
  translation of the field; i.e. this counter does NOT inherit the grid-locking of
  the predecessor project's counter.
- S3 (failure zone): the measured/predicted ratio falls below 1 as continuum power
  approaches the Nyquist frequency, and recovers toward 1 as pixels-per-wavelength
  increases. This localises the failure zone to under-resolved high-k power.

## Distinction from the null

The null (H0) is that n_meas = n_pred within tolerance in the well-resolved regime.
The alternative (H1-dev) is a mismatch that persists as pixels-per-wavelength
increases. Only H1-dev would be interesting; S1-S3 are characterisation, not
discovery.

## Prior expectation

Both H0 and the textbook form k0^2/(4*pi) are well established. We expect to
reproduce them (evidence state CONTROLLED). Offline formula checks during planning
gave measured/predicted ~ 1.01 for narrow-band fields (see EXPERIMENT_PLAN.md notes);
these are planning checks, NOT the registered result.

## What would falsify H0

- A ratio whose 99% CI excludes 1 by more than the 3% tolerance in the well-resolved
  regime, that does not shrink as pixels-per-wavelength increases.
- A failure of charge neutrality beyond Monte-Carlo error.
- A shift-dependent count (grid locking).
