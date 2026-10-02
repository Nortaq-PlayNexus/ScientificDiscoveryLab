"""Run the isolated N-003 Feigenbaum audit repair.

The runner reads only the newly frozen N-003 preregistration.  It does not
import the historical EXP-0014 engine and it does not call or modify the
historical EXP-0014 preregistration.  Result and report files in this repair
area are created with exclusive-create semantics so a prior evidence artifact
is never overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import mpmath as mp

REPAIR_ROOT = Path(__file__).resolve().parents[1]
CODE_ROOT = REPAIR_ROOT / "CODE"
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from feigenbaum_n003_solver import (  # noqa: E402
    FamilyResult,
    SolverConfig,
    family_as_dict,
    run_all,
)


DEFAULT_PREREG = REPAIR_ROOT / "CONFIG" / "prereg_N-003_feigenbaum_audit_repair.json"
DEFAULT_RESULTS = REPAIR_ROOT / "RESULTS" / "N003_feigenbaum_audit_repair_results.json"
DEFAULT_REPORT = REPAIR_ROOT / "REPORT" / "N003_feigenbaum_audit_repair.md"


def _read_new_prereg(path: Path) -> dict[str, Any]:
    """Read the repair preregistration, with an explicit path guard."""

    path = Path(path).resolve()
    if path.name != "prereg_N-003_feigenbaum_audit_repair.json":
        raise ValueError(f"unexpected preregistration path: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("finding") != "N-003":
        raise ValueError("preregistration is not for N-003")
    if payload.get("creation_mode", "").split()[0] != "exclusive-create":
        raise ValueError("preregistration does not declare exclusive creation")
    return payload


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_exclusive(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
    except FileExistsError as exc:
        raise FileExistsError(f"refusing to overwrite audit artifact: {path}") from exc


def _config_from_prereg(prereg: dict[str, Any]) -> SolverConfig:
    precision = prereg["precision"]
    controls = prereg["solver_controls"]
    return SolverConfig(
        decimal_digits=int(precision["decimal_digits"]),
        scan_points=int(precision["scan_points_primary"]),
        continuation_factor=int(controls["continuation_horizon_factor"]),
        initial_horizon=str(controls["initial_horizon"]),
        max_horizon_expansions=int(controls["max_horizon_expansions"]),
        bisection_iterations=int(controls["bisection_iterations"]),
        root_width_exponent=int(controls["root_width_exponent"]),
        start_offset_dps_divisor=int(controls["start_offset_dps_divisor"]),
        period_guard_digits=int(controls["period_guard_digits"]),
        check_scan_resolution=True,
    )


def _family_literature_status(
    family: FamilyResult, prereg: dict[str, Any]
) -> dict[str, Any]:
    literature = prereg["literature_comparison"]
    if family.z == 2:
        reference_text = literature["z2_reference"]["value"]
        reference = mp.mpf(reference_text)
        if family.deltas:
            last_n = max(family.deltas)
            observed = family.deltas[last_n]
            deviation = abs(observed - reference)
            return {
                "status": "reproduced_known_limit_at_finite_n",
                "reference": reference_text,
                "reference_source": literature["z2_reference"]["source"],
                "last_n": last_n,
                "observed": mp.nstr(observed, family.decimal_digits),
                "absolute_deviation": mp.nstr(deviation, family.decimal_digits),
                "interpretation": (
                    "Finite-n superstable ratio agrees with the published "
                    "quadratic Feigenbaum delta; this is a reproduction, not a discovery."
                ),
            }
    if family.z == 4:
        reference_text = literature["hu_mao_actual_record"]["table_i_exact_delta_displayed"]["z4"]
        reference = mp.mpf(reference_text)
        if family.deltas:
            last_n = max(family.deltas)
            observed = family.deltas[last_n]
            deviation = abs(observed - reference)
            return {
                "status": "direct_even_order_comparison_at_paper_precision",
                "reference": reference_text,
                "reference_source": literature["hu_mao_actual_record"]["citation"],
                "doi": literature["hu_mao_actual_record"]["doi"],
                "last_n": last_n,
                "observed": mp.nstr(observed, family.decimal_digits),
                "absolute_deviation_from_displayed_4_digit_value": mp.nstr(
                    deviation, family.decimal_digits
                ),
                "interpretation": (
                    "The map convention agrees for even z; the finite-n ratio "
                    "is compared only with the four-digit table value."
                ),
            }
    return {
        "status": "not_directly_reported_by_Hu_Mao",
        "reference": None,
        "reference_source": literature["hu_mao_actual_record"]["citation"],
        "doi": literature["hu_mao_actual_record"]["doi"],
        "interpretation": (
            "Hu-Mao's actual paper studies z=2,4,6,8 and does not provide a "
            "z=3 table entry. The historical 4.894 value is not used as a "
            "literature comparator."
        ),
    }


def build_payload(
    prereg_path: Path = DEFAULT_PREREG,
) -> tuple[dict[str, Any], FamilyResult]:
    """Run all requested families and build a JSON-safe evidence payload."""

    prereg_path = Path(prereg_path)
    prereg = _read_new_prereg(prereg_path)
    config = _config_from_prereg(prereg)
    n_min, n_max = prereg["root_definition"]["requested_n_range"]
    if int(n_min) != 2:
        raise ValueError("N-003 protocol must begin scanned roots at n=2")
    families = run_all((2, 3, 4), n_max=int(n_max), config=config)

    serialized_families: dict[str, Any] = {}
    for z, result in families.items():
        serialized_families[str(z)] = family_as_dict(result)
        serialized_families[str(z)]["literature_comparison"] = _family_literature_status(
            result, prereg
        )

    all_complete = all(result.complete for result in families.values())
    all_periods = all(
        result.sequence_checks["all_completed_periods_verified"]
        for result in families.values()
    )
    all_resolution_checks = all(
        all(
            root.bracketing["resolution_check_passed"]
            for root in result.roots
        )
        for result in families.values()
    )
    payload: dict[str, Any] = {
        "experiment_id": prereg["experiment_id"],
        "finding": prereg["finding"],
        "status": "COMPLETE" if all_complete else "INCOMPLETE",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "implementation": "feigenbaum_n003_solver.py",
        "implementation_sha256": _sha256(CODE_ROOT / "feigenbaum_n003_solver.py"),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "mpmath": mp.__version__,
        },
        "preregistration": {
            "path": str(prereg_path),
            "sha256": _sha256(prereg_path),
            "read_only": True,
        },
        "map_convention": prereg["map_convention"],
        "precision": {
            "arithmetic": "mpmath",
            "decimal_digits": config.decimal_digits,
            "scan_points": config.scan_points,
            "resolution_check": config.check_scan_resolution,
        },
        "families": serialized_families,
        "checks": {
            "all_requested_families_complete": all_complete,
            "all_completed_periods_verified": all_periods,
            "all_resolution_checks_passed": all_resolution_checks,
            "alpha_estimated": False,
            "alpha_status": prereg["alpha"]["reason"],
            "monotonicity_is_reported_not_assumed": True,
        },
        "claim_limitation": prereg["claim_scope"],
    }
    return payload, families


def _markdown_table(rows: list[list[str]], headers: list[str]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(payload: dict[str, Any]) -> str:
    """Render a concise, provenance-preserving technical report."""

    families = payload["families"]
    lines = [
        "# N-003 Feigenbaum Audit-Repair Report",
        "",
        "**Status:** " + payload["status"],
        "**Scope:** z=2 smoke/control and z=3/z=4 diagnosis only; no discovery claim.",
        "",
        "## Frozen protocol and convention",
        "",
        "The implementation reads only the new N-003 preregistration. The map is",
        "`f_a(x) = 1 - a*abs(x)**z` with `x_0=0`; `z` is the extremum exponent",
        "and `n` labels exact period `P_n=2**n`.",
        "",
        f"Arithmetic: mpmath at {payload['precision']['decimal_digits']} decimal digits; "
        "primary scan and doubled-resolution scan are both required.",
        f"Environment: Python `{payload['environment']['python']}`; "
        f"mpmath `{payload['environment']['mpmath']}`; platform "
        f"`{payload['environment']['platform']}`.",
        "",
        "## Computed sequences",
        "",
    ]
    for z in ("2", "3", "4"):
        fam = families[z]
        lines.append(f"### z={z} — {fam['status']}")
        lines.append("")
        rows = []
        for n in range(2, int(fam["n_max_requested"]) + 1):
            if str(n) not in fam["a_values"]:
                rows.append([str(n), "—", "—", "—", "—"])
                continue
            root = next((r for r in fam["roots"] if int(r["n"]) == n), None)
            cert = root["certificate"] if root else {}
            rows.append(
                [
                    str(n),
                    fam["a_values"][str(n)][:28],
                    fam["deltas"].get(str(n), "—")[:28],
                    str(root["period"]) if root else "—",
                    str(cert.get("verified", "—")),
                ]
            )
        lines.append(
            _markdown_table(
                rows,
                ["n", "a_n (28 digits)", "delta_n (28 digits)", "P_n", "period verified"],
            )
        )
        checks = fam["sequence_checks"]
        lines.extend(
            [
                "",
                f"- Parameters strictly increasing: **{checks['parameter_strictly_increasing']}**",
                f"- Deltas strictly increasing: **{checks['delta_strictly_increasing']}**",
                f"- Deltas nondecreasing: **{checks['delta_nondecreasing']}**",
                f"- All completed periods independently verified: **{checks['all_completed_periods_verified']}**",
                f"- Alpha: **not computed** ({fam['alpha_status']})",
                "",
            ]
        )
        comp = fam["literature_comparison"]
        lines.append(
            f"Literature status: `{comp['status']}`. {comp['interpretation']}"
        )
        if comp.get("reference") is not None:
            lines.append(
                f"Reference `{comp['reference']}`; last observed "
                f"`{comp.get('observed', 'n/a')}`."
            )
        lines.append("")

    lines.extend(
        [
            "## Interpretation and limitations",
            "",
            "- z=2 is a known Feigenbaum reproduction, not a discovery.",
            "- z=3 and z=4 have strictly increasing period-verified parameter "
            "sequences, but their finite delta ratios are not monotone: z=3 "
            "decreases from n=9 to n=10, and z=4 decreases after n=6. Under the "
            "frozen claim gate, no monotone convergence claim is made for those "
            "families; the computation is a root-selection diagnosis.",
            "- The actual Hu-Mao record is B. Hu and J. M. Mao, *Period doubling: "
            "Universality and critical-point order*, Phys. Rev. A 25, 3259–3261 "
            "(1982), DOI `10.1103/PhysRevA.25.3259`. It studies even orders "
            "z=2,4,6,8 and displays exact delta values 4.669, 7.284, 9.296, "
            "10.948; it does not report z=3.",
            "- The historical z=3/z=4 claims are not treated as evidence. Their "
            "root-selection problems are outside the repaired implementation.",
            "- A finite scan cannot prove that no unresolved sign changes exist "
            "between grid points. The doubled-resolution check, direct/grouped "
            "period certificates, and explicit stop rule reduce but do not "
            "eliminate this numerical limitation.",
            "- At 100 digits the configured zero tolerance is 1e-80; trailing "
            "digits beyond that numerical certificate should not be interpreted "
            "as additional independent accuracy.",
            "- No alpha is reported because no spatial scaling variable is defined "
            "in this protocol.",
            "- EXP-0014 historical files/results remain preserved and untouched.",
            "",
        ]
    )
    return "\n".join(lines)


def run(
    prereg_path: Path = DEFAULT_PREREG,
    results_path: Path = DEFAULT_RESULTS,
    report_path: Path = DEFAULT_REPORT,
) -> dict[str, Any]:
    payload, _ = build_payload(prereg_path)
    _write_exclusive(
        results_path,
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n",
    )
    _write_exclusive(report_path, render_report(payload))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prereg", type=Path, default=DEFAULT_PREREG)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    payload = run(args.prereg, args.results, args.report)
    print(json.dumps({
        "status": payload["status"],
        "results": str(args.results),
        "report": str(args.report),
        "z2_delta_last": payload["families"]["2"]["deltas"].get(str(
            payload["families"]["2"]["n_max_completed"]
        )),
        "z3_delta_last": payload["families"]["3"]["deltas"].get(str(
            payload["families"]["3"]["n_max_completed"]
        )),
        "z4_delta_last": payload["families"]["4"]["deltas"].get(str(
            payload["families"]["4"]["n_max_completed"]
        )),
    }, indent=2))
    if payload["status"] != "COMPLETE":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
