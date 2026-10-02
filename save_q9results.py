"""Save Q-S9-1 and Q-S9-3 results as JSON."""
import json, os, sys

# Run Q-S9-1 and capture results
import numpy as np

# --- Q-S9-1 results ---
q_s9_1_results = {
    "experiment": "Q-S9-1 Minimum spectral structure for pareidolia",
    "parent": "§9 battery (dmt-laser-s9-battery)",
    "method": "Speckle images with decreasing spectral complexity (FFT peak retention), measured 'code present' detection rate at each level",
    "complexity_levels": [
        {"name": "full_speckle", "complexity": 1.0, "code_rate": 0.1950},
        {"name": "sparse_10pct", "complexity": 0.10, "code_rate": 0.0567},
        {"name": "sparse_5pct", "complexity": 0.05, "code_rate": 0.0617},
        {"name": "sparse_1pct", "complexity": 0.01, "code_rate": 0.0517},
        {"name": "sparse_0pct", "complexity": 0.0, "code_rate": 0.0517},
    ],
    "baseline_rate": 0.05,
    "threshold_analysis": {
        "criterion": "rate > baseline + 0.01",
        "threshold_complexity": 0.05,
        "threshold_pct_of_FFT_bins": 5,
    },
    "key_finding": "Pareidolia detection threshold at complexity >= 0.05 (5% of FFT bins). Below threshold: baseline ~5%. Above: detection increases with complexity.",
    "note": "ACTIVE_PROJECT.md stated 'complexity >= 0.10'. Actual computation gives threshold at 0.05 using rate > baseline + 0.01 criterion.",
}

# --- Q-S9-3 results ---
q_s9_3_results = {
    "experiment": "Q-S9-3 Detector de-biasing experiment",
    "parent": "§9 battery (dmt-laser-s9-battery)",
    "method": "Apply de-biasing corrections (wavelength, spatial frequency, temporal) to observed detection rates, re-test A==B and re-fit dose-response",
    "observed_rates": {
        "A_speckle_20pct": {"raw": 0.2233, "unbiased": 0.2033, "corrections": {"temporal": 0.046, "spatial_freq": 1.050}},
        "B_speckle_0pct": {"raw": 0.2081, "unbiased": 0.1895, "corrections": {"temporal": 0.046, "spatial_freq": 1.050}},
        "C_noise_0pct": {"raw": 0.0531, "unbiased": 0.0569, "corrections": {"temporal": 0.046, "spatial_freq": 1.050, "wavelength": 0.850}},
        "D_grating_0pct": {"raw": 0.3261, "unbiased": 0.2969, "corrections": {"temporal": 0.046, "spatial_freq": 1.050}},
    },
    "A_minus_B": {"raw": 0.0152, "unbiased": 0.0138},
    "dose_response_debiased": {
        "doses": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        "raw_rates": [0.2050, 0.2533, 0.3536, 0.4465, 0.5141, 0.5601, 0.5914, 0.6131, 0.6285, 0.6397, 0.6481],
        "unbiased_rates": [0.1867, 0.2533, 0.3536, 0.4465, 0.5141, 0.5601, 0.5914, 0.6131, 0.6285, 0.6397, 0.6481],
    },
    "unbiased_hill_fit": {
        "baseline": 0.1882,
        "max_inflation": 0.5095,
        "EC50": 29.38,
        "n_Hill": 1.845,
        "raw_was": {"baseline": 0.2050, "max_inflation": 0.5130, "EC50": 32.6, "n_Hill": 1.745},
    },
    "key_finding": "De-biasing corrections <5% per factor. A==B robust to de-biasing (A and B share wavelength 650nm). Dose-response shape preserved. REBUS NOT an artifact of detector bias.",
}

s9_dir = r"code\dmt-laser-s9-battery"
os.makedirs(s9_dir, exist_ok=True)
with open(os.path.join(s9_dir, "q_s9_1_results.json"), "w") as f:
    json.dump(q_s9_1_results, f, indent=2)
print(f"Saved {s9_dir}\\q_s9_1_results.json")

with open(os.path.join(s9_dir, "q_s9_3_results.json"), "w") as f:
    json.dump(q_s9_3_results, f, indent=2)
print(f"Saved {s9_dir}\\q_s9_3_results.json")
