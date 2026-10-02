"""perc_engine — shared fast percolation machinery for Q-P005..Q-P011.

One graph-based architecture used by every experiment in the extended
percolation program:
  * any planar lattice is an explicit edge list over an LxL node grid
    (square, triangular, honeycomb/checkerboard-diagonal, brick);
  * occupation semantics: SITE = nodes open; BOND = edges open;
  * per realization, the induced subgraph is built as a CSR and components
    come from scipy.sparse.csgraph.connected_components (C speed);
  * open-BC vertical spanning (row 0 -> row L-1) is the crossing estimator;
  * all random draws come from G_LAB rng(label, seed) (EXP-0004-certified).

Any result that matters goes through this module; REPLICATION/ contains
pure-Python union-find independent implementations on identical streams.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(ROOT, "..", "..", "..", ".."))
ENGINE = os.path.join(LAB, "04_SHARED_ENGINE")
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

from engine.utilities.core import rng, seed_value, sha256_text  # noqa: E402
from scipy import sparse as ssp  # noqa: E402
from scipy.sparse import csgraph as scg  # noqa: E402
from scipy import stats as sstats  # noqa: E402
from scipy import optimize as sopt  # noqa: E402


# ----------------------------------------------------------------------------
# Lattice topologies: explicit (N= L*L) node grids + edge lists
# ----------------------------------------------------------------------------

def _grid_nodes(L: int):
    rows = np.repeat(np.arange(L, dtype=np.int64), L).reshape(L, L)
    cols = np.tile(np.arange(L, dtype=np.int64), L).reshape(L, L)
    return rows, cols


def square_lattice(L: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Nearest-neighbour 4-connectivity on an L x L grid.

    Returns (src, dst) int arrays of undirected edges and node count L*L.
    This SAME graph carries bond percolation (edges open) or site
    percolation (nodes open + edges between open nodes).
    """
    rows, cols = _grid_nodes(L)
    idx = (rows * L + cols).astype(np.int64).reshape(L, L)
    # horizontal edges (r, c)-(r, c+1) — stored once (undirected CSR)
    h_src = idx[:, :-1].ravel()
    h_dst = idx[:, 1:].ravel()
    # vertical edges (r, c)-(r+1, c) — stored once
    vsrc = (rows[:-1, :] * L + cols[:-1, :]).ravel().astype(np.int64)
    vdst = (rows[1:, :] * L + cols[1:, :]).ravel().astype(np.int64)
    src = np.concatenate([h_src, vsrc])
    dst = np.concatenate([h_dst, vdst])
    return src, dst, int(L * L)


def triangular_lattice(L: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Triangular lattice = square + one diagonal per cell (all NE).

    Degree-6 graph; the triangular lattice is self-dual for site percolation.
    """
    rows, cols = _grid_nodes(L)
    idx = (rows * L + cols).astype(np.int64).reshape(L, L)
    h_src = idx[:, :-1].ravel()
    h_dst = idx[:, 1:].ravel()
    vsrc = (rows[:-1, :] * L + cols[:-1, :]).ravel().astype(np.int64)
    vdst = (rows[1:, :] * L + cols[1:, :]).ravel().astype(np.int64)
    di_src = (rows[:-1, :-1] * L + cols[:-1, :-1]).ravel().astype(np.int64)
    di_dst = ((rows[:-1, :-1] + 1) * L + (cols[:-1, :-1] + 1)).ravel().astype(np.int64)
    src = np.concatenate([h_src, vsrc, di_src])
    dst = np.concatenate([h_dst, vdst, di_dst])
    return src, dst, int(L * L)


def honeycomb_lattice(L: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Honeycomb = planar dual of the triangular (square+NE-diag) lattice.

    The triangles of the (L-1)x(L-1) cell grid are the vertices:
      TA(r,c) = {(r,c),(r+1,c),(r+1,c+1)}        index = 2*(r*C+c)
      TB(r,c) = {(r,c),(r,c+1),(r+1,c+1)}        index = 2*(r*C+c)+1
    with C = L-1 cells per row. Two triangles are adjacent (share an edge) of
    degree 3 exactly:
      TA(r,c) <-> TB(r,c)   [NE diagonal]
      TA(r,c) <-> TB(r,c-1) [bottom edge]
      TA(r,c) <-> TB(r+1,c) [right edge]
      TB(r,c) <-> TA(r-1,c) [top edge]
      TB(r,c) <-> TA(r,c+1) [right edge]
    Every node therefore has degree 3 (honeycomb). Spanning is row-0 triangles
    (r=0) to row-(L-2) triangles (r=C-1).
    """
    C = int(L) - 1
    r, c = np.mgrid[0:C, 0:C]
    idTA = (2 * (r * C + c)).astype(np.int64)
    idTB = idTA + 1
    src = []
    dst = []

    def add(a, b):
        src.append(np.asarray([a], dtype=np.int64)[0])
        dst.append(np.asarray([b], dtype=np.int64)[0])

    A = idTA.ravel()
    B = idTB.ravel()
    # TA(r,c) <-> TB(r,c)
    src.append(A); dst.append(B)
    # TA(r,c) <-> TB(r,c-1)  for c>=1
    m = c[:, 1:] >= 1
    src.append(idTA[:, 1:][m]); dst.append(idTB[:, :-1][m])
    # TA(r,c) <-> TB(r+1,c)  for r <= C-2
    m = r[:-1] <= C - 2
    src.append(idTA[:-1][m]); dst.append(idTB[1:][m])
    # TB(r,c) <-> TA(r-1,c)  for r>=1
    m = r[1:] >= 1
    src.append(idTB[1:][m]); dst.append(idTA[:-1][m])
    src_a = np.concatenate(src)
    dst_a = np.concatenate(dst)
    N = int(2 * C * C)
    return src_a, dst_a, N


def brick_lattice(L: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Brick-wall (hexagonal) embedding with clean rows (used for honeycomb veto).

    Kept for generality; the checkerboard honeycomb is the primary hex model.
    """
    return honeycomb_lattice(L)


def rect_square_lattice(W: int, H: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Rectangle W x H, 4-connectivity, nodes id = r*W+c (r in 0..H-1)."""
    rows, cols = np.mgrid[0:H, 0:W]
    idx = (rows * W + cols).ravel().astype(np.int64)
    h_src = (rows[:, :-1] * W + cols[:, :-1]).ravel().astype(np.int64)
    h_dst = (rows[:, :-1] * W + cols[:, :-1] + 1).ravel().astype(np.int64)
    v_src = (rows[:-1, :] * W + cols[:-1, :]).ravel().astype(np.int64)
    v_dst = ((rows[:-1, :] + 1) * W + cols[:-1, :]).ravel().astype(np.int64)
    src = np.concatenate([h_src, h_dst, v_src, v_dst])
    dst = np.concatenate([h_dst, h_src, v_dst, v_src])
    return src, dst, int(W * H)


def cubic_lattice_3d(L: int) -> tuple[np.ndarray, np.ndarray, int]:
    """3D simple cubic lattice: 6-connectivity, L x L x L nodes.

    Node id = x + L*y + L^2*z (x,y,z in 0..L-1).
    Returns (src, dst) int arrays of undirected edges and node count L^3.
    """
    x, y, z = np.mgrid[0:L, 0:L, 0:L]
    idx = (x + L * y + L * L * z).astype(np.int64).reshape(L, L, L)
    src_list, dst_list = [], []
    for axis in range(3):
        slc_src = [slice(None), slice(None), slice(None)]
        slc_dst = [slice(None), slice(None), slice(None)]
        slc_src[axis] = slice(0, -1)
        slc_dst[axis] = slice(1, None)
        s = idx[tuple(slc_src)].ravel().astype(np.int64)
        d = idx[tuple(slc_dst)].ravel().astype(np.int64)
        src_list.append(s)
        dst_list.append(d)
    src = np.concatenate(src_list)
    dst = np.concatenate(dst_list)
    return src, dst, int(L ** 3)


# ----------------------------------------------------------------------------
# Crossing-size / row-vertex helpers
# ----------------------------------------------------------------------------

def row_node_indices(L: int) -> tuple[np.ndarray, np.ndarray]:
    """Indices of row 0 and row L-1 for an LxL grid."""
    return np.arange(L, dtype=np.int64), np.arange((L - 1) * L, L * L, dtype=np.int64)


# ----------------------------------------------------------------------------
# One realization: CSR + components + spanning + cluster stats
# ----------------------------------------------------------------------------

def build_component_array(edges_src, edges_dst, N, open_e, open_nodes=None):
    """Labels of the induced subgraph (open nodes + open edges).

    Site semantics: open_nodes selects occupied sites; edges are active when
    both endpoints are open (open_e unused, pass None).
    Bond semantics: open_nodes=None (all nodes active); open_e selects open
    edges. Isolated active nodes become singleton components via self loops.
    """
    if open_nodes is not None:
        active = open_nodes
        e_ok = open_e if open_e is not None else None
        eff_src = edges_src[active[edges_src] & active[edges_dst]]
        eff_dst = edges_dst[active[edges_src] & active[edges_dst]]
        # isolated open nodes
        connected = np.unique(np.concatenate([eff_src, eff_dst]))
        iso = np.setdiff1d(np.flatnonzero(active), connected, assume_unique=False)
        if iso.size:
            eff_src = np.concatenate([eff_src, iso])
            eff_dst = np.concatenate([eff_dst, iso])
    else:
        e_ok = open_e
        eff_src = edges_src[e_ok]
        eff_dst = edges_dst[e_ok]
        iv = np.flatnonzero(e_ok)
        lone = np.setdiff1d(np.arange(N, dtype=np.int64),
                            np.unique(np.concatenate([eff_src, eff_dst])), assume_unique=False)
        # note: nodes not incident to any open edge are singletons only if all
        # nodes are active (bond semantics) -> add self loops
        if lone.size:
            eff_src = np.concatenate([eff_src, lone])
            eff_dst = np.concatenate([eff_dst, lone])
    data = np.ones(eff_src.shape[0], dtype=np.int8)
    M = ssp.coo_matrix((data, (eff_src, eff_dst)), shape=(N, N)).tocsr()
    n_comp, labels = scg.connected_components(M, directed=False)
    return labels, n_comp


def spanning_flags(
    labels,
    N,
    L,
    top_rows=None,
    bottom_rows=None,
    node_rows=None,
    *,
    ndim=2,
):
    """Return ``(vertical_span, horizontal_span)`` for a labeled graph.

    The historical/default 2D convention checks rows ``0 -> L-1`` and columns
    ``0 -> L-1`` on an ``L x L`` grid. For an explicitly cubic graph
    (``N == L**3``), ``ndim=3`` checks opposite **z planes** for the vertical
    event and opposite **x planes across the full volume** for the horizontal
    event. Dimension is never inferred from ``N`` so a future non-cubic graph
    cannot silently receive cubic boundaries.
    """
    if ndim not in (2, 3):
        raise ValueError(f"ndim must be 2 or 3, got {ndim!r}")
    labels = np.asarray(labels)
    L = int(L)
    N = int(N)
    if labels.ndim != 1 or labels.shape[0] != N:
        raise ValueError(f"labels must be a 1-D array of length N={N}")
    if ndim == 3:
        if N != L**3:
            raise ValueError(f"3D spanning requires N=L^3; got N={N}, L^3={L**3}")
        if node_rows is not None:
            raise ValueError("node_rows is a 2D-only custom-boundary option")
        if top_rows is not None or bottom_rows is not None:
            raise ValueError("custom top_rows/bottom_rows are not supported in 3D")
        # Flattened node IDs reshape as [z, y, x] because
        # node_id = x + L*y + L**2*z.
        ids = np.arange(N, dtype=np.int64).reshape(L, L, L)
        z0 = set(labels[ids[0, :, :]].ravel().tolist())
        z1 = set(labels[ids[L - 1, :, :]].ravel().tolist())
        x0 = set(labels[ids[:, :, 0]].ravel().tolist())
        x1 = set(labels[ids[:, :, L - 1]].ravel().tolist())
        return bool(z0 & z1), bool(x0 & x1)

    # Backward-compatible 2D path, including the legacy node_rows override.
    if top_rows is None:
        top_rows = (0,)
    if bottom_rows is None:
        bottom_rows = (L - 1,)
    if node_rows is None:
        rows = (np.repeat(np.arange(L), L)).astype(np.int64)
        cols = np.tile(np.arange(L), L).astype(np.int64)
        left = cols == 0
        right = cols == L - 1
        lt = np.flatnonzero(left)
        rt = np.flatnonzero(right)
        lset = set(labels[lt].tolist())
        rset = set(labels[rt].tolist())
        h_span = bool(lset & rset)
    else:
        rows = np.asarray(node_rows, dtype=np.int64)
        h_span = False
    top = np.concatenate([rows[:, None] == t for t in top_rows]).any(axis=1)
    bot = np.concatenate([rows[:, None] == b for b in bottom_rows]).any(axis=1)
    tv = np.flatnonzero(top)
    bv = np.flatnonzero(bot)
    tset = set(labels[tv].tolist())
    bset = set(labels[bv].tolist())
    v_span = bool(tset & bset)
    return v_span, h_span


def cluster_stats(labels, N):
    """(sizes array, largest size, index of largest component)."""
    sizes = np.bincount(labels, minlength=int(labels.max()) + 1)
    sizes = sizes.astype(np.int64)
    largest = int(sizes[1:].max()) if sizes.shape[0] > 1 else 0
    big_idx = int(np.argmax(sizes[1:]) + 1)
    return sizes, largest, big_idx


def site_cluster_sizes(edges_src, edges_dst, N, open_nodes):
    """Sizes of every OPEN cluster in a site-percolation realization.

    Closed sites form their own singleton components (absent rows of the CSR),
    so a naive bincount(labels) would pollute the census with closed-site
    singletons. Restricting labels to the open subset folds each open cluster
    onto its label; bincount then yields per-cluster open sizes exactly.
    """
    active = open_nodes
    eff_ok = active[edges_src] & active[edges_dst]
    eff_src = edges_src[eff_ok]
    eff_dst = edges_dst[eff_ok]
    connected = np.unique(np.concatenate([eff_src, eff_dst]))
    iso = np.setdiff1d(np.flatnonzero(active), connected, assume_unique=False)
    if iso.size:
        eff_src = np.concatenate([eff_src, iso])
        eff_dst = np.concatenate([eff_dst, iso])
    data = np.ones(eff_src.shape[0], dtype=np.int8)
    M = ssp.coo_matrix((data, (eff_src, eff_dst)), shape=(N, N)).tocsr()
    _, labels = scg.connected_components(M, directed=False)
    open_idx = np.flatnonzero(active)
    lab_open = labels[open_idx]
    sizes = np.bincount(lab_open.astype(np.int64))
    sizes = sizes[sizes > 0]  # drop zero bins (labels owned only by closed sites)
    return sizes.astype(np.int64), len(sizes), lab_open


def largest_cluster_mask(labels, big_idx, N):
    return labels == big_idx


# ----------------------------------------------------------------------------
# RNG cell streams (G_LAB; deterministic per cell)
# ----------------------------------------------------------------------------

def cell_rng(label: str, seed: int):
    return rng(label, seed)


def draw_site_cell(edges_src, edges_dst, N, L, p, n_real, seed, label):
    """Draw n_real site-occupation configs; return per-real component labels."""
    gen = cell_rng(label, seed)
    u = gen.random(n_real * N)
    out = []
    for t in range(n_real):
        open_nodes = u[t * N:(t + 1) * N] < p
        labels, n_comp = build_component_array(edges_src, edges_dst, N, None, open_nodes)
        out.append(labels)
    return out


def draw_bond_cell(edges_src, edges_dst, E, N, L, p, n_real, seed, label):
    gen = cell_rng(label, seed)
    u = gen.random(n_real * E)
    out = []
    for t in range(n_real):
        open_e = u[t * E:(t + 1) * E] < p
        labels, n_comp = build_component_array(edges_src, edges_dst, N, open_e, None)
        out.append(labels)
    return out


# ----------------------------------------------------------------------------
# Cell statistics accumulation (reuseable for thresholds and exponents)
# ----------------------------------------------------------------------------

def run_span_cell_edges(edges_src, edges_dst, N, L, p, n_real, seed, label,
                        semantics="bond", want_stats=False, want_largest_mass=False,
                        want_cluster_sizes=False, node_rows=None, bottom_row=None,
                        *, ndim=2):
    """Generate a full cell, count vertical/horizontal spans (+optional stats).

    Returns dict(k_v, k_h, n) plus optional raw statistics arrays.
    """
    gen = cell_rng(label, seed)
    E = int(edges_src.shape[0])
    if semantics == "bond":
        tot = n_real * E
        u = gen.random(tot)
    else:
        tot = n_real * N
        u = gen.random(tot)
    k_v = 0
    k_h = 0
    if bottom_row is None:
        bottom_row = int(L) - 1
    stats = []
    cluster_size_lists = []
    for t in range(n_real):
        if semantics == "bond":
            open_e = u[t * E:(t + 1) * E] < p
            labels, n_comp = build_component_array(edges_src, edges_dst, N, open_e, None)
        else:
            open_nodes = u[t * N:(t + 1) * N] < p
            labels, n_comp = build_component_array(edges_src, edges_dst, N, None, open_nodes)
        span_kwargs = {"node_rows": node_rows, "ndim": ndim}
        if ndim == 2:
            span_kwargs["bottom_rows"] = (bottom_row,)
        v_span, h_span = spanning_flags(labels, N, L, **span_kwargs)
        k_v += int(v_span)
        k_h += int(h_span)
        if want_stats or want_largest_mass or want_cluster_sizes:
            if semantics == "site":
                csizes, n_open_clusters, _ = site_cluster_sizes(edges_src, edges_dst, N, open_nodes)
                sizes = csizes
            else:
                sizes, _, _ = cluster_stats(labels, N)
                sizes = sizes[1:]
            n_clusters = int(sizes.shape[0])
            largest = int(sizes.max()) if n_clusters else 0
            rec = {}
            if want_largest_mass:
                rec["mass"] = largest  # largest open-cluster size in sites
                rec["L2"] = N
            if want_stats:
                rec["n_comp"] = int(n_comp)
                rec["n_clusters"] = n_clusters
                if n_clusters > 1:
                    rec["second"] = int(np.partition(sizes, -2)[-2])
                else:
                    rec["second"] = 0
            stats.append(rec)
            if want_cluster_sizes:
                cluster_size_lists.append(np.sort(sizes)[::-1])
    out = {"k_v": k_v, "k_h": k_h, "n": n_real, "ndim": int(ndim)}
    if want_largest_mass:
        out["masses"] = [r["mass"] for r in stats]
        out["L2"] = N
    if want_stats:
        out["n_comps"] = [r["n_comp"] for r in stats]
        out["second_sizes"] = [r["second"] for r in stats]
    if want_cluster_sizes:
        out["cluster_sizes"] = cluster_size_lists
    return out


# ----------------------------------------------------------------------------
# Fitting (p50, bootstrap, FSS, probit width) — shared by all questions
# ----------------------------------------------------------------------------

def interp_p50(ps, W, target=0.5):
    ps = np.asarray(ps, dtype=float)
    W = np.asarray(W, dtype=float)
    below = W < target
    above = W > target
    if not below.any() or not above.any():
        raise ValueError("target not bracketed")
    i = int(np.flatnonzero(below)[-1])
    j = int(np.flatnonzero(above)[0])
    if i >= j:
        raise ValueError("grid ordering issue")
    p0, p1 = ps[i], ps[j]
    w0, w1 = W[i], W[j]
    return float(p0 + (target - w0) * (p1 - p0) / (w1 - w0))


def bootstrap_p50(ps, ks, ns, draws=500, seed=42, label="perc-boot"):
    gen = rng(label, seed)
    ws = np.asarray(ks, dtype=float) / np.asarray(ns, dtype=float)
    ps = np.asarray(ps, dtype=float)
    out = []
    for _ in range(draws):
        kb = gen.binomial(np.asarray(ns, dtype=np.int64), ws)
        wb = kb / np.asarray(ns, dtype=float)
        try:
            out.append(interp_p50(ps, wb))
        except ValueError:
            continue
    if len(out) < 2:
        raise RuntimeError("bootstrap too degenerate")
    out = np.asarray(out)
    return float(out.mean()), float(out.std(ddof=1) if len(out) > 1 else 0.0), out


def fss_fit(Ls, y, se=None, xexp=-3.0 / 4.0, drop=None, weights=True):
    """WLS (or OLS) y(L) = a + b*L^xexp. Returns dict with a, se_a, b, chi2_red."""
    Ls = np.asarray(Ls, dtype=float)
    y = np.asarray(y, dtype=float)
    if drop:
        keep = ~np.isin(Ls, np.asarray(drop, dtype=float))
        Ls, y = Ls[keep], y[keep]
        if se is not None:
            se = np.asarray(se, dtype=float)[keep]
    x = Ls ** (float(xexp))
    if weights and se is not None and np.all(se > 0):
        w = 1.0 / np.asarray(se, dtype=float)
        A = np.vstack([np.ones_like(x), x]).T
        W = np.diag(w)
        coef, *_ = np.linalg.lstsq(W @ A, W @ y, rcond=None)
        resid = y - (A @ coef)
        chi2 = float(np.sum((resid * w) ** 2))
        cov = np.linalg.inv(A.T @ (W @ W) @ A)
    else:
        A = np.vstack([np.ones_like(x), x]).T
        coef, *_ = np.linalg.lstsq(A, y, rcond=None)
        resid = y - (A @ coef)
        chi2 = float(np.sum(resid ** 2))
        cov = np.linalg.inv(A.T @ A)
    a, b = float(coef[0]), float(coef[1])
    df = max(int(len(Ls)) - 2, 1)
    chi2_red = chi2 / df if df > 0 else None
    se_a = float(np.sqrt(cov[0, 0])) if len(Ls) > 2 else None
    return {"a": a, "se_a": se_a, "b": b, "chi2_red": chi2_red, "L_used": sorted(int(l) for l in Ls)}


def loglog_slope(x, y):
    x = np.log(np.asarray(x, dtype=float))
    y = np.log(np.asarray(y, dtype=float))
    coef = np.polyfit(x, y, 1)
    return float(coef[0]), float(coef[1])


def probit_fit(ps, ks, ns, s0=0.10):
    """MLE probit width (mu, sigma) with anti-degenerate start (EXP-0005 lesson)."""
    ps = np.asarray(ps, dtype=float)
    k = np.asarray(ks, dtype=np.int64)
    n = np.asarray(ns, dtype=np.int64)
    W = k / n
    try:
        mu0 = interp_p50(ps, W)
    except ValueError:
        mu0 = float(np.median(ps))

    def nll(theta):
        mu, logs = theta
        s = np.exp(logs)
        z = (ps - mu) / s
        P = sstats.norm.cdf(z)
        P = np.clip(P, 1e-12, 1.0 - 1e-12)
        return -float(np.sum(k * np.log(P) + (n - k) * np.log(1.0 - P)))

    res = sopt.minimize(nll, [mu0, np.log(s0)], method="L-BFGS-B",
                        bounds=[(None, None), (-10, 10)])
    mu, s = float(res.x[0]), float(np.exp(res.x[1]))
    return mu, s, res.success


# ----------------------------------------------------------------------------
# Registry/metadata helpers
# ----------------------------------------------------------------------------

def append_registry(RESULTS, CONFIG, EXP_ID, QUESTION_ID, HYP_ID, decision,
                    result_path, extra=None):
    from engine.reproducibility.experiments import append_registry_row
    row = {"experiment_id": EXP_ID, "question": QUESTION_ID, "hypothesis": HYP_ID,
           "seed": 42, "decision": decision, "result_path": result_path}
    if extra:
        row.update(extra)
    append_registry_row(os.path.join(CONFIG, "registry.jsonl"), row)


def write_summary(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
    return path