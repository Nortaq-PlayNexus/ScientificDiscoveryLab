# Security Policy

## Scope

A computational research laboratory: numerical simulation code, JSON/YAML result
files, Markdown documents, and a small SQLite-backed experiment store. There is no
web server, no authentication layer, no user-facing network service, and no
`eval`, `pickle`, or dynamic code loading in the analysis path.

**Known vulnerabilities: none identified.**

## Dependencies

Pinned in `requirements.txt` — scientific Python only (`numpy`, `scipy`,
`scikit-learn`, `sympy`, `networkx`, `matplotlib`, `pandas`) plus the
laboratory's own `sqlite3`-backed store. All are standard PyPI packages installed
from PyPI, not from private indexes. `pytest` is required to run the suite.

## What is deliberately not supported

- Running as a service or exposing any port.
- Processing untrusted structured input. The JSON readers use the standard
  library and take no code-execution paths, but the laboratory does not promise
  safety on adversarial schemas.
- Loading model weights or remote resources.
- Any workflow holding credentials. Nothing in this repository requires them.

## Data integrity as a security property

This repository's main risk is not network-facing. It is **silent modification of
recorded evidence**, which is why the following are treated as integrity
concerns and covered by the audit controls:

- Raw results are read-only; digests are recorded in manifests and verified.
- Immutable audit baselines must never be refreshed to make a failing test pass.
- The append-only registry's historical prefix is pinned separately from the live
  file, so a wholesale rewrite cannot launder itself.
- `manifest.json` records a SHA-256 for every published file.

See `RESEARCH_RULES.md` §11, `tools/verify_manifest.py`, and the
`AUDIT_REPAIR_N04…` investigation.

## Reporting

Open a private security advisory, or contact the maintainers directly. Please do
not open a public issue for an unfixed vulnerability.

Given the scope, the most likely reports concern the integrity controls rather
than conventional vulnerabilities. Those are equally welcome — several defects
found during self-audit are documented in `AUDIT/`, `CHANGELOG.md` and
`CHANGELOG_TEST_TOLERANCE_REPAIR.md`.