#!/usr/bin/env python3
"""Run the bounded, read-only N-004 RNG calibration smoke.

This entry point has no production mode.  It replays the stored 80x24 audit
matrix, verifies historical hashes, and performs a tiny stream-plumbing check;
it never imports the historical runner and never emits a certification verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import platform
import shutil
import sys
import uuid
from typing import Any

import numpy as np
import scipy

REPAIR_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = REPAIR_ROOT.parents[3]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
if str(SHARED_ENGINE) not in sys.path:
    sys.path.insert(0, str(SHARED_ENGINE))
CODE_ROOT = REPAIR_ROOT / "CODE"
if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from engine.hypothesis_testing.prereg import verify_frozen_config  # noqa: E402
from engine.utilities.core import rng  # noqa: E402
from n004_calibration import (  # noqa: E402
    N004Error,
    dependence_diagnostics,
    replay_historical_audit,
    row_preserving_resample,
    sha256_file,
)

DEFAULT_CONFIG = REPAIR_ROOT / "CONFIG" / "n004_smoke_config.json"


class SmokeError(RuntimeError):
    """Fail-closed smoke error."""


class MTAdapter:
    def __init__(self, seed: int):
        self.generator = np.random.RandomState(seed)

    def integers(self, low: int, high: int, size: int, dtype=np.uint32):
        if high == 2**32:
            lo = self.generator.randint(0, 65536, size).astype(np.uint32)
            hi = self.generator.randint(0, 65536, size).astype(np.uint32)
            raw = (hi << np.uint32(16)) | lo
        else:
            raw = self.generator.randint(low, high, size)
        return np.asarray(raw, dtype=dtype)

    def random(self, size: int):
        return np.asarray(self.generator.random(size))


def make_generator(name: str, seed: int):
    if name == "G_LAB":
        return rng("N004:smoke", seed)
    if name == "G_PCG":
        return np.random.default_rng(seed)
    if name == "G_MT":
        return MTAdapter(seed)
    raise SmokeError(f"unsupported smoke generator: {name}")


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    if config.get("experiment_id") != "N-004-RNG-CALIBRATION-SMOKE":
        raise SmokeError("unexpected N-004 smoke experiment")
    params = config.get("parameters")
    if not isinstance(params, dict):
        raise SmokeError("N-004 config has no parameters object")
    if params.get("execution_class") != "infrastructure_smoke":
        raise SmokeError("only infrastructure_smoke is permitted")
    if params.get("production_run") is not False:
        raise SmokeError("production execution must be disabled")
    if params.get("certification_claim") is not False:
        raise SmokeError("certification claim must be disabled")
    if params.get("scientific_result", "missing") is not None:
        raise SmokeError("scientific_result must be null")
    if params.get("audit_finding_id") != "N-004":
        raise SmokeError("config is not scoped to N-004")
    seeds = params.get("live_plumbing_seeds")
    bits = params.get("live_plumbing_bit_lengths")
    if not isinstance(seeds, list) or not 1 <= len(seeds) <= 8:
        raise SmokeError("live smoke seed count is outside the hard cap")
    if not isinstance(bits, list) or not bits or any(
        type(value) is not int or value < 256 or value > 16384 or value % 8
        for value in bits
    ):
        raise SmokeError("live smoke bit lengths must be 256..16384 and byte-aligned")
    if params.get("live_battery_analysis") is not False:
        raise SmokeError("bounded smoke must not run statistical battery inference")
    return params


def load_config(path: Path) -> dict[str, Any]:
    config = verify_frozen_config(path)
    validate_config(config)
    return config


def verify_historical_inputs(params: dict[str, Any]) -> list[dict[str, Any]]:
    hashes = params.get("historical_input_sha256")
    if not isinstance(hashes, dict) or not hashes:
        raise SmokeError("historical input hash map is missing")
    records = []
    for relative, expected in sorted(hashes.items()):
        if Path(relative).is_absolute() or not isinstance(expected, str):
            raise SmokeError(f"malformed historical input entry: {relative}")
        path = (LAB_ROOT / relative).resolve()
        try:
            path.relative_to(LAB_ROOT.resolve())
        except ValueError as exc:
            raise SmokeError(f"historical input escapes lab root: {relative}") from exc
        if not path.is_file():
            raise SmokeError(f"historical input is missing: {relative}")
        actual = sha256_file(path)
        if actual != expected:
            raise SmokeError(f"historical input hash mismatch: {relative}")
        records.append({"path": relative, "sha256": actual, "size_bytes": path.stat().st_size})
    return records


def draw_shared_streams_for_bits(generator: Any, n_bits: int) -> dict[str, Any]:
    if type(n_bits) is not int or n_bits < 256 or n_bits > 16384 or n_bits % 8:
        raise SmokeError("invalid bounded stream length")
    n_bytes = n_bits // 8
    raw = generator.integers(0, 256, n_bytes, dtype=np.uint32).astype(np.uint8)
    bits = np.unpackbits(raw)
    if bits.size != n_bits:
        raise SmokeError("stream adapter produced the wrong bit count")
    return {
        "n_bits": int(bits.size),
        "bytes_sha256": hashlib.sha256(raw.tobytes()).hexdigest(),
        "bits_sha256": hashlib.sha256(bits.tobytes()).hexdigest(),
        "stream_mode": "shared_single_draw_per_generator_and_seed",
    }


def run_live_plumbing(params: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for name in params["live_plumbing_generators"]:
        for seed in params["live_plumbing_seeds"]:
            generator = make_generator(str(name), int(seed))
            for n_bits in params["live_plumbing_bit_lengths"]:
                rows.append(
                    {
                        "generator": str(name),
                        "seed": int(seed),
                        **draw_shared_streams_for_bits(generator, int(n_bits)),
                    }
                )
    return {
        "status": "PASS_STREAM_PLUMBING_ONLY",
        "battery_analysis_executed": False,
        "rows": rows,
        "generator_count": len(params["live_plumbing_generators"]),
        "seed_count": len(params["live_plumbing_seeds"]),
        "bit_lengths": [int(x) for x in params["live_plumbing_bit_lengths"]],
    }


def _forbidden_keys(value: Any, path: str = "payload") -> None:
    if isinstance(value, dict):
        forbidden = {"decision", "verdict", "certification", "certified"}
        for key, child in value.items():
            if key in forbidden:
                raise SmokeError(f"forbidden claim field at {path}.{key}")
            _forbidden_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _forbidden_keys(child, f"{path}[{index}]")


def validate_claim_contract(payload: dict[str, Any]) -> None:
    _forbidden_keys(payload)
    if payload.get("status") != "INFRASTRUCTURE_SMOKE_ONLY":
        raise SmokeError("invalid smoke status")
    if payload.get("scientific_result", "missing") is not None:
        raise SmokeError("smoke scientific_result must be null")
    if payload.get("certification_claim") is not False:
        raise SmokeError("smoke certification_claim must be false")
    if payload.get("production_run_launched") is not False:
        raise SmokeError("smoke production_run_launched must be false")


def write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def run_smoke(config_path: Path, output_dir: Path) -> dict[str, Any]:
    config_path = config_path.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    if output_dir.exists():
        raise SmokeError(f"refusing to overwrite existing output directory: {output_dir}")
    config = load_config(config_path)
    params = validate_config(config)
    historical_inputs = verify_historical_inputs(params)
    # This guard is intentionally before any generator construction.
    if params.get("production_run") is not False:
        raise SmokeError("production profile is guarded")
    audit_path = (LAB_ROOT / params["historical_audit_result"]).resolve()
    replay = replay_historical_audit(audit_path)
    live = run_live_plumbing(params)
    sample_matrix = np.asarray(
        replay["summaries"]["G_LAB"]["per_seed_small_p_count"]["values"], dtype=float
    ).reshape(-1, 1)
    resampled, indices = row_preserving_resample(sample_matrix, draws=4, seed=7)
    payload: dict[str, Any] = {
        "schema": "n004-rng-calibration-smoke/v1",
        "status": "INFRASTRUCTURE_SMOKE_ONLY",
        "audit_finding_id": "N-004",
        "experiment_id": config["experiment_id"],
        "scientific_result": None,
        "certification_claim": False,
        "production_run_launched": False,
        "historical_inputs": historical_inputs,
        "historical_replay": replay,
        "live_stream_plumbing": live,
        "dependence_policy": {
            "seed_rows_preserved": True,
            "pooled_pvalue_inference": False,
            "per_test_familywise_rule": params["per_test_familywise_rule"],
            "stream_mode": params["historical_stream_mode"],
        },
        "row_resampling_smoke": {
            "draws": int(resampled.shape[0]),
            "index_shape": list(indices.shape),
            "source": "historical_G_LAB_per_seed_small_p_counts",
            "all_indices_in_range": bool(
                np.all((indices >= 0) & (indices < sample_matrix.shape[0]))
            ),
            "resampled_shape": list(resampled.shape),
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    validate_claim_contract(payload)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = output_dir.parent / f".{output_dir.name}.staging-{os.getpid()}-{uuid.uuid4().hex}"
    staging.mkdir()
    try:
        result_path = staging / "N004_rng_calibration_smoke_results.json"
        write_json_exclusive(result_path, payload)
        manifest = {
            "schema": "n004-rng-calibration-smoke-manifest/v1",
            "status": "PASS_INFRASTRUCTURE_SMOKE_ONLY",
            "config": {
                "path": str(config_path),
                "sha256": sha256_file(config_path),
            },
            "result": {
                "filename": result_path.name,
                "sha256": sha256_file(result_path),
                "size_bytes": result_path.stat().st_size,
            },
            "production_run_launched": False,
            "scientific_result": None,
            "certification_claim": False,
        }
        write_json_exclusive(staging / "N004_rng_calibration_smoke_manifest.json", manifest)
        os.replace(staging, output_dir)
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = run_smoke(args.config, args.output_dir)
    except (N004Error, SmokeError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 2
    print(json.dumps({
        "status": result["status"],
        "replay": result["historical_replay"]["status"],
        "live": result["live_stream_plumbing"]["status"],
        "scientific_result": result["scientific_result"],
        "certification_claim": result["certification_claim"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
