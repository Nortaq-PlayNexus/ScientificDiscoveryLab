#!/usr/bin/env python3
"""N-004 production runner - per-test dependence-aware RNG battery calibration.

Answers the audit's question: which INDIVIDUAL battery tests are calibrated, per
generator and per stream length, independent of the withdrawn pooled decision?

Frozen protocol: CONFIG/prereg_N004_PRODUCTION.json (config_sha256 bound, never
overwritten). The shared battery module is hash-checked at runtime and is never
modified.

Subcommands: run, analyze, validate.

Design notes that matter for interpretation:
  * The primary statistic is the uniformity of each test's p-value ACROSS
    independent seeds, not a single pooled pass/fail. That is what the audit
    asked for and it is the only reading that survives shared input streams.
  * A deliberately broken generator is included and MUST be flagged. If it is
    not, the run is classified BATTERY_INVALID and no statement about G_LAB is
    permitted.
  * Family-wise inference per seed is reported two ways: Holm (assumes
    independence) and a max-T permutation control that respects the shared
    stream. The disagreement between them is itself reported.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

INV_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = INV_ROOT.parents[3]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
for _p in (str(SHARED_ENGINE), str(SHARED_ENGINE.parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engine.hypothesis_testing.prereg import verify_frozen_config  # noqa: E402
from engine.utilities.core import rng as lab_rng  # noqa: E402
from engine.validation import rng_battery as rb  # noqa: E402

PREREG = INV_ROOT / "CONFIG" / "prereg_N004_PRODUCTION.json"
MANIFEST_SCHEMA = "n004-calibration-manifest-v1"
SUMMARY_SCHEMA = "n004-calibration-summary-v1"

BATTERY_SHA256 = "5f53f3eacdf38e8cf0d47ddf3f7f71935856120fe08120f043347caa663b3b9e"

WORKERS = 8


class N004Error(RuntimeError):
    pass


class ConfigError(N004Error):
    pass


class GateError(N004Error):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_strict_json(path: Path) -> dict[str, Any]:
    def no_dupes(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ConfigError(f"duplicate JSON key: {k}")
            out[k] = v
        return out

    def no_nonfinite(x):
        raise ConfigError(f"non-finite JSON number: {x}")

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=no_dupes, parse_constant=no_nonfinite)


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True, allow_nan=False)
        fh.write("\n")
    return path


# --------------------------------------------------------------------------
# generators
# --------------------------------------------------------------------------

def gen_glab(seed: int):
    """The laboratory stream: sha256-derived PCG64, exactly as every experiment uses it."""
    return lab_rng(f"n004-production-{seed}", seed)


def gen_pcg64(seed: int):
    return np.random.default_rng(seed)


class RandomStateShim:
    """Adapter giving the legacy RandomState the modern Generator API.

    ``np.random.RandomState`` (Mersenne Twister) exposes ``randint`` and
    ``random_sample``, not ``integers``/``random``. The shared battery calls the
    modern names, so without this shim the entire MT19937 arm raised
    AttributeError on every seed. Caught by the run's own error accounting: 260
    of 1040 evaluations failed, all of them this generator.
    """

    def __init__(self, rs: np.random.RandomState):
        self._rs = rs

    def integers(self, low: int, high: int, size=None, dtype=None) -> np.ndarray:
        lo, hi = int(low), int(high)
        if hi <= 2 ** 31:
            arr = self._rs.randint(lo, hi, size=size)
        else:
            # RandomState.randint is int32-bounded and raises
            # "high is out of bounds for int32" for the battery's 2**32 word
            # draw, so build 32-bit words from two 16-bit draws instead.
            n = 1 if size is None else int(np.prod(np.atleast_1d(size)))
            a = self._rs.randint(0, 2 ** 16, size=n).astype(np.uint64)
            b = self._rs.randint(0, 2 ** 16, size=n).astype(np.uint64)
            vals = ((a << 16) | b) % np.uint64(hi - lo) + np.uint64(lo)
            arr = vals if size is not None else int(vals[0])
        if dtype is not None:
            arr = arr.astype(dtype)
        return arr

    def random(self, size=None) -> np.ndarray:
        return self._rs.random_sample(size)


def gen_mt19937(seed: int):
    return RandomStateShim(np.random.RandomState(seed))


class BrokenLCG:
    """Deliberately broken generator used as a positive control.

    A 31-bit linear congruential engine with the classic spectral weaknesses:
    modulus 2^31-1, multiplier 1103515245, increment 12345. The state is
    returned as a float in [0,1) by dividing by the modulus, which keeps the
    short-period lattice structure visible in the low bits.
    """

    MOD = 2 ** 31 - 1
    A = 1103515245
    C = 12345

    def __init__(self, seed: int):
        self.state = int(seed) % self.MOD

    def _next_u32(self) -> int:
        self.state = (self.A * self.state + self.C) % self.MOD
        return self.state

    def random(self, size: int) -> np.ndarray:
        out = np.empty(size, dtype=np.float64)
        for i in range(size):
            out[i] = self._next_u32() / float(self.MOD)
        return out

    def integers(self, low: int, high: int, size=None, dtype=None) -> np.ndarray:
        n = 1 if size is None else int(np.prod(np.atleast_1d(size)))
        span = int(high) - int(low)
        vals = np.array([self._next_u32() % span for _ in range(n)], dtype=np.int64)
        if dtype is not None and np.issubdtype(np.dtype(dtype), np.integer):
            return vals.astype(dtype)
        return vals + int(low)


GENERATOR_FACTORIES = {
    "G_LAB": gen_glab,
    "PCG64_direct": gen_pcg64,
    "MT19937": gen_mt19937,
    "WEAK_LCG_BROKEN": BrokenLCG,
}


# --------------------------------------------------------------------------
# one battery evaluation
# --------------------------------------------------------------------------

def battery_pvalues(generator: str, seed: int, shift: int) -> list[float]:
    """Run the unmodified shared battery once and return its 24 p-values."""
    gen = GENERATOR_FACTORIES[generator](seed)
    nbytes, nfloat, nword = rb.NBYTES << shift, rb.NF << shift, rb.NW << shift
    bytes_arr = gen.integers(0, 256, nbytes, dtype=np.uint32).astype(np.uint8)
    floats_arr = gen.random(nfloat)
    words_arr = gen.integers(0, 2 ** 32, nword, dtype=np.uint32).astype(np.uint32)
    bits = np.unpackbits(bytes_arr)
    # NOTE: run_battery takes (bits, bytes_arr, floats_arr, words_arr)
    out = rb.run_battery(bits, bytes_arr, floats_arr, words_arr)
    return [float(p) for _, p in out]


def _worker(task: tuple[str, int, int]) -> tuple[str, int, int, list[float], float]:
    generator, seed, shift = task
    t0 = time.perf_counter()
    try:
        pvals = battery_pvalues(generator, seed, shift)
        err = ""
    except Exception as exc:  # a broken generator may legitimately fail
        pvals = []
        err = f"{type(exc).__name__}: {exc}"
    return generator, seed, shift, pvals, time.perf_counter() - t0, err  # type: ignore[return-value]


# --------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------

def holm_rejections(pvals: np.ndarray, alpha: float) -> int:
    """Number of Holm step-down rejections for one seed (assumes independence)."""
    p = np.asarray(pvals, dtype=float)
    finite = np.sort(p[np.isfinite(p)])
    m = finite.size
    count = 0
    for i, v in enumerate(finite):
        if v <= alpha / (m - i):
            count += 1
        else:
            break
    return count


def bonferroni_rejections(pvals: np.ndarray, alpha: float) -> int:
    """Bonferroni count: the family-wise control that is VALID UNDER ARBITRARY
    DEPENDENCE between tests.

    This is the correct dependence-respecting family-wise measure for this
    setting, because the 24 tests inside one seed all read the same input stream
    and are positively dependent. Bonferroni needs no independence assumption.

    An earlier draft of this file used a "max-T permutation" control that
    permuted the observed p-values to build a null for the maximum. That is
    invalid: the maximum is permutation-invariant, so every permuted maximum
    equals the observed maximum, and the test could never reject. In a preflight
    it reported a 0.000 family-wise rate for a deliberately broken generator
    that Holm rejected on 12 of 12 seeds. The substitution is recorded in
    CONFIG/production_changes.jsonl.
    """
    p = np.asarray(pvals, dtype=float)
    p = p[np.isfinite(p)]
    if p.size == 0:
        return 0
    return int(np.sum(p <= alpha / p.size))


def sidak_rejections(pvals: np.ndarray, alpha: float) -> int:
    """Sidak count: slightly more powerful than Bonferroni but assumes independence.

    Reported only to expose how much the tests' dependence matters: the gap
    between Sidak and Bonferroni is a direct measure of the dependence penalty.
    """
    p = np.asarray(pvals, dtype=float)
    p = p[np.isfinite(p)]
    if p.size == 0:
        return 0
    thresh = 1.0 - (1.0 - alpha) ** (1.0 / p.size)
    return int(np.sum(p <= thresh))


def ks_uniform(pvals: np.ndarray) -> tuple[float, float]:
    """One-sample KS of p-values against Uniform(0,1)."""
    p = np.asarray(pvals, dtype=float)
    p = p[np.isfinite(p)]
    if p.size < 5:
        return float("nan"), float("nan")
    res = stats.kstest(p, "uniform")
    return float(res.statistic), float(res.pvalue)


def exact_binomial_band(k: int, n: int, alpha: float = 0.01) -> tuple[float, float]:
    """Two-sided exact Clopper-Pearson band for a rejection rate."""
    if n == 0:
        return (0.0, 1.0)
    lo = 0.0 if k == 0 else float(stats.beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(stats.beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def bh_reject(pvals: np.ndarray, alpha: float) -> np.ndarray:
    """Benjamini-Hochberg step-up decision booleans."""
    p = np.asarray(pvals, dtype=float)
    ok = np.isfinite(p)
    out = np.zeros(p.shape, dtype=bool)
    if not ok.any():
        return out
    vals = p[ok]
    m = vals.size
    order = np.argsort(vals)
    thresh = alpha * (np.arange(1, m + 1) / m)
    passed = vals[order] <= thresh
    if passed.any():
        cut = int(np.max(np.flatnonzero(passed)))
        out[np.flatnonzero(ok)[order[: cut + 1]]] = True
    return out


# --------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------

def load_prereg(path: Path) -> dict[str, Any]:
    doc = verify_frozen_config(path)
    p = doc["parameters"]
    if p.get("audit_finding_id") != "N-004":
        raise ConfigError("preregistration is not the N-004 protocol")
    for key in ("generators", "bit_lengths", "seeds_per_generator_and_length",
                "alpha", "familywise_methods", "primary_statistic", "decision_rule"):
        if key not in p:
            raise ConfigError(f"preregistration missing parameter: {key}")
    for name in p["generators"]:
        if name not in GENERATOR_FACTORIES:
            raise ConfigError(f"preregistered generator {name} has no implementation")
    return doc


def run(prereg_path: Path, out_dir: Path) -> int:
    doc = load_prereg(prereg_path)
    p = doc["parameters"]
    prereg_sha = doc["config_sha256"]
    out_dir = Path(out_dir).resolve()
    if out_dir.exists():
        raise N004Error(f"refusing to overwrite existing output directory: {out_dir}")
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = out_dir.parent / f".{out_dir.name}.staging-{os.getpid()}-{uuid.uuid4().hex}"
    staging.mkdir()

    battery_path = Path(rb.__file__).resolve()
    battery_actual = sha256_file(battery_path)
    if battery_actual != BATTERY_SHA256:
        write_json(staging / "battery_hash_mismatch.json", {
            "expected": BATTERY_SHA256, "actual": battery_actual, "path": str(battery_path)})
        raise GateError("shared battery module hash changed; refusing to run")

    tasks = []
    for label, expo in p["bit_lengths"].items():
        shift = int(expo) - 18
        n_seeds = int(p["seeds_per_generator_and_length"][label])
        for gname in p["generators"]:
            for i in range(n_seeds):
                tasks.append((gname, 900000 + i, shift))
    total = len(tasks)
    print(f"  {total} battery evaluations across {len(p['generators'])} generators "
          f"and {len(p['bit_lengths'])} stream lengths, {WORKERS} workers", flush=True)

    t0 = time.perf_counter()
    rows: list[tuple] = []
    errors: list[str] = []
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        for k, res in enumerate(pool.map(_worker, tasks, chunksize=1), start=1):
            gname, seed, shift, pvals, dt, err = res
            rows.append((gname, seed, shift, pvals))
            if err:
                errors.append(f"{gname}/seed{seed}/shift{shift}: {err}")
            if k % 25 == 0 or k == total:
                el = time.perf_counter() - t0
                print(f"    {k}/{total} ({el:7.1f}s, eta {(total-k)/max(k/el,1e-9):7.1f}s)",
                      flush=True)
    wall = time.perf_counter() - t0

    # ---- completeness gate: every preregistered (generator, length) cell must
    # have exactly the preregistered number of successful evaluations. Without
    # this the runner reported success while an entire generator arm had failed,
    # which is fail-open and would have produced a silently partial artifact.
    expected: dict[tuple[str, int], int] = {}
    for label, expo in p["bit_lengths"].items():
        shift = int(expo) - 18
        n_seeds = int(p["seeds_per_generator_and_length"][label])
        for gname in p["generators"]:
            expected[(gname, shift)] = n_seeds
    got: dict[tuple[str, int], int] = {}
    for gname, seed, shift, pvals, *_ in rows:
        if pvals:
            got[(gname, shift)] = got.get((gname, shift), 0) + 1
    incomplete = []
    for key, want in sorted(expected.items()):
        have = got.get(key, 0)
        if have != want:
            incomplete.append(f"{key[0]}@shift{key[1]}: expected {want}, got {have}")
    if incomplete:
        write_json(staging / "incomplete_run.json", {
            "reason": "not every preregistered cell produced the preregistered "
                      "number of successful battery evaluations",
            "incomplete_cells": incomplete,
            "evaluation_errors": errors[:50],
            "n_errors": len(errors),
        })
        raise GateError("incomplete run; refusing to write a manifest: "
                        + "; ".join(incomplete[:6]))

    # ---- persist raw p-values
    # TEST_IDS must be populated HERE as well as in analyze(): a previous version
    # left it empty at run time, so zip([], pvals) silently inserted nothing while
    # the manifest still reported 24960 rows written. The insert count and the
    # table count are now both asserted against each other.
    global TEST_IDS
    TEST_IDS = _test_ids()
    if len(TEST_IDS) != int(p["battery"]["tests"]):
        raise GateError(f"battery exposes {len(TEST_IDS)} tests, preregistration "
                        f"declares {p['battery']['tests']}")
    db_path = staging / "N004_raw.sqlite3"
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    inserted = 0
    try:
        con.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.executemany("INSERT INTO meta VALUES (?,?)", [
            ("prereg_sha256", prereg_sha), ("schema", MANIFEST_SCHEMA),
            ("battery_sha256", battery_actual),
            ("alpha", repr(float(p["alpha"]))),
        ])
        con.execute("CREATE TABLE pvalues (generator TEXT, seed INTEGER, shift INTEGER, "
                    "test_id TEXT, pvalue REAL, PRIMARY KEY (generator, seed, shift, test_id))")
        for gname, seed, shift, pvals, *_ in rows:
            if not pvals:
                continue
            if len(pvals) != len(TEST_IDS):
                raise GateError(f"expected {len(TEST_IDS)} p-values from "
                                f"{gname}/seed{seed}/shift{shift}, got {len(pvals)}")
            con.executemany("INSERT OR REPLACE INTO pvalues VALUES (?,?,?,?,?)", [
                (gname, seed, shift, tid, float(v)) for tid, v in zip(TEST_IDS, pvals)])
            inserted += len(pvals)
        con.commit()
        stored = con.execute("SELECT COUNT(*) FROM pvalues").fetchone()[0]
        if stored != inserted:
            raise GateError(f"pvalues table holds {stored} rows but {inserted} were inserted")
        n_complete = con.execute(
            "SELECT COUNT(*) FROM (SELECT generator, shift, seed FROM pvalues "
            "GROUP BY generator, shift, seed HAVING COUNT(*) = ?)", (len(TEST_IDS),)
        ).fetchone()[0]
        if n_complete != total:
            raise GateError(f"{n_complete} complete seed-vectors stored, expected {total}")
    finally:
        con.close()
    n_written = inserted

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "audit_finding_id": "N-004",
        "question_id": "Q-I004",
        "prereg_sha256": prereg_sha,
        "prereg_path": str(Path(prereg_path).resolve()),
        "battery_module": str(battery_path),
        "battery_sha256": battery_actual,
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "raw_sqlite_sha256": sha256_file(db_path),
        "raw_sqlite_bytes": db_path.stat().st_size,
        "raw_rows_written": n_written,
        "evaluations": total,
        "evaluation_errors": errors,
        "workers": WORKERS,
        "wall_seconds": wall,
        "alpha": float(p["alpha"]),
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
        },
    }
    manifest["manifest_sha256"] = sha256_bytes(json.dumps(
        manifest, allow_nan=False, ensure_ascii=False,
        separators=(",", ":"), sort_keys=True).encode("utf-8"))
    write_json(staging / "N004_manifest.json", manifest)

    shutil.rmtree(out_dir, ignore_errors=True)
    staging.rename(out_dir)
    print(f"\nraw artifact + manifest written to {out_dir}")
    print(f"total wall time {wall:.1f}s; evaluation errors: {len(errors)}")
    for e in errors[:5]:
        print(f"  ERROR {e}")
    return 0


def _test_ids() -> list[str]:
    gen = np.random.default_rng(0)
    b = gen.integers(0, 256, rb.NBYTES, dtype=np.uint32).astype(np.uint8)
    f = gen.random(rb.NF)
    w = gen.integers(0, 2 ** 32, rb.NW, dtype=np.uint32).astype(np.uint32)
    return [tid for tid, _ in rb.run_battery(np.unpackbits(b), b, f, w)]


TEST_IDS: list[str] = []


def analyze(prereg_path: Path, artifact_dir: Path) -> int:
    global TEST_IDS
    doc = load_prereg(prereg_path)
    p = doc["parameters"]
    artifact_dir = Path(artifact_dir).resolve()
    manifest = load_strict_json(artifact_dir / "N004_manifest.json")
    if manifest["prereg_sha256"] != doc["config_sha256"]:
        raise ConfigError("artifact was produced under a different preregistration")
    if manifest["battery_sha256"] != BATTERY_SHA256:
        raise ConfigError("artifact was produced with a different battery module")
    TEST_IDS = _test_ids()
    if len(TEST_IDS) != int(p["battery"]["tests"]):
        raise ConfigError(f"battery exposes {len(TEST_IDS)} tests, "
                          f"preregistration declares {p['battery']['tests']}")
    alpha = float(p["alpha"])

    con = sqlite3.connect(artifact_dir / "N004_raw.sqlite3")
    # key by (generator, shift, seed, test_id): the row order returned by SQL is
    # not the battery's test order, so the matrix must be rebuilt by name.
    collected: dict[tuple[str, int, int], dict[str, float]] = {}
    try:
        for gname, seed, shift, tid, val in con.execute(
                "SELECT generator, seed, shift, test_id, pvalue FROM pvalues"):
            collected.setdefault((str(gname), int(shift), int(seed)), {})[str(tid)] = float(val)
    finally:
        con.close()

    per_seed: dict[tuple[str, int], dict[int, dict[str, float]]] = {}
    for (gname, shift, seed), by_test in collected.items():
        if set(by_test) != set(TEST_IDS):
            raise GateError(
                f"incomplete test set for {gname}/shift{shift}/seed{seed}: "
                f"{sorted(set(TEST_IDS) - set(by_test))}")
        per_seed.setdefault((gname, shift), {})[seed] = by_test

    cells = []
    for (gname, shift), by_seed in sorted(per_seed.items()):
        seeds = sorted(by_seed)
        mat = np.array([[by_seed[s][tid] for tid in TEST_IDS] for s in seeds],
                       dtype=float)  # (n_seeds, n_tests) in TEST_IDS order
        n_seeds, n_tests = mat.shape

        per_test = []
        for j, tid in enumerate(TEST_IDS):
            col = mat[:, j]
            finite = col[np.isfinite(col)]
            ks_d, ks_p = ks_uniform(finite)
            k = int(np.sum(finite < alpha))
            lo, hi = exact_binomial_band(k, finite.size, alpha)
            per_test.append({
                "test_id": tid,
                "n": int(finite.size),
                "n_nonfinite": int(col.size - finite.size),
                "ks_stat": ks_d,
                "ks_pvalue": ks_p,
                "rejections_at_alpha": k,
                "observed_rate": (k / finite.size) if finite.size else None,
                "binomial_band": [lo, hi],
                "rate_in_band": bool(lo <= (k / finite.size if finite.size else 0.0) <= hi),
                "mean_p": float(finite.mean()) if finite.size else None,
            })
        ks_p = np.array([r["ks_pvalue"] if np.isfinite(r["ks_pvalue"]) else 1.0 for r in per_test])
        reject = bh_reject(ks_p, alpha)
        for r, rej in zip(per_test, reject):
            r["bh_reject_ks"] = bool(rej)
            r["status"] = ("miscalibrated" if rej or not r["rate_in_band"]
                           else "calibrated")

        holm_counts = [holm_rejections(mat[i], alpha) for i in range(n_seeds)]
        bonf_counts = [bonferroni_rejections(mat[i], alpha) for i in range(n_seeds)]
        sidak_counts = [sidak_rejections(mat[i], alpha) for i in range(n_seeds)]
        naive_counts = [int(np.sum(mat[i][np.isfinite(mat[i])] < alpha)) for i in range(n_seeds)]

        cells.append({
            "generator": gname,
            "shift": shift,
            "bit_length": f"2^{18 + shift}",
            "role": p["generators"][gname]["role"],
            "n_seeds": int(n_seeds),
            "per_test": per_test,
            "n_miscalibrated": int(sum(1 for r in per_test if r["status"] == "miscalibrated")),
            "miscalibrated_tests": [r["test_id"] for r in per_test if r["status"] == "miscalibrated"],
            "bonferroni_familywise_rate": float(np.mean([c > 0 for c in bonf_counts])),
            "bonferroni_mean_rejections": float(np.mean(bonf_counts)),
            "holm_familywise_rate": float(np.mean([c > 0 for c in holm_counts])),
            "holm_mean_rejections": float(np.mean(holm_counts)),
            "sidak_familywise_rate_independence_assuming": float(np.mean([c > 0 for c in sidak_counts])),
            "uncorrected_familywise_rate": float(np.mean([c > 0 for c in naive_counts])),
            "nominal_familywise_alpha": alpha,
            "dependence_penalty_sidak_over_bonferroni": float(
                np.mean([c > 0 for c in sidak_counts]) /
                max(np.mean([c > 0 for c in bonf_counts]), 1e-12)),
        })

    # ---- positive control gate
    broken = [c for c in cells if c["role"] == "positive_control_must_fail"]
    control_ok = bool(broken) and all(
        (c["bonferroni_familywise_rate"] > 0
         or c["holm_familywise_rate"] > 0
         or c["n_miscalibrated"] > 0) for c in broken)
    battery_verdict = "BATTERY_VALID" if control_ok else "BATTERY_INVALID"

    glab = [c for c in cells if c["generator"] == "G_LAB"]
    glab_status = ("INTERPRETABLE" if control_ok else "NOT_INTERPRETABLE_BATTERY_INVALID")

    summary = {
        "summary_schema": SUMMARY_SCHEMA,
        "audit_finding_id": "N-004",
        "question_id": "Q-I004",
        "prereg_sha256": doc["config_sha256"],
        "manifest_sha256": manifest["manifest_sha256"],
        "battery_verdict": battery_verdict,
        "positive_control_gate": {
            "requirement": p["positive_control"]["requirement"],
            "passed": control_ok,
            "per_length": [{"bit_length": c["bit_length"],
                            "bonferroni_familywise_rate": c["bonferroni_familywise_rate"],
                            "holm_familywise_rate": c["holm_familywise_rate"],
                            "n_miscalibrated": c["n_miscalibrated"]}
                           for c in broken],
        },
        "G_LAB_status": glab_status,
        "cells": cells,
        "resolution": p["resolution"],
        "claim_guards": p["claim_guards"],
        "known_limitations": p["known_limitations"],
        "certification_claim": False,
        "historical_certificate_reinstated": False,
    }
    write_json(artifact_dir / "N004_summary.json", summary)

    print(f"battery verdict: {battery_verdict}  (G_LAB status: {glab_status})")
    print()
    hdr = (f"{'generator':<18}{'bits':<7}{'role':<28}{'n':>4}{'miscal':>8}"
           f"{'bonfFW':>8}{'holmFW':>8}{'sidakFW':>9}{'uncorrFW':>10}")
    print(hdr)
    print("-" * len(hdr))
    for c in cells:
        print(f"{c['generator']:<18}{c['bit_length']:<7}{c['role']:<28}"
              f"{c['n_seeds']:>4}{c['n_miscalibrated']:>8}"
              f"{c['bonferroni_familywise_rate']:>8.3f}"
              f"{c['holm_familywise_rate']:>8.3f}"
              f"{c['sidak_familywise_rate_independence_assuming']:>9.3f}"
              f"{c['uncorrected_familywise_rate']:>10.3f}")
    print()
    for c in cells:
        if c["miscalibrated_tests"]:
            print(f"  {c['generator']} @ {c['bit_length']}: "
                  f"{', '.join(c['miscalibrated_tests'])}")
    return 0


def validate(prereg_path: Path, artifact_dir: Path) -> int:
    doc = load_prereg(prereg_path)
    artifact_dir = Path(artifact_dir).resolve()
    manifest = load_strict_json(artifact_dir / "N004_manifest.json")
    problems = []
    if manifest["prereg_sha256"] != doc["config_sha256"]:
        problems.append("preregistration hash mismatch")
    if manifest["battery_sha256"] != BATTERY_SHA256:
        problems.append("battery module hash mismatch")
    if sha256_file(Path(manifest["battery_module"])) != BATTERY_SHA256:
        problems.append("battery module has changed on disk since the run")
    db = artifact_dir / "N004_raw.sqlite3"
    if sha256_file(db) != manifest["raw_sqlite_sha256"]:
        problems.append("raw sqlite hash mismatch")
    payload = dict(manifest)
    recorded = payload.pop("manifest_sha256", None)
    actual = sha256_bytes(json.dumps(payload, allow_nan=False, ensure_ascii=False,
                                     separators=(",", ":"), sort_keys=True).encode("utf-8"))
    if recorded != actual:
        problems.append("manifest self-hash mismatch")
    sp = artifact_dir / "N004_summary.json"
    verdict = load_strict_json(sp)["battery_verdict"] if sp.exists() else None
    for p_ in problems:
        print(f"FAIL {p_}")
    if not problems:
        print(f"PASS artifact validated; battery_verdict={verdict}")
    return 1 if problems else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--prereg", type=Path, default=PREREG)
    r.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("analyze")
    a.add_argument("--prereg", type=Path, default=PREREG)
    a.add_argument("--artifact", type=Path, required=True)
    v = sub.add_parser("validate")
    v.add_argument("--prereg", type=Path, default=PREREG)
    v.add_argument("--artifact", type=Path, required=True)
    args = ap.parse_args()
    try:
        if args.cmd == "run":
            return run(args.prereg, args.out)
        if args.cmd == "analyze":
            return analyze(args.prereg, args.artifact)
        return validate(args.prereg, args.artifact)
    except N004Error as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
