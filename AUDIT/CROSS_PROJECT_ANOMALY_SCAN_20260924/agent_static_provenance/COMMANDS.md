# Static/provenance audit command manifest

All commands below were run from `C:\Users\natha\ScientificDiscoveryLab` on 2026-09-24. Historical experiment writers were not executed. The only writes from verification commands were new audit artifacts under this directory (and Python bytecode caches, which were excluded/removed from the final inventory).

## Commands

```text
python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance/scan_static_provenance.py
python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance/verify_static_findings.py
python -m py_compile AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance/verify_cross_project_findings.py
python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance/verify_cross_project_findings.py
python -m json.tool AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance/findings.json
python -c "import json; json.load(open('AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance/cross_project_verification.json',encoding='utf-8'),parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))"
git status --short -- AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_static_provenance
```

## Preserved logs and machine-readable evidence

- `scan_static_provenance.log.txt` — first whole-tree scan attempt; it stopped on an AST scanner `AttributeError` and is retained rather than rewritten.
- `scan_static_provenance.log` — scanner output/status.
- `verify_static_findings.log` — candidate verification output.
- `verify_static_findings.py` and `verified_candidate_evidence.json` — first-pass safe reproductions.
- `verify_cross_project_findings.py` and `cross_project_verification.json` — final read-only cross-project verifier.
- `cross_project_verification.log` — successful final verifier run (`checks: 21`).
- `result_hash_check.txt` — recorded-versus-file hash comparison.
- `findings.json` — final strict-JSON finding set.

## Safety notes

- No historical `.py` result writer was invoked.
- Q-M007, Q-P006, Q-P007, EXP-0006, Feigenbaum, S9, and Q-M008 checks were static reads or in-memory calculations.
- The preregistration overwrite demonstration used `tempfile.TemporaryDirectory()` only.
- The SQLite inspection used a read-only URI connection.
- Existing audit and experiment artifacts were not edited.
