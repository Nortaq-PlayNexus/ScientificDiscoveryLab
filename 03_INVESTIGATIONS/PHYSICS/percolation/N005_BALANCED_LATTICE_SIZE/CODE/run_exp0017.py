#!/usr/bin/env python3
"""EXP-0017 / N-005 runner - balanced power-of-two vs non-power-of-two lattice test.

Tests audit finding N-005: is there a reproducible power-of-two effect on the
2D site cluster-mass exponent once physical size, estimator, and random-stream
policy are matched?

Design (frozen in CONFIG/prereg_EXP-0017.json, SHA-256 bound):

  * One L x L uniform field per realization yields every preregistered
    sub-window size, so a power-of-two size and its neighbour share all random
    numbers (nested common random numbers). This is the PRIMARY estimator.
  * An independent-stream arm repeats the contrast with no sharing at all.
  * A null-control arm contrasts two adjacent NON-power-of-two pairs, which
    measures how large a purely smooth size dependence looks in this estimator.
  * A 2-adic ladder separates "power of two" from "even" and from higher
    powers of two.
  * A second implementation (explicit edge list + connected_components) and a
    from-scratch pure-Python BFS census provide independence checks.

Subcommands: run, analyze, validate. The runner refuses to overwrite an
existing output directory and never modifies historical experiment data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage
from scipy import sparse as ssp
from scipy.sparse import csgraph as scg

INV_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = INV_ROOT.parents[3]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
for _p in (str(SHARED_ENGINE), str(SHARED_ENGINE.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engine.hypothesis_testing.prereg import verify_frozen_config  # noqa: E402
from engine.utilities.core import rng  # noqa: E402

PREREG = INV_ROOT / "CONFIG" / "prereg_EXP-0017.json"

# Four-connectivity: centre plus edge neighbours, no diagonals. Verified against
# a from-scratch BFS census; see REPORT/TECHNICAL_EXP-0017.md.
STRUCT4 = np.array([[0, 1, 0],
                    [1, 1, 1],
                    [0, 1, 0]], dtype=bool)

# Implementation choices the prereg left open, recorded here and echoed into the
# manifest so they are never implicit.
IMPL_CHOICES = {
    "realization_block": 8,
    "c7_subsample_n": 8,
    "bfs_bases": [128, 256],
    "bfs_n": 3,
    "bootstrap_draws": 5000,
    "bootstrap_seed": 5170017,
    "ladder_pairs": "consecutive ladder members, reported descriptively",
}

MANIFEST_SCHEMA = "n005-exp0017-manifest-v1"
SUMMARY_SCHEMA = "n005-exp0017-summary-v1"


class N005Error(RuntimeError):
    pass


class ConfigError(N005Error):
    pass


class GateError(N005Error):
    pass


# --------------------------------------------------------------------------
# hashing / strict json
# --------------------------------------------------------------------------

def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_array(arr: np.ndarray) -> str:
    return sha256_bytes(np.ascontiguousarray(arr).tobytes())


def load_strict_json(path: Path) -> dict[str, Any]:
    def no_dupes(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ConfigError(f"duplicate JSON key: {k}")
            out[k] = v
        return out

    def no_nonfinite(x):
        raise ConfigError(f"non-finite JSON number: {x}")

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=no_dupes,
                      parse_constant=no_nonfinite)


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, allow_nan=False)
        fh.write("\n")
    return path


# --------------------------------------------------------------------------
# census implementations
# --------------------------------------------------------------------------

def census_ndimage(mask: np.ndarray) -> np.ndarray:
    """Primary: four-connectivity labelling of open sites.

    Closed sites are background, so bincount over the labels counts open sites
    only and needs no set arithmetic.
    """
    labels, _ = ndimage.label(mask, structure=STRUCT4)
    sizes = np.bincount(labels.ravel())[1:]
    return sizes[sizes > 0].astype(np.int64)


def square_edge_list(L: int) -> tuple[np.ndarray, np.ndarray]:
    """Explicit open-boundary square-lattice edge list, node id = r*L + c."""
    rows = np.repeat(np.arange(L, dtype=np.int64), L).reshape(L, L)
    cols = np.tile(np.arange(L, dtype=np.int64), L).reshape(L, L)
    idx = (rows * L + cols).reshape(L, L)
    h_src = idx[:, :-1].ravel()
    h_dst = idx[:, 1:].ravel()
    v_src = idx[:-1, :].ravel()
    v_dst = idx[1:, :].ravel()
    return (np.concatenate([h_src, v_src]),
            np.concatenate([h_dst, v_dst]))


_EDGE_CACHE: dict[int, tuple[np.ndarray, np.ndarray]] = {}


def census_edge_list(mask: np.ndarray) -> np.ndarray:
    """Independent implementation: explicit edge list + connected_components."""
    L = mask.shape[0]
    if L not in _EDGE_CACHE:
        _EDGE_CACHE[L] = square_edge_list(L)
    src, dst = _EDGE_CACHE[L]
    flat = mask.ravel()
    ok = flat[src] & flat[dst]
    es, ed = src[ok], dst[ok]
    connected = np.unique(np.concatenate([es, ed])) if es.size else np.empty(0, np.int64)
    iso = np.setdiff1d(np.flatnonzero(flat), connected)
    if iso.size:
        es = np.concatenate([es, iso])
        ed = np.concatenate([ed, iso])
    data = np.ones(es.shape[0], dtype=np.int8)
    M = ssp.coo_matrix((data, (es, ed)), shape=(L * L, L * L)).tocsr()
    _, labels = scg.connected_components(M, directed=False)
    open_idx = np.flatnonzero(flat)
    sizes = np.bincount(labels[open_idx].astype(np.int64))
    sizes = sizes[sizes > 0]
    return sizes.astype(np.int64)


def census_bfs_python(mask: np.ndarray) -> int:
    """Third implementation: from-scratch BFS, pure Python, no numpy/scipy.

    Returns the largest open cluster size. O(L^2) with Python-level loops, so
    this is only used on small cells.
    """
    L = mask.shape[0]
    rows = [list(r) for r in mask.tolist()]
    seen = [[False] * L for _ in range(L)]
    best = 0
    for r0 in range(L):
        for c0 in range(L):
            if not rows[r0][c0] or seen[r0][c0]:
                continue
            q = deque([(r0, c0)])
            seen[r0][c0] = True
            size = 0
            while q:
                r, c = q.popleft()
                size += 1
                if r + 1 < L and rows[r + 1][c] and not seen[r + 1][c]:
                    seen[r + 1][c] = True
                    q.append((r + 1, c))
                if r - 1 >= 0 and rows[r - 1][c] and not seen[r - 1][c]:
                    seen[r - 1][c] = True
                    q.append((r - 1, c))
                if c + 1 < L and rows[r][c + 1] and not seen[r][c + 1]:
                    seen[r][c + 1] = True
                    q.append((r, c + 1))
                if c - 1 >= 0 and rows[r][c - 1] and not seen[r][c - 1]:
                    seen[r][c - 1] = True
                    q.append((r, c - 1))
            best = max(best, size)
    return best


def largest(sizes: np.ndarray) -> int:
    return int(sizes.max()) if sizes.size else 0


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------

def load_prereg(path: Path) -> dict[str, Any]:
    doc = verify_frozen_config(path)
    p = doc["parameters"]
    if p.get("audit_finding_id") != "N-005":
        raise ConfigError("preregistration is not the N-005 protocol")
    if p.get("investigation_id") != "Q-P009":
        raise ConfigError("preregistration is not the Q-P009 protocol")
    for key in ("base_sizes", "n_real", "pair_offsets", "ladder_offsets",
                "ladder_bases", "p_c", "equivalence_margin", "reference_D_f",
                "independent_stream_replication_n"):
        if key not in p:
            raise ConfigError(f"preregistration missing parameter: {key}")
    if float(p["p_c"]) != 0.5927460507921:
        raise ConfigError("unexpected p_c in frozen preregistration")
    return doc


def sizes_for_base(params: dict[str, Any], base: int) -> list[int]:
    """Every sub-window size sampled from a base field, ascending."""
    wanted = set()
    for spec in params["pair_offsets"].values():
        wanted.add(base - int(spec["upper"]))
        wanted.add(base - int(spec["lower"]))
    if base in [int(b) for b in params["ladder_bases"]]:
        for off in params["ladder_offsets"]:
            wanted.add(base - int(off))
    return sorted(s for s in wanted if 2 <= s <= base)


def pair_specs(params: dict[str, Any], base: int) -> list[tuple[str, int, int]]:
    """(pair_type, size_hi, size_lo) for one base, in preregistered order."""
    out = []
    for name, spec in params["pair_offsets"].items():
        out.append((name, base - int(spec["upper"]), base - int(spec["lower"])))
    return out


# --------------------------------------------------------------------------
# measurement
# --------------------------------------------------------------------------

def measure_nested(params: dict[str, Any], base: int, n_real: int, tag: str,
                    c7_n: int, bfs_bases: list[int], bfs_n: int,
                    progress: bool = True) -> dict[str, Any]:
    """Nested common-random-numbers arm: one field per realization, many sizes."""
    p_c = float(params["p_c"])
    sizes = sizes_for_base(params, base)
    smax = {s: np.zeros(n_real, dtype=np.int64) for s in sizes}
    n_open = {s: np.zeros(n_real, dtype=np.int64) for s in sizes}
    field_hashes: list[str] = []
    c7_checked = 0
    c7_mismatch: list[str] = []
    bfs_checked = 0
    bfs_mismatch: list[str] = []
    block = int(IMPL_CHOICES["realization_block"])
    gen = rng(f"exp0017-nested-L{base}-{tag}", 20260926 + base)
    t0 = time.perf_counter()
    done = 0
    while done < n_real:
        m = min(block, n_real - done)
        u = gen.random(m * base * base)
        for j in range(m):
            i = done + j
            field = (u[j * base * base:(j + 1) * base * base] < p_c).reshape(base, base)
            field_hashes.append(sha256_array(field))
            for s in sizes:
                sub = field[:s, :s]
                n_open[s][i] = int(sub.sum())
                smax[s][i] = largest(census_ndimage(sub))
            if i < c7_n:
                for s in sizes:
                    a = int(smax[s][i])
                    b = largest(census_edge_list(field[:s, :s]))
                    c7_checked += 1
                    if a != b:
                        c7_mismatch.append(f"L{base}:r{i}:size{s}:ndimage={a}:edge={b}")
            if base in bfs_bases and i < bfs_n:
                for s in sizes:
                    a = int(smax[s][i])
                    b = census_bfs_python(field[:s, :s])
                    bfs_checked += 1
                    if a != b:
                        bfs_mismatch.append(f"L{base}:r{i}:size{s}:ndimage={a}:bfs={b}")
        done += m
        if progress:
            el = time.perf_counter() - t0
            rate = done / max(el, 1e-9)
            print(f"    base {base}: {done}/{n_real} realizations "
                  f"({el:6.1f}s, {rate:5.2f}/s, eta {(n_real-done)/max(rate,1e-9):6.1f}s)",
                  flush=True)
    return {
        "mode": "nested",
        "base": base,
        "n_real": n_real,
        "sizes": sizes,
        "smax": smax,
        "n_open": n_open,
        "field_hashes": field_hashes,
        "c7_checked": c7_checked,
        "c7_mismatch": c7_mismatch,
        "bfs_checked": bfs_checked,
        "bfs_mismatch": bfs_mismatch,
        "seconds": time.perf_counter() - t0,
    }


def measure_independent(params: dict[str, Any], base: int, n_real: int, tag: str,
                        progress: bool = True) -> dict[str, Any]:
    """Independent-stream arm: every sampled size gets its own fresh field."""
    p_c = float(params["p_c"])
    specs = pair_specs(params, base)
    sizes = sorted({s for _, hi, lo in specs for s in (hi, lo)})
    smax = {s: np.zeros(n_real, dtype=np.int64) for s in sizes}
    n_open = {s: np.zeros(n_real, dtype=np.int64) for s in sizes}
    field_hashes: dict[int, list[str]] = {s: [] for s in sizes}
    gens = {s: rng(f"exp0017-indep-L{base}-S{s}-{tag}", 20260926 + base + s)
            for s in sizes}
    t0 = time.perf_counter()
    for i in range(n_real):
        for s in sizes:
            field = (gens[s].random(s * s) < p_c).reshape(s, s)
            field_hashes[s].append(sha256_array(field))
            n_open[s][i] = int(field.sum())
            smax[s][i] = largest(census_ndimage(field))
        if progress and (i + 1) % 5 == 0:
            el = time.perf_counter() - t0
            print(f"    indep base {base}: {i+1}/{n_real} ({el:6.1f}s)", flush=True)
    return {
        "mode": "independent",
        "base": base,
        "n_real": n_real,
        "sizes": sizes,
        "smax": smax,
        "n_open": n_open,
        # flat digest list in (size, realization) order, matching the nested arm's
        # contract, plus the per-size breakdown for the manifest
        "field_hashes": [h for s in sizes for h in field_hashes[s]],
        "field_sha256_by_size": field_hashes,
        "seconds": time.perf_counter() - t0,
    }


def sanity_checks() -> dict[str, Any]:
    """C9: exact-zero and all-open fields must behave exactly."""
    out = {}
    for L in (8, 33):
        empty = np.zeros((L, L), dtype=bool)
        full = np.ones((L, L), dtype=bool)
        out[f"empty_{L}"] = {
            "ndimage": largest(census_ndimage(empty)),
            "edge": largest(census_edge_list(empty)),
            "bfs": census_bfs_python(empty),
        }
        out[f"full_{L}"] = {
            "ndimage": largest(census_ndimage(full)),
            "edge": largest(census_edge_list(full)),
            "bfs": census_bfs_python(full),
        }
    problems = []
    for key, rec in out.items():
        vals = set(rec.values())
        expect = 0 if key.startswith("empty") else int(key.split("_")[1]) ** 2
        if vals != {expect}:
            problems.append(f"{key}: {rec} != {expect}")
    if problems:
        raise GateError("sanity fields failed: " + "; ".join(problems))
    return out


# --------------------------------------------------------------------------
# storage
# --------------------------------------------------------------------------

def store_raw(db_path: Path, arms: dict[str, list[dict[str, Any]]],
              prereg_sha: str, params: dict[str, Any]) -> None:
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        con.execute("PRAGMA journal_mode=DELETE")
        con.execute(
            "CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.executemany(
            "INSERT INTO meta VALUES (?,?)",
            [("prereg_sha256", prereg_sha),
             ("schema", MANIFEST_SCHEMA),
             ("p_c", repr(float(params["p_c"]))),
             ("equivalence_margin", repr(float(params["equivalence_margin"]))),
             ("reference_D_f", repr(float(params["reference_D_f"]))),
             ("impl_choices", json.dumps(IMPL_CHOICES, sort_keys=True))])
        con.execute(
            "CREATE TABLE arm (mode TEXT, base INTEGER, n_real INTEGER, "
            "size INTEGER, smax BLOB, n_open BLOB, smax_sha256 TEXT, "
            "n_open_sha256 TEXT, field_digest TEXT, PRIMARY KEY "
            "(mode, base, size))")
        for mode, records in arms.items():
            for rec in records:
                # Field digests are per realization for the nested arm and per
                # size for the independent arm; both are flattened to one digest.
                fh = rec["field_hashes"]
                if isinstance(fh, dict):
                    flat = "".join("".join(v) for _s, v in sorted(fh.items()))
                else:
                    flat = "".join(fh)
                digest = sha256_bytes(flat.encode("utf-8"))
                for s in rec["sizes"]:
                    con.execute(
                        "INSERT INTO arm VALUES (?,?,?,?,?,?,?,?,?)",
                        (mode, int(rec["base"]), int(rec["n_real"]), int(s),
                         np.ascontiguousarray(rec["smax"][s], dtype=np.int64).tobytes(),
                         np.ascontiguousarray(rec["n_open"][s], dtype=np.int64).tobytes(),
                         sha256_array(rec["smax"][s]),
                         sha256_array(rec["n_open"][s]),
                         digest))
        con.commit()
    finally:
        con.close()


def load_raw(db_path: Path) -> dict[tuple[str, int, int], tuple[np.ndarray, np.ndarray]]:
    con = sqlite3.connect(db_path)
    out: dict[tuple[str, int, int], tuple[np.ndarray, np.ndarray]] = {}
    try:
        for mode, base, size, sb, nb, sh, nh in con.execute(
                "SELECT mode, base, size, smax, n_open, smax_sha256, n_open_sha256 FROM arm"):
            arr_s = np.frombuffer(sb, dtype=np.int64)
            arr_n = np.frombuffer(nb, dtype=np.int64)
            if sha256_array(arr_s) != sh or sha256_array(arr_n) != nh:
                raise GateError(f"raw round-trip hash mismatch at {mode}/L{base}/s{size}")
            out[(str(mode), int(base), int(size))] = (arr_s.copy(), arr_n.copy())
    finally:
        con.close()
    return out


# --------------------------------------------------------------------------
# analysis
# --------------------------------------------------------------------------

def pair_logdiff(base: int, hi: int, lo: int,
                 idx: np.ndarray | None = None) -> np.ndarray:
    """Realization-level paired differences of log S between two nested sizes.

    ``_SMAX`` is keyed by ``(base, size)``. The same realization index is used
    for both sizes, which is what makes the estimate paired and what the
    bootstrap must preserve.
    """
    a = np.asarray(_SMAX[(base, hi)], dtype=np.float64)
    b = np.asarray(_SMAX[(base, lo)], dtype=np.float64)
    if idx is not None:
        a = a[idx]
        b = b[idx]
    if np.any(a <= 0) or np.any(b <= 0):
        raise GateError(f"non-positive S_max in pair (L{base}:{hi},{lo}); cannot take logs")
    return np.log(a) - np.log(b)


def _pair_sizes(params: dict[str, Any], base: int, type_name: str) -> tuple[int, int]:
    for name, hi, lo in pair_specs(params, base):
        if name == type_name:
            return hi, lo
    raise ConfigError(f"unknown pair type {type_name!r}")


def slope_and_var(base: int, hi: int, lo: int,
                  idx: np.ndarray | None = None) -> tuple[float, float, np.ndarray]:
    d = pair_logdiff(base, hi, lo, idx)
    denom = float(np.log(hi / lo))
    n = d.size
    slope = float(d.mean() / denom)
    var = float(d.var(ddof=1)) / n / (denom ** 2) if n > 1 else 0.0
    return slope, var, d


def delta_and_var(base: int, params: dict[str, Any], type_a: str, type_b: str,
                  idx: np.ndarray | None = None) -> tuple[float, float]:
    """Slope difference for one base, with the paired covariance included.

    The two pair types share every random number inside a realization, so their
    differences are strongly correlated. Ignoring that covariance would
    overstate the uncertainty on beta by a large factor.
    """
    hi_a, lo_a = _pair_sizes(params, base, type_a)
    hi_b, lo_b = _pair_sizes(params, base, type_b)
    s_a, v_a, d_a = slope_and_var(base, hi_a, lo_a, idx)
    s_b, v_b, d_b = slope_and_var(base, hi_b, lo_b, idx)
    m = d_a.size
    cov = float(np.cov(d_a, d_b, ddof=1)[0, 1]) / m if m > 1 else 0.0
    cov /= (np.log(hi_a / lo_a) * np.log(hi_b / lo_b))
    return float(s_a - s_b), float(max(v_a + v_b - 2.0 * cov, 1e-300))


def contrast(params: dict[str, Any], bases: list[int],
             type_a: str, type_b: str,
             draws: int, seed: int) -> dict[str, Any]:
    """Inverse-variance-weighted mean of (slope_a - slope_b) over bases.

    The bootstrap resamples realization indices within each base and reuses the
    same indices for every size of that base, so the nested pairing is preserved
    exactly as in the point estimate.
    """
    n_by_base = {b: int(_SMAX[(b, _pair_sizes(params, b, type_a)[0])].size)
                 for b in bases}
    per_base: dict[int, tuple[float, float]] = {}
    slopes: dict[int, dict[str, float]] = {}
    for b in bases:
        d, v = delta_and_var(b, params, type_a, type_b)
        per_base[b] = (d, v)
        slopes[b] = {}
        for name, hi, lo in pair_specs(params, b):
            slopes[b][name] = slope_and_var(b, hi, lo)[0]

    def pooled(pb: dict[int, tuple[float, float]]) -> float:
        w = {b: 1.0 / max(pb[b][1], 1e-300) for b in bases}
        return float(sum(w[b] * pb[b][0] for b in bases) / sum(w.values()))

    beta = pooled(per_base)

    gen = rng(f"n005-boot-{type_a}-{type_b}", seed)
    reps = np.empty(draws, dtype=np.float64)
    for d in range(draws):
        pb = {}
        for b in bases:
            idx = gen.integers(0, n_by_base[b], size=n_by_base[b])
            pb[b] = delta_and_var(b, params, type_a, type_b, idx)
        reps[d] = pooled(pb)
    return {
        "pair_types": [type_a, type_b],
        "per_base_slopes": {str(b): slopes[b] for b in bases},
        "per_base_delta": {str(b): per_base[b][0] for b in bases},
        "per_base_delta_var": {str(b): per_base[b][1] for b in bases},
        "beta": beta,
        "ci95": [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))],
        "ci90": [float(np.percentile(reps, 5.0)), float(np.percentile(reps, 95.0))],
        "bootstrap_draws": draws,
        "bootstrap_sd": float(reps.std(ddof=1)),
    }


_SMAX: dict[tuple[int, int], np.ndarray] = {}


# --------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------

def run(prereg_path: Path, out_dir: Path) -> int:
    doc = load_prereg(prereg_path)
    params = doc["parameters"]
    prereg_sha = doc["config_sha256"]
    out_dir = Path(out_dir).resolve()
    if out_dir.exists():
        raise N005Error(f"refusing to overwrite existing output directory: {out_dir}")
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = out_dir.parent / f".{out_dir.name}.staging-{os.getpid()}-{uuid.uuid4().hex}"
    staging.mkdir()

    t_start = time.perf_counter()
    sanity = sanity_checks()
    print("  C9 sanity fields: PASS (exact zero and all-open agree in all three implementations)",
          flush=True)

    nested: list[dict[str, Any]] = []
    indep: list[dict[str, Any]] = []
    total_target = sum(int(params["n_real"][str(b)]) for b in params["base_sizes"])
    total_target += int(params["independent_stream_replication_n"]) * len(params["base_sizes"])
    done_est = 0
    for base in params["base_sizes"]:
        base = int(base)
        n_real = int(params["n_real"][str(base)])
        print(f"[nested] base L={base}  n={n_real}", flush=True)
        rec = measure_nested(params, base, n_real, tag="main",
                             c7_n=int(IMPL_CHOICES["c7_subsample_n"]),
                             bfs_bases=[int(b) for b in IMPL_CHOICES["bfs_bases"]],
                             bfs_n=int(IMPL_CHOICES["bfs_n"]))
        nested.append(rec)
        done_est += n_real
        print(f"  -> {rec['seconds']:.1f}s  c7_checked={rec['c7_checked']} "
              f"bfs_checked={rec['bfs_checked']}", flush=True)
    for base in params["base_sizes"]:
        base = int(base)
        n_real = int(params["independent_stream_replication_n"])
        print(f"[independent] base L={base}  n={n_real}", flush=True)
        rec = measure_independent(params, base, n_real, tag="main")
        indep.append(rec)
        done_est += n_real
        print(f"  -> {rec['seconds']:.1f}s", flush=True)

    # ---- gates on the measurement itself
    gate_rows = []

    def gate(name: str, ok: bool, detail: str) -> None:
        gate_rows.append({"gate": name, "pass": bool(ok), "detail": detail})

    c7_total = sum(r["c7_checked"] for r in nested)
    c7_bad = [m for r in nested for m in r["c7_mismatch"]]
    gate("C7_second_implementation", c7_total > 0 and not c7_bad,
         f"{c7_total} cells checked on identical masks, {len(c7_bad)} mismatches")

    bfs_total = sum(r["bfs_checked"] for r in nested)
    bfs_bad = [m for r in nested for m in r["bfs_mismatch"]]
    gate("C8_third_implementation", bfs_total > 0 and not bfs_bad,
         f"{bfs_total} cells checked against from-scratch BFS, {len(bfs_bad)} mismatches")

    mono_bad = []
    for rec in nested:
        base = rec["base"]
        for name, hi, lo in pair_specs(params, base):
            for s_hi, s_lo in ((hi, lo),):
                a = rec["smax"][s_hi]
                b = rec["smax"][s_lo]
                if np.any(b > a):
                    mono_bad.append(f"L{base}:{name}:{int(np.sum(b > a))} violations")
    gate("C3_nested_monotonicity", not mono_bad,
         "S_max must be non-decreasing from the smaller to the larger nested window; "
         + ("no violations" if not mono_bad else "; ".join(mono_bad[:5])))

    bound_bad = []
    for rec in nested:
        for s in rec["sizes"]:
            if np.any(rec["smax"][s] > rec["n_open"][s]) or np.any(rec["smax"][s] > s * s):
                bound_bad.append(f"L{rec['base']}:s{s}")
    gate("C2_mass_bounds", not bound_bad,
         "S_max <= open sites <= L^2 for every entry"
         + ("" if not bound_bad else f"; violations at {bound_bad[:5]}"))

    count_ok = all(len(r["smax"][r["sizes"][0]]) == r["n_real"] for r in nested)
    count_ok = count_ok and all(len(r["smax"][r["sizes"][0]]) ==
                                int(params["n_real"][str(r["base"])]) for r in nested)
    gate("C10_realization_counts", count_ok,
         "nested arm realization counts match the frozen preregistration exactly")

    if not all(g["pass"] for g in gate_rows):
        failed = [g["gate"] for g in gate_rows if not g["pass"]]
        write_json(staging / "gates_failed.json",
                   {"gates": gate_rows, "verdict": "INCONCLUSIVE",
                    "reason": f"engineering gate failure: {failed}"})
        raise GateError(f"measurement gates failed: {failed}")

    # ---- persist raw
    db_path = staging / "EXP-0017_raw.sqlite3"
    store_raw(db_path, {"nested": nested, "independent": indep}, prereg_sha, params)

    # ---- round-trip
    loaded = load_raw(db_path)
    rt_bad = []
    for rec in nested:
        for s in rec["sizes"]:
            key = ("nested", int(rec["base"]), int(s))
            if key not in loaded:
                rt_bad.append(f"missing {key}")
            elif not np.array_equal(loaded[key][0], np.asarray(rec["smax"][s], dtype=np.int64)):
                rt_bad.append(f"mismatch {key}")
    for rec in indep:
        for s in rec["sizes"]:
            key = ("independent", int(rec["base"]), int(s))
            if key not in loaded:
                rt_bad.append(f"missing {key}")
            elif not np.array_equal(loaded[key][0], np.asarray(rec["smax"][s], dtype=np.int64)):
                rt_bad.append(f"mismatch {key}")
    if rt_bad:
        raise GateError(f"raw round-trip failed: {rt_bad[:5]}")
    gate_rows.append({"gate": "C1_raw_round_trip", "pass": True,
                      "detail": f"{len(loaded)} stored arrays reloaded bit-exactly"})

    # ---- manifest
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "experiment_id": "EXP-0017",
        "question_id": "Q-P009",
        "audit_finding_id": "N-005",
        "prereg_sha256": prereg_sha,
        "prereg_path": str(Path(prereg_path).resolve()),
        "p_c": float(params["p_c"]),
        "equivalence_margin": float(params["equivalence_margin"]),
        "reference_D_f": float(params["reference_D_f"]),
        "impl_choices": IMPL_CHOICES,
        "raw_sqlite_sha256": sha256_file(db_path),
        "raw_sqlite_bytes": db_path.stat().st_size,
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "structure_four_connectivity": STRUCT4.astype(int).tolist(),
        "sanity_fields": sanity,
        "gates": gate_rows,
        "arms": {
            "nested": [{"base": r["base"], "n_real": r["n_real"], "sizes": r["sizes"],
                        "field_digest": sha256_bytes("".join(r["field_hashes"]).encode("utf-8")),
                        "seconds": r["seconds"]} for r in nested],
            "independent": [{"base": r["base"], "n_real": r["n_real"], "sizes": r["sizes"],
                             "seconds": r["seconds"]} for r in indep],
        },
        "wall_seconds": time.perf_counter() - t_start,
        "numpy_version": np.__version__,
        "scipy_version": __import__("scipy").__version__,
        "python_version": sys.version.split()[0],
    }
    manifest["manifest_sha256"] = sha256_bytes(
        json.dumps(manifest, allow_nan=False, ensure_ascii=False,
                   separators=(",", ":"), sort_keys=True).encode("utf-8"))
    write_json(staging / "EXP-0017_manifest.json", manifest)

    shutil.rmtree(out_dir, ignore_errors=True)
    staging.rename(out_dir)
    print(f"\nraw artifact + manifest written to {out_dir}")
    print(f"total wall time {manifest['wall_seconds']:.1f}s")
    return 0


def contradicts(primary_verdict: str, primary_beta: float, indep_beta: float,
                indep_ci95: list[float], margin: float) -> tuple[bool, str]:
    """Operational definition of "contradicts the primary verdict".

    A weaker cross-check can only CONTRADICT the primary if it *resolves* the
    contrast in the opposite direction. An arm that excludes nothing is
    underpowered, not contradictory, and must not void a result that the primary
    arm resolved. This distinction was fixed before execution and logged in the
    hash chain; see CONFIG/changes.jsonl.
    """
    indep_excludes_zero = bool(indep_ci95[0] > 0 or indep_ci95[1] < 0)
    if not indep_excludes_zero:
        return False, ("independent arm does not exclude zero; reported as "
                       "underpowered rather than contradictory")
    if primary_verdict == "LATTICE_ARTIFACT_UNSUPPORTED":
        if abs(indep_beta) > margin:
            return True, ("primary demonstrated equivalence at the margin but the "
                          "independent arm resolves an effect larger than the margin")
        return False, "independent arm excludes zero but stays inside the margin"
    if primary_verdict == "LATTICE_ARTIFACT_SUPPORTED":
        if (primary_beta > 0) != (indep_beta > 0):
            return True, "independent arm resolves the opposite sign"
        return False, "independent arm resolves the same sign; consistent"
    return False, "primary is INCONCLUSIVE_BY_RESOLUTION; a cross-check cannot overturn it"


def decide_verdict(beta: float, ci90: list[float], ci95: list[float],
                   margin: float) -> tuple[str, bool, bool]:
    """Frozen decision rule. Returns (verdict, equivalence_demonstrated, excludes_zero).

    Kept as a pure function so the thresholds are unit-testable without running
    a 45-minute experiment.
    """
    equivalence = bool(ci90[0] > -margin and ci90[1] < margin)
    excludes_zero = bool(ci95[0] > 0 or ci95[1] < 0)
    if equivalence:
        return "LATTICE_ARTIFACT_UNSUPPORTED", True, excludes_zero
    if excludes_zero and abs(beta) > margin:
        return "LATTICE_ARTIFACT_SUPPORTED", False, True
    return "INCONCLUSIVE_BY_RESOLUTION", False, excludes_zero


def slope_weights(sizes: list[int]) -> np.ndarray:
    """OLS slope functional weights: w_j = (x_j - xbar) / sum((x - xbar)^2).

    These sum to zero, which is what makes the arm-to-arm difference cancel the
    large marginal fluctuation of log S_max.
    """
    x = np.log(np.asarray(sizes, dtype=float))
    xc = x - x.mean()
    denom = float((xc ** 2).sum())
    if denom <= 0:
        raise ConfigError("slope weights are degenerate: ladder sizes are identical")
    return xc / denom


def ladder_contrast(raw: dict, bases: list[int], draws: int, seed: int,
                    offset: int = 1, mode: str = "nested") -> dict[str, Any]:
    """PRIMARY estimator: D_f(P2 ladder) - D_f(non-P2 ladder).

    Each arm's slope is a linear functional of the mean log S_max at its ladder
    sizes. Size ``base - offset`` is the nested partner of ``base`` and comes
    from the same field, so both arms share every realization.

    Uncertainty is a paired bootstrap: realization indices are resampled within
    each base and reused for both sizes, so the nested pairing is preserved and
    the covariance structure is carried by the resampling rather than by an
    analytic formula. Nothing is divided by log(1 + 1/L), which is what made the
    superseded local-slope estimator noise-dominated.
    """
    p2_sizes = [int(b) for b in bases]
    np2_sizes = [int(b) - offset for b in bases]
    wp = slope_weights(p2_sizes)
    wn = slope_weights(np2_sizes)
    p2 = [np.log(np.asarray(raw[(mode, b, b)][0], dtype=np.float64)) for b in p2_sizes]
    np2 = [np.log(np.asarray(raw[(mode, b, b - offset)][0], dtype=np.float64))
           for b in p2_sizes]
    for arr in p2 + np2:
        if np.any(arr <= 0):
            raise GateError("non-positive S_max in the ladder contrast")

    def point(mm_p2, mm_np2):
        return float(np.dot(wp, mm_p2) - np.dot(wn, mm_np2))

    beta = point([a.mean() for a in p2], [a.mean() for a in np2])
    gen = rng(f"n005-ladder-boot-{offset}", seed)
    reps = np.empty(draws, dtype=np.float64)
    for d in range(draws):
        mm_p2, mm_np2 = [], []
        for a, b in zip(p2, np2):
            k = min(a.size, b.size)
            idx = gen.integers(0, k, size=k)
            mm_p2.append(a[idx].mean())
            mm_np2.append(b[idx].mean())
        reps[d] = point(mm_p2, mm_np2)
    per_base = []
    for a, b, sp, sn in zip(p2, np2, p2_sizes, np2_sizes):
        d = a - b
        per_base.append({
            "sizes": [sn, sp],
            "mean_log_s_p2": float(a.mean()),
            "mean_log_s_nonp2": float(b.mean()),
            "paired_difference": float(d.mean()),
            "paired_sd": float(d.std(ddof=1)),
            "n": int(d.size),
        })
    return {
        "estimator": "difference_of_two_global_ols_slope_functionals",
        "arm_mode": mode,
        "p2_ladder": p2_sizes,
        "nonp2_ladder": np2_sizes,
        "p2_slope_weights": [float(v) for v in wp],
        "nonp2_slope_weights": [float(v) for v in wn],
        "D_f_p2_ladder": float(np.dot(wp, [a.mean() for a in p2])),
        "D_f_nonp2_ladder": float(np.dot(wn, [a.mean() for a in np2])),
        "beta": beta,
        "ci90": [float(np.percentile(reps, 5.0)), float(np.percentile(reps, 95.0))],
        "ci95": [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))],
        "bootstrap_draws": draws,
        "bootstrap_sd": float(reps.std(ddof=1)),
        "per_base": per_base,
    }


def ladder_contrast_synthetic_check() -> dict[str, Any]:
    """Self-check of the primary estimator on synthetic ladders.

    Confirms a null power law returns zero and that an injected exponent offset
    is recovered. Recorded in the summary so the estimator's validity is
    evidenced in the artifact itself, not only in the test suite.
    """
    bases = [128, 256, 512, 1024]
    wp = slope_weights(bases)
    wn = slope_weights([b - 1 for b in bases])
    d_f = 91.0 / 48.0
    out = {}
    for label, offset, correction in (("null", 0.0, 0.0),
                                      ("injected_plus", 0.0265, 0.0),
                                      ("injected_minus", -0.0265, 0.0),
                                      ("shared_correction", 0.0, 0.30)):
        gen = np.random.default_rng(4242)
        common = gen.normal(0.0, 0.40, 120)
        p2, np2 = [], []
        for b in bases:
            p2.append((d_f + offset) * np.log(b) + correction * np.log(b) ** 2 + common)
            np2.append(d_f * np.log(b - 1) + correction * np.log(b - 1) ** 2 + common)
        beta = float(np.dot(wp, [a.mean() for a in p2])
                     - np.dot(wn, [a.mean() for a in np2]))
        out[label] = {"beta": beta, "injected_exponent_offset": offset,
                      "injected_correction": correction}
    return out


def analyze(prereg_path: Path, artifact_dir: Path) -> int:
    global _SMAX
    doc = load_prereg(prereg_path)
    params = doc["parameters"]
    artifact_dir = Path(artifact_dir).resolve()
    manifest = load_strict_json(artifact_dir / "EXP-0017_manifest.json")
    if manifest["prereg_sha256"] != doc["config_sha256"]:
        raise ConfigError("artifact was produced under a different preregistration")
    raw = load_raw(artifact_dir / "EXP-0017_raw.sqlite3")

    bases = [int(b) for b in params["base_sizes"]]
    draws = int(IMPL_CHOICES["bootstrap_draws"])
    seed = int(IMPL_CHOICES["bootstrap_seed"])

    # primary (nested) arm
    _SMAX = {(b, s): raw[("nested", b, s)][0] for b in bases
             for (m, bb, s) in raw if m == "nested" and bb == b}
    primary = ladder_contrast(raw, bases, draws, seed)
    primary["synthetic_self_check"] = ladder_contrast_synthetic_check()
    # superseded estimator, retained as a labelled diagnostic only
    superseded = contrast(params, bases, "p2_anchored", "nonp2_anchored", draws, seed)
    nullc = contrast(params, bases, "nonp2_anchored", "nonp2_null_control", draws, seed + 1)

    # independent-stream arm, analysed with the same corrected estimator
    raw_indep = {k: v for k, v in raw.items() if k[0] == "independent"}
    indep = ladder_contrast(raw_indep, bases, draws, seed + 2, mode="independent")
    _SMAX = {(b, s): raw_indep[("independent", b, s)][0] for b in bases
             for (m, bb, s) in raw_indep if bb == b}
    indep_local = contrast(params, bases, "p2_anchored", "nonp2_anchored", draws, seed + 5)

    # absolute D_f over the nested arm, all sampled sizes pooled
    _SMAX = {(b, s): raw[("nested", b, s)][0] for b in bases
             for (m, bb, s) in raw if m == "nested" and bb == b}
    abs_fit = absolute_D_f(params, bases, raw, draws, seed + 3)

    ladder = ladder_report(params, bases, raw)

    margin = float(params["equivalence_margin"])
    dref = float(params["reference_D_f"])
    beta = primary["beta"]
    ci90 = primary["ci90"]
    ci95 = primary["ci95"]
    verdict, equiv, excludes_zero = decide_verdict(beta, ci90, ci95, margin)

    sens = {
        "independent_arm_beta": indep["beta"],
        "independent_arm_ci95": indep["ci95"],
        "independent_arm_ci90": indep["ci90"],
        "independent_arm_verdict": decide_verdict(
            indep["beta"], indep["ci90"], indep["ci95"], margin)[0],
        "independent_arm_local_slope_beta": indep_local["beta"],
        "null_control_beta": nullc["beta"],
        "null_control_ci95": nullc["ci95"],
        "null_control_note": (
            "the preregistered smooth-artifact control, computed with the "
            "SUPERSEDED local-slope estimator. It is retained because its "
            "magnitude exceeding the superseded primary contrast is the "
            "diagnostic that identified the estimator defect; it is not a valid "
            "effect-size estimate in its own right"
        ),
        "beta_exceeds_null_control": abs(beta) > max(abs(nullc["ci95"][0]),
                                                     abs(nullc["ci95"][1])),
        "beta_over_historical_deficit": beta / float(params["historical_p2_deficit"]),
    }
    contra, contra_reason = contradicts(verdict, beta, indep["beta"], indep["ci95"], margin)
    sens["independent_arm_contradicts"] = contra
    sens["independent_arm_contradiction_reason"] = contra_reason
    if contra or (verdict == "LATTICE_ARTIFACT_SUPPORTED"
                  and not sens["beta_exceeds_null_control"]):
        verdict = "WINDOW_OR_ESTIMATOR_SENSITIVE"
        sens["sensitivity_trigger"] = (
            contra_reason if contra
            else "beta does not exceed the smooth-artifact null control")

    gates_ok = all(g["pass"] for g in manifest["gates"])
    summary = {
        "summary_schema": SUMMARY_SCHEMA,
        "experiment_id": "EXP-0017",
        "question_id": "Q-P009",
        "audit_finding_id": "N-005",
        "prereg_sha256": doc["config_sha256"],
        "manifest_sha256": manifest["manifest_sha256"],
        "verdict": verdict if gates_ok else "INCONCLUSIVE",
        "verdict_rule": params["decision_rule"],
        "primary_statistic": primary,
        "superseded_estimator_diagnostic": {
            "status": "INVALID_NOISE_AMPLIFIED_DO_NOT_USE_AS_AN_EFFECT_ESTIMATE",
            "reason": (
                "divides the paired difference by log(hi/lo) ~ 1e-3 at L=1024, "
                "amplifying noise by ~1e3; retained as evidence only"
            ),
            "result": superseded,
        },
        "estimator_amendment": {
            "change_log": "CONFIG/changes.jsonl",
            "superseded_summary": "EXP-0017_summary_v1_local_slope_SUPERSEDED.json",
            "note": (
                "the primary statistic was replaced after the first analysis was "
                "found to be noise-dominated; the raw artifact was not modified "
                "and no new data was collected for the change"
            ),
        },
        "equivalence_margin": margin,
        "equivalence_demonstrated": bool(equiv),
        "ci95_excludes_zero": bool(excludes_zero),
        "reference_D_f": dref,
        "null_control": nullc,
        "sensitivity": sens,
        "absolute_D_f": abs_fit,
        "ladder": ladder,
        "gates": manifest["gates"],
        "impl_choices": IMPL_CHOICES,
        "known_limitations": params["known_limitations"],
        "claim_guards": params["claim_guards"],
        "novelty_claim": False,
    }
    write_json(artifact_dir / "EXP-0017_summary.json", summary)
    print(json.dumps({
        "verdict": summary["verdict"],
        "beta": primary["beta"],
        "ci90": primary["ci90"],
        "ci95": primary["ci95"],
        "D_f_p2_ladder": primary["D_f_p2_ladder"],
        "D_f_nonp2_ladder": primary["D_f_nonp2_ladder"],
        "margin": margin,
        "synthetic_self_check": {k: round(v["beta"], 5)
                                 for k, v in primary["synthetic_self_check"].items()},
        "independent_beta": indep["beta"],
        "independent_ci90": indep["ci90"],
        "absolute_D_f": abs_fit["D_f"],
        "absolute_D_f_ci95": abs_fit["ci95"],
    }, indent=2))
    return 0


def absolute_D_f(params, bases, raw, draws, seed) -> dict[str, Any]:
    """Slope of log S_max vs log L over every sampled nested size."""
    xs, ys, groups = [], [], []
    for b in bases:
        for (m, bb, s) in sorted(raw):
            if m != "nested" or bb != b:
                continue
            arr = raw[(m, bb, s)][0].astype(np.float64)
            xs.append(np.full(arr.shape, np.log(s)))
            ys.append(np.log(arr))
            groups.append((b, s))
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    A = np.vstack([np.ones_like(x), x]).T
    coef, *_ = np.linalg.lstsq(A, y, rcond=None)
    gen = rng("n005-absdf", seed)
    idx_b = gen.integers(0, x.size, size=(draws, x.size))
    reps = np.empty(draws)
    for d in range(draws):
        i = idx_b[d]
        Xi = x[i]
        yi = y[i]
        Ai = np.vstack([np.ones_like(Xi), Xi]).T
        c, *_ = np.linalg.lstsq(Ai, yi, rcond=None)
        reps[d] = c[1]
    ref = float(params["reference_D_f"])
    return {
        "sizes": sorted({s for _, s in groups}),
        "D_f": float(coef[1]),
        "ci95": [float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5))],
        "reference": ref,
        "deviation": float(coef[1] - ref),
        "reference_inside_ci95": bool(np.percentile(reps, 2.5) <= ref <= np.percentile(reps, 97.5)),
        "note": ("pooled over every sampled nested size; the primary claim of this "
                 "experiment is the power-of-two contrast, not this absolute value"),
    }


def ladder_report(params, bases, raw) -> dict[str, Any]:
    """Local slopes along the 2-adic ladder, reported descriptively."""
    out = []
    for b in [int(x) for x in params["ladder_bases"]]:
        sizes = sorted(s for (m, bb, s) in raw if m == "nested" and bb == b)
        series = {}
        for s in sizes:
            series[s] = np.log(raw[("nested", b, s)][0].astype(np.float64))
        rows = []
        for lo, hi in zip(sizes[:-1], sizes[1:]):
            d = series[hi] - series[lo]
            rows.append({
                "sizes": [lo, hi],
                "v2": [v2(lo), v2(hi)],
                "local_slope": float(d.mean() / np.log(hi / lo)),
                "sd": float(d.std(ddof=1)),
                "n": int(d.size),
            })
        out.append({"base": b, "pairs": rows})
    return {"ladder_bases": [int(x) for x in params["ladder_bases"]],
            "note": IMPL_CHOICES["ladder_pairs"], "by_base": out}


def v2(n: int) -> int:
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k


def validate(prereg_path: Path, artifact_dir: Path) -> int:
    doc = load_prereg(prereg_path)
    artifact_dir = Path(artifact_dir).resolve()
    manifest = load_strict_json(artifact_dir / "EXP-0017_manifest.json")
    problems = []
    if manifest["prereg_sha256"] != doc["config_sha256"]:
        problems.append("preregistration hash mismatch")
    db = artifact_dir / "EXP-0017_raw.sqlite3"
    if sha256_file(db) != manifest["raw_sqlite_sha256"]:
        problems.append("raw sqlite hash mismatch")
    payload = dict(manifest)
    recorded = payload.pop("manifest_sha256", None)
    actual = sha256_bytes(json.dumps(payload, allow_nan=False, ensure_ascii=False,
                                     separators=(",", ":"), sort_keys=True).encode("utf-8"))
    if recorded != actual:
        problems.append("manifest self-hash mismatch")
    try:
        load_raw(db)
    except GateError as exc:
        problems.append(str(exc))
    summary_path = artifact_dir / "EXP-0017_summary.json"
    verdict = None
    if summary_path.exists():
        verdict = load_strict_json(summary_path).get("verdict")
    for p in problems:
        print(f"FAIL {p}")
    if not problems:
        print(f"PASS artifact validated; verdict={verdict}")
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--prereg", type=Path, default=PREREG)
    r.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("analyze")
    a.add_argument("--prereg", type=Path, default=PREREG)
    a.add_argument("--artifact", type=Path, required=True)
    v = sub.add_parser("validate")
    v.add_argument("--prereg", type=Path, default=PREREG)
    v.add_argument("--artifact", type=Path, required=True)
    args = ap.parse_args()
    try:
        if args.cmd == "run":
            return run(args.prereg, args.out)
        if args.cmd == "analyze":
            return analyze(args.prereg, args.artifact)
        return validate(args.prereg, args.artifact)
    except N005Error as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
