# Verification command index

Run commands from the repository root:

```text
C:\Users\natha\ScientificDiscoveryLab
```

## Final read-only run

The complete 25-case run used for the final `verification_results.json` and `verification.log` was:

```powershell
python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py *> AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verification.log
```

The whole-tree inventory command was:

```powershell
python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/scan_claims_data.py
```

The scanner writes only `scan_output.json` in this audit-output directory. The verifier does not call a historical experiment writer; its temporary preregistration reproduction is created and removed under this output directory.

## One command per finding

Each command below is the minimal read-only reproduction case linked from the corresponding finding in `findings.json`.

| Finding | Verification case | Command |
|---|---|---|
| CP-001 | `hash_contract` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case hash_contract` |
| CP-002 | `freeze_overwrite` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case freeze_overwrite` |
| CP-003 | `empty_data` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case empty_data` |
| CP-004 | `registry` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case registry` |
| CP-005 | `external` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case external` |
| CP-006 | `application` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case application` |
| CP-007 | `exp0006` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case exp0006` |
| CP-008 | `qp006` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case qp006` |
| CP-009 | `exp0010` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case exp0010` |
| CP-010 | `qp007` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case qp007` |
| CP-011 | `qp007_tau` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case qp007_tau` |
| CP-012 | `3d_boundary` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case 3d_boundary` |
| CP-013 | `3d_runner` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case 3d_runner` |
| CP-014 | `3d_main` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case 3d_main` |
| CP-015 | `qm007` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case qm007` |
| CP-016 | `qm007_controls` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case qm007_controls` |
| CP-017 | `qm008` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case qm008` |
| CP-018 | `qm008` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case qm008` |
| CP-019 | `qm008_sieve` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case qm008_sieve` |
| CP-020 | `s9_hardcoded` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case s9_hardcoded` |
| CP-021 | `s9_synthetic` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case s9_synthetic` |
| CP-022 | `optics_pvalues` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case optics_pvalues` |
| CP-023 | `collatz` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case collatz` |
| CP-024 | `feigenbaum` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case feigenbaum` |
| CP-025 | `rng` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case rng` |
| CP-026 | `stale_audit` | `python AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_claims_data/verify_findings.py --case stale_audit` |

Running an individual case overwrites `verification_results.json` with that case only; rerun the complete command above before relying on the aggregate JSON. Per-case logs are retained under `case_logs/`.

## Structural validation

After editing an output JSON file, the following read-only check was used to confirm syntax, unique IDs, required fields, case links, and successful case status:

```powershell
@'
import json
from pathlib import Path
root = Path.cwd()
out = root / "AUDIT" / "CROSS_PROJECT_ANOMALY_SCAN_20260924" / "agent_claims_data"
findings = json.loads((out / "findings.json").read_text(encoding="utf-8"))
results = json.loads((out / "verification_results.json").read_text(encoding="utf-8"))
items = findings["findings"]
required = {"id", "title", "category", "severity", "confidence", "prior_overlap", "evidence", "anomaly", "benign_alternative", "effect_on_prior_claim", "minimal_reproduction_command", "verification_case", "verification_artifact"}
assert [x["id"] for x in items] == [f"CP-{i:03d}" for i in range(1, 27)]
assert all(required <= set(x) for x in items)
assert len(results["cases"]) == 25
assert all(results["cases"][x["verification_case"]]["ok"] is True for x in items)
print("findings/verification JSON checks passed")
'@ | python -
```

The final check found 26 unique finding IDs, 25 successful verification cases, and no unlinked or failed finding case.
