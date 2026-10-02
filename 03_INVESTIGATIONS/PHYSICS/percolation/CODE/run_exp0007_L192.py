"""EXP-0007 Stage 1 L=192 only."""
import json, os, sys
import numpy as np

LAB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
ENGINE = os.path.join(LAB, "04_SHARED_ENGINE")
sys.path.insert(0, ENGINE)
sys.path.insert(0, os.path.join(ENGINE, ".."))
from engine.utilities.core import rng

ROOT = os.path.dirname(os.path.abspath(__file__))

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
    p_grid = list(np.arange(0.38, 0.64, 0.02))
    L, n_real, seed = 192, 300, 303
    out = []
    for i, p in enumerate(p_grid):
        print(f"  p={p:.2f} ({i+1}/{len(p_grid)})", flush=True)
        pres = _ufind_bond_wrap_cell(L, p, n_real, seed)
        out.append({"L": L, "p": float(p), "seed": seed, "n": pres["n"], "k": int(pres["k"])})
    path = os.path.join(ROOT, "RESULTS", "EXP-0007_raw_L192.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh)
    print(f"WROTE {path}")
    print("STAGE 1 DONE")

if __name__ == "__main__":
    main()
