# Cross-project static/provenance anomaly scan

**Agent:** `agent_static_provenance`  
**Date:** 2026-09-24  
**Scope:** whole laboratory tree, with emphasis on cross-file provenance, hardcoded outputs, result writers, duplicate data, chronology, registry/status consistency, and statistical implementation details.  
**Historical files changed by this agent:** none. A point-in-time baseline comparison records five concurrent changes under `AUDIT/SUBAGENT_EXP0003_BROADBAND_20260924`; those were outside this agent's output and are documented in `historical_integrity_check.json`.

## Executive result

The most important unexpected finding is that the 3-D percolation C7 check is **not independent evidence for the boundary condition**. `spanning_flags()` builds `L × L` row/column arrays for an `L^3` node graph, so for `L=4,N=64` it selects bottom indices `12–15`, while the intended `z=L-1` plane is `16–63`. The 3-D C7 union-find code repeats the same convention, so matching counts only show agreement on the same wrong estimand.

Three additional provenance breaks are unusually concrete:

1. The current investigation-local EXP-0006 runner contains a different interpolation denominator from the one that can reproduce the stored result, while a root wrapper invokes a different older runner. Its C2 pass is also a literal `a-a` subtraction.
2. Q-M007's headline `38/40` BH-FDR result is generated from aggregate residuals with an approximate/nonstandard tail formula; the script has no per-cell observed/expected data. A separate hardcoded audit writer says the 40-cell FDR was **not** applied.
3. Q-P007 has two writers targeting the same result path, one reads keys the engine never returns, the phase-2 cache omits the cluster-size arrays required for tau, and the phase-1 `p_c` inputs are literals.

These findings invalidate or materially narrow several prior classifications; they are not generic recommendations.

## Method and preservation

- Read the existing independent audit (`AUDIT/INDEPENDENT_AUDIT_20260924/README.md`, `independent_static_results.json`, `AUDIT/BUGS.md`, and `AUDIT/CLAIM_REGISTRY.md`) before scanning.
- Reviewed investigation code/results/reports/configs, `04_SHARED_ENGINE`, `src`, tests, root writers, registries, raw/data stores, duplicate hashes, JSON validity, and chronology.
- Used AST/text inspection, deterministic in-memory calculations, file hashes, and a temporary directory for the preregistration overwrite test.
- Did not run historical result writers. The final verifier wrote only `cross_project_verification.json` and its log in this directory.
- The first whole-tree scanner stopped on an AST `AttributeError`; its failure is preserved in `scan_static_provenance.log.txt`. The later safe verifier completed all 21 checks.

## Findings index

The authoritative structured record is [`findings.json`](findings.json). Every entry there includes exact locations, observed values/quotes, rationale, benign alternative, severity/confidence, a minimal reproduction command, and prior-classification impact.

| ID | Finding | Severity | Status relative to prior audit |
|---|---|---:|---|
| SP-001 | 3-D spanning routine uses 2-D boundary indices; C7 repeats the defect | Critical | New; invalidates stored 3-D boundary measurements |
| SP-002 | 3-D nested cluster cache makes every tau tail empty | Critical | New; tau is structurally invalid |
| SP-003 | 3-D width samples are silently reduced 10x; ragged fits truncate to minimum n | High | New; preregistered sample/precision claims do not hold |
| SP-004 | Default 3-D runner selects main config; main-named result is a pilot copy | High | New; C-009 provenance becomes non-reproducible |
| SP-005 | EXP-0006 interpolation formula and writer do not regenerate stored p50 | High | New; C-005 EXP-0006 evidence becomes provenance-limited |
| SP-006 | EXP-0006 C2/C7 pass fields are not computed as stated | High | New; control support is removed |
| SP-007 | Q-M007 40-cell BH-FDR uses aggregate-residual approximation and wrong tail semantics | High | New; C-010 remains descriptive only, 38/40 withdrawn |
| SP-008 | `save_audits.py` hardcodes conclusions and emits contradictory Q-M007 artifacts | High | New; C-016 strengthened |
| SP-009 | Q-P007 writers/cache collide and cannot reconstruct tau | Critical | New; C-008 invalid result reinforced |
| SP-010 | Q-P006 cells are copied Q-P005 data despite no-reuse preregistration | High | Corroborates B-002 |
| SP-011 | `freeze_config()` overwrites an existing “immutable” preregistration | High | New; C-001 immutability claim narrowed |
| SP-012 | `result_hash` is neither a consistent file hash nor consistently current semantic hash | Medium | New; hash-based provenance is unusable |
| SP-013 | Feigenbaum path/date/status/control artifacts contradict one another | Critical | Corroborates B-003/B-004/B-005 |
| SP-014 | Q-M008 changes gap denominator, blocks, p-value calculation, and BH rule | High | New; C-010/C-014 not an exact method reproduction |
| SP-015 | Optics bootstrap p-values are floored at machine epsilon | Medium | New; known-law results remain, p-values do not |
| SP-016 | Q-S9 outputs are literal/synthetic while reports call them measured | Critical | Corroborates B-007 with report mismatch |
| SP-017 | Registry/status files omit IDs and disagree with result files; ID collisions remain | High | Corroborates B-016 |
| SP-018 | All `05_DATA` stores and all 21 SQLite tables are empty | High | Corroborates B-017 |
| SP-019 | EXP-0007 preregistration says EXP-0006 never ran; effective bootstrap count is 495 vs 500 | Medium | New qualification to C-005/C-016 |
| SP-020 | Application API mislabels partial charge, depiction call fails, and one test assertion is tautological | Medium | New; software-only infrastructure claim narrowed |
| SP-021 | EXP-0010 uses one pooled D_f fit for an all-non-power-of-two gate and omits C7 | High | New; EXP-0010 cannot close the lattice-artifact claim |
| SP-022 | EXP-0009 C7 reuses identical streams and is implementation-only evidence | Medium | New; C7 is not independent sampling |
| SP-023 | Q-M007's first prime-gap bin is structurally impossible under the stated support | High | Corroborates B-011; first-bin significance is contaminated |
| SP-024 | Q-S9-2 stores assumed parameters as fits and mixes absolute/relative units | High | Corroborates B-007; effect-size interpretation invalid |
| SP-025 | Planned Q-M008 10^10 segmented sieve fails a 1000-number sanity check | High | New; future 10^10 path is not auditable |

## Highest-signal evidence

### 3-D boundary and shared C7 defect

`perc_engine.py:226-251` constructs `rows`/`cols` with length `L²`; `run_exp0011.py:51-58` passes `N=L³`. For `L=4`, the selected bottom set is `[12,13,14,15]`, disjoint from the intended final z-plane `[16,...,63]`. The C7 source explicitly says “only check z=0 plane” and uses the same 2-D IDs. A 1000-draw cross-check recorded in the main second-pass evidence gives, at `L=8`, current-slice counts `(v,h)=(33,28)` versus correct opposite-plane counts `(327,316)`.

### EXP-0006 writer/control collision

The current formula at `run_percolation_exp0006.py:64` is:

```text
p0 + (0.5-w0)*(p1-p0)/(w1-p0)
```

The stored raw cells give `0.7965714285714307` for `L=64` under that literal expression, versus stored `0.4998542286084771`; the corrected denominator gives `0.4998211091234348`. The current runner mtime is 2026-09-22, while the result mtime is 2026-09-17. The root wrapper imports `run_percolation` instead. At lines 291-293, current C2 computes `a-a`, writes `pair_diff: 0.0`, and hardcodes `pass: True`; the stored result has `pair_diff: 0.0010144666894992271`.

### Q-M007 inferential mismatch

`compute_bhfr_40cell.py:27-49` explicitly says it only has bin totals and approximates each cell with `std_residual**2`. It then uses `0.5*erfc` on a Wilson–Hilferty-like transformed statistic. Stored bin-1 p-values are `2.05e-7, 3.07e-13, 4.20e-25, 1.63e-49`; the exact chi-square(1) upper tails for the same statistics are `7.27e-184, 0, 0, 0`. The technical report nevertheless says `38/40` and “new analytical finding.” The generated 2026-09-19 audit artifact says the 40-cell FDR was not applied, demonstrating that the two reports are not a clean supersession chain.

### Q-P007 non-reconstructibility

`run_q_p007.py` requests `o["chis"]`, `o["pinfs"]`, and `o["sizes"]`, but `run_span_cell_edges()` returns `cluster_sizes`; both runners write `EXP-0009-pc_results.json`. `run_phase2.py` saves only `sizes_n`/`sizes_n_total` in NPZ cache files, yet later evaluates `cells[tL]["sizes"]`. The stored result consequently has `tau.mean=null` and `tau_raw.total_tail_clusters=0`.

### Additional gate and data findings

- **EXP-0010:** the preregistration requires `D_f` within tolerance at every non-power-of-two size and requires C7, but `run_exp0010.py:113-147` computes one pooled slope and stores only C1. The report repeats the pooled value as if it were four per-size measurements.
- **EXP-0009 C7:** `independent_check_exp0009.py:1-8` explicitly uses identical labels, seeds, and the first 40 realizations. It is a valid implementation check, not independent sampling.
- **Q-M007 support:** the first exponential-bin edge is `0.10536051565782628`, below the odd-prime lower bound `2/ln(10^8)=0.10857362047581294`; all four first-bin counts are zero by construction.
- **S9/Q-M008 future paths:** Q-S9-2 writes assumed Hill constants and mixes absolute/relative units; the planned Q-M008 segmented sieve returns 157 primes at a 1000 sanity limit instead of 168.


## Prior-audit impact

- **3-D:** C-009 should be treated as invalid for stored measurements, not merely an incomplete pilot. C7 agreement is not independent.
- **EXP-0006:** C-005's known 2-D threshold support may survive through other evidence, but the EXP-0006 fine-grid result and controls are not directly reproducible from the identified current runner.
- **Q-P007:** C-008 remains invalid for tau; the refined-p_c PASS narrative is not independently established.
- **Q-M007/Q-M008:** C-010/C-014 remain descriptive only. The 38/40 FDR and “same method as EXP-0008” wording are withdrawn.
- **Feigenbaum:** C-011's z=2 reproduction remains; z=3/z=4 and control provenance remain contradicted/invalid.
- **EXP-0010/Q-P005:** the non-power-of-two result is a pooled fit with a missing C7/per-L gate, so it cannot independently close the exponent-anomaly claim.
- **S9:** C-013 remains invalid/not reproduced; Q-S9-2 also has a self-consistent unit/fit failure.
- **Registry/data:** C-016 remains contradicted as a provenance record; empty stores prevent raw-data-dependent upgrades.

## Limitations

- Filesystem mtimes and embedded dates are evidence of inconsistency, not a cryptographic execution timeline.
- The scan cannot recover deleted raw inputs or prove which of two historical writers actually ran on a given date.
- The report does not treat ordinary stale documentation as a finding unless it changes a specific result, gate, or provenance claim.
- Existing prior-audit defects not reclassified as new are listed in `findings.json` under `prior_audit_corroborations_not_counted_as_new`.

## Artifacts

- [`findings.json`](findings.json) — final 25-finding machine-readable record.
- [`cross_project_verification.json`](cross_project_verification.json) — final safe verifier output.
- [`cross_project_verification.log`](cross_project_verification.log) — successful verifier log.
- [`verified_candidate_evidence.json`](verified_candidate_evidence.json) and [`verify_static_findings.py`](verify_static_findings.py) — first-pass candidate evidence.
- [`COMMANDS.md`](COMMANDS.md) / [`commands.txt`](commands.txt) — command and preservation manifest.
- [`historical_integrity_check.json`](historical_integrity_check.json) — baseline hash comparison; it records five concurrent sub-audit files outside this agent output and no intentional historical experiment-file edits by this agent.
- `scan_static_provenance.log.txt` — preserved failed first scanner run.
