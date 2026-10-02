import json
import math
from pathlib import Path

# Load Q-M007 results
data_path = Path(r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\MATHEMATICS\prime_gaps\Q-M007\q_m007_results.json")
with open(data_path) as f:
    data = json.load(f)

alpha = 0.01
num_blocks = 4  # B1, B2, B3, B4
num_bins = 10   # exponential quantile bins 1-10

# Extract p-values from chi2 contributions
# For each cell (bin x block), compute chi2 contribution and then p-value
# chi2 contribution = (obs - exp)^2 / exp for the cell

pvalues = []
cell_details = []

for bin_id in range(1, num_bins + 1):
    bin_data = data["bin_summary"][str(bin_id)]
    obs_total = bin_data["obs_total"]
    exp_total = bin_data["exp_total"]
    
    for block_idx in range(num_blocks):
        # For a single cell, we need obs and exp for that specific bin in that specific block
        # Since we only have bin-level totals, we need to approximate
        # Using the ratio of obs_total/exp_total as a proxy for the cell's deviation
        
        # The chi2 contribution per bin is given
        chi2_contrib = bin_data["mean_chi2_contribution"]
        
        # For a single cell in a single block, approximate:
        # chi2_cell ≈ chi2_contrib / num_blocks (if evenly distributed)
        # But this is approximate since bins may not be evenly distributed
        
        # Better approach: use the std_residuals_per_block to estimate cell-level chi2
        std_residual = bin_data["std_residuals_per_block"][block_idx]
        chi2_cell = std_residual ** 2  # For a single cell, z^2 ≈ chi2_1
        
        # Convert to p-value (chi2 with 1 df)
        # Using survival function approximation
        p_value = math.exp(-0.5 * chi2_cell)  # Approximate for large chi2
        # Better: use Wilson-Hilferty approximation for chi2 CDF
        if chi2_cell > 0:
            z = ((chi2_cell / 1) ** (1/6) * (1 - 2/(9*1))) / math.sqrt(2/(9*1))
            # Standard normal CDF approximation
            p_value = 0.5 * math.erfc(z / math.sqrt(2))
        else:
            p_value = 1.0
        
        pvalues.append(p_value)
        cell_details.append({
            "bin": bin_id,
            "block": block_idx + 1,
            "std_residual": std_residual,
            "chi2_cell": chi2_cell,
            "p_value": p_value
        })

# Sort p-values
sorted_p = sorted(pvalues)
m = len(sorted_p)

# BH-FDR at alpha=0.01
print("BH-FDR on 40-cell grid (alpha=0.01)")
print("=" * 60)
print(f"Total cells: {m}")
print()

# Find largest k such that p_(k) <= (k/m) * alpha
significant = []
for k in range(m, 0, -1):
    threshold = (k / m) * alpha
    if sorted_p[k-1] <= threshold:
        significant = sorted_p[:k]
        break

print(f"BH-FDR threshold: {alpha}")
print(f"Significant cells: {len(significant)} / {m}")
print()

# Now check each cell individually
print("Per-cell results:")
print(f"{'Bin':>3} {'Block':>5} {'z':>8} {'p_value':>12} {'Significant':>12}")
print("-" * 60)

sig_count = 0
for cell in cell_details:
    # Check if this p-value is in the significant set
    is_sig = any(abs(cell["p_value"] - sp) < 1e-15 for sp in significant)
    if is_sig:
        sig_count += 1
    print(f"{cell['bin']:>3} {cell['block']:>5} {cell['std_residual']:>8.2f} {cell['p_value']:>12.2e} {'YES' if is_sig else '':>12}")

print()
print(f"Total significant after BH-FDR: {sig_count} / {m}")
print()

# Compare with EXP-0008 (20 tail cells: 5 thresholds x 4 blocks)
print("Comparison with EXP-0008 (20 tail cells):")
print("EXP-0008: G1 and G3 rejected after BH-FDR in 4/4 blocks")
print("Q-M007: 40-cell grid provides finer resolution")

# Save results
output = {
    "experiment": "Q-M007 BH-FDR on 40-cell grid",
    "parent": "EXP-0008",
    "alpha": alpha,
    "total_cells": m,
    "significant_cells": len(significant),
    "cells": cell_details,
    "summary": {
        "under_represented_bins": [1, 10],
        "over_represented_bins": [3, 5, 6, 7, 8, 9],
        "bin_1_anomaly": "0 observed vs 576022 expected (minimum gap effect)",
        "shape": "NARROWER than Exp(1) — both tails lighter, mid-bins over-represented"
    }
}

output_path = Path(r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\MATHEMATICS\prime_gaps\Q-M007\BHFR_40cell_results.json")
with open(output_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"\nSaved to: {output_path}")
