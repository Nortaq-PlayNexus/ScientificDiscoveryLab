#!/usr/bin/env python3
"""Append the pre-execution family-wise-method substitution to the N-004 chain.

Written BEFORE any production data exists. The preregistration named
``holm_step_down`` and ``max_t_permutation``. A preflight on 12 seeds showed the
max-T permutation control is mathematically incapable of rejecting, so it is
replaced by the Bonferroni family-wise count, which is valid under arbitrary
dependence between tests. Idempotent.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

INV_ROOT = Path(__file__).resolve().parents[1]
LAB_ROOT = INV_ROOT.parents[3]
SHARED_ENGINE = LAB_ROOT / "04_SHARED_ENGINE"
if str(SHARED_ENGINE) not in sys.path:
    sys.path.insert(0, str(SHARED_ENGINE))

from engine.hypothesis_testing.prereg import log_change, verify_change_log  # noqa: E402

CHANGELOG = INV_ROOT / "CONFIG" / "production_changes.jsonl"

ENTRIES = [
    (
        "Family-wise inference: the max-T permutation control is replaced by the "
        "Bonferroni count, and Sidak plus an uncorrected count are added as "
        "reported diagnostics",
        "The preregistration named 'max_t_permutation' as a dependence-respecting "
        "control. A preflight on 12 seeds per generator showed this control is "
        "mathematically incapable of rejecting: the maximum of a set of p-values "
        "is permutation-invariant, so permuting the observed p-values to build a "
        "null distribution for the maximum yields a null whose every draw equals "
        "the observed maximum. The control reported a family-wise rate of 0.000 "
        "for the deliberately broken generator WEAK_LCG_BROKEN, which the Holm "
        "count rejected on 12 of 12 seeds and whose T13_words test rejects on "
        "100% of seeds. Had this shipped, the run would have reported that a "
        "blatantly broken generator shows no family-wise evidence against it, "
        "which would have inverted the audit's central finding. The substitute is "
        "the Bonferroni count, which is valid under ARBITRARY dependence and "
        "therefore needs no independence assumption about tests that share one "
        "input stream; this is strictly more appropriate than either Holm or "
        "Sidak for the dependence the audit was worried about. Sidak (which does "
        "assume independence) and the uncorrected per-seed rejection rate are "
        "reported alongside so the size of the dependence penalty is visible "
        "rather than hidden. The primary per-test statistic, the alpha of 0.01, "
        "the seed counts, the generators, the bit lengths, the positive-control "
        "gate, and the claim guards are all UNCHANGED.",
    ),
    (
        "Implementation fixes after a discarded first attempt: RandomState "
        "adapter for the MT19937 arm, and a fail-closed completeness gate",
        "The first execution attempt completed in 330 s but 260 of 1040 battery "
        "evaluations raised, all of them the MT19937 arm, and the runner still "
        "exited 0. Two defects: (1) numpy.random.RandomState exposes randint and "
        "random_sample, not the modern integers/random that the shared battery "
        "calls, so every MT19937 evaluation raised AttributeError; (2) even after "
        "adding that adapter, RandomState.randint is int32-bounded and raises "
        "'high is out of bounds for int32' on the battery's 2**32 word draw, so "
        "32-bit words are now assembled from two 16-bit draws and verified uniform "
        "(top-byte chi-square 255.9 on df 255). Separately the runner was "
        "FAIL-OPEN: it reported success and wrote a manifest despite a wholly "
        "missing generator arm. It now refuses to write a manifest unless every "
        "preregistered (generator, bit length) cell produced exactly the "
        "preregistered number of successful evaluations, writing an "
        "incomplete_run.json diagnostic instead. The failed attempt is preserved "
        "as RESULTS/N004_PRODUCTION_20260926_INCOMPLETE_MT19937_ARM. No "
        "preregistered scientific content changed.",
    ),
    (
        "Third discarded attempt: raw p-value rows were never written because "
        "TEST_IDS was only populated in analyze(); run now populates it and "
        "asserts the stored row count",
        "The second attempt reported 1040/1040 successful evaluations, zero "
        "errors, and a manifest claiming raw_rows_written = 24960, but the "
        "SQLite pvalues table contained 0 rows. Cause: TEST_IDS is a module-level "
        "list that only analyze() populated, so at run time zip([], pvals) "
        "inserted nothing while the counter incremented regardless. This is the "
        "second fail-open defect in this runner and the same class as the first "
        "(a manifest asserting data that was not stored). The run path now "
        "populates TEST_IDS before writing, refuses any seed-vector whose length "
        "differs from the declared test count, and after commit asserts that the "
        "pvalues table row count equals the number of values inserted AND that "
        "the number of complete seed-vectors equals the number of evaluations. "
        "The failed artifact is preserved as "
        "RESULTS/N004_PRODUCTION_20260926_V2_NO_RAW_ROWS. No scientific content "
        "changed.",
    ),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--changelog", type=Path, default=CHANGELOG)
    args = parser.parse_args()
    seen = {e["change"] for e in verify_change_log(args.changelog)}
    out = []
    for what, why in ENTRIES:
        if what in seen:
            out.append({"entry_hash": "already-present", "change": what[:70] + "..."})
            continue
        entry = log_change(experiment_id="N-004-RNG-CALIBRATION-PRODUCTION",
                           what_changed=what, reason=why,
                           changelog_path=args.changelog)
        out.append({"entry_hash": entry["entry_hash"], "change": what[:70] + "..."})
    print(json.dumps({"changelog": str(Path(args.changelog).resolve()),
                      "entries": out}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
