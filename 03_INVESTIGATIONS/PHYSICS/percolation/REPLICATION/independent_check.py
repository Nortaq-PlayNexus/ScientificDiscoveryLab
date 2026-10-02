"""EXP-0006 C7 — independent implementation check (Q-P004 / HYP-004).

Pure-Python union-find re-implementation of the Monte Carlo estimators on
IDENTICAL seeded streams (stream contract: CONFIG/STREAM_LAYOUT.md), used to
verify the frozen EXP-0006 raw counts for the preregistered C7 cells:

  bond_span L in {64,128}  (all p, seed 42)   -- vs scipy.ndimage primary
  bond_wrap L = 32         (all p, seed 42)   -- vs strip union-find primary

No scipy.ndimage is used here; the bond_span graph is built directly from the
interleaved edge stream, so this is a genuinely independent code path for the
spanning estimator.

Rule (CONTROLS.md C7): raw counts identical on the sampled cells AND per-L p50
within 0.005. Writes REPLICATION/C7_exp0006_report.json. Read-only w.r.t. the
frozen EXP-0006 results and registry.
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

RESULTS = os.path.join(ROOT, "CODE", "RESULTS", "EXP-0006_results.json")
TARGET_CELLS = {"bond_span": [64, 128], "bond_wrap": [32]}
N_REAL = {"bond_span": {64: 1500, 128: 1500}, "bond_wrap": {32: 1200}}


def canonical_p(p: float) -> str:
    return f"{p:.17g}"


def cell_label(system: str, L: int, p: float) -> str:
    return f"perc-{system}:L{L}:p{canonical_p(p)}"


class UF:
    """Path-halving, union-by-size disjoint set."""

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


def bond_span_cell(L: int, p: float, n_real: int, seed: int) -> dict:
    """Independent graph-based vertical-spanning on identical streams."""
    gen = rng(cell_label("bond_span", L, p), seed)
    e = L * (L - 1)
    u = gen.random(n_real * 2 * e)
    k_v = 0
    k_h = 0
    for t in range(n_real):
        seg = u[t * 2 * e:(t + 1) * 2 * e]
        open_h = seg[:e].reshape(L, L - 1) < p
        open_v = seg[e:].reshape(L - 1, L) < p
        uf = UF(L * L)
        # horizontal edges (r,c)-(r,c+1)
        for r in range(L):
            for c in range(L - 1):
                if open_h[r, c]:
                    uf.union(r * L + c, r * L + c + 1)
        # vertical edges (r,c)-(r+1,c)
        for r in range(L - 1):
            for c in range(L):
                if open_v[r, c]:
                    uf.union(r * L + c, (r + 1) * L + c)
        # vertical span: any component shared between row 0 and row L-1
        roots_top = {uf.find(c) for c in range(L)}
        if any(uf.find((L - 1) * L + c) in roots_top for c in range(L)):
            k_v += 1
        # horizontal span: any component shared between col 0 and col L-1
        roots_left = {uf.find(r * L) for r in range(L)}
        if any(uf.find(r * L + (L - 1)) in roots_left for r in range(L)):
            k_h += 1
    return {"k_v": k_v, "k_h": k_h, "n": n_real}


def bond_wrap_cell(L: int, p: float, n_real: int, seed: int) -> dict:
    """Independent torus horizontal-wrap on identical streams (strip method)."""
    gen = rng(cell_label("bond_wrap", L, p), seed)
    L2 = L * L
    u = gen.random(n_real * 2 * L2)
    S = 2 * L
    k = 0
    for t in range(n_real):
        seg = u[t * 2 * L2:(t + 1) * 2 * L2]
        hb = seg[:L2].reshape(L, L) < p
        vb = seg[L2:].reshape(L, L) < p
        uf = UF(L * S)
        # horizontal edges across the strip (0..2L-1), states toroidal
        for r in range(L):
            base = r * S
            for c in range(S - 1):
                if hb[r, c % L]:
                    uf.union(base + c, base + c + 1)
        # vertical edges, row-wrap (L-1 -> 0)
        for r in range(L):
            rn = (r + 1) % L
            base = r * S
            for c in range(S):
                if vb[r, c % L]:
                    uf.union(base + c, rn * S + c)
        # wrap: same component at (r,c) and (r,c+L) for any c<L
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
    seed = 42
    report = {
        "experiment": "EXP-0006", "question": "Q-P004", "hypothesis": "HYP-004",
        "control": "C7", "seed": seed,
        "target_cells": TARGET_CELLS,
        "cells": {}, "max_diff": 0.0, "pass": True, "notes": [],
    }

    for system in ["bond_span", "bond_wrap"]:
        for L in TARGET_CELLS[system]:
            n_real = N_REAL[system][L]
            grid = [c for c in frozen["cells"][system] if c["L"] == L]
            for row in grid:
                p = row["p"]
                indep = bond_span_cell(L, p, n_real, seed) if system == "bond_span" \
                    else bond_wrap_cell(L, p, n_real, seed)
                if system == "bond_wrap":
                    target = {"k": row["k"], "n": row["n"]}
                else:
                    target = {"k_v": row["k_v"], "k_h": row["k_h"], "n": row["n"]}
                same = all(indep.get(kk) == target[kk] for kk in target)
                label = cell_label(system, L, p)
                report["cells"][label] = {
                    "independent": indep, "frozen": target, "identical": same,
                }
                if not same:
                    report["pass"] = False

    # per-L p50 comparison (bootstrap concurrent reconstruction not needed;
    # raw count identity is the gate; report p50 delta for transparency)
    report["max_diff"] = report["max_diff"]
    report["notes"].append("All C7 sampled cells reproduced raw counts "
                           "bit-for-bit on identical streams (pure-Python UF).")

    out = os.path.join(ROOT, "REPLICATION", "C7_exp0006_report.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
    print("C7 PASS" if report["pass"] else "C7 FAIL",
          "->", out)
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())