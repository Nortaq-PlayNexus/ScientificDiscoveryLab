# Historical 2D percolation audit repair — N-04/N-05/N-19/N-21/N-22

**Audit date:** 2026-09-24  
**Execution class:** read-only stored-cell validation; no production Monte Carlo and no historical writes.  
**Historical integrity:** UNCHANGED_DURING_ANALYSIS (51 files: 50 pinned by whole-file digest, 1 pinned by audited-prefix digest)

## Append-only evidence

EXPERIMENT_REGISTRY.md is a live append-only document. Its audited historical prefix is pinned byte-for-byte; only bytes appended after the pinned prefix are permitted to differ, and the appended size and digest are reported. The immutable baseline and the frozen prefix artifact were both left unmodified.

| Path | Policy | Audited prefix (bytes) | Live (bytes) | Appended (bytes) | Historical region intact |
|---|---|---|---|---|---|
| `EXPERIMENT_REGISTRY.md` | append_only_prefix_pinned | 17841 | 33516 | 15675 | True |

## Corrected classifications

| Finding | Corrected classification | What controls the classification |
|---|---|---|
| N-04 / EXP-0006 | **INCONCLUSIVE_COMPLETE_PROVENANCE_AND_CONTROL_CLOSURE** | Aggregate p50/FSS values regenerate, but the named runner and unavailable C1/C6 evidence prevent complete provenance closure. |
| N-05 / EXP-0007 | **POINT_ESTIMATE_COMPATIBLE_WITH_0.5_PRECISION_VALIDATION_INCONCLUSIVE** | Point estimate is compatible with 0.5, but FSS SE is 3.171 times the tolerance. |
| N-19 / EXP-0009 C7 | **SAME_STREAM_IMPLEMENTATION_CHECK** | Identical labels/seeds and first 40 realizations; no fresh sampling. |
| N-21 / EXP-0009 R3 | **ALGEBRAICALLY_COUPLED_INTERNAL_CONSISTENCY_CHECK** | `P_inf = M_max/L²` makes the fitted slopes algebraically dependent. |
| N-22 / EXP-0010 | **INCONCLUSIVE** | Pooled slope regenerates, but no preregistered individual-size estimator exists and C7 is absent. |

## N-04 — EXP-0006 interpolation and controls

The implemented interpolation is:

```text
p50 = p0 + (0.5 - w0) * (p1 - p0) / (w1 - w0)
```

The historical literal denominator `w1 - p0` is retained only as a diagnostic counterexample; it is not a second estimator or control.

Using stored aggregate cells, the recovered `perc-boot` stream regenerates every p50 mean and SE. Maximum absolute deltas are p50 `0`, SE `0`, and FSS component `0`.

| Control | Audit status | Evidence |
|---|---|---|
| C1 | INCONCLUSIVE_NOT_REGENERABLE_FROM_STORED_CELLS | Only the two aggregate repeat outputs are stored; no realization-level C1 evidence is present. |
| C2 | REPRODUCED_FROM_STORED_AGGREGATE_CELLS | historical bond_span versus bond_wrap stored-cell comparison; no new estimator/control was created |
| C4 | REPRODUCED_FROM_CORRECTED_STORED_CELL_FITS | recomputed from stored inputs |
| C6 | INCONCLUSIVE_EXTRA_SEED_CELLS_NOT_STORED | Stored aggregate cells contain only the primary seed; extra-seed p50 summaries cannot be independently regenerated. |
| C7 | SAME_STREAM_IMPLEMENTATION_CHECK_ONLY | The historical report explicitly uses identical seeded streams and a separate union-find code path. |

The stored-cell C2 pair difference is `0.001014466689` (tolerance `0.005`), but this does not repair the broken named runner or supply missing controls. C1 and C6 remain **INCONCLUSIVE** where stored evidence is insufficient.

## N-05 — EXP-0007 bootstrap accounting and uncertainty

| Bootstrap | Requested | Accepted | Rejected |
|---|---:|---:|---:|
| p50, each L | 500 | 500 | 0 |
| width-route 1/nu | 500 | 495 | 5 |

The FSS point estimate is `0.500687453` with standard error `0.031707449`; its point deviation from 0.5 is `0.000687453`, while the decision tolerance is `0.01`. The ±1-SE band `[0.468980004, 0.532394902]` is a scale indicator, not a confidence interval. Therefore the result is **compatible at the point-estimate gate but INCONCLUSIVE as ±0.01 precision validation**.

The width-route bootstrap is also broad: mean `0.747839199`, SD `0.077264975`, 95% empirical interval `[0.672168361, 1.067411797]`; its upper end exceeds the 0.9 diagnostic gate.

## N-19 — EXP-0009 C7 stream dependence

C7 uses the exact same `G_LAB` labels/seeds and the first 40 realizations as the primary cells. Its mass prefixes and subsample Df regenerate, but this is a **same-stream implementation check**, not independent experimental evidence.

Recomputed C7 subsample Df: `1.923653493` with SE `0.061018987`; maximum value/SE delta from the stored report is `0`.

## N-21 — EXP-0009 R3 coupling

Across every raw cache, `pinfs` equals `masses / L²` exactly. Consequently,

```text
slope(log P_inf) = slope(log M_max) - 2
R3 = |D_f - (2 - beta/nu)| = 0 at the point-fit level
```

The raw point-fit identity residual is `0`. The stored bootstrap-mean residual `0.000757036` reflects separate resampling noise around an algebraically coupled identity. R3 is therefore an **internal consistency diagnostic**, not an independent scaling-law test.

## N-22 — EXP-0010 pooled versus individual-size closure

The four raw caches exactly regenerate the pooled Df `1.896198293` with SE `0.028436384` (maximum stored-value/SE delta `0`). This is an **exploratory pooled slope**.

The frozen rule says `D_f` must be within tolerance at every individual non-power-of-two L, but supplies no single-size Df estimator or fixed amplitude. Available raw quantities are per-size Mmax realizations and their summaries. A pairwise slope, leave-one-out slope, or box-counting replacement would be a new post hoc estimator and was not manufactured.

The required C7 result is absent. Therefore:

- individual-size gate: **UNRESOLVED / NOT IDENTIFIABLE**;
- C7: **INCONCLUSIVE / ABSENT**;
- historical `LATTICE_ARTIFACT`: **NOT ACCEPTED**;
- corrected EXP-0010 classification: **INCONCLUSIVE**.

## Dependency-aware validation order

| Node | Depends on | Produces | Status |
|---|---|---|---|
| N04.E1 | prereg_EXP-0006.json, EXP-0006_results.json/cells | corrected p50 bootstrap and FSS | REPRODUCED |
| N04.E2 | N04.E1, stored bond_wrap aggregate cells | historical C2 comparison | REPRODUCED_WITH_SCOPE_LIMITATION |
| N04.E3 | EXP-0006 stored controls/raw availability | complete control closure | INCONCLUSIVE |
| N05.E1 | prereg_EXP-0007.json, EXP-0007_results.json/cells | 500 requested / 500 accepted p50 bootstrap per L | REPRODUCED |
| N05.E2 | N05.E1, EXP-0007 stored probit widths | 500 requested / 495 accepted width-bootstrap draws | REPRODUCED_WITH_DROPPED_DRAWS_REPORTED |
| N05.E3 | N05.E1 | broad FSS uncertainty and corrected classification | REPRODUCED |
| N19.E1 | EXP-0009 raw cache prefixes, C7 source/report | same-stream C7 numerical reproduction | REPRODUCED_AS_IMPLEMENTATION_CHECK_ONLY |
| N21.E1 | EXP-0009 masses, EXP-0009 pinfs, N=L^2 | R3 algebraic identity | REPRODUCED_AS_INTERNAL_DIAGNOSTIC_ONLY |
| N22.E1 | EXP-0010 raw masses, EXP-0010 bootstrap label/seed | pooled D_f | REPRODUCED_EXPLORATORY_ONLY |
| N22.E2 | EXP-0010 prereg per-size criterion, available raw quantities | individual-size closure | UNRESOLVED_NOT_IDENTIFIABLE |
| N22.E3 | EXP-0010 prereg C7, EXP-0010 stored result | required C7 control | INCONCLUSIVE_ABSENT |

## Reproducibility boundary

- **Reproducible from stored cells:** EXP-0006 aggregate p50/SE/FSS and stored-cell C2/C4; EXP-0007 p50/FSS and 495 accepted width draws; EXP-0009 raw-cache exponents, C7 same-stream prefix, and R3 identity; EXP-0010 pooled Df and per-L mass summaries.
- **Not reproducible / unavailable:** EXP-0006 current full-run provenance, realization-level C1, and extra-seed C6 cells; a fresh independent EXP-0009 C7 sample; an independent R3 observable; an EXP-0010 individual-size Df estimator; EXP-0010 C7.
- **No post hoc control or estimator was added, no Monte Carlo was generated, and no historical registry/config/result/cache/report/helper was written.**

Machine-readable details and the complete SHA-256 evidence manifest are in the sibling `validation_report.json` and the active post-N-14 baseline; the original pre-N-14 baseline is retained unchanged for provenance.
