"""Q-M008: Prime gap test at 10^10 (segmented sieve).

Sieves [2, 10^10) in segments of 10^8.
Memory: O(sqrt(N)) for base sieve + O(segment_size) per segment.
"""
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats as sp_stats

def base_sieve(limit):
    """Standard sieve for primes up to limit."""
    if limit < 2:
        return np.array([], dtype=np.int64)
    is_prime = np.ones(limit + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return np.nonzero(is_prime)[0].astype(np.int64)

def segmented_gap_stats(limit, segment_size=10**8):
    """Compute gap statistics using segmented sieve."""
    print(f"  Building base sieve up to sqrt({limit:,})...", flush=True)
    base_primes = base_sieve(int(math.isqrt(limit)) + 1)
    print(f"  Base sieve: {len(base_primes):,} primes up to {len(base_primes):,}", flush=True)
    
    gaps = []
    total_primes = 0
    prev_prime = None
    
    n_segments = (limit + segment_size - 1) // segment_size
    
    for seg_idx in range(n_segments):
        low = seg_idx * segment_size
        high = min(low + segment_size, limit)
        
        if low % (10**9) == 0 or seg_idx == 0:
            print(f"    Segment {seg_idx+1}/{n_segments}: [{low:,}, {high:,})", flush=True)
        
        # Sieve [low, high)
        seg_len = high - low
        is_prime_seg = np.ones(seg_len, dtype=bool)
        
        if seg_len > 0:
            is_prime_seg[0] = False
        if seg_len > 1:
            is_prime_seg[1] = False
        
        for p in base_primes:
            if p * p > high:
                break
            # Find first multiple of p >= low
            start = ((low + p - 1) // p) * p
            if start == p:
                start += p  # p itself is prime, don't mark it
            if start < low:
                start += p
            is_prime_seg[start - low::p] = False
        
        primes_in_seg = np.nonzero(is_prime_seg)[0] + low
        
        # Connect to previous segment
        if prev_prime is not None and len(primes_in_seg) > 0:
            gap = int(primes_in_seg[0]) - prev_prime
            log_p = math.log(int(primes_in_seg[0]))
            if log_p > 0:
                gaps.append(gap / log_p)
        
        # Compute gaps within segment
        if len(primes_in_seg) > 1:
            deltas = (primes_in_seg[1:] - primes_in_seg[:-1]).astype(np.float64)
            log_p = np.log(primes_in_seg[1:].astype(np.float64))
            seg_gaps = deltas / log_p
            gaps.extend(seg_gaps.tolist())
        
        total_primes += len(primes_in_seg)
        if len(primes_in_seg) > 0:
            prev_prime = int(primes_in_seg[-1])
    
    print(f"  Total primes: {total_primes:,}", flush=True)
    return np.array(gaps, dtype=np.float64), total_primes

def main():
    print("=" * 60, flush=True)
    print("Q-M008: Prime Gap Test at 10^10 (segmented sieve)", flush=True)
    print("=" * 60, flush=True)
    
    t0 = time.time()
    
    limit = 10**10
    
    try:
        gaps, n_primes = segmented_gap_stats(limit, segment_size=10**8)
        
        print(f"\nRunning analysis...", flush=True)
        t1 = time.time()
        
        # Chi-square GOF
        J = 10
        edges = [-math.log(1 - j/J) for j in range(1, J)]
        edges = [0.0] + edges + [float('inf')]
        observed, _ = np.histogram(gaps, bins=edges)
        expected = len(gaps) / J
        chi2 = float(np.sum((observed - expected)**2 / expected))
        dof = J - 1
        chi2_p = float(1 - sp_stats.chi2.cdf(chi2, dof))
        
        # KS test
        ks_stat, ks_p = sp_stats.kstest(gaps, 'expon')
        
        print(f"  N primes: {n_primes:,}", flush=True)
        print(f"  N gaps: {len(gaps):,}", flush=True)
        print(f"  Overall chi2: {chi2:.1f} (dof={dof}, p={chi2_p:.2e})", flush=True)
        print(f"  Overall KS: {ks_stat:.4f} (p={ks_p:.2e})", flush=True)
        print(f"  Analysis time: {time.time()-t1:.1f}s", flush=True)
        print(f"  Total time: {time.time()-t0:.1f}s", flush=True)
        
        # Save
        output_dir = Path(r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/RESULTS")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        result = {
            "limit": limit,
            "n_primes": n_primes,
            "n_gaps": len(gaps),
            "method": "segmented sieve (segments of 10^8)",
            "total_time": time.time() - t0,
            "overall": {
                "chi2": {"chi2": chi2, "dof": dof, "p_value": chi2_p},
                "ks": {"ks_stat": float(ks_stat), "p_value": float(ks_p)},
            },
            "status": "COMPLETE",
            "note": "10^10 run. Deviation expected to persist based on 10^8->10^9 trend.",
        }
        
        with open(output_dir / "Q-M008_1e10_results.json", "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"Saved: {output_dir / 'Q-M008_1e10_results.json'}", flush=True)
        print("Q-M008 10^10 complete.", flush=True)
        
    except MemoryError:
        print("MEMORY ERROR: Cannot complete 10^10 run", flush=True)
        # Save partial results
        output_dir = Path(r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/RESULTS")
        output_dir.mkdir(parents=True, exist_ok=True)
        result = {"limit": limit, "status": "MEMORY_ERROR", "note": "Segmented sieve ran out of memory"}
        with open(output_dir / "Q-M008_1e10_results.json", "w") as f:
            json.dump(result, f, indent=2)
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        output_dir = Path(r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS/MATHEMATICS/prime_gaps/Q-M008/RESULTS")
        output_dir.mkdir(parents=True, exist_ok=True)
        result = {"limit": limit, "status": "ERROR", "error": str(e)}
        with open(output_dir / "Q-M008_1e10_results.json", "w") as f:
            json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
