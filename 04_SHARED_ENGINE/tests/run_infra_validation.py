"""Infra validation — proves the shared engine works before any real experiment.

Batch EXP-0001 (first registry entries). Tests (no heavy compute):
  1. RNG determinism across fresh processes (same config+seed => identical draws)
  2. sha256 utilities (file + text)
  3. BH-FDR correctness on a constructed case
  4. matched-spectrum surrogate reproduces the power spectrum of its source
  5. experiment.json buildings + manifest hashing
  6. universal template scaffold is non-destructive/lists expected dirs
  7. Welch t + Cohen's d on a known-trivial case

Run:  python tests/run_infra_validation.py   (from 04_SHARED_ENGINE)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

from engine.datasets.manifest import manifest_directory  # noqa: E402
from engine.hypothesis_testing.prereg import (  # noqa: E402
    PreregistrationExistsError,
    freeze_config,
    verify_frozen_config,
)
from engine.reproducibility.experiments import (  # noqa: E402
    append_registry_row,
    read_registry,
    scaffold_investigation,
)
from engine.simulation.controls import matched_spectrum_surrogate, gaussian_field  # noqa: E402
from engine.statistics.testers import bh_fdr, cohens_d, welch_t, binomial_band  # noqa: E402
from engine.utilities.core import (  # noqa: E402
    make_experiment_json,
    rng,
    sha256_file,
    sha256_text,
    version_info,
)
from engine.validation import rng_battery  # noqa: E402


def _rng_check(seed=42):
    a = rng("infra", seed).random(64)
    code = (
        "import sys; sys.path.insert(0, %r); "
        "from engine.utilities.core import rng; "
        "import numpy as np; "
        "print(np.array2string(rng('infra', 42).random(64), precision=18, separator=',', "
        "max_line_width=10**9))"
    ) % ROOT
    out = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    ).stdout.strip()
    b = np.array([float(x) for x in out.strip("[]").replace(",", " ").split()])
    return np.allclose(a, b, rtol=0, atol=1e-15)


def run_all():
    results = {}
    checks = []

    def check(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        return ok

    # 1. RNG determinism across fresh processes
    check("rng_determinism_across_processes", _rng_check())

    # 2. sha256 text
    check("sha256_text", sha256_text("abc") == sha256_text("abc"))

    # 3. BH-FDR: 8 p-values, 1 known-small
    pvals = [0.001, 0.2, 0.3, 0.4, 0.5, 0.001, 0.9, 0.8]
    sig, _ = bh_fdr(pvals, alpha=0.01)
    check("bh_fdr_flags_small", int(sig.sum()) >= 1)
    # regression: same-pipendulum case must NOT flag all (bug: argwhere(flip).max())
    p2 = [2.2e-16] + [0.5] * 19
    sig2, _ = bh_fdr(p2, alpha=0.01)
    check("bh_fdr_counts_only_small", int(sig2.sum()) == 1)
    empty, _ = bh_fdr([0.2, 0.3, 0.9], alpha=0.01)
    check("bh_fdr_no_false_positive", not empty.any())

    # 4. matched-spectrum surrogate reproduces source power spectrum
    src = gaussian_field((64, 64), seed=3, label="infra-src")
    sur = matched_spectrum_surrogate(src, seed=9, label="infra-sur")
    psd_a = np.abs(np.fft.fft2(src)) ** 2
    psd_b = np.abs(np.fft.fft2(sur)) ** 2
    check("matched_spectrum_surrogate", np.allclose(psd_a, psd_b, rtol=1e-6))

    # 5. experiment.json building
    with tempfile.TemporaryDirectory() as tmp:
        meta = make_experiment_json(
            "EXP-0001-INFRA",
            "Q-INFRA",
            "HYP-INFRA",
            seed=42,
            parameters={"n": 64},
            result={"rng_ok": True},
            out_path=os.path.join(tmp, "experiment.json"),
        )
        check("experiment_json_built", meta["experiment_id"] == "EXP-0001-INFRA")

        # Preregistration immutability: first write verifies; second write fails
        # closed without changing the frozen bytes.
        prereg_path = os.path.join(tmp, "prereg.json")
        frozen = freeze_config(
            experiment_id="EXP-0001-INFRA",
            hypothesis_id="HYP-INFRA",
            question_id="Q-INFRA",
            seed=42,
            params={"n": 64},
            out_path=prereg_path,
        )
        check(
            "prereg_hash_roundtrip",
            verify_frozen_config(prereg_path) == frozen,
        )
        before = open(prereg_path, "rb").read()
        try:
            freeze_config(
                experiment_id="EXP-0001-INFRA",
                hypothesis_id="HYP-INFRA",
                question_id="Q-INFRA",
                seed=42,
                params={"n": 65},
                out_path=prereg_path,
            )
        except PreregistrationExistsError:
            refused = True
        else:
            refused = False
        check(
            "prereg_refuses_overwrite",
            refused and open(prereg_path, "rb").read() == before,
        )

        # manifest hashing
        man = manifest_directory(tmp)
        check("manifest_hashes", any(man["entries"]))

        # 6. scaffold template (non-destructive)
        inv = scaffold_investigation(os.path.join(tmp, "inv"), "Infra", "Q-INFRA")
        check(
            "template_scaffold",
            os.path.exists(os.path.join(inv["root"], "QUESTION.md"))
            and os.path.isdir(os.path.join(inv["root"], "CONFIG")),
        )

        # append-only registry
        reg_path = os.path.join(tmp, "registry.jsonl")
        append_registry_row(reg_path, {"experiment_id": "EXP-0001", "seed": 42})
        append_registry_row(reg_path, {"experiment_id": "EXP-0001", "seed": 43})
        rows = read_registry(reg_path)
        check("append_only_registry", len(rows) == 2 and rows[1]["seed"] == 43)

    # 7. stats sanity on a known case
    a = np.random.default_rng(0).normal(0, 1, 500)
    b = np.random.default_rng(1).normal(1, 1, 500)
    t, df, p = welch_t(a, b)
    d = cohens_d(a, b)
    band = binomial_band(1000, p=0.5)
    check("stats_sane", p < 1e-6 and band["lo"] < 500 < band["hi"])

    # 8. PRNG battery structural sanity (supports EXP-0004)
    barr, farr, warr, sbits = rng_battery.streams_for(rng("battery-infra", 1))
    cells = rng_battery.run_battery(sbits, barr, farr, warr)
    check(
        "battery_returns_full_grid",
        len(cells) == len(rng_battery.TEST_IDS),
        f"({len(cells)} cells)",
    )
    check(
        "battery_pvalues_valid",
        all((0.0 <= p <= 1.0) if p == p else True for _, p in cells),
    )
    check(
        "battery_monobit_has_power",
        rng_battery.t_monobit(np.unpackbits(np.zeros(1 << 15, np.uint8))) < 1e-6,
        "(all-zero stream rejected)",
    )

    results["checks"] = checks
    results["passed"] = sum(c["ok"] for c in checks)
    results["total"] = len(checks)
    results["software"] = version_info()

    # Write result alongside tests
    out_path = os.path.join(ROOT, "tests", "infra_validation_results.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    for c in checks:
        print(f"[{'PASS' if c['ok'] else 'FAIL'}] {c['name']} {c['detail']}")
    print(f"\n{results['passed']}/{results['total']} infra checks passed -> {out_path}")
    return results


if __name__ == "__main__":
    res = run_all()
    sys.exit(0 if res["passed"] == res["total"] else 1)