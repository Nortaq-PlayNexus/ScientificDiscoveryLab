# EXPERIMENT_PLAN — EXP-0015 (Q-AC001 / HYP-AC001)

Preregistered protocol. Frozen before execution; any later change is appended to
`CONFIG/changelog.jsonl` via `engine.hypothesis_testing.prereg.log_change`.

## Aim

Certify one six-module simulator of water's response to sound and vibration
against six independent published laws, jointly, with resolution ladders and an
independent re-implementation. This is instrument certification of known physics.
**No novelty claim of any kind is made or permitted.**

## Modules and their independent anchors

| Module | Anchor | Reference |
|---|---|---|
| S1 | c(T,S,P) fresh-water table + UNESCO vs Mackenzie agreement | Fofonoff & Millard 1983; Chen & Millero 1977; Wong & Zhu 1995; Mackenzie 1981 |
| S2 | f_n = n c/2L and (2n-1)c/4L | classical organ-pipe / acoustic-resonator theory |
| S3 | alpha = 2.50e-14 f^2 Np/m; classical 1.1e-14 s^2/m | fresh-water absorption handbooks; Francois & Garrison 1982; Ainslie & McColm 1998 |
| S4 | Gorkov force -> nodes for phi > 0, spacing lambda/2, t_90 ~ a^2 | Gorkov 1962; Leighton, *The Acoustic Bubble*; acoustophoresis reviews |
| S5 | f_0 = (1/2 pi R0) sqrt(3 kappa P0/rho), f_0 R_0 ~ 3 Hz m | Minnaert 1933 |
| S6 | omega_0^2 = (gk + sigma k^3/rho) tanh(kh); subharmonic omega/2; Gamma_c = 4 mu/omega_0 | Faraday 1831; Benjamin & Ursell 1954; Miles 1990 |

## Frozen parameters

See `PREDICTIONS.md` for the complete frozen test grid, tolerances and decision
rule. Summary: alpha = 0.01, SEED = 42, SEED_LADDER = (42, 7, 123, 2023,
314159, 271828), BH-FDR across all cells.

## Implementation (`CODE/water_acoustics_engine.py`)

Six self-contained physics modules plus a small shared layer:

- `sound_speed_unesco(T_S_P)` — exact UNESCO polynomial with the published
  Wong & Zhu (1995) coefficient table. P in bar.
- `sound_speed_mackenzie(T_S_D)` — independent 9-term fit, P expressed as depth
  (D in m, converted internally by the standard 1 dbar ~ 1 m relation only for
  the pressure term used in the cross-check).
- `solve_column_response(f_array, L, config, ppw, ...)` — batched Thomas
  tridiagonal solve of the 1-D complex Helmholtz equation
  p'' + k^2 p = 0 with k = omega/c + i(alpha_wall + alpha_bulk), rigid end
  p' = 0 and pressure-release end p = 0. Returns |p| at a probe.
- `propagate_attenuation(f_array, ...)` — time-domain split-operator
  propagation of a narrowband pulse with the imposed exponential loss; receiver
  amplitude ratio gives alpha_fit.
- `classical_absorption(nu, c)` — first-principles
  (8 pi^2/3) nu/c^3 plus the thermal term.
- `gorkov_phi(rho_p, beta_p)`, `radiation_force(x, ...)`, `integrate_particles(...)`
  — Gorkov force + Stokes drag, RK-free exponential-safe explicit integration.
- `minnaert_omega0(R0)`, `rayleigh_plesset_sweep(R0, ...)` — driven
  Rayleigh-Plesset integrated vectorised across frequencies.
- `vertical_operator(Nz, h, k)` — **finite-difference** vertical Laplace solve
  with Neumann bottom, Dirichlet top, returning phi_z(0); this is what keeps the
  dispersion test non-circular.
- `free_surface_modes(...)`, `run_faraday(...)`, `measure_threshold(...)`,
  `free_decay_rate(...)` — cosine-mode free-surface model with damping and
  vertical container oscillation.

### Non-circularity rules baked into the implementation

1. S6 never computes tanh(kh); it solves Laplace on a grid and takes phi_z(0).
2. S3 anchors the *value* of alpha to an independent literature number and to the
   first-principles classical calculation (which itself is compared against an
   independent published value); gate S3b tests solver fidelity only.
3. S1 cross-checks two independently fitted equations of state, not one
   equation against itself.
4. C5 route (S2) is a time-domain propagation, independent of the
   frequency-domain Helmholtz solve used for the primary route.

## Execution order

```
1. freeze CONFIG/prereg_EXP-0015.json          (engine.hypothesis_testing.prereg.freeze_config)
2. run S1..S6 + controls C1..C11 in CODE/run_exp0015.py
3. write RESULTS/EXP-0015_results.json
4. write CONFIG/EXP-0015_experiment.json (make_experiment_json: ids, UTC time,
   python/lib versions, machine, seed, params, sha256 of results)
5. append CONFIG/registry.jsonl and CONFIG/changelog.jsonl
6. run REPLICATION/independent_check.py        (C12)
7. run CODE/make_figures.py
8. apply the frozen decision rule
9. write REPORT/TECHNICAL_SUMMARY.md and REPORT/PLAIN_ENGLISH_SUMMARY.md
10. update lab registries: QUESTIONS, HYPOTHESES, EXPERIMENT_REGISTRY,
    CURRENT_STATUS, DISCOVERY_LOG, CHANGELOG, MASTER_CANDIDATES, MASTER_INDEX
```

## Gate register

| Gate | Statement |
|---|---|
| S1a | fresh-water anchors, max rel dev <= 5e-4 |
| S1b | UNESCO vs Mackenzie, max rel dev <= 1e-3 over 0..30 degC |
| S1c | c increases monotonically with P; dc/dP in [0.10, 0.22] m/s/bar |
| S2a | first 6 peaks of 4 cells within 1 % of the predicted ladder |
| S2b | f_n ratio L=0.50 : L=0.25 = 0.500 within 1 % |
| S2c | ppw ladder monotone, ppw=80 residual <= 5e-3 |
| S2d | boundary switch reproduces the odd-harmonic series |
| S3a | classical alpha_cl/f^2 within 10 % of published 1.1e-14 s^2/m |
| S3b | alpha_fit within 5 % of imposed at {1, 3, 10, 30} MHz |
| S3c | ppw ladder at 3 MHz monotone, ppw=80 residual <= 2e-2 |
| S3d | log-log slope 2.00 +/- 0.05 over 1-30 MHz |
| S3e | time-domain route agrees with frequency-domain route within 5 % |
| S4a | all particles within 0.02 (lambda/2) of a node |
| S4b | log-log slope of t_90 vs a = 2.00 +/- 0.10 |
| S4c | phi<0 control converges to antinodes |
| S4d | null: displacement < 1e-9 lambda |
| S4e | lambda/4 shift leaves the node set unchanged (< 1e-6 lambda) |
| S5a | log-log slope of f_0 vs R0 = -1.00 +/- 0.05 |
| S5b | f_0 R_0 in [3.0, 3.5] Hz m |
| S6a | discrete-vs-analytic dispersion <= 1 % for m = 1..15 |
| S6a' | Nz ladder monotone, Nz=48 satisfies the 1 % gate |
| S6b | fitted mu within 5 % of 2 nu k^2 |
| S6c | Gamma_c within 30 % of 4 mu_meas / omega_0, monotone crossing |
| S6d | correct mode selected; omega_0(k_sel) = omega_d/2 within 5 % |
| S6e | f_resp / f_drive = 0.500 +/- 0.01 |
| S6f | detuned drive decays for all Gamma <= 0.016 |

Controls C1..C12 as tabulated in `CONTROLS.md`.

## Decision rule (frozen)

As stated at the end of `PREDICTIONS.md`. Evidence state after a full pass:
**CONTROLLED**. ABNORMAL escalates rather than tunes.

## Runtime expectation

CPU-minutes on the lab machine (i7-8700, 24 GB). 1-D batched Helmholtz solves,
vectorised Rayleigh-Plesset sweeps, small spectral free-surface model. Nothing
requires CUDA.

## Out of scope (declared, not silently omitted)

- 2-D nonlinear Faraday pattern selection (squares/hexagons need four-wave
  coupling absent from a linear model).
- Quantitative Blake-threshold theory and sonochemistry yields.
- Molecular-scale cavitation (needs 10^8-10^11 atom MD; see the 2026 Fugaku
  study) — the continuum Rayleigh-Plesset model is explicitly not that.
- Any claim that water "stores", "remembers" or is structurally changed by
  sound. No source found in the searched literature supports this; it is outside
  the lab's scope.
