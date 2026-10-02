# PROJECT INVENTORY — Independent Audit 2026-09-24

**Source tree:** `C:\Users\natha\ScientificDiscoveryLab`  
**Historical outputs:** preserved; no original experiment result was intentionally overwritten.  
**Inventory convention:** recursive file inventory excluding `__pycache__`, `.git`, and `.pytest_cache`; audit-generated files are included in the current count and identified separately.

## 1. Counts

### Baseline inventory at audit initialization

- 513 files
- 221,270,825 bytes
- 135 Python files
- 240 Markdown files
- 85 JSON files
- 17 NPZ files
- 1 RAR archive
- 1 SQLite database
- 1 Python parse anomaly (a UTF-8 BOM in `run_collatz.py`; not evidence of a failed run)

The baseline machine-readable records are preserved in:

- `AUDIT/INDEPENDENT_AUDIT_20260924/file_manifest.json`
- `AUDIT/INDEPENDENT_AUDIT_20260924/inventory_summary.json`

### Current inventory after independent audit artifacts

A fresh inventory on 2026-09-24 found **633 files / 225,411,614 bytes**, excluding caches. The increase is entirely due to audit scripts, raw audit outputs (including the EXP-0003 control CSVs/JSON), logs, the preserved prior-audit copy, and the new EXP-0003 investigation addendum. Current machine-readable record:

- `AUDIT/INDEPENDENT_AUDIT_20260924/current_inventory.json`

Current extension counts include 150 `.py`, 262 `.md`, 116 `.json`, 20 `.npz`, 40 `.log`, 11 `.csv`, 4 `.png`, 1 `.db`, and 1 `.rar` (plus small text/config files).

## 2. Top-level structure

| Path | Contents / audit relevance |
|---|---|
| `00_FOUNDATION/` | Scientific-method, statistics, simulation, falsification, and terminology rules |
| `01_RESEARCH_MAP/` | 15 field-level research maps and notes |
| `02_CANDIDATE_PROBLEMS/` | Candidate-question registries and priority lists |
| `03_INVESTIGATIONS/` | 292 current files across acoustics, fluid dynamics, mathematics, optics, other, and physics |
| `04_SHARED_ENGINE/` | Shared RNG, statistics, reproducibility, simulation, and validation code |
| `05_DATA/` | Directory scaffold; raw/processed/generated/external data directories are empty |
| `05_EXTERNAL_RESEARCHER_DOSSIER/` | External dossier; referenced source/results are not included in this audit |
| `06_RESULTS/` | Categorized result directories; no files found in the four category directories at baseline |
| `07_REPORTS/` | Report category scaffold |
| `08_REPLICATION/` | Replication category scaffold |
| `99_ARCHIVE/` | Present but empty at baseline |
| `src/` | 33 application/source files |
| `tests/` | 29 test files |
| `AUDIT/` | This independent audit and preserved `PRIOR_AUDIT_20260923/` |
| root | Registry, status, hypothesis/question lists, helper scripts, database, archive, and dashboard files |

## 3. Investigation inventory

| Domain | Investigation areas observed | Important audit artifacts |
|---|---|---|
| OPTICS | speckle contrast, vortex density | EXP-0002/0003 configs, code, results, replication reports, literature |
| PHYSICS | 2D percolation, Q-P005/Q-P006/Q-P007, 3D percolation | threshold/exponent runs, raw NPZ cells, C7 reports, pilot/main configs |
| MATHEMATICS | prime gaps, Collatz, Feigenbaum constants | raw prime results, hardcoded S9 outputs, Feigenbaum engine/results |
| OTHER | RNG certification, cone-mosaic/S9 materials | battery code/results, hardcoded S9 writer, synthetic dose-response code |
| ACOUSTICS | water sound response | active scaffold; insufficient data for scientific validation |
| FLUID_DYNAMICS | notes/scaffold only | no completed audited result |

## 4. Data and provenance findings

### SQLite database

`sovereign_biolab.db` is 184,320 bytes with 21 tables. Every table queried during the audit had zero rows, including `experiments`, `datasets`, `hypotheses`, `evidence_records`, `results`, and `simulations`. It is a schema artifact, not an independent raw-data source.

### `05_DATA`

The following directories contained no files at the baseline audit:

- `05_DATA/raw/`
- `05_DATA/processed/`
- `05_DATA/generated/`
- `05_DATA/external_sources/`

### Archive

`percolation.rar` was inspected as an archive. Its contents are a percolation snapshot/duplicate of material already represented in the tree, not an independent experiment or external replication. It cannot establish provenance by itself.

### Git/provenance

The repository has no commits and the files are untracked. Therefore historical authorship, chronology, and “original vs copied” claims cannot be established from Git history. SHA-256 manifests establish current bytes only.

## 5. Identifier and copy findings

- Q-P006 raw cell files at L=512, 1024, and 2048 are byte-identical copies of Q-P005 files, despite the Q-P006 note claiming no cells were reused.
- `HYP-005` is mentioned by both EXP-0008 prime gaps and EXP-0009 percolation exponents.
- `EXP-0009` is reused by Q-P005, Q-P006, and Q-P007.
- `EXP-0012` and `EXP-0013` collide with unrelated prime-gap filenames/scaffolds.
- `EXP-0015` collides with acoustics/fluid-dynamics scaffolding.
- The Feigenbaum canonical `RESULTS` directory is empty; stored output is nested under `CODE/03_INVESTIGATIONS/.../RESULTS`.
- The Q-P007 cache stores nested cluster-size arrays incorrectly; the current runner cannot reload its own cache (`KeyError: sizes`).

## 6. Test and source baseline

`python -m pytest` passed **287 tests** with 411 warnings in 26.60 seconds. This verifies software-level behavior under the test suite, not scientific validity. A direct `pytest` launcher previously had an import-path/collection issue; the module invocation is the valid baseline.

The 149 current Python-file inventory includes audit scripts. The one AST parse warning is a BOM at the start of `03_INVESTIGATIONS/MATHEMATICS/collatz/CODE/run_collatz.py`; Python itself normally accepts a UTF-8 BOM when executing the file. It is retained as a parser/provenance warning, not silently “fixed.”

## 7. Inventory interpretation

The laboratory has substantial documentation, deterministic code, and several valid software reproductions. It does **not** have a populated raw-data repository, commit-level provenance, or a complete set of independent raw measurements for all claims. Claims must therefore be classified from the actual result files and reruns, not from filenames, registry labels, or prior audit summaries.
