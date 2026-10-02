## Falsification planning — Q-M005

### Kill-the-hypothesis checks

1. **Floating-point precision:** If delta_n is sensitive to numerical precision (xtol changes), results are unreliable.
2. **Root-finding failure:** If Newton's method fails to converge for some n, the a_n values are wrong.
3. **Non-monotonic convergence:** If delta_n oscillates, the RG analysis may not apply directly.
4. **Boundary effects:** If the map has additional fixed points near [-1,1] that interfere with superstable cycle search.
5. **Published value disagreement:** If delta_infty for z=2 disagrees with Feigenbaum 1978 beyond 5e-2, the method is broken.

### Plan

- Run z=2 through n=8; verify against published delta = 4.6692016091029 at n=6.
- Run z=3,4 through n=6; compare to Hu & Mao 1982 published values.
- If z=2 fails: the numerical method is broken, fix and rerun before attempting z=3,4.
- If z=3 or z=4 fails but z=2 passes: document as new finding (but unlikely — method is standard).
- If any order fails: record the failure mode in state/failure_mode.json.

### Expected failure modes

- **Overflow:** For large z and large n, a_n grows; check |a_n| < 1000.
- **Period not found:** Newton may not converge; use brentq fallback with bracket search.
- **Slow convergence at z=4:** May need n > 8 for accurate delta_infty estimate.
