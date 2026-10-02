# CONTROLS — Q-M005

## Control suite for Feigenbaum constant computation

### C1: Known-value reproduction (z=2)
Compute delta_n and alpha_n for z = 2 through n = 8. Verify:
- |delta_6 - 4.6692016091029| < 1e-3
- |alpha_6 - (-2.5029078750957)| < 1e-3
This is the primary control — if we cannot reproduce the known z=2 values,
the entire computation is invalid.

### C2: Convergence monotonicity
For each z, verify that |delta_n - delta_infty| is monotonically decreasing
for n >= 3. Non-monotonic convergence is not a failure per se but must be
documented and explained.

### C3: Seed variation
Repeat each computation with 5 independent initial parameter intervals.
All runs must converge to the same delta_infty within tolerance.

### C4: Method variation (independent implementation)
Compute delta_n for z = 2 using a completely different root-finding
approach (brentq vs Newton). Results must agree to 1e-6.

### C5: Resolution variation (n range)
Compute through n = 6, 8, 10. Convergence should be stable:
adding more n should not change delta_{n-1} by more than 1e-5.

### C6: Floating-point precision
Recompute with increased tolerance (xtol = 1e-14 vs 1e-12).
Results should be identical within 1e-8.

### C7: Independent implementation
A separate, pure-Python implementation (no shared code with the primary)
computes delta_3 for z = 2 and 3. Results must agree within 1e-4.