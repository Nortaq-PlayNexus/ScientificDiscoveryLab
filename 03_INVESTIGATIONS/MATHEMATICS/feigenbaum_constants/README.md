# README — Feigenbaum universality in higher-order 1D maps (Q-M005)

Status: **EXP-0014 preregistration frozen; awaiting execution.**

Purpose: Test whether the Feigenbaum universality class extends to
maps with local extrema of order z = 2, 3, 4 by computing the
convergence rates delta_n and alpha_n for each order and checking
their limits against published values. This is a known-result
reproduction with honest error bars — not a search for new constants.

## The question

Do one-dimensional maps f(x) = 1 - a*|x|^z (z = extremum order)
exhibit Feigenbaum-like universal scaling constants delta_infty
and alpha_infty that depend on z but are universal within each z-class?

## Layout

| Path | Meaning |
|---|---|
| `CONFIG/prereg_EXP-0014.json` | frozen preregistration (single source of truth) |
| `CODE/run_feigenbaum.py` | runner implementing the frozen protocol |
| `CODE/feigenbaum_engine.py` | superstable-cycle finder + scaling estimator |
| `REPLICATION/` | independent implementation + seed sweeps |
| `RESULTS/` | raw outputs + separated summary |
| `REPORT/` | technical + plain-language reports |
| `FALSIFICATION/` | kill-the-hypothesis planning |
| `state/` | per-investigation live state |

## Conventions inherited

- BH-FDR alpha 0.01 unless preregistered otherwise.
- Append-only registry (`CONFIG/registry.jsonl`).
- Technical + plain summaries; primary results separated from estimator/
  implementation diagnostics.
- All numerical code uses `math`/`numpy` only — no unverified dependencies.