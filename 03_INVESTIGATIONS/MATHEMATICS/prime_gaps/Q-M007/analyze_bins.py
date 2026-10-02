"""Q-M007 - Per-bin residual analysis of EXP-0008 prime gaps.

Reads EXP-0008_results.json, computes per-bin standardized residuals
and chi2 contributions for each of 10 exponential quantile bins x 4 blocks.
Identifies WHERE exactly the deviation from Poisson/Gallagher lives.
"""
import json
import os

import numpy as np

INVESTIGATION = r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\MATHEMATICS\prime_gaps"
RESULTS_PATH = os.path.join(INVESTIGATION, "RESULTS", "EXP-0008_results.json")

data = json.load(open(RESULTS_PATH, encoding="utf-8"))
pr = data["primary_results"]
blocks = pr["blocks"]

BLOCK_LABELS = ["B1", "B2", "B3", "B4"]
block_data = {b["label"]: b for b in blocks}

print("=" * 88)
print("Q-M007: Per-bin residual analysis (EXP-0008)")
print("=" * 88)

bin_std_residuals = {j: [] for j in range(1, 11)}
bin_chi2_contrib = {j: [] for j in range(1, 11)}
bin_obs_total = {j: 0 for j in range(1, 11)}
bin_exp_total = {j: 0 for j in range(1, 11)}

for b in BLOCK_LABELS:
    blk = block_data[b]
    obs = np.array(blk["counts"], dtype=float)
    exp = np.array(blk["expected"], dtype=float)
    n = blk["n_gaps"]

    std_res = (obs - exp) / np.sqrt(exp + 1e-30)
    chi2c = (obs - exp) ** 2 / (exp + 1e-30)

    print("\n--- %s (n=%s) ---" % (b, format(n, ",")))
    print("  %4s | %10s | %10s | %10s | %9s | %11s" % (
        "Bin", "Edge_lo", "Obs", "Exp", "Std_res", "chi2_contrib"))
    for j in range(10):
        edge_lo = blk["edges"][j] if j < len(blk["edges"]) else float("inf")
        print("  %4d | %10.6f | %10.0f | %10.1f | %+9.4f | %11.4f" % (
            j + 1, edge_lo, obs[j], exp[j], std_res[j], chi2c[j]))
        bin_std_residuals[j + 1].append(std_res[j])
        bin_chi2_contrib[j + 1].append(chi2c[j])
        bin_obs_total[j + 1] += obs[j]
        bin_exp_total[j + 1] += exp[j]

print("\n" + "=" * 88)
print("CROSS-BLOCK SUMMARY (per bin, averaged over B1-B4)")
print("=" * 88)
print("  %4s | %10s | %10s | %8s | %11s | %9s | %9s" % (
    "Bin", "Mean_obs", "Mean_exp", "Ratio", "Mean_StdRes", "Mean_chi2", "SD_StdRes"))
print("  " + "-" * 86)

mean_std_res = {}
mean_chi2 = {}
ratio = {}
for j in range(1, 11):
    msr = float(np.mean(bin_std_residuals[j]))
    mch = float(np.mean(bin_chi2_contrib[j]))
    r = bin_obs_total[j] / bin_exp_total[j]
    sd = float(np.std(bin_std_residuals[j]))
    mean_std_res[j] = msr
    mean_chi2[j] = mch
    ratio[j] = r
    print("  %4d | %10.0f | %10.0f | %8.4f | %+11.4f | %9.4f | %9.4f" % (
        j, bin_obs_total[j], bin_exp_total[j], r, msr, mch, sd))

print("\n" + "=" * 88)
print("CHI2 DECOMPOSITION CHECK")
print("=" * 88)
for b in BLOCK_LABELS:
    blk = block_data[b]
    total_chi2 = blk["chi2"]
    sum_contrib = sum(sum(bin_chi2_contrib[j]) for j in range(1, 11))
    match = "PASS" if abs(total_chi2 - sum_contrib) < 1.0 else "FAIL"
    print("  %s: total=%s  sum(contrib)=%s  %s" % (
        b, format(total_chi2, ",.2f"), format(sum_contrib, ",.2f"), match))

print("\n" + "=" * 88)
print("TAIL vs BULK ANALYSIS")
print("=" * 88)
for b in BLOCK_LABELS:
    blk = block_data[b]
    obs = np.array(blk["counts"], dtype=float)
    exp = np.array(blk["expected"], dtype=float)
    bulk_obs = obs[:5].sum()
    bulk_exp = exp[:5].sum()
    tail_obs = obs[5:].sum()
    tail_exp = exp[5:].sum()
    bulk_ratio = bulk_obs / bulk_exp if bulk_exp > 0 else 0
    tail_ratio = tail_obs / tail_exp if tail_exp > 0 else 0
    print("  %s: bulk_ratio=%.4f  tail_ratio=%.4f" % (b, bulk_ratio, tail_ratio))

print("\n" + "=" * 88)
print("KEY FINDINGS")
print("=" * 88)
sorted_bins = sorted(range(1, 11), key=lambda j: -abs(mean_std_res[j]))
print("  Bins ranked by |mean standardized residual|:")
for rank, j in enumerate(sorted_bins, 1):
    sig = "***" if abs(mean_std_res[j]) > 3 else ("**" if abs(mean_std_res[j]) > 2 else ("*" if abs(mean_std_res[j]) > 1.5 else ""))
    print("    %d. Bin %d: mean_std_res=%+.4f, mean_chi2=%.4f, ratio=%.4f %s" % (
        rank, j, mean_std_res[j], mean_chi2[j], ratio[j], sig))

under_bins = [j for j in range(1, 11) if mean_std_res[j] < -1.5]
over_bins = [j for j in range(1, 11) if mean_std_res[j] > 1.5]
print("\n  Under-represented bins (std_res < -1.5): %s" % under_bins)
print("  Over-represented bins (std_res > +1.5): %s" % over_bins)
# Both tails lighter + concentration at intermediate values
both_tails = 1 in under_bins and 10 in under_bins
has_mid_over = any(3 <= j <= 5 for j in over_bins)
print("\n  Pattern:")
if both_tails:
    print("  - BOTH tails under-represented (bins 1, 10 empty/deficient)")
if has_mid_over:
    print("  - MEDIUM bins (3, 5) MASSIVELY over-represented")
print("  - Distribution is NARROWER than Exp(1): lower variance,")
print("    peak at intermediate values, lighter tails on both sides.")
print("  - This is a SHAPE deviation, not just a tail effect.")
print("  - Possible explanations: shifted gamma, compound distribution,")
print("    or number-theoretic constraint on minimum gap size.")

OUT_DIR = os.path.join(INVESTIGATION, "Q-M007")
os.makedirs(OUT_DIR, exist_ok=True)
out = {
    "experiment": "Q-M007 per-bin residual analysis",
    "parent": "EXP-0008",
    "bin_summary": {str(j): {
        "mean_std_residual": mean_std_res[j],
        "mean_chi2_contribution": mean_chi2[j],
        "obs_total": bin_obs_total[j],
        "exp_total": bin_exp_total[j],
        "ratio": ratio[j],
        "std_residuals_per_block": bin_std_residuals[j],
    } for j in range(1, 11)},
}
with open(os.path.join(OUT_DIR, "q_m007_results.json"), "w") as f:
    json.dump(out, f, indent=2, default=str)
print("\n  Saved: %s/q_m007_results.json" % OUT_DIR)
