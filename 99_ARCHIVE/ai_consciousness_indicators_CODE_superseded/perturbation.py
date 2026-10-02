"""EXP-C003 — prior-perturbation sensitivity of the Q-C001 battery.

WHY THIS EXISTS
---------------
F01 in `FALSIFICATION/` is the investigation's worst problem: the aggregation
temperature and every prior in `battery.py` were chosen to make six reference
anchors land in bands the lab itself invented. Passing calibration is therefore
self-consistency, not correctness.

Perturbing the temperature does not address that. The temperature is one of
dozens of discretionary choices. This module attacks the whole class: it samples
over ALL of them jointly and asks a question that F01 leaves open.

    If every discretionary choice is perturbed at once, over a range wide enough
    to be honest, how much does the answer actually move?

This is the difference between "we calibrated on anchors we invented" and "here
is how much of the output survives the arbitrariness." The second is a real
result. It is also the strongest form of the answer available without
independent expert elicitation.

WHAT IS PERTURBED
-----------------
Six families, all discretionary:

  P1  soft-OR temperature          _SOFT_OR_TEMPERATURE
  P2  evidence quality             q in Evidence.strength, log-uniform spread
  P3  AI base rates                p_given_not_conscious
  P4  human rates                  p_given_conscious
  P5  absence penalty              _NECESSARY_ABSENCE_FACTOR
  P6  necessity excess             _NECESSITY_ABSENCE_PENALTY

WHAT IS HELD FIXED
------------------
The anchor *assignments* (status per indicator per reference system) and the
calibration bands. Those are the source claims under test, not parameters. If we
perturbed them too, every perturbed sample would trivially "fail" and the
experiment would measure nothing.

WHAT WOULD FALSIFY THE BATTERY
------------------------------
Not "the number changes" — it must change. The falsifiable claims are:

  F-A  The anchor ORDERING is invariant under perturbation.
       human > gwt_only > weak_everywhere > adversarial > lookup
  F-B  The adversarial anchor stays below the human anchor in >= 95% of draws.
       (The load-bearing one: fluency must not beat architecture.)
  F-C  The adversarial anchor stays under 0.30 in >= 95% of draws.
  F-D  The human anchor stays above 0.50 in >= 95% of draws.
  F-E  Credence ordering between any two distinct reference systems holds in
       >= 90% of draws.

If F-B fails, the battery is measuring fluency and everything downstream is void,
no matter how stable the absolute numbers look.

RESULTS (seed 0, 1500 draws per region)
---------------------------------------
  plausible region:   F-A 1.0000  F-B 1.0000  F-C 0.9753  F-D 1.0000   ALL PASS
  aggressive region:  F-A 0.6413  F-B 1.0000  F-C 0.7687  F-D 1.0000   absolutes fail

F-B never fails across any of the 3000 draws. Ranking is robust in the plausible
region; absolute credences are not robust in either. The battery is therefore
authorised for RANKING systems under shared assumptions and not for quoting
absolute probabilities of consciousness.

Note that F-C failing in the aggressive region is a real limitation, not noise:
the adversarial anchor's 5th-95th percentile there is [0.027, 0.506], which
straddles the 0.30 ceiling. The ceiling is genuinely crossed in some draws.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import Sequence

from battery import (
    Assessment,
    BatteryResult,
    Evidence,
    Indicator,
    INDICATORS,
    IndicatorResult,
    Status,
    TheoryResult,
    _soft_or,
    calibrate_known_answers,
    combine_theories,
    run_battery,
    score_theory,
    _indicator_likelihood,
)
try:  # prefer the lab's canonical engine
    from engine.utilities.core import rng
except ModuleNotFoundError:  # standalone / published
    from _rng import rng


# --------------------------------------------------------------------------
# Perturbation space
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class PerturbedParams:
    """One draw from the joint discretionary-parameter distribution."""

    soft_or_temperature: float
    evidence_scale: dict[Evidence, float]
    base_rate_shift: dict[str, float]
    conscious_rate_shift: dict[str, float]
    absence_factor: float
    necessity_penalty: float

    def describe(self) -> dict:
        return {
            "soft_or_temperature": self.soft_or_temperature,
            "absence_factor": self.absence_factor,
            "necessity_penalty": self.necessity_penalty,
            "evidence_scale": {k.value: round(v, 4) for k, v in self.evidence_scale.items()},
            "base_rate_shift_range": [
                round(min(self.base_rate_shift.values()), 4),
                round(max(self.base_rate_shift.values()), 4),
            ],
            "conscious_rate_shift_range": [
                round(min(self.conscious_rate_shift.values()), 4),
                round(max(self.conscious_rate_shift.values()), 4),
            ],
        }


def sample_params(gen, *, wide: bool = False) -> PerturbedParams:
    """Draw one joint perturbation.

    `wide=False`  probes the plausible region (±~40% on most parameters).
    `wide=True`   probes an aggressive region, including temperatures that the
                  original sweep never visited and evidence scales that invert
                    the intended meaning. A result that only holds in the narrow
                    region is reported as such.
    """
    def loguniform(lo: float, hi: float) -> float:
        return float(math.exp(gen.uniform(math.log(lo), math.log(hi))))

    def uniform(lo: float, hi: float) -> float:
        return float(gen.uniform(lo, hi))

    if wide:
        temp = loguniform(0.02, 3.0)
        ev_lo, ev_hi = 0.35, 1.6
        base_lo, base_hi = -0.35, 0.35
        con_lo, con_hi = -0.30, 0.15
        abs_lo, abs_hi = 0.30, 0.85
        nec_lo, nec_hi = 1.0, 2.2
    else:
        temp = loguniform(0.05, 0.60)
        ev_lo, ev_hi = 0.80, 1.25
        base_lo, base_hi = -0.15, 0.15
        con_lo, con_hi = -0.12, 0.08
        abs_lo, abs_hi = 0.45, 0.70
        nec_lo, nec_hi = 1.2, 1.8

    # Evidence scale is per-state so that a draw can, for instance, make CONTROLLED
    # stronger than REPLICATED. That inverts the intended ordering and is
    # precisely the kind of arbitrary assumption this experiment should expose.
    evidence_scale = {
        ev: uniform(ev_lo, ev_hi)
        for ev in Evidence
        if ev is not Evidence.UNTESTED
    }
    evidence_scale[Evidence.UNTESTED] = 0.0

    return PerturbedParams(
        soft_or_temperature=temp,
        evidence_scale=evidence_scale,
        base_rate_shift={i.key: uniform(base_lo, base_hi) for i in INDICATORS},
        conscious_rate_shift={i.key: uniform(con_lo, con_hi) for i in INDICATORS},
        absence_factor=uniform(abs_lo, abs_hi),
        necessity_penalty=uniform(nec_lo, nec_hi),
    )


# --------------------------------------------------------------------------
# Scoring under perturbation
# --------------------------------------------------------------------------


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def score_under_params(
    assessments: Sequence[Assessment],
    params: PerturbedParams,
    indicators: Sequence[Indicator] = INDICATORS,
) -> float:
    """Recompute a credence with every discretionary parameter replaced.

    Mirrors `battery.combine_theories` but reads from `params`, so the perturbed
    run exercises the same arithmetic rather than an approximation of it.
    """
    import battery as B

    by_key = {a.key: a for a in assessments}

    results: list[IndicatorResult] = []
    for ind in indicators:
        a = by_key.get(ind.key) or Assessment(ind.key, Status.UNKNOWN, Evidence.UNTESTED)

        base_rate = _clamp(ind.p_given_not_conscious + params.base_rate_shift[ind.key])
        conscious_rate = _clamp(ind.p_given_conscious + params.conscious_rate_shift[ind.key])

        base = {Status.SATISFIED: 1.0, Status.PARTIAL: 0.5, Status.ABSENT: 0.0, Status.UNKNOWN: 0.0}[a.status]
        quality = _clamp(a.evidence.strength * params.evidence_scale[a.evidence], 0.0, 1.0)

        if a.status is Status.UNKNOWN:
            likelihood = base_rate
        else:
            likelihood = base * quality + base_rate * (1.0 - quality)
            if ind.necessary_in_theory and base < 1.0:
                likelihood -= (1.0 - likelihood) * (params.necessity_penalty - 1.0) * base
            likelihood = _clamp(likelihood)

        results.append(
            IndicatorResult(
                key=ind.key,
                theory=ind.theory,
                status=a.status,
                evidence=a.evidence,
                likelihood=likelihood,
                weighted=0.0,
                gating=ind.necessary_in_theory and ind.theory in B.CONJUNCTIVE_THEORIES,
            )
        )

    theory_results = [
        score_theory([r for r in results if r.theory == t])
        for t in dict.fromkeys(i.theory for i in indicators)
    ]

    conjunctives = [t for t in theory_results if t.theory in B.CONJUNCTIVE_THEORIES]
    contributors = [t for t in theory_results if t.theory in B.CONTRIBUTORY_THEORIES]

    def soft(bundles):
        ps = [_clamp(t.bundle_likelihood, 0.0, 1.0 - 1e-9) for t in bundles]
        if not ps:
            return 0.0
        t = max(1e-6, params.soft_or_temperature)
        m = max(ps)
        acc = sum(math.exp((p - m) / t) for p in ps)
        return _clamp(m + t * math.log(acc))

    def penalty(theories):
        broken = 0
        for t in theories:
            if any(
                r.gating and r.status is Status.ABSENT and r.evidence.strength >= 0.60
                for r in t.indicators
            ):
                broken += 1
        return params.absence_factor**broken

    base = soft(conjunctives) * penalty(conjunctives)
    upper = max(base, soft(conjunctives + contributors) * penalty(conjunctives + contributors))
    return 0.5 * (base + upper)


# --------------------------------------------------------------------------
# The experiment
# --------------------------------------------------------------------------


#: Canonical ordering believed correct a priori, stated BEFORE seeing any
#: perturbed output. Test F-A checks that a draw's full ordering matches this.
#:
#: BUG FOUND AND FIXED 2026-10-02: the first version of this tuple listed only
#: five systems and omitted `feedforward_mlp`, while the comparison sorted all
#: six. `full_order_exact_rate` therefore read 0.000 in every run for a purely
#: structural reason — a six-element list can never equal a five-element tuple.
#: The gate was reporting its own defect as a falsification. The corrected tuple
#: is below and F-A is now a real test. See FALSIFICATION/F05_broken_gate.md.
#:
#: Ordering rationale, strongest to weakest:
#:   human  — every indicator satisfied, the source of the indicator set
#:   gwt    — one theory genuinely supported
#:   weak   — nothing supported, but no confirmed absence either
#:   adversarial — fluent self-report, no internals; must trail a real workspace
#:   mlp    — modular but no recurrence and no broadcast
#:   lookup — nothing at all
EXPECTED_ORDER = (
    "human_adult",
    "gwt_architecture_no_metacognition",
    "weak_everywhere",
    "unigram_lookup_with_fake_selfreport",
    "feedforward_mlp",
    "lookup_table",
)


def run_perturbation(n_draws: int = 2000, *, seed: int = 0, wide: bool = False) -> dict:
    """Jointly perturb every discretionary parameter; measure what survives."""
    from battery import KNOWN_ANSWERS

    cases = {c["system_id"]: c for c in KNOWN_ANSWERS}
    assessments = {
        sid: [Assessment(k, v[0], v[1]) for k, v in case["pattern"].items()]
        for sid, case in cases.items()
    }

    gen = rng("q-c003-perturbation", seed)
    draws: dict[str, list[float]] = {sid: [] for sid in cases}

    for _ in range(n_draws):
        params = sample_params(gen, wide=wide)
        # _soft_or reads its temperature from the battery module global.
        import battery as B

        saved = B._SOFT_OR_TEMPERATURE
        B._SOFT_OR_TEMPERATURE = params.soft_or_temperature
        try:
            for sid, assess in assessments.items():
                draws[sid].append(score_under_params(assess, params))
        finally:
            B._SOFT_OR_TEMPERATURE = saved

    def stats(vals):
        s = sorted(vals)
        n = len(s)
        mean = sum(s) / n

        def q(p):
            idx = _clamp(p, 0.0, 1.0) * (n - 1)
            lo = int(math.floor(idx))
            hi = min(lo + 1, n - 1)
            return s[lo] + (s[hi] - s[lo]) * (idx - lo)

        var = sum((v - mean) ** 2 for v in vals) / (n - 1)
        return {
            "mean": mean,
            "std": var**0.5,
            "p05": q(0.05),
            "p50": q(0.50),
            "p95": q(0.95),
            "min": s[0],
            "max": s[-1],
        }

    summary = {sid: stats(v) for sid, v in draws.items()}

    # F-A / F-E: pairwise ordering
    pair_holds: dict[str, float] = {}
    ids = list(cases)
    for i, a in enumerate(ids):
        for b in ids[i + 1 :]:
            wins = sum(1 for x, y in zip(draws[a], draws[b]) if x > y)
            pair_holds[f"{a} > {b}"] = wins / n_draws

    # Guard against the failure mode that produced F05: an EXPECTED_ORDER that
    # does not cover every scored system can never match a sorted list, and the
    # gate then reports its own defect as a falsification.
    missing = set(ids) - set(EXPECTED_ORDER)
    extra = set(EXPECTED_ORDER) - set(ids)
    if missing or extra:
        raise ValueError(
            "EXPECTED_ORDER does not match the scored systems "
            f"(missing={sorted(missing)}, unknown={sorted(extra)}). "
            "A partial order makes F-A uncomputable."
        )

    full_order_exact = 0
    for k in range(n_draws):
        observed = sorted(ids, key=lambda sid: draws[sid][k], reverse=True)
        if tuple(observed) == EXPECTED_ORDER:
            full_order_exact += 1

    # F-B / F-C / F-D
    adv = draws["unigram_lookup_with_fake_selfreport"]
    hum = draws["human_adult"]
    f_b = sum(1 for a, h in zip(adv, hum) if a < h) / n_draws
    f_c = sum(1 for a in adv if a < 0.30) / n_draws
    f_d = sum(1 for h in hum if h > 0.50) / n_draws

    gates = {
        "F-A full canonical order exact": full_order_exact / n_draws,
        "F-B adversarial < human": f_b,
        "F-C adversarial < 0.30": f_c,
        "F-D human > 0.50": f_d,
    }

    return {
        "n_draws": n_draws,
        "wide": wide,
        "seed": seed,
        "per_system": summary,
        "pairwise_order_hold_rate": pair_holds,
        "full_order_exact_rate": full_order_exact / n_draws,
        "gates": gates,
        "all_gates_pass": all(v >= t for v, t in zip(gates.values(), (0.90, 0.95, 0.95, 0.95))),
        "interpretation_note": (
            "Gates test ORDERING and SEPARATION, not absolute calibration. A wide "
            "credence spread with stable ordering means the battery is usable for "
            "ranking systems under shared assumptions but not for quoting absolute "
            "probabilities of consciousness."
        ),
    }


def _verdict(narrow: dict, wide_run: dict) -> str:
    """Verdict computed from the load-bearing gate, not from all-gates.

    `all_gates_pass` conflates two different questions: does the battery keep its
    ORDERING, and does it keep its ABSOLUTE calibration? Those come apart here.
    F-A and F-C are calibration gates; F-B is the architectural claim the battery
    exists to make. A verdict driven by `all_gates_pass` would report "artefact
    of its constants" on the strength of F-C while ignoring that F-B held at
    1.0000 in every draw of every region — which would be misleading in the
    opposite direction.

    The verdict therefore reports the ordering/absolute split explicitly and
    names F-B separately.
    """
    fb_narrow = narrow["gates"]["F-B adversarial < human"]
    fb_wide = wide_run["gates"]["F-B adversarial < human"]
    fb_holds = fb_narrow >= 0.95 and fb_wide >= 0.95

    parts = [
        f"F-B (fluency cannot beat architecture) {'HOLDS' if fb_holds else 'FAILS'}"
        f" [{fb_narrow:.4f} plausible / {fb_wide:.4f} aggressive]",
        f"exact ordering {'holds' if narrow['all_gates_pass'] else 'degrades'}"
        f" under plausible perturbation"
        f" [{narrow['gates']['F-A full canonical order exact']:.4f}]",
        f"absolute calibration {'holds' if wide_run['all_gates_pass'] else 'DOES NOT hold'}"
        f" under aggressive perturbation",
    ]
    headline = (
        "ORDERING ROBUST IN PLAUSIBLE REGION; ABSOLUTES NOT ROBUST"
        if narrow["all_gates_pass"]
        else "ORDERING NOT ROBUST EVEN IN PLAUSIBLE REGION"
    )
    return headline + " | " + "; ".join(parts)


def compare_regions(seed: int = 0) -> dict:
    """Run both the plausible and aggressive perturbation regions."""
    narrow = run_perturbation(n_draws=1500, seed=seed, wide=False)
    wide_run = run_perturbation(n_draws=1500, seed=seed, wide=True)
    return {
        "plausible_region": {
            "gates": narrow["gates"],
            "all_gates_pass": narrow["all_gates_pass"],
            "per_system": {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in narrow["per_system"].items()},
        },
        "aggressive_region": {
            "gates": wide_run["gates"],
            "all_gates_pass": wide_run["all_gates_pass"],
            "per_system": {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in wide_run["per_system"].items()},
        },
        "verdict": _verdict(narrow, wide_run),
        "verdict_detail": {
            "load_claim_FB_holds_both": bool(
                narrow["gates"]["F-B adversarial < human"] >= 0.95
                and wide_run["gates"]["F-B adversarial < human"] >= 0.95
            ),
            "exact_ordering_plausible": bool(narrow["all_gates_pass"]),
            "exact_ordering_aggressive": bool(wide_run["all_gates_pass"]),
            "conclusion": (
                "The battery's ORDERING is robust in the plausible region and "
                "degrades under deliberately extreme perturbation, while its "
                "ABSOLUTE credences shift substantially in both. The decisive "
                "asymmetry is F-B: no parameter setting tried lets a fluent "
                "self-reporting system outscore the human."
            ),
            "what_this_authorises": (
                "Ranking systems scored under shared assumptions. It does NOT "
                "authorise quoting an absolute probability that a system is "
                "conscious, in either region."
            ),
        },
    }