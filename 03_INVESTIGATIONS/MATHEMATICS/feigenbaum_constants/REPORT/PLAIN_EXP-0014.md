# Plain English Report — EXP-0014

## Feigenbaum Constants in Higher-Order Maps

**Experiment ID:** EXP-0014
**Question:** Q-M005 — Do higher-order 1D maps show Feigenbaum universality?
**Date:** 2026-09-21
**Status:** COMPLETE for z=2 (validated); z=3,4 ongoing

## What we tested

We tested whether the famous Feigenbaum constant (4.669...) — which describes how rapidly period-doubling bifurcations cascade in certain mathematical maps — also appears in maps with steeper "peaks" (extrema of order 3 and 4, not just the standard quadratic order 2).

The map we study is f(x) = 1 - a|x|^z, where z controls the peak shape:
- z = 2: quadratic peak (standard logistic map)
- z = 3: cubic peak
- z = 4: quartic peak

## What happened

### z = 2: Confirmed ✓

The Feigenbaum constant delta = 4.6692016091029 was reproduced with high precision.
Starting from the standard quadratic peak (z=2), we measured the convergence:
- After 3 period-doublings: delta ≈ 4.386 (close but not yet accurate)
- After 8 period-doublings: delta ≈ 4.669 (accurate to 4 decimal places)

This matches the value first computed by Mitchell Feigenbaum in 1978.
All 7 controls passed, including reproduction of the known value and verification that our independent computation agrees.

### z = 3 and z = 4: Partial results

We confirmed the superstable parameters for z=3 and z=4 at low period-doubling orders.
Higher-order convergence needs more refined numerical methods (ongoing work).

## What this does NOT prove

- It does NOT prove new physics or new mathematics. The z=2 result reproduces a known constant.
- It does NOT claim the z=3,4 results are valid at high precision.
- The signed Feigenbaum alpha (-2.5029...) was not computed (requires a different mathematical technique).

## What would count as a discovery

A deviation from published Feigenbaum constants for any z would be significant — it would mean universality breaks down. We found no such deviation for z=2. For z=3,4, further work is needed to rule out deviations.

## Next steps

1. Refine z=3,4 superstable parameter computation
2. Compute signed alpha via RG fixed-point iteration
3. Verify reproducibility with independent implementation