"""Freeze the N-003 repair protocol with an exclusive-create operation.

This script is intentionally separate from the historical EXP-0014 runner.  It
has no import or path dependency on ``prereg_EXP-0014.json`` and refuses to
replace an existing repair preregistration.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPAIR_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PREREG = REPAIR_ROOT / "CONFIG" / "prereg_N-003_feigenbaum_audit_repair.json"


PREREGISTRATION: dict[str, Any] = {
    "experiment_id": "N-003-FEIGENBAUM-AUDIT-REPAIR",
    "finding": "N-003",
    "title": "High-precision repair of the z=3 and z=4 Feigenbaum superstable sequences",
    "frozen_date": "2026-09-24",
    "status_at_freeze": "UNTESTED",
    "creation_mode": "exclusive-create (open mode x; never overwrite)",
    "historical_artifact_policy": (
        "Preserve EXP-0014 code, reports, preregistration, and results as evidence. "
        "This repair does not call, import, or modify the historical EXP-0014 preregistration."
    ),
    "question": (
        "Under one explicit map convention, what period-verified superstable "
        "parameter sequences and finite-n delta ratios are obtained for z=3 and z=4?"
    ),
    "claim_scope": (
        "Known-universality numerical reproduction and diagnosis only; no discovery claim."
    ),
    "map_convention": {
        "formula": "f_a(x) = 1 - a*abs(x)**z",
        "critical_seed": "x_0 = 0",
        "z_meaning": (
            "z is the positive-integer exponent/order in abs(x)**z; it is not "
            "the period-doubling index n and is not a parameter alias."
        ),
        "z_values": [2, 3, 4],
        "n_meaning": "n labels exact period P_n = 2**n",
        "n1_seed": "a_1 = 1, with exact period P_1 = 2",
        "domain_note": (
            "The real map is evaluated on its attracting interval; abs(x)**z "
            "is retained for odd z."
        ),
    },
    "root_definition": {
        "residual": "R_n(a) = f_a**(2**n)(0)",
        "root_condition": "R_n(a_n) = 0 (superstable critical cycle)",
        "delta_definition": "delta_n = (a_(n-1)-a_(n-2))/(a_n-a_(n-1)) for n >= 3",
        "requested_n_range": [2, 10],
        "continuation": "Start each scan at the previously verified a_(n-1).",
        "root_selection": (
            "Scan strictly to the right; refine the first sign-changing bracket; "
            "accept only a candidate with exact first return P_n. If the first "
            "sign-changing candidate fails period verification, inspect the next "
            "candidate; never fall back to an unverified bracket."
        ),
        "bracketing_stop": (
            "Stop and report INCOMPLETE if no period-verified first sign-changing "
            "root is found within the configured horizon expansions or if a finer "
            "resolution scan changes the first root."
        ),
    },
    "period_certificate": {
        "direct_check": "smallest k in [1,P_n] with abs(f_a**k(0)) <= zero_tolerance",
        "independent_check": (
            "separately grouped f_a**2 composition checks proper power-of-two "
            "divisors and the f_a**P_n return"
        ),
        "tolerance": "10**(-(decimal_digits - 20))",
        "required_result": "direct_first_return = grouped_first_return = P_n",
    },
    "precision": {
        "arithmetic": "mpmath arbitrary precision",
        "decimal_digits": 100,
        "allowed_decimal_digits": [80, 100],
        "root_bracket_width": "10**(-(decimal_digits - 12))",
        "scan_points_primary": 2048,
        "scan_resolution_check": "repeat the first-root scan at 4096 points",
    },
    "solver_controls": {
        "continuation_horizon_factor": 40,
        "initial_horizon": "1",
        "max_horizon_expansions": 8,
        "bisection_iterations": 500,
        "root_width_exponent": 12,
        "start_offset_dps_divisor": 2,
        "start_offset_rule": "10**(-max(12, floor(decimal_digits/2))) * max(1, abs(a_left))",
        "period_guard_digits": 20,
    },
    "sequence_checks": {
        "parameters": "report strict increase of a_n",
        "deltas": (
            "report every adjacent delta transition and strict/nondecreasing "
            "checks; a nonmonotone finite sequence is reported, not hidden"
        ),
        "claim_gate": (
            "Do not call a monotone convergence claim supported if the reported "
            "delta sequence is nonmonotone."
        ),
    },
    "controls": [
        "analytic a_1=1 period-2 seed",
        "direct first-return certificate",
        "independent grouped power-of-two first-return certificate",
        "z=2 Feigenbaum delta smoke comparison",
        "literature convention/metadata check",
    ],
    "alpha": {
        "estimate": False,
        "reason": (
            "No spatial scaling variable is defined by this protocol. Do not "
            "report alpha or infer a signed/absolute reduction exponent."
        ),
    },
    "literature_comparison": {
        "z2_reference": {
            "value": "4.669201609102990671853203820466201617258185577475768632745651343054117265635530130179812",
            "source": "M. Feigenbaum, J. Stat. Phys. 19, 25-52 (1978), DOI 10.1007/BF01020332",
        },
        "hu_mao_actual_record": {
            "citation": (
                "B. Hu and J. M. Mao, Period doubling: Universality and "
                "critical-point order, Phys. Rev. A 25, 3259-3261 (1982)"
            ),
            "doi": "10.1103/PhysRevA.25.3259",
            "map_in_paper": "f(x)=1-a*x**z",
            "orders_in_paper": [2, 4, 6, 8],
            "table_i_exact_delta_displayed": {
                "z2": "4.669",
                "z4": "7.284",
                "z6": "9.296",
                "z8": "10.948",
            },
            "comparison_rule": (
                "For even z the paper's x**z agrees with abs(x)**z on real x. "
                "Hu-Mao does not report z=3; do not use the historical 4.894/5.168 "
                "z=3/z=4 pair as a Hu-Mao comparison."
            ),
        },
    },
    "outputs": {
        "implementation": "CODE/feigenbaum_n003_solver.py",
        "runner": "CODE/run_n003_audit.py",
        "tests": "tests/test_n003_feigenbaum_audit_repair.py",
        "result_directory": "RESULTS/",
    },
}


def freeze_prereg(path: Path = DEFAULT_PREREG) -> Path:
    """Create the frozen JSON once, failing if the path already exists."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(PREREGISTRATION, indent=2, sort_keys=True) + "\n"
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise FileExistsError(
            f"refusing to overwrite frozen N-003 preregistration: {path}"
        ) from exc
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_PREREG,
        help="new preregistration path (must not already exist)",
    )
    args = parser.parse_args()
    path = freeze_prereg(args.path)
    print(path)


if __name__ == "__main__":
    main()
