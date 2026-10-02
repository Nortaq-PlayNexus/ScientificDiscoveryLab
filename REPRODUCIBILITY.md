# REPRODUCIBILITY

How to reproduce anything in this laboratory on this machine.

## Machine

| Item | Value |
|---|---|
| OS | Windows 10 Home |
| CPU | Intel Core i7-8700 (6C / 12T) @ 3.20 GHz |
| RAM | 24 GB |
| GPU | NVIDIA GTX 1080 8 GB |
| Free disk | ~1.5 TB (C:) |

## Software

| Tool | Version |
|---|---|
| Python | 3.14.7 |
| numpy | 2.5.3 |
| scipy | 1.18.1 |
| matplotlib | 3.11.2 |
| scikit-image | 0.26.0 |
| scikit-learn | 1.9.1 |
| sympy | 1.14.0 |
| torch | 2.14.0+cpu (CPU-only) |
| torchvision | 0.29.0+cpu |
| Pillow | 12.3.0 |
| ImageIO | 2.37.4 |

Note: torch is the CPU build. JAX, TensorFlow, pandas, astropy, statsmodels,
plotly/dash are NOT installed. pandas absence means shared code avoids pandas
dependencies; if a future analysis needs pandas, install it and record the change.

## Determinism rules

- Random numbers MUST come from `engine.utilities.rng(label, seed)` (sha256-derived
  Generator, independent of Python's `hash()` salt). Verified stable across fresh
  processes.
- Record the experiment's random seed in `experiment.json`.
- When a result depends on a seed, run multiple seeds and report the distribution.

## Every experiment must record (experiment.json)

- experiment ID
- date/time (UTC ISO 8601)
- Python version
- dependency versions (key libs)
- git commit if the investigation is in a repo
- random seed
- parameters
- dataset file hashes (sha256)
- result file hashes (sha256)

## Immutable preregistrations

- New protocols must be created with
  `engine.hypothesis_testing.prereg.freeze_config()`.
- Creation uses exclusive filesystem semantics. Calling it again for an
  existing destination raises `PreregistrationExistsError`; it never silently
  overwrites a timestamp or parameter set.
- Each frozen JSON embeds `config_sha256`, calculated over canonical UTF-8 JSON
  with sorted keys, compact separators, and nonfinite numbers rejected.
- Load with `verify_frozen_config()` and verify expected experiment/parameter
  fields before execution.
- Post-freeze changes go to `log_change()` as a separate SHA-256 hash chain.
  This detects accidental/local edits but is not an external signature; export
  or anchor the chain head when stronger tamper evidence is required.

## Result hash scopes

`result_hash` in a new `experiment.json` is explicitly the hash of the
**canonical JSON result object**. When a separate result file exists, pass its
path as `result_path`; the record then stores its exact byte length and SHA-256
under `result_artifact` with scope `exact_artifact_bytes`. Do not treat these
two hashes as interchangeable. `verify_experiment_result_hash()` checks both
when the artifact path is available.

## Test-state isolation

Pytest sets `SOVEREIGN_BIOLAB_DATABASE_URL` to a process-specific temporary
SQLite database during conftest import. Tests may create and remove rows, but
must not mutate the persistent `sovereign_biolab.db`. Verify its SHA-256 before
and after any future database test campaign.

## Standard commands

- Infra self-test: `python -m engine.tests.run_infra_validation` (or the equivalent
  runner in `04_SHARED_ENGINE/`).
- Dashboard: `python dashboard.py` (Open `http://127.0.0.1:8008`).
- Each investigation documents its own run commands in its `REPORT/` or README.

## Environment gotchas

- Global Python 3.14.7 at `python`. The coherent-optical-ai-sandbox uses its own
  `.venv` (Python 3.14.7).
- PowerShell: run `$env:PYTHONUTF8=1` where files contain non-ASCII box-drawing etc.
- Never delete files under `05_DATA/raw/`. Raw data is immutable.