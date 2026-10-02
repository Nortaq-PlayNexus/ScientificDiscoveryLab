# Parallel-runner coexistence note

During finalization I detected a separate, pre-existing runner in this same assigned
folder:

- `run_broadband_audit.py`
- `run_environment.json`
- `full_run.log`

It was running with `--n-real 8` and is not the implementation used for the report
in `REPORT/SUBAGENT_REPORT.md`. I did not stop, edit, overwrite, or incorporate its
in-progress files. The report and all primary artifacts I generated are namespaced
under `CODE/`, `RESULTS/`, `REPORT/`, and `LOGS/` within this directory. The other
runner should be allowed to finish independently so the main auditor can compare
both protocols if useful.
