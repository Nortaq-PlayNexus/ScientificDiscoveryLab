"""Q-M008 runner — Prime gap scaling test (10^8 verification + 10^9 main).

Extends EXP-0008 analysis to larger scales. Uses same methodology:
- Gap definition: delta = (p_{i+1} - p_i) / ln(p_i)
- 10 exponential-quantile bins: -ln(1 - j/10) for j=1..9
- 4 blocks matching EXP-0008 structure
- chi2 GOF vs Exp(1), KS test, BH-FDR correction
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

# Add shared engine path
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "04_SHARED_ENGINE"
))

HERE = os.path.dirname(os.path.abspath(__file__))
INVESTIGATION = os.path.dirname(HERE)
RESULTS_DIR = os.path.join(INVESTIGATION, "RESULTS")
PRIMES_DIR = os.path.join(INVESTIGATION, "DATA")

def sieve_primes_numpy(limit):
    """Numpy sieve of Eratosthenes, returns array of primes."""
    if limit < 2:
        return np.array([], dtype=np.int64)
    is_prime = np.ones(limit + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return np.nonzero(is_prime)[0].astype(np.int64)

def compute_gaps(primes):
    """Compute normalized gaps."""
    if len(primes) < 2:
        return np.array([], dtype=np.float64)
    deltas = (primes[1:] - primes[:-1]).astype(np.float64)
    log_p = np.log(primes[1:].astype(np.float64))
    return deltas / log_p

def chi2_goF(gaps, J=10):
    """Chi-square GOF vs Exp(1) with J bins."""
    if len(gaps) == 0:
        return None
    # Exponential-quantile bin edges: -ln(1 - j/J) for j=1..J-1
    edges = [-math.log(1 - j/J) for j in range(1, J)]
    edges = [0.0] + edges + [float('inf')]
    observed, _ = np.histogram(gaps, bins=edges)
    expected = len(gaps) / J
    chi2 = np.sum((observed - expected)**2 / expected)
    dof = J - 1
    p_value = 1 - sp_stats.chi2.cdf(chi2, dof)
    return {
        "chi2": float(chi2),
        "dof": dof,
        "p_value": float(p_value),
        "observed": observed.tolist(),
        "expected": [expected] * J,
    }

def ks_test(gaps):
    """KS test vs Exp(1)."""
    if len(gaps) == 0:
        return None
    stat, p_value = sp_stats.kstest(gaps, 'expon')
    return {"ks_stat": float(stat), "p_value": float(p_value)}

def tail_test(gaps, t_values=[1, 2, 3, 4, 5]):
    """Survival P(delta > t) vs exp(-t)."""
    if len(gaps) == 0:
        return None
    results = {}
    for t in t_values:
        n_above = np.sum(gaps > t)
        n_total = len(gaps)
        observed_rate = n_above / n_total
        expected_rate = math.exp(-t)
        # z-test for proportion
        se = math.sqrt(expected_rate * (1 - expected_rate) / n_total)
        z = (observed_rate - expected_rate) / se if se > 0 else 0
        p_value = 2 * (1 - sp_stats.norm.cdf(abs(z)))
        results[str(t)] = {
            "observed_rate": float(observed_rate),
            "expected_rate": expected_rate,
            "z": float(z),
            "p_value": float(p_value),
        }
    return results

def bh_fdr(p_values, alpha=0.01):
    """Benjamini-Hochberg FDR correction."""
    n = len(p_values)
    if n == 0:
        return []
    sorted_idx = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_idx]
    critical = np.arange(1, n+1) / n * alpha
    significant = sorted_p <= critical
    # Map back to original indices
    results = [False] * n
    for i, idx in enumerate(sorted_idx):
        results[idx] = bool(significant[i])
    return results

def run_analysis(limit, blocks=None):
    """Run full Q-M008 analysis at a given scale."""
    t0 = time.time()
    
    if blocks is None:
        # Match EXP-0008 block structure, scaled
        blocks = [
            {"label": f"B1", "lo": limit // 100, "hi": limit // 10},
            {"label": f"B2", "lo": limit // 10, "hi": limit // 2},
            {"label": f"B3", "lo": limit // 2, "hi": limit // 1.25},
            {"label": f"B4", "lo": int(limit // 1.25), "hi": limit},
        ]
    
    print(f"  Sieving to {limit:,}...", flush=True)
    primes = sieve_primes_numpy(limit)
    print(f"  Found {len(primes):,} primes in {time.time()-t0:.1f}s", flush=True)
    
    gaps = compute_gaps(primes)
    print(f"  Computed {len(gaps):,} gaps", flush=True)
    
    t1 = time.time()
    
    # Overall statistics
    overall_chi2 = chi2_goF(gaps)
    overall_ks = ks_test(gaps)
    overall_tail = tail_test(gaps)
    
    # Per-block statistics
    block_results = []
    all_p_values = []
    all_labels = []
    
    for b in blocks:
        # Find indices of primes in [lo, hi)
        mask = (primes >= b["lo"]) & (primes < b["hi"])
        block_primes = primes[mask]
        if len(block_primes) < 2:
            block_results.append({"label": b["label"], "error": "too few primes"})
            continue
        block_gaps = compute_gaps(block_primes)
        
        chi2 = chi2_goF(block_gaps)
        ks = ks_test(block_gaps)
        tail = tail_test(block_gaps)
        
        # Use chi2 p-value for BH-FDR
        p = chi2["p_value"] if chi2 else 1.0
        all_p_values.append(p)
        all_labels.append(b["label"])
        
        block_results.append({
            "label": b["label"],
            "n_primes": len(block_primes),
            "n_gaps": len(block_gaps),
            "chi2": chi2,
            "ks": ks,
            "tail": tail,
        })
    
    # BH-FDR correction across blocks
    fdr_significant = bh_fdr(all_p_values, alpha=0.01)
    
    print(f"  Analysis complete in {time.time()-t1:.1f}s", flush=True)
    
    return {
        "limit": limit,
        "n_primes": len(primes),
        "n_gaps": len(gaps),
        "sieve_time": time.time() - t0,
        "analysis_time": time.time() - t1,
        "total_time": time.time() - t0,
        "overall": {
            "chi2": overall_chi2,
            "ks": overall_ks,
            "tail": overall_tail,
        },
        "blocks": block_results,
        "bh_fdr": {
            "alpha": 0.01,
            "p_values": dict(zip(all_labels, all_p_values)),
            "significant": dict(zip(all_labels, fdr_significant)),
        },
    }

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    print("=" * 60, flush=True)
    print("Q-M008: Prime Gap Scaling Test", flush=True)
    print("=" * 60, flush=True)
    
    results = {}
    
    # === 10^8 VERIFICATION ===
    print("\n[1/2] Scale: 10^8 (verification vs EXP-0008)", flush=True)
    r_1e8 = run_analysis(10**8)
    results["1e8"] = r_1e8
    
    # Save immediately
    save_path = os.path.join(RESULTS_DIR, "Q-M008_1e8_results.json")
    with open(save_path, "w") as f:
        json.dump(r_1e8, f, indent=2, default=str)
    print(f"  Saved: {save_path}", flush=True)
    
    # Summary
    chi2_vals = []
    for b in r_1e8["blocks"]:
        if "chi2" in b:
            chi2_vals.append(b["chi2"]["p_value"])
    sig = sum(1 for v in chi2_vals if v < 0.01)
    print(f"  Blocks with p<0.01: {sig}/{len(chi2_vals)}", flush=True)
    
    # === 10^9 MAIN TEST ===
    print("\n[2/2] Scale: 10^9 (main test)", flush=True)
    print("  Estimated time: 2-5 minutes...", flush=True)
    
    try:
        r_1e9 = run_analysis(10**9)
        results["1e9"] = r_1e9
        
        save_path = os.path.join(RESULTS_DIR, "Q-M008_1e9_results.json")
        with open(save_path, "w") as f:
            json.dump(r_1e9, f, indent=2, default=str)
        print(f"  Saved: {save_path}", flush=True)
        
        # Summary
        chi2_vals = []
        for b in r_1e9["blocks"]:
            if "chi2" in b:
                chi2_vals.append(b["chi2"]["p_value"])
        sig = sum(1 for v in chi2_vals if v < 0.01)
        print(f"  Blocks with p<0.01: {sig}/{len(chi2_vals)}", flush=True)
        
    except MemoryError:
        print("  MEMORY ERROR: Cannot allocate sieve for 10^9", flush=True)
        results["1e9"] = {"error": "MemoryError"}
    except Exception as e:
        print(f"  ERROR: {e}", flush=True)
        results["1e9"] = {"error": str(e)}
    
    # === COMPARISON ===
    print("\n" + "=" * 60, flush=True)
    print("COMPARISON: 10^8 vs 10^9", flush=True)
    print("=" * 60, flush=True)
    
    if "1e8" in results and "1e9" in results and "error" not in results.get("1e9", {}):
        for scale1, scale2 in [("1e8", "1e9")]:
            r1 = results[scale1]
            r2 = results[scale2]
            print(f"\n  {scale1}: {r1['n_primes']:,} primes, {r1['n_gaps']:,} gaps", flush=True)
            print(f"  {scale2}: {r2['n_primes']:,} primes, {r2['n_gaps']:,} gaps", flush=True)
            
            if "chi2" in r1.get("overall", {}) and "chi2" in r2.get("overall", {}):
                c1 = r1["overall"]["chi2"]["chi2"]
                c2 = r2["overall"]["chi2"]["chi2"]
                p1 = r1["overall"]["chi2"]["p_value"]
                p2 = r2["overall"]["chi2"]["p_value"]
                print(f"  Overall chi2: {c1:.1f} (p={p1:.2e}) -> {c2:.1f} (p={p2:.2e})", flush=True)
            
            for b1, b2 in zip(r1["blocks"], r2["blocks"]):
                if "chi2" in b1 and "chi2" in b2:
                    print(f"  {b1['label']}: chi2 p={b1['chi2']['p_value']:.2e} -> {b2['chi2']['p_value']:.2e}", flush=True)
    
    # Save combined results
    combined_path = os.path.join(RESULTS_DIR, "Q-M008_combined.json")
    with open(combined_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved combined: {combined_path}", flush=True)
    
    print("\nQ-M008 complete.", flush=True)

if __name__ == "__main__":
    main()
