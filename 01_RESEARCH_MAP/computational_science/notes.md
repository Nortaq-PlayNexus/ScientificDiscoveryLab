# COMPUTATIONAL SCIENCE — research map

## Known
- Floating-point summation-order effects are characterised by Higham; end-to-end
  "emergent metric" sensitivity is under-documented in practice.
- Determinism is a lab requirement (sha256-seeded RNG; verified stable).

## Computable
- I002 (summation order), I004 (PRNG). Also the lab's own numeric-hygiene tooling.

## Rule
- Every pipeline must quantify drift between reduction orders and declare tolerance
  before "anomaly" attribution. This map file is where that standard lives.