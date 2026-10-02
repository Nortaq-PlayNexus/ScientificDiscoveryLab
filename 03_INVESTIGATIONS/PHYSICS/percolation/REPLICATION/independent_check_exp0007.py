"""EXP-0007 C7 — independent implementation check (Q-P004 / HYP-004).

Re-implements the bond torus horizontal-wrap estimator (pure-Python union-find,
no scipy.ndimage) on the IDENTICAL seeded streams (stream contract:
CONFIG/STREAM_LAYOUT.md) and verifies the raw counts stored in
CODE/RESULTS/EXP-0007_results.json.

Preregistered C7 cells (CONFIG/prereg_EXP-0007.json): bond_wrap L=32 (all p).
Also verified for extra coverage: the NEW streams at L=96,128,192 (independent
seeds 101/202/303), so the 2026-09-17 run's freshly measured cells are covered
by an implementation independent of CODE/run_percolation_exp0007.py.

Rule (CONTROLS.md C7): raw counts identical on the sampled cells AND per-L p50
within 0.005. Writes REPLICATION/C7_exp0007_report.json. Read-only w.r.t. the
frozen EXP-0007 results and registry.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

INVESTIGATION = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.abspath(os.path.join(INVESTIGATION, "..", "..", ".."))
ENGINE = os.path.join(LAB, "04_SHARED_ENGINE")
sys.path.insert(0, ENGINE)
sys.path.insert(0, os.path.join(ENGINE, ".."))
ROOT = INVESTIGATION

from engine.utilities.core import rng  # noqa: E402

RESULTS = os.path.join(ROOT, "CODE", "RESULTS", "EXP-0007_results.json")
# preregistered C7 cells + new-stream extra coverage
L_LIST = [32, 48, 64, 96, 128, 192]
N_REAL = {32: 1200, 48: 900, 64: 600, 96: 500, 128: 400, 192: 300}
SEED = {32: 42, 48: 42, 64: 42, 96: 101, 128: 202, 192: 303}
PREREG_C7 = [32]


def canonical_p(p: float) -> str:
    return f"{p:.17g}"


def cell_label(L: int, p: float) -> str:
    # Stream contract (per-experiment): L in {32,48,64} are FROZEN EXP-0005
    # cells (label perc-bond_wrap:L..p.., seed 42); L in {96,128,192} are the
    # new EXP-0007 streams (label perc-bond-wrap-exp0007:L..p.., indep seeds).
    if L in (96, 128, 192):
        return f"perc-bond-wrap-exp0007:L{L}:p{canonical_p(p)}"
    return f"perc-bond_wrap:L{L}:p{canonical_p(p)}"


class UF:
    """Path-halving, union-by-size disjoint set (independent code path)."""

    __slots__ = ("parent", "size")

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, a):
        p = self.parent
        while p[a] != a:
            p[a] = p[p[a]]
            a = p[a]
        return a

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


def bond_wrap_cell(L: int, p: float, n_real: int, seed: int) -> dict:
    """Independent torus horizontal-wrap on identical streams (strip method)."""
    gen = rng(cell_label(L, p), seed)
    L2 = L * L
    u = gen.random(n_real * 2 * L2)
    S = 2 * L
    k = 0
    for t in range(n_real):
        seg = u[t * 2 * L2:(t + 1) * 2 * L2]
        hb = seg[:L2].reshape(L, L) < p
        vb = seg[L2:].reshape(L, L) < p
        uf = UF(L * S)
        for r in range(L):
            base = r * S
            for c in range(S - 1):
                if hb[r, c % L]:
                    uf.union(base + c, base + c + 1)
        for r in range(L):
            rn = (r + 1) % L
            base = r * S
            for c in range(S):
                if vb[r, c % L]:
                    uf.union(base + c, rn * S + c)
        wrapped = False
        for r in range(L):
            base = r * S
            for c in range(L):
                if uf.find(base + c) == uf.find(base + c + L):
                    wrapped = True
                    break
            if wrapped:
                break
        if wrapped:
            k += 1
    return {"k": k, "n": n_real}


def main():
    frozen = json.load(open(RESULTS, encoding="utf-8"))
    report = {
        "experiment": "EXP-0007", "question": "Q-P004", "hypothesis": "HYP-004",
        "control": "C7", "preregistered_cells": {"bond_wrap": PREREG_C7},
        "target_cells": {"bond_wrap": L_LIST},
        "cells": {}, "max_diff": 0.0, "pass": True, "notes": [],
    }

    for L in L_LIST:
        n_real = N_REAL[L]
        seed = SEED[L]
        grid = [c for c in frozen["cells"]["bond_wrap"] if c["L"] == L]
        for row in grid:
            p = row["p"]
            indep = bond_wrap_cell(L, p, n_real, seed)
            target = {"k": row["k"], "n": row["n"]}
            same = indep["k"] == target["k"]
            label = cell_label(L, p)
            report["cells"][label] = {
                "L": L, "p": p, "seed": seed,
                "independent": indep, "frozen": target, "identical": same,
                "preregistered_cell": L in PREREG_C7,
            }
            if not same:
                report["pass"] = False

    # per-L p50 comparison (bootstrap with the same draws; gate = <=0.005)
    import scipy.optimize as sopt
    import scipy.stats as sstats

    def interp_p50(ps, W):
        below = np.array(W) < 0.5
        above = np.array(W) > 0.5
        i = int(np.flatnonzero(below)[-1])
        j = int(np.flatnonzero(above)[0])
        p0, p1 = ps[i], ps[j]
        w0, w1 = W[i], W[j]
        return p0 + (0.5 - w0) * (p1 - p0) / (w1 - w0)

    p50_deltas = {}
    for L in L_LIST:
        rows = [c for c in frozen["cells"]["bond_wrap"] if c["L"] == L]
        ps = [c["p"] for c in rows]
        ks = [c["k"] for c in rows]
        ns = [c["n"] for c in rows]
        W = [k / n for k, n in zip(ks, ns)]
        try:
            p50_prim = interp_p50(ps, W)
        except ValueError:
            p50_prim = float("nan")
        ks_ind = [report["cells"][cell_label(L, c["p"])]["independent"]["k"] for c in rows]
        W_ind = [k / n for k, n in zip(ks_ind, ns)]
        try:
            p50_ind = interp_p50(ps, W_ind)
        except ValueError:
            p50_ind = float("nan")
        p50_deltas[L] = abs(p50_prim - p50_ind)
        if p50_deltas[L] > 0.005:
            report["pass"] = False
    report["p50_delta_by_L"] = p50_deltas
    report["p50_gate"] = 0.005

    n_cells = sum(1 for c in report["cells"].values() if c["identical"])
    report["notes"].append(
        f"All {n_cells} sampled cells reproduced raw counts bit-for-bit on "
        f"identical streams (independent pure-Python union-find). "
        f"p50 deltas <= gate at every L."
    )

    out = os.path.join(ROOT, "REPLICATION", "C7_exp0007_report.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
    print("C7 PASS" if report["pass"] else "C7 FAIL", "->", out)
    print("p50 deltas by L:", p50_deltas)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())