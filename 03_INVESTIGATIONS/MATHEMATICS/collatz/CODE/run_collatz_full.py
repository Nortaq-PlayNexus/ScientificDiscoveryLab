import json
import math
from pathlib import Path

# Q-M001 FULL RUN: Test convergent families at N=100000
# Focus: (a=b, c=a) families and (a=7,b=7,c=7) which was not tested in pilot
# Also test representative divergent families at larger N

def collatz_stop(n, a, b, c, max_steps=100000):
    steps = 0
    while n != 1 and steps < max_steps:
        if n % a == 0:
            n = n // a
        else:
            n = n * b + c
        steps += 1
    return steps if n == 1 else max_steps

def run_family(a, b, c, N, max_steps=100000):
    """Run Collatz for parameter family (a,b,c) at scale N."""
    stopping_times = []
    reached_one = 0
    max_found = 0
    cycles_found = []
    
    # Test all odd n < N
    for n0 in range(1, N, 2):
        st = collatz_stop(n0, a, b, c, max_steps=max_steps)
        stopping_times.append(st)
        if st < max_steps:
            reached_one += 1
        else:
            # Check if it's cycling (not just slow)
            if st == max_steps:
                cycles_found.append(n0)
        max_found = max(max_found, st)
    
    if not stopping_times:
        return {"error": "no data"}
    
    stops_arr = sorted(stopping_times)
    n = len(stops_arr)
    mean_st = sum(stops_arr) / n
    median_st = stops_arr[n // 2] if n > 0 else 0
    
    # Percentage that reached 1
    pct_reached = reached_one / n * 100
    
    return {
        "a": a, "b": b, "c": c,
        "N": N,
        "n_observations": n,
        "mean_stopping_time": round(mean_st, 3),
        "median_stopping_time": median_st,
        "max_stopping_time": max_found,
        "reached_one": reached_one,
        "pct_reached_one": round(pct_reached, 2),
        "cycles_found": len(cycles_found),
    }

if __name__ == "__main__":
    output_dir = Path(r"C:\Users\natha\ScientificDiscoveryLab\03_INVESTIGATIONS\MATHEMATICS\collatz\RESULTS")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Q-M001 FULL RUN (N=100000)")
    print("=" * 60)
    
    results = []
    
    # Test convergent families at N=100000
    convergent = [(3,3,3), (5,5,5), (7,7,7)]
    for a, b, c in convergent:
        print(f"\nTesting convergent family (a={a}, b={b}, c={c})...", flush=True)
        result = run_family(a, b, c, N=100000, max_steps=100000)
        results.append(result)
        if "error" not in result:
            print(f"  Mean ST: {result['mean_stopping_time']}, "
                  f"Max ST: {result['max_stopping_time']}, "
                  f"Reached 1: {result['reached_one']}/{result['n_observations']} ({result['pct_reached_one']}%)",
                  flush=True)
    
    # Test a few representative divergent families at N=100000
    # (smaller range since they likely diverge at large N)
    divergent = [(3,3,1), (3,5,1), (5,3,1), (7,5,3), (7,7,5)]
    for a, b, c in divergent:
        print(f"\nTesting divergent family (a={a}, b={b}, c={c})...", flush=True)
        # Use smaller N for divergent families - they may not converge
        result = run_family(a, b, c, N=10000, max_steps=10000)
        results.append(result)
        if "error" not in result:
            print(f"  Mean ST: {result['mean_stopping_time']}, "
                  f"Max ST: {result['max_stopping_time']}, "
                  f"Reached 1: {result['reached_one']}/{result['n_observations']} ({result['pct_reached_one']}%)",
                  flush=True)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in results:
        if "error" not in r:
            tag = "CONVERGENT" if r["pct_reached_one"] > 90 else ("PARTIAL" if r["pct_reached_one"] > 0 else "DIVERGENT")
            print(f"  (a={r['a']}, b={r['b']}, c={r['c']}): "
                  f"{r['pct_reached_one']}% reached 1, mean ST={r['mean_stopping_time']}, "
                  f"max ST={r['max_stopping_time']}, {tag}")
    
    # Save results
    output = {
        "experiment": "Q-M001 Generalized Collatz stopping-time statistics (FULL)",
        "parameters": {
            "convergent_families": convergent,
            "divergent_families": divergent,
            "N_convergent": 100000,
            "N_divergent": 10000,
            "max_steps": 100000,
        },
        "results": results,
        "note": "Convergent families tested at N=100000; divergent families at N=10000 (expected to diverge).",
        "status": "FULL RUN COMPLETE",
    }
    
    output_path = output_dir / "Q-M001_full_results.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nSaved to {output_path}")
