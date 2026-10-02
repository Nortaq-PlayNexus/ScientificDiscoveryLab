"""EXP-0004 - Lab RNG statistical certification (Q-I004 / HYP-003).

Frozen protocol in 03_INVESTIGATIONS/OTHER/rng_certification/EXPERIMENT_PLAN.md
and CONFIG/prereg_EXP-0004.json (created by this script BEFORE any battery rows
are computed).

Run from the investigation folder:
    python CODE/run_rng_cert.py
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

import numpy as np

ENGINE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "04_SHARED_ENGINE")
)
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)

from engine.hypothesis_testing.prereg import freeze_config  # noqa: E402
from engine.reproducibility.experiments import append_registry_row  # noqa: E402
from engine.statistics.testers import bh_fdr, binomial_band  # noqa: E402
from engine.utilities.core import SEED_LADDER, make_experiment_json, rng  # noqa: E402
from engine.validation import rng_battery  # noqa: E402
from engine.validation.rng_battery import run_battery, streams_for  # noqa: E402

from scipy import stats  # noqa: E402

INV = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPERIMENT_ID = "EXP-0004"
QUESTION_ID = "Q-I004"
HYPOTHESIS_ID = "HYP-003"
SEED = 42
ALPHA = 0.01
BAND_COVERAGE = 0.95
LAB_LABEL = "Q-I004:cert"
ALT_LABEL = "Q-I004:alt"
GEN_NAMES = ("G_LAB", "G_PCG", "G_MT")


class _Adapter:
    """Uniform call interface over numpy Generator / RandomState."""

    def __init__(self, gen, use_randint=False):
        self._gen = gen
        self._use_randint = use_randint

    def integers(self, low, high, size, dtype=np.uint32):
        if self._use_randint:
            if high == 2 ** 32:
                lo = self._gen.randint(0, 65536, size).astype(np.uint32)
                hi = self._gen.randint(0, 65536, size).astype(np.uint32)
                raw = (hi << np.uint32(16)) | lo
            else:
                raw = self._gen.randint(low, high, size)
        else:
            raw = self._gen.integers(low, high, size, dtype=np.uint32)
        return np.asarray(raw).astype(dtype)

    def random(self, size):
        return np.asarray(self._gen.random(size))


def make_generator(name, seed):
    if name == "G_LAB":
        return _Adapter(rng(LAB_LABEL, seed))
    if name == "G_PCG":
        return _Adapter(np.random.default_rng(seed))
    if name == "G_MT":
        return _Adapter(np.random.RandomState(seed), use_randint=True)
    raise ValueError(name)


def sha_bytes(arr):
    return hashlib.sha256(arr.tobytes()).hexdigest()


def child_stream_hash(seed):
    """C1: G_LAB byte-stream sha256 computed in a fresh subprocess."""
    code = (
        "import sys, hashlib; sys.path.insert(0, sys.argv[1]);"
        "from engine.utilities.core import rng;"
        "from engine.validation.rng_battery import draw_arrays;"
        "b, _, _ = draw_arrays(rng(%r, int(sys.argv[2])));"
        "print(hashlib.sha256(b.tobytes()).hexdigest())" % LAB_LABEL
    )
    res = subprocess.run(
        [sys.executable, "-c", code, ENGINE, str(seed)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return res.stdout.strip()


def aggregate(generator_ps):
    """Decision stats for one generator over all seeds (frozen rule).

    generator_ps: list of list[(test_id, p)] (one list per seed).
    """
    merged = [p for per_seed in generator_ps for _, p in per_seed]
    n = len(merged)
    ks_p = float(stats.kstest(merged, "uniform").pvalue)
    small_p = [p for p in merged if p <= ALPHA]
    band = binomial_band(n, p=ALPHA, alpha=1.0 - BAND_COVERAGE)
    sig, _ = bh_fdr(merged, alpha=ALPHA)
    fdr_count = int(sig.sum())
    return {
        "n_cells": n,
        "ks_p": ks_p,
        "ks_pass": bool(ks_p > ALPHA),
        "small_p_count": len(small_p),
        "small_p_min": min(small_p) if small_p else None,
        "binomial_band": band,
        "small_p_in_band": bool(band["lo"] <= len(small_p) <= band["hi"]),
        "fdr_flag_count": fdr_count,
        "fdr_in_band": bool(band["lo"] <= fdr_count <= band["hi"]),
        "pass_rule": bool(
            ks_p > ALPHA
            and band["lo"] <= len(small_p) <= band["hi"]
            and band["lo"] <= fdr_count <= band["hi"]
        ),
    }


def main():
    for sub in ("CONFIG", "RESULTS", "FIGURES", "REPORT", "REPLICATION"):
        os.makedirs(os.path.join(INV, sub), exist_ok=True)

    # ---------------- frozen preregistration (before any computation) -------
    freeze_config(
        experiment_id=EXPERIMENT_ID,
        hypothesis_id=HYPOTHESIS_ID,
        question_id=QUESTION_ID,
        seed=SEED,
        alpha=ALPHA,
        controls=(
            "C1 determinism across processes",
            "C2 label independence",
            "C3 control-generator calibration (G_PCG, G_MT)",
            "C4 KS uniformity",
            "C5 expected rejection rate (binomial band)",
            "C6 BH-FDR supervision",
            "C7 independent implementation",
            "C8 length stability (4x stream)",
        ),
        analyses=(
            "one-sample KS of p-multiset vs Uniform(0,1)",
            "exact central binomial band on small-p count",
            "BH-FDR flag count vs same band",
        ),
        params={
            "generators": list(GEN_NAMES),
            "lab_label": LAB_LABEL,
            "seeds": list(SEED_LADDER),
            "nbytes": rng_battery.NBYTES,
            "nfloats": rng_battery.NF,
            "nwords": rng_battery.NW,
            "nbits": rng_battery.NBITS,
            "test_ids": list(rng_battery.TEST_IDS),
        },
        out_path=os.path.join(INV, "CONFIG", "prereg_EXP-0004.json"),
        note="Frozen before execution. Certification = calibration claim (H0), "
        "not discovery.",
    )

    # ---------------- battery grid: generator x seed ------------------------
    by_gen = {}
    hashes = {}
    for name in GEN_NAMES:
        per_seed = []
        seed_stream_hash = {}
        for s in SEED_LADDER:
            gen = make_generator(name, s)
            bytes_arr, floats_arr, words_arr, bits = streams_for(gen)
            seed_stream_hash[s] = sha_bytes(bytes_arr)
            pvals = run_battery(bits, bytes_arr, floats_arr, words_arr)
            per_seed.append(
                {
                    "seed": s,
                    "stream_sha256": seed_stream_hash[s],
                    "pvals": dict(pvals),
                }
            )
        hashes[name] = seed_stream_hash
        by_gen[name] = per_seed

    # ---------------- controls -------------------------------------------------
    c1_hash = child_stream_hash(SEED)
    c1_ok = c1_hash == hashes["G_LAB"][SEED]

    alt_hash = sha_bytes(streams_for(_Adapter(rng(ALT_LABEL, SEED)))[0])
    c2_ok = alt_hash != hashes["G_LAB"][SEED]

    control_detail = {
        "C1_determinism": {
            "fresh_process_sha256": c1_hash,
            "parent_process_sha256": hashes["G_LAB"][SEED],
            "pass": c1_ok,
        },
        "C2_label_independence": {
            "alt_label_sha256": alt_hash,
            "primary_label_sha256": hashes["G_LAB"][SEED],
            "pass": c2_ok,
        },
    }

    # ---------------- aggregation & decision -----------------------------------
    stats_by_gen = {}
    for name in GEN_NAMES:
        stats_by_gen[name] = aggregate(
            [[(tid, p) for tid, p in ps["pvals"].items()] for ps in by_gen[name]]
        )
    medians = {}
    for name in GEN_NAMES:
        by_test = {}
        for ps in by_gen[name]:
            for tid, p in ps["pvals"].items():
                by_test.setdefault(tid, []).append(p)
        medians[name] = {tid: float(np.median(v)) for tid, v in by_test.items()}

    lab = stats_by_gen["G_LAB"]
    any_control_ok = any(stats_by_gen[c]["pass_rule"] for c in ("G_PCG", "G_MT"))
    if not c1_ok or not c2_ok:
        decision = "INCONCLUSIVE"
        conclusion = (
            "Determinism/label controls failed (C1/C2) - the certificate is void; "
            "rerun before any judgement."
        )
    elif lab["pass_rule"] and any_control_ok:
        decision = "CERTIFIED"
        conclusion = (
            "The lab RNG (sha256-derived PCG64) passes the preregistered lightweight "
            "battery at lab stream lengths, over 6 seeds, judged by KS uniformity, "
            "exact binomial rejection band, and BH-FDR supervision; and the battery "
            "is validated on known-good controls. Certificate: CONTROLLED."
        )
    elif (not lab["pass_rule"]) and any_control_ok:
        decision = "ABNORMAL_LAB_SPECIFIC"
        conclusion = (
            "The lab RNG fails the battery while a known-good control passes - "
            "genuine RNG-level red flag; run the kill-the-hypothesis battery; "
            "do NOT use this RNG until resolved."
        )
    else:
        decision = "INCONCLUSIVE"
        conclusion = (
            "Lab RNG and/or controls fail together; battery over-rejection suspected "
            "(S2). Fix the battery, not the RNG. Certificate NOT issued."
        )

    # ---------------- C8 length stability (4x, seed 42, G_LAB) -----------------
    long_gen = make_generator("G_LAB", SEED)
    long_bytes = long_gen.integers(0, 256, rng_battery.NBYTES * 4, dtype=np.uint32)
    long_floats = long_gen.random(rng_battery.NF * 4)
    long_words = long_gen.integers(0, 2 ** 32, rng_battery.NW * 4, dtype=np.uint32)
    long_bytes_u8 = np.asarray(long_bytes).astype(np.uint8)
    long_bits = np.unpackbits(long_bytes_u8)
    long_pvals = [p for _, p in run_battery(long_bits, long_bytes_u8, long_floats,
                                            long_words)]
    long_agg = aggregate([[(f"L{n}", p) for n, p in enumerate(long_pvals)]])
    c8 = {"long_stream_agg": long_agg, "long_stream_pass": long_agg["pass_rule"]}

    result = {
        "experiment": EXPERIMENT_ID,
        "question": QUESTION_ID,
        "hypothesis": HYPOTHESIS_ID,
        "alpha": ALPHA,
        "band_coverage": BAND_COVERAGE,
        "generators": by_gen,
        "hashes": hashes,
        "controls": control_detail,
        "length_stability_c8": c8,
        "aggregates": stats_by_gen,
        "per_test_median": medians,
        "decision": decision,
        "conclusion_lab": conclusion,
    }
    res_path = os.path.join(INV, "RESULTS", "EXP-0004_results.json")
    with open(res_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)

    make_experiment_json(
        experiment_id=EXPERIMENT_ID,
        question=QUESTION_ID,
        hypothesis=HYPOTHESIS_ID,
        seed=SEED,
        parameters={
            "generators": list(GEN_NAMES),
            "lab_label": LAB_LABEL,
            "seeds": list(SEED_LADDER),
            "nbytes": rng_battery.NBYTES,
            "nbits": rng_battery.NBITS,
        },
        result={
            "decision": decision,
            "conclusion": conclusion,
            "aggregates": stats_by_gen,
            "controls": control_detail,
        },
        out_path=os.path.join(INV, "CONFIG", f"{EXPERIMENT_ID}_experiment.json"),
    )
    append_registry_row(
        os.path.join(INV, "CONFIG", "registry.jsonl"),
        {
            "experiment_id": EXPERIMENT_ID,
            "hypothesis": HYPOTHESIS_ID,
            "question": QUESTION_ID,
            "seed": SEED,
            "decision": decision,
            "result_path": res_path,
        },
    )

    print(f"{EXPERIMENT_ID} decision: {decision}")
    for name in GEN_NAMES:
        a = stats_by_gen[name]
        print(
            f"  {name:5s} n={a['n_cells']:3d} ks_p={a['ks_p']:.4f} "
            f"small_p={a['small_p_count']}/{a['binomial_band']['lo']}-"
            f"{a['binomial_band']['hi']} fdr={a['fdr_flag_count']} "
            f"pass={a['pass_rule']}"
        )
    print(f"  C1 determinism pass={c1_ok}")
    print(f"  C2 label independence pass={c2_ok}")
    return result


if __name__ == "__main__":
    main()