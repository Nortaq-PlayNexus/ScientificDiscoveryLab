"""EXP-0007 Stage 1 — collect NEW bond_wrap cells at L=96,128,192.

Independent seeds (101/202/303). Writes raw per-cell counts to
RESULTS/EXP-0007_raw_L96.json, _L128.json, _L192.json one file per L
so a timeout does not lose all progress. Frozen L=32,48,64 data
comes from EXP-0005 (CODE/RESULTS/EXP-0005_results.json).
"""
from __future__ import annotations
import json, os, sys
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
ENGINE = os.path.join(LAB, "04_SHARED_ENGINE")
sys.path.insert(0, ENGINE)
sys.path.insert(0, os.path.join(ENGINE, ".."))
from engine.utilities.core import rng

def cell_label(L, p):
    return f"perc-bond-wrap-exp0007:L{L}:p{p:.17g}"

def _ufind_bond_wrap_cell(L, p, n_real, seed):
    gen = rng(cell_label(L, p), seed)
    total = n_real * 2 * L * L
    u = gen.random(total)
    S = 2 * L
    parent = list(range(L * S))
    size = [1] * (L * S)
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    k = 0
    for t in range(n_real):
        h = u[t * 2 * L * L:(t + 1) * 2 * L * L] < p
        hb = h[:L * L].reshape(L, L)
        vb = h[L * L:].reshape(L, L)
        parent[:] = list(range(L * S))
        size[:] = [1] * (L * S)
        for r in range(L):
            base = r * S
            for c in range(S - 1):
                if hb[r, c % L]:
                    a, b = base + c, base + c + 1
                    ra, sna = find(a), find(b)
                    if ra != sna:
                        if size[ra] < size[sna]: ra, sna = sna, ra
                        parent[sna] = ra; size[ra] += size[sna]
        for r in range(L):
            rn = (r + 1) % L
            base = r * S
            for c in range(S):
                if vb[r, c % L]:
                    a, b = base + c, rn * S + c
                    ra, sna = find(a), find(b)
                    if ra != sna:
                        if size[ra] < size[sna]: ra, sna = sna, ra
                        parent[sna] = ra; size[ra] += size[sna]
        wrapped = False
        for r in range(L):
            base = r * S
            for c in range(L):
                if find(base + c) == find(base + c + L):
                    wrapped = True; break
            if wrapped: break
        if wrapped: k += 1
    return {"k": k, "n": n_real}

def main():
    L_configs = [(96, 500, 101), (128, 400, 202), (192, 300, 303)]
    p_grid = list(np.arange(0.38, 0.64, 0.02))
    for L, n_real, seed in L_configs:
        out = []
        for i, p in enumerate(p_grid):
            if i % 5 == 0:
                print(f"  L={L} p={p:.2f} ({i+1}/{len(p_grid)})", flush=True)
            pres = _ufind_bond_wrap_cell(L, p, n_real, seed)
            out.append({"L": L, "p": float(p), "seed": seed, "n": pres["n"], "k": int(pres["k"])})
        path = os.path.join(ROOT, "RESULTS", f"EXP-0007_raw_L{L}.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(out, fh)
        print(f"  WROTE {path} ({len(out)} cells)", flush=True)
    print("STAGE 1 DONE")

if __name__ == "__main__":
    main()
