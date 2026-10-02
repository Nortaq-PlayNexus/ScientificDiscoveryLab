#!/usr/bin/env python3
"""Freeze the EXP-0017 / N-005 balanced lattice-size protocol exactly once.

Addresses audit finding N-005 (AUDIT/NEXT_EXPERIMENTS.md Priority 1): is there a
reproducible power-of-two effect on the 2D site cluster-mass exponent, after
matching physical size, estimator, and random-stream policy?

Design decisions frozen here, all before any execution:

  * NESTED common-random-numbers pairs. One L x L uniform field yields the
    configuration for every preregistered sub-window size, so a power-of-two
    size and its neighbour share every random number. A preregistered
    independent-stream arm re-measures the primary contrast without any sharing.
  * A NULL-CONTRAST arm: two adjacent NON-power-of-two pairs one unit apart.
    Any smooth size-dependent finite-size correction shows up here, so the
    power-of-two contrast can be compared against the scale of a known-smooth
    artifact.
  * A 2-ADIC LADDER to separate "power of two" from "even" and from higher
    powers of two.
  * An equivalence (TOST-style) test with a margin preregistered BELOW the
    historical effect size, plus an explicit INCONCLUSIVE_BY_RESOLUTION state so
    an underpowered run can never be reported as "no effect".

Falsification (from the audit): if the contrast lies below the preregistered
equivalence margin, "lattice artifact" is unsupported.
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

from engine.hypothesis_testing.prereg import freeze_config  # noqa: E402

DEFAULT_TARGET = INV_ROOT / "CONFIG" / "prereg_EXP-0017.json"

D_F_REF = 91.0 / 48.0          # 1.8958333...
EQUIV_MARGIN = 0.010           # preregistered equivalence margin in D_f units
HISTORICAL_P2_DEFICIT = 0.0265 # EXP-0009 1.8697 vs EXP-0010 1.8962

BASES = [128, 256, 512, 1024]
N_REAL = {"128": 100, "256": 100, "512": 100, "1024": 60}

# Sub-window sizes sampled from each base field. `offset` is the number of rows
# and columns trimmed from the bottom/right, so size = base - offset.
PAIR_OFFSETS = {
    "p2_anchored": {"upper": 0, "lower": 1},        # (L-1) -> L, midpoint L-0.5
    "nonp2_anchored": {"upper": 1, "lower": 2},     # (L-2) -> (L-1), midpoint L-1.5
    "nonp2_null_control": {"upper": 2, "lower": 3},  # (L-3) -> (L-2), midpoint L-2.5
}
# 2-adic ladder: even non-power-of-two sub-windows, offsets chosen so that
# size = base-offset has a low power-of-two divisibility.
LADDER_OFFSETS = [2, 4, 8]   # sizes L-2, L-4, L-8 (all even when base is even)
LADDER_BASES = [256, 512]

REPLICATION_N = 40

PARAMS = {
    "audit_finding_id": "N-005",
    "investigation_id": "Q-P009",
    "system": "2D square-lattice site percolation, four-connectivity, open boundaries",
    "p_c": 0.5927460507921,
    "p_c_source": "Ziff PRL 117, 125703 (2016) exact 2D site threshold; used as a fixed input, NOT re-estimated",
    "primary_estimator": {
        "quantity": "largest open cluster size S_max in sites",
        "implementation": "scipy.ndimage.label with four-neighbour structure [[0,1,0],[1,1,1],[0,1,0]]",
        "independence_implementation": "scipy.sparse.csgraph.connected_components on an explicit square-lattice edge list",
    },
    "base_sizes": BASES,
    "n_real": N_REAL,
    "pair_offsets": PAIR_OFFSETS,
    "ladder_offsets": LADDER_OFFSETS,
    "ladder_bases": LADDER_BASES,
    "independent_stream_replication_n": REPLICATION_N,
    "reference_D_f": D_F_REF,
    "equivalence_margin": EQUIV_MARGIN,
    "historical_p2_deficit": HISTORICAL_P2_DEFICIT,
    "margin_rationale": (
        f"The historical claim is a power-of-two deficit of about "
        f"{HISTORICAL_P2_DEFICIT} in D_f (EXP-0009 1.8697 on powers of two vs "
        f"EXP-0010 1.8962 off them). The equivalence margin {EQUIV_MARGIN} is "
        f"{HISTORICAL_P2_DEFICIT / EQUIV_MARGIN:.2f}x smaller than that effect, "
        "so 'no lattice artifact' is only declared when the data exclude an "
        "effect large enough to explain the historical discrepancy."
    ),
    "primary_statistic": {
        "name": "power_of_two_contrast_beta",
        "definition": (
            "For each base L, the local log-log slope between two nested "
            "sub-window sizes is estimated from the paired realization-level "
            "differences of log S_max. beta is the inverse-variance-weighted "
            "difference between the mean slope of power-of-two-anchored pairs "
            "(L-1 -> L) and the mean slope of non-power-of-two-anchored pairs "
            "(L-2 -> L-1)."
        ),
        "why_this_estimator": (
            "Both pair types are local finite differences of the same scaling "
            "function at sizes one unit apart, so any smooth size-dependent "
            "finite-size correction largely cancels and beta isolates a genuine "
            "power-of-two discontinuity."
        ),
        "uncertainty": "nonparametric bootstrap over realizations, paired within each base",
    },
    "decision_rule": {
        "LATTICE_ARTIFACT_SUPPORTED": (
            "the 95% interval for beta excludes 0 AND |beta| exceeds the "
            "equivalence margin: a power-of-two effect is resolved and is large "
            "enough to matter"
        ),
        "LATTICE_ARTIFACT_UNSUPPORTED": (
            "the entire 90% interval for beta lies strictly inside "
            f"(-{EQUIV_MARGIN}, +{EQUIV_MARGIN}): equivalence is demonstrated at "
            "the preregistered margin, so a power-of-two artifact of the size "
            "needed to explain the historical discrepancy is excluded"
        ),
        "INCONCLUSIVE_BY_RESOLUTION": (
            "the 90% interval is not contained in the equivalence margin and "
            "does not exclude 0. This is an explicit non-result: the run could "
            "not resolve the contrast and must NOT be reported as 'no effect'"
        ),
        "WINDOW_OR_ESTIMATOR_SENSITIVE": (
            "the independent-stream arm or the 2-adic ladder contradicts the "
            "primary verdict; the primary verdict is then void"
        ),
        "engineering_failure": (
            "any preregistered gate failure (C7 disagreement, raw round-trip "
            "mismatch, incomplete realization counts) yields INCONCLUSIVE"
        ),
    },
    "null_contrast_control": {
        "name": "smooth_artifact_scale",
        "definition": (
            "difference between the nonp2_anchored slope and the "
            "nonp2_null_control slope, i.e. two adjacent non-power-of-two pairs "
            "one unit apart"
        ),
        "interpretation": (
            "This quantifies how large a purely smooth size dependence appears "
            "in the same estimator. If |beta| is not clearly larger than this "
            "control, a power-of-two interpretation is not supported even if "
            "beta is nominally nonzero."
        ),
    },
    "controls": [
        "nested common-random-numbers pairing, with an independent-stream arm as the cross-check",
        "null contrast between two adjacent non-power-of-two pairs",
        "2-adic ladder separating power-of-two from even and from higher divisibility",
        "independent second implementation (explicit edge list + connected_components) on the same masks",
        "from-scratch pure-Python BFS census on the smallest cells as a third implementation",
        "raw per-realization S_max for every sampled size, hash-bound and round-trip validated",
        "exact-zero and all-open sanity fields",
    ],
    "known_limitations": [
        "p_c is a fixed input at the infinite-lattice value; open boundaries "
        "shift the finite-size threshold by O(1/L), so the sampled point is "
        "slightly off criticality and that offset is not measured here",
        "nested sub-windows are not independent samples; the bootstrap "
        "resamples realizations, which preserves the pairing",
        "the contrast tests a discontinuity in the size axis, not the absolute "
        "accuracy of D_f, which is reported separately",
        "sizes are matched in linear size to one lattice unit, so residual "
        "area mismatch is O(1/L) and is absorbed by the pair-type contrast",
    ],
    "claim_guards": [
        "This tests a numerical artifact in one estimator. It cannot establish "
        "or refute new physics.",
        "EXP-0009 and EXP-0010 historical conclusions are not modified by this "
        "run; they are tested, not overwritten.",
        "No novelty claim. A positive result is an escalation, not a discovery.",
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()
    frozen = freeze_config(
        experiment_id="EXP-0017",
        hypothesis_id="HYP-P009",
        question_id="Q-P009",
        seed=20260926,
        alpha=0.01,
        controls=tuple(PARAMS["controls"]),
        analyses=(
            "primary: power-of-two contrast beta, nested paired design, realization bootstrap",
            "control: smooth-artifact null contrast between adjacent non-power-of-two pairs",
            "secondary: 2-adic ladder contrasts",
            "secondary: independent-stream replication of the primary contrast",
            "secondary: absolute D_f of the balanced set vs 91/48",
            "gates: C7 second implementation, third implementation, raw round-trip",
        ),
        params=PARAMS,
        out_path=target,
        note=(
            "Addresses audit finding N-005. Frozen before any execution. Tests "
            "whether the historical power-of-two lattice artifact is "
            "reproducible under a balanced, matched, dependence-aware design. "
            "Amend only through CONFIG/changes.jsonl."
        ),
    )
    print(json.dumps({
        "created": str(target),
        "config_sha256": frozen["config_sha256"],
        "equivalence_margin": EQUIV_MARGIN,
        "reference_D_f": D_F_REF,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
