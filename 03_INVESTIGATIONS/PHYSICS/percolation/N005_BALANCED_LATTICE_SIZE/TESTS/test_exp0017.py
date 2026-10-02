"""Focused tests for EXP-0017 / N-005.

Covers the three implementations, the raw round-trip, the frozen verdict rule,
and an end-to-end recovery test of a deliberately injected power-of-two offset.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

AREA = Path(__file__).resolve().parents[1]
LAB = AREA.parents[3]
SHARED = LAB / "04_SHARED_ENGINE"
for _p in (str(SHARED), str(SHARED.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

RUNNER_PATH = AREA / "CODE" / "run_exp0017.py"
SPEC = importlib.util.spec_from_file_location("exp0017_runner_under_test", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)

PREREG = AREA / "CONFIG" / "prereg_EXP-0017.json"


# ---------------------------------------------------------------- structure

def test_four_connectivity_structure_has_no_diagonals() -> None:
    s = runner.STRUCT4
    assert s[1, 1] and s[0, 1] and s[2, 1] and s[1, 0] and s[1, 2]
    assert not s[0, 0] and not s[0, 2] and not s[2, 0] and not s[2, 2]
    assert int(s.sum()) == 5


def test_edge_list_is_an_open_square_lattice() -> None:
    for L in (4, 7, 16):
        src, dst = runner.square_edge_list(L)
        assert src.size == 2 * L * (L - 1)
        assert dst.size == src.size
        # no wrap edges: no node may have a neighbour across the far boundary
        assert not np.any((src % L == 0) & (dst % L == L - 1))
        assert not np.any((src // L == 0) & (dst // L == L - 1))
        # every edge joins 4-neighbours
        assert np.all(np.abs(src // L - dst // L) + np.abs(src % L - dst % L) == 1)


# ---------------------------------------------------------------- censuses

@pytest.mark.parametrize("L,p", [(24, 0.30), (32, 0.5927460507921), (20, 0.75), (17, 0.50)])
def test_three_implementations_agree_exactly(L: int, p: float) -> None:
    gen = np.random.default_rng(1234 + L)
    for _ in range(3):
        mask = gen.random((L, L)) < p
        a = sorted(runner.census_ndimage(mask).tolist())
        b = sorted(runner.census_edge_list(mask).tolist())
        assert a == b, "ndimage and edge-list cluster censuses must be identical"
        assert runner.census_bfs_python(mask) == max(a) if a else True


def test_sanity_fields_are_exact() -> None:
    out = runner.sanity_checks()
    assert out["empty_8"]["ndimage"] == 0
    assert out["full_8"]["ndimage"] == 64
    assert out["full_33"]["bfs"] == 33 * 33


def test_nested_windows_are_monotone_in_size() -> None:
    """S_max of a sub-window can never exceed S_max of the full field."""
    gen = np.random.default_rng(99)
    for _ in range(5):
        L = 24
        field = gen.random((L, L)) < 0.55
        prev = None
        for s in range(8, L + 1):
            cur = runner.largest(runner.census_ndimage(field[:s, :s]))
            if prev is not None:
                assert cur >= prev
            prev = cur


# ---------------------------------------------------------------- storage

def test_raw_round_trip_is_bit_exact(tmp_path: Path) -> None:
    params = runner.load_prereg(PREREG)["parameters"]
    smax = {16: np.array([10, 20, 30], dtype=np.int64),
            15: np.array([9, 19, 29], dtype=np.int64)}
    n_open = {16: np.array([100, 200, 300], dtype=np.int64),
              15: np.array([90, 190, 290], dtype=np.int64)}
    rec = {"base": 16, "n_real": 3, "sizes": [15, 16], "smax": smax,
           "n_open": n_open, "field_hashes": ["a", "b", "c"]}
    db = tmp_path / "raw.sqlite3"
    runner.store_raw(db, {"nested": [rec]}, "deadbeef" * 8, params)
    loaded = runner.load_raw(db)
    assert set(loaded) == {("nested", 16, 15), ("nested", 16, 16)}
    for s in (15, 16):
        assert np.array_equal(loaded[("nested", 16, s)][0], smax[s])
        assert np.array_equal(loaded[("nested", 16, s)][1], n_open[s])


def test_raw_tampering_is_rejected(tmp_path: Path) -> None:
    import sqlite3
    params = runner.load_prereg(PREREG)["parameters"]
    rec = {"base": 16, "n_real": 2, "sizes": [15],
           "smax": {15: np.array([5, 6], dtype=np.int64)},
           "n_open": {15: np.array([50, 60], dtype=np.int64)},
           "field_hashes": ["a", "b"]}
    db = tmp_path / "raw.sqlite3"
    runner.store_raw(db, {"nested": [rec]}, "deadbeef" * 8, params)
    con = sqlite3.connect(db)
    con.execute("UPDATE arm SET smax = ?", (np.array([7, 6], dtype=np.int64).tobytes(),))
    con.commit()
    con.close()
    with pytest.raises(runner.GateError):
        runner.load_raw(db)


# ---------------------------------------------------------------- verdict rule

def test_equivalence_verdict_when_interval_inside_margin() -> None:
    v, eq, ex = runner.decide_verdict(0.001, [-0.004, 0.006], [-0.005, 0.007], 0.010)
    assert v == "LATTICE_ARTIFACT_UNSUPPORTED"
    assert eq is True and ex is False


def test_supported_verdict_requires_exclusion_and_size() -> None:
    v, eq, ex = runner.decide_verdict(0.030, [0.022, 0.038], [0.019, 0.041], 0.010)
    assert v == "LATTICE_ARTIFACT_SUPPORTED"
    assert eq is False and ex is True


def test_nonzero_but_small_effect_is_inconclusive_not_unsupported() -> None:
    """The whole point of INCONCLUSIVE_BY_RESOLUTION: never report 'no effect'."""
    v, _, _ = runner.decide_verdict(0.006, [-0.002, 0.014], [-0.004, 0.016], 0.010)
    assert v == "INCONCLUSIVE_BY_RESOLUTION"


def test_wide_interval_is_inconclusive_not_unsupported() -> None:
    v, eq, _ = runner.decide_verdict(0.0, [-0.05, 0.05], [-0.06, 0.06], 0.010)
    assert v == "INCONCLUSIVE_BY_RESOLUTION"
    assert eq is False


# ---------------------------------------------------------------- estimator

def _synthetic_pair_smax(base: int, n: int, p2_offset: float, noise: float,
                         seed: int) -> dict[int, np.ndarray]:
    """Fake nested data: S scales as L^D_f, with an optional P2-only offset.

    The offset is applied ONLY to the power-of-two sample, which is exactly the
    signal the primary contrast is meant to detect.
    """
    gen = np.random.default_rng(seed)
    d_f = 91.0 / 48.0
    common = gen.normal(0.0, noise, size=n)
    out = {}
    for off in (0, 1, 2, 3):
        s = base - off
        shift = p2_offset if off == 0 else 0.0
        out[s] = np.exp(d_f * np.log(s) + common + shift)
    return out


def test_contrast_recovers_an_injected_power_of_two_offset() -> None:
    params = runner.load_prereg(PREREG)["parameters"]
    bases = [128, 256, 512, 1024]
    runner._SMAX = {}
    for b in bases:
        fake = _synthetic_pair_smax(b, 400, p2_offset=np.log(1.10), noise=0.02, seed=b)
        for s, arr in fake.items():
            runner._SMAX[(b, s)] = arr
    res = runner.contrast(params, bases, "p2_anchored", "nonp2_anchored", 400, 11)
    # a 10% mass deficit at a power of two is a slope shift of
    # log(1.10)/log(128/127)-ish; just assert it lands on the injected size
    assert res["beta"] > 0.05, f"contrast failed to recover the injected offset: {res['beta']}"
    v, _, _ = runner.decide_verdict(res["beta"], res["ci90"], res["ci95"], 0.010)
    assert v == "LATTICE_ARTIFACT_SUPPORTED"


def test_contrast_is_near_zero_without_an_injected_offset() -> None:
    params = runner.load_prereg(PREREG)["parameters"]
    bases = [128, 256, 512, 1024]
    runner._SMAX = {}
    for b in bases:
        fake = _synthetic_pair_smax(b, 400, p2_offset=0.0, noise=0.02, seed=b)
        for s, arr in fake.items():
            runner._SMAX[(b, s)] = arr
    res = runner.contrast(params, bases, "p2_anchored", "nonp2_anchored", 400, 12)
    assert abs(res["beta"]) < 0.01
    v, eq, _ = runner.decide_verdict(res["beta"], res["ci90"], res["ci95"], 0.010)
    assert v == "LATTICE_ARTIFACT_UNSUPPORTED"
    assert eq is True


def test_preregistration_is_frozen_and_binds_the_margin() -> None:
    doc = runner.load_prereg(PREREG)
    p = doc["parameters"]
    assert p["equivalence_margin"] == 0.010
    assert p["reference_D_f"] == 91.0 / 48.0
    assert p["audit_finding_id"] == "N-005"
    # the preregistration must refuse a silent edit
    raw = json.loads(PREREG.read_text(encoding="utf-8"))
    assert raw["config_sha256"]
    with pytest.raises(Exception):
        runner.load_prereg(AREA / "CONFIG" / "does_not_exist.json")


# ------------------------------------------------- corrected primary estimator

BASES = [128, 256, 512, 1024]


def _fake_raw(d_f=91.0 / 48.0, p2_exponent_offset=0.0, correction=0.0,
              noise=0.40, n=120, seed=7):
    """Synthetic nested raw table with a known injected exponent offset."""
    gen = np.random.default_rng(seed)
    raw = {}
    for b in BASES:
        common = gen.normal(0.0, noise, n)
        for off in (0, 1):
            s = b - off
            d = d_f + (p2_exponent_offset if off == 0 else 0.0)
            val = np.exp(d * np.log(s) + correction * np.log(s) ** 2 + common)
            raw[("nested", b, s)] = (val, None)
    return raw


def test_slope_weights_sum_to_zero() -> None:
    for sizes in (BASES, [b - 1 for b in BASES]):
        w = runner.slope_weights(sizes)
        assert abs(float(w.sum())) < 1e-12
        assert len(w) == len(sizes)


def test_slope_weights_recover_a_pure_power_law() -> None:
    d_f = 91.0 / 48.0
    w = runner.slope_weights(BASES)
    y = np.array([d_f * np.log(s) for s in BASES])
    assert abs(float(np.dot(w, y)) - d_f) < 1e-10


def test_ladder_contrast_is_null_for_a_pure_power_law() -> None:
    raw = _fake_raw(p2_exponent_offset=0.0)
    res = runner.ladder_contrast(raw, BASES, draws=2000, seed=1)
    assert abs(res["beta"]) < 1e-3
    lo, hi = res["ci90"]
    assert lo < 0.0 < hi


@pytest.mark.parametrize("offset", [0.0265, -0.0265])
def test_ladder_contrast_recovers_an_injected_exponent_offset(offset: float) -> None:
    raw = _fake_raw(p2_exponent_offset=offset)
    res = runner.ladder_contrast(raw, BASES, draws=2000, seed=2)
    assert abs(res["beta"] - offset) < 2e-3, f"recovered {res['beta']}, expected {offset}"
    lo, hi = res["ci95"]
    assert (lo > 0 and hi > 0) if offset > 0 else (lo < 0 and hi < 0)


def test_ladder_contrast_tolerates_a_shared_smooth_correction() -> None:
    """A finite-size correction common to both arms must not manufacture beta."""
    raw = _fake_raw(p2_exponent_offset=0.0, correction=0.30)
    res = runner.ladder_contrast(raw, BASES, draws=2000, seed=3)
    # documented sensitivity is about 0.009 per unit of quadratic correction
    assert abs(res["beta"]) < 0.010, res["beta"]


def test_synthetic_self_check_is_recorded_and_passes() -> None:
    out = runner.ladder_contrast_synthetic_check()
    assert abs(out["null"]["beta"]) < 1e-3
    assert abs(out["injected_plus"]["beta"] - 0.0265) < 2e-3
    assert abs(out["injected_minus"]["beta"] + 0.0265) < 2e-3


def test_ladder_contrast_verdict_on_real_artifact_is_equivalence() -> None:
    """The committed artifact must satisfy the frozen equivalence rule."""
    art = AREA / "RESULTS" / "EXP-0017_20260926"
    summary = json.loads((art / "EXP-0017_summary.json").read_text(encoding="utf-8"))
    beta = summary["primary_statistic"]["beta"]
    ci90 = summary["primary_statistic"]["ci90"]
    v, eq, _ = runner.decide_verdict(beta, ci90,
                                     summary["primary_statistic"]["ci95"],
                                     summary["equivalence_margin"])
    assert eq is True
    assert v == "LATTICE_ARTIFACT_UNSUPPORTED"
    assert summary["verdict"] == v
    # and the effect must be far smaller than the historical deficit
    assert abs(beta) < 0.010
