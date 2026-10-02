"""Corrected EXP-0011/0013 C7 implementation cross-check for cubic spanning.

The union-find code specifies opposite 3D planes independently of
``perc_engine.spanning_flags``. It uses the same named streams as the primary
runner when a config is supplied, so this is an implementation cross-check on
identical Monte Carlo realizations—not independent experimental replication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CODE_DIR = HERE.parent
QDIR = CODE_DIR.parent
PHYSICS = QDIR.parent
ENGINE = PHYSICS / "percolation" / "ENGINE"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

import perc_engine as pe  # noqa: E402

class UF:
    __slots__ = ("parent", "size")

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

    def find(self, a):
        parent = self.parent
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(self, a, b):
        root_a, root_b = self.find(a), self.find(b)
        if root_a == root_b:
            return
        if self.size[root_a] < self.size[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]


def _plane_roots(uf: UF, node_ids) -> set[int]:
    return {uf.find(int(node_id)) for node_id in node_ids}


def independent_cubic_spans(uf: UF, L: int) -> tuple[bool, bool]:
    """Check z=0/z=L-1 and full-volume x=0/x=L-1 independently of SciPy labels."""
    L = int(L)
    z_low = [x + L * y for y in range(L) for x in range(L)]
    z_high = [node + L * L * (L - 1) for node in z_low]
    x_low = [L * y + L * L * z for z in range(L) for y in range(L)]
    x_high = [(L - 1) + L * y + L * L * z for z in range(L) for y in range(L)]
    return (
        bool(_plane_roots(uf, z_low) & _plane_roots(uf, z_high)),
        bool(_plane_roots(uf, x_low) & _plane_roots(uf, x_high)),
    )


def union_find_components(src, dst, N: int, open_nodes) -> UF:
    """Build components for open sites with literal nearest-neighbour edges."""
    e_ok = open_nodes[src] & open_nodes[dst]
    uf = UF(int(N))
    for edge_src, edge_dst in zip(src[e_ok], dst[e_ok]):
        uf.union(int(edge_src), int(edge_dst))
    return uf


def uf_span(src, dst, N, L, p, n_real, seed, label) -> tuple[int, int]:
    """Independent same-stream spanning count using one realization at a time."""
    generator = pe.cell_rng(label, seed)
    k_v = 0
    k_h = 0
    for _ in range(int(n_real)):
        open_nodes = generator.random(int(N)) < p
        uf = union_find_components(src, dst, N, open_nodes)
        span_v, span_h = independent_cubic_spans(uf, L)
        k_v += int(span_v)
        k_h += int(span_h)
    return k_v, k_h


def synthetic_self_test() -> dict:
    """Lock the intended estimand before any stochastic comparison."""
    L = 4
    src, dst, N = pe.cubic_lattice_3d(L)
    cases = {}

    z_path = np.asarray([1 + L * 2 + L * L * z for z in range(L)])
    open_nodes = np.zeros(N, dtype=bool)
    open_nodes[z_path] = True
    cases["opposite_z_path"] = independent_cubic_spans(
        union_find_components(src, dst, N, open_nodes), L
    )

    old_slice_path = np.asarray([1 + L * y for y in range(L)])
    open_nodes = np.zeros(N, dtype=bool)
    open_nodes[old_slice_path] = True
    cases["old_z0_slice_path"] = independent_cubic_spans(
        union_find_components(src, dst, N, open_nodes), L
    )

    x_path = np.asarray([20, 21, 22, 23])
    open_nodes = np.zeros(N, dtype=bool)
    open_nodes[x_path] = True
    cases["full_volume_x_path"] = independent_cubic_spans(
        union_find_components(src, dst, N, open_nodes), L
    )

    expected = {
        "opposite_z_path": (True, False),
        "old_z0_slice_path": (False, False),
        "full_volume_x_path": (False, True),
    }
    return {
        "pass": cases == expected,
        "observed": {key: list(value) for key, value in cases.items()},
        "expected": {key: list(value) for key, value in expected.items()},
    }


def _cell_label(config: dict, L: int, kind: str) -> str:
    params = config["parameters"]
    token = config.get("p_canon_token") or params.get("p_canon_token")
    if token is None:
        token = "p" + str(int(round(float(params["p_c"]) * 10_000_000)))
    pattern = params["rng_label_pattern"]
    token = str(token)
    if f"p<pcanon>" in pattern and token.startswith("p"):
        pattern = pattern.replace("p<pcanon>", token)
    else:
        pattern = pattern.replace("<pcanon>", token)
    return pattern.replace("<L>", str(L)).replace("<kind>", kind)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _realization_seed(config: dict, L: int, realization: int) -> int:
    params = config["parameters"]
    return int(
        config["seed"]
        + L * int(params["l_seed_multiplier"])
        + realization * int(params["r_seed_stride"])
    )


def _load_config(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    config = json.loads(raw.decode("utf-8"))
    if config.get("parameters", {}).get("system") != "site_cubic_3d":
        raise ValueError("C7 requires a site_cubic_3d preregistration")
    recorded = config.get("config_sha256")
    payload = dict(config)
    payload.pop("config_sha256", None)
    canonical = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    actual = hashlib.sha256(canonical).hexdigest()
    if recorded != actual:
        raise ValueError("config_sha256 mismatch; refusing C7")
    params = config["parameters"]
    for key in ("l_seed_multiplier", "p_seed_stride", "r_seed_stride"):
        if int(params.get(key, 0)) <= 0:
            raise ValueError(f"C7 requires positive config seed field {key}")
    return config, actual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--n-real", type=int, default=50)
    parser.add_argument("--L", type=int, nargs="*", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="new JSON report path; must remain under this replication directory",
    )
    args = parser.parse_args()

    config, config_sha256 = _load_config(args.config.resolve())
    parameters = config["parameters"]
    L_list = args.L if args.L is not None else parameters["width_L_list"]
    if args.n_real <= 0:
        raise ValueError("--n-real must be positive")
    missing = [L for L in L_list if f"L{L}" not in parameters["width_grid"]]
    if missing:
        raise ValueError(
            "Config has no width_grid entry for "
            f"L={missing}; available={sorted(parameters['width_grid'])}"
        )

    self_test = synthetic_self_test()
    if not self_test["pass"]:
        print(f"[C7-3D] synthetic self-test FAIL: {self_test}", flush=True)
        return 2

    p_c = float(parameters["p_c"])
    cells = {}
    all_pass = self_test["pass"]
    for L in L_list:
        src, dst, N = pe.cubic_lattice_3d(int(L))
        label = _cell_label(config, int(L), "exp")
        print(
            f"[C7-3D] L={L}: {args.n_real} same-stream implementation cells",
            flush=True,
        )
        for index in range(args.n_real):
            seed = _realization_seed(config, int(L), index)
            lab = pe.run_span_cell_edges(
                src,
                dst,
                N,
                int(L),
                p_c,
                1,
                seed,
                label,
                semantics="site",
                ndim=3,
            )
            independent = uf_span(
                src, dst, N, int(L), p_c, 1, seed, label
            )
            observed = (int(lab["k_v"]), int(lab["k_h"]))
            pass_cell = observed == independent
            all_pass = all_pass and pass_cell
            cells[f"L{L}-cell{index}"] = {
                "L": int(L),
                "cell": index,
                "seed": seed,
                "label": label,
                "pass": pass_cell,
                "lab_k_v": observed[0],
                "lab_k_h": observed[1],
                "independent_k_v": independent[0],
                "independent_k_h": independent[1],
            }

    report = {
        "schema": "q-p008/c7-cubic-union-find/v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "experiment": config["experiment_id"],
        "question": config["question_id"],
        "hypothesis": config["hypothesis_id"],
        "control": "C7",
        "config_path": str(args.config.resolve()),
        "config_sha256": config_sha256,
        "script_path": str(Path(__file__).resolve()),
        "script_sha256": _sha256_file(Path(__file__).resolve()),
        "engine_path": str(Path(pe.__file__).resolve()),
        "engine_sha256": _sha256_file(Path(pe.__file__).resolve()),
        "p_c": p_c,
        "L_list": [int(L) for L in L_list],
        "n_real_per_L": int(args.n_real),
        "estimand": {
            "k_v": "one component intersects z=0 and z=L-1",
            "k_h": "one component intersects x=0 and x=L-1 across the full volume",
        },
        "independent_implementation": "literal pure-Python union-find and plane construction",
        "same_stream_implementation_crosscheck": True,
        "independent_experimental_replication": False,
        "synthetic_self_test": self_test,
        "all_pass": bool(all_pass),
        "cells": cells,
    }
    if args.output is None:
        output = HERE / (
            f"C7_{config['experiment_id']}_{config_sha256[:12]}_corrected_report.json"
        )
    else:
        output = args.output.expanduser().resolve()
        if output == HERE or HERE not in output.parents:
            raise ValueError(
                "C7 output must be a new file below the replication directory"
            )
    if output.exists():
        raise FileExistsError(f"refusing to overwrite C7 evidence: {output}")
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    print(
        f"[C7-3D] {'PASS' if all_pass else 'FAIL'} -> {output}",
        flush=True,
    )
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
