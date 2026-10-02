"""Dependence-aware analysis primitives for the isolated N-004 RNG repair.

The historical battery is intentionally not modified.  This module replays its
stored 80-seed audit matrix, keeps seed rows intact, and provides conservative
per-test diagnostics.  It does not certify a generator or interpret a
production-scale result.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from scipy import stats

from engine.validation.rng_battery import TEST_IDS


ALPHA = 0.01
AUDIT_SEEDS = tuple(range(100000, 100080))


class N004Error(RuntimeError):
    """Fail-closed N-004 repair error."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise N004Error(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _reject_constant(value: str) -> None:
    raise N004Error(f"non-finite JSON constant: {value}")


def load_strict_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, N004Error) as exc:
        raise N004Error(f"cannot read strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise N004Error(f"JSON root must be an object: {path}")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exact_band(n: int, p: float = ALPHA, coverage: float = 0.95) -> list[int]:
    if n < 1 or not 0.0 < p < 1.0 or not 0.0 < coverage < 1.0:
        raise N004Error("invalid exact-band arguments")
    lo, hi = stats.binom.ppf((1.0 - coverage) / 2.0, n, p), stats.binom.ppf(
        1.0 - (1.0 - coverage) / 2.0, n, p
    )
    return [int(lo), int(hi)]


def bh_flags(values: Sequence[float], alpha: float = ALPHA) -> np.ndarray:
    p = np.asarray(values, dtype=float)
    if p.ndim != 1 or p.size == 0:
        raise N004Error("BH input must be a nonempty one-dimensional array")
    order = np.argsort(p, kind="mergesort")
    thresholds = alpha * np.arange(1, p.size + 1, dtype=float) / p.size
    passed = p[order] <= thresholds
    out = np.zeros(p.size, dtype=bool)
    if bool(np.any(passed)):
        out[order[: int(np.flatnonzero(passed).max()) + 1]] = True
    return out


def holm_fwer(values: Sequence[float], alpha: float = ALPHA) -> dict[str, Any]:
    """Holm step-down FWER adjustment that treats NaNs deterministically.

    This is a conservative family-wise rule over the supplied marginal tests;
    it is not a model for the dependence between tests.  NaNs are retained as
    non-rejected entries with a null adjusted p-value.
    """
    p = np.asarray(values, dtype=float)
    if p.ndim != 1 or p.size == 0 or not 0.0 < alpha < 1.0:
        raise N004Error("Holm input must be a nonempty vector and alpha in (0,1)")
    finite = np.isfinite(p)
    if np.any(finite & ((p < 0.0) | (p > 1.0))):
        raise N004Error("Holm p-values must lie in [0,1]")
    adjusted = np.full(p.size, np.nan, dtype=float)
    rejected = np.zeros(p.size, dtype=bool)
    finite_indices = np.flatnonzero(finite)
    m = finite_indices.size
    if m:
        order = finite_indices[np.argsort(p[finite_indices], kind="mergesort")]
        running = 0.0
        last_rank = -1
        for rank, index in enumerate(order):
            adjusted_value = min(1.0, (m - rank) * float(p[index]))
            running = max(running, adjusted_value)
            adjusted[index] = running
            if float(p[index]) <= alpha / (m - rank):
                last_rank = rank
        if last_rank >= 0:
            rejected[order[: last_rank + 1]] = True
    return {
        "alpha": float(alpha),
        "n_total": int(p.size),
        "n_finite": int(m),
        "rejected_indices": [int(i) for i in np.flatnonzero(rejected)],
        "rejected_count": int(rejected.sum()),
        "adjusted_pvalues": [
            None if not math.isfinite(float(value)) else float(value)
            for value in adjusted
        ],
        "nan_policy": "non-rejected with null adjusted p-value",
    }


def _ks(values: np.ndarray) -> dict[str, float | None]:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return {"stat": None, "p": None}
    result = stats.kstest(finite, "uniform")
    return {"stat": float(result.statistic), "p": float(result.pvalue)}


def summarize_per_test(
    matrix: np.ndarray,
    test_ids: Sequence[str] = TEST_IDS,
    alpha: float = ALPHA,
) -> list[dict[str, Any]]:
    values = np.asarray(matrix, dtype=float)
    if values.ndim != 2 or values.shape[1] != len(test_ids):
        raise N004Error("matrix shape does not match test_ids")
    output = []
    for index, test_id in enumerate(test_ids):
        column = values[:, index]
        finite = column[np.isfinite(column)]
        ks = _ks(finite)
        output.append(
            {
                "test_id": str(test_id),
                "n": int(finite.size),
                "ks_stat": ks["stat"],
                "ks_p": ks["p"],
                "small_p_count": int(np.sum(finite <= alpha)),
                "small_p_fraction": (
                    float(np.mean(finite <= alpha)) if finite.size else None
                ),
                "min": float(np.min(finite)) if finite.size else None,
                "max": float(np.max(finite)) if finite.size else None,
            }
        )
    return output


def dependence_diagnostics(matrix: np.ndarray) -> dict[str, Any]:
    values = np.asarray(matrix, dtype=float)
    if values.ndim != 2 or values.shape[0] < 2 or values.shape[1] < 2:
        raise N004Error("dependence diagnostics require at least 2x2 values")
    with np.errstate(invalid="ignore", divide="ignore"):
        corr = np.corrcoef(values, rowvar=False)
    offdiag = ~np.eye(corr.shape[0], dtype=bool)
    finite_corr = corr[np.isfinite(corr) & offdiag]
    pairs = []
    for i in range(corr.shape[0]):
        for j in range(i + 1, corr.shape[0]):
            value = float(corr[i, j])
            if math.isfinite(value):
                pairs.append((i, j, value))
    return {
        "mean_abs_offdiag": float(np.mean(np.abs(finite_corr))) if finite_corr.size else None,
        "max_abs_offdiag": float(np.max(np.abs(finite_corr))) if finite_corr.size else None,
        "pairs_abs_corr_ge_0_3": int(sum(abs(value) >= 0.3 for _, _, value in pairs)),
        "pairs_abs_corr_ge_0_5": int(sum(abs(value) >= 0.5 for _, _, value in pairs)),
        "correlation_matrix": corr.tolist(),
        "identical_column_pairs": [
            [i, j]
            for i in range(values.shape[1])
            for j in range(i + 1, values.shape[1])
            if np.array_equal(values[:, i], values[:, j])
        ],
    }


def row_preserving_resample(
    matrix: np.ndarray,
    draws: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(matrix, dtype=float)
    if values.ndim != 2 or values.shape[0] < 1 or draws < 1:
        raise N004Error("row-preserving resampling requires a nonempty matrix and draws")
    generator = np.random.default_rng(seed)
    indices = generator.integers(0, values.shape[0], size=(draws, values.shape[0]))
    return values[indices], indices


def _assert_close(actual: Any, expected: Any, path: str = "value") -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise N004Error(f"replay key mismatch at {path}")
        for key in expected:
            _assert_close(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise N004Error(f"replay length mismatch at {path}")
        for index, (left, right) in enumerate(zip(actual, expected)):
            _assert_close(left, right, f"{path}[{index}]")
    elif isinstance(expected, float):
        if not isinstance(actual, (int, float)) or not math.isclose(
            float(actual), expected, rel_tol=2e-12, abs_tol=2e-15
        ):
            raise N004Error(f"replay numeric mismatch at {path}: {actual!r} != {expected!r}")
    elif actual != expected:
        raise N004Error(f"replay mismatch at {path}: {actual!r} != {expected!r}")


def summarize_matrix(
    matrix: np.ndarray,
    test_ids: Sequence[str] = TEST_IDS,
    alpha: float = ALPHA,
) -> dict[str, Any]:
    values = np.asarray(matrix, dtype=float)
    if values.ndim != 2 or values.shape[0] < 1:
        raise N004Error("matrix must be nonempty and two-dimensional")
    flat = values.ravel()
    finite_flat = flat[np.isfinite(flat)]
    pooled_ks = _ks(finite_flat)
    per_test = summarize_per_test(values, test_ids=test_ids, alpha=alpha)
    dependence = dependence_diagnostics(values) if values.shape[1] > 1 else {}
    marginal_pvalues = [
        item["ks_p"] if item["ks_p"] is not None else np.nan
        for item in per_test
    ]
    return {
        "n_seeds": int(values.shape[0]),
        "n_pvalues": int(flat.size),
        "pooled_ks": pooled_ks,
        "pooled_small_p_count": int(np.sum(finite_flat <= alpha)),
        "pooled_binomial_band_if_independent": exact_band(int(finite_flat.size), alpha),
        "pooled_bh_flag_count": int(bh_flags(finite_flat, alpha).sum()),
        "holm_fwer_over_test_marginals": holm_fwer(marginal_pvalues, alpha),
        "per_test": {item["test_id"]: {k: v for k, v in item.items() if k != "test_id"} for item in per_test},
        "pvalue_correlation": {
            key: dependence[key]
            for key in (
                "mean_abs_offdiag",
                "max_abs_offdiag",
                "pairs_abs_corr_ge_0_3",
                "pairs_abs_corr_ge_0_5",
            )
        },
        "per_seed_small_p_count": {
            "values": [int(x) for x in np.sum(values <= alpha, axis=1)],
            "mean": float(np.mean(np.sum(values <= alpha, axis=1))),
            "sd": float(np.std(np.sum(values <= alpha, axis=1), ddof=1)) if values.shape[0] > 1 else 0.0,
            "max": int(np.max(np.sum(values <= alpha, axis=1))),
        },
    }


def replay_historical_audit(path: Path) -> dict[str, Any]:
    payload = load_strict_json(path)
    if payload.get("test_ids") != list(TEST_IDS):
        raise N004Error("historical audit TEST_IDS do not match shared battery")
    if tuple(payload.get("seeds", ())) != AUDIT_SEEDS:
        raise N004Error("historical audit seed ladder is not the registered 80-seed ladder")
    generators = payload.get("generators")
    if not isinstance(generators, dict) or set(generators) != {"G_LAB", "G_PCG", "G_MT"}:
        raise N004Error("historical audit generator set is incomplete")
    replayed = {}
    for name in ("G_LAB", "G_PCG", "G_MT"):
        record = generators[name]
        raw = np.asarray(record.get("raw_pvalues"), dtype=float)
        if raw.shape != (80, len(TEST_IDS)):
            raise N004Error(f"raw p-value matrix shape mismatch for {name}")
        recomputed = summarize_matrix(raw, alpha=float(payload.get("alpha", ALPHA)))
        for key in (
            "n_seeds",
            "n_pvalues",
            "pooled_ks",
            "pooled_small_p_count",
            "pooled_binomial_band_if_independent",
            "pooled_bh_flag_count",
            "per_test",
            "pvalue_correlation",
            "per_seed_small_p_count",
        ):
            _assert_close(recomputed[key], record[key], f"{name}.{key}")
        replayed[name] = recomputed
    return {
        "status": "PASS_EXACT_80X24_REPLAY",
        "source_sha256": sha256_file(path),
        "test_ids": list(TEST_IDS),
        "seeds": list(AUDIT_SEEDS),
        "stream_mode": "historical_shared_arrays",
        "summaries": replayed,
    }
