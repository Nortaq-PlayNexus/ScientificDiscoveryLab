"""N-003 Feigenbaum audit-repair solver.

This module is deliberately self-contained.  It does not import the historical
EXP-0014 engine and it never reads or writes the historical experiment files.

Mathematical convention
----------------------
For a positive integer extremum order ``z`` we use the one-hump map

    f_a(x) = 1 - a * abs(x) ** z,       x_0 = 0,

where ``a`` is the control parameter.  The index ``n`` is *not* the
period: the requested period is ``P_n = 2**n``.  Thus ``z`` is the exponent
in the absolute-power cusp and ``n`` labels the period-doubling level.  The
z=2, z=3, z=4 labels in this audit therefore have an explicit, fixed
meaning; in particular z=3 means ``abs(x)**3`` rather than ``x**3``.

The roots are superstable parameter values, defined by

    R_n(a) = f_a ** P_n (0) = 0.

The repair starts at the analytically known ``a_1 = 1`` (period 2), and for
 each later n scans strictly to the right of the previously *verified* root.
The first sign-changing bracket encountered is refined and accepted only if
an independent first-return certificate proves exact period P_n.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import mpmath as mp


MIN_DECIMAL_DIGITS = 80
MAX_DECIMAL_DIGITS = 100
DEFAULT_DECIMAL_DIGITS = 100


class FeigenbaumAuditError(RuntimeError):
    """Base class for fail-closed N-003 audit errors."""


class BracketingError(FeigenbaumAuditError):
    """Raised when a verified first root cannot be isolated."""


class PeriodVerificationError(FeigenbaumAuditError):
    """Raised when a root cannot be certified as the requested period."""


@dataclass(frozen=True)
class SolverConfig:
    """Numerical controls for the repair.

    The defaults are deliberately conservative.  ``decimal_digits`` is
    restricted to the requested 80--100 digit range.  The scan is only a
    bracketing device: a candidate is never accepted solely because a scan
    point changed sign.
    """

    decimal_digits: int = DEFAULT_DECIMAL_DIGITS
    scan_points: int = 2048
    continuation_factor: int = 40
    initial_horizon: str = "1"
    max_horizon_expansions: int = 8
    bisection_iterations: int = 500
    # A root is refined until its parameter bracket is at most this wide.
    root_width_exponent: int = 12
    # Start just to the right of the inherited root, not exactly on it.
    start_offset_dps_divisor: int = 2
    # Numerical zero threshold for period certificates: 10^(-dps+guard).
    period_guard_digits: int = 20
    # Compare the first accepted root against a doubled-resolution scan.
    check_scan_resolution: bool = True

    def validate(self) -> None:
        if not MIN_DECIMAL_DIGITS <= self.decimal_digits <= MAX_DECIMAL_DIGITS:
            raise ValueError(
                f"decimal_digits must be in [{MIN_DECIMAL_DIGITS}, "
                f"{MAX_DECIMAL_DIGITS}], got {self.decimal_digits}"
            )
        if self.scan_points < 32:
            raise ValueError("scan_points must be at least 32")
        if self.continuation_factor < 2:
            raise ValueError("continuation_factor must be at least 2")
        if self.max_horizon_expansions < 0:
            raise ValueError("max_horizon_expansions must be non-negative")
        if self.bisection_iterations < 100:
            raise ValueError("bisection_iterations must be at least 100")
        if self.period_guard_digits < 4:
            raise ValueError("period_guard_digits must be at least 4")


@dataclass(frozen=True)
class PeriodCertificate:
    """Independent numerical certificate for an exact power-of-two period."""

    requested_period: int
    direct_first_return: int | None
    independent_power_two_first_return: int | None
    direct_return_residual: str
    grouped_return_residual: str
    zero_tolerance: str
    verified: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "requested_period": self.requested_period,
            "direct_first_return": self.direct_first_return,
            "independent_power_two_first_return": (
                self.independent_power_two_first_return
            ),
            "direct_return_residual": self.direct_return_residual,
            "grouped_return_residual": self.grouped_return_residual,
            "zero_tolerance": self.zero_tolerance,
            "verified": self.verified,
        }


@dataclass(frozen=True)
class RootResult:
    n: int
    period: int
    a: mp.mpf
    residual: mp.mpf
    certificate: PeriodCertificate
    bracketing: dict[str, Any]


@dataclass(frozen=True)
class FamilyResult:
    z: int
    n_max_requested: int
    n_max_completed: int
    status: str
    stop_reason: str | None
    decimal_digits: int
    a_values: dict[int, mp.mpf]
    roots: tuple[RootResult, ...]
    deltas: dict[int, mp.mpf]
    sequence_checks: dict[str, Any]

    @property
    def complete(self) -> bool:
        return self.status == "COMPLETE"


def _validate_z(z: int) -> None:
    if isinstance(z, bool) or not isinstance(z, int) or z < 1:
        raise ValueError(f"z must be a positive integer, got {z!r}")


def _validate_n(n: int) -> None:
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError(f"n must be a positive integer, got {n!r}")


def _power10(exponent: int) -> mp.mpf:
    return mp.power(mp.mpf(10), exponent)


def _zero_tolerance(config: SolverConfig) -> mp.mpf:
    return _power10(-(config.decimal_digits - config.period_guard_digits))


def _root_width_tolerance(config: SolverConfig) -> mp.mpf:
    return _power10(-(config.decimal_digits - config.root_width_exponent))


def _start_offset(a_left: mp.mpf, config: SolverConfig) -> mp.mpf:
    # This is much larger than the requested root bracket width, while still
    # being tiny compared with every non-degenerate parameter step in the
    # audit.  It prevents the inherited zero at a_{n-1} from being rescanned.
    digits = max(12, config.decimal_digits // config.start_offset_dps_divisor)
    return _power10(-digits) * max(mp.mpf(1), abs(a_left))


def _sign(value: mp.mpf) -> int:
    if value == 0:
        return 0
    return 1 if value > 0 else -1


def _opposite_sign(left: mp.mpf, right: mp.mpf) -> bool:
    return _sign(left) * _sign(right) < 0


def map_value(x: mp.mpf, a: mp.mpf, z: int) -> mp.mpf:
    """Evaluate the explicitly declared map ``1 - a*abs(x)**z``."""

    _validate_z(z)
    return mp.mpf(1) - a * (abs(x) ** z)


def _grouped_map_value(x: mp.mpf, a: mp.mpf, z: int) -> mp.mpf:
    """Second iterate, written separately for the independent certificate."""

    y = mp.mpf(1) - a * (abs(x) ** z)
    return mp.mpf(1) - a * (abs(y) ** z)


def iterate_from_critical(
    a: mp.mpf, z: int, iterations: int, *, grouped: bool = False
) -> mp.mpf:
    """Return the state after ``iterations`` applications of f to zero."""

    _validate_z(z)
    if iterations < 0:
        raise ValueError("iterations must be non-negative")
    x = mp.mpf(0)
    step = _grouped_map_value if grouped else map_value
    if grouped:
        if iterations % 2:
            raise ValueError("grouped iteration requires an even iteration count")
        for _ in range(iterations // 2):
            x = step(x, a, z)
    else:
        for _ in range(iterations):
            x = step(x, a, z)
    return x


def return_residual(a: mp.mpf, z: int, n: int) -> mp.mpf:
    """Primary residual ``f^(2**n)(0)`` for the declared map."""

    _validate_n(n)
    return iterate_from_critical(a, z, 1 << n, grouped=False)


def direct_first_return(
    a: mp.mpf, z: int, period: int, zero_tolerance: mp.mpf
) -> int | None:
    """Return the first k<=period with ``abs(f^k(0)) <= zero_tolerance``."""

    _validate_z(z)
    if period < 1:
        raise ValueError("period must be positive")
    x = mp.mpf(0)
    for k in range(1, period + 1):
        x = map_value(x, a, z)
        if abs(x) <= zero_tolerance:
            return k
    return None


def independent_power_two_first_return(
    a: mp.mpf, z: int, period: int, zero_tolerance: mp.mpf
) -> int | None:
    """Check return times using separately grouped two-step composition.

    For ``period=2**q`` this checks every proper power-of-two divisor by
    repeatedly applying ``f^2``.  It is an independent implementation path
    from :func:`direct_first_return`, not a second call to the same residual.
    """

    _validate_z(z)
    if period < 1 or period & (period - 1):
        raise ValueError("independent check requires a power-of-two period")
    if period == 1:
        return 1 if abs(mp.mpf(0)) <= zero_tolerance else None
    groups = period // 2
    x = mp.mpf(0)
    # Repeated f^2 applications produce f^2, f^4, f^6, ... .  The proper
    # power-of-two divisors occur at group numbers 1, 2, 4, ..., period/4.
    for group in range(1, groups + 1):
        x = _grouped_map_value(x, a, z)
        if group < groups and group & (group - 1) == 0:
            if abs(x) <= zero_tolerance:
                return 2 * group
    return period if abs(x) <= zero_tolerance else None


def certify_period(
    a: mp.mpf, z: int, n: int, config: SolverConfig | None = None
) -> PeriodCertificate:
    """Return a direct plus grouped first-return certificate for period 2**n."""

    cfg = config or SolverConfig()
    cfg.validate()
    _validate_n(n)
    with mp.workdps(cfg.decimal_digits):
        period = 1 << n
        tol = _zero_tolerance(cfg)
        direct = direct_first_return(a, z, period, tol)
        grouped = independent_power_two_first_return(a, z, period, tol)
        direct_residual = iterate_from_critical(a, z, period, grouped=False)
        grouped_residual = iterate_from_critical(a, z, period, grouped=True)
        verified = (
            direct == period
            and grouped == period
            and abs(direct_residual) <= tol
            and abs(grouped_residual) <= tol
        )
        return PeriodCertificate(
            requested_period=period,
            direct_first_return=direct,
            independent_power_two_first_return=grouped,
            direct_return_residual=mp.nstr(direct_residual, cfg.decimal_digits),
            grouped_return_residual=mp.nstr(grouped_residual, cfg.decimal_digits),
            zero_tolerance=mp.nstr(tol, cfg.decimal_digits),
            verified=verified,
        )


def _bisect_sign_change(
    left: mp.mpf,
    right: mp.mpf,
    left_value: mp.mpf,
    z: int,
    n: int,
    config: SolverConfig,
) -> tuple[mp.mpf, int]:
    """Refine a sign-changing bracket without using a floating-point solver."""

    # Recompute the endpoint once to make the precondition explicit and to
    # avoid accepting a stale or rounded scan value.
    right_value = return_residual(right, z, n)
    if not _opposite_sign(left_value, right_value):
        raise BracketingError("bracket does not have opposite residual signs")

    width_tolerance = _root_width_tolerance(config)
    residual_tolerance = _zero_tolerance(config)
    for iteration in range(1, config.bisection_iterations + 1):
        middle = (left + right) / 2
        middle_value = return_residual(middle, z, n)
        if middle_value == 0 or abs(middle_value) <= residual_tolerance:
            return middle, iteration
        if right - left <= width_tolerance:
            return middle, iteration
        if _opposite_sign(left_value, middle_value):
            right = middle
            right_value = middle_value
        else:
            left = middle
            left_value = middle_value

    # A final midpoint is still a deterministic fail-closed result, but the
    # caller will reject it if its period certificate is not clean.
    return (left + right) / 2, config.bisection_iterations


def _scan_until_verified(
    z: int,
    n: int,
    a_left: mp.mpf,
    horizon: mp.mpf,
    config: SolverConfig,
) -> tuple[mp.mpf | None, list[dict[str, Any]], dict[str, Any]]:
    """Scan left-to-right and return the first period-verified root.

    The returned metadata includes every sign-changing candidate inspected up
    to the accepted root.  A failed period certificate is never used as a
    fallback root; scanning continues to the next sign change.
    """

    _validate_n(n)
    offset = _start_offset(a_left, config)
    start = a_left + offset
    if start >= a_left + horizon:
        raise BracketingError("scan horizon is smaller than the inherited-root offset")

    left = start
    left_value = return_residual(left, z, n)
    if left_value == 0:
        # This should only happen for a pathologically tiny horizon.  Move one
        # additional offset to the right rather than accepting the inherited
        # root.
        left += offset
        left_value = return_residual(left, z, n)

    candidates: list[dict[str, Any]] = []
    first_sign_change_index: int | None = None
    scan_points = config.scan_points
    scan_start = left
    span = (a_left + horizon) - scan_start
    for index in range(1, scan_points + 1):
        right = scan_start + span * mp.mpf(index) / mp.mpf(scan_points)
        right_value = return_residual(right, z, n)
        if _opposite_sign(left_value, right_value):
            if first_sign_change_index is None:
                first_sign_change_index = index
            root, iterations = _bisect_sign_change(
                left, right, left_value, z, n, config
            )
            certificate = certify_period(root, z, n, config)
            candidate = {
                "scan_index": index,
                "bracket_left": mp.nstr(left, config.decimal_digits),
                "bracket_right": mp.nstr(right, config.decimal_digits),
                "root": mp.nstr(root, config.decimal_digits),
                "bisection_iterations": iterations,
                "residual": mp.nstr(
                    return_residual(root, z, n), config.decimal_digits
                ),
                "certificate": certificate.as_dict(),
            }
            candidates.append(candidate)
            if certificate.verified:
                metadata = {
                    "horizon": mp.nstr(horizon, config.decimal_digits),
                    "scan_points": scan_points,
                    "start_offset": mp.nstr(offset, config.decimal_digits),
                    "first_sign_change_index": first_sign_change_index,
                    "candidates_examined": len(candidates),
                    "accepted_candidate_index": len(candidates) - 1,
                }
                return root, candidates, metadata
        left, left_value = right, right_value

    metadata = {
        "horizon": mp.nstr(horizon, config.decimal_digits),
        "scan_points": scan_points,
        "start_offset": mp.nstr(offset, config.decimal_digits),
        "first_sign_change_index": first_sign_change_index,
        "candidates_examined": len(candidates),
        "accepted_candidate_index": None,
    }
    return None, candidates, metadata


def find_first_verified_root(
    z: int,
    n: int,
    a_left: mp.mpf,
    previous_step: mp.mpf | None,
    config: SolverConfig | None = None,
) -> RootResult:
    """Find the first exact-period root strictly right of ``a_left``.

    ``a_left`` must be the previously verified superstable parameter.  The
    scan horizon is continuation-based: 40 times the preceding parameter
    step (or one unit for n=2), expanded only if no verified root is found.
    """

    cfg = config or SolverConfig()
    cfg.validate()
    _validate_z(z)
    _validate_n(n)
    if n == 1:
        raise ValueError("n=1 is the analytic seed a_1=1, not a scanned root")
    with mp.workdps(cfg.decimal_digits):
        left = mp.mpf(a_left)
        if previous_step is None:
            base_horizon = mp.mpf(cfg.initial_horizon)
        else:
            step = abs(mp.mpf(previous_step))
            if step == 0:
                raise BracketingError("previous continuation step is zero")
            base_horizon = step * mp.mpf(cfg.continuation_factor)
        if base_horizon <= 0:
            raise BracketingError("non-positive continuation horizon")

        all_attempts: list[dict[str, Any]] = []
        horizon = base_horizon
        for attempt in range(cfg.max_horizon_expansions + 1):
            root, candidates, metadata = _scan_until_verified(
                z, n, left, horizon, cfg
            )
            metadata["attempt"] = attempt + 1
            all_attempts.append(
                {
                    "metadata": metadata,
                    "candidates": candidates,
                }
            )
            if root is not None:
                # The scan is intentionally repeated at a finer resolution.
                # If the first root changes under that check, fail closed
                # rather than silently selecting a later root.
                if cfg.check_scan_resolution:
                    fine_cfg = SolverConfig(
                        decimal_digits=cfg.decimal_digits,
                        scan_points=cfg.scan_points * 2,
                        continuation_factor=cfg.continuation_factor,
                        initial_horizon=cfg.initial_horizon,
                        max_horizon_expansions=cfg.max_horizon_expansions,
                        bisection_iterations=cfg.bisection_iterations,
                        root_width_exponent=cfg.root_width_exponent,
                        start_offset_dps_divisor=cfg.start_offset_dps_divisor,
                        period_guard_digits=cfg.period_guard_digits,
                        check_scan_resolution=False,
                    )
                    fine_root, fine_candidates, fine_metadata = _scan_until_verified(
                        z, n, left, horizon, fine_cfg
                    )
                    if fine_root is None:
                        raise BracketingError(
                            "resolution check found no verified root: "
                            f"z={z}, n={n}, horizon={mp.nstr(horizon, 20)}"
                        )
                    compare_tol = _power10(-(cfg.decimal_digits - 30))
                    if abs(fine_root - root) > compare_tol:
                        raise BracketingError(
                            "first-root resolution check disagrees: "
                            f"z={z}, n={n}, coarse={mp.nstr(root, 30)}, "
                            f"fine={mp.nstr(fine_root, 30)}"
                        )
                    # Preserve the fine scan's certificate and diagnostics as
                    # the primary record; it is the same first root, refined
                    # to the same high-precision bracket.
                    root = fine_root
                    candidates = fine_candidates
                    metadata = fine_metadata
                    metadata["attempt"] = attempt + 1
                    coarse_root_text = all_attempts[-1]["candidates"][-1]["root"]
                    metadata["resolution_check"] = {
                        "coarse_root": mp.nstr(
                            mp.mpf(coarse_root_text), cfg.decimal_digits
                        ),
                        "fine_root": mp.nstr(fine_root, cfg.decimal_digits),
                        "comparison_tolerance": mp.nstr(
                            compare_tol, cfg.decimal_digits
                        ),
                    }
                certificate = certify_period(root, z, n, cfg)
                if not certificate.verified:
                    raise PeriodVerificationError(
                        f"candidate failed period certificate: z={z}, n={n}"
                    )
                bracketing = {
                    "left_verified_root": mp.nstr(left, cfg.decimal_digits),
                    "previous_step": (
                        None
                        if previous_step is None
                        else mp.nstr(previous_step, cfg.decimal_digits)
                    ),
                    "attempts": all_attempts,
                    "selected": metadata,
                    "resolution_check_passed": bool(
                        not cfg.check_scan_resolution
                        or "resolution_check" in metadata
                    ),
                }
                return RootResult(
                    n=n,
                    period=1 << n,
                    a=root,
                    residual=return_residual(root, z, n),
                    certificate=certificate,
                    bracketing=bracketing,
                )
            horizon *= 4
        raise BracketingError(
            f"no first sign-changing exact-period root for z={z}, n={n}; "
            f"bracketing/precision inadequate after {len(all_attempts)} attempts"
        )


def _sequence_diagnostics(
    a_values: dict[int, mp.mpf], deltas: dict[int, mp.mpf]
) -> dict[str, Any]:
    ordered_n = sorted(a_values)
    parameter_differences = [
        {
            "from_n": n0,
            "to_n": n1,
            "difference": mp.nstr(a_values[n1] - a_values[n0], 80),
        }
        for n0, n1 in zip(ordered_n, ordered_n[1:])
    ]
    parameter_strictly_increasing = all(
        a_values[n1] > a_values[n0] for n0, n1 in zip(ordered_n, ordered_n[1:])
    )

    delta_ns = sorted(deltas)
    delta_transitions = []
    for n0, n1 in zip(delta_ns, delta_ns[1:]):
        difference = deltas[n1] - deltas[n0]
        delta_transitions.append(
            {
                "from_n": n0,
                "to_n": n1,
                "difference": mp.nstr(difference, 80),
                "increasing": difference > 0,
                "decreasing": difference < 0,
            }
        )
    delta_strictly_increasing = all(
        item["increasing"] for item in delta_transitions
    )
    delta_nondecreasing = all(
        deltas[n1] >= deltas[n0] for n0, n1 in zip(delta_ns, delta_ns[1:])
    )
    return {
        "parameter_strictly_increasing": parameter_strictly_increasing,
        "parameter_differences": parameter_differences,
        "delta_strictly_increasing": delta_strictly_increasing,
        "delta_nondecreasing": delta_nondecreasing,
        "delta_transitions": delta_transitions,
        "all_completed_periods_verified": None,
    }


def compute_deltas(a_values: dict[int, mp.mpf]) -> dict[int, mp.mpf]:
    """Compute delta_n=(a_{n-1}-a_{n-2})/(a_n-a_{n-1}) for n>=3."""

    deltas: dict[int, mp.mpf] = {}
    for n in range(3, max(a_values, default=0) + 1):
        if n - 2 not in a_values or n - 1 not in a_values or n not in a_values:
            continue
        denominator = a_values[n] - a_values[n - 1]
        if denominator == 0:
            raise FeigenbaumAuditError(f"zero continuation step at n={n}")
        deltas[n] = (a_values[n - 1] - a_values[n - 2]) / denominator
    return deltas


def run_family(
    z: int,
    n_max: int = 10,
    config: SolverConfig | None = None,
) -> FamilyResult:
    """Run one exponent family and fail closed on inadequate bracketing."""

    _validate_z(z)
    if n_max < 1:
        raise ValueError("n_max must be at least 1")
    cfg = config or SolverConfig()
    cfg.validate()
    with mp.workdps(cfg.decimal_digits):
        a_values: dict[int, mp.mpf] = {1: mp.mpf(1)}
        roots: list[RootResult] = []
        previous_step: mp.mpf | None = None
        stop_reason: str | None = None
        status = "COMPLETE"
        completed = 1
        for n in range(2, n_max + 1):
            try:
                root = find_first_verified_root(
                    z=z,
                    n=n,
                    a_left=a_values[n - 1],
                    previous_step=previous_step,
                    config=cfg,
                )
            except (BracketingError, PeriodVerificationError) as exc:
                status = "INCOMPLETE"
                stop_reason = str(exc)
                break
            a_values[n] = root.a
            roots.append(root)
            previous_step = root.a - a_values[n - 1]
            completed = n

        deltas = compute_deltas(a_values)
        checks = _sequence_diagnostics(a_values, deltas)
        checks["all_completed_periods_verified"] = all(
            root.certificate.verified for root in roots
        )
        checks["all_completed_roots_are_to_the_right"] = all(
            root.a > a_values[root.n - 1] for root in roots
        )
        return FamilyResult(
            z=z,
            n_max_requested=n_max,
            n_max_completed=completed,
            status=status,
            stop_reason=stop_reason,
            decimal_digits=cfg.decimal_digits,
            a_values=a_values,
            roots=tuple(roots),
            deltas=deltas,
            sequence_checks=checks,
        )


def family_as_dict(result: FamilyResult, *, digits: int | None = None) -> dict[str, Any]:
    """Serialize a family without converting high-precision values to floats."""

    output_digits = digits or result.decimal_digits
    return {
        "z": result.z,
        "n_max_requested": result.n_max_requested,
        "n_max_completed": result.n_max_completed,
        "status": result.status,
        "stop_reason": result.stop_reason,
        "decimal_digits": result.decimal_digits,
        "a_values": {
            str(n): mp.nstr(a, output_digits) for n, a in sorted(result.a_values.items())
        },
        "roots": [
            {
                "n": root.n,
                "period": root.period,
                "a": mp.nstr(root.a, output_digits),
                "residual": mp.nstr(root.residual, output_digits),
                "certificate": root.certificate.as_dict(),
                "bracketing": root.bracketing,
            }
            for root in result.roots
        ],
        "deltas": {
            str(n): mp.nstr(value, output_digits) for n, value in sorted(result.deltas.items())
        },
        "sequence_checks": result.sequence_checks,
        "alpha": None,
        "alpha_status": "not computed; no spatial scaling variable was defined",
    }


def run_all(
    exponents: Iterable[int] = (2, 3, 4),
    n_max: int = 10,
    config: SolverConfig | None = None,
) -> dict[int, FamilyResult]:
    """Run the requested exponent families independently."""

    return {z: run_family(z, n_max=n_max, config=config) for z in exponents}


__all__ = [
    "BracketingError",
    "DEFAULT_DECIMAL_DIGITS",
    "FamilyResult",
    "FeigenbaumAuditError",
    "MAX_DECIMAL_DIGITS",
    "MIN_DECIMAL_DIGITS",
    "PeriodCertificate",
    "PeriodVerificationError",
    "RootResult",
    "SolverConfig",
    "certify_period",
    "compute_deltas",
    "direct_first_return",
    "family_as_dict",
    "find_first_verified_root",
    "independent_power_two_first_return",
    "iterate_from_critical",
    "map_value",
    "return_residual",
    "run_all",
    "run_family",
]
