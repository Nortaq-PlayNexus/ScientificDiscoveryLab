"""EXP-0009 / Q-P005 — C7 independent implementation (pure-Python union-find).

Re-derives M_max and chi on the IDENTICAL frozen streams (same G_LAB rng
label + seed, first 40 realizations of each exponent cell) with NO
scipy.sparse / csgraph — a bespoke union-find with path compression and
size-tracking. Verifies bit-identical per-realization statistics vs the
engine's census and the D_f subsample slope within 3 joint-SE of the
bootstrap SE recorded in EXP-0009_results.json.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
QDIR = os.path.dirname(HERE)
ROOT = os.path.dirname(QDIR)  # percolation investigation root
ENGINE = os.path.join(ROOT, "ENGINE")
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

import perc_engine as pe  # noqa: E402

PCONF = os.path.join(QDIR, "CONFIG")
PC = json.load(open(os.path.join(PCONF, "prereg_EXP-0009.json"), encoding="utf-8"))
SEED = PC["seed"]
P_C = PC["parameters"]["p_c"]
PCAN = PC["p_canon_token"]
LBASE = PC["rng_label_pattern"]
NSUB = 40
L_LIST = [128, 256, 512]


def cell_label(L, kind):
    return LBASE.replace("<system>", "site-square").replace("<L>", str(L)).replace(
        "<pcanon>", PCAN).replace("<kind>", kind)


class UnionFind:
    __slots__ = ("parent", "size", "largest")

    def __init__(self, n):
        self.parent = np.arange(n, dtype=np.int64)
        self.size = np.ones(n, dtype=np.int64)
        self.largest = 1

    def find(self, x):
        p = self.parent
        while p[x] != x:
            p[x] = p[p[x]]          # path halving
            x = p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.size[rb] = 0          # deactivate stale root so size[] holds live clusters only
        if self.size[ra] > self.largest:
            self.largest = int(self.size[ra])

    def merge_neighbors(self, idx, W, H):
        """idx: (H, W) int32 array of node ids (open=-1 .. n-1, closed=-1)."""
        for r in range(H):
            base = r * W
            row = idx[r]
            for c in range(W):
                v = row[c]
                if v < 0:
                    continue
                if c + 1 < W and row[c + 1] >= 0:
                    self.union(v, row[c + 1])
                if r + 1 < H and idx[r + 1][c] >= 0:
                    self.union(v, idx[r + 1][c])


def uf_census(L, n, seed, kind="exp"):
    """Pure-Python cluster census on the frozen stream (no scipy)."""
    lab = cell_label(L, kind)
    gen = pe.rng(lab, seed)
    W = H = L
    tot = n * L * L
    u = gen.random(tot)
    masses = np.empty(n, dtype=np.float64)
    chis = np.empty(n, dtype=np.float64)
    for t in range(n):
        occ = (u[t * L * L:(t + 1) * L * L] < P_C)
        arr = occ.reshape(H, W).astype(np.int64)
        idx = np.full((H, W), -1, dtype=np.int64)
        ctr = 0
        for r in range(H):
            for c in range(W):
                if arr[r, c]:
                    idx[r, c] = ctr
                    ctr += 1
        if ctr == 0:
            masses[t] = 0.0
            chis[t] = 0.0
            continue
        uf = UnionFind(ctr)
        uf.merge_neighbors(idx, W, H)
        # chi: second moment / first moment over cluster sizes
        sizes = uf.size[uf.size > 0]
        masses[t] = float(uf.largest)
        s = sizes.astype(np.float64)
        chis[t] = float((s * s).sum() / s.sum())
    return masses, chis


def engine_subset(L, n, seed):
    src, dst, N = pe.square_lattice(L)
    lab = cell_label(L, "exp")
    o = pe.run_span_cell_edges(src, dst, N, L, P_C, n, seed, lab, semantics="site",
                               want_largest_mass=True, want_cluster_sizes=True)
    chis = []
    for ss in o["cluster_sizes"]:
        s = np.asarray(ss, dtype=np.float64)
        chis.append(float((s * s).sum() / s.sum()) if s.size else 0.0)
    return np.asarray(o["masses"], dtype=np.float64), np.asarray(chis, dtype=np.float64)


def main():
    perL = {}
    all_diffs = []
    uf_mass = {}
    for L in L_LIST:
        m_uf, c_uf = uf_census(L, NSUB, SEED)
        m_eng, c_eng = engine_subset(L, NSUB, SEED)
        dm = np.abs(m_uf - m_eng)
        dc = np.abs(c_uf - c_eng)
        perL[L] = {"n": NSUB, "Mmax_identical": bool(dm.max() == 0),
                   "chi_identical": bool(dc.max() == 0),
                   "max_diff_Mmax": float(dm.max()), "max_diff_chi": float(dc.max()),
                   "uf_mean_Mmax": float(m_uf.mean()), "eng_mean_Mmax": float(m_eng.mean())}
        all_diffs.append(float(dm.max())); all_diffs.append(float(dc.max()))
        uf_mass[L] = m_uf
        print(f"L={L}: Mmax identical={dm.max()==0} chi identical={dc.max()==0}")

    # D_f on the union-find subsample over the 4 sizes; compare with results JSON
    logx = np.log(np.asarray(L_LIST, dtype=np.float64))
    slopes = []
    gen = pe.rng("c7-df-boot", SEED)
    for _ in range(2000):
        means = []
        for L in L_LIST:
            idx = gen.integers(0, NSUB, size=NSUB)
            means.append(uf_mass[L][idx].mean())
        slopes.append(np.polyfit(logx, np.log(np.array(means)), 1)[0])
    slopes = np.asarray(slopes)
    uf_Df = float(slopes.mean())
    uf_Df_se = float(slopes.std(ddof=1))

    # compare to engine D_f in EXP-0009_results.json (bootstrap SE recorded)
    res = json.load(open(os.path.join(QDIR, "CODE", "RESULTS", "EXP-0009_results.json"),
                         encoding="utf-8"))
    eng_Df = res["primary_results"]["exponents"]["D_f"]["value"]
    eng_se = res["primary_results"]["exponents"]["D_f"]["se"]
    dDf = abs(uf_Df - eng_Df)
    tol = 3.0 * max(eng_se, uf_Df_se, 1e-9)
    gate_dDf = bool(dDf <= tol)

    gate_stats = all(v["Mmax_identical"] and v["chi_identical"] for v in perL.values())
    report = {
        "experiment_id": "EXP-0009", "gate": "C7",
        "implementation": "pure-Python union-find (path halving, size-tracking); no scipy.sparse/csgraph",
        "streams": "identical G_LAB rng labels/seeds; first 40 realizations of each exponent cell",
        "per_L": {str(k): v for k, v in perL.items()},
        "per_realization_Mmax_identical": bool(gate_stats),
        "D_f": {"uf_subsample": uf_Df, "uf_boot_se": uf_Df_se,
                "engine_reported": eng_Df, "engine_boot_se": eng_se,
                "abs_diff": dDf, "tol_3se": tol, "pass": bool(gate_dDf)},
        "pass": bool(gate_stats and gate_dDf),
    }
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    rp = os.path.join(HERE, "C7_exp0009_report.json")
    with open(rp, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    # the runner merges this report into the final summary/results files
    print(json.dumps(report, indent=2))
    print("C7 PASS:", report["pass"])


if __name__ == "__main__":
    main()