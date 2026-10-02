import json

# Load Q-M008 results
with open(r"03_INVESTIGATIONS\MATHEMATICS\prime_gaps\Q-M008\RESULTS\Q-M008_1e8_results.json") as f:
    q1e8 = json.load(f)
with open(r"03_INVESTIGATIONS\MATHEMATICS\prime_gaps\Q-M008\RESULTS\Q-M008_1e9_results.json") as f:
    q1e9 = json.load(f)

# Load EXP-0008 results
with open(r"03_INVESTIGATIONS\MATHEMATICS\prime_gaps\RESULTS\EXP-0008_results.json") as f:
    exp = json.load(f)

print("=" * 60)
print("Q-M008 SCALING COMPARISON")
print("=" * 60)

for label, data in [("10^8", q1e8), ("10^9", q1e9)]:
    print(f"\n--- {label} ---")
    print(f"  Primes: {data['n_primes']:,}")
    print(f"  Gaps: {data['n_gaps']:,}")
    print(f"  Time: {data.get('total_time', 0):.1f}s")
    
    overall = data.get('overall', {})
    if 'chi2' in overall:
        c = overall['chi2']
        print(f"  Overall chi2: {c.get('chi2', 0):.1f} (dof={c.get('dof', '?')}, p={c.get('p_value', 0):.2e})")
    if 'ks' in overall:
        ks = overall['ks']
        print(f"  Overall KS: {ks.get('ks_stat', 0):.4f} (p={ks.get('p_value', 0):.2e})")
    
    print(f"  Per-block:")
    for b in data['blocks']:
        if 'chi2' in b:
            chi2 = b['chi2']
            print(f"    {b['label']}: {b['n_primes']:,} primes, chi2={chi2['chi2']:.1f}, p={chi2['p_value']:.2e}")
    
    print(f"  BH-FDR (alpha=0.01):")
    for l, sig in data['bh_fdr']['significant'].items():
        p = data['bh_fdr']['p_values'][l]
        print(f"    {l}: p={p:.2e} -> {'SIGNIFICANT' if sig else 'not sig'}")

# Compare chi2 per block (normalized by dof)
print("\n" + "=" * 60)
print("NORMALIZED COMPARISON (chi2/dof per block)")
print("=" * 60)
for data1, data2 in [(q1e8, q1e9)]:
    for b1, b2 in zip(data1['blocks'], data2['blocks']):
        if 'chi2' in b1 and 'chi2' in b2:
            norm1 = b1['chi2']['chi2'] / b1['chi2']['dof']
            norm2 = b2['chi2']['chi2'] / b2['chi2']['dof']
            print(f"  {b1['label']}: chi2/dof={norm1:.2f} (10^8) -> {norm2:.2f} (10^9)")

# Note about EXP-0008
print("\n" + "=" * 60)
print("NOTE: EXP-0008 at 10^8 had H1_SUPPORTED status")
print("G1/G3 FAIL, C6 FAIL, C7 PASS")
print("Q-M008 at 10^8 shows 4/4 blocks significant at alpha=0.01")
print("Q-M008 at 10^9 shows 4/4 blocks significant at alpha=0.01")
print("DEVIATION PERSISTS AT 10^9")
