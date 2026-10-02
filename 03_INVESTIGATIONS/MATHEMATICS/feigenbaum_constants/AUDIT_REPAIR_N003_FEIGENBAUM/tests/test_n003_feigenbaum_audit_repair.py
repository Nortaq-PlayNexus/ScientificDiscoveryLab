"""Focused tests for the isolated N-003 Feigenbaum repair."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import mpmath as mp
import pytest

REPAIR_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = REPAIR_ROOT / "CODE"
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from feigenbaum_n003_solver import (  # noqa: E402
    SolverConfig,
    certify_period,
    family_as_dict,
    map_value,
    run_family,
)
from freeze_prereg_n003 import freeze_prereg  # noqa: E402


def _config(points: int = 256) -> SolverConfig:
    # 80 digits is the low end of the preregistered range and keeps these
    # focused tests quick while exercising the same high-precision code path.
    return SolverConfig(
        decimal_digits=80,
        scan_points=points,
        check_scan_resolution=True,
    )


def test_analytic_seed_and_explicit_map_convention() -> None:
    with mp.workdps(80):
        a = mp.mpf(1)
        seed = certify_period(a, z=2, n=1, config=_config())
        assert seed.verified
        assert seed.direct_first_return == 2
        assert seed.independent_power_two_first_return == 2
        # Odd z uses abs(x)**z, not x**z.
        assert map_value(mp.mpf(-2), mp.mpf(3), 3) == mp.mpf(1) - 3 * 8


def test_first_return_rejects_an_inherited_period_root() -> None:
    family = run_family(z=2, n_max=2, config=_config())
    assert family.complete
    a2 = family.a_values[2]
    # a_2 is a period-4 root, hence it is an inherited zero for R_3 and
    # must not be accepted as a period-8 root.
    certificate = certify_period(a2, z=2, n=3, config=_config())
    assert certificate.direct_first_return == 4
    assert certificate.independent_power_two_first_return == 4
    assert not certificate.verified


def test_tiny_continuation_selects_period_verified_z3_roots() -> None:
    family = run_family(z=3, n_max=3, config=_config(512))
    assert family.complete
    assert family.n_max_completed == 3
    assert family.a_values[2] < family.a_values[3]
    assert family.sequence_checks["all_completed_periods_verified"]
    assert family.sequence_checks["parameter_strictly_increasing"]
    assert family.deltas[3] > mp.mpf("5.4")
    assert all(root.certificate.verified for root in family.roots)


def test_z2_smoke_reproduces_known_delta_limit() -> None:
    family = run_family(z=2, n_max=6, config=_config(512))
    assert family.complete
    delta6 = family.deltas[6]
    reference = mp.mpf("4.669201609102990671853203820466201617258185577475768632745651343054")
    assert abs(delta6 - reference) < mp.mpf("0.01")
    assert family.sequence_checks["delta_strictly_increasing"]
    assert all(root.certificate.verified for root in family.roots)


def test_sequence_diagnostics_report_nonmonotone_delta() -> None:
    family = run_family(z=4, n_max=7, config=_config(256))
    assert family.complete
    assert family.sequence_checks["parameter_strictly_increasing"]
    # The z=4 finite-n ratio peaks at n=6 and then decreases; this must be
    # surfaced rather than converted into a false convergence claim.
    assert not family.sequence_checks["delta_strictly_increasing"]
    assert not family.sequence_checks["delta_nondecreasing"]


def test_alpha_is_not_silently_estimated() -> None:
    family = run_family(z=2, n_max=2, config=_config(256))
    serialized = family_as_dict(family)
    assert serialized["alpha"] is None
    assert "not computed" in serialized["alpha_status"]


def test_preregistration_freeze_is_exclusive_and_valid_json(tmp_path: Path) -> None:
    target = tmp_path / "CONFIG" / "prereg_N-003_feigenbaum_audit_repair.json"
    created = freeze_prereg(target)
    assert created == target
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["finding"] == "N-003"
    assert payload["precision"]["decimal_digits"] == 100
    assert "abs(x)**z" in payload["map_convention"]["formula"]
    with pytest.raises(FileExistsError):
        freeze_prereg(target)
