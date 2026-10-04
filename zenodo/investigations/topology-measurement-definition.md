# Topology-measurement definition

**Experiments:** EXP-0016 · **Question:** Q-O007

## What this is

Under what conditions do discrete representations of optical phase topology disagree about singularity count, charge, or identity?

This deposit is one investigation from a larger laboratory, published separately
so it can be cited on its own. The laboratory as a whole — its registries,
governance rules, and the self-audit that found four defects in its own
instruments — is published separately as
[`10.5281/zenodo.23109117`](https://doi.org/10.5281/zenodo.23109117).

## Why separate deposits

A single question in this laboratory can span several experiments. Q-P004 covers
EXP-0005/0006/0007 and Q-P005 covers EXP-0009/0010. Splitting those across
separate DOIs would scatter one scientific answer across four identifiers and
make it harder to cite, not easier. The investigation — the unit with its own
README, preregistration, code, config and results — is therefore the unit of
deposit, and the experiment IDs are recorded above so a reader can drill down.

## What is in the archive

Code, frozen preregistrations, configs, results, reports and audit trails for
this investigation.

Raw simulation output is **excluded**: `.npz`, `.sqlite3` and `.db`, 362 MB
across the laboratory. That data is regenerable from the seeds recorded in each
preregistration, and including it would make this archive an order of magnitude
larger for no gain in verifiability. The code that consumes it ships here; the
inputs it consumes do not.

## Reproducibility and honesty

This laboratory runs to a written standard (`RESEARCH_RULES.md`): claim
layering, preregistration before analysis, mandatory controls, adversarial
falsification, evidence grading, read-only raw data, and fail-closed runners.

**No physics discovery is claimed.** Several experiments here are INCONCLUSIVE,
and one anomaly was traced to an instrument defect rather than to nature. Null
results are recorded with the same care as positive ones, and a preregistered
prediction that failed is reported as having failed.

Two defects in the laboratory's own instruments were found during self-audit and
are documented in the laboratory deposit: a statistical test that applied a
z-score conversion to a statistic already in `erfc` units, and a percolation
exponent estimator biased upward by 0.11 to 0.35. In the second case the defect
made the laboratory's own anomaly look *smaller* than it really was.

## Licence

MIT — see the licence file in the laboratory repository, or
`CITATION.cff` there.
