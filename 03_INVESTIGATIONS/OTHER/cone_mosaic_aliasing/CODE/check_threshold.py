import json

# Check Q-S9-1 raw data for threshold discrepancy
with open(r"C:\Users\natha\ScientificDiscoveryLab\CODE\dmt-laser-s9-battery\q_s9_1_results.json") as f:
    d = json.load(f)

print("=== Q-S9-1 Raw Data Summary ===")
print(f"Baseline rate: {d.get('baseline_rate', 'N/A')}")

# Threshold analysis
ta = d.get('threshold_analysis', {})
print(f"Threshold analysis:")
for k, v in ta.items():
    print(f"  {k}: {v}")

# Complexity levels
cl = d.get('complexity_levels', [])
print(f"\nComplexity levels ({len(cl)}):")
for item in cl:
    name = item.get('name', '?')
    comp = item.get('complexity', '?')
    code_rate = item.get('code_rate', '?')
    detection = item.get('detection_rate', item.get('detection', 'N/A'))
    print(f"  {name}: complexity={comp}, code_rate={code_rate}, detection={detection}")

# Key finding
print("\n=== Key Finding ===")
threshold = ta.get('threshold_complexity', 'N/A')
print(f"Computed threshold complexity: {threshold}")
print(f"ACTIVE_PROJECT.md claims: 0.10")
print(f"Discrepancy: {'CONFIRMED - actual is lower than documented' if isinstance(threshold, (int, float)) and threshold < 0.10 else 'CHECK'}")
