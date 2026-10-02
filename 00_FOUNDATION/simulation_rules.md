# Simulation Rules

How simulations in this laboratory are written, validated, and trusted.

## Principles

1. **A simulation is a model, not reality.** A pattern in a simulation is a pattern
   in the model. Connecting it to the world requires physical reasoning and,
   ideally, external data.
2. **Simulation bugs look like discoveries.** Numerical error, aliasing,
   boundary effects, unit mistakes and floating-point behaviour routinely produce
   "exciting" artifacts. The kill-the-hypothesis engine is mandatory.
3. **A simulation result is only trustworthy if it reproduces something known.**
   Every new simulator first must pass known-result validation (e.g., diffraction of
   a known aperture, a known analytic solution, a conservation law).

## Required properties

- **Deterministic**: same config + seed => identical output (bit-for-bit where
  feasible). Use the lab RNG.
- **Recorded**: full config in `experiment.json`; result hashes computed.
- **Resilient**: long runs checkpoint; crash recovery; low-resource mode.

## Baseline validation for a new simulator

| Check | What it catches |
|---|---|
| Energy/norm conservation | Unit-scaled or non-unitary numerical schemes |
| Analytic asymptotic match | Wrong scaling/frequency |
| Grid-convergence test | Resolution-dependent artifacts |
| Boundary-padding test | Edge artifacts leaking into the field |
| Method-difference test (2nd algorithm) | Method-specific artifacts |
| Known case (textbook/aperture) | Wrong physics implemented |

## Controls specific to simulation

- `null control` — random input with matched power spectrum/size.
- `matched control` — same simulation, one factor changed only.
- `parameter-shuffled control` — property association broken.
- `resolution ladder` — 32 -> 64 -> 128 -> 256 -> ... ; a real feature is stable,
  an artifact often drifts/appears/disappears.
- `seed ladder` — same config, several seeds.
- `synthetic test data` — embed a known signal; the simulator must recover it.

## Division of labour

- Physics kernels (e.g., angular-spectrum propagation) are validated against
  analytic results exactly as the sandbox does (ASE/sandbox precedent: ASM unitary
  to ~1e-13, energy error ~1e-16, independent implementation NCC=1.0).
- Statistical layers never call physics kernels; they consume numbers and return
  decisions. This keeps them interchangeable.

## Recording

Every simulator run writes `experiment.json` with: ID, date, versions, seed,
parameters, dataset hashes, result hashes, and the control suite actually run.