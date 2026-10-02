# Reproduction commands

All commands are read-only. Run them from `C:\Users\natha\ScientificDiscoveryLab` unless a command says otherwise. The script does not call historical experiment writers and does not write result files.

## Full captured run

```powershell
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py 2>&1 | Out-File -Encoding utf8 AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduction.log
```

## Individual cases

```powershell
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case prime_first_bin
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case qm007_pvalue
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case qm008_method_mismatch
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case qm008_pvalue_bh
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case qp006_duplicate
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case qp007_sample
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case qp007_cache
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case qp007_pc
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case three_d_boundary
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case three_d_sample
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case three_d_provenance
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case exp0007_draws_precision
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case optics_floor
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case feigenbaum_results
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case s9_hardcoded
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case s9_synthetic
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case s9_units
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case rng_dependence
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case collatz
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case exp0009_c7_streams
python -B AUDIT/CROSS_PROJECT_ANOMALY_SCAN_20260924/agent_numerical_statistics/reproduce.py --case r3_coupling
```

The full run uses Python, NumPy, and SciPy already present in the laboratory environment. The RNG case uses the repository's deterministic `engine.utilities.core.rng` and `rng_battery`; the 3-D boundary case imports the repository's `perc_engine` but uses synthetic labels and writes nothing.
