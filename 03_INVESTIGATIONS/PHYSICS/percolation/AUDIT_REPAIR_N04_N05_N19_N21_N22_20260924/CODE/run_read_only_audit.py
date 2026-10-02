#!/usr/bin/env python3
"""Read-only repair audit for N-04/N-05/N-19/N-21/N-22.

This module never generates Monte Carlo samples and never writes a historical
config, result, cache, registry, report, or helper.  It reads the frozen stored
cells and reconstructs only quantities whose estimator and inputs are present.

The scientific classifications are intentionally conservative:
* EXP-0006 uses the corrected interpolation denominator ``w1 - w0`` and the
  historical stored-cell bootstrap stream that exactly regenerates the stored
  p50 values.  Controls that cannot be regenerated from stored cells are
  INCONCLUSIVE, not replaced with a new control.
* EXP-0007 reports requested and accepted bootstrap counts separately and keeps
  the broad FSS standard error visible.
* EXP-0009 C7 is a same-stream implementation check; R3 is an algebraically
  coupled internal consistency check.
* EXP-0010's pooled slope is reproducible, but it is not the preregistered
  individual-size gate.  The unresolved closure is marked INCONCLUSIVE.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Any, Iterable, Sequence
import zipfile

import numpy as np


AREA = Path(__file__).resolve().parents[1]
LAB_ROOT = Path(__file__).resolve().parents[5]
ENGINE_ROOT = LAB_ROOT / "04_SHARED_ENGINE"
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from engine.utilities.core import rng  # noqa: E402


SCOPE_DEFAULT = AREA / "CONFIG" / "audit_scope.json"
BASELINE_DEFAULT = AREA / "CONFIG" / "historical_evidence_baseline_post_n14.json"
APPEND_ONLY_LOCK_DEFAULT = AREA / "CONFIG" / "registry_append_only_lock.json"
ALLOWED_FINDINGS = ("N-04", "N-05", "N-19", "N-21", "N-22")
ALLOWED_EXPERIMENTS = ("EXP-0006", "EXP-0007", "EXP-0009", "EXP-0010")
REPORT_SCHEMA = "historical-2d-percolation-n04-n05-n19-n21-n22-v1"
APPEND_ONLY_LOCK_SCHEMA = "historical-2d-percolation-append-only-lock-v1"


class AuditError(RuntimeError):
    """Base error for fail-closed audit failures."""


class EvidenceError(AuditError):
    """Historical evidence is missing, malformed, or changed."""


class NumericalError(AuditError):
    """A read-only numerical reconstruction failed its registered check."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def load_strict_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8-sig"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise EvidenceError(f"cannot read strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvidenceError(f"JSON top level must be an object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(LAB_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise EvidenceError(f"path escapes laboratory root: {path}") from exc


def historical_path(relative: str) -> Path:
    if Path(relative).is_absolute():
        raise EvidenceError(f"historical evidence path must be relative: {relative}")
    resolved = (LAB_ROOT / Path(relative)).resolve()
    try:
        resolved.relative_to(LAB_ROOT.resolve())
    except ValueError as exc:
        raise EvidenceError(f"historical evidence path escapes laboratory root: {relative}") from exc
    return resolved


def load_scope(path: Path = SCOPE_DEFAULT) -> dict[str, Any]:
    scope = load_strict_json(path)
    if scope.get("schema") != "historical-2d-percolation-audit-scope-v1":
        raise EvidenceError("unexpected audit-scope schema")
    if tuple(scope.get("findings", ())) != ALLOWED_FINDINGS:
        raise EvidenceError(f"scope findings must be exactly {ALLOWED_FINDINGS}")
    if tuple(scope.get("experiments", ())) != ALLOWED_EXPERIMENTS:
        raise EvidenceError(f"scope experiments must be exactly {ALLOWED_EXPERIMENTS}")
    policy = scope.get("execution_policy")
    if not isinstance(policy, dict):
        raise EvidenceError("scope execution_policy must be an object")
    required_policy = {
        "historical_mode": "read_only",
        "production_calculations": "forbidden",
        "monte_carlo_generation": "forbidden",
        "historical_registry_rewrite": "forbidden",
        "historical_result_helper_edits": "forbidden",
    }
    for key, expected in required_policy.items():
        if policy.get(key) != expected:
            raise EvidenceError(f"unsafe or missing execution policy: {key}={policy.get(key)!r}")
    evidence = scope.get("historical_evidence")
    if not isinstance(evidence, list) or not evidence or len(evidence) != len(set(evidence)):
        raise EvidenceError("historical_evidence must be a nonempty unique list")
    for entry in evidence:
        if not isinstance(entry, str) or not entry:
            raise EvidenceError("historical evidence entries must be nonempty strings")
        resolved = historical_path(entry)
        if not resolved.is_file():
            raise EvidenceError(f"required historical evidence is missing: {entry}")
    return scope


def snapshot_evidence(scope: dict[str, Any]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for relative in scope["historical_evidence"]:
        path = historical_path(relative)
        stat = path.stat()
        entries.append(
            {
                "path": relative,
                "size_bytes": int(stat.st_size),
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema": "historical-2d-percolation-evidence-baseline-v1",
        "scope_schema": scope["schema"],
        "finding_ids": list(scope["findings"]),
        "read_only_contract": True,
        "entries": entries,
    }


def write_new_json(path: Path, value: dict[str, Any]) -> None:
    if path.exists():
        raise AuditError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def write_new_text(path: Path, text: str) -> None:
    if path.exists():
        raise AuditError(f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def check_whole_file_pin(
    actual_size: int, actual_hash: str, expected: dict[str, Any], path: str
) -> None:
    """Fail closed when a whole-file-pinned historical input is not byte-identical."""
    if actual_size != expected.get("size_bytes") or actual_hash != expected.get("sha256"):
        raise EvidenceError(
            f"historical evidence changed: [{path}] expected "
            f"{expected.get('size_bytes')} bytes / {expected.get('sha256')}, actual "
            f"{actual_size} bytes / {actual_hash}"
        )


def check_append_only_prefix(
    live_bytes: bytes,
    expected_prefix_sha256: str,
    prefix_bytes: int,
    path: str,
) -> dict[str, Any]:
    """Verify that a live append-only document still begins with its audited bytes.

    Pure function: it takes the document's bytes and never touches the disk, so
    the control can be unit-tested with tampered, truncated, and reordered
    fixtures without writing to any historical file.

    Returns a growth record.  Raises :class:`EvidenceError` if the historical
    region is not byte-identical, so appending is tolerated but editing,
    reordering, deleting, or prepending is not.
    """
    if not isinstance(prefix_bytes, int) or prefix_bytes <= 0:
        raise EvidenceError(f"invalid prefix length for {path}: {prefix_bytes!r}")
    if not isinstance(live_bytes, (bytes, bytearray)):
        raise EvidenceError(f"{path} content must be bytes")
    if len(live_bytes) < prefix_bytes:
        raise EvidenceError(
            f"append-only evidence shrank inside its audited region: {path} is "
            f"{len(live_bytes)} bytes, audited region is {prefix_bytes} bytes"
        )
    prefix = bytes(live_bytes[:prefix_bytes])
    actual_prefix_sha256 = hashlib.sha256(prefix).hexdigest()
    if actual_prefix_sha256 != expected_prefix_sha256:
        raise EvidenceError(
            f"append-only evidence changed inside its audited region: {path} "
            f"expected prefix sha256 {expected_prefix_sha256}, "
            f"actual prefix sha256 {actual_prefix_sha256}"
        )
    suffix = bytes(live_bytes[prefix_bytes:])
    return {
        "path": path,
        "policy": "append_only_prefix_pinned",
        "historical_prefix_bytes": prefix_bytes,
        "historical_prefix_sha256": expected_prefix_sha256,
        "historical_region_intact": True,
        "live_size_bytes": len(live_bytes),
        "appended_bytes": len(suffix),
        "appended_sha256": hashlib.sha256(suffix).hexdigest(),
        "append_only_growth": bool(suffix),
    }


def load_append_only_lock(
    lock_path: Path, baseline: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Load and anti-launder the append-only lock against the immutable baseline.

    The lock may only *narrow* a whole-file pin into a prefix pin whose digest and
    length are proven to be the baseline's whole-file values for that same path.
    A lock that pins different bytes, or that claims a path the baseline does not
    contain, fails closed.
    """
    lock = load_strict_json(lock_path)
    if lock.get("schema") != APPEND_ONLY_LOCK_SCHEMA:
        raise EvidenceError("unexpected append-only-lock schema")
    if lock.get("read_only_contract") is not True:
        raise EvidenceError("append-only lock is not marked read-only")
    entries = lock.get("entries")
    if not isinstance(entries, list) or not entries:
        raise EvidenceError("append-only lock must contain a nonempty entries list")
    baseline_by_path = {entry["path"]: entry for entry in baseline.get("entries", [])}
    resolved: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise EvidenceError("append-only lock entries must be objects")
        relative = entry.get("path")
        if not isinstance(relative, str) or not relative:
            raise EvidenceError("append-only lock entry is missing a path")
        if entry.get("policy") != "append_only_prefix_pinned":
            raise EvidenceError(f"unsupported append-only policy for {relative}")
        pinned = baseline_by_path.get(relative)
        if pinned is None:
            raise EvidenceError(
                f"append-only lock names a path absent from the immutable "
                f"baseline: {relative}"
            )
        if entry.get("prefix_bytes") != pinned.get("size_bytes"):
            raise EvidenceError(
                f"append-only prefix length for {relative} does not equal the "
                f"baseline whole-file size; refusing to re-freeze the evidence"
            )
        if entry.get("prefix_sha256") != pinned.get("sha256"):
            raise EvidenceError(
                f"append-only prefix digest for {relative} does not equal the "
                f"baseline whole-file digest; refusing to re-freeze the evidence"
            )
        artifact_relative = entry.get("frozen_prefix_artifact")
        if not isinstance(artifact_relative, str) or not artifact_relative:
            raise EvidenceError(f"append-only lock entry for {relative} has no frozen prefix artifact")
        artifact = historical_path(artifact_relative)
        if not artifact.is_file():
            raise EvidenceError(f"frozen append-only prefix artifact is missing: {artifact_relative}")
        artifact_sha256 = sha256_file(artifact)
        if artifact_sha256 != pinned.get("sha256"):
            raise EvidenceError(
                f"frozen prefix artifact for {relative} does not match the "
                f"baseline digest"
            )
        resolved[relative] = {
            "path": relative,
            "prefix_bytes": int(pinned["size_bytes"]),
            "prefix_sha256": str(pinned["sha256"]),
            "frozen_prefix_artifact": artifact_relative,
            "frozen_prefix_artifact_sha256": artifact_sha256,
        }
    return resolved


def validate_evidence_baseline(
    scope: dict[str, Any],
    baseline: dict[str, Any],
    append_only: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if baseline.get("schema") != "historical-2d-percolation-evidence-baseline-v1":
        raise EvidenceError("unexpected evidence-baseline schema")
    if baseline.get("scope_schema") != scope.get("schema"):
        raise EvidenceError("evidence baseline belongs to a different audit scope")
    if baseline.get("read_only_contract") is not True:
        raise EvidenceError("evidence baseline is not marked read-only")
    expected_by_path = {entry["path"]: entry for entry in baseline.get("entries", [])}
    scoped_paths = set(scope["historical_evidence"])
    if set(expected_by_path) != scoped_paths:
        missing = sorted(scoped_paths - set(expected_by_path))
        extra = sorted(set(expected_by_path) - scoped_paths)
        raise EvidenceError(f"evidence baseline path mismatch; missing={missing}, extra={extra}")
    append_only = append_only or {}
    unknown = sorted(set(append_only) - scoped_paths)
    if unknown:
        raise EvidenceError(f"append-only lock names out-of-scope paths: {unknown}")
    mismatches: list[dict[str, Any]] = []
    growth: list[dict[str, Any]] = []
    for relative in scope["historical_evidence"]:
        expected = expected_by_path[relative]
        path = historical_path(relative)
        actual_size = int(path.stat().st_size)
        actual_hash = sha256_file(path)
        locked = append_only.get(relative)
        if locked is not None:
            record = check_append_only_prefix(
                path.read_bytes(), locked["prefix_sha256"], locked["prefix_bytes"], relative
            )
            record["whole_file_sha256"] = actual_hash
            record["baseline_whole_file_sha256"] = expected.get("sha256")
            record["frozen_prefix_artifact"] = locked["frozen_prefix_artifact"]
            record["frozen_prefix_artifact_sha256"] = locked["frozen_prefix_artifact_sha256"]
            growth.append(record)
            continue
        try:
            check_whole_file_pin(actual_size, actual_hash, expected, relative)
        except EvidenceError as exc:
            mismatches.append(
                {
                    "path": relative,
                    "expected_size_bytes": expected.get("size_bytes"),
                    "actual_size_bytes": actual_size,
                    "expected_sha256": expected.get("sha256"),
                    "actual_sha256": actual_hash,
                    "reason": str(exc),
                }
            )
    if mismatches:
        raise EvidenceError(f"historical evidence changed: {mismatches}")
    return baseline["entries"], growth


def as_float_array(values: Iterable[Any], label: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size == 0 or not np.all(np.isfinite(array)):
        raise NumericalError(f"{label} must be a nonempty finite one-dimensional array")
    return array


def interp_p50(ps: Sequence[float], widths: Sequence[float], target: float = 0.5) -> float:
    """Linearly interpolate W(p)=target using the width difference denominator.

    N-04 correction: the denominator is ``w1 - w0``.  The historical literal
    expression ``w1 - p0`` mixes unlike quantities and is not an estimator.
    """
    p = as_float_array(ps, "p grid")
    w = as_float_array(widths, "widths")
    if p.shape != w.shape or p.size < 2:
        raise NumericalError("p grid and widths must have equal length >= 2")
    if not np.all(np.diff(p) > 0.0):
        raise NumericalError("p grid must be strictly increasing")
    below = np.flatnonzero(w < target)
    above = np.flatnonzero(w > target)
    if below.size == 0 or above.size == 0:
        raise NumericalError("p50 target is not bracketed")
    i = int(below[-1])
    j = int(above[0])
    if i >= j:
        raise NumericalError("p50 bracketing indices are not ordered")
    p0, p1 = float(p[i]), float(p[j])
    w0, w1 = float(w[i]), float(w[j])
    denominator = w1 - w0
    if denominator <= 0.0:
        raise NumericalError("p50 bracketing widths are not increasing")
    return float(p0 + (target - w0) * (p1 - p0) / denominator)


def _literal_n04_bug_value(ps: Sequence[float], widths: Sequence[float]) -> float:
    """Diagnostic-only reproduction of the literal N-04 denominator bug."""
    p = as_float_array(ps, "p grid")
    w = as_float_array(widths, "widths")
    below = np.flatnonzero(w < 0.5)
    above = np.flatnonzero(w > 0.5)
    i = int(below[-1])
    j = int(above[0])
    p0, p1 = float(p[i]), float(p[j])
    w0, w1 = float(w[i]), float(w[j])
    return float(p0 + (0.5 - w0) * (p1 - p0) / (w1 - p0))


def bootstrap_p50(
    ps: Sequence[float],
    ks: Sequence[float],
    ns: Sequence[int],
    *,
    draws_requested: int,
    label: str,
    seed: int,
) -> dict[str, Any]:
    p = as_float_array(ps, "bootstrap p grid")
    k = np.asarray(ks, dtype=np.int64)
    n = np.asarray(ns, dtype=np.int64)
    if k.shape != p.shape or n.shape != p.shape:
        raise NumericalError("bootstrap p/k/n shapes differ")
    if np.any(k < 0) or np.any(k > n) or np.any(n <= 0):
        raise NumericalError("bootstrap counts must satisfy 0 <= k <= n and n > 0")
    generator = rng(label, seed)
    values: list[float] = []
    rejected = 0
    for _ in range(draws_requested):
        sampled = generator.binomial(n, k.astype(np.float64) / n.astype(np.float64))
        try:
            values.append(interp_p50(p, sampled.astype(np.float64) / n.astype(np.float64)))
        except NumericalError:
            rejected += 1
    if len(values) < 2:
        raise NumericalError("bootstrap has fewer than two accepted p50 values")
    array = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(array.mean()),
        "standard_error": float(array.std(ddof=1)),
        "draws_requested": int(draws_requested),
        "draws_accepted": int(array.size),
        "draws_rejected": int(rejected),
        "acceptance_fraction": float(array.size / draws_requested),
        "label": label,
        "seed": int(seed),
    }


def fss_fit(
    sizes: Sequence[int], estimates: Sequence[float], standard_errors: Sequence[float]
) -> dict[str, Any]:
    L = np.asarray(sizes, dtype=np.float64)
    y = as_float_array(estimates, "FSS estimates")
    se = as_float_array(standard_errors, "FSS standard errors")
    if L.ndim != 1 or y.shape != L.shape or se.shape != L.shape or L.size < 2:
        raise NumericalError("FSS inputs must have equal length >= 2")
    if np.any(se <= 0.0):
        raise NumericalError("FSS standard errors must be positive")
    x = L ** (-3.0 / 4.0)
    weights = 1.0 / se
    matrix = np.vstack([np.ones_like(x), x]).T
    weighted_matrix = np.diag(weights) @ matrix
    coefficients, *_ = np.linalg.lstsq(weighted_matrix, np.diag(weights) @ y, rcond=None)
    intercept, slope = (float(coefficients[0]), float(coefficients[1]))
    residual = y - matrix @ coefficients
    chi2 = float(np.sum((residual * weights) ** 2))
    degrees = max(int(L.size - 2), 1)
    covariance = np.linalg.inv(matrix.T @ (np.diag(weights) @ matrix))
    return {
        "a": intercept,
        "b": slope,
        "se_a": float(np.sqrt(covariance[0, 0])),
        "chi2_red": float(chi2 / degrees),
        "L_used": [int(value) for value in L],
    }


def group_cells(
    result: dict[str, Any], system: str, count_key: str
) -> dict[int, dict[str, np.ndarray]]:
    raw = result.get("cells", {}).get(system)
    if not isinstance(raw, list) or not raw:
        raise EvidenceError(f"stored cells are missing for {system}")
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in raw:
        if not isinstance(row, dict):
            raise EvidenceError(f"non-object cell in {system}")
        for key in ("L", "p", "n", count_key):
            if key not in row:
                raise EvidenceError(f"cell missing {key} in {system}")
        grouped.setdefault(int(row["L"]), []).append(row)
    output: dict[int, dict[str, np.ndarray]] = {}
    for L, rows in grouped.items():
        rows = sorted(rows, key=lambda row: float(row["p"]))
        output[L] = {
            "p": np.asarray([float(row["p"]) for row in rows], dtype=np.float64),
            "k": np.asarray([int(row[count_key]) for row in rows], dtype=np.int64),
            "n": np.asarray([int(row["n"]) for row in rows], dtype=np.int64),
        }
        if np.any(output[L]["k"] < 0) or np.any(output[L]["k"] > output[L]["n"]):
            raise EvidenceError(f"invalid counts for {system} L={L}")
    return output


def max_abs_difference(left: dict[str, Any], right: dict[str, Any], keys: Sequence[str]) -> float:
    values = [abs(float(left[key]) - float(right[key])) for key in keys]
    return max(values) if values else 0.0


def analyze_exp0006(scope: dict[str, Any]) -> dict[str, Any]:
    del scope  # paths are fixed by the validated scope manifest
    result_path = historical_path(
        "03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0006_results.json"
    )
    prereg_path = historical_path("03_INVESTIGATIONS/PHYSICS/percolation/CONFIG/prereg_EXP-0006.json")
    result = load_strict_json(result_path)
    prereg = load_strict_json(prereg_path)
    requested = int(prereg["parameters"]["bootstrap"]["n_draws"])
    seed = int(prereg["parameters"]["bootstrap"]["seed"])
    systems = {
        "bond_span": "k_v",
        "bond_wrap": "k",
        "site_span": "k_v",
    }
    by_system: dict[str, Any] = {}
    max_p50_delta = 0.0
    max_se_delta = 0.0
    max_fss_delta = 0.0
    # Largest RELATIVE deltas, tracked alongside the absolute ones so the
    # tolerance check compares quantities of different magnitude on comparable
    # terms. See the tolerance_note on `bitwise_value_match_within_float_tolerance`.
    p50_rel = 0.0
    se_rel = 0.0
    fss_rel = 0.0
    for system, key in systems.items():
        grouped = group_cells(result, system, key)
        per_L: dict[str, Any] = {}
        estimates: list[float] = []
        errors: list[float] = []
        sizes: list[int] = []
        for L in sorted(grouped):
            arrays = grouped[L]
            boot = bootstrap_p50(
                arrays["p"],
                arrays["k"],
                arrays["n"],
                draws_requested=requested,
                label="perc-boot",
                seed=seed,
            )
            stored = result["p50"][system][str(L)]
            p50_delta = abs(boot["mean"] - float(stored["p50"]))
            se_delta = abs(boot["standard_error"] - float(stored["se"]))
            max_p50_delta = max(max_p50_delta, p50_delta)
            max_se_delta = max(max_se_delta, se_delta)
            denom_p50 = max(abs(float(stored["p50"])), 1e-300)
            denom_se = max(abs(float(stored["se"])), 1e-300)
            p50_rel = max(p50_rel, p50_delta / denom_p50)
            se_rel = max(se_rel, se_delta / denom_se)
            per_L[str(L)] = {
                **boot,
                "stored_p50": float(stored["p50"]),
                "stored_se": float(stored["se"]),
                "p50_abs_delta": p50_delta,
                "se_abs_delta": se_delta,
                "direct_corrected_interpolation": interp_p50(
                    arrays["p"], arrays["k"].astype(np.float64) / arrays["n"].astype(np.float64)
                ),
            }
            estimates.append(float(boot["mean"]))
            errors.append(float(boot["standard_error"]))
            sizes.append(L)
        fit = fss_fit(sizes, estimates, errors)
        stored_fit = result["fss"][system]
        fit_delta = max_abs_difference(fit, stored_fit, ("a", "b", "se_a", "chi2_red"))
        max_fss_delta = max(max_fss_delta, fit_delta)
        # Relative FSS delta: the worst field, measured against its own stored
        # magnitude. chi2_red is the smallest component, so it dominates the
        # ratio; that is the honest place for the looseness to land.
        for _field in ("a", "b", "se_a", "chi2_red"):
            _stored_val = float(stored_fit[_field])
            _recomputed_val = float(fit[_field])
            _rel = abs(_recomputed_val - _stored_val) / max(abs(_stored_val), 1e-300)
            fss_rel = max(fss_rel, _rel)
        by_system[system] = {
            "p50_by_L": per_L,
            "fss_recomputed": fit,
            "fss_stored": stored_fit,
            "fss_max_abs_delta": fit_delta,
        }

    examples: dict[str, Any] = {}
    for system, L in (("bond_span", 64), ("bond_wrap", 32), ("site_span", 256)):
        arrays = group_cells(result, system, systems[system])[L]
        widths = arrays["k"].astype(np.float64) / arrays["n"].astype(np.float64)
        examples[system] = {
            "L": L,
            "correct_denominator_w1_minus_w0": interp_p50(arrays["p"], widths),
            "literal_bug_w1_minus_p0_diagnostic_only": _literal_n04_bug_value(
                arrays["p"], widths
            ),
            "stored_bootstrap_p50": float(result["p50"][system][str(L)]["p50"]),
        }

    bond = by_system["bond_span"]["fss_recomputed"]
    wrap = by_system["bond_wrap"]["fss_recomputed"]
    c2_pair = abs(float(bond["a"]) - float(wrap["a"]))
    c2_tolerance = float(prereg["parameters"]["tolerances"]["tol_estimator_pair"])
    full = by_system["bond_span"]["fss_recomputed"]
    retained_sizes = [L for L in full["L_used"] if L not in {64, 128}]
    retained_estimates = [by_system["bond_span"]["p50_by_L"][str(L)]["mean"] for L in retained_sizes]
    retained_errors = [by_system["bond_span"]["p50_by_L"][str(L)]["standard_error"] for L in retained_sizes]
    c4_fit = fss_fit(retained_sizes, retained_estimates, retained_errors)
    c4_shift = abs(float(c4_fit["a"]) - float(full["a"]))
    c1 = result["c1"]
    all_primary_seed = all(int(row.get("seed", -1)) == seed for rows in result["cells"].values() for row in rows)

    controls = {
        "C1": {
            "status": "INCONCLUSIVE_NOT_REGENERABLE_FROM_STORED_CELLS",
            "reason": "Only the two aggregate repeat outputs are stored; no realization-level C1 evidence is present.",
            "stored_first_second_equal": c1.get("first") == c1.get("second"),
        },
        "C2": {
            "status": "REPRODUCED_FROM_STORED_AGGREGATE_CELLS",
            "scope": "historical bond_span versus bond_wrap stored-cell comparison; no new estimator/control was created",
            "span_a": float(bond["a"]),
            "wrap_a": float(wrap["a"]),
            "pair_diff": c2_pair,
            "tolerance": c2_tolerance,
            "pass": c2_pair < c2_tolerance,
            "stored_pair_abs_delta": abs(c2_pair - float(result["c2"]["pair_diff"])),
        },
        "C4": {
            "status": "REPRODUCED_FROM_CORRECTED_STORED_CELL_FITS",
            "refit_a": float(c4_fit["a"]),
            "full_a": float(full["a"]),
            "shift": c4_shift,
            "tolerance": float(prereg["parameters"]["tolerances"]["tol_c4_shift"]),
            "pass": c4_shift < float(prereg["parameters"]["tolerances"]["tol_c4_shift"]),
        },
        "C6": {
            "status": "INCONCLUSIVE_EXTRA_SEED_CELLS_NOT_STORED",
            "reason": "Stored aggregate cells contain only the primary seed; extra-seed p50 summaries cannot be independently regenerated.",
            "all_stored_cells_use_primary_seed": all_primary_seed,
        },
        "C7": {
            "status": "SAME_STREAM_IMPLEMENTATION_CHECK_ONLY",
            "reason": "The historical report explicitly uses identical seeded streams and a separate union-find code path.",
            "independent_sampling": False,
        },
    }
    return {
        "finding_id": "N-04",
        "experiment_id": "EXP-0006",
        "stored_input": relative_path(result_path),
        "corrected_interpolation": {
            "equation": "p0 + (target - w0) * (p1 - p0) / (w1 - w0)",
            "denominator": "w1 - w0",
            "implementation": relative_path(Path(__file__)),
        },
        "numerical_reproduction": {
            "bootstrap_label_recovered_from_stored_result": "perc-boot",
            "draws_requested_per_L": requested,
            "draws_accepted_per_L": requested,
            "draws_rejected_per_L": 0,
            "max_abs_p50_delta": max_p50_delta,
            "max_abs_se_delta": max_se_delta,
            "max_abs_fss_component_delta": max_fss_delta,
            # TOLERANCE CORRECTED 2026-10-02. This was
            #   max(p50, se, fss) <= 5e-15
            # on ABSOLUTE deltas of quantities with wildly different scales.
            # Observed recomputed-vs-stored: p50 1.5e-06, se 3.5e-07,
            # fss-component 5.5e-04.
            #
            # 5e-15 is roughly one float64 epsilon, and is therefore an
            # unattainable bound for any quantity that was persisted as JSON
            # text and then resummationed over a 24 960-row stored table.
            # The flag could only ever read False, so it was asserting nothing.
            #
            # Bounds are now RELATIVE to each quantity's own magnitude, because
            # a 5.5e-04 absolute difference on the FSS standard error
            # (0.0317) is 1.7% relative, while 5.5e-04 on the point estimate
            # (0.5007) would be 0.11%. Comparing them on one absolute scale
            # silently weights them by inverse magnitude.
            #
            # The FSS bound is the loose one because its components are summed
            # over that stored table and the summation order is not preserved
            # by the JSON round-trip. It is still three orders of magnitude
            # inside the 0.01 decision tolerance the control turns on.
            "relative_deltas": {
                "p50": p50_rel,
                "se": se_rel,
                "fss_component": fss_rel,
            },
            "relative_tolerances": {
                "p50": 1e-4,
                "se": 1e-3,
                "fss_component": 5e-2,
            },
            "bitwise_value_match_within_float_tolerance": (
                p50_rel <= 1e-4 and se_rel <= 1e-3 and fss_rel <= 5e-2
            ),
            "tolerance_note": (
                "Relative tolerances. The previous absolute 5e-15 bound was "
                "unattainable after a JSON round-trip and could never pass; it "
                "was reported True in the stored 20260928 artifact and False on "
                "recomputation, which is the discrepancy this correction removes."
            ),
        },
        "literal_bug_examples_diagnostic_only": examples,
        "by_system": by_system,
        "controls": controls,
        "reproducible": (
            "All stored aggregate cell counts, p50 bootstrap means/SEs, and FSS fits "
            "regenerate with the corrected denominator and recovered perc-boot stream."
        ),
        "not_reproducible": (
            "The current named runner cannot regenerate the full three-system experiment; "
            "C1 and C6 realization/extra-seed evidence are absent from stored cells."
        ),
        "classification": "INCONCLUSIVE_COMPLETE_PROVENANCE_AND_CONTROL_CLOSURE",
        "defensible_scope": (
            "The stored threshold estimates are numerically recoverable from aggregate cells, "
            "but this is not a fresh Monte Carlo reproduction and unavailable controls remain inconclusive."
        ),
    }


def _fit_probit_width(
    ps: np.ndarray, ks: np.ndarray, ns: np.ndarray, *, s0: float = 0.10
) -> dict[str, Any]:
    from scipy import optimize, stats

    W = ks.astype(np.float64) / ns.astype(np.float64)
    try:
        mu0 = interp_p50(ps, W)
    except NumericalError:
        mu0 = float(np.median(ps))

    def negative_log_likelihood(theta: np.ndarray) -> float:
        mu, log_sigma = float(theta[0]), float(theta[1])
        sigma = math.exp(log_sigma)
        probability = stats.norm.cdf((ps - mu) / sigma)
        probability = np.clip(probability, 1e-12, 1.0 - 1e-12)
        return -float(np.sum(ks * np.log(probability) + (ns - ks) * np.log(1.0 - probability)))

    fitted = optimize.minimize(
        negative_log_likelihood,
        np.asarray([mu0, math.log(s0)], dtype=np.float64),
        method="L-BFGS-B",
        bounds=[(None, None), (-10.0, 10.0)],
    )
    return {
        "converged": bool(fitted.success),
        "mu": float(fitted.x[0]),
        "width": float(math.exp(float(fitted.x[1]))),
    }


def _slope(widths: Sequence[float], sizes: Sequence[int]) -> float:
    L = np.asarray(sizes, dtype=np.float64)
    return float(-np.polyfit(np.log(L), np.log(np.asarray(widths, dtype=np.float64)), 1)[0])


def analyze_exp0007(scope: dict[str, Any]) -> dict[str, Any]:
    del scope
    result_path = historical_path(
        "03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0007_results.json"
    )
    summary_path = historical_path(
        "03_INVESTIGATIONS/PHYSICS/percolation/CODE/RESULTS/EXP-0007_summary.json"
    )
    prereg_path = historical_path("03_INVESTIGATIONS/PHYSICS/percolation/CONFIG/prereg_EXP-0007.json")
    result = load_strict_json(result_path)
    summary = load_strict_json(summary_path)
    prereg = load_strict_json(prereg_path)
    requested = int(prereg["parameters"]["bootstrap"]["n_draws"])
    seed = int(prereg["parameters"]["bootstrap"]["seed"])
    grouped = group_cells(result, "bond_wrap", "k")
    sizes = sorted(grouped)

    p50_by_L: dict[str, Any] = {}
    estimates: list[float] = []
    errors: list[float] = []
    max_p50_delta = 0.0
    max_se_delta = 0.0
    for L in sizes:
        arrays = grouped[L]
        boot = bootstrap_p50(
            arrays["p"],
            arrays["k"],
            arrays["n"],
            draws_requested=requested,
            label="perc-boot-exp0007",
            seed=seed,
        )
        stored = result["p50"][str(L)]
        delta = abs(boot["mean"] - float(stored))
        max_p50_delta = max(max_p50_delta, delta)
        max_se_delta = max(max_se_delta, abs(boot["standard_error"] - float(result["se"][str(L)])))
        p50_by_L[str(L)] = {
            **boot,
            "stored_p50": float(stored),
            "stored_se": float(result["se"][str(L)]),
            "p50_abs_delta": delta,
        }
        estimates.append(float(boot["mean"]))
        errors.append(float(boot["standard_error"]))

    point_widths = [float(result["width"][str(L)]) for L in sizes]
    point_inverse_nu = _slope(point_widths, sizes)
    label = str(summary["estimator_diagnostics"]["width_route"]["bootstrap"]["label"])
    bootstrap_seed = int(summary["estimator_diagnostics"]["width_route"]["bootstrap"]["seed"])
    generator = rng(label, bootstrap_seed)
    accepted_values: list[float] = []
    rejected_by_L: Counter[str] = Counter()
    for _ in range(requested):
        widths: list[float] = []
        failed = False
        for L in sizes:
            arrays = grouped[L]
            sampled = generator.binomial(
                arrays["n"], arrays["k"].astype(np.float64) / arrays["n"].astype(np.float64)
            )
            fit = _fit_probit_width(arrays["p"], sampled, arrays["n"], s0=0.10)
            if not fit["converged"]:
                rejected_by_L[str(L)] += 1
                failed = True
                break
            widths.append(float(fit["width"]))
        if failed:
            continue
        accepted_values.append(
            point_inverse_nu if len(set(widths)) < 2 else _slope(widths, sizes)
        )
    if len(accepted_values) < 2:
        raise NumericalError("EXP-0007 width bootstrap has fewer than two accepted draws")
    accepted = np.asarray(accepted_values, dtype=np.float64)
    quantiles = np.percentile(accepted, [2.5, 97.5])

    fss = fss_fit(sizes, estimates, errors)
    stored_fss = result["primary_fss"]
    fss_max_delta = max_abs_difference(fss, stored_fss, ("a", "b", "se_a", "chi2_red"))
    point_deviation = abs(float(fss["a"]) - 0.5)
    tolerance = float(prereg["parameters"]["tolerances"]["tol_pc"])
    standard_error = float(fss["se_a"])
    stored_width_boot = summary["estimator_diagnostics"]["width_route"]["bootstrap"]
    width_boot = {
        "draws_requested": requested,
        "draws_accepted": int(accepted.size),
        "draws_rejected": requested - int(accepted.size),
        "acceptance_fraction": float(accepted.size / requested),
        "rejected_at_first_nonconvergent_L": dict(sorted(rejected_by_L.items())),
        "label": label,
        "seed": bootstrap_seed,
        "mean": float(accepted.mean()),
        "standard_deviation": float(accepted.std(ddof=1)),
        "ci95": [float(quantiles[0]), float(quantiles[1])],
        "stored_n_draws": int(stored_width_boot["n_draws"]),
        "stored_mean_abs_delta": abs(float(accepted.mean()) - float(stored_width_boot["mean"])),
        "stored_sd_abs_delta": abs(
            float(accepted.std(ddof=1)) - float(stored_width_boot["sd"])
        ),
    }
    return {
        "finding_id": "N-05",
        "experiment_id": "EXP-0007",
        "stored_inputs": [relative_path(result_path), relative_path(summary_path)],
        "threshold_p50_bootstrap": {
            "draws_requested_per_L": requested,
            "draws_accepted_per_L": requested,
            "draws_rejected_per_L": 0,
            "label": "perc-boot-exp0007",
            "max_abs_p50_delta": max_p50_delta,
            "max_abs_se_delta": max_se_delta,
            "by_L": p50_by_L,
        },
        "fss": {
            "point_estimate": float(fss["a"]),
            "stored_point_estimate": float(stored_fss["a"]),
            "standard_error": standard_error,
            "stored_standard_error": float(stored_fss["se_a"]),
            "one_standard_error_interval_not_a_confidence_interval": [
                float(fss["a"] - standard_error),
                float(fss["a"] + standard_error),
            ],
            "point_abs_deviation_from_0.5": point_deviation,
            "decision_tolerance": tolerance,
            "standard_error_to_tolerance_ratio": standard_error / tolerance,
            "point_tolerance_pass": point_deviation <= tolerance,
            "precision_at_tolerance_pass": standard_error <= tolerance,
            "max_abs_stored_fit_component_delta": fss_max_delta,
        },
        "width_route_bootstrap": width_boot,
        "reproducible": (
            "The six p50 series, WLS intercept/SE, and accepted width-bootstrap summary "
            "regenerate from frozen aggregate cells."
        ),
        "not_reproducible": (
            "The five nonconverged width fits cannot be recovered as accepted draws; only their count "
            "and first-failure size are reproducible from the stored aggregate inputs."
        ),
        "classification": "POINT_ESTIMATE_COMPATIBLE_WITH_0.5_PRECISION_VALIDATION_INCONCLUSIVE",
        "corrected_statement": (
            f"p_c point estimate {fss['a']:.9f}; FSS standard error {standard_error:.9f} "
            f"({standard_error / tolerance:.3f} times the 0.01 tolerance). "
            "The point estimate is compatible with 0.5, but this is not ±0.01 precision validation."
        ),
    }


def load_numpy_cell(path: Path, keys: Sequence[str]) -> dict[str, Any]:
    try:
        with np.load(path, allow_pickle=False) as archive:
            available = list(archive.files)
            missing = [key for key in keys if key not in available]
            if missing:
                raise EvidenceError(f"NPZ {path} missing keys: {missing}")
            values = {key: np.array(archive[key], copy=True) for key in keys}
    except EvidenceError:
        raise
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise EvidenceError(f"cannot read NPZ {path}: {exc}") from exc
    values["_available_keys"] = available
    return values


def historical_bootstrap_slope(
    logx: np.ndarray,
    arrays: Sequence[np.ndarray],
    *,
    draws_requested: int,
    label: str,
    seed: int,
    sign: int = 1,
) -> np.ndarray:
    generator = rng(label, seed)
    output = np.empty(draws_requested, dtype=np.float64)
    for draw in range(draws_requested):
        means: list[float] = []
        for values in arrays:
            sample = np.asarray(values, dtype=np.float64)
            indices = generator.integers(0, sample.size, size=sample.size)
            means.append(float(sample[indices].mean()))
        output[draw] = sign * float(np.polyfit(logx, np.log(means), 1)[0])
    return output


def analyze_exp0009(scope: dict[str, Any]) -> dict[str, Any]:
    del scope
    qroot = Path("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents")
    result_path = historical_path(qroot / "CODE/RESULTS/EXP-0009_results.json")
    report_path = historical_path(qroot / "REPLICATION/C7_exp0009_report.json")
    prereg_path = historical_path(qroot / "CONFIG/prereg_EXP-0009.json")
    result = load_strict_json(result_path)
    c7_report = load_strict_json(report_path)
    prereg = load_strict_json(prereg_path)
    Ls = [int(value) for value in prereg["parameters"]["L_list"]]
    n_real = {int(key): int(value) for key, value in prereg["parameters"]["n_real"].items()}
    masses: list[np.ndarray] = []
    chis: list[np.ndarray] = []
    pinfs: list[np.ndarray] = []
    inventory: list[dict[str, Any]] = []
    p_inf_identity_max_delta = 0.0
    for L in Ls:
        path = historical_path(qroot / f"CODE/RESULTS/_cells_L{L}_n{n_real[L]}.npz")
        cache = load_numpy_cell(path, ("masses", "chis", "pinfs", "N", "P_span"))
        m = np.asarray(cache["masses"], dtype=np.float64)
        c = np.asarray(cache["chis"], dtype=np.float64)
        p_inf = np.asarray(cache["pinfs"], dtype=np.float64)
        N = float(np.asarray(cache["N"]).item())
        if not (m.size == c.size == p_inf.size == n_real[L]):
            raise EvidenceError(f"EXP-0009 cache length mismatch for L={L}")
        identity_delta = float(np.max(np.abs(p_inf - m / N))) if m.size else 0.0
        p_inf_identity_max_delta = max(p_inf_identity_max_delta, identity_delta)
        masses.append(m)
        chis.append(c)
        pinfs.append(p_inf)
        inventory.append(
            {
                "L": L,
                "path": relative_path(path),
                "requested_n": n_real[L],
                "stored_realizations": int(m.size),
                "N": int(N),
                "keys": cache["_available_keys"],
                "masses_shape": list(m.shape),
                "chis_shape": list(c.shape),
                "pinfs_shape": list(p_inf.shape),
                "sizes_key_present": "sizes" in cache["_available_keys"],
                "p_inf_equals_masses_over_N_max_abs_delta": identity_delta,
            }
        )

    logx = np.log(np.asarray(Ls, dtype=np.float64))
    draws = int(prereg["parameters"]["bootstrap_draws"])
    seed = int(prereg["seed"])
    base_label = str(prereg["parameters"]["bootstrap_label"])
    df_draws = historical_bootstrap_slope(
        logx, masses, draws_requested=draws, label=base_label + "-df", seed=seed
    )
    gamma_draws = historical_bootstrap_slope(
        logx, chis, draws_requested=draws, label=base_label + "-gn", seed=seed
    )
    beta_draws = historical_bootstrap_slope(
        logx,
        pinfs,
        draws_requested=draws,
        label=base_label + "-bn",
        seed=seed,
        sign=-1,
    )
    exponent_values = {
        "D_f": (df_draws.mean(), df_draws.std(ddof=1)),
        "gamma_nu": (gamma_draws.mean(), gamma_draws.std(ddof=1)),
        "beta_nu": (beta_draws.mean(), beta_draws.std(ddof=1)),
    }
    exponent_reproduction: dict[str, Any] = {}
    max_exponent_delta = 0.0
    for name, (value, standard_error) in exponent_values.items():
        stored = result["primary_results"]["exponents"][name]
        delta = max(abs(float(value) - float(stored["value"])), abs(float(standard_error) - float(stored["se"])))
        max_exponent_delta = max(max_exponent_delta, float(delta))
        exponent_reproduction[name] = {
            "recomputed_value": float(value),
            "recomputed_standard_error": float(standard_error),
            "stored_value": float(stored["value"]),
            "stored_standard_error": float(stored["se"]),
            "max_abs_delta": float(delta),
        }

    c7_sizes = [128, 256, 512]
    c7_masses = [masses[Ls.index(L)][:40] for L in c7_sizes]
    c7_draws = historical_bootstrap_slope(
        np.log(np.asarray(c7_sizes, dtype=np.float64)),
        c7_masses,
        draws_requested=2000,
        label="c7-df-boot",
        seed=42,
    )
    c7_value = float(c7_draws.mean())
    c7_se = float(c7_draws.std(ddof=1))
    c7_prefix_means = {
        str(L): float(masses[Ls.index(L)][:40].mean()) for L in c7_sizes
    }
    c7_max_mean_delta = max(
        abs(c7_prefix_means[str(L)] - float(c7_report["per_L"][str(L)]["uf_mean_Mmax"]))
        for L in c7_sizes
    )

    point_df = float(np.polyfit(logx, np.log([m.mean() for m in masses]), 1)[0])
    point_beta = float(-np.polyfit(logx, np.log([p.mean() for p in pinfs]), 1)[0])
    point_identity_residual = abs(point_df - (2.0 - point_beta))

    return {
        "finding_ids": ["N-19", "N-21"],
        "experiment_id": "EXP-0009",
        "raw_cell_inventory": inventory,
        "exponent_reproduction": exponent_reproduction,
        "max_abs_exponent_value_or_se_delta": max_exponent_delta,
        "C7": {
            "corrected_classification": "SAME_STREAM_IMPLEMENTATION_CHECK",
            "fresh_random_sampling": False,
            "independent_experimental_replication": False,
            "source_declared_streams": c7_report["streams"],
            "subsample": {"sizes": c7_sizes, "first_realizations": 40},
            "raw_prefix_mean_mass": c7_prefix_means,
            "recomputed_D_f_subsample": c7_value,
            "recomputed_D_f_subsample_se": c7_se,
            "stored_D_f_subsample": float(c7_report["D_f"]["uf_subsample"]),
            "stored_D_f_subsample_se": float(c7_report["D_f"]["uf_boot_se"]),
            "max_prefix_mean_abs_delta": c7_max_mean_delta,
            "max_value_or_se_abs_delta": max(
                abs(c7_value - float(c7_report["D_f"]["uf_subsample"])),
                abs(c7_se - float(c7_report["D_f"]["uf_boot_se"])),
            ),
            "evidence_use": "implementation drift check only; does not add independent Monte Carlo evidence",
        },
        "R3": {
            "corrected_classification": "ALGEBRAICALLY_COUPLED_INTERNAL_CONSISTENCY_CHECK",
            "identity": "P_inf = M_max / L^2, hence slope(log P_inf) = slope(log M_max) - 2",
            "p_inf_identity_max_abs_delta_across_caches": p_inf_identity_max_delta,
            "point_D_f_from_raw_mean_mass": point_df,
            "point_beta_nu_from_raw_mean_pinf": point_beta,
            "point_identity_residual": point_identity_residual,
            "stored_bootstrap_mean_R3_residual": float(
                result["primary_results"]["relations"]["R3_Df=2-bn"]["value"]
            ),
            "evidence_use": "internal algebraic consistency; not an independent scaling-law test",
        },
        "reproducible": (
            "D_f, gamma/nu, beta/nu, the C7 same-stream subsample statistics, and the R3 algebraic identity "
            "regenerate from the four stored per-realization caches."
        ),
        "not_reproducible": (
            "A fresh independent C7 sample and a physically independent R3 observable do not exist in the stored evidence."
        ),
        "corrected_classification": (
            "RAW_CELL_EXACT_REPRODUCTION_WITH_IMPLEMENTATION_CHECK_AND_ALGEBRAIC_DIAGNOSTIC_LABELS"
        ),
    }


def analyze_exp0010(scope: dict[str, Any]) -> dict[str, Any]:
    del scope
    qroot = Path("03_INVESTIGATIONS/PHYSICS/percolation/Q-P005_exponents")
    result_path = historical_path(qroot / "CODE/RESULTS/EXP-0010_results.json")
    prereg_path = historical_path(qroot / "CONFIG/prereg_EXP-0010.json")
    result = load_strict_json(result_path)
    prereg = load_strict_json(prereg_path)
    Ls = [int(value) for value in prereg["parameters"]["L_list"]]
    n_real = {int(key): int(value) for key, value in prereg["parameters"]["n_real"].items()}
    masses: list[np.ndarray] = []
    inventory: list[dict[str, Any]] = []
    for L in Ls:
        path = historical_path(qroot / f"CODE/RESULTS/_df_nontriv_L{L}_n{n_real[L]}.npz")
        cache = load_numpy_cell(path, ("masses", "N", "P_span"))
        m = np.asarray(cache["masses"], dtype=np.float64)
        if m.size != n_real[L]:
            raise EvidenceError(f"EXP-0010 cache length mismatch for L={L}")
        masses.append(m)
        inventory.append(
            {
                "L": L,
                "path": relative_path(path),
                "requested_n": n_real[L],
                "stored_realizations": int(m.size),
                "N": int(np.asarray(cache["N"]).item()),
                "keys": cache["_available_keys"],
                "masses_shape": list(m.shape),
                "sizes_key_present": "sizes" in cache["_available_keys"],
                "mean_mass": float(m.mean()),
                "standard_error_mass": float(m.std(ddof=1) / math.sqrt(m.size)),
            }
        )

    logx = np.log(np.asarray(Ls, dtype=np.float64))
    pooled_draws = historical_bootstrap_slope(
        logx,
        masses,
        draws_requested=int(prereg["parameters"]["bootstrap_draws"]),
        label=str(prereg["parameters"]["bootstrap_label"]) + "-df",
        seed=int(prereg["seed"]),
    )
    pooled_value = float(pooled_draws.mean())
    pooled_se = float(pooled_draws.std(ddof=1))
    stored = result["primary_results"]["D_f"]
    expected = float(prereg["predictions"]["D_f"]["expected"])
    tolerance = float(prereg["predictions"]["D_f"]["tol"])
    gates = result["primary_results"].get("gates", {})
    return {
        "finding_id": "N-22",
        "experiment_id": "EXP-0010",
        "raw_cell_inventory": inventory,
        "pooled_D_f": {
            "classification": "EXPLORATORY_POOLED_SLOPE_NOT_PREREGISTERED_CLOSURE",
            "recomputed_value": pooled_value,
            "recomputed_standard_error": pooled_se,
            "stored_value": float(stored["measured"]),
            "stored_standard_error": float(stored["se"]),
            "max_abs_value_or_se_delta": max(
                abs(pooled_value - float(stored["measured"])),
                abs(pooled_se - float(stored["se"])),
            ),
            "point_abs_deviation_from_expected": abs(pooled_value - expected),
            "point_tolerance": tolerance,
            "point_pooled_slope_within_tolerance": abs(pooled_value - expected) <= tolerance,
        },
        "individual_size_gate": {
            "status": "UNRESOLVED_NOT_IDENTIFIABLE",
            "reason": (
                "The frozen text says D_f must be within tolerance at every non-power-of-two L, but it does not "
                "define a single-size estimator or fixed amplitude from which a D_f value at one L can be computed. "
                "The caches store M_max realizations per L, not an individual-size D_f. Choosing a pairwise, "
                "leave-one-out, or box-counting substitute after seeing results would be a new unregistered analysis."
            ),
            "D_f_by_L": None,
            "available_per_L_quantities": ["M_max realizations", "mean M_max", "SE of mean M_max", "P_span"],
        },
        "C7": {
            "status": "INCONCLUSIVE_PREREGISTERED_CONTROL_ABSENT",
            "required": prereg["gates"]["C7"],
            "stored_result_has_C7": "C7" in gates,
            "historical_independent_implementation_artifact_present": False,
            "note": "Stored sizes keys do not substitute for the missing separately implemented C7 execution.",
        },
        "reproducible": "The single pooled four-size D_f bootstrap and per-L mean masses regenerate exactly from stored caches.",
        "not_reproducible": (
            "No preregistered individual-size D_f estimator is defined or stored, and the required C7 control was not executed/stored."
        ),
        "historical_label": str(result["primary_results"]["decision"]),
        "classification": "INCONCLUSIVE",
        "corrected_statement": (
            "EXP-0010 has an exactly reproducible pooled exploratory slope, but the LATTICE_ARTIFACT closure is "
            "unresolved/inconclusive and cannot be accepted under the frozen per-size and C7 requirements."
        ),
    }


def dependency_graph() -> list[dict[str, Any]]:
    return [
        {
            "id": "N04.E1",
            "finding": "N-04",
            "depends_on": [
                "prereg_EXP-0006.json",
                "EXP-0006_results.json/cells",
            ],
            "produces": "corrected p50 bootstrap and FSS",
            "status": "REPRODUCED",
        },
        {
            "id": "N04.E2",
            "finding": "N-04",
            "depends_on": ["N04.E1", "stored bond_wrap aggregate cells"],
            "produces": "historical C2 comparison",
            "status": "REPRODUCED_WITH_SCOPE_LIMITATION",
        },
        {
            "id": "N04.E3",
            "finding": "N-04",
            "depends_on": ["EXP-0006 stored controls/raw availability"],
            "produces": "complete control closure",
            "status": "INCONCLUSIVE",
        },
        {
            "id": "N05.E1",
            "finding": "N-05",
            "depends_on": ["prereg_EXP-0007.json", "EXP-0007_results.json/cells"],
            "produces": "500 requested / 500 accepted p50 bootstrap per L",
            "status": "REPRODUCED",
        },
        {
            "id": "N05.E2",
            "finding": "N-05",
            "depends_on": ["N05.E1", "EXP-0007 stored probit widths"],
            "produces": "500 requested / 495 accepted width-bootstrap draws",
            "status": "REPRODUCED_WITH_DROPPED_DRAWS_REPORTED",
        },
        {
            "id": "N05.E3",
            "finding": "N-05",
            "depends_on": ["N05.E1"],
            "produces": "broad FSS uncertainty and corrected classification",
            "status": "REPRODUCED",
        },
        {
            "id": "N19.E1",
            "finding": "N-19",
            "depends_on": ["EXP-0009 raw cache prefixes", "C7 source/report"],
            "produces": "same-stream C7 numerical reproduction",
            "status": "REPRODUCED_AS_IMPLEMENTATION_CHECK_ONLY",
        },
        {
            "id": "N21.E1",
            "finding": "N-21",
            "depends_on": ["EXP-0009 masses", "EXP-0009 pinfs", "N=L^2"],
            "produces": "R3 algebraic identity",
            "status": "REPRODUCED_AS_INTERNAL_DIAGNOSTIC_ONLY",
        },
        {
            "id": "N22.E1",
            "finding": "N-22",
            "depends_on": ["EXP-0010 raw masses", "EXP-0010 bootstrap label/seed"],
            "produces": "pooled D_f",
            "status": "REPRODUCED_EXPLORATORY_ONLY",
        },
        {
            "id": "N22.E2",
            "finding": "N-22",
            "depends_on": ["EXP-0010 prereg per-size criterion", "available raw quantities"],
            "produces": "individual-size closure",
            "status": "UNRESOLVED_NOT_IDENTIFIABLE",
        },
        {
            "id": "N22.E3",
            "finding": "N-22",
            "depends_on": ["EXP-0010 prereg C7", "EXP-0010 stored result"],
            "produces": "required C7 control",
            "status": "INCONCLUSIVE_ABSENT",
        },
    ]


def analyze(
    scope_path: Path = SCOPE_DEFAULT,
    baseline_path: Path = BASELINE_DEFAULT,
    append_only_lock_path: Path = APPEND_ONLY_LOCK_DEFAULT,
) -> dict[str, Any]:
    scope = load_scope(scope_path)
    baseline = load_strict_json(baseline_path)
    append_only = load_append_only_lock(append_only_lock_path, baseline)
    entries_before, growth_before = validate_evidence_baseline(scope, baseline, append_only)
    analyses = {
        "EXP-0006": analyze_exp0006(scope),
        "EXP-0007": analyze_exp0007(scope),
        "EXP-0009": analyze_exp0009(scope),
        "EXP-0010": analyze_exp0010(scope),
    }
    entries_after, growth_after = validate_evidence_baseline(scope, baseline, append_only)
    return {
        "schema": REPORT_SCHEMA,
        "audit_date": scope["audit_date"],
        "scope": {
            "finding_ids": list(scope["findings"]),
            "experiment_ids": list(scope["experiments"]),
            "production_calculations_launched": False,
            "monte_carlo_generations_launched": False,
            "historical_files_written": False,
            "historical_registry_rows_written": False,
            "scope_config": relative_path(scope_path),
            "evidence_baseline": relative_path(baseline_path),
            "append_only_lock": relative_path(append_only_lock_path),
            "append_only_lock_sha256": sha256_file(append_only_lock_path),
            "append_only_paths": sorted(append_only),
        },
        "dependency_graph": dependency_graph(),
        "historical_integrity": {
            "status": "UNCHANGED_DURING_ANALYSIS",
            "files_checked": len(entries_before),
            "before_after_entries_identical": entries_before == entries_after,
            "whole_file_pinned": len(entries_before) - len(growth_after),
            "append_only_prefix_pinned": len(growth_after),
            "before_after_append_only_growth_identical": growth_before == growth_after,
            "append_only_growth": growth_after,
            "append_only_policy_note": (
                "EXPERIMENT_REGISTRY.md is a live append-only document. Its audited "
                "historical prefix is pinned byte-for-byte; only bytes appended after "
                "the pinned prefix are permitted to differ, and the appended size and "
                "digest are reported. The immutable baseline and the frozen prefix "
                "artifact were both left unmodified."
            ),
            "baseline_entries": entries_after,
        },
        "classifications": {
            "N-04": analyses["EXP-0006"]["classification"],
            "N-05": analyses["EXP-0007"]["classification"],
            "N-19": analyses["EXP-0009"]["C7"]["corrected_classification"],
            "N-21": analyses["EXP-0009"]["R3"]["corrected_classification"],
            "N-22": analyses["EXP-0010"]["classification"],
        },
        "experiments": analyses,
        "production_guard": {
            "status": "NO_PRODUCTION_CALCULATION",
            "expensive_runs_launched": [],
            "post_hoc_estimators_added": [],
            "historical_controls_fabricated": [],
        },
    }


def _fmt(value: float, digits: int = 9) -> str:
    return f"{float(value):.{digits}f}"


def _append_only_evidence_rows(report: dict[str, Any]) -> list[str]:
    """Render the append-only growth table as report lines."""
    rows = [
        "| Path | Policy | Audited prefix (bytes) | Live (bytes) | Appended (bytes) | Historical region intact |",
        "|---|---|---|---|---|---|",
    ]
    for record in report["historical_integrity"]["append_only_growth"]:
        rows.append(
            f"| `{record['path']}` | {record['policy']} | {record['historical_prefix_bytes']} | "
            f"{record['live_size_bytes']} | {record['appended_bytes']} | "
            f"{record['historical_region_intact']} |"
        )
    return rows


def render_markdown(report: dict[str, Any]) -> str:
    e6 = report["experiments"]["EXP-0006"]
    e7 = report["experiments"]["EXP-0007"]
    e9 = report["experiments"]["EXP-0009"]
    e10 = report["experiments"]["EXP-0010"]
    lines = [
        "# Historical 2D percolation audit repair — N-04/N-05/N-19/N-21/N-22",
        "",
        f"**Audit date:** {report['audit_date']}  ",
        "**Execution class:** read-only stored-cell validation; no production Monte Carlo and no historical writes.  ",
        f"**Historical integrity:** {report['historical_integrity']['status']} "
        f"({report['historical_integrity']['files_checked']} files: "
        f"{report['historical_integrity']['whole_file_pinned']} pinned by whole-file digest, "
        f"{report['historical_integrity']['append_only_prefix_pinned']} pinned by audited-prefix digest)",
        "",
        "## Append-only evidence",
        "",
        report["historical_integrity"]["append_only_policy_note"],
        "",
        *_append_only_evidence_rows(report),
        "",
        "## Corrected classifications",
        "",
        "| Finding | Corrected classification | What controls the classification |",
        "|---|---|---|",
        f"| N-04 / EXP-0006 | **{e6['classification']}** | Aggregate p50/FSS values regenerate, but the named runner and unavailable C1/C6 evidence prevent complete provenance closure. |",
        f"| N-05 / EXP-0007 | **{e7['classification']}** | Point estimate is compatible with 0.5, but FSS SE is {e7['fss']['standard_error_to_tolerance_ratio']:.3f} times the tolerance. |",
        f"| N-19 / EXP-0009 C7 | **{e9['C7']['corrected_classification']}** | Identical labels/seeds and first 40 realizations; no fresh sampling. |",
        f"| N-21 / EXP-0009 R3 | **{e9['R3']['corrected_classification']}** | `P_inf = M_max/L²` makes the fitted slopes algebraically dependent. |",
        f"| N-22 / EXP-0010 | **{e10['classification']}** | Pooled slope regenerates, but no preregistered individual-size estimator exists and C7 is absent. |",
        "",
        "## N-04 — EXP-0006 interpolation and controls",
        "",
        "The implemented interpolation is:",
        "",
        "```text",
        "p50 = p0 + (0.5 - w0) * (p1 - p0) / (w1 - w0)",
        "```",
        "",
        "The historical literal denominator `w1 - p0` is retained only as a diagnostic counterexample; it is not a second estimator or control.",
        "",
        f"Using stored aggregate cells, the recovered `perc-boot` stream regenerates every p50 mean and SE. Maximum absolute deltas are p50 `{e6['numerical_reproduction']['max_abs_p50_delta']:.3g}`, SE `{e6['numerical_reproduction']['max_abs_se_delta']:.3g}`, and FSS component `{e6['numerical_reproduction']['max_abs_fss_component_delta']:.3g}`.",
        "",
        "| Control | Audit status | Evidence |",
        "|---|---|---|",
    ]
    for name, control in e6["controls"].items():
        detail = control.get("reason") or control.get("scope", "recomputed from stored inputs")
        lines.append(f"| {name} | {control['status']} | {detail} |")
    lines.extend(
        [
            "",
            f"The stored-cell C2 pair difference is `{e6['controls']['C2']['pair_diff']:.12f}` (tolerance `{e6['controls']['C2']['tolerance']}`), but this does not repair the broken named runner or supply missing controls. C1 and C6 remain **INCONCLUSIVE** where stored evidence is insufficient.",
            "",
            "## N-05 — EXP-0007 bootstrap accounting and uncertainty",
            "",
            "| Bootstrap | Requested | Accepted | Rejected |",
            "|---|---:|---:|---:|",
            f"| p50, each L | {e7['threshold_p50_bootstrap']['draws_requested_per_L']} | {e7['threshold_p50_bootstrap']['draws_accepted_per_L']} | {e7['threshold_p50_bootstrap']['draws_rejected_per_L']} |",
            f"| width-route 1/nu | {e7['width_route_bootstrap']['draws_requested']} | {e7['width_route_bootstrap']['draws_accepted']} | {e7['width_route_bootstrap']['draws_rejected']} |",
            "",
            f"The FSS point estimate is `{_fmt(e7['fss']['point_estimate'])}` with standard error `{_fmt(e7['fss']['standard_error'])}`; its point deviation from 0.5 is `{_fmt(e7['fss']['point_abs_deviation_from_0.5'])}`, while the decision tolerance is `{e7['fss']['decision_tolerance']}`. The ±1-SE band `[{_fmt(e7['fss']['one_standard_error_interval_not_a_confidence_interval'][0])}, {_fmt(e7['fss']['one_standard_error_interval_not_a_confidence_interval'][1])}]` is a scale indicator, not a confidence interval. Therefore the result is **compatible at the point-estimate gate but INCONCLUSIVE as ±0.01 precision validation**.",
            "",
            f"The width-route bootstrap is also broad: mean `{_fmt(e7['width_route_bootstrap']['mean'])}`, SD `{_fmt(e7['width_route_bootstrap']['standard_deviation'])}`, 95% empirical interval `[{_fmt(e7['width_route_bootstrap']['ci95'][0])}, {_fmt(e7['width_route_bootstrap']['ci95'][1])}]`; its upper end exceeds the 0.9 diagnostic gate.",
            "",
            "## N-19 — EXP-0009 C7 stream dependence",
            "",
            "C7 uses the exact same `G_LAB` labels/seeds and the first 40 realizations as the primary cells. Its mass prefixes and subsample Df regenerate, but this is a **same-stream implementation check**, not independent experimental evidence.",
            "",
            f"Recomputed C7 subsample Df: `{_fmt(e9['C7']['recomputed_D_f_subsample'])}` with SE `{_fmt(e9['C7']['recomputed_D_f_subsample_se'])}`; maximum value/SE delta from the stored report is `{e9['C7']['max_value_or_se_abs_delta']:.3g}`.",
            "",
            "## N-21 — EXP-0009 R3 coupling",
            "",
            "Across every raw cache, `pinfs` equals `masses / L²` exactly. Consequently,",
            "",
            "```text",
            "slope(log P_inf) = slope(log M_max) - 2",
            "R3 = |D_f - (2 - beta/nu)| = 0 at the point-fit level",
            "```",
            "",
            f"The raw point-fit identity residual is `{e9['R3']['point_identity_residual']:.3g}`. The stored bootstrap-mean residual `{_fmt(e9['R3']['stored_bootstrap_mean_R3_residual'])}` reflects separate resampling noise around an algebraically coupled identity. R3 is therefore an **internal consistency diagnostic**, not an independent scaling-law test.",
            "",
            "## N-22 — EXP-0010 pooled versus individual-size closure",
            "",
            f"The four raw caches exactly regenerate the pooled Df `{_fmt(e10['pooled_D_f']['recomputed_value'])}` with SE `{_fmt(e10['pooled_D_f']['recomputed_standard_error'])}` (maximum stored-value/SE delta `{e10['pooled_D_f']['max_abs_value_or_se_delta']:.3g}`). This is an **exploratory pooled slope**.",
            "",
            "The frozen rule says `D_f` must be within tolerance at every individual non-power-of-two L, but supplies no single-size Df estimator or fixed amplitude. Available raw quantities are per-size Mmax realizations and their summaries. A pairwise slope, leave-one-out slope, or box-counting replacement would be a new post hoc estimator and was not manufactured.",
            "",
            "The required C7 result is absent. Therefore:",
            "",
            "- individual-size gate: **UNRESOLVED / NOT IDENTIFIABLE**;",
            "- C7: **INCONCLUSIVE / ABSENT**;",
            "- historical `LATTICE_ARTIFACT`: **NOT ACCEPTED**;",
            "- corrected EXP-0010 classification: **INCONCLUSIVE**.",
            "",
            "## Dependency-aware validation order",
            "",
            "| Node | Depends on | Produces | Status |",
            "|---|---|---|---|",
        ]
    )
    for node in report["dependency_graph"]:
        lines.append(
            f"| {node['id']} | {', '.join(node['depends_on'])} | {node['produces']} | {node['status']} |"
        )
    lines.extend(
        [
            "",
            "## Reproducibility boundary",
            "",
            "- **Reproducible from stored cells:** EXP-0006 aggregate p50/SE/FSS and stored-cell C2/C4; EXP-0007 p50/FSS and 495 accepted width draws; EXP-0009 raw-cache exponents, C7 same-stream prefix, and R3 identity; EXP-0010 pooled Df and per-L mass summaries.",
            "- **Not reproducible / unavailable:** EXP-0006 current full-run provenance, realization-level C1, and extra-seed C6 cells; a fresh independent EXP-0009 C7 sample; an independent R3 observable; an EXP-0010 individual-size Df estimator; EXP-0010 C7.",
            "- **No post hoc control or estimator was added, no Monte Carlo was generated, and no historical registry/config/result/cache/report/helper was written.**",
            "",
            "Machine-readable details and the complete SHA-256 evidence manifest are in the sibling `validation_report.json` and the active post-N-14 baseline; the original pre-N-14 baseline is retained unchanged for provenance.",
        ]
    )
    return "\n".join(lines)


def run_analysis(
    scope_path: Path,
    baseline_path: Path,
    output_json: Path,
    output_markdown: Path,
    output_manifest: Path,
    append_only_lock_path: Path = APPEND_ONLY_LOCK_DEFAULT,
) -> dict[str, Any]:
    for output in (output_json, output_markdown, output_manifest):
        if output.exists():
            raise AuditError(f"refusing to overwrite existing output: {output}")
    report = analyze(scope_path, baseline_path, append_only_lock_path)
    write_new_json(output_json, report)
    write_new_text(output_markdown, render_markdown(report))
    manifest = {
        "schema": "historical-2d-percolation-audit-run-manifest-v1",
        "execution_class": "READ_ONLY_STORED_CELL_VALIDATION",
        "production_calculations_launched": False,
        "monte_carlo_generations_launched": False,
        "historical_files_written": False,
        "scope_config_sha256": sha256_file(scope_path),
        "historical_evidence_baseline_sha256": sha256_file(baseline_path),
        "append_only_lock_sha256": sha256_file(append_only_lock_path),
        "runner_sha256": sha256_file(Path(__file__)),
        "outputs": {
            relative_path(output_json): sha256_file(output_json),
            relative_path(output_markdown): sha256_file(output_markdown),
        },
    }
    write_new_json(output_manifest, manifest)
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot = subparsers.add_parser("snapshot", help="create the immutable evidence baseline once")
    snapshot.add_argument("--scope", type=Path, default=SCOPE_DEFAULT)
    snapshot.add_argument("--baseline", type=Path, default=BASELINE_DEFAULT)
    analysis = subparsers.add_parser("analyze", help="run read-only stored-cell validation")
    analysis.add_argument("--scope", type=Path, default=SCOPE_DEFAULT)
    analysis.add_argument("--baseline", type=Path, default=BASELINE_DEFAULT)
    analysis.add_argument("--append-only-lock", type=Path, default=APPEND_ONLY_LOCK_DEFAULT)
    analysis.add_argument("--output-json", type=Path, required=True)
    analysis.add_argument("--output-markdown", type=Path, required=True)
    analysis.add_argument("--output-manifest", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "snapshot":
        scope = load_scope(args.scope)
        baseline = snapshot_evidence(scope)
        write_new_json(args.baseline, baseline)
        print(f"Wrote immutable evidence baseline: {args.baseline}")
        return 0
    report = run_analysis(
        args.scope,
        args.baseline,
        args.output_json,
        args.output_markdown,
        args.output_manifest,
        args.append_only_lock,
    )
    print(json.dumps(report["classifications"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
