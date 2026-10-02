# Second-Pass Audit Log

Date: 2026-09-24

1. Read the first independent audit and treated all historical reports/registries as claims.
2. Launched isolated whole-tree static/numerical/claims scans under `AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/`.
3. Inspected all investigation runners, replication scripts, result JSON/NPZ files, controls, preregistrations, shared engine, application code, and tests.
4. Ran `MAIN_AUDIT/second_pass_evidence.py` (read-only historical tree).
5. Ran `agent_numerical_statistics/reproduce.py` (read-only historical tree).
6. Ran `python -m pytest`: 287 passed, 411 warnings.
7. Detected that the test run changed `sovereign_biolab.db` byte-for-byte while leaving all table counts at zero. Restored the exact baseline copy from `C:/Users/natha/AppData/Local/Temp/opencode/ScientificDiscoveryLab_audit_20260924_0325/sovereign_biolab.db`; baseline SHA-256 verified.
8. Rechecked the 513-file baseline manifest: no non-AUDIT source/result file is changed or missing. Only prior audit files remain different from the original baseline.
9. Preserved the malformed sub-agent artifact hash manifest rather than rewriting it; documented it as N-16.
10. Collected the three independent reviewer reports: `agent_static_provenance` (25 findings / 21 strict checks), `agent_numerical_statistics` (21 findings), and `agent_claims_data` (26 findings / 25 verification cases).
11. Integrated the additional EXP-0010 pooled-gate, same-stream C7, Q-M007 support-bound, S9 unit, and registry/data provenance findings into this consolidated report.
12. Revalidated the consolidated JSON after the additions; it contains 25 N-series entries (some are corroborations or qualifications of the first audit).

Primary report: `SECOND_PASS_REPORT.md`
Machine-readable findings: `second_pass_findings.json`
Raw evidence: `second_pass_evidence.json`
Test side-effect record: `pytest_side_effect_record.json`
