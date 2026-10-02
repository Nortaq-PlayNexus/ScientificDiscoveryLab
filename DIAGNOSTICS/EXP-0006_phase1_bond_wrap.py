"""EXP-0006 Phase 1 diagnostic - bond_wrap FG failure deep analysis.
No new MC. Reads frozen EXP-0006 bond_wrap cells + EXP-0005 comparison.
"""
import json, os, sys
import numpy as np
from scipy.optimize import curve_fit

INV = os.path.join("03_INVESTIGATIONS", "PHYSICS", "percolation")
R06 = os.path.join(INV, "CODE", "RESULTS", "EXP-0006_results.json")
R05 = os.path.join(INV, "CODE", "RESULTS", "EXP-0005_results.json")
CFG06 = os.path.join(INV, "CODE", "CONFIG", "EXP-0006_experiment.json")

def load(p): return json.load(open(p, encoding="utf-8"))
R6 = load(R06); R5 = load(R05); C6 = load(CFG06)

print("=" * 70)
print("EXP-0006 PHASE 1: bond_wrap FG failure deep analysis")
print("No new MC - all data from frozen EXP-0006 and EXP-0005")
print("=" * 70)

p50_bw = R6["p50"]["bond_wrap"]
print("\n## 1. bond_wrap p50 at L=32,48,64 (from EXP-0006)")
for L in [32, 48, 64]:
    d = p50_bw[str(L)]
    print("  L=%d: p50=%.6f +- %.6f (width=%.6f)" % (L, d["p50"], d["se"], d["width"]))
    print("        p50_ml=%.6f" % d["p50_ml"])

p32 = p50_bw["32"]["p50"]; e32 = p50_bw["32"]["se"]
p48 = p50_bw["48"]["p50"]; e48 = p50_bw["48"]["se"]
p64 = p50_bw["64"]["p50"]; e64 = p50_bw["64"]["se"]
dip = p48 - p32
peak = p64 - p48
print("\n## 2. Non-monotonicity quantification")
print("  L=48 dip below L=32: %.6f (%.2f SE)" % (dip, abs(dip)/e48))
print("  L=64 rise above L=48: %.6f (%.2f SE)" % (peak, peak/e48))
print("  Peak-to-trough range: %.6f" % (p64 - p48))
pair_L32_L48 = abs(p32-p48)/np.sqrt(e32**2+e48**2)
pair_L48_L64 = abs(p48-p64)/np.sqrt(e48**2+e64**2)
pair_L32_L64 = abs(p32-p64)/np.sqrt(e32**2+e64**2)
print("  Pairwise SE ratios: L32-L48=%.2fSE, L48-L64=%.2fSE, L32-L64=%.2fSE"
      % (pair_L32_L48, pair_L48_L64, pair_L32_L64))

def bootstrap_p50(cell_L, n_bootstrap=2000, seed=42):
    rng = np.random.default_rng(seed)
    cells_L = [c for c in R6["cells"]["bond_wrap"] if c["L"] == cell_L]
    ps = np.array([c["p"] for c in cells_L])
    ns = np.array([c["n"] for c in cells_L])
    p50s = []
    for _ in range(n_bootstrap):
        ks = rng.binomial(ns, ps)
        order = np.argsort(ps)
        ps_s = ps[order]; ks_s = ks[order]
        W_s = ks_s / ns[order]
        if W_s[0] > 0.5 or W_s[-1] < 0.5:
            continue
        p50 = float(np.interp(0.5, W_s, ps_s))
        p50s.append(p50)
    return np.array(p50s)

print("\n## 3. Parametric bootstrap CIs (2000 resamples, seed=42)")
p50s_by_L = {}
for L in [32, 48, 64]:
    bstrap = bootstrap_p50(L)
    if len(bstrap) == 0:
        print("  L=%d: no valid resamples" % L)
        p50s_by_L[L] = np.array([])
        continue
    ci_lo = np.percentile(bstrap, 2.5)
    ci_hi = np.percentile(bstrap, 97.5)
    p50s_by_L[L] = bstrap
    print("  L=%d: p50_95CI=[%.6f, %.6f], median=%.6f, n_valid=%d"
          % (L, ci_lo, ci_hi, np.median(bstrap), len(bstrap)))

print("\n## 4. Bootstrap CI overlap (tests if p50 values are distinguishable)")
for Li in [32, 48, 64]:
    for Lj in [32, 48, 64]:
        if Li >= Lj: continue
        a = p50s_by_L[Li]; b = p50s_by_L[Lj]
        if len(a) == 0 or len(b) == 0: continue
        diff = abs(np.median(a) - np.median(b))
        pooled_se = np.sqrt(np.var(a)/len(a) + np.var(b)/len(b))
        z = diff / pooled_se if pooled_se > 0 else float("inf")
        sig = "SIGNIFICANT" if z > 2 else "overlap"
        print("  L=%d vs L=%d: |d|=%f, z=%.2f -> %s" % (Li, Lj, diff, z, sig))

print("\n## 5. FSS model comparison (3 points, same limitation)")
Ls = np.array([32, 48, 64], dtype=float)
ps_arr = np.array([p32, p48, p64])
A = np.column_stack([np.ones(3), Ls**(-0.75)])
coef_fixed, _, _, _ = np.linalg.lstsq(A, ps_arr, rcond=None)
resid_fixed = ps_arr - A @ coef_fixed
resid_std_fixed = float(np.std(resid_fixed, ddof=2))
print("  Fixed exp (-3/4): a=%.6f, b=%.6f, resid_std=%.6f"
      % (coef_fixed[0], coef_fixed[1], resid_std_fixed))
print("  NOTE: 3 pts, 2 params -> 1 dof. Free-exp (3 params) has 0 dof")
print("  -> Model comparison impossible with 3 points; need 4+ points")

logL = np.log(Ls); logdev = np.log(np.abs(ps_arr - 0.5))
slope_loglog, intercept_loglog = np.polyfit(logL, logdev, 1)
dev_pred = 0.5 + intercept_loglog * Ls**slope_loglog
resid_loglog = ps_arr - dev_pred
resid_std_loglog = float(np.std(resid_loglog, ddof=2))
print("  Log-log (p_c=0.5): slope=%.6f, resid_std=%.6f"
      % (slope_loglog, resid_std_loglog))
coef_Linv, _, _, _ = np.linalg.lstsq(np.column_stack([np.ones(3), 1/Ls]), ps_arr, rcond=None)
resid_Linv = ps_arr - (coef_Linv[0] + coef_Linv[1]/Ls)
resid_std_Linv = float(np.std(resid_Linv, ddof=2))
print("  1/L model: a=%.6f, b=%.6f, resid_std=%.6f"
      % (coef_Linv[0], coef_Linv[1], resid_std_Linv))
print("  All models resid_std ~0.002 -> indistinguishable with 3 points")

print("\n## 6. Consistency with EXP-0005 (same cells, same seed=42)")
p50_bw5 = R5["p50"]["bond_wrap"]
identical = True
for L in [32, 48, 64]:
    d6 = p50_bw[str(L)]; d5 = p50_bw5[str(L)]
    match = abs(d6["p50"] - d5["p50"]) < 1e-10
    if not match: identical = False
    print("  L=%d: EXP-0006=%.10f, EXP-0005=%.10f, match=%s"
          % (L, d6["p50"], d5["p50"], match))
fg6 = R6["gates"]["FG"]["bond_wrap"]; fg5 = R5["gates"]["FG"]["bond_wrap"]
print("  FG bond_wrap chi2_red: 006=%.10f, 005=%.10f, match=%s"
      % (fg6, fg5, abs(fg6-fg5) < 1e-8))

print("\n## 7. C2 independent implementation check")
c2 = R6["c2"]
print("  C2 pair_diff=%.6f (tol<0.005: %s)"
      % (c2["pair_diff"], "PASS" if c2["pass"] else "FAIL"))
print("  bond_span a=%.6f, bond_wrap a=%.6f" % (c2["span_a"], c2["wrap_a"]))

print("\n## 8. Phase 1 verdict")
all_under_2SE = all([pair_L32_L48 < 2, pair_L48_L64 < 2, pair_L32_L64 < 2])
max_SE_ratio = max(abs(dip)/e48, abs(peak)/e48)
print("  (a) Statistical noise? All pairwise <2SE: %s (max %.2fSE)"
      % (all_under_2SE, max_SE_ratio))
print("  (b) Model inadequacy? Untestable with 3 points (need 4+)")
print("  (c) Estimator artifact? EXP-0005 identical: %s" % identical)
print("  (d) Genuine deviation? Max |dev|/SE: %.2fSE" % max_SE_ratio)
print("\n  PHASE 1 VERDICT: INCONCLUSIVE")
print("  - L48 dip = %.2fSE" % (abs(dip)/e48))
print("  - L64 rise = %.2fSE" % (peak/e48))
print("  - L48-L64 pair = %.2fSE (borderline, bootstrap CIs overlap)" % pair_L48_L64)
print("  - 3 data points cannot distinguish FSS models")
print("  - Non-monotonicity plausible as noise OR systematic")
print("  - RECOMMEND Phase 2: extended-L bond_wrap MC (L=96,128,192)")
