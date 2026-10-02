"""Isolated audit-repair runner for findings N-06/N-07/N-08.

This module is deliberately outside the historical Q-M007/Q-M008 runners.  It
never writes to their CONFIG, RESULTS, or REPORT directories.  The runner has
one frozen, hash-locked configuration and one descriptive smoke analysis.

The implementation repairs numerical defects only:

* gaps use ``(p_{i+1} - p_i) / log(p_i)``;
* Benjamini--Hochberg is a genuine step-up procedure;
* chi-square and normal tails are evaluated in log-survival form and are
  never replaced by an artificial exact zero;
* the parity-lattice null retains the exact even-gap support and reports bins
  which are structurally empty at the tested scale;
* the segmented sieve uses ``max(p*p, first_multiple_at_or_after(low))`` so
  a segment never marks a prime itself.

The discrete parity model used here is a *diagnostic surrogate*.  It is not a
claim about primes, Gallagher's theorem, or a novel prime process.  In
particular it has no wheel, singular-series, or consecutive-pair correction.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Sequence

import numpy as np
from scipy import special
from scipy.special import logsumexp


AUDIT_DIR = Path(__file__).resolve().parent
PRIME_GAP_ROOT = AUDIT_DIR.parent
CONFIG_DIR = AUDIT_DIR / "CONFIG"
RESULTS_DIR = AUDIT_DIR / "RESULTS"
REPORT_DIR = AUDIT_DIR / "REPORT"
PRODUCTION_LIMIT = 10_000_000_000
FIRST_SEGMENT_LIMIT = 100_000_000
ANALYSIS_ID = "PGA-AUDIT-N06-N08-20260924"
FROZEN_CONFIG_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
LN10 = math.log(10.0)
LOG2 = math.log(2.0)


class AuditInputError(ValueError):
    """Raised when an input/config artifact is missing or malformed."""


class AuditIntegrityError(AuditInputError):
    """Raised when a frozen artifact does not match its recorded digest."""


class AuditOutputError(RuntimeError):
    """Raised when an output would overwrite an existing artifact."""


@dataclass(frozen=True)
class BlockSpec:
    label: str
    lo: int
    hi: int

    def __post_init__(self) -> None:
        if not self.label:
            raise AuditInputError("block label must be non-empty")
        if type(self.lo) is not int or type(self.hi) is not int:
            raise AuditInputError("block bounds must be integers")
        if self.lo < 3 or self.hi <= self.lo:
            raise AuditInputError(f"invalid lower-prime block: {self}")


@dataclass(frozen=True)
class PrimeSegment:
    index: int
    lo: int
    hi: int
    primes: np.ndarray


@dataclass
class BlockState:
    spec: BlockSpec
    bin_edges: np.ndarray
    n: int = 0
    mean: float = 0.0
    m2: float = 0.0
    sum_upper_normalized: float = 0.0
    observed: np.ndarray | None = None
    parity_expected: np.ndarray | None = None
    simulated_counts: np.ndarray | None = None
    tail_counts: dict[str, int] | None = None
    first_lower: int | None = None
    last_lower: int | None = None
    last_upper: int | None = None
    min_observed: float = math.inf
    max_observed: float = -math.inf

    def __post_init__(self) -> None:
        self.observed = np.zeros(len(self.bin_edges) - 1, dtype=np.int64)
        self.parity_expected = np.zeros(len(self.bin_edges) - 1, dtype=np.float64)
        self.simulated_counts = np.zeros(
            (0, len(self.bin_edges) - 1), dtype=np.int64
        )
        self.tail_counts = {}

    @property
    def variance(self) -> float:
        if self.n < 2:
            return 0.0
        return max(0.0, self.m2 / (self.n - 1))

    @property
    def standard_deviation(self) -> float:
        return math.sqrt(self.variance)

    def add_batch(
        self,
        lower: np.ndarray,
        upper: np.ndarray,
        simulation_replicates: int,
        rng: np.random.Generator,
        chunk_size: int = 100_000,
    ) -> None:
        if lower.size == 0:
            return
        if lower.size != upper.size:
            raise AuditInputError("lower/upper arrays have different lengths")
        if np.any(lower < 3) or np.any(upper <= lower):
            raise AuditInputError("invalid lower/upper prime arrays")

        for start in range(0, lower.size, chunk_size):
            stop = min(start + chunk_size, lower.size)
            p = lower[start:stop]
            q = upper[start:stop]
            log_p = np.log(p.astype(np.float64))
            delta = (q.astype(np.float64) - p.astype(np.float64)) / log_p
            if not np.all(np.isfinite(delta)) or np.any(delta <= 0.0):
                raise AuditInputError("non-positive/non-finite normalized gap")

            batch_n = int(delta.size)
            batch_mean = float(np.mean(delta))
            batch_m2 = float(np.sum((delta - batch_mean) ** 2))
            if self.n:
                correction = batch_mean - self.mean
                combined_n = self.n + batch_n
                self.m2 += batch_m2 + correction * correction * self.n * batch_n / combined_n
                self.mean += correction * batch_n / combined_n
                self.n = combined_n
            else:
                self.n = batch_n
                self.mean = batch_mean
                self.m2 = batch_m2

            upper_delta = (q.astype(np.float64) - p.astype(np.float64)) / np.log(
                q.astype(np.float64)
            )
            self.sum_upper_normalized += float(np.sum(upper_delta))

            indices = np.searchsorted(self.bin_edges[1:-1], delta, side="right")
            self.observed += np.bincount(
                indices, minlength=len(self.bin_edges) - 1
            ).astype(np.int64)

            probabilities = parity_bin_probabilities(p, self.bin_edges)
            self.parity_expected += np.sum(probabilities, axis=0, dtype=np.float64)

            if self.simulated_counts.shape[0] == 0:
                self.simulated_counts = np.zeros(
                    (simulation_replicates, len(self.bin_edges) - 1), dtype=np.int64
                )
            for replicate in range(simulation_replicates):
                simulated_delta = simulate_discrete_gap_values(p, rng)
                sim_indices = np.searchsorted(
                    self.bin_edges[1:-1], simulated_delta, side="right"
                )
                self.simulated_counts[replicate] += np.bincount(
                    sim_indices, minlength=len(self.bin_edges) - 1
                ).astype(np.int64)

            if self.first_lower is None:
                self.first_lower = int(p[0])
            self.last_lower = int(p[-1])
            self.last_upper = int(q[-1])
            self.min_observed = min(self.min_observed, float(np.min(delta)))
            self.max_observed = max(self.max_observed, float(np.max(delta)))

    def summary(self, alpha: float) -> dict[str, Any]:
        if self.observed is None or self.parity_expected is None:
            raise AuditInputError("block was not initialized")
        if self.n <= 0:
            raise AuditInputError(f"block {self.spec.label} has no gaps")
        observed = [int(x) for x in self.observed]
        if sum(observed) != self.n:
            raise AuditInputError(
                f"histogram total mismatch in {self.spec.label}: "
                f"{sum(observed)} != {self.n}"
            )
        expected_continuous = self.n / (len(self.bin_edges) - 1)
        parity_expected = [float(x) for x in self.parity_expected]
        if not math.isclose(
            sum(parity_expected), self.n, rel_tol=2e-12, abs_tol=2e-8
        ):
            raise AuditInputError(
                f"parity expected-count total mismatch in {self.spec.label}"
            )

        floor = 2.0 / math.log(self.spec.hi)
        empty_by_edge = [
            index + 1
            for index, upper in enumerate(self.bin_edges[1:])
            if float(upper) <= floor
        ]
        empty_by_surrogate = [
            index + 1
            for index, probability in enumerate(parity_expected)
            if probability == 0.0
        ]
        continuous = pearson_chi_square(
            observed,
            [expected_continuous] * len(observed),
            supported_only=False,
            label="continuous Exp(1) operational diagnostic",
        )
        parity = pearson_chi_square(
            observed,
            parity_expected,
            supported_only=True,
            label="conditional parity-geometric surrogate",
        )

        tails: dict[str, Any] = {}
        for threshold in (1, 2, 3, 4, 5):
            count = int(self.tail_counts.get(str(threshold), 0))
            rate = count / self.n
            expected_rate = math.exp(-float(threshold))
            se = math.sqrt(expected_rate * (1.0 - expected_rate) / self.n)
            z = (rate - expected_rate) / se if se else 0.0
            tails[str(threshold)] = {
                "observed": count,
                "observed_rate": rate,
                "continuous_expected_rate": expected_rate,
                "z": z,
                **normal_two_sided_survival(z),
            }

        simulated_mean = (
            np.mean(self.simulated_counts, axis=0).astype(np.float64).tolist()
            if self.simulated_counts.size
            else []
        )
        simulation_error = None
        if simulated_mean:
            simulation_error = float(
                np.max(np.abs(np.asarray(simulated_mean) - np.asarray(parity_expected)))
            )

        return {
            "label": self.spec.label,
            "lo": self.spec.lo,
            "hi": self.spec.hi,
            "n_gaps": self.n,
            "first_lower_prime": self.first_lower,
            "last_lower_prime": self.last_lower,
            "last_upper_prime": self.last_upper,
            "normalization": "delta=(upper-lower)/ln(lower)",
            "mean_delta": self.mean,
            "variance_delta": self.variance,
            "standard_deviation_delta": self.standard_deviation,
            "mean_upper_prime_normalized_for_comparison": self.sum_upper_normalized
            / self.n,
            "minimum_observed_delta": self.min_observed,
            "maximum_observed_delta": self.max_observed,
            "bin_edges_internal": [float(x) for x in self.bin_edges[:-1]],
            "last_bin": "[edge_9,+infinity)",
            "observed_counts": observed,
            "continuous_exp1_expected_counts": [
                float(expected_continuous) for _ in observed
            ],
            "parity_geometric_expected_counts": parity_expected,
            "parity_simulation_mean_counts": simulated_mean,
            "parity_simulation_replicates": int(self.simulated_counts.shape[0]),
            "parity_simulation_max_abs_count_error": simulation_error,
            "structural_support": {
                "parity_floor_at_block_upper_bound": floor,
                "floor_is_not_attained_by_lower_prime_in_block": True,
                "empty_bins_by_edge_and_parity_floor": empty_by_edge,
                "empty_bins_in_conditional_surrogate": empty_by_surrogate,
                "first_bin_structurally_empty": 1 in empty_by_edge,
            },
            "chi_square_continuous_exp1_diagnostic": continuous,
            "chi_square_parity_geometric_diagnostic": parity,
            "tail_continuous_exp1_diagnostic": tails,
        }


class StreamingGapAccumulator:
    """Accumulate block statistics without retaining all normalized gaps."""

    def __init__(
        self,
        blocks: Sequence[BlockSpec],
        bin_edges: np.ndarray,
        simulation_replicates: int,
        seed: int,
    ) -> None:
        if not blocks:
            raise AuditInputError("at least one block is required")
        if bin_edges.ndim != 1 or len(bin_edges) < 2:
            raise AuditInputError("bin_edges must be a one-dimensional edge vector")
        if (
            not np.all(np.isfinite(bin_edges[:-1]))
            or not math.isinf(float(bin_edges[-1]))
            or float(bin_edges[-1]) <= 0.0
            or np.any(np.diff(bin_edges) <= 0)
        ):
            raise AuditInputError(
                "bin_edges must be finite except for a positive final infinity edge"
            )
        if bin_edges[0] != 0.0 or simulation_replicates < 0:
            raise AuditInputError("invalid binning or simulation configuration")
        self.blocks = list(blocks)
        self.bin_edges = np.asarray(bin_edges, dtype=np.float64)
        self.states = {
            block.label: BlockState(block, self.bin_edges) for block in self.blocks
        }
        self.previous_prime: int | None = None
        self.total_streamed_gaps = 0
        self.total_selected_gaps = 0
        self.simulation_replicates = int(simulation_replicates)
        self.rng = np.random.default_rng(seed)

    def ingest_segment(self, segment: PrimeSegment) -> None:
        primes = np.asarray(segment.primes, dtype=np.int64)
        if primes.ndim != 1:
            raise AuditInputError("segment primes must be one-dimensional")
        if primes.size and np.any(np.diff(primes) <= 0):
            raise AuditInputError("segment primes are not strictly increasing")
        if not primes.size:
            return

        if self.previous_prime is None:
            lower = primes[:-1]
            upper = primes[1:]
        else:
            lower = np.concatenate(
                (np.asarray([self.previous_prime], dtype=np.int64), primes[:-1])
            )
            upper = primes
        self.previous_prime = int(primes[-1])
        self.total_streamed_gaps += int(lower.size)

        for block in self.blocks:
            mask = (lower >= block.lo) & (lower < block.hi)
            self.total_selected_gaps += int(np.count_nonzero(mask))
            if np.any(mask):
                self.states[block.label].add_batch(
                    lower[mask],
                    upper[mask],
                    self.simulation_replicates,
                    self.rng,
                )

    def summaries(self, alpha: float) -> list[dict[str, Any]]:
        return [self.states[block.label].summary(alpha) for block in self.blocks]


# ---------------------------------------------------------------------------
# Strict frozen-config and provenance handling
# ---------------------------------------------------------------------------


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise AuditInputError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_json_constant(value: str) -> Any:
    raise AuditInputError(f"non-finite JSON constant is not allowed: {value}")


def load_strict_json(path: Path) -> Any:
    if not path.is_file():
        raise AuditInputError(f"missing JSON input: {path}")
    try:
        text = path.read_text(encoding="utf-8")
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_json_constant,
        )
    except AuditInputError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditInputError(f"malformed JSON input {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    if not path.is_file():
        raise AuditInputError(f"missing file for hash: {path}")
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_frozen_config(config_path: Path, digest_path: Path) -> dict[str, Any]:
    """Load a config only when its exact bytes match the freeze sidecar."""

    if not config_path.is_file():
        raise AuditInputError(f"missing frozen config: {config_path}")
    if not digest_path.is_file():
        raise AuditInputError(f"missing config freeze digest: {digest_path}")
    try:
        digest_text = digest_path.read_text(encoding="ascii").strip()
    except (OSError, UnicodeError) as exc:
        raise AuditInputError(f"cannot read config freeze digest: {exc}") from exc
    match = re.fullmatch(r"([0-9a-f]{64})(?:\s+.*)?", digest_text)
    if not match:
        raise AuditInputError("config freeze digest is malformed")
    expected = match.group(1)
    actual = sha256_file(config_path)
    if actual != expected:
        raise AuditIntegrityError(
            f"frozen config hash mismatch: expected {expected}, got {actual}"
        )
    config = load_strict_json(config_path)
    if not isinstance(config, dict):
        raise AuditInputError("frozen config root must be an object")
    validate_config(config)
    return config


def _require_key(obj: dict[str, Any], key: str, context: str) -> Any:
    if key not in obj:
        raise AuditInputError(f"missing config key {context}.{key}")
    return obj[key]


def validate_config(config: dict[str, Any]) -> None:
    if config.get("schema_version") != "prime-gap-audit-repair/v1":
        raise AuditInputError("unsupported or missing schema_version")
    if config.get("analysis_id") != ANALYSIS_ID:
        raise AuditInputError("analysis_id does not identify this isolated audit")
    if config.get("scope_findings") != ["N-06", "N-07", "N-08"]:
        raise AuditInputError("scope must be exactly N-06/N-07/N-08")
    if config.get("interpretation") != "DESCRIPTIVE_ONLY":
        raise AuditInputError("this runner only permits descriptive output")

    normalization = _require_key(config, "normalization", "config")
    if normalization.get("denominator") != "log(lower_prime)":
        raise AuditInputError("normalization must use log(lower_prime)")
    if normalization.get("block_assignment") != "lo <= lower_prime < hi":
        raise AuditInputError("unexpected lower-prime block convention")
    if normalization.get("include_successor_across_upper_boundary") is not True:
        raise AuditInputError("successor-across-boundary gaps must be retained")

    binning = _require_key(config, "binning", "config")
    if binning.get("count") != 10 or binning.get("rule") != "exponential_quantile":
        raise AuditInputError("unexpected binning configuration")
    if binning.get("structural_empty_cells") != "exclude_only_when_expected_zero":
        raise AuditInputError("structural empty-cell policy is missing")

    bh = _require_key(config, "bh", "config")
    if bh.get("method") != "step_up" or not isinstance(bh.get("alpha"), (int, float)):
        raise AuditInputError("BH must specify step_up and alpha")
    if not 0.0 < float(bh["alpha"]) < 1.0:
        raise AuditInputError("BH alpha is out of range")

    survival = _require_key(config, "survival", "config")
    if survival.get("method") != "log_survival_no_exact_zero":
        raise AuditInputError("survival method is not log-safe")
    if survival.get("underflow_representation") != "null_plus_log10":
        raise AuditInputError("underflow representation is not fail-safe")

    discrete = _require_key(config, "discrete_null", "config")
    if discrete.get("model") != "conditional_parity_geometric":
        raise AuditInputError("unexpected discrete null")
    if discrete.get("support") != "exact_even_gap_lattice":
        raise AuditInputError("discrete null must retain exact even-gap support")
    if discrete.get("is_scientific_gallagher_null") is not False:
        raise AuditInputError("discrete surrogate must be marked non-scientific")

    sieve = _require_key(config, "sieve_smoke", "config")
    required_ints = {
        "sieve_limit": 100_000_100,
        "data_cutoff": 100_000_000,
        "segment_size": 100_000_000,
        "first_segment_end": 100_000_000,
        "production_limit": PRODUCTION_LIMIT,
    }
    for key, expected in required_ints.items():
        if sieve.get(key) != expected:
            raise AuditInputError(f"sieve_smoke.{key} must equal {expected}")
    if sieve.get("run_production") is not False:
        raise AuditInputError("production 10^10 execution is forbidden by this audit")
    if sieve.get("trusted_small_comparison_limit") != 1000:
        raise AuditInputError("small trusted sieve comparison is not configured")

    blocks = _require_key(config, "blocks", "config")
    if not isinstance(blocks, list) or len(blocks) != 4:
        raise AuditInputError("four matched decade blocks are required")
    parsed_blocks: list[BlockSpec] = []
    for item in blocks:
        if not isinstance(item, dict):
            raise AuditInputError("block entries must be objects")
        parsed_blocks.append(
            BlockSpec(
                label=_require_key(item, "label", "block"),
                lo=_require_key(item, "lo", "block"),
                hi=_require_key(item, "hi", "block"),
            )
        )
    if [b.label for b in parsed_blocks] != ["B1", "B2", "B3", "B4"]:
        raise AuditInputError("unexpected block labels")
    if [(b.lo, b.hi) for b in parsed_blocks] != [
        (10_000, 100_000),
        (100_000, 1_000_000),
        (1_000_000, 10_000_000),
        (10_000_000, 100_000_000),
    ]:
        raise AuditInputError("blocks do not match the historical EXP-0008 ranges")

    evidence = _require_key(config, "historical_evidence", "config")
    if not isinstance(evidence, list) or not evidence:
        raise AuditInputError("historical evidence manifest is required")
    for item in evidence:
        if not isinstance(item, dict):
            raise AuditInputError("historical evidence entries must be objects")
        rel = _require_key(item, "path", "historical_evidence")
        digest = _require_key(item, "sha256", "historical_evidence")
        if not isinstance(rel, str) or Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise AuditInputError(f"unsafe historical path: {rel!r}")
        if not FROZEN_CONFIG_SHA256_RE.fullmatch(str(digest)):
            raise AuditInputError(f"malformed historical digest for {rel}")


def verify_historical_evidence(config: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in config["historical_evidence"]:
        path = (PRIME_GAP_ROOT / item["path"]).resolve()
        root = PRIME_GAP_ROOT.resolve()
        if not str(path).startswith(str(root) + str(Path("/"))):
            raise AuditInputError(f"historical path escapes prime-gap root: {path}")
        if not path.is_file():
            raise AuditInputError(f"missing historical evidence: {path}")
        actual = sha256_file(path)
        if actual != item["sha256"]:
            raise AuditIntegrityError(
                f"historical evidence changed: {item['path']} "
                f"(expected {item['sha256']}, got {actual})"
            )
        records.append(
            {
                "path": item["path"],
                "sha256": actual,
                "bytes": path.stat().st_size,
                "read_only": True,
            }
        )
    return records


# ---------------------------------------------------------------------------
# Sieve implementations
# ---------------------------------------------------------------------------


def _validate_sieve_limit(limit: int) -> None:
    if type(limit) is not int or limit < 0:
        raise AuditInputError(f"invalid sieve limit: {limit!r}")


def simple_sieve_primes(limit: int) -> np.ndarray:
    """Trusted, deliberately simple full sieve used only for small controls."""

    _validate_sieve_limit(limit)
    if limit < 2:
        return np.empty(0, dtype=np.int64)
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(limit) + 1):
        if flags[p]:
            start = p * p
            count = (limit - start) // p + 1
            flags[start : limit + 1 : p] = b"\x00" * count
    return np.fromiter(
        (value for value, flag in enumerate(flags) if flag), dtype=np.int64
    )


def segment_ranges(limit: int, segment_size: int) -> list[tuple[int, int]]:
    """Return inclusive, non-overlapping ranges covering 0..limit."""

    _validate_sieve_limit(limit)
    if type(segment_size) is not int or segment_size <= 0:
        raise AuditInputError(f"invalid segment size: {segment_size!r}")
    ranges: list[tuple[int, int]] = []
    low = 0
    while low <= limit:
        high = min(limit, low + segment_size - 1)
        ranges.append((low, high))
        low = high + 1
    return ranges


def sieve_segment(
    lo: int, hi: int, base_primes: Sequence[int]
) -> np.ndarray:
    """Sieve one inclusive segment, retaining primes at the segment start."""

    if type(lo) is not int or type(hi) is not int or lo < 0 or hi < lo:
        raise AuditInputError(f"invalid segment bounds: [{lo}, {hi}]")
    length = hi - lo + 1
    flags = np.ones(length, dtype=np.uint8)
    if lo == 0:
        flags[0] = 0
    if lo <= 1 <= hi:
        flags[1 - lo] = 0

    root = math.isqrt(hi)
    for p_value in base_primes:
        p = int(p_value)
        if p > root:
            break
        first_multiple = ((lo + p - 1) // p) * p
        start = max(p * p, first_multiple)
        if start > hi:
            continue
        count = (hi - start) // p + 1
        flags[start - lo :: p] = 0
    return np.flatnonzero(flags).astype(np.int64) + lo


def iter_segmented_prime_segments(
    limit: int, segment_size: int
) -> Iterator[PrimeSegment]:
    """Yield a streaming segmented sieve with a base-prime sieve."""

    _validate_sieve_limit(limit)
    if type(segment_size) is not int or segment_size <= 0:
        raise AuditInputError(f"invalid segment size: {segment_size!r}")
    base_primes = simple_sieve_primes(math.isqrt(limit)).tolist()
    for index, (lo, hi) in enumerate(segment_ranges(limit, segment_size)):
        yield PrimeSegment(index, lo, hi, sieve_segment(lo, hi, base_primes))


def iter_segmented_primes(limit: int, segment_size: int) -> Iterator[int]:
    for segment in iter_segmented_prime_segments(limit, segment_size):
        yield from (int(value) for value in segment.primes)


# ---------------------------------------------------------------------------
# Discrete support and survival statistics
# ---------------------------------------------------------------------------


def _survival_payload(log10_p: float) -> dict[str, Any]:
    if not math.isfinite(log10_p):
        raise AuditInputError("log-survival became non-finite")
    # A p-value is JSON-null when it is below the smallest subnormal float.
    # The log10 value is always retained; no artificial exact zero is emitted.
    min_log10_subnormal = math.log10(float(np.nextafter(0.0, 1.0)))
    p_value: float | None
    if log10_p >= min_log10_subnormal:
        candidate = 10.0**log10_p
        p_value = float(candidate) if candidate > 0.0 else None
    else:
        p_value = None
    return {
        "p_value": p_value,
        "log10_p_value": float(log10_p),
        "p_value_representable": p_value is not None,
    }


def log_chi_square_survival(statistic: float, dof: int) -> float:
    """Return log(Q(dof/2, statistic/2)) in log space.

    For integer chi-square degrees of freedom, the half-integer incomplete
    gamma recurrence is an exact expression and avoids both CDF subtraction
    and underflow of the regularized gamma function.
    """

    if not math.isfinite(float(statistic)) or statistic < 0.0:
        raise AuditInputError("chi-square statistic must be finite and non-negative")
    if type(dof) is not int or dof <= 0:
        raise AuditInputError("chi-square degrees of freedom must be a positive integer")
    if statistic == 0.0:
        return 0.0

    y = float(statistic) / 2.0
    if dof % 2 == 0:
        m = dof // 2
        logs = [-y + j * math.log(y) - math.lgamma(j + 1) for j in range(m)]
    else:
        # Q(1/2,y) = erfc(sqrt(y)) = 2*Phi(-sqrt(2y)); recur upward.
        m = dof // 2
        base = LOG2 + float(special.log_ndtr(-math.sqrt(2.0 * y)))
        terms = [
            -y + (j + 0.5) * math.log(y) - math.lgamma(j + 1.5)
            for j in range(m)
        ]
        return float(logsumexp([base, *terms]))
    return float(logsumexp(logs))


def chi_square_survival(statistic: float, dof: int) -> dict[str, Any]:
    log10_p = log_chi_square_survival(statistic, dof) / LN10
    return {
        "statistic": float(statistic),
        "dof": int(dof),
        **_survival_payload(log10_p),
    }


def normal_two_sided_survival(z: float) -> dict[str, Any]:
    if not math.isfinite(float(z)):
        raise AuditInputError("normal z statistic must be finite")
    log10_p = (math.log(2.0) + float(special.log_ndtr(-abs(float(z))))) / LN10
    return {"z": float(z), **_survival_payload(log10_p)}


def parity_bin_probabilities(
    lower_primes: np.ndarray, bin_edges: np.ndarray
) -> np.ndarray:
    """Exact conditional bin probabilities for an even-gap geometric null.

    Conditional on each lower prime ``p > 2``, the number K of odd-candidate
    steps to the next selected candidate is geometric with ``q=2/log(p)``.
    Therefore ``delta=2K/log(p)`` has exact discrete support ``{2,4,...}``
    relative to p.  This is a local parity surrogate, not a prime theorem.
    """

    p = np.asarray(lower_primes, dtype=np.float64)
    edges = np.asarray(bin_edges, dtype=np.float64)
    if p.ndim != 1 or p.size == 0 or np.any(p <= math.e):
        raise AuditInputError("parity null requires lower primes greater than e")
    if edges.ndim != 1 or edges.size < 2 or edges[0] != 0.0:
        raise AuditInputError("invalid parity-null edges")
    log_p = np.log(p)
    q = 2.0 / log_p
    if np.any(q <= 0.0) or np.any(q >= 1.0):
        raise AuditInputError("parity success probability must be in (0,1)")
    remainder = 1.0 - q
    result = np.zeros((p.size, edges.size - 1), dtype=np.float64)

    for index in range(edges.size - 1):
        lower_edge = float(edges[index])
        upper_edge = float(edges[index + 1])
        k_min = np.maximum(
            1,
            np.ceil(lower_edge * log_p / 2.0).astype(np.int64),
        )
        lower_survival = remainder ** (k_min - 1)
        if math.isinf(upper_edge):
            result[:, index] = lower_survival
            continue
        k_exclusive = np.ceil(upper_edge * log_p / 2.0).astype(np.int64)
        upper_survival = remainder ** np.maximum(k_exclusive - 1, 0)
        probability = lower_survival - upper_survival
        probability = np.where(k_exclusive > k_min, probability, 0.0)
        result[:, index] = probability

    result = np.maximum(result, 0.0)
    row_sums = np.sum(result, axis=1)
    if np.any(~np.isfinite(row_sums)) or not np.allclose(
        row_sums, 1.0, rtol=2e-10, atol=2e-10
    ):
        raise AuditInputError("parity-null bin probabilities do not sum to one")
    return result


def simulate_discrete_gap_values(
    lower_primes: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    """Simulate one conditional even-gap renewal value per lower prime."""

    p = np.asarray(lower_primes, dtype=np.float64)
    q = 2.0 / np.log(p)
    if np.any(p <= math.e) or np.any(q <= 0.0) or np.any(q >= 1.0):
        raise AuditInputError("invalid lower primes for discrete simulation")
    steps = rng.geometric(q).astype(np.float64)
    return 2.0 * steps / np.log(p)


def pearson_chi_square(
    observed: Sequence[int],
    expected: Sequence[float],
    supported_only: bool,
    label: str,
) -> dict[str, Any]:
    obs = np.asarray(observed, dtype=np.float64)
    exp = np.asarray(expected, dtype=np.float64)
    if obs.ndim != 1 or exp.ndim != 1 or obs.size != exp.size or obs.size == 0:
        raise AuditInputError(f"invalid histogram for {label}")
    if np.any(obs < 0) or np.any(exp < 0) or not np.all(np.isfinite(exp)):
        raise AuditInputError(f"negative/non-finite histogram for {label}")
    if not math.isclose(float(np.sum(obs)), float(np.sum(exp)), rel_tol=2e-10, abs_tol=2e-8):
        raise AuditInputError(f"histogram totals do not match for {label}")
    supported = exp > 0.0
    incompatible = np.any(obs[~supported] > 0)
    keep = supported if supported_only else np.ones_like(supported, dtype=bool)
    if incompatible:
        return {
            "label": label,
            "status": "INCOMPATIBLE_WITH_DECLARED_SUPPORT",
            "statistic": None,
            "dof": None,
            "p_value": None,
            "log10_p_value": None,
            "p_value_representable": False,
            "unsupported_cells_with_positive_observations": [
                int(i + 1) for i, value in enumerate(~supported) if obs[i] > 0
            ],
        }
    if int(np.sum(keep)) < 2:
        raise AuditInputError(f"not enough supported cells for {label}")
    stat = float(np.sum((obs[keep] - exp[keep]) ** 2 / exp[keep]))
    dof = int(np.sum(keep)) - 1
    return {
        "label": label,
        "status": "DESCRIPTIVE_ASYMPTOTIC_DIAGNOSTIC",
        "statistic": stat,
        "dof": dof,
        **chi_square_survival(stat, dof),
    }


def bh_step_up(
    log10_p_values: Sequence[float], alpha: float
) -> dict[str, Any]:
    """Benjamini--Hochberg step-up BH in log10-p space."""

    if not log10_p_values:
        raise AuditInputError("BH requires at least one p-value")
    if not 0.0 < alpha < 1.0:
        raise AuditInputError("BH alpha must be in (0,1)")
    logs = [float(value) for value in log10_p_values]
    if any(not math.isfinite(value) or value > 1e-10 for value in logs):
        raise AuditInputError("BH requires finite log10 p-values <= 0")
    m = len(logs)
    order = sorted(range(m), key=lambda index: (logs[index], index))
    qualifying: list[int] = []
    for rank, index in enumerate(order, start=1):
        threshold = math.log10(alpha) + math.log10(rank / m)
        if logs[index] <= threshold + 1e-15:
            qualifying.append(rank)
    k = max(qualifying) if qualifying else 0
    rejected = [False] * m
    for index in order[:k]:
        rejected[index] = True

    adjusted_sorted = [0.0] * m
    running = 0.0
    for position in range(m - 1, -1, -1):
        rank = position + 1
        candidate = logs[order[position]] + math.log10(m / rank)
        running = min(running, candidate) if position != m - 1 else candidate
        adjusted_sorted[position] = min(0.0, running)
    adjusted = [0.0] * m
    for position, index in enumerate(order):
        adjusted[index] = adjusted_sorted[position]
    return {
        "method": "Benjamini-Hochberg step-up",
        "alpha": float(alpha),
        "m": m,
        "largest_qualifying_rank": k,
        "rejected": rejected,
        "log10_adjusted_p_values": adjusted,
        "threshold_log10_at_largest_rank": (
            math.log10(alpha) + math.log10(k / m) if k else None
        ),
    }


# ---------------------------------------------------------------------------
# Smoke execution and output
# ---------------------------------------------------------------------------


def make_exponential_bin_edges(count: int = 10) -> np.ndarray:
    if type(count) is not int or count < 2:
        raise AuditInputError("bin count must be an integer >= 2")
    return np.asarray(
        [0.0]
        + [-math.log(1.0 - j / count) for j in range(1, count)]
        + [math.inf],
        dtype=np.float64,
    )


def _config_blocks(config: dict[str, Any]) -> list[BlockSpec]:
    return [BlockSpec(item["label"], item["lo"], item["hi"]) for item in config["blocks"]]


def verify_small_sieve_controls() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for limit, size in ((0, 1), (1, 1), (2, 1), (10, 3), (49, 7), (1000, 7), (1000, 1000)):
        expected = simple_sieve_primes(limit)
        actual = np.fromiter(iter_segmented_primes(limit, size), dtype=np.int64)
        if not np.array_equal(actual, expected):
            raise AuditInputError(
                f"segmented sieve differs from trusted sieve: limit={limit}, size={size}"
            )
        checks.append(
            {
                "limit": limit,
                "segment_size": size,
                "prime_count": int(actual.size),
                "match": True,
            }
        )
    return {
        "trusted_simple_sieve": "bytearray full Eratosthenes",
        "checks": checks,
        "boundary_ranges_limit_10_size_4": [
            {"lo": lo, "hi": hi} for lo, hi in segment_ranges(10, 4)
        ],
    }


def _array_sha256(values: np.ndarray) -> str:
    return hashlib.sha256(
        np.asarray(values, dtype="<i8").tobytes(order="C")
    ).hexdigest()


def run_smoke(config: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run only the frozen, manageable 10^8-scale smoke."""

    sieve_cfg = config["sieve_smoke"]
    limit = int(sieve_cfg["sieve_limit"])
    if limit >= PRODUCTION_LIMIT or int(sieve_cfg["data_cutoff"]) >= PRODUCTION_LIMIT:
        raise AuditInputError("refusing any 10^10 production execution")
    segment_size = int(sieve_cfg["segment_size"])
    blocks = _config_blocks(config)
    edges = make_exponential_bin_edges(int(config["binning"]["count"]))
    discrete_cfg = config["discrete_null"]
    simulation_replicates = int(discrete_cfg["simulation_replicates"])
    rng_seed = int(discrete_cfg["seed"])
    accumulator = StreamingGapAccumulator(
        blocks, edges, simulation_replicates, rng_seed
    )

    first_segment_record: dict[str, Any] | None = None
    total_primes = 0
    for segment in iter_segmented_prime_segments(limit, segment_size):
        total_primes += int(segment.primes.size)
        accumulator.ingest_segment(segment)
        if segment.index == 0:
            first_segment_record = {
                "index": segment.index,
                "lo": segment.lo,
                "hi": segment.hi,
                "hi_exclusive": segment.hi + 1,
                "prime_count": int(segment.primes.size),
                "first_prime": int(segment.primes[0]) if segment.primes.size else None,
                "last_prime": int(segment.primes[-1]) if segment.primes.size else None,
                "prime_vector_sha256": _array_sha256(segment.primes),
            }
    if first_segment_record is None:
        raise AuditInputError("segmented sieve yielded no first segment")
    if first_segment_record["hi_exclusive"] != FIRST_SEGMENT_LIMIT:
        raise AuditInputError("first segment does not cover [0,10^8)")
    if first_segment_record["prime_count"] != 5_761_455:
        raise AuditInputError(
            "first-segment prime count changed; expected pi(10^8)=5,761,455"
        )
    if first_segment_record["last_prime"] != 99_999_989:
        raise AuditInputError("first segment does not end with the expected prime")

    summaries = accumulator.summaries(float(config["bh"]["alpha"]))
    if sum(item["n_gaps"] for item in summaries) != accumulator.total_selected_gaps:
        raise AuditInputError("block gap totals do not match streamed gaps")
    if any(item["n_gaps"] <= 0 for item in summaries):
        raise AuditInputError("one or more configured blocks are empty")

    historical = verify_historical_evidence(config)
    small_controls = verify_small_sieve_controls()
    raw: dict[str, Any] = {
        "schema_version": "prime-gap-audit-repair/raw-v1",
        "analysis_id": ANALYSIS_ID,
        "status": "COMPLETE_DESCRIPTIVE_SMOKE",
        "scope_findings": ["N-06", "N-07", "N-08"],
        "interpretation": "DESCRIPTIVE_ONLY",
        "novelty_claim": False,
        "production_10e10_run": False,
        "sieve": {
            "sieve_limit": limit,
            "data_cutoff": int(sieve_cfg["data_cutoff"]),
            "segment_size": segment_size,
            "segment_ranges_are_inclusive": True,
            "total_primes_through_sieve_limit": total_primes,
            "streamed_lower_prime_gaps": accumulator.total_streamed_gaps,
            "selected_block_lower_prime_gaps": accumulator.total_selected_gaps,
            "first_segment": first_segment_record,
            "trusted_small_sieve_controls": small_controls,
        },
        "normalization": {
            "definition": "(p_{i+1}-p_i)/ln(p_i)",
            "denominator": "lower prime",
            "lower_prime_block_assignment": "lo <= p_i < hi",
            "successor_crossing_upper_boundary_included": True,
        },
        "binning": {
            "rule": "exponential quantile, J=10",
            "internal_edges": [float(value) for value in edges[:-1]],
            "last_bin": "[edge_9,+infinity)",
        },
        "discrete_null": {
            "model": "conditional parity-geometric renewal diagnostic",
            "candidate_support": "odd integers greater than 2; every gap is an even integer",
            "success_probability": "q(p)=2/ln(p)",
            "gap_definition": "delta=2K/ln(p), K~Geometric(q(p))",
            "bin_probabilities": "exact conditional geometric sums; no artificial mass in impossible bins",
            "simulation_replicates": simulation_replicates,
            "simulation_seed": rng_seed,
            "scientific_status": "diagnostic surrogate only; no wheel/singular-series/consecutive-pair model",
        },
        "blocks": summaries,
        "provenance": {
            "config_path": str(CONFIG_DIR / "prereg_pga_audit_n06_n08_20260924.json"),
            "config_sha256": sha256_file(
                CONFIG_DIR / "prereg_pga_audit_n06_n08_20260924.json"
            ),
            "code_path": str(Path(__file__).resolve()),
            "code_sha256": sha256_file(Path(__file__).resolve()),
            "historical_evidence": historical,
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
        },
    }

    continuous_logs = [
        item["chi_square_continuous_exp1_diagnostic"]["log10_p_value"]
        for item in summaries
    ]
    parity_logs = [
        item["chi_square_parity_geometric_diagnostic"]["log10_p_value"]
        for item in summaries
    ]
    continuous_bh = bh_step_up(continuous_logs, float(config["bh"]["alpha"]))
    parity_bh = bh_step_up(parity_logs, float(config["bh"]["alpha"]))

    cell_records: list[dict[str, Any]] = []
    for block in summaries:
        expected = block["continuous_exp1_expected_counts"]
        for bin_index, (observed, expected_count) in enumerate(
            zip(block["observed_counts"], expected), start=1
        ):
            z2 = (float(observed) - float(expected_count)) ** 2 / float(
                expected_count
            )
            cell_records.append(
                {
                    "block": block["label"],
                    "bin": bin_index,
                    "observed": int(observed),
                    "expected_continuous": float(expected_count),
                    "z_squared": float(z2),
                    "one_df_survival": chi_square_survival(z2, 1),
                    "structurally_empty_under_parity_floor": bin_index
                    in block["structural_support"]["empty_bins_by_edge_and_parity_floor"],
                    "interpretation": "exploratory numerical screen only; nested/correlated cells",
                }
            )
    cell_bh = bh_step_up(
        [record["one_df_survival"]["log10_p_value"] for record in cell_records],
        float(config["bh"]["alpha"]),
    )
    for record, rejected, adjusted in zip(
        cell_records,
        cell_bh["rejected"],
        cell_bh["log10_adjusted_p_values"],
    ):
        record["bh_step_up_rejected"] = bool(rejected)
        record["bh_step_up_log10_adjusted_p"] = float(adjusted)

    derived: dict[str, Any] = {
        "schema_version": "prime-gap-audit-repair/derived-v1",
        "analysis_id": ANALYSIS_ID,
        "status": "DESCRIPTIVE_ONLY",
        "scope_findings": ["N-06", "N-07", "N-08"],
        "novelty_claim": False,
        "production_10e10_run": False,
        "corrected_definitions": {
            "normalization": "lower prime",
            "bh": "step-up BH over four block-level families",
            "survival": "log-survival; underflow represented by JSON null plus log10 p",
        },
        "matched_range": {
            "blocks": config["blocks"],
            "why_matched": "same four EXP-0008 lower-prime decade blocks, with corrected boundary inclusion",
        },
        "bh_families": {
            "continuous_exp1_operational_diagnostic": {
                **continuous_bh,
                "warning": "The continuous null assigns mass to structurally impossible first bins; this is not a Gallagher-model conclusion.",
            },
            "parity_geometric_diagnostic": {
                **parity_bh,
                "warning": "The local parity surrogate is discrete but not a complete prime-process null; p-values remain descriptive.",
            },
        },
        "qm007_exploratory_40_cell_numerical_screen": {
            "family_size": len(cell_records),
            "bh": cell_bh,
            "cells": cell_records,
            "warning": "This corrects the malformed one-df survival arithmetic only. The 40 cells are nested and dependent; the first bin is structurally empty at these scales. No confirmatory or discovery interpretation is permitted.",
        },
        "unresolved_statistical_issues": [
            "The parity/geometric surrogate does not include wheel, singular-series, or consecutive-pair corrections.",
            "Prime gaps are serially/arithmetic dependent; Pearson chi-square p-values are not dependence-calibrated scientific p-values.",
            "The fixed-bin screen is exploratory and the bin edges themselves are scale-sensitive.",
            "No 10^9/10^10 scientific replication was run here; the planned 10^10 run was not executed.",
            "No novelty or mechanism claim follows from this audit repair.",
        ],
    }
    return raw, derived


def _json_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise AuditOutputError(f"cannot serialize finite JSON output: {exc}") from exc
    return (text + "\n").encode("utf-8")


def write_exclusive(path: Path, data: bytes) -> None:
    if path.exists():
        raise AuditOutputError(f"refusing to overwrite existing artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(data)
    except FileExistsError as exc:
        raise AuditOutputError(f"refusing to overwrite existing artifact: {path}") from exc
    except OSError as exc:
        raise AuditOutputError(f"cannot write artifact {path}: {exc}") from exc


def _format_log10(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"1e{value:.6g}"


def render_report(raw: dict[str, Any], derived: dict[str, Any]) -> str:
    sieve = raw["sieve"]
    first = sieve["first_segment"]
    lines = [
        "# Isolated audit repair — Q-M007/Q-M008 N-06/N-07/N-08",
        "",
        "**Status: descriptive audit smoke only. No novelty or discovery claim.**",
        "",
        "This run is isolated from the historical Q-M007/Q-M008 files. Historical configs and results were hash-checked and not modified. The planned 10^10 production sieve was not run.",
        "",
        "## Numerical repairs",
        "",
        "- Normalization is `(p_{i+1}-p_i)/ln(p_i)` with lower-prime block assignment `lo <= p_i < hi`; the successor is retained when it crosses the upper boundary.",
        "- BH is the step-up procedure, with later qualifying ranks propagated backward.",
        "- Chi-square and normal tails use log-survival calculations. A p-value below the representable float range is JSON `null` with its `log10_p_value`, never an artificial `0.0`.",
        "- The parity-geometric diagnostic has support `delta=2K/ln(p)`, `K` geometric with `q=2/ln(p)`. It retains the exact even-gap lattice and exposes the structurally empty first bin.",
        "",
        "## Segmented sieve control",
        "",
        f"- Sieve limit: `{sieve['sieve_limit']:,}`; segment size: `{sieve['segment_size']:,}`; segments are inclusive and non-overlapping.",
        f"- First segment `[{first['lo']:,}, {first['hi_exclusive']:,})` retained `{first['prime_count']:,}` primes, including `{first['first_prime']}` and ending at `{first['last_prime']:,}`.",
        f"- The first-segment vector SHA-256 is `{first['prime_vector_sha256']}`; trusted small-limit comparisons and boundary checks are recorded in the raw summary.",
        "",
        "## Matched 10^8-scale smoke",
        "",
        "The four blocks match the historical EXP-0008 lower-prime decade ranges, but use corrected lower-prime normalization and boundary inclusion. These numbers are a numerical/descriptive smoke, not a scale replication or a Gallagher test.",
        "",
        "| Block | n gaps | mean delta | SD | first-bin observed | first-bin parity expected | continuous chi2 (log10 p) | parity chi2 (log10 p) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for block in raw["blocks"]:
        continuous = block["chi_square_continuous_exp1_diagnostic"]
        parity = block["chi_square_parity_geometric_diagnostic"]
        lines.append(
            f"| {block['label']} | {block['n_gaps']:,} | {block['mean_delta']:.9f} | {block['standard_deviation_delta']:.9f} | {block['observed_counts'][0]} | {block['parity_geometric_expected_counts'][0]:.6g} | {continuous['statistic']:.3f} ({_format_log10(continuous['log10_p_value'])}) | {parity['statistic']:.3f} ({_format_log10(parity['log10_p_value'])}) |"
        )
    continuous_bh = derived["bh_families"]["continuous_exp1_operational_diagnostic"]
    parity_bh = derived["bh_families"]["parity_geometric_diagnostic"]
    lines += [
        "",
        "## Corrected BH screens",
        "",
        f"- Continuous Exp(1) operational family: largest qualifying rank `{continuous_bh['largest_qualifying_rank']}/{continuous_bh['m']}`; this null is structurally misspecified.",
        f"- Parity-geometric diagnostic family: largest qualifying rank `{parity_bh['largest_qualifying_rank']}/{parity_bh['m']}`; this is not a complete prime null.",
        f"- Q-M007 numerical 40-cell screen: corrected one-df survival arithmetic and step-up BH were recomputed for `{derived['qm007_exploratory_40_cell_numerical_screen']['family_size']}` nested cells, but the screen is exploratory and not confirmatory.",
        "",
        "## Unresolved issues and limits",
        "",
    ]
    lines.extend(f"- {issue}" for issue in derived["unresolved_statistical_issues"])
    lines += [
        "",
        "The historical Q-M007 and Q-M008 outputs remain evidence artifacts only. No statement here upgrades their earlier persistence or 38/40 wording.",
        "",
    ]
    return "\n".join(lines)


def execute(config_path: Path, digest_path: Path, output_subdir: Path) -> dict[str, Any]:
    config = load_frozen_config(config_path, digest_path)
    configured_subdir = Path(config["output_subdir"])
    if output_subdir != configured_subdir:
        raise AuditInputError(
            f"output path must equal frozen {configured_subdir}, got {output_subdir}"
        )
    output_dir = (AUDIT_DIR / output_subdir).resolve()
    allowed_root = AUDIT_DIR.resolve()
    if not str(output_dir).startswith(str(allowed_root) + str(Path("/"))):
        raise AuditInputError("output directory escapes the isolated audit directory")
    raw, derived = run_smoke(config)
    raw_path = output_dir / "raw_summary.json"
    derived_path = output_dir / "derived_summary.json"
    report_path = output_dir / "REPORT.md"
    manifest_path = output_dir / "artifact_manifest.json"
    for path in (raw_path, derived_path, report_path, manifest_path):
        if path.exists():
            raise AuditOutputError(f"refusing to overwrite existing artifact: {path}")

    write_exclusive(raw_path, _json_bytes(raw))
    write_exclusive(derived_path, _json_bytes(derived))
    write_exclusive(report_path, render_report(raw, derived).encode("utf-8"))
    manifest = {
        "schema_version": "prime-gap-audit-repair/manifest-v1",
        "analysis_id": ANALYSIS_ID,
        "config_sha256": raw["provenance"]["config_sha256"],
        "code_sha256": raw["provenance"]["code_sha256"],
        "artifacts": [
            {
                "path": str(path.relative_to(AUDIT_DIR)).replace("\\", "/"),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in (raw_path, derived_path, report_path)
        ],
        "historical_artifacts_modified": False,
    }
    write_exclusive(manifest_path, _json_bytes(manifest))
    return {
        "raw": str(raw_path),
        "derived": str(derived_path),
        "report": str(report_path),
        "manifest": str(manifest_path),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=CONFIG_DIR / "prereg_pga_audit_n06_n08_20260924.json",
    )
    parser.add_argument(
        "--config-sha256",
        type=Path,
        default=CONFIG_DIR / "prereg_pga_audit_n06_n08_20260924.sha256",
    )
    parser.add_argument(
        "--output-subdir",
        type=Path,
        default=Path("RESULTS/MATCHED_1E8_20260924"),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        paths = execute(args.config, args.config_sha256, args.output_subdir)
    except (AuditInputError, AuditIntegrityError, AuditOutputError) as exc:
        print(f"FAIL CLOSED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(paths, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
