# README — Prime gap distribution vs Poisson/Gallagher model (Q-M002 / HYP-005 / EXP-0008)

Status: **EXP-0008 in preparation** (preregistration frozen; runner in validation).

Purpose: reproduce, on this machine, the Poisson (Gallagher 1976) prediction for
prime gaps in four disjoint ranges of the integers. This is a known-result
reproduction with a built-in falsification test — not a search for new
structure. Evidence ceiling: CONTROLLED unless a reproducible deviation
survives all gates.

## The question

Normalized prime gaps δ = (p_{i+1} − p_i) / ln(p_i): does their distribution
match Exp(1) across four disjoint ranges up to 10^8, after conditioning on
residue classes? Null = Gallagher/Poisson model holds; alternative = a
reproducible systematic deviation that survives residue-class conditioning.

## Layout

| Path | Meaning |
|---|---|
| `CONFIG/prereg_EXP-0008.json` | frozen preregistration (single source of truth) |
| `CODE/run_prime_gaps.py` | runner implementing the frozen protocol |
| `REPLICATION/independent_check.py` | independent implementation (C7) |
| `RESULTS/` | raw outputs + separated summary |
| `REPORT/` | technical + plain-language reports |
| `FALSIFICATION/` | kill-the-hypothesis planning |
| `state/` | per-investigation live state |

## Conventions inherited

- All randomness from `engine.utilities.core.rng(label, seed)` (sha256-derived).
- BH-FDR alpha 0.01 unless preregistered otherwise.
- Append-only registry (`CONFIG/registry.jsonl`).
- Technical + plain summaries; primary results separated from estimator/
  implementation diagnostics.
- Frozen EXP-0005/0006/0007 records are not modified.
