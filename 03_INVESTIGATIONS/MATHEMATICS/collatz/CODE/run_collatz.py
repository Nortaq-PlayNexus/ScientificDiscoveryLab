import json
import math
from pathlib import Path

# Q-M001: Generalized Collatz stopping-time statistics (PILOT)
# Pilot: reduced N and n_real for quick execution
# Full run: N=100000, n_real=100 (estimated: CPU-minutes per family)

def collatz_stop(n, a, b, c, max_steps=1000):
    steps = 0
    while n != 1 and steps < max_steps:
        if n % a == 0:
            n = n // a
        else:
            n = n * b + c
        steps += 1
    return steps if n == 1 else max_steps  # max_steps = "didn't reach 1"

def run_family(a, b, c, N, n_real):
    """Run Collatz for parameter family (a,b,c)."""
    rng_state = 42  # deterministic
    stopping_times = []
    cycles_found = []
    
    for run in range(n_real):
        rng_state = (rng_state * 1103515245 + 12345) % (2**31)
        start = rng_state % (N // 2) * 2 + 1  # odd starting points
        
        for n0 in range(start, start + 500, 2):  # 250 odd numbers per run
            if n0 >= N:
                break
            st = collatz_stop(n0, a, b, c)
            stopping_times.append(st)
            if st >= 999:  # near max_steps
                cycles_found.append(n0)
    
    if not stopping_times:
        return {"error": "no data"}
    
    stops_arr = sorted(stopping_times)
    n = len(stops_arr)
    mean_st = sum(stops_arr) / n
    median_st = stops_arr[n // 2] if n > 0 else 0
    
    # Stopping time distribution (binned)
    bins = {}
    for st in stopping_times:
        bin_key = min(st // 10 * 10, 1000)
        bins[bin_key] = bins.get(bin_key, 0) + 1
    
    unique_cycles = list(set(cycles_found))
    
    return {
        "a": a, "b": b, "c": c,
        "n_observations": n,
        "mean_stopping_time": round(mean_st, 3),
        "median_stopping_time": median_st,
        "max_stopping_time": max(stops_arr),
        "stopping_time_distribution": dict(sorted(bins.items())),
        "cycles_found": len(unique_cycles),
        "cycle_examples": unique_cycles[:10],
    }

if __name__ == "__main__":
    output_dir = Path(r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\MATHEMATICS\collatz\RESULTS")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    a_vals = [3, 5, 7]
    b_vals = [3, 5, 7]
    c_vals = [1, 3, 5]
    
    print("Q-M001: Generalized Collatz stopping-time statistics (PILOT)")
    print(f"Parameters: a={a_vals}, b={b_vals}, c={c_vals}")
    print(f"N=1000, n_real=5 per family")
    print()
    
    for a in a_vals:
        for b in b_vals:
            for c in c_vals:
                print(f"  (a={a}, b={b}, c={c})...", end=" ")
                result = run_family(a, b, c, N=1000, n_real=5)
                results.append(result)
                print(f"mean ST={result.get('mean_stopping_time', 'N/A')}, "
                      f"max ST={result.get('max_stopping_time')}, "
                      f"cycles={result.get('cycles_found', 0)}")
    
    # Heuristic model comparison
    # For classic Collatz (a=3, b=3, c=1), expected mean ST ~ log2(N) * ln(2) â‰ˆ 6.93 for N=1000
    print()
    print("Heuristic model predictions (mean stopping time â‰ˆ log2(N) * log2(a/b)):")
    for a in a_vals:
        for b in b_vals:
            for c in c_vals:
                predicted = math.log(1000) * math.log(b/a) / math.log(2) if a != b else float('inf')
                actual_mean = [r for r in results if r.get('a') == a and r.get('b') == b and r.get('c') == c]
                if actual_mean and 'mean_stopping_time' in actual_mean[0]:
                    actual = actual_mean[0]['mean_stopping_time']
                    ratio = actual / predicted if predicted > 0 else float('inf')
                    dev = "PASS" if 0.1 < ratio < 10 else "CHECK"
                    print("  (a=%d, b=%d, c=%d): predicted=%.1f, actual=%.1f, ratio=%.2f [%s]" % (a,b,c,predicted,actual,ratio,dev))
    
    # Save results
    output = {
        "experiment": "Q-M001 Generalized Collatz stopping-time statistics",
        "parameters": {
            "a_values": a_vals, "b_values": b_vals, "c_values": c_vals,
            "N": 1000, "n_real": 5, "pilot": True,
            "full_run_plan": "N=100000, n_real=100 (CPU-minutes per family)",
        },
        "results": results,
        "key_finding": "Pilot run complete. Deviations from heuristic model will be assessed at full scale.",
        "status": "PILOT COMPLETE â€” full run pending compute resources",
    }
    
    output_path = output_dir / "Q-M001_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved to {output_path}")
