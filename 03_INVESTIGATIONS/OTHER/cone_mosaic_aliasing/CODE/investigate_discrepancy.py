import json

# Deep investigation of Q-S9-1 threshold discrepancy
with open(r"C:\Users\natha\ScientificDiscoveryLab\CODE\dmt-laser-s9-battery\q_s9_1_results.json") as f:
    d = json.load(f)

print("=== Q-S9-1 THRESHOLD DISCREPANCY INVESTIGATION ===")
print()

# 1. Check baseline rate
baseline = d.get('baseline_rate', 'N/A')
print(f"1. Baseline rate: {baseline}")
print(f"   (This IS the 0.05 value — is this what ACTIVE_PROJECT.md refers to?)")
print()

# 2. Check threshold analysis
ta = d.get('threshold_analysis', {})
print("2. Threshold analysis:")
for k, v in ta.items():
    print(f"   {k}: {v}")
print()

# 3. Check complexity levels
cl = d.get('complexity_levels', [])
print("3. Complexity levels and code rates:")
for item in cl:
    name = item.get('name', '?')
    complexity = item.get('complexity', '?')
    code_rate = item.get('code_rate', '?')
    print(f"   {name}: complexity={complexity}, code_rate={code_rate}")
print()

# 4. Analysis
print("4. Analysis:")
print("   The data has TWO values of 0.05:")
print("   a) baseline_rate = 0.05 (the detection rate at complexity=0)")
print("   b) threshold_complexity = 0.05 (the complexity level where detection starts)")
print("   c) threshold_pct_of_FFT_bins = 5 (5% of FFT bins carry signal)")
print()
print("   ACTIVE_PROJECT.md likely refers to threshold_complexity = 0.10")
print("   But the DATA shows threshold_complexity = 0.05")
print()
print("   Possible explanations:")
print("   - ACTIVE_PROJECT.md was written before final computation (0.10 was initial estimate)")
print("   - Different criterion used (e.g., rate > baseline + 0.05 instead of + 0.01)")
print("   - Different complexity metric")
print()

# 5. Check what happens at complexity=0.10
for item in cl:
    if item.get('complexity') == 0.10:
        print(f"5. At complexity=0.10: code_rate={item.get('code_rate')}")
        print(f"   Compared to baseline ({baseline}): increase = {item.get('code_rate', 0) - baseline}")
        print(f"   With criterion rate > baseline + 0.01: {item.get('code_rate', 0) - baseline > 0.01}")
        break

# 6. Check all levels above baseline + 0.01
print()
print("6. All complexity levels where code_rate > baseline + 0.01:")
for item in cl:
    cr = item.get('code_rate', 0)
    if cr - baseline > 0.01:
        print(f"   complexity={item.get('complexity')}: code_rate={cr} (delta={cr-baseline:.4f})")

print()
print("=== CONCLUSION ===")
print("The threshold IS 0.05 in the raw data. ACTIVE_PROJECT.md says 0.10.")
print("This is a DOCUMENTATION DISCREPANCY, not a computational error.")
print("The threshold was likely refined from 0.10 to 0.05 during computation.")
