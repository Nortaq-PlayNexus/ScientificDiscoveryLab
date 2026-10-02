# Planning checks (disclosed, NOT part of the registered result)

Before freezing EXP-0015, offline sanity checks were run outside the lab to
confirm the reference constants, choose the test grids, and set tolerances.
They are recorded here so the design's assumptions are auditable. They are
explicitly **not** the registered experiment and their numbers must not be
reported as EXP-0015 results.

## Check 1 — UNESCO coefficient transcription

The Wong & Zhu (1995) coefficient table was taken from two independent web
renderings of the same algorithm (`tsuchiya2.org/soundspeed/unesco.htm` and the
SONAR.m `sound_speed_sea_unesco` documentation, which also carries an Octave
implementation). Both agree on every coefficient except a sign typo in the
markdown table for A01; the Octave source in the second rendering uses
A01 = -1.262e-2, matching the first source. The code version was adopted.

Hand-evaluated pure-water values Cw(T, 0 bar) against the standard fresh-water
sound-speed table at 1 atm:

| T (degC) | table (m/s) | Cw computed | rel dev |
|---|---|---|---|
| 0 | 1402.39 | 1402.388 | 0.000 % |
| 5 | 1426.50 | 1426.168 | 0.023 % |
| 10 | 1447.10 | 1447.280 | 0.012 % |
| 15 | 1466.00 | 1466.014 | 0.001 % |
| 20 | 1482.00 | 1482.359 | 0.024 % |
| 25 | 1497.00 | 1496.704 | 0.020 % |
| 30 | 1509.50 | 1509.144 | 0.024 % |
| 35 | 1520.00 | 1519.826 | 0.011 % |

Worst case 0.024 %, comfortably inside the 0.05 % gate. This is why S1a's
tolerance is 5e-4.

## Check 2 — UNESCO vs Mackenzie agreement

Mackenzie's nine-term fit was re-derived from its published form and evaluated
at the same fresh-water points. Agreement is worst near 10-15 degC
(~0.055 %) and best near 30 degC (~0.006 %). Hence S1b's tolerance is 1.0e-3,
deliberately looser than S1a because these are two independently fitted
surfaces, not one surface against itself.

At S = 35, T = 0, P = 0 both give ~1449 m/s (UNESCO 1449.18, Mackenzie 1448.96),
0.015 % apart — this is the frozen C2 positive control.

## Check 3 — acoustic tube Q and sweep resolution

Wall-loss attenuation for a thin boundary layer,

    alpha_wall = sqrt(nu * omega / 2) / (a * c) * (1 + (gamma-1)/sqrt(Pr)),

evaluated at a = 0.010 m gives alpha_wall = 6.52e-3 Np/m at 2964.7 Hz, hence
Q = omega/(2 alpha_wall c) ~ 960 and a half-power width of ~3 Hz for the
fundamental of the 0.25 m column. A 10 Hz sweep would have missed or
mis-located these peaks, so the preregistered sweep step is **0.5 Hz** over
[100, 20000] Hz (39801 samples per cell), with parabolic sub-grid refinement.
This single check drove the largest cost in the experiment.

## Check 4 — classical absorption algebra

The classical (viscosity + thermal conduction) absorption reduces to

    alpha_cl / f^2 = (8 pi^2 / 3) * nu / c^3  +  thermal term.

With the literature values quoted by the source we reproduce (nu = 1.44e-6 m2/s
at 280 K, c = 1500 m/s) this gives 1.123e-14 s2/m against the published
1.1e-14 s2/m — a 2 % match, which is why S3a's tolerance is 10 %.

**Cost check that moved the gated band.** Because alpha grows as f^2 while
lambda shrinks as 1/f, the cell count for a fixed optical depth over a fixed
band scales as 1/f. Resolving a 14.8 mm wavelength (100 kHz) over the ~4 km of
fresh water needed for alpha*z ~ 1 costs ~10^7 cells per solve; at 1 MHz the
same optical depth costs ~2x10^6 and at 30 MHz ~5x10^4. The original draft
gated {100 kHz, 300 kHz, 1 MHz, 3 MHz}, which would have needed 10^7 cells at
the low end and (worse) spent most of the band where absorption over any
laboratory distance is unmeasurably small. Before any registered execution the
gated band was therefore set to **{1, 3, 10, 30} MHz** with
z_max = min(1.0 m, 3/alpha), and the audio-band value moved to
characterisation. This is a design correction made *before* the prereg was
frozen, not a post-hoc change; it is recorded here and in CHANGELOG.md.

The thermal term was estimated at ~1.3e-7 s2/m-equivalent, i.e. under 1e-3 of
the viscous term for water (gamma ~ 1.001), and is reported but not gated.

At 20 degC the classical value is 8.11e-15 s2/m against the accepted total
2.50e-14 s2/m, a ratio of 3.1. The literature ratio (at 280 K) is ~2.3. Both are
consistent with the same structural-relaxation excess; the difference is that
nu is ~30 % larger at 280 K. Reported as characterisation only.

## Check 5 — Gorkov contrast factor

phi(polystyrene in water) = (5*1050 - 2*998.2)/(2*1050 + 998.2) -
2.16e-10/4.6e-10 = 1.05016 - 0.46957 = **+0.5806** > 0, so particles go to
pressure nodes — consistent with the acoustophoresis literature (polystyrene in
water accumulates at nodes). Because phi is comfortably away from zero, the
sign-reversal control C9 is unambiguous.

Timing was checked for a = 10 um at f = 1 MHz, p0 = 1e5 Pa: migration proceeds
on a minutes timescale, so T = 2000 s and dt = 0.02 s are sufficient and the
a^2 law is visible across a = {5, 10, 20} um.

## Check 6 — Minnaert constant

Evaluating omega_0^2 = (3 kappa (P0 - P_vap) + 2 sigma (3 kappa - 2)/R0) /
(rho R0^2) for R0 in {0.5, 1, 2, 5, 10} mm gives f_0 R_0 ~ 3.25 Hz m for all
five, against the literature compact form "R0 f0 ~ 3 Hz m". Hence S5b gates
[3.0, 3.5] Hz m rather than a single value.

## Check 7 — Faraday threshold magnitude and tongue width

For mode m = 8 in a 0.10 m channel on a 0.010 m layer, the dispersion gives
omega_0 = 59.78 rad/s and mu = 2 nu k^2 = 0.1267 /s, so the damped-Mathieu
n = 1 prediction Gamma_c = 4 mu/omega_0 = **0.0085**. This set the Gamma ladder
{0.002 ... 0.016} in steps of 0.002, giving a crossing bracket with ~12 %
resolution against a 30 % gate.

The tongue half-width in drive frequency is ~ h/4 (h = Gamma here) for the
undamped Mathieu system; at Gamma = 0.01 that is 0.25 %, far narrower than the
6-10 % spacing between adjacent modes of the channel. This is why S6d drives
*exactly* at 2 omega_0(m) for each test mode: a drive between two modes is
correctly predicted to excite nothing, which is itself checked by S6f.

## Check 8 — vertical-grid convergence expectation

With Nz = 48 on a 0.010 m layer the finest cell spacing is dz = 2.13e-4 m and
k dz = 0.080 at m = 12, giving a second-order error of order 5e-4 — well inside
the 1 % gate. At Nz = 6, k dz ~ 0.8-4 across the mode set and the error reaches
several percent, so the ladder {6, 12, 24, 48} actually exercises convergence
rather than sitting entirely in the converged regime.

## Consequences for the design

- S1a/S1b tolerances set from Checks 1-2, not chosen for convenience.
- Sweep step set by Check 3 (the dominant computational cost).
- S3a anchored to an independent published number rather than to the value the
  solver was handed (anti-circularity).
- S4a/S4b tolerances set from Check 5; S5b from Check 6.
- S6c ladder and tolerance set from Check 7; S6d/S6f justified by the tongue
  width in Check 7.
- Every ladder in C4 was chosen to leave the under-resolved regime (Check 8) so
  that convergence is observable rather than assumed.

These checks are also referenced in PREDICTIONS.md for full disclosure.
