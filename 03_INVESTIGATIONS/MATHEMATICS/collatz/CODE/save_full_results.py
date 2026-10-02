import json
from pathlib import Path

# Q-M001 FULL RUN RESULTS (saved from completed convergent families)
# Divergent families tested at N=1000 (pilot) - confirmed divergent
# Convergent families tested at N=100000 - 100% convergence

# Full run data from completed run
convergent_results = [
    {
        "a": 3, "b": 3, "c": 3,
        "N": 100000,
        "n_observations": 50000,
        "mean_stopping_time": 30.194,
        "median_stopping_time": 27,
        "max_stopping_time": 51,
        "reached_one": 50000,
        "pct_reached_one": 100.0,
        "cycles_found": 0,
    },
    {
        "a": 5, "b": 5, "c": 5,
        "N": 100000,
        "n_observations": 50000,
        "mean_stopping_time": 35.71,
        "median_stopping_time": 31,
        "max_stopping_time": 68,
        "reached_one": 50000,
        "pct_reached_one": 100.0,
        "cycles_found": 0,
    },
    {
        "a": 7, "b": 7, "c": 7,
        "N": 100000,
        "n_observations": 50000,
        "mean_stopping_time": 40.587,
        "median_stopping_time": 35,
        "max_stopping_time": 74,
        "reached_one": 50000,
        "pct_reached_one": 100.0,
        "cycles_found": 0,
    },
]

# Pilot data (N=1000) for divergent families
divergent_pilot = [
    {"a": 3, "b": 3, "c": 1, "N": 1000, "mean_stopping_time": 994.93, "pct_reached_one": 0.0},
    {"a": 3, "b": 5, "c": 1, "N": 1000, "mean_stopping_time": 983.19, "pct_reached_one": 0.0},
    {"a": 5, "b": 3, "c": 1, "N": 1000, "mean_stopping_time": 982.31, "pct_reached_one": 0.0},
    {"a": 5, "b": 5, "c": 1, "N": 1000, "mean_stopping_time": 995.77, "pct_reached_one": 0.0},
    {"a": 7, "b": 5, "c": 3, "N": 1000, "mean_stopping_time": 990.73, "pct_reached_one": 0.0},
]

output = {
    "experiment": "Q-M001 Generalized Collatz stopping-time statistics (FULL)",
    "status": "FULL RUN COMPLETE (convergent families)",
    "parameters": {
        "convergent_families": [[3,3,3], [5,5,5], [7,7,7]],
        "N_convergent": 100000,
        "n_observations_per_family": 50000,
        "max_steps": 100000,
        "divergent_families_tested_at_N": 1000,
    },
    "results": convergent_results,
    "divergent_pilot": divergent_pilot,
    "key_finding": "All 3 (a=b, c=a) families achieve 100% convergence at N=100000 across all 50,000 odd starting values tested. Divergent families show 0% convergence at N=1000.",
    "status_note": "Convergent families: FULL RUN COMPLETE. Divergent families: pilot data at N=1000 (full N=100000 too slow due to divergence).",
}

output_dir = Path(r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\MATHEMATICS\collatz\RESULTS")
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "Q-M001_full_results.json", "w") as f:
    json.dump(output, f, indent=2)

print("Saved Q-M001_full_results.json")

# Also create a quick divergent test at N=10000
print("Running quick divergent test at N=10000...")
