"""Q-M008: Prime gap scaling test at 10^10 (segmented sieve).

Uses segmented sieve to avoid memory allocation of ~10GB.
Sieves in segments of 10^8, accumulates gap statistics.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

def segmented_sieve_gaps(limit, segment_size=10**8):
    """Compute gaps using segmented sieve. Returns array of normalized gaps."""
    all_gaps = []
    
    # First, sieve [0, segment_size) to get primes up to segment_size
    # Then for each subsequent segment, sieve and connect to previous prime
    
    print(f"  Segmented sieve to {limit:,} (segments of {segment_size:,})...", flush=True)
    
    t0 = time.time()
    
    # Stage 1: Sieve first segment
    is_prime = np.ones(segment_size, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.isqrt(segment_size)) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    
    primes_in_segment = np.nonzero(is_prime)[0]
    prev_prime = int(primes_in_segment[-1]) if len(primes_in_segment) > 0 else None
    
    total_primes = len(primes_in_segment)
    
    # Stage 2: Subsequent segments
    low = segment_size
    while low < limit:
        high = min(low + segment_size, limit)
        seg_len = high - low
        
        is_prime_seg = np.ones(seg_len, dtype=bool)
        is_prime_seg[0] = is_prime_seg[1] = False if seg_len > 1 else True
        
        sqrt_high = int(math.isqrt(high))
        for i in range(2, sqrt_high + 1):
            if i < segment_size:
                if not is_prime[i]:
                    continue
            else:
                # Need to check if i is prime (from previous segments)
                # For simplicity, assume small i are already sieved
                pass
            
            # Mark multiples of i in [low, high)
            start = ((low + i - 1) // i) * i
            if start == i:
                start += i
            is_prime_seg[start - low::i] = False
        
        primes_in_seg = np.nonzero(is_prime_seg)[0] + low
        
        # Connect to previous prime
        if prev_prime is not None and len(primes_in_seg) > 0:
            gap = int(primes_in_seg[0]) - prev_prime
            log_p = math.log(int(primes_in_seg[0]))
            all_gaps.append(gap / log_p)
        
        all_gaps.extend((primes_in_seg[1:] - primes_in_seg[:-1]) / np.log(primes_in_seg[1:].astype(np.float64)))
        
        total_primes += len(primes_in_seg)
        if len(primes_in_seg) > 0:
            prev_prime = int(primes_in_seg[-1])
        
        low = high
        
        if int(low / segment_size) % 2 == 0:
            print(f"    Sievered {low:,}/{limit:,} ({100*low/limit:.0f}%)", flush=True)
    
    print(f"  Sieve complete: {total_primes:,} primes in {time.time()-t0:.1f}s", flush=True)
    
    return np.array(all_gaps, dtype=np.float64), total_primes

def chi2_goF(gaps, J=10):
    if len(gaps) == 0:
        return None
    edges = [-math.log(1 - j/J) for j in range(1, J)]
    edges = [0.0] + edges + [float('inf')]
    observed, _ = np.histogram(gaps, bins=edges)
    expected = len(gaps) / J
    chi2 = np.sum((observed - expected)**2 / expected)
    dof = J - 1
    p_value = 1 - sp_stats.chi2.cdf(chi2, dof)
    return {"chi2": float(chi2), "dof": dof, "p_value": float(p_value)}

def main():
    print("=" * 60, flush=True)
    print("Q-M008: Prime Gap Scaling Test at 10^10 (segmented sieve)", flush=True)
    print("=" * 60, flush=True)
    
    t0 = time.time()
    
    print("\nComputing gaps at 10^10...", flush=True)
    gaps, n_primes = segmented_sieve_gaps(10**10, segment_size=10**8)
    
    print(f"\nTotal primes: {n_primes:,}", flush=True)
    print(f"Total gaps: {len(gaps):,}", flush=True)
    
    # Analysis
    print("\nRunning analysis...", flush=True)
    t1 = time.time()
    
    chi2 = chi2_goF(gaps)
    ks_stat, ks_p = sp_stats.kstest(gaps, 'expon')
    
    print(f"  Overall chi2: {chi2['chi2']:.1f} (dof={chi2['dof']}, p={chi2['p_value']:.2e})", flush=True)
    print(f"  Overall KS: {ks_stat:.4f} (p={ks_p:.2e})", flush=True)
    
    print(f"  Analysis complete in {time.time()-t1:.1f}s", flush=True)
    print(f"  Total time: {time.time()-t0:.1f}s", flush=True)
    
    # Save
    output_dir = Path(r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/RESULTS")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    result = {
        "limit": 10**10,
        "n_primes": n_primes,
        "n_gaps": len(gaps),
        "method": "segmented sieve (segments of 10^8)",
        "total_time": time.time() - t0,
        "overall": {
            "chi2": chi2,
            "ks": {"ks_stat": float(ks_stat), "p_value": float(ks_p)},
        },
        "note": "10^10 run uses segmented sieve due to memory constraints. Gap statistics are approximate due to segment boundaries.",
    }
    
    with open(output_dir / "Q-M008_1e10_results.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"\nSaved to {output_dir / 'Q-M008_1e10_results.json'}", flush=True)
    print("\nQ-M008 10^10 complete.", flush=True)

if __name__ == "__main__":
    main()
