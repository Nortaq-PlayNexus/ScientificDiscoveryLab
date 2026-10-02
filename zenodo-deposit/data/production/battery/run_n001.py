#!/usr/bin/env python3
"""Canonical N-001 repair runner for Q-P007 cluster-size storage and tau.

The runner is intentionally isolated from the historical Q-P007 runners and
results.  It writes one SQLite3 row per (L, realization_id, p_c arm), where the
cluster-size payload is a flat little-endian int64 array.  Complete tails are
defined as payload[1:] after removing exactly one largest-cluster entry from
that realization.  Canonical and refined p_c arms use one common uniform field
per realization.

No output is written in place.  Existing destinations are rejected, artifacts
are staged and validated before an atomic directory rename, and analysis fails
closed if the binary artifact, manifest, configuration hash, pairing, or raw
array invariants do not validate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import sqlite3
import sys
from typing import Any, Sequence
import uuid

import numpy as np
import scipy
from scipy import ndimage

LAB_ROOT = Path(__file__).resolve().parents[6]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
if str(SHARED_ENGINE) not in sys.path:
    sys.path.insert(0, str(SHARED_ENGINE))
from engine.hypothesis_testing.prereg import verify_frozen_config  # noqa: E402


RAW_SCHEMA = "n001-qp007-raw-v2"
MANIFEST_SCHEMA = "n001-qp007-manifest-v2"
SQLITE_APPLICATION_ID = 0x4E303031  # "N001"
SQLITE_USER_VERSION = 1
P_ARMS = ("canonical", "refined")


class N001Error(RuntimeError):
    """Base class for fail-closed N-001 errors."""


class ConfigError(N001Error):
    """Configuration is missing, inconsistent, or unsafe."""


class ArtifactError(N001Error):
    """Raw artifact or manifest is missing or malformed."""


class AnalysisError(N001Error):
    """A valid artifact cannot support the configured analysis."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def load_strict_json(path: Path, error_type: type[N001Error] = ConfigError) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise error_type(f"cannot read strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise error_type(f"top-level JSON value must be an object: {path}")
    return value


def write_strict_json(path: Path, value: dict[str, Any]) -> None:
    text = json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    ) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def realization_id(L: int, realization_index: int) -> str:
    return f"L{L:04d}-r{realization_index:06d}"


def _require_int(value: Any, label: str, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ConfigError(f"{label} must be an integer >= {minimum}, got {value!r}")
    return int(value)


def validate_config(config: dict[str, Any], profile_name: str) -> dict[str, Any]:
    if config.get("schema_version") != 1:
        raise ConfigError("N-001 config schema_version must equal 1")
    for key in ("audit_finding_id", "investigation_id", "run_id", "p_values", "rng", "storage", "analysis", "profiles"):
        if key not in config:
            raise ConfigError(f"missing required config key: {key}")
    if config["audit_finding_id"] != "N-001" or config["investigation_id"] != "Q-P007":
        raise ConfigError("this runner is restricted to audit finding N-001 / Q-P007")
    if not isinstance(config["rng"], dict) or not isinstance(config["storage"], dict):
        raise ConfigError("config rng and storage sections must be objects")
    if not isinstance(config["analysis"], dict) or not isinstance(config["profiles"], dict):
        raise ConfigError("config analysis and profiles sections must be objects")
    if config["rng"].get("generator") != "numpy.PCG64":
        raise ConfigError("only the explicitly configured numpy.PCG64 generator is supported")
    if config["storage"].get("format") != "SQLite3":
        raise ConfigError("N-001 raw storage format must be SQLite3")
    if config["storage"].get("array_dtype") != "little-endian int64":
        raise ConfigError("N-001 raw array dtype must be little-endian int64")
    if config["storage"].get("array_ndim") != 1:
        raise ConfigError("N-001 raw arrays must be one-dimensional")
    if config["storage"].get("component_backend") != "scipy.ndimage.label with deterministic four-neighbor structure":
        raise ConfigError("component backend must be the configured deterministic four-neighbor scipy.ndimage.label")

    p_values = config["p_values"]
    if not isinstance(p_values, dict):
        raise ConfigError("config.p_values must be an object")
    for arm in P_ARMS:
        p = p_values.get(arm)
        if isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(float(p)) or not 0.0 < float(p) < 1.0:
            raise ConfigError(f"p_values.{arm} must be finite and in (0, 1)")
    if float(p_values["canonical"]) <= float(p_values["refined"]):
        raise ConfigError("canonical p_c must be greater than refined p_c for this paired audit")

    profiles = config["profiles"]
    if profile_name not in profiles:
        raise ConfigError(f"unknown profile {profile_name!r}; expected one of {sorted(profiles)}")
    profile = profiles[profile_name]
    if not isinstance(profile, dict):
        raise ConfigError("profile must be a JSON object")

    L_list = profile.get("L_list")
    if not isinstance(L_list, list) or not L_list:
        raise ConfigError("profile.L_list must be a nonempty list")
    Ls = [_require_int(value, "profile.L_list entry", minimum=2) for value in L_list]
    if len(set(Ls)) != len(Ls):
        raise ConfigError("profile.L_list contains duplicates")
    n_real_raw = profile.get("n_real")
    if not isinstance(n_real_raw, dict):
        raise ConfigError("profile.n_real must be an object keyed by decimal L strings")
    n_real: dict[int, int] = {}
    for L_key, value in n_real_raw.items():
        if not isinstance(L_key, str) or not L_key.isdecimal():
            raise ConfigError(f"n_real key must be a decimal L string, got {L_key!r}")
        L = int(L_key)
        if L < 2 or str(L) != L_key:
            raise ConfigError(f"n_real L key must be a canonical decimal string, got {L_key!r}")
        n_real[L] = _require_int(value, f"n_real[{L}]")
    if set(n_real) != set(Ls):
        raise ConfigError("profile.n_real keys must exactly match profile.L_list")

    tau_L = _require_int(profile.get("tau_L"), "profile.tau_L", minimum=2)
    if tau_L not in Ls:
        raise ConfigError(f"active profile.tau_L={tau_L} is absent from profile.L_list={Ls}")

    windows = profile.get("fit_windows")
    if not isinstance(windows, list) or not windows:
        raise ConfigError("profile.fit_windows must be a nonempty list")
    names: set[str] = set()
    for window in windows:
        if not isinstance(window, dict):
            raise ConfigError("each fit window must be an object")
        name = window.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise ConfigError("fit-window names must be unique nonempty strings")
        names.add(name)
        for estimator in ("cumulative", "histogram"):
            bounds = window.get(estimator)
            if not isinstance(bounds, list) or len(bounds) != 2:
                raise ConfigError(f"fit window {name}.{estimator} must be [lo, hi]")
            lo = _require_int(bounds[0], f"fit window {name}.{estimator} lo")
            hi = _require_int(bounds[1], f"fit window {name}.{estimator} hi")
            if lo > hi:
                raise ConfigError(f"fit window {name}.{estimator} has lo > hi")

    bootstrap = profile.get("bootstrap")
    if not isinstance(bootstrap, dict):
        raise ConfigError("profile.bootstrap must be an object")
    draws = _require_int(bootstrap.get("draws"), "bootstrap.draws", minimum=2)
    block_size = _require_int(bootstrap.get("block_size"), "bootstrap.block_size")
    if n_real[tau_L] % block_size != 0:
        raise ConfigError("bootstrap.block_size must divide the active tau_L realization count")
    minimum_fraction = bootstrap.get("minimum_success_fraction")
    if not isinstance(minimum_fraction, (int, float)) or isinstance(minimum_fraction, bool) or not 0.0 < float(minimum_fraction) <= 1.0:
        raise ConfigError("bootstrap.minimum_success_fraction must be in (0, 1]")
    confidence = bootstrap.get("confidence_level")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0.0 < float(confidence) < 1.0:
        raise ConfigError("bootstrap.confidence_level must be in (0, 1)")
    _require_int(bootstrap.get("seed"), "bootstrap.seed", minimum=0)
    if profile.get("execution_class") not in {"infrastructure_smoke", "expensive_production"}:
        raise ConfigError("profile.execution_class is invalid")
    if not isinstance(profile.get("scientific_status"), str) or not profile["scientific_status"]:
        raise ConfigError("profile.scientific_status must be a nonempty string")
    analysis_bootstrap = config["analysis"].get("bootstrap")
    if not isinstance(analysis_bootstrap, dict):
        raise ConfigError("analysis.bootstrap must be an object")
    if analysis_bootstrap.get("unit") != "realization_block":
        raise ConfigError("analysis.bootstrap.unit must be realization_block")
    if analysis_bootstrap.get("clusters_resampled_individually") is not False:
        raise ConfigError("iid-cluster bootstrap must be explicitly disabled")
    if analysis_bootstrap.get("paired_resampling") is not True:
        raise ConfigError("paired realization-block resampling must be explicitly enabled")
    return profile


def artifact_names(profile_name: str) -> tuple[str, str, str]:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in profile_name)
    return (
        f"N001_{safe}_raw.sqlite3",
        f"N001_{safe}_manifest.json",
        f"N001_{safe}_summary.json",
    )


def seed_material(namespace: str, run_id: str, L: int, realization_index: int) -> bytes:
    label = f"{namespace}\0{run_id}\0L={L}\0realization={realization_index}".encode("utf-8")
    return hashlib.sha256(label).digest()


def generate_uniforms(namespace: str, run_id: str, L: int, realization_index: int) -> np.ndarray:
    entropy = int.from_bytes(seed_material(namespace, run_id, L, realization_index), byteorder="big", signed=False)
    generator = np.random.Generator(np.random.PCG64(np.random.SeedSequence(entropy)))
    return generator.random(L * L, dtype=np.float64)


def pack_mask(mask: np.ndarray) -> bytes:
    flat = np.asarray(mask, dtype=np.bool_).reshape(-1)
    return np.packbits(flat, bitorder="little").tobytes()


def unpack_mask(payload: bytes, site_count: int) -> np.ndarray:
    raw = np.frombuffer(payload, dtype=np.uint8)
    if raw.ndim != 1 or raw.size != (site_count + 7) // 8:
        raise ArtifactError("packed mask has the wrong byte length")
    return np.unpackbits(raw, count=site_count, bitorder="little").astype(bool, copy=False)


def flat_cluster_sizes(mask: np.ndarray) -> np.ndarray:
    matrix = np.asarray(mask, dtype=np.bool_).reshape((int(np.sqrt(mask.size)),) * 2)
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("cluster-size backend requires a square mask")
    structure = np.asarray([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)
    labels, component_count = ndimage.label(matrix, structure=structure)
    if component_count == 0:
        return np.asarray([], dtype="<i8")
    counts = np.bincount(labels.reshape(-1), minlength=component_count + 1)[1:]
    return np.sort(counts.astype(np.int64, copy=False))[::-1].astype("<i8", copy=False)


def _int64_bytes(array: np.ndarray) -> bytes:
    if array.ndim != 1:
        raise ValueError("only flat arrays may be serialized")
    return np.ascontiguousarray(array, dtype="<i8").tobytes(order="C")


def _create_database(
    db_path: Path,
    config: dict[str, Any],
    config_hash: str,
    profile_name: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute(f"PRAGMA application_id={SQLITE_APPLICATION_ID}")
        conn.execute(f"PRAGMA user_version={SQLITE_USER_VERSION}")
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.executescript(
            """
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            ) WITHOUT ROWID;
            CREATE TABLE realizations (
                L INTEGER NOT NULL,
                realization_index INTEGER NOT NULL,
                realization_id TEXT NOT NULL,
                base_seed_hex TEXT NOT NULL,
                uniform_sha256 TEXT NOT NULL,
                canonical_mask BLOB NOT NULL,
                refined_mask BLOB NOT NULL,
                canonical_mask_sha256 TEXT NOT NULL,
                refined_mask_sha256 TEXT NOT NULL,
                PRIMARY KEY (L, realization_id),
                UNIQUE (L, realization_index),
                CHECK (L >= 2),
                CHECK (realization_index >= 0)
            );
            CREATE TABLE cluster_arrays (
                L INTEGER NOT NULL,
                realization_id TEXT NOT NULL,
                realization_index INTEGER NOT NULL,
                p_arm TEXT NOT NULL,
                p_value REAL NOT NULL,
                full_sizes BLOB NOT NULL,
                storage_dtype TEXT NOT NULL,
                storage_ndim INTEGER NOT NULL,
                n_clusters INTEGER NOT NULL,
                tail_start INTEGER NOT NULL,
                n_tail INTEGER NOT NULL,
                largest_size INTEGER NOT NULL,
                occupied_sites INTEGER NOT NULL,
                full_sizes_sha256 TEXT NOT NULL,
                tail_sha256 TEXT NOT NULL,
                PRIMARY KEY (L, realization_id, p_arm),
                FOREIGN KEY (L, realization_id)
                    REFERENCES realizations(L, realization_id),
                CHECK (p_arm IN ('canonical', 'refined')),
                CHECK (storage_dtype = 'little-endian int64'),
                CHECK (storage_ndim = 1),
                CHECK (n_clusters >= 0),
                CHECK (occupied_sites >= 0),
                CHECK (
                    (n_clusters = 0 AND tail_start = 0 AND n_tail = 0 AND largest_size = 0)
                    OR
                    (n_clusters >= 1 AND tail_start = 1 AND n_tail = n_clusters - 1)
                )
            );
            CREATE INDEX cluster_arrays_by_arm
                ON cluster_arrays(L, p_arm, realization_index);
            """
        )
        metadata = {
            "artifact_schema": RAW_SCHEMA,
            "audit_finding_id": str(config["audit_finding_id"]),
            "investigation_id": str(config["investigation_id"]),
            "run_id": str(config["run_id"]),
            "config_sha256": config_hash,
            "profile_name": profile_name,
            "profile_json": json.dumps(profile, sort_keys=True, separators=(",", ":")),
            "p_values_json": json.dumps(
                {arm: float(config["p_values"][arm]) for arm in P_ARMS},
                sort_keys=True,
                separators=(",", ":"),
            ),
            "rng_generator": str(config["rng"]["generator"]),
            "seed_namespace": str(config["rng"]["seed_namespace"]),
            "active_tau_L": str(int(profile["tau_L"])),
            "component_backend": str(config["storage"]["component_backend"]),
        }
        conn.executemany("INSERT INTO metadata(key, value) VALUES (?, ?)", sorted(metadata.items()))

        manifest_realizations: list[dict[str, Any]] = []
        effective: dict[str, dict[str, Any]] = {}
        for L in profile["L_list"]:
            for arm in P_ARMS:
                effective.setdefault(str(L), {})[arm] = {
                    "completed_realizations": 0,
                    "effective_realizations": 0,
                    "excluded_empty_tail_realizations": 0,
                    "total_clusters": 0,
                    "total_tail_clusters": 0,
                }

            for index in range(int(profile["n_real"][str(L)])):
                rid = realization_id(int(L), index)
                seed_hex = seed_material(
                    str(config["rng"]["seed_namespace"]),
                    str(config["run_id"]),
                    int(L),
                    index,
                ).hex()
                uniforms = generate_uniforms(
                    str(config["rng"]["seed_namespace"]),
                    str(config["run_id"]),
                    int(L),
                    index,
                )
                uniform_hash = sha256_bytes(uniforms.tobytes(order="C"))
                masks = {arm: uniforms < float(config["p_values"][arm]) for arm in P_ARMS}
                packed = {arm: pack_mask(masks[arm]) for arm in P_ARMS}
                mask_hashes = {arm: sha256_bytes(packed[arm]) for arm in P_ARMS}
                conn.execute(
                    """
                    INSERT INTO realizations(
                        L, realization_index, realization_id, base_seed_hex,
                        uniform_sha256, canonical_mask, refined_mask,
                        canonical_mask_sha256, refined_mask_sha256
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        int(L),
                        index,
                        rid,
                        seed_hex,
                        uniform_hash,
                        sqlite3.Binary(packed["canonical"]),
                        sqlite3.Binary(packed["refined"]),
                        mask_hashes["canonical"],
                        mask_hashes["refined"],
                    ),
                )

                record: dict[str, Any] = {
                    "L": int(L),
                    "realization_index": index,
                    "realization_id": rid,
                    "base_seed_hex": seed_hex,
                    "uniform_sha256": uniform_hash,
                    "p_arms": {},
                }
                for arm in P_ARMS:
                    sizes = flat_cluster_sizes(masks[arm])
                    if sizes.ndim != 1:
                        raise ArtifactError("cluster-size backend violated the flat-array invariant")
                    if sizes.size and (np.any(sizes <= 0) or np.any(np.diff(sizes) > 0)):
                        raise ArtifactError("cluster sizes must be positive and non-increasing")
                    occupied = int(masks[arm].sum())
                    if int(sizes.sum()) != occupied:
                        raise ArtifactError("cluster sizes do not sum to the paired mask population")
                    n_tail = max(int(sizes.size) - 1, 0)
                    tail_start = 1 if sizes.size else 0
                    tail = sizes[tail_start:]
                    full_bytes = _int64_bytes(sizes)
                    tail_bytes = _int64_bytes(tail)
                    full_hash = sha256_bytes(full_bytes)
                    tail_hash = sha256_bytes(tail_bytes)
                    largest = int(sizes[0]) if sizes.size else 0
                    conn.execute(
                        """
                        INSERT INTO cluster_arrays(
                            L, realization_id, realization_index, p_arm, p_value,
                            full_sizes, storage_dtype, storage_ndim,
                            n_clusters, tail_start, n_tail, largest_size,
                            occupied_sites, full_sizes_sha256, tail_sha256
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            int(L),
                            rid,
                            index,
                            arm,
                            float(config["p_values"][arm]),
                            sqlite3.Binary(full_bytes),
                            "little-endian int64",
                            1,
                            int(sizes.size),
                            tail_start,
                            n_tail,
                            largest,
                            occupied,
                            full_hash,
                            tail_hash,
                        ),
                    )
                    counts = effective[str(L)][arm]
                    counts["completed_realizations"] += 1
                    counts["effective_realizations"] += int(n_tail > 0)
                    counts["excluded_empty_tail_realizations"] += int(n_tail == 0)
                    counts["total_clusters"] += int(sizes.size)
                    counts["total_tail_clusters"] += n_tail
                    record["p_arms"][arm] = {
                        "p_value": float(config["p_values"][arm]),
                        "mask_sha256": mask_hashes[arm],
                        "occupied_sites": occupied,
                        "n_clusters": int(sizes.size),
                        "tail_start": tail_start,
                        "n_tail": n_tail,
                        "largest_cluster_removed": largest,
                        "storage_dtype": "little-endian int64",
                        "storage_ndim": 1,
                        "full_sizes_sha256": full_hash,
                        "tail_sha256": tail_hash,
                    }
                manifest_realizations.append(record)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {"realizations": manifest_realizations, "effective_counts": effective}


def _connect_readonly(db_path: Path) -> sqlite3.Connection:
    uri = db_path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _metadata_map(conn: sqlite3.Connection) -> dict[str, str]:
    try:
        return {str(row["key"]): str(row["value"]) for row in conn.execute("SELECT key, value FROM metadata")}
    except sqlite3.DatabaseError as exc:
        raise ArtifactError(f"raw artifact metadata table is malformed: {exc}") from exc


def _require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise ArtifactError(f"{label} mismatch: actual={actual!r}, expected={expected!r}")


def validate_artifact(artifact_dir: Path, config_path: Path, expected_profile: str | None = None) -> dict[str, Any]:
    artifact_dir = Path(artifact_dir)
    config_path = Path(config_path)
    if not artifact_dir.is_dir():
        raise ArtifactError(f"required artifact directory is missing: {artifact_dir}")
    config = load_strict_json(config_path, ConfigError)
    config_hash = sha256_file(config_path)
    manifest_candidates = sorted(artifact_dir.glob("*_manifest.json"))
    if len(manifest_candidates) != 1:
        raise ArtifactError(f"expected exactly one N-001 manifest, found {len(manifest_candidates)}")
    manifest = load_strict_json(manifest_candidates[0], ArtifactError)
    if manifest.get("manifest_schema") != MANIFEST_SCHEMA:
        raise ArtifactError("manifest schema mismatch")
    profile_name = manifest.get("profile_name")
    if not isinstance(profile_name, str):
        raise ArtifactError("manifest.profile_name is missing")
    if expected_profile is not None and profile_name != expected_profile:
        raise ArtifactError(f"artifact profile {profile_name!r} does not match requested {expected_profile!r}")
    profile = validate_config(config, profile_name)
    _require_equal(manifest.get("audit_finding_id"), "N-001", "manifest.audit_finding_id")
    _require_equal(manifest.get("investigation_id"), "Q-P007", "manifest.investigation_id")
    _require_equal(manifest.get("run_id"), config["run_id"], "manifest.run_id")
    _require_equal(manifest.get("config_sha256"), config_hash, "manifest.config_sha256")
    _require_equal(manifest.get("profile"), profile, "manifest.profile")
    _require_equal(manifest.get("active_tau_L"), int(profile["tau_L"]), "manifest.active_tau_L")
    _require_equal(manifest.get("p_values"), {arm: float(config["p_values"][arm]) for arm in P_ARMS}, "manifest.p_values")
    _require_equal(
        manifest.get("requested_realizations"),
        {str(L): int(profile["n_real"][str(L)]) for L in profile["L_list"]},
        "manifest.requested_realizations",
    )
    _require_equal(manifest.get("raw_array_ndim"), 1, "manifest.raw_array_ndim")
    _require_equal(manifest.get("raw_array_dtype"), "little-endian int64", "manifest.raw_array_dtype")
    _require_equal(
        manifest.get("component_backend"),
        config["storage"]["component_backend"],
        "manifest.component_backend",
    )
    _require_equal(manifest.get("largest_cluster_policy"), "remove_one_per_realization_before_pooling", "manifest.largest_cluster_policy")
    _require_equal(manifest.get("scientific_status"), profile["scientific_status"], "manifest.scientific_status")
    _require_equal(manifest.get("scientific_result"), None, "manifest.scientific_result")
    production_lock = manifest.get("production_prereg")
    if profile["execution_class"] == "infrastructure_smoke":
        _require_equal(production_lock, None, "manifest.production_prereg for smoke")
    else:
        if not isinstance(production_lock, dict):
            raise ArtifactError("production manifest requires production_prereg")
        lock_path_value = production_lock.get("path")
        if not isinstance(lock_path_value, str) or not Path(lock_path_value).is_file():
            raise ArtifactError("production preregistration lock is missing")
        # The lock's identity is the CANONICAL PAYLOAD hash recorded by
        # validate_production_prereg() (locked["config_sha256"]). Comparing that
        # against the exact file byte hash is a scope error: the frozen document
        # embeds its own digest and is pretty-printed, so the two can never be
        # equal and every production run fails closed for the wrong reason.
        # Re-verifying through verify_frozen_config() recomputes the canonical
        # digest from the file and rejects any edit, so tamper detection is
        # preserved rather than weakened.
        try:
            lock_payload = verify_frozen_config(Path(lock_path_value))
        except Exception as exc:  # integrity, schema, or strict-JSON failure
            raise ArtifactError(
                f"production preregistration lock failed re-verification: {exc}"
            ) from exc
        _require_equal(
            production_lock.get("sha256"),
            str(lock_payload["config_sha256"]),
            "production preregistration lock canonical SHA-256",
        )
    config_filename = manifest.get("config_filename")
    if not isinstance(config_filename, str) or Path(config_filename).name != config_filename:
        raise ArtifactError("manifest.config_filename must be a simple filename")
    runner_record = manifest.get("runner")
    if not isinstance(runner_record, dict):
        raise ArtifactError("manifest.runner must be an object")
    runner_filename = runner_record.get("filename")
    runner_hash = runner_record.get("sha256")
    if not isinstance(runner_filename, str) or Path(runner_filename).name != runner_filename:
        raise ArtifactError("manifest.runner.filename must be a simple filename")
    if not isinstance(runner_hash, str) or len(runner_hash) != 64 or any(ch not in "0123456789abcdef" for ch in runner_hash):
        raise ArtifactError("manifest.runner.sha256 is malformed")
    _require_equal(
        runner_hash,
        sha256_file(Path(__file__).resolve()),
        "manifest.runner.sha256 vs current canonical runner",
    )
    software = manifest.get("software")
    if not isinstance(software, dict) or set(software) != {"python", "numpy", "scipy"}:
        raise ArtifactError("manifest.software must record python, numpy, and scipy")
    if any(not isinstance(software[key], str) or not software[key] for key in software):
        raise ArtifactError("manifest software versions must be nonempty strings")

    artifact_record = manifest.get("artifact")
    if not isinstance(artifact_record, dict):
        raise ArtifactError("manifest.artifact must be an object")
    artifact_name = artifact_record.get("filename")
    manifest_name = manifest.get("manifest_filename")
    if not isinstance(artifact_name, str) or Path(artifact_name).name != artifact_name:
        raise ArtifactError("manifest artifact filename must be a simple filename")
    if not isinstance(manifest_name, str) or Path(manifest_name).name != manifest_name or manifest_name != manifest_candidates[0].name:
        raise ArtifactError("manifest self-filename is invalid")
    db_path = artifact_dir / artifact_name
    if not db_path.is_file():
        raise ArtifactError(f"required raw binary artifact is missing: {db_path}")
    _require_equal(artifact_record.get("format"), "SQLite3", "manifest artifact format")
    _require_equal(artifact_record.get("sha256"), sha256_file(db_path), "artifact SHA-256")
    _require_equal(artifact_record.get("size_bytes"), db_path.stat().st_size, "artifact byte size")

    summary_record = manifest.get("summary")
    if not isinstance(summary_record, dict):
        raise ArtifactError("manifest.summary must be an object")
    summary_name = summary_record.get("filename")
    if not isinstance(summary_name, str) or Path(summary_name).name != summary_name:
        raise ArtifactError("manifest.summary.filename must be a simple filename")
    _require_equal(
        summary_name,
        artifact_names(profile_name)[2],
        "manifest.summary.filename",
    )
    summary_path = artifact_dir / summary_name
    if not summary_path.is_file():
        raise ArtifactError(f"required summary artifact is missing: {summary_path}")
    _require_equal(summary_record.get("sha256"), sha256_file(summary_path), "summary SHA-256")
    _require_equal(summary_record.get("size_bytes"), summary_path.stat().st_size, "summary byte size")

    try:
        conn = _connect_readonly(db_path)
    except sqlite3.DatabaseError as exc:
        raise ArtifactError(f"cannot open raw binary artifact: {exc}") from exc
    try:
        quick_check = conn.execute("PRAGMA quick_check").fetchone()[0]
        if quick_check != "ok":
            raise ArtifactError(f"SQLite quick_check failed: {quick_check}")
        app_id = int(conn.execute("PRAGMA application_id").fetchone()[0])
        user_version = int(conn.execute("PRAGMA user_version").fetchone()[0])
        _require_equal(app_id, SQLITE_APPLICATION_ID, "SQLite application_id")
        _require_equal(user_version, SQLITE_USER_VERSION, "SQLite user_version")
        tables = {
            str(row[0])
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        }
        if tables != {"metadata", "realizations", "cluster_arrays"}:
            raise ArtifactError(f"unexpected SQLite schema tables: {sorted(tables)}")

        metadata = _metadata_map(conn)
        expected_metadata = {
            "artifact_schema": RAW_SCHEMA,
            "audit_finding_id": "N-001",
            "investigation_id": "Q-P007",
            "run_id": str(config["run_id"]),
            "config_sha256": config_hash,
            "profile_name": profile_name,
            "rng_generator": "numpy.PCG64",
            "seed_namespace": str(config["rng"]["seed_namespace"]),
            "active_tau_L": str(int(profile["tau_L"])),
            "component_backend": str(config["storage"]["component_backend"]),
        }
        for key, expected in expected_metadata.items():
            _require_equal(metadata.get(key), expected, f"metadata.{key}")
        _require_equal(json.loads(metadata["p_values_json"]), {arm: float(config["p_values"][arm]) for arm in P_ARMS}, "metadata p_values")
        _require_equal(json.loads(metadata["profile_json"]), profile, "metadata profile snapshot")

        realization_rows = list(conn.execute("SELECT * FROM realizations ORDER BY L, realization_index"))
        array_rows = list(conn.execute("SELECT * FROM cluster_arrays ORDER BY L, realization_index, p_arm"))
        manifest_records = manifest.get("realizations")
        if not isinstance(manifest_records, list) or len(manifest_records) != len(realization_rows):
            raise ArtifactError("manifest realization record count mismatch")
        expected_pair_count = sum(int(profile["n_real"][str(L)]) for L in profile["L_list"])
        if len(realization_rows) != expected_pair_count or len(array_rows) != 2 * expected_pair_count:
            raise ArtifactError("raw realization or cluster-array row count mismatch")

        rows_by_key = {(int(row["L"]), str(row["realization_id"])): row for row in realization_rows}
        arrays_by_key = {
            (int(row["L"]), str(row["realization_id"]), str(row["p_arm"])): row
            for row in array_rows
        }
        if len(rows_by_key) != len(realization_rows) or len(arrays_by_key) != len(array_rows):
            raise ArtifactError("duplicate realization or cluster-array keys")

        computed_effective: dict[str, dict[str, Any]] = {}
        seen_by_L: dict[int, set[int]] = {}
        for record in manifest_records:
            if not isinstance(record, dict):
                raise ArtifactError("manifest realization records must be objects")
            L = _require_int(record.get("L"), "manifest realization L", minimum=2)
            index = _require_int(record.get("realization_index"), "manifest realization index", minimum=0)
            rid = record.get("realization_id")
            if rid != realization_id(L, index):
                raise ArtifactError(f"manifest realization_id mismatch for L={L}, index={index}")
            if L not in profile["L_list"] or index >= int(profile["n_real"][str(L)]):
                raise ArtifactError(f"unexpected realization {rid}")
            if index in seen_by_L.setdefault(L, set()):
                raise ArtifactError(f"duplicate realization index for L={L}")
            seen_by_L[L].add(index)
            row = rows_by_key.get((L, rid))
            if row is None:
                raise ArtifactError(f"missing raw realization row for {rid}")
            _require_equal(int(row["realization_index"]), index, f"{rid} realization_index")
            expected_seed_hex = seed_material(
                str(config["rng"]["seed_namespace"]),
                str(config["run_id"]),
                L,
                index,
            ).hex()
            _require_equal(str(row["base_seed_hex"]), expected_seed_hex, f"{rid} base_seed_hex")
            _require_equal(str(row["base_seed_hex"]), record.get("base_seed_hex"), f"{rid} manifest base_seed_hex")
            _require_equal(str(row["uniform_sha256"]), record.get("uniform_sha256"), f"{rid} uniform_sha256")

            regenerated = generate_uniforms(
                str(config["rng"]["seed_namespace"]),
                str(config["run_id"]),
                L,
                index,
            )
            regenerated_hash = sha256_bytes(regenerated.tobytes(order="C"))
            if regenerated_hash != str(row["uniform_sha256"]):
                raise ArtifactError(f"{rid} common-uniform hash does not reproduce")
            expected_masks = {arm: regenerated < float(config["p_values"][arm]) for arm in P_ARMS}
            for arm in P_ARMS:
                stored_mask = bytes(row[f"{arm}_mask"])
                _require_equal(sha256_bytes(stored_mask), str(row[f"{arm}_mask_sha256"]), f"{rid} {arm} mask hash")
                if not np.array_equal(unpack_mask(stored_mask, L * L), expected_masks[arm]):
                    raise ArtifactError(f"{rid} {arm} mask is not the paired threshold mask")

            arm_record = record.get("p_arms")
            if not isinstance(arm_record, dict) or set(arm_record) != set(P_ARMS):
                raise ArtifactError(f"{rid} manifest p_arms must contain exactly canonical and refined")
            for arm in P_ARMS:
                if not isinstance(arm_record[arm], dict):
                    raise ArtifactError(f"{rid} {arm} manifest p-arm record must be an object")
                arm_row = arrays_by_key.get((L, rid, arm))
                if arm_row is None:
                    raise ArtifactError(f"missing {arm} cluster array for {rid}")
                _require_equal(int(arm_row["realization_index"]), index, f"{rid} {arm} realization_index")
                _require_equal(float(arm_row["p_value"]), float(config["p_values"][arm]), f"{rid} {arm} p_value")
                _require_equal(str(arm_row["storage_dtype"]), "little-endian int64", f"{rid} {arm} storage_dtype")
                ndim = int(arm_row["storage_ndim"])
                if ndim != 1:
                    raise ArtifactError(f"{rid} {arm} storage_ndim={ndim}; nested arrays are forbidden")
                expected_tail_start = 1 if int(arm_row["n_clusters"]) else 0
                _require_equal(
                    int(arm_row["tail_start"]),
                    expected_tail_start,
                    f"{rid} {arm} tail_start",
                )
                payload = bytes(arm_row["full_sizes"])
                if len(payload) % np.dtype("<i8").itemsize != 0:
                    raise ArtifactError(f"{rid} {arm} full_sizes byte length is malformed")
                sizes = np.frombuffer(payload, dtype="<i8")
                if sizes.ndim != 1:
                    raise ArtifactError(f"{rid} {arm} decoded array is not flat")
                _require_equal(int(sizes.size), int(arm_row["n_clusters"]), f"{rid} {arm} n_clusters")
                _require_equal(
                    int(arm_row["n_tail"]),
                    max(int(sizes.size) - 1, 0),
                    f"{rid} {arm} n_tail",
                )
                if sizes.size and (np.any(sizes <= 0) or np.any(np.diff(sizes) > 0)):
                    raise ArtifactError(f"{rid} {arm} sizes are not positive and non-increasing")
                expected_sizes = flat_cluster_sizes(expected_masks[arm])
                if not np.array_equal(sizes, expected_sizes):
                    raise ArtifactError(
                        f"{rid} {arm} cluster sizes are not the components of the regenerated mask"
                    )
                _require_equal(int(arm_row["largest_size"]), int(sizes[0]) if sizes.size else 0, f"{rid} {arm} largest_size")
                _require_equal(
                    int(arm_row["occupied_sites"]),
                    int(expected_masks[arm].sum()),
                    f"{rid} {arm} occupied_sites vs mask",
                )
                _require_equal(int(arm_row["occupied_sites"]), int(sizes.sum()), f"{rid} {arm} occupied_sites vs sizes")
                _require_equal(str(arm_row["full_sizes_sha256"]), sha256_bytes(payload), f"{rid} {arm} full hash")
                tail = sizes[expected_tail_start:]
                _require_equal(str(arm_row["tail_sha256"]), sha256_bytes(_int64_bytes(tail)), f"{rid} {arm} tail hash")
                expected_arm = arm_record[arm]
                _require_equal(expected_arm.get("p_value"), float(config["p_values"][arm]), f"{rid} {arm} manifest p_value")
                for key in (
                    "mask_sha256",
                    "occupied_sites",
                    "n_clusters",
                    "tail_start",
                    "n_tail",
                    "largest_cluster_removed",
                    "storage_dtype",
                    "storage_ndim",
                    "full_sizes_sha256",
                    "tail_sha256",
                ):
                    if key == "mask_sha256":
                        db_value = str(row[f"{arm}_mask_sha256"])
                    elif key == "largest_cluster_removed":
                        db_value = int(arm_row["largest_size"])
                    elif key == "storage_ndim":
                        db_value = ndim
                    else:
                        db_value = arm_row[key]
                    _require_equal(expected_arm.get(key), db_value, f"{rid} {arm} manifest field {key}")

                counts = computed_effective.setdefault(str(L), {}).setdefault(
                    arm,
                    {
                        "completed_realizations": 0,
                        "effective_realizations": 0,
                        "excluded_empty_tail_realizations": 0,
                        "total_clusters": 0,
                        "total_tail_clusters": 0,
                    },
                )
                counts["completed_realizations"] += 1
                counts["effective_realizations"] += int(tail.size > 0)
                counts["excluded_empty_tail_realizations"] += int(tail.size == 0)
                counts["total_clusters"] += int(sizes.size)
                counts["total_tail_clusters"] += int(tail.size)

        for L in profile["L_list"]:
            expected_indices = set(range(int(profile["n_real"][str(L)])))
            if seen_by_L.get(int(L), set()) != expected_indices:
                raise ArtifactError(f"realization indices are incomplete for L={L}")
        _require_equal(manifest.get("effective_sample_counts"), computed_effective, "manifest effective_sample_counts")
        if not any(value["effective_realizations"] > 0 for arm in computed_effective.values() for value in arm.values()):
            raise ArtifactError("all stored realization tails are empty")
        manifest_pairing = manifest.get("pairing")
        expected_pairing = {
            "common_uniform_field_per_realization": True,
            "canonical_refined_aligned_by_realization_id": True,
            "iid_cluster_bootstrap": False,
        }
        if manifest_pairing != expected_pairing:
            raise ArtifactError("manifest pairing/bootstrap provenance is incomplete or inconsistent")
    except sqlite3.DatabaseError as exc:
        raise ArtifactError(f"malformed SQLite artifact: {exc}") from exc
    finally:
        conn.close()

    manifest["_config"] = config
    manifest["_profile"] = profile
    stored_summary = load_strict_json(summary_path, ArtifactError)
    recomputed_summary = analyze_validated_artifact(artifact_dir, manifest)
    if stored_summary != recomputed_summary:
        raise ArtifactError(
            "stored summary does not exactly match canonical analysis of validated raw arrays"
        )
    manifest["_summary"] = stored_summary
    return manifest


def load_tails(artifact_dir: Path, manifest: dict[str, Any], L: int, p_arm: str) -> tuple[list[str], list[np.ndarray]]:
    if p_arm not in P_ARMS:
        raise AnalysisError(f"unknown p_c arm {p_arm!r}")
    artifact_name = manifest["artifact"]["filename"]
    db_path = Path(artifact_dir) / artifact_name
    conn: sqlite3.Connection | None = None
    try:
        conn = _connect_readonly(db_path)
        rows = list(
            conn.execute(
                """
                SELECT realization_id, full_sizes, n_tail, storage_ndim
                FROM cluster_arrays
                WHERE L = ? AND p_arm = ?
                ORDER BY realization_index
                """,
                (int(L), p_arm),
            )
        )
    except sqlite3.DatabaseError as exc:
        raise ArtifactError(f"cannot read validated tails: {exc}") from exc
    finally:
        if conn is not None:
            conn.close()
    ids: list[str] = []
    tails: list[np.ndarray] = []
    for row in rows:
        if int(row["storage_ndim"]) != 1:
            raise ArtifactError("validated artifact acquired a nested storage_ndim")
        sizes = np.frombuffer(bytes(row["full_sizes"]), dtype="<i8")
        tail_start = 1 if sizes.size else 0
        if sizes.ndim != 1 or sizes.size - tail_start != int(row["n_tail"]):
            raise ArtifactError("tail row changed or has a malformed flat-array shape")
        ids.append(str(row["realization_id"]))
        tails.append(sizes[tail_start:].copy())
    return ids, tails


def _weighted_loglog_fit(x: np.ndarray, y: np.ndarray, weights: np.ndarray, tau_sign: float) -> dict[str, float | int]:
    if x.size < 3 or x.size != y.size or x.size != weights.size:
        raise AnalysisError("log-log fit has fewer than three usable points")
    matrix = np.column_stack((np.ones(x.size), x))
    root_weight = np.sqrt(np.asarray(weights, dtype=float))
    weighted_matrix = matrix * root_weight[:, None]
    weighted_y = y * root_weight
    coefficients, *_ = np.linalg.lstsq(weighted_matrix, weighted_y, rcond=None)
    residual = y - matrix @ coefficients
    information = matrix.T @ (np.asarray(weights, dtype=float)[:, None] * matrix)
    covariance = np.linalg.pinv(information, rcond=1e-12)
    slope = float(coefficients[1])
    return {
        "tau": float(tau_sign * slope),
        "intercept": float(coefficients[0]),
        "slope": slope,
        "slope_standard_error": float(math.sqrt(max(float(covariance[1, 1]), 0.0))),
        "chi2_reduced_diagnostic": float(np.sum((residual * root_weight) ** 2) / max(x.size - 2, 1)),
        "points": int(x.size),
    }


def fit_tau(tails: Sequence[np.ndarray], estimator: str, lo: int, hi: int) -> dict[str, Any] | None:
    flat_arrays = [np.asarray(tail, dtype=np.int64) for tail in tails]
    if any(array.ndim != 1 for array in flat_arrays):
        raise AnalysisError("tau analysis received a nested array")
    nonempty = [array for array in flat_arrays if array.size]
    if not nonempty:
        return None
    pooled = np.concatenate(nonempty)
    if np.any(pooled <= 0):
        raise AnalysisError("tail contains non-positive cluster sizes")
    effective_realizations = len(nonempty)

    if estimator == "cumulative":
        ordered = np.sort(pooled)[::-1]
        grid = np.unique(np.geomspace(int(lo), int(hi), 250).astype(np.int64))
        n_gt = np.searchsorted(-ordered, -(grid + 1)).astype(float)
        keep = n_gt >= 3
        if int(keep.sum()) < 20:
            return None
        x = np.log(grid[keep].astype(float))
        y = np.log(n_gt[keep])
        weights = np.sqrt(n_gt[keep])
        fit = _weighted_loglog_fit(x, y, weights, tau_sign=1.0)
        # N_>(s) ~ s^(-(tau-1)), hence slope = 1-tau.
        fit["tau"] = float(1.0 - fit["slope"])
        fit.update(
            {
                "estimator": "cumulative",
                "requested_window": [int(lo), int(hi)],
                "used_window": [int(grid[keep].min()), int(grid[keep].max())],
                "requested_realizations": int(len(tails)),
                "effective_realizations": effective_realizations,
                "tail_clusters": int(pooled.size),
            }
        )
        return fit

    if estimator == "histogram":
        histogram = np.bincount(pooled)
        sizes = np.arange(histogram.size, dtype=np.int64)
        keep = (sizes >= int(lo)) & (sizes <= int(hi)) & (histogram > 0)
        if int(keep.sum()) < 12:
            return None
        x = np.log(sizes[keep].astype(float))
        y = np.log(histogram[keep].astype(float))
        weights = np.sqrt(histogram[keep].astype(float))
        fit = _weighted_loglog_fit(x, y, weights, tau_sign=-1.0)
        fit.update(
            {
                "estimator": "histogram",
                "requested_window": [int(lo), int(hi)],
                "used_window": [int(sizes[keep].min()), int(sizes[keep].max())],
                "requested_realizations": int(len(tails)),
                "effective_realizations": effective_realizations,
                "tail_clusters": int(pooled.size),
            }
        )
        return fit

    raise AnalysisError(f"unknown tau estimator {estimator!r}")


def _bootstrap_seed(base_seed: int, *labels: object) -> int:
    material = "\0".join([str(base_seed), *(str(label) for label in labels)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big", signed=False)


def realization_block_indices(
    realization_count: int,
    block_size: int,
    generator: np.random.Generator,
) -> np.ndarray:
    if realization_count < 1 or block_size < 1 or realization_count % block_size:
        raise AnalysisError("realization blocks are invalid")
    blocks = [np.arange(start, start + block_size) for start in range(0, realization_count, block_size)]
    selected = generator.integers(0, len(blocks), size=len(blocks))
    return np.concatenate([blocks[int(index)] for index in selected])


def _interval(values: Sequence[float], confidence: float) -> list[float]:
    array = np.asarray(values, dtype=float)
    alpha = 1.0 - float(confidence)
    return [float(np.quantile(array, alpha / 2.0)), float(np.quantile(array, 1.0 - alpha / 2.0))]


def paired_realization_bootstrap(
    canonical_tails: Sequence[np.ndarray],
    refined_tails: Sequence[np.ndarray],
    canonical_ids: Sequence[str],
    refined_ids: Sequence[str],
    estimator: str,
    lo: int,
    hi: int,
    settings: dict[str, Any],
    seed_label: str,
) -> dict[str, Any]:
    if len(canonical_tails) != len(refined_tails) or list(canonical_ids) != list(refined_ids):
        raise AnalysisError("canonical/refined realization IDs are not paired")
    n = len(canonical_tails)
    block_size = int(settings["block_size"])
    generator = np.random.Generator(
        np.random.PCG64(np.random.SeedSequence(_bootstrap_seed(int(settings["seed"]), seed_label)))
    )
    canonical_draws: list[float] = []
    refined_draws: list[float] = []
    for _ in range(int(settings["draws"])):
        selected = realization_block_indices(n, block_size, generator)
        canonical_fit = fit_tau([canonical_tails[int(index)] for index in selected], estimator, lo, hi)
        refined_fit = fit_tau([refined_tails[int(index)] for index in selected], estimator, lo, hi)
        if canonical_fit is None or refined_fit is None:
            continue
        canonical_draws.append(float(canonical_fit["tau"]))
        refined_draws.append(float(refined_fit["tau"]))
    success_fraction = len(canonical_draws) / int(settings["draws"])
    minimum = int(math.ceil(float(settings["minimum_success_fraction"]) * int(settings["draws"])))
    if len(canonical_draws) < minimum or len(refined_draws) != len(canonical_draws):
        raise AnalysisError(
            f"paired realization bootstrap for {seed_label} has only {len(canonical_draws)}/{settings['draws']} usable draws"
        )
    differences = np.asarray(refined_draws) - np.asarray(canonical_draws)
    confidence = float(settings["confidence_level"])
    return {
        "resampling_unit": "realization_block",
        "clusters_resampled_individually": False,
        "paired_across_p_arms": True,
        "block_size": block_size,
        "block_count": n // block_size,
        "draws_requested": int(settings["draws"]),
        "draws_successful": len(canonical_draws),
        "success_fraction": success_fraction,
        "confidence_level": confidence,
        "canonical_sd": float(np.std(canonical_draws, ddof=1)),
        "refined_sd": float(np.std(refined_draws, ddof=1)),
        "paired_delta_refined_minus_canonical_sd": float(np.std(differences, ddof=1)),
        "canonical_interval": _interval(canonical_draws, confidence),
        "refined_interval": _interval(refined_draws, confidence),
        "paired_delta_interval": _interval(differences, confidence),
    }


def analyze_validated_artifact(artifact_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    config = manifest["_config"]
    profile = manifest["_profile"]
    tau_L = int(profile["tau_L"])
    canonical_ids, canonical_tails = load_tails(artifact_dir, manifest, tau_L, "canonical")
    refined_ids, refined_tails = load_tails(artifact_dir, manifest, tau_L, "refined")
    if not canonical_ids or canonical_ids != refined_ids:
        raise AnalysisError("active tau_L has no aligned canonical/refined realizations")
    if not any(tail.size for tail in canonical_tails) or not any(tail.size for tail in refined_tails):
        raise AnalysisError("active tau_L has an empty complete tail in both required arms")

    fits: dict[str, Any] = {}
    for window in profile["fit_windows"]:
        name = str(window["name"])
        fits[name] = {}
        for estimator in ("cumulative", "histogram"):
            lo_hi = window[estimator]
            lo, hi = int(lo_hi[0]), int(lo_hi[1])
            canonical_point = fit_tau(canonical_tails, estimator, lo, hi)
            refined_point = fit_tau(refined_tails, estimator, lo, hi)
            if canonical_point is None or refined_point is None:
                raise AnalysisError(f"configured {estimator} window {name} has insufficient usable bins")
            bootstrap = paired_realization_bootstrap(
                canonical_tails,
                refined_tails,
                canonical_ids,
                refined_ids,
                estimator,
                lo,
                hi,
                profile["bootstrap"],
                f"{tau_L}:{name}:{estimator}",
            )
            fits[name][estimator] = {
                "canonical": canonical_point,
                "refined": refined_point,
                "paired_point_delta_refined_minus_canonical": float(refined_point["tau"] - canonical_point["tau"]),
                "bootstrap": bootstrap,
            }

    status = str(profile["scientific_status"])
    if profile["execution_class"] == "infrastructure_smoke":
        interpretation = "Infrastructure smoke only; no scientific tau or p_c conclusion is authorized."
        power_status = "NOT_APPLICABLE_TO_INFRASTRUCTURE_SMOKE"
        power_reason = "No empirical power estimate is made from deterministic infrastructure smoke data."
    else:
        interpretation = "Fit diagnostics only; scientific interpretation is intentionally deferred to a separately reviewed production report."
        power_status = "REQUIRES_PAIRED_PRODUCTION_BOOTSTRAP_VARIANCE"
        power_reason = "A post-run power calculation must use the paired realization-block variance from this production artifact."
    return {
        "summary_schema": "n001-qp007-summary-v3",
        "audit_finding_id": "N-001",
        "investigation_id": "Q-P007",
        "run_id": str(config["run_id"]),
        "profile_name": str(manifest["profile_name"]),
        "profile_source": f"profiles.{manifest['profile_name']}",
        "active_tau_L": tau_L,
        "active_tau_L_source": f"profiles.{manifest['profile_name']}.tau_L",
        "requested_realizations_at_tau_L": len(canonical_tails),
        "effective_realizations_at_tau_L": {
            "canonical": sum(tail.size > 0 for tail in canonical_tails),
            "refined": sum(tail.size > 0 for tail in refined_tails),
        },
        "paired_realization_ids_sha256": sha256_bytes("\n".join(canonical_ids).encode("utf-8")),
        "largest_cluster_policy": "one largest entry removed independently within every realization before pooling",
        "cumulative_tau_definition": "tau = 1 - survival_slope for N_>(s) ~ s^(-(tau-1))",
        "fits": fits,
        "power_analysis": {
            "status": power_status,
            "planning_target_only": config["analysis"]["planning_only"],
            "reason": power_reason,
        },
        "scientific_result": None,
        "interpretation": interpretation,
        "status": status,
    }


def analyze_artifact(artifact_dir: Path, config_path: Path, expected_profile: str | None = None) -> dict[str, Any]:
    manifest = validate_artifact(artifact_dir, config_path, expected_profile)
    return manifest["_summary"]


def validate_production_prereg(
    prereg_path: Path,
    source_config_path: Path,
    production_profile: dict[str, Any],
) -> str:
    """Validate a separate immutable lock before any production execution."""
    locked = verify_frozen_config(prereg_path)
    parameters = locked.get("parameters")
    if not isinstance(parameters, dict):
        raise ConfigError("production preregistration has no parameters object")
    def require(actual: Any, expected: Any, label: str) -> None:
        if actual != expected:
            raise ConfigError(f"{label} mismatch: actual={actual!r}, expected={expected!r}")

    require(
        parameters.get("audit_finding_id"),
        "N-001",
        "production preregistration audit_finding_id",
    )
    require(
        parameters.get("source_repair_config_sha256"),
        sha256_file(source_config_path),
        "production preregistration source config SHA-256",
    )
    require(
        parameters.get("profile_name"),
        "production",
        "production preregistration profile_name",
    )
    profile_json = json.dumps(
        production_profile,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    require(
        parameters.get("production_profile_sha256"),
        sha256_bytes(profile_json),
        "production preregistration production profile SHA-256",
    )
    return str(locked["config_sha256"])


def run_experiment(
    config_path: Path,
    profile_name: str,
    output_dir: Path,
    production_confirmation: str | None = None,
    production_prereg_path: Path | None = None,
) -> dict[str, Any]:
    config_path = Path(config_path).resolve()
    output_dir = Path(output_dir).resolve()
    config = load_strict_json(config_path, ConfigError)
    profile = validate_config(config, profile_name)
    production_lock = None
    if profile["execution_class"] == "expensive_production":
        if production_confirmation != "N-001-PRODUCTION":
            raise ConfigError(
                "expensive production profile is guarded; explicit --confirm-production N-001-PRODUCTION is required"
            )
        if production_prereg_path is None:
            raise ConfigError(
                "expensive production requires a separate immutable --production-prereg lock"
            )
        production_lock = {
            "filename": Path(production_prereg_path).resolve().name,
            "path": str(Path(production_prereg_path).resolve()),
            "sha256": validate_production_prereg(
                Path(production_prereg_path), config_path, profile
            ),
        }
    if output_dir.exists():
        raise ArtifactError(f"refusing to overwrite existing output directory: {output_dir}")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = output_dir.parent / f".{output_dir.name}.staging-{os.getpid()}-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        db_name, manifest_name, summary_name = artifact_names(profile_name)
        db_path = staging / db_name
        config_hash = sha256_file(config_path)
        raw_summary = _create_database(db_path, config, config_hash, profile_name, profile)
        manifest: dict[str, Any] = {
            "manifest_schema": MANIFEST_SCHEMA,
            "audit_finding_id": "N-001",
            "investigation_id": "Q-P007",
            "run_id": str(config["run_id"]),
            "profile_name": profile_name,
            "config_sha256": config_hash,
            "config_filename": config_path.name,
            "production_prereg": production_lock,
            "runner": {
                "filename": Path(__file__).name,
                "sha256": sha256_file(Path(__file__).resolve()),
            },
            "software": {
                "python": sys.version,
                "numpy": np.__version__,
                "scipy": scipy.__version__,
            },
            "profile_source": f"profiles.{profile_name}",
            "profile": profile,
            "active_tau_L": int(profile["tau_L"]),
            "p_values": {arm: float(config["p_values"][arm]) for arm in P_ARMS},
            "raw_array_dtype": "little-endian int64",
            "raw_array_ndim": 1,
            "component_backend": str(config["storage"]["component_backend"]),
            "raw_storage": "one full_sizes BLOB per realization and p_c arm; complete tail is full_sizes[1:]",
            "largest_cluster_policy": "remove_one_per_realization_before_pooling",
            "pairing": {
                "common_uniform_field_per_realization": True,
                "canonical_refined_aligned_by_realization_id": True,
                "iid_cluster_bootstrap": False,
            },
            "requested_realizations": {str(L): int(profile["n_real"][str(L)]) for L in profile["L_list"]},
            "effective_sample_counts": raw_summary["effective_counts"],
            "realizations": raw_summary["realizations"],
            "artifact": {
                "filename": db_name,
                "size_bytes": db_path.stat().st_size,
                "sha256": sha256_file(db_path),
                "format": "SQLite3",
            },
            "manifest_filename": manifest_name,
            "scientific_status": str(profile["scientific_status"]),
            "scientific_result": None,
        }
        analysis_manifest = {**manifest, "_config": config, "_profile": profile}
        summary = analyze_validated_artifact(staging, analysis_manifest)
        summary_path = staging / summary_name
        write_strict_json(summary_path, summary)
        manifest["summary"] = {
            "filename": summary_name,
            "size_bytes": summary_path.stat().st_size,
            "sha256": sha256_file(summary_path),
        }
        write_strict_json(staging / manifest_name, manifest)
        validate_artifact(staging, config_path, profile_name)
        os.replace(staging, output_dir)
        return summary
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="run one explicitly selected profile into a new directory")
    run_parser.add_argument("--config", type=Path, required=True)
    run_parser.add_argument("--profile", required=True)
    run_parser.add_argument("--output-dir", type=Path, required=True)
    run_parser.add_argument("--confirm-production")
    run_parser.add_argument("--production-prereg", type=Path)

    validate_parser = subparsers.add_parser("validate", help="fail-closed validation of a completed artifact")
    validate_parser.add_argument("--config", type=Path, required=True)
    validate_parser.add_argument("--artifact-dir", type=Path, required=True)
    validate_parser.add_argument("--profile")

    analyze_parser = subparsers.add_parser("analyze", help="validate then emit dependence-aware fit diagnostics")
    analyze_parser.add_argument("--config", type=Path, required=True)
    analyze_parser.add_argument("--artifact-dir", type=Path, required=True)
    analyze_parser.add_argument("--profile")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "run":
            summary = run_experiment(
                args.config,
                args.profile,
                args.output_dir,
                production_confirmation=args.confirm_production,
                production_prereg_path=args.production_prereg,
            )
        elif args.command == "validate":
            manifest = validate_artifact(args.artifact_dir, args.config, args.profile)
            summary = {
                "validation": "PASS",
                "profile_name": manifest["profile_name"],
                "active_tau_L": manifest["active_tau_L"],
                "scientific_result": None,
            }
        else:
            summary = analyze_artifact(args.artifact_dir, args.config, args.profile)
        print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (N001Error, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
