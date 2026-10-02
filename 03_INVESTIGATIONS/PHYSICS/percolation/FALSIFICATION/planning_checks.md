# FALSIFICATION / planning checks — EXP-0005

Planning-time checks that must hold before results are trusted, plus the
falsification ladder.

## Planning checks (run at code-writing time, BEFORE the frozen run)

Every item below is a throwaway sanity check (outside RESULTS/), recorded here so
the discipline is visible. "Throwaway" = used only to debug the machinery, never to
guide thresholds (those were frozen first).

1. **Wrap detector sanity on hand-checkable lattices.** Bond torus 4x4 with
   specific edge configurations whose wrapping status is known by inspection:
   the detector must return exactly the hand-computed value. Also on a 2x2 torus
   with all edges open -> wraps; all edges closed -> never.
2. **Compare wrap detector to naive boundary-column test.** On random small torus
   bond configs, the naive test ("cluster touches column 0 and column L-1") must
   overcount (>=) the true wrap count; the true detector is expected to be lower
   or equal. (A sanity sign, not a calibration.)
3. **Spanning detector vs scipy.ndimage.label.** On random open L x L bond configs,
   top-bottom spanning from union-find equals ndimage.label(4-connectivity) result
   for moderate L; also validates the C7 route.
4. **p50 on a knife-edge test.** Near p = 0.5 (bond), W(0.5) for L=64 must sit
   mid-grid (well away from 0 and 1) — i.e., the interpolation always brackets 0.5.
5. **Finite-size sanity.** p50(L) for L in {16,32,64,128} must be monotone
   decreasing toward 1/2 within noise (sign + magnitude check on a quick run).
6. **Where the missing-correction risk lives.** The FSS single-term fit's
   extrapolation error is bounded by C4/C8 diagnostics; this is disclosed, not
   hidden.

If ANY planning check fails, fix the CODE, re-verify, and do NOT report the run.
Do not adjust tolerances to accommodate results.

## Falsification ladder (from CONTROLS.md)

1. INCONCLUSIVE: procedure break (fit gate, C1, C2 conflict, C4 shift, C7 mismatch).
   -> debug/fix the machinery, re-run, keep both registry rows (append-only).
2. ABNORMAL: all gates green but a threshold outside its 0.01 tolerance of a known
   anchor -> consistent unexplained deviation; escalate, report only.
3. H0_SUPPORTED: all gates green and all thresholds inside tolerances -> certification.

## Death of HYP-004?

HYP-004 survives in the H0_SUPPORTED case, and is NOT "true" in the other cases —
it is neutralised: INCONCLUSIVE means "unknown, machinery suspect"; ABNORMAL means
"known physics contradicted" (red flag). Neither confirms nor refutes any physics;
HYP-004 is a measure of the pipeline, not of percolation.