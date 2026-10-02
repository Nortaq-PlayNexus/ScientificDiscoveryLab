#!/usr/bin/env python3
"""Audit every caller of the shared battery's ``_erfc_p`` helper.

``_erfc_p(z) == erfc(|z| / sqrt(2))`` is the two-sided normal tail
``2(1 - Phi(|z|))``.  It is therefore correct **only** when the argument is a
standardised z-score.  Applied to a quantity a specification already defines in
``erfc`` units it silently inflates the p-value.

Whether a given caller is wrong is not a matter of convention: calibration is an
empirical property.  So this module does two independent things.

1. Classifies each caller's argument as ``z_score`` or ``erfc_unit`` from the
   formula itself, and records the reference the classification is based on.
2. Measures the empirical uniformity of the resulting p-values on fresh
   calibrated streams.  A caller classified ``z_score`` that produces uniform
   p-values is confirmed; a caller classified ``z_score`` that does not is a
   defect the classification missed.

Nothing here modifies the shared battery, and nothing certifies a generator.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
from scipy import stats

AREA = Path(__file__).resolve().parents[1]
LAB_ROOT = Path(__file__).resolve().parents[5]
ENGINE_ROOT = LAB_ROOT / "04_SHARED_ENGINE"
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))
sys.path.insert(0, str(AREA / "CODE"))

from engine.utilities.core import rng as lab_rng  # noqa: E402
from engine.validation import rng_battery as rb  # noqa: E402
import runs_sp800_22 as ref  # noqa: E402

REPORT_SCHEMA = "erfc-caller-audit-v1"


class AuditError(RuntimeError):
    """Fail-closed audit failure."""

# How each caller's argument is built, and the authority for that reading.
# `argument_kind` is the only thing classification depends on; `expected` is the
# closed form a conforming implementation must produce, used by the tests.
CALLERS: dict[str, dict[str, Any]] = {
    "T01_monobit": {
        "caller": "t_monobit",
        "argument_kind": "z_score",
        "argument": "s / sqrt(n) where s = 2*ones - n, so s/sqrt(n) ~ N(0,1)",
        "authority": (
            "the monobit statistic S = sum(2*eps_i - 1) has variance n under H0, "
            "so S/sqrt(n) is a standardised z-score and the two-sided normal "
            "tail is the correct p-value"
        ),
        "nist_section": "SP 800-22 Rev 1a section 2.1",
    },
    "T03_runs": {
        "caller": "t_runs",
        "argument_kind": "erfc_unit",
        "argument": "abs(V - 2 n pi (1-pi)) / (2 sqrt(2 n) pi (1-pi))",
        "authority": (
            "section 2.3 step 3 passes this quantity directly to erfc; it is "
            "already in erfc units, so no further sqrt(2) may be applied"
        ),
        "nist_section": "SP 800-22 Rev 1a section 2.3",
    },
    "T06_dft": {
        "caller": "t_dft",
        "argument_kind": "z_score",
        "argument": "d = (n1 - 0.95 n/2) / sqrt(n * 0.95 * 0.05 / 4)",
        "authority": (
            "section 2.9.3 step 6 defines d as a standardised deviation of the "
            "observed count from its expectation, and its p-value as the "
            "two-sided normal tail of d"
        ),
        "nist_section": "SP 800-22 Rev 1a section 2.9.3",
    },
    "T07_nontemplate": {
        "caller": "t_nontemplate",
        "argument_kind": "z_score",
        "argument": "(matches - nwin * 2^-m) / sqrt(nwin * 2^-m (1 - 2^-m))",
        "authority": (
            "a normal approximation to the window-match count, which is a "
            "documented deviation from section 2.7's chi-square form; the "
            "sqrt(2) conversion is correct for a z-score, and the "
            "approximation itself is sound here because the expected match "
            "count is about 57, far into the normal regime"
        ),
        "nist_section": "SP 800-22 Rev 1a section 2.7 (documented deviation)",
    },
    "T15_ac1..T15_ac8": {
        "caller": "t_autocorr",
        "argument_kind": "z_score",
        "keys": [f"T15_ac{lag}" for lag in range(1, 9)],
        "argument": "c / sqrt(n - lag) where c = sum x_i x_{i+lag}, x = 2*bit-1",
        "authority": (
            "a laboratory-specific classic autocorrelation test, not an SP "
            "800-22 test; under independence c/sqrt(n-lag) is standardised"
        ),
        "nist_section": "laboratory-specific (no SP 800-22 section)",
    },
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ks_uniform(p: np.ndarray) -> dict[str, Any]:
    finite = np.asarray(p, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size < 8:
        return {"n": int(finite.size), "ks_pvalue": None, "uniform_rejected": None}
    result = stats.kstest(finite, "uniform")
    return {
        "n": int(finite.size),
        "ks_stat": float(result.statistic),
        "ks_pvalue": float(result.pvalue),
        "uniform_rejected": bool(result.pvalue <= 0.01),
        "mean_p": float(finite.mean()),
        "rejections_at_alpha": int((finite < 0.01).sum()),
    }


def fresh_bits(label: str, seed: int, shift: int) -> np.ndarray:
    gen = lab_rng(label, seed)
    return np.unpackbits(gen.integers(0, 256, rb.NBYTES << shift, dtype=np.uint32).astype(np.uint8))


def collect(seed: int, shift: int, label: str) -> dict[str, float]:
    bits = fresh_bits(label, seed, shift)
    out: dict[str, float] = {
        "T01_monobit": float(rb.t_monobit(bits)),
        "T03_runs": float(rb.t_runs(bits)),
        "T06_dft": float(rb.t_dft(bits)),
        "T07_nontemplate": float(rb.t_nontemplate(bits)),
    }
    for lag, p in enumerate(rb.t_autocorr(bits), start=1):
        out[f"T15_ac{lag}"] = float(p)
    out["T03_runs_corrected"] = float(ref.runs_test_sp800_22(bits))
    out["T03_applicable"] = float(
        ref.runs_test_sp800_22_with_applicability(bits)["applicable"]
    )
    return out


def analyze(seeds: int, shift: int, label: str) -> dict[str, Any]:
    rows = [collect(s, shift, f"{label}-{shift}") for s in range(1, seeds + 1)]
    names = list(rows[0])
    measured = {
        name: ks_uniform(np.array([r[name] for r in rows]))
        for name in names
    }

    cells = []
    for test_id, meta in CALLERS.items():
        keys = meta.get("keys") or [k for k in names if k == test_id or k.startswith(test_id)]
        missing = [k for k in keys if k not in names]
        if missing:
            raise AuditError(f"caller {test_id} declares keys that were never collected: {missing}")
        pooled = np.array([r[k] for k in keys for r in rows])
        cell = {
            "test_id": test_id,
            "keys_pooled": keys,
            "argument_kind": meta["argument_kind"],
            "conforming_by_construction": meta["argument_kind"] == "z_score",
            "argument": meta["argument"],
            "authority": meta["authority"],
            "reference": meta["nist_section"],
            "measured": ks_uniform(pooled),
        }
        # Fail closed on an unmeasurable cell. An absent measurement must never
        # read as a pass, which is the fail-open defect this laboratory has now
        # hit twice in production runners.
        measurable = cell["measured"]["ks_pvalue"] is not None
        cell["measurable"] = measurable
        if not measurable:
            cell["verdict"] = "UNRESOLVED_NO_MEASUREMENT"
            cell["corrected_measured"] = None
            cell["empirical_detection"] = "UNRESOLVED_NO_MEASUREMENT"
        elif test_id == "T03_runs":
            cell["corrected_measured"] = measured["T03_runs_corrected"]
            cell["corrected_measurable"] = measured["T03_runs_corrected"]["ks_pvalue"] is not None
            cell["sp800_22_applicable_seeds"] = int(sum(r["T03_applicable"] for r in rows))
            cell["sp800_22_applicability_fraction"] = cell["sp800_22_applicable_seeds"] / len(rows)
            # The extra sqrt(2) is a deterministic property of the code, provable as
            # an exact algebraic identity, so the classification is a PROOF and not a
            # statistical inference. What the empirical test supplies is the power
            # to DETECT that defect at this length, and those are reported
            # separately on purpose: failing to detect it at 2^22 is a resolution
            # failure, never evidence of its absence.
            cell["verdict"] = "DEFECTIVE_BY_ALGEBRAIC_IDENTITY"
            cell["empirical_detection"] = (
                "DETECTED_AT_THIS_LENGTH"
                if cell["measured"]["uniform_rejected"]
                else "NOT_DETECTED_AT_THIS_RESOLUTION"
            )
            cell["detection_caveat"] = (
                "A non-detection here is a limit of the 200-seed KS test, not "
                "evidence of correctness. The identity is asserted to rel=1e-12 by "
                "the test suite, so the defect holds at every stream length."
            )
        else:
            # A caller classified z_score must ALSO be empirically uniform. If it
            # is not, the classification is wrong and that is reported, not hidden.
            cell["verdict"] = (
                "UNEXPLAINED_NON_UNIFORMITY"
                if cell["measured"]["uniform_rejected"]
                else "CONFIRMED_CALIBRATED"
            )
            cell["empirical_detection"] = "NOT_APPLICABLE"
        cells.append(cell)

    defective = [c["test_id"] for c in cells if c["verdict"] == "DEFECTIVE_BY_ALGEBRAIC_IDENTITY"]
    unexplained = [
        c["test_id"] for c in cells if c["verdict"] in ("UNEXPLAINED_NON_UNIFORMITY",)
    ]
    unresolved = [
        c["test_id"] for c in cells if c["verdict"].startswith("UNRESOLVED")
    ]
    undetected = [
        c["test_id"] for c in cells if c["empirical_detection"] == "NOT_DETECTED_AT_THIS_RESOLUTION"
    ]
    return {
        "schema": REPORT_SCHEMA,
        "bit_length": f"2^{18 + shift}",
        "seeds": seeds,
        "label": label,
        "alpha": 0.01,
        "shared_battery_sha256": sha256_file(Path(rb.__file__)),
        "helper": {
            "name": "engine.validation.rng_battery._erfc_p",
            "definition": "erfc(|z| / sqrt(2))",
            "meaning": "the two-sided normal tail 2(1 - Phi(|z|))",
            "valid_only_for": "standardised z-scores",
        },
        "cells": cells,
        "summary": {
            "callers_audited": len(cells),
            "defective": defective,
            "unexplained_non_uniformity": unexplained,
            "unresolved": unresolved,
            "defects_not_detected_at_this_length": undetected,
            "all_measured_callers_uniform_excluding_proven_defects": (
                not unexplained and not unresolved
            ),
            "conclusion": (
                "Exactly one caller, T03_runs, passes a quantity already in erfc "
                "units, so the sqrt(2) is provably spurious there. The other four "
                "pass genuine z-scores and are empirically uniform, so the sqrt(2) "
                "is correct for them. Note that empirical non-detection of the "
                "T03 defect at 2^22 is a resolution failure of the 200-seed KS "
                "test, not evidence that the defect is absent."
                if defective == ["T03_runs"] and not unexplained and not unresolved
                else "See cells; the pattern differs from the single-caller defect."
            ),
        },
    }


if __name__ == "__main__":
    seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    label = sys.argv[2] if len(sys.argv) > 2 else "erfc-caller-audit"
    shift = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    print(json.dumps(analyze(seeds, shift, label), indent=2, sort_keys=True))
