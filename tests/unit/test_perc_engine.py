"""Regression tests for dimension-explicit percolation spanning."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

LAB_ROOT = Path(__file__).resolve().parents[2]
ENGINE = (
    LAB_ROOT
    / "03_INVESTIGATIONS"
    / "PHYSICS"
    / "percolation"
    / "ENGINE"
)
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

import perc_engine as pe  # noqa: E402

C7_PATH = (
    LAB_ROOT
    / "03_INVESTIGATIONS"
    / "PHYSICS"
    / "percolation_3d"
    / "CODE"
    / "REPLICATION"
    / "independent_check_EXP0011.py"
)
C7_SPEC = importlib.util.spec_from_file_location("perc3d_c7", C7_PATH)
assert C7_SPEC is not None and C7_SPEC.loader is not None
c7 = importlib.util.module_from_spec(C7_SPEC)
C7_SPEC.loader.exec_module(c7)


def test_2d_spanning_contract_is_unchanged():
    labels = np.arange(16, dtype=np.int64)
    labels[[0, 1, 2, 3, 12, 13, 14, 15]] = 16  # y=0 -> y=3
    labels[[4, 5, 6, 7]] = 17                  # x=0 -> x=3

    assert pe.spanning_flags(labels, 16, 4, ndim=2) == (True, True)


def test_3d_opposite_z_path_is_vertical_but_old_slice_path_is_not():
    L = 4
    N = L**3
    z_path = np.asarray([1 + L * 2 + L * L * z for z in range(L)])
    labels = np.arange(N, dtype=np.int64)
    labels[z_path] = N

    assert pe.spanning_flags(labels, N, L, ndim=3) == (True, False)

    slice_path = np.asarray([1 + L * y for y in range(L)])
    labels = np.arange(N, dtype=np.int64)
    labels[slice_path] = N

    assert pe.spanning_flags(labels, N, L, ndim=3) == (False, False)


def test_3d_horizontal_span_uses_full_volume_x_planes():
    L = 4
    N = L**3
    x_path = np.asarray([20, 21, 22, 23])  # x=0..3, y=1, z=1
    labels = np.arange(N, dtype=np.int64)
    labels[x_path] = N

    assert pe.spanning_flags(labels, N, L, ndim=3) == (False, True)


def test_3d_rejects_non_cubic_graph_and_invalid_dimension():
    labels = np.arange(16, dtype=np.int64)
    with pytest.raises(ValueError, match="N=L\\^3"):
        pe.spanning_flags(labels, 16, 4, ndim=3)
    with pytest.raises(ValueError, match="ndim must be"):
        pe.spanning_flags(np.arange(16), 16, 4, ndim=4)


def test_run_span_cell_edges_propagates_cubic_boundaries(monkeypatch):
    L = 4
    N = L**3
    src, dst, observed_N = pe.cubic_lattice_3d(L)
    assert observed_N == N
    path = np.asarray([1 + L * 2 + L * L * z for z in range(L)])
    uniforms = np.ones(N, dtype=float)
    uniforms[path] = 0.0  # site is open when uniform < p

    class FakeGenerator:
        def random(self, size):
            assert size == N
            return uniforms.copy()

    monkeypatch.setattr(pe, "cell_rng", lambda label, seed: FakeGenerator())
    result = pe.run_span_cell_edges(
        src,
        dst,
        N,
        L,
        p=0.5,
        n_real=1,
        seed=1,
        label="synthetic-3d-path",
        semantics="site",
        want_cluster_sizes=True,
        ndim=3,
    )

    assert result["k_v"] == 1
    assert result["k_h"] == 0
    assert result["n"] == 1
    assert result["ndim"] == 3
    assert len(result["cluster_sizes"]) == 1
    assert isinstance(result["cluster_sizes"][0], np.ndarray)
    sizes = result["cluster_sizes"][0]
    assert sizes.tolist() == [4]


def test_independent_c7_uses_opposite_planes_and_matches_primary_stream():
    assert c7.synthetic_self_test()["pass"] is True
    L = 3
    src, dst, N = pe.cubic_lattice_3d(L)
    for seed in (11, 29, 47):
        label = "c7-same-stream-smoke"
        primary = pe.run_span_cell_edges(
            src,
            dst,
            N,
            L,
            p=0.3116079,
            n_real=1,
            seed=seed,
            label=label,
            semantics="site",
            ndim=3,
        )
        independent = c7.uf_span(
            src, dst, N, L, 0.3116079, 1, seed, label
        )
        assert independent == (primary["k_v"], primary["k_h"])
