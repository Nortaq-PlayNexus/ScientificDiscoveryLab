# Planning checks (disclosed, NOT part of the registered result)

Before freezing EXP-0003, three throwaway scripts were run outside the lab to sanity
check the analytic formula and the detectors. They are reproduced here in spirit so
the design's assumptions are auditable. They are explicitly NOT the registered
experiment and their numbers must not be reported as EXP-0003 results.

## Check 1 — formula factor
For thin ring spectra at N=512, measured/predicted (spectral n_pred) was 0.980, 0.963,
0.945 at k0 = pi/8, pi/4, pi/2 for a *thick* shell; the special-case k0^2/(4*pi)
differed from the spectral prediction because a thick discrete shell has
<kx^2> > k0^2/2. Conclusion: use the exact discrete spectral n_pred, not k0^2/4pi,
as the primary prediction.

## Check 2 — resolution/bandwidth
- Narrow ring (half-width 0.20): ratio -> ~1.01 at N=512/1024 for all k0.
- Thick ring (0.75) and Gaussian (sigma_k=0.5): ratio ~0.91-0.94 and did NOT converge
  with N. Diagnosis: power near the Nyquist shell is under-resolved by the plaquette
  detector, a pixels-per-wavelength limit, not a shrinking-in-N artifact.

## Check 3 — pixels-per-wavelength ladder
At N=1024, narrow ring: ratio = 1.012, 1.002, 1.012, 1.006, 0.989 at wavelengths
4, 8, 16, 32, 64 px. This motivated prediction S3 (failure zone tied to the high-k
tail) and the primary tolerance of 3%.

## Consequence for design
- Primary H0 tested on well-resolved narrow-band cells (P >= 8).
- Broadband deficit treated as a characterisation (S3), not a deviation claim.
- Half-pixel shift test promoted to a first-class control (C4) after the predecessor
  project's grid-locking finding.

These checks are also noted in PREDICTIONS.md for full disclosure.
