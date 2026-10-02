# PREDICTIONS — EXP-0015 (frozen before execution)

All numbers below were fixed before the registered run. Pre-design sanity checks
that informed these tolerances are disclosed in `FALSIFICATION/planning_checks.md`
and are **not** the registered result.

Global: alpha = 0.01, BH-FDR across all preregistered cells, SEED = 42,
SEED_LADDER = (42, 7, 123, 2023, 314159, 271828).

Water constants used throughout (published values, frozen):

| Symbol | Value | Units | Source |
|---|---|---|---|
| rho_f | 998.2 | kg/m3 | fresh water @ 20 degC |
| sigma | 0.0728 | N/m | surface tension @ 20 degC |
| mu | 1.002e-3 | Pa s | dynamic viscosity @ 20 degC |
| nu | 1.003e-6 | m2/s | kinematic viscosity @ 20 degC |
| beta_f | 4.6e-10 | 1/Pa | compressibility of water |
| P0 | 101325 | Pa | 1 atm |
| P_vap | 2339 | Pa | vapour pressure @ 20 degC |
| kappa | 1.4 | - | ratio of specific heats of air |
| g | 9.81 | m/s2 | standard gravity |
| c_p, c_v | 4182, 4178 | J/(kg K) | fresh water @ 20 degC |
| k_th | 0.598 | W/(m K) | thermal conductivity @ 20 degC |
| a_tube | 0.010 | m | acoustic tube radius (S2) |
| L_ch | 0.10 | m | Faraday channel length (S6) |
| h_layer | 0.010 | m | water layer depth (S6) |

---

## S1 — speed of sound c(T, S, P)

**Primary H0 (S1a) — published fresh-water anchors.**
For fresh water (S = 0) at P = 1 bar, `c_UNESCO` must match the tabulated anchor
at every temperature in T = {0, 5, 10, 15, 20, 25, 30, 35} degC with relative
error <= 5e-4 (0.05 %).

Frozen anchors (m/s): 1402.39, 1426.50, 1447.10, 1466.00, 1482.00, 1497.00,
1509.50, 1520.00.

**Secondary H0 (S1b) — independent-method agreement.**
Over T = 0..30 degC in 1 degC steps (31 points), S = 0, P = 1 bar, the UNESCO
(Chen-Millero / Wong-Zhu) and Mackenzie (1981) formulations must agree with
max relative deviation <= 1.0e-3 (0.10 %).

**Secondary H0 (S1c) — pressure trend.**
At T = 20 degC, S = 0, c must increase monotonically over
P = {1, 10, 50, 100, 500, 1000} bar, and dc/dP at the surface must lie in
[0.10, 0.22] m/s per bar (UNESCO C10 = 0.153563 m/s/bar).

**Positive control (C2).** Seawater S = 35, T = 0 degC, P = 0 bar: UNESCO and
Mackenzie must agree within 0.1 % (expected ~1449 m/s for both).

---

## S2 — bounded-column resonance

Model: 1-D damped driven Helmholtz in a water column of length L, tube radius
a = 0.010 m. Sound speed c = c_UNESCO(20 degC, 1 bar) = 1482.359 m/s.

Loss model (frozen, first principles):

    alpha_wall = sqrt(nu * omega / 2) / (a * c) * (1 + (gamma-1)/sqrt(Pr))
    alpha_bulk = 2.50e-14 * f**2            (fresh water, 20 degC)
    k = omega/c + 1j * (alpha_wall + alpha_bulk)

with gamma = c_p/c_v = 1.00096 and Pr = nu * c_p / k_th = 7.01.

**Predicted resonance ladders**

- Config A (rigid-rigid, sealed):  f_n = n * c / (2L)
- Config B (rigid-free, open top / free surface): f_n = (2n-1) * c / (4L)

| L (m) | config | f_1..f_6 (Hz) |
|---|---|---|
| 0.25 | A | 2964.7, 5929.4, 8894.1, 11858.9, 14823.6, 17788.3 |
| 0.25 | B | 1482.4, 4447.1, 7411.8, 10376.5, 13341.2, 16305.9 |
| 0.50 | A | 1482.4, 2964.7, 4447.1, 5929.4, 7411.8, 8894.1 |
| 0.50 | B |  741.2, 2223.5, 3705.9, 5188.3, 6670.6, 8153.0 |

**Gates**

- **S2a** — For each of the 4 cells, locate the first 6 response peaks on a
  sweep f in [100, 20000] Hz with df = 0.5 Hz, refined by parabolic
  interpolation over the 3 samples around each maximum. Every peak must satisfy
  |f_meas - f_pred| / f_pred <= 1.0e-2.
- **S2b (scaling)** — For every mode index n, f_n(L=0.50) / f_n(L=0.25) must
  equal 0.500 within 1 % (all four cells combined).
- **S2c (resolution ladder)** — For config A, L = 0.25 m, repeat at
  points-per-wavelength ppw = {20, 40, 80} measured at 20 kHz. The maximum
  peak residual over the 6 modes must decrease monotonically with ppw and the
  ppw = 80 value must be <= 5e-3. Expected scaling ~ ppw^-2 (3-point
  Laplacian modified wavenumber).
- **S2d (boundary)** — Switching A -> B must relocate the whole ladder to the
  odd-harmonic series, not merely shift it: the measured B ladder must fit
  (2n-1)c/4L with the same <= 1 % tolerance (already implied by S2a but
  reported separately as the boundary falsifier).

---

## S3 — absorption vs frequency

**S3a — first-principles classical absorption (independent literature number).**

    alpha_cl / f**2 = (8 * pi**2 / 3) * nu / c**3   + thermal term

- **Gate S3a:** evaluated with the *literature* values used by the source we are
  reproducing (nu = 1.44e-6 m2/s at 280 K, c = 1500 m/s), the result must be
  within 10 % of the published 1.1e-14 s2/m. (Closed-form value: 1.123e-14.)
- Thermal term must be reported; it is predicted to be < 1e-3 of the viscous
  term for water at 20 degC.

**S3b — solver fidelity (the propagation solver recovers the intended decay).**

Imposed alpha = 2.50e-14 f^2 Np/m. A harmonic field is propagated through a
uniform column by finite differences with a first-order radiation condition at
the far end; alpha is fitted from the amplitude slope over the receiving region.

Test band **f = {1.0e6, 3.0e6, 1.0e7, 3.0e7} Hz** (ultrasound).

Band choice (recorded honestly): because alpha grows as f^2 while lambda shrinks
as 1/f, the number of cells needed to observe a fixed optical depth over a fixed
band scales as 1/f. At 100 kHz the column required for alpha*z ~ 1 is several
kilometres of water resolved at 14.8 mm wavelength (~10^7 cells), which is
neither physical as a laboratory statement nor affordable. The gated band is
therefore the ultrasonic band, where one metre of fresh water already gives a
measurable drop. Audio-band attenuation is reported as characterisation
(alpha(1 kHz) = 2.5e-8 Np/m, i.e. 2.2e-7 dB/m — negligible by construction).

Column length per frequency: z_max = min(1.0 m, 3.0/alpha). Primary ppw = 20
measured at the cell's own frequency.

- **Gate S3b:** |alpha_fit / alpha_imposed - 1| <= 5.0e-2 at each of the four
  test frequencies.

**S3c — resolution ladder.**

- **Gate S3c:** at f = 3.0e6 Hz, ppw = {10, 20, 40, 80}; residuals must decrease
  monotonically and the ppw = 80 value must be <= 2.0e-2.

**S3d — band slope (characterisation, gated as a pipeline check).**

- **Gate S3d:** least-squares slope of log(alpha_fit) on log(f) across the four
  test frequencies must equal 2.00 within +/- 0.05.

**S3e — method variation (C5).** An independent time-domain split-step
propagation at f = 3.0e6 Hz over z = 0.2 m must agree with the frequency-domain
route to within 5 %.

**Characterisation (no gate).** total/classical ratio at 20 degC is predicted
near 3.1 (2.50e-14 / 8.11e-15), consistent with the documented structural-
relaxation excess (literature quotes ~2.3 at 280 K because nu is larger there).
Reported, not gated.

---

## S4 — acoustic radiation force / pressure-node patterning

Standing wave, f = 1.0 MHz, lambda = c/f = 1.48236 mm, domain = 3 lambda,
pressure p(x) = p0 sin(2 pi x / lambda), p0 = 1.0e5 Pa.

Gorkov force and Stokes drag:

    phi     = (5*rho_p - 2*rho_f)/(2*rho_p + rho_f) - beta_p/beta_f
    V_p     = (4/3) pi a**3
    F(x)    = -(pi * p0**2 * V_p * beta_f / (2*lambda)) * phi * sin(4 pi x / lambda)
    dx/dt   = F / (6 * pi * mu * a)

- **Predicted phi (polystyrene in water)** = **+0.5806** (rho_p = 1050 kg/m3,
  beta_p = 2.16e-10 1/Pa) => stable fixed points at the **pressure nodes**
  x = j * lambda/2, j = 0..6.
- **Gate S4a:** after T = 2000 s, every particle of every radius and every seed
  lies within 0.02 * (lambda/2) of the nearest node.
- **Gate S4b (a^2 law):** t_90 (time to reach 90 % of final displacement) for
  a = {5, 10, 20} um must have log-log slope 2.00 within +/- 0.10
  (force ~ a^3, Stokes drag ~ a  =>  v ~ a^2).
- **Gate S4c (contrast sign, matched control):** with phi = -0.5806 the same
  initial conditions must converge within 0.02 * (lambda/2) of the **pressure
  antinodes** x = (j + 1/2) * lambda/2. A solver that sends particles to nodes
  regardless of the sign of phi fails here.
- **Gate S4d (null):** with p0 = 0, total displacement must be < 1e-9 * lambda
  for all particles.
- **Gate S4e (shift / grid-lock falsifier):** translating every initial
  position by lambda/4 (half the node spacing) must yield the same final node
  set, with max node-position change < 1e-6 * lambda.
- **Seeds:** 6 random initial-position sets from SEED_LADDER; the spread of t_90
  must be consistent with the deterministic dynamics (relative sd < 0.25).

---

## S5 — bubble (Minnaert) response and cavitation onset

Rayleigh-Plesset, linearised resonance prediction:

    omega_0**2 = ( 3*kappa*(P0 - P_vap) + 2*sigma*(3*kappa - 2)/R0 ) / (rho_f * R0**2)

- **Predicted f_0 * R_0 = 3.25 Hz m** for R0 in {0.5, 1, 2, 5, 10} mm
  (literature compact form: R0 f0 ~ 3 Hz m, Minnaert 1933).
- **Gate S5a:** log-log slope of f_0 vs R0 = -1.00 within +/- 0.05.
- **Gate S5b:** every f_0 * R0 in [3.0, 3.5] Hz m.

Measurement: drive p_a = 1000 Pa, sweep 60 frequencies over [0.35, 2.5] f_0,
parabolic peak interpolation. Resonance width must be resolved by the sweep
(predicted f_0/Q with Q ~ 100-1000 -> df/f <= 1e-2 is adequate).

**Characterisation (no gate):**

- Linearity: at f = f_0, (R_max - R0) vs p_a must have log-log slope 1.00 within
  +/- 0.05 for p_a <= 0.2 P0.
- Cavitation onset: smallest p_a with R_max > 2 R0, reported per R0 and
  compared in magnitude with P0. Predicted onset <~ P0 (Blake regime);
  a precise Blake value is explicitly out of scope and is NOT gated.
- Harmonic content: |R(2f)|/|R(f)| reported vs p_a.

---

## S6 — free-surface (Faraday) response

Linear potential-flow free surface: cosine modes in x (Neumann walls) with a
**finite-difference vertical Laplace solve** (so tanh(kh) is never assumed),
Nz points on the layer of depth h = 0.010 m, channel L = 0.10 m,
k_m = m*pi/L for m = 1..15.

Damping model (frozen): mu_k = 2 * nu * k**2  (Lamb free-surface viscous
damping), implemented as an extra -2*mu*psi term so that each mode obeys the
damped Mathieu equation

    eta_ddot + 2 mu eta_dot + omega_0**2 (1 + Gamma cos(omega_d t)) eta = 0

with omega_0**2 = (g k + sigma k**3 / rho) * tanh(k h).

**Predicted dispersion table** (primary, Nz = 48):

| m | k (1/m) | omega_0 (rad/s) | f_0 (Hz) | f_d = f_0*2 (Hz) |
|---|---|---|---|---|
| 6 | 188.50 | 47.26 | 7.521 | 15.04 |
| 7 | 219.91 | 53.49 | 8.514 | 17.03 |
| 8 | 251.33 | 59.78 | 9.515 | 19.03 |
| 9 | 282.74 | 66.26 | 10.548 | 21.10 |
| 10| 314.16 | 72.96 | 11.613 | 23.23 |
| 12| 376.99 | 87.17 | 13.875 | 27.75 |
| 15| 471.24 | 110.68| 17.617 | 35.23 |

**Gates**

- **S6a (dispersion).** omega_num from the discrete vertical Laplace solve must
  match omega_0 = sqrt((g k + sigma k^3/rho) tanh(k h)) with relative error
  <= 1.0e-2 for all m = 1..15 at Nz = 48.
- **S6a' (resolution ladder).** Nz = {6, 12, 24, 48}: the max relative error
  over m = 1..15 must decrease monotonically and the Nz = 48 value must satisfy
  the 1 % gate. (Predicted ~ Nz^-2.)
- **S6b (free-decay damping).** With the drive off and mode m = 8 released at
  small amplitude, fitting ln(eta_pk) vs t must return mu_meas with
  |mu_meas / (2 nu k^2) - 1| <= 5.0e-2. This mu_meas, not the input value, is
  what S6c uses.
- **S6c (threshold).** At omega_d = 2 omega_0 (m = 8), a Gamma ladder
  Gamma = {0.002, 0.004, 0.006, 0.008, 0.010, 0.012, 0.014, 0.016} must show
  decay for all Gamma below the crossing and growth for all Gamma above. The
  crossing Gamma_c must satisfy
  |Gamma_c / (4 mu_meas / omega_0) - 1| <= 0.30.
  **Predicted Gamma_c = 4 mu_meas / omega_0** (damped Mathieu n = 1 tongue;
  growth rate at exact 2:1 drive = omega_0 Gamma/4).
- **S6d (wavelength selection).** Driving at each f_d in the table above must
  make mode m the dominant surface mode (largest time-averaged |eta|^2 among
  m = 1..15), and omega_0(k_selected) must equal omega_d/2 within 5 %.
- **S6e (subharmonic).** In every growing run the response spectrum must peak at
  f_resp / f_drive = 0.500 within +/- 0.01 (Faraday 1831; Benjamin & Ursell 1954).
- **S6f (detuned control).** Driving at 1.2 x 2 omega_0 for m = 8 must produce
  net decay for all Gamma <= 0.016 (outside the tongue).

**Declared model limits (characterisation, not gates):**

- The model is **linear**: above threshold the amplitude grows without bound.
  Only onset, growth sign, subharmonic ratio and selected wavelength are gated;
  saturation and pattern shape (squares/hexagons) are out of scope.
- mu = 2 nu k^2 omits contact-line, meniscus and bottom-boundary-layer
  dissipation, so the simulated Gamma_c is **lower than** experimentally observed
  Faraday thresholds for water. It must not be quoted as an experimental value.

---

## Frozen decision rule

    H0_SUPPORTED  if every gate S1a..S6f passes AND the C12 independent
                  re-implementation agrees with the main run within its
                  stated tolerances.
    ABNORMAL      if exactly one gate fails and the failure does NOT shrink
                  under the corresponding refinement (defect or model limit)
                  -> escalate, do not tune.
    INCONCLUSIVE  otherwise.
    H1_DEV        only if a failure survives C1-C11 and C12 AND is stable under
                  refinement -> then report as a controlled deviation, never
                  interpreted as new physics.

Evidence state after a full pass: **CONTROLLED** (certification of an instrument
against established laws; no novelty claim of any kind).
