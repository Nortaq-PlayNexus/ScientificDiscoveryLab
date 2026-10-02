# Cross-project claims/data anomaly scan

**Audit date:** 2026-09-24  
**Scope:** `C:\Users\natha\ScientificDiscoveryLab` and the whole in-tree laboratory, source, test, registry, configuration, raw/result, report, and database surface. Historical experiment files, registries, reports, and result files were not edited. All new artifacts are confined to `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/`.

## Executive verdict

The scan found **26 evidence-backed findings**: **5 CRITICAL, 18 HIGH, and 3 MEDIUM**. The strongest conclusion is not that every numerical result is false; it is that several current claims are **not self-authenticating from the supplied artifacts**. The same provenance and method weaknesses recur across projects: result-hash semantics do not verify result files, preregistration can be overwritten, central raw-data storage is empty, follow-up experiments reuse data or controls, and reports state conclusions that the current code/results cannot regenerate.

The highest-impact issues are:

- **CP-008 (CRITICAL):** Q-P006’s three raw-cell files are byte-identical to Q-P005 while its preregistration says no cells were reused, and its stored result omits required gates.
- **CP-012 (CRITICAL):** the 3D runner inherits a spanning estimator built from 2D row/column indices; the supplied C7 check repeats the same convention rather than testing opposite 3D faces.
- **CP-015 (CRITICAL):** Q-M007’s reported 38/40 BH result uses reconstructed pseudo-p-values; the stored formula is not a calibrated chi-square survival calculation.
- **CP-021 (CRITICAL):** Q-S9-2 generates a Hill curve from assumed parameters and stores those assumptions as fitted parameters, not measured dose-response data.
- **CP-024 (CRITICAL):** EXP-0014 combines an invalid preregistration, a nested/ambiguous result path, nonfinite higher-order sequences, and hardcoded control passes. The narrow z=2 result remains separable.

These findings do **not** automatically invalidate the independent, narrowly scoped portions of C-002/C-003 or the z=2 Feigenbaum result. They do invalidate broad provenance, independence, control, and mechanism claims that rely on the affected artifacts.

## Method and evidence

1. The whole-tree scanner inventoried **662 files**, excluding this output directory and caches: `scan_output.json`.
2. `verify_findings.py` ran **25 read-only cases** after the final artifact update. All 25 cases report `ok: true` in `verification_results.json`; a case-level `ok` means the reproduction ran and produced evidence, not that every scientific interpretation is universally proven.
3. The scan compared code, preregistration/configuration, result JSON/NPZ, reports, registries, and existing audit/claim documents. It checked exact SHA-256 relationships, JSON validity, source/result schema, sample accounting, formulas, controls, and cross-file quotations.
4. No historical writer was invoked. Temporary reproduction files, where needed, were confined to the output directory and removed by the verifier.

Every finding in `findings.json` records an exact path plus line/JSON location, observed value, anomaly, benign alternative, severity/confidence, minimal command, verification case, and prior-claim impact.

## Findings at a glance

| ID | Severity | Finding and verification case | Prior-claim consequence |
|---|---|---|---|
| CP-001 | HIGH | `result_hash` is a canonical result-object hash, not the documented result-file hash (`hash_contract`). | C-016 and hash-based reproduction justifications are weakened; C-002/C-003/C-004 values are not automatically changed. |
| CP-002 | HIGH | The “immutable” preregistration helper overwrites its target on every call (`freeze_overwrite`). | Preregistration-before-execution provenance must be downgraded wherever reruns occurred. |
| CP-003 | HIGH | `05_DATA`, `06_RESULTS`, `07_REPORTS`, `08_REPLICATION`, `99_ARCHIVE` are empty; all 21 SQLite tables have zero rows (`empty_data`). | C-016 is contradicted as a complete provenance record; local artifacts remain inspectable. |
| CP-004 | HIGH | Registry counts, question statuses, IDs, and Git chronology are not mutually authoritative (`registry`). | Status/ID-based conclusions for Q-M008, Q-S9, and 3D work are unresolved. |
| CP-005 | MEDIUM | The external dossier points to an external sandbox not included in the audited tree (`external`). | C-015 remains NOT VERIFIABLE from this tree. |
| CP-006 | MEDIUM | `formal_charge` emits RDKit `MaxAbsPartialCharge`; the visible test does not test it and contains a tautology (`application`). | Molecular application metadata using that field is not scientifically validated. |
| CP-007 | HIGH | Current EXP-0006 interpolation uses `w1-p0` instead of `w1-w0`, and its C2 branch asserts a zero difference (`exp0006`). | C-005’s EXP-0006 component needs a source-version caveat; unqualified C2/re-run claims fail. |
| CP-008 | CRITICAL | Q-P006 cells are byte-identical to Q-P005 and required gates/1-over-ν are absent (`qp006`). | C-007/C-008 cannot use Q-P006 as independent precision evidence. |
| CP-009 | HIGH | EXP-0010 applies one pooled `D_f` pass to a preregistered all-non-power-of-two criterion and omits C7 (`exp0010`). | C-006 remains contradicted; the historical `LATTICE_ARTIFACT` label is unsupported by the frozen gate. |
| CP-010 | HIGH | Q-P007 hardcodes phase-1 `p_c` values and aligns exponent samples to the minimum `n=25` (`qp007`). | C-007’s “resolved by refined `p_c`” interpretation becomes exploratory/inconclusive. |
| CP-011 | HIGH | Q-P007’s cache omits cluster-size arrays and the tau slice removes the only nested array (`qp007_tau`). | C-008’s stored tau branch is invalid/inconclusive. |
| CP-012 | CRITICAL | 3D spanning uses 2D row/column indices for an `L^3` label array; C7 repeats the convention (`3d_boundary`). | C-009 remains inconclusive; no 3D exponent or p_c claim is upgraded. |
| CP-013 | HIGH | The 3D pilot reduces width samples to one tenth, truncates exponents to `n=50`, and empties tau (`3d_runner`). | C-009’s pilot values are exploratory; the “sample-limited” tau explanation is unproven. |
| CP-014 | HIGH | The default 3D runner selects EXP-0013, then hardcodes `tau_L=24` absent from its `L_list`; no main result exists (`3d_main`). | C-009 remains inconclusive and the supplied runner is not a complete main-run route. |
| CP-015 | CRITICAL | Q-M007 reconstructs cell p-values from residuals and a Wilson–Hilferty-like proxy; 38/40 is not a direct 40-cell BH test (`qm007`). | C-010 must remain descriptive only; 38/40 cannot support a mechanism or formal shape discovery. |
| CP-016 | HIGH | The 40-cell script reads only the parent result and the report presents inherited/same-data C7 as independent (`qm007_controls`). | C-010 cannot use 8/8 controls to upgrade the extension; C-016 is further weakened. |
| CP-017 | HIGH | Q-M008 uses upper-prime normalization and different block boundaries from EXP-0008 (`qm008`). | C-014 remains descriptive; Q-M008 is not a matched continuation or asymptotic proof. |
| CP-018 | HIGH | Q-M008 uses rank-wise BH flags instead of step-up and computes extreme tails as `1-cdf` (`qm008`). | C-014 significance language is implementation-qualified and not upgradeable. |
| CP-019 | HIGH | The planned 10^10 sieve returns 157 primes instead of 168 at a 1000-number sanity check (`qm008_sieve`). | No current or future 10^10 result from this code is supportable. |
| CP-020 | HIGH | Q-S9-1/3 writers contain literal dictionaries; stored rates/corrections contradict report controls (`s9_hardcoded`). | C-013 threshold and detector-artifact claims remain invalid/not reproduced. |
| CP-021 | CRITICAL | Q-S9-2 is synthetic and writes `TRUE_*` generation constants as fitted parameters (`s9_synthetic`). | C-013’s EC50/Hill/maximum claims have no empirical support. |
| CP-022 | MEDIUM | EXP-0002 bootstrap p-values are discrete 500-draw tail proportions with a 0.004 resolution floor and epsilon floor (`optics_pvalues`). | C-002’s law reproduction can remain; historical FDR/p-value precision language must be qualified. |
| CP-023 | HIGH | The Collatz “full” artifact is partly hardcoded, covers 3 convergent plus 5 pilot families of 27, and labels timeouts as cycles (`collatz`). | C-012 remains contradicted/incomplete; the tested finite summaries are descriptive only. |
| CP-024 | CRITICAL | EXP-0014 has malformed preregistration provenance, nested result placement, invalid z=3/z=4 values, and hardcoded controls (`feigenbaum`). | C-011 must be split: z=2 remains narrow/reproduced; higher-order and all-controls claims fail. |
| CP-025 | HIGH | The RNG battery pools p-values from shared streams; fresh-seed p-value correlation reaches about 0.995 (`rng`). | C-004 remains method-invalid; `CERTIFIED` cannot follow from the pooled test. |
| CP-026 | HIGH | Older discovery/final-audit summaries preserve stronger headlines than corrected artifacts support (`stale_audit`). | C-016 remains contradicted; consumers should use the later claim registry, not stale headlines. |

## Cross-project patterns

### 1. Provenance contracts are not enforced

CP-001–CP-004 show a consistent failure of the project’s reproducibility layer. A hash with the expected name does not hash result bytes; a helper described as immutable rewrites preregistrations; the advertised central raw/result/database chain is empty; and registry/question/Git records disagree. This means filename, timestamp, or registry status cannot safely stand in for an immutable experiment identity.

### 2. “Independent” follow-ups often reuse the parent data or controls

CP-008, CP-016, and CP-025 are direct examples. Q-P006’s raw cells are byte-identical to Q-P005. Q-M007’s extension reads only the parent result and inherits same-data controls. The RNG battery aggregates p-values that are strongly dependent by construction. Deterministic reruns can produce identical bytes, but deterministic reuse is still not independent replication.

### 3. Stored conclusions outrun the executable decision path

CP-007, CP-009, CP-010, CP-011, CP-013, and CP-014 show preregistered sample sizes, per-size gates, cache structures, or tau sizes that are not what the current runner executes. In these cases a stored `pass`, a null tau, or a narrative table can be an artifact of a different code path or an incomplete decision rather than a measured result.

### 4. Statistical labels are stronger than the calculations

CP-015, CP-017, CP-018, CP-022, and CP-025 concern approximate or dependence-invalid p-values, mismatched null/normalization methods, BH step-up errors, finite Monte Carlo resolution, or pooled dependence. These do not make every underlying finite-sample statistic disappear, but they prevent formal FDR, certification, mechanism, or asymptotic language.

### 5. Empirical outputs can be hardcoded or synthetic

CP-020, CP-021, and CP-023 are direct provenance failures. Literal result dictionaries, assumed Hill parameters, and timeout paths labeled as cycles cannot support the corresponding empirical claims without a traceable raw-data path.

## Impact on the prior claim registry

The later `AUDIT/CLAIM_REGISTRY.md` classifications are generally compatible with this scan, with the following explicit boundaries:

- **C-002:** retain the narrow speckle-law reproduction; downgrade only p-value/FDR precision claims (CP-001, CP-022).
- **C-003:** no new direct reversal here; provenance and application metadata caveats remain (CP-001, CP-006).
- **C-004:** retain `CONTRADICTED / METHOD INVALID`; no RNG certificate can be inferred from pooled dependent p-values (CP-001, CP-025).
- **C-005:** retain the independently supported portions; do not treat the current EXP-0006 pair as an exact source/result replay (CP-007).
- **C-006:** remain contradicted; EXP-0010’s pooled decision cannot support the preregistered lattice-artifact criterion (CP-009).
- **C-007/C-008:** keep the limited 2D findings separate from the invalid Q-P006/Q-P007 follow-up paths (CP-008–CP-011).
- **C-009:** remain inconclusive; neither the pilot nor the missing main run establishes 3D exponents (CP-012–CP-014).
- **C-010/C-014:** remain descriptive only; the formal BH, controls, normalization, and future-sieve evidence do not support a new prime-gap process (CP-015–CP-019).
- **C-011:** preserve the narrow z=2 result while invalidating the historical z=3/z=4 and all-controls package (CP-024).
- **C-012:** remain contradicted/incomplete (CP-023).
- **C-013:** remain invalid/not reproduced (CP-020, CP-021).
- **C-015:** remain not verifiable from this tree (CP-005).
- **C-016:** remain contradicted as a provenance record (CP-001–CP-004, CP-016, CP-026).

## Overlap with the prior audit

The findings deliberately cite `AUDIT/CLAIM_REGISTRY.md` and `AUDIT/BUGS.md` in each finding’s `prior_overlap` field. This is an independent second pass in scope and evidence selection, not an independent confirmation of every prior conclusion. The strongest cross-layer additions are the paired source/result drift in EXP-0006, the exact Q-P005/Q-P006 byte identity, the 3D semantic boundary mismatch, the Q-M007/Q-M008 formula/method mismatches, and the hardcoded/synthetic Q-S9 result paths. Existing audit artifacts should therefore be treated as context and leads, not as a substitute for the current evidence in `findings.json`.

## Limitations and benign alternatives

- The audit is read-only and does not rerun historical simulations. A result generated by a corrected source version, a deterministic rerun, or an artifact stored outside the supplied tree could explain some source/result differences; the supplied pair is nevertheless not self-reproducing.
- Byte identity proves equality of the supplied NPZ files, not whether copying or deterministic regeneration caused the equality. Either explanation defeats an independent-replication interpretation.
- The empty central directories/database may be intentional caches or an incomplete snapshot. They still cannot substantiate the global provenance claims made by the documentation.
- The external sandbox is not included in the audited tree. CP-005 is a scope/provenance finding, not a finding that the external results are false.
- `ok: true` in `verification_results.json` means a read-only case executed successfully. It should not be read as “the historical claim is true.”
- The enclosing Git repository is `C:/Users/natha`, not the laboratory subdirectory, and has zero commits; project files are untracked. Git chronology and authorship therefore cannot be inferred from the supplied repository state.

## Recommended remediation order

1. Establish content-addressed raw/result manifests, immutable preregistration IDs, and a single canonical result path; make the database either populated or explicitly non-authoritative.
2. Stop treating Q-P006/Q-M007 and inherited controls as independent; rerun follow-ups with isolated seeds, raw fields, and a dependency-aware analysis.
3. Correct and independently test the 3D opposite-face spanning observable before any production 3D run.
4. Recompute prime-gap nulls and p-values with a finite-range/dependence-aware model, proper BH step-up, and stable survival functions; repair the sieve before any 10^10 run.
5. Remove hardcoded/synthetic S9 outputs from empirical claims and require raw observations plus input hashes.
6. Replace the pooled RNG certificate with per-test calibration over independent fresh streams and a declared dependence model.
7. Mark older discovery/final-audit headlines as superseded wherever the later claim registry or this scan changes their status.

## Artifacts

- `findings.json` — machine-readable findings, evidence, alternatives, severity/confidence, and claim impact.
- `verify_findings.py` — read-only case runner.
- `verification_results.json` — final 25-case evidence output; all cases are `ok: true`.
- `verification.log` — combined final verifier log.
- `case_logs/` — per-case logs from the verification run.
- `scan_claims_data.py` / `scan_output.json` — whole-tree inventory, hashes, parse failures, and references.
- `git_provenance.log` — Git-root and untracked-file evidence.
- `commands.md` — command index and one minimal command per finding.
