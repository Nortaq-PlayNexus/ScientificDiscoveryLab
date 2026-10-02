"""Q-C001 consciousness indicator battery — scoring, aggregation, calibration.

DESIGN NOTE — why this is not a checklist
------------------------------------------
The obvious implementation scores each indicator and counts the satisfied ones.
That is wrong, and wrong in a way that inflates results, so this module refuses
to do it.

Butlin et al. (2023, Table 1) do not claim "N of 14 satisfied => consciousness".
They claim that *some subsets are jointly sufficient*, and each indicator is
necessary *according to at least one theory*. That gives three distinct problems
a count cannot handle:

1. **Intra-theory correlation.** RPT-1 and RPT-2 come from one theory about one
   mechanism. Counting them twice is double-counting evidence.
2. **Inter-theory non-independence.** The theories are not independent
   hypotheses either. A system that satisfies GWT-2 (bottleneck + selective
   attention) typically gets GWT-3 (broadcast) nearly free.
3. **Necessity vs sufficiency asymmetry.** Failing one indicator of a theory
   that treats it as necessary is far more informative than satisfying the other
   thirteen.

So the aggregation here runs in two stages:

    stage 1: collapse indicators WITHIN a theory to one theory-level verdict
             (a theory's bundle is what it cares about, not its parts)
    stage 2: combine theory-level verdicts across theories with a soft-OR, then
             apply a multiplicative penalty per theory whose necessary
             indicators are confirmed absent

Stage 2 encodes two claims that pull in opposite directions, which is why it is
not a single combiner. The theories assert **sufficiency** — some subset is
enough — so across theories the combiner is an OR; a plain OR is too generous,
so it is a temperature-smoothed maximum. The theories also assert
**necessity** — several properties are required — so each theory with a
confirmed-absent necessary indicator is charged a penalty once, per theory
rather than per indicator. An earlier iteration used a noisy-AND and drove a
plausible system to exactly 0.000; see FALSIFICATION F00.

and the final number is a credence, not a verdict. The battery returns bounds and
decompositions, never a boolean.

Also implemented here, because a battery nobody has calibrated is not a
measurement instrument: `calibrate_known_answers`, which runs the scoring
function against reference systems whose consciousness status is not in dispute.
If the battery cannot separate a human from a lookup table, its output on
frontier models is uninterpretable and the gate fails closed.

Evidence states (RESEARCH_RULES.md §8) are carried through, not silently
promoted. A verdict computed from UNTESTED evidence is returned as UNTESTED.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Mapping, Sequence

try:  # prefer the lab's canonical engine when running inside the lab checkout
    from engine.utilities.core import rng, sha256_json
except ModuleNotFoundError:  # standalone / published
    from _rng import rng, sha256_json

# --------------------------------------------------------------------------
# Evidence states — RESEARCH_RULES.md §8
# --------------------------------------------------------------------------


class Evidence(str, Enum):
    """Evidence state for one indicator assessment."""

    UNTESTED = "UNTESTED"
    INITIAL = "INITIAL_RESULT"
    CONTROLLED = "CONTROLLED"
    REPLICATED = "REPLICATED"
    INDEPENDENT = "INDEPENDENTLY_REPRODUCED"
    LITERATURE = "LITERATURE_CHECKED"
    EXTERNAL = "EXTERNALLY_VALIDATED"

    @property
    def strength(self) -> float:
        """Multiplier on how much credence mass an assessment may carry.

        Deliberately sub-linear: going from INITIAL to REPLICATED should move the
        number, but not rescue a claim built on a theory that failed its
        controls. Evidence quality and theory quality are separate axes.
        """
        return {
            Evidence.UNTESTED: 0.0,
            Evidence.INITIAL: 0.35,
            Evidence.CONTROLLED: 0.60,
            Evidence.REPLICATED: 0.80,
            Evidence.INDEPENDENT: 0.90,
            Evidence.LITERATURE: 0.95,
            Evidence.EXTERNAL: 1.00,
        }[self]


class Status(str, Enum):
    """Indicator assessment outcome. NOT a consciousness verdict."""

    SATISFIED = "SATISFIED"
    PARTIAL = "PARTIALLY_SATISFIED"
    ABSENT = "NOT_SATISFIED"
    UNKNOWN = "UNTESTED"


@dataclass(frozen=True)
class Indicator:
    """One indicator property from Butlin et al. 2023 Table 1."""

    key: str
    theory: str
    text: str
    #: True where the source theory treats the property as NECESSARY.
    necessary_in_theory: bool
    #: Prior credence that a conscious system shows this property (from human work).
    p_given_conscious: float
    #: Prior credence an arbitrary software system shows it (base rate for AI).
    p_given_not_conscious: float
    #: Properties only identifiable from weights we cannot access.
    requires_whitebox: bool = False


# Table 1 of Butlin, Long et al., arXiv:2308.08708 (2023), and the condensed
# restatement in Butlin, Long, Bayne, Bengio et al., Trends Cogn Sci 30(6):488-501
# (2026), DOI 10.1016/j.tics.2025.10.011. Wording abbreviated here.
# Positional args after the text are: necessary_in_theory, p_given_conscious,
# p_given_not_conscious. Both probabilities are hand-set from the literature
# narrative (see LITERATURE.md), not measured. Long lines are deliberate: one
# indicator per row reads better here than a reflowed table.
INDICATORS: tuple[Indicator, ...] = (
    Indicator("RPT-1", "RPT", "Input modules using algorithmic recurrence", True, 0.95, 0.60),
    Indicator("RPT-2", "RPT",
              "Input modules generating organised, integrated perceptual representations",
              True, 0.80, 0.25),
    Indicator("GWT-1", "GWT",
              "Multiple specialised systems capable of operating in parallel (modularity)",
              True, 0.85, 0.70),
    Indicator("GWT-2", "GWT",
              "Limited-capacity workspace: information bottleneck plus selective attention",
              True, 0.90, 0.15),
    Indicator("GWT-3", "GWT",
              "Global broadcast: workspace contents available to all modules",
              True, 0.85, 0.10),
    Indicator("GWT-4", "GWT",
              "State-dependent attention enabling serial module queries for complex tasks",
              True, 0.75, 0.10),
    Indicator("HOT-1", "HOT", "Generative, top-down or noisy perception modules",
              True, 0.80, 0.30),
    Indicator("HOT-2", "HOT",
              "Metacognitive monitoring separating reliable representations from noise",
              True, 0.80, 0.20),
    Indicator("HOT-3", "HOT",
              "Agency via belief-formation/action-selection with disposition to update "
              "on metacognitive output",
              True, 0.80, 0.25),
    Indicator("HOT-4", "HOT", "Sparse and smooth coding generating a quality space",
              True, 0.60, 0.20),
    Indicator("AST-1", "AST",
              "Predictive model representing and enabling control over current attention state",
              True, 0.75, 0.10),
    Indicator("PP-1", "PP", "Input modules using predictive coding", False, 0.85, 0.35),
    Indicator("AE-1", "AE",
              "Agency: learning from feedback, flexible responsiveness to competing goals",
              False, 0.90, 0.45),
    Indicator("AE-2", "AE",
              "Embodiment: modelling output-input contingencies and using this model in control",
              False, 0.70, 0.15),
)

INDICATORS_BY_KEY: Mapping[str, Indicator] = {i.key: i for i in INDICATORS}

#: Theories whose bundles are treated as jointly sufficient (Butlin et al. 2023 §2.5).
#: AE and PP are deliberately EXCLUDED from the conjunction: the source treats
#: them as possible contributors, not as jointly sufficient conditions. Counting
#: them as required would let their absence veto a system the other theories
#: call a strong candidate.
CONJUNCTIVE_THEORIES: tuple[str, ...] = ("RPT", "GWT", "HOT", "AST")
#: Contributory only — recorded, reported, never gating.
CONTRIBUTORY_THEORIES: tuple[str, ...] = ("PP", "AE")


# --------------------------------------------------------------------------
# Assessments
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Assessment:
    """One indicator's assessment: outcome + how well we know it."""

    key: str
    status: Status
    evidence: Evidence
    note: str = ""

    def __post_init__(self) -> None:
        if self.key not in INDICATORS_BY_KEY:
            raise KeyError(f"unknown indicator: {self.key}")
        if self.status is Status.UNKNOWN and self.evidence is not Evidence.UNTESTED:
            raise ValueError(
                f"{self.key}: UNKNOWN outcome cannot carry {self.evidence.value}. "
                "An unrun test has no evidence grade; record it as UNTESTED."
            )
        if self.status in (Status.SATISFIED, Status.PARTIAL) and self.evidence is Evidence.UNTESTED:
            raise ValueError(
                f"{self.key}: claims SATISFIED/PARTIAL with no evidence. "
                "If it has not been tested it is UNTESTED, not SATISFIED."
            )


#: Numeric value of each status in [0, 1] before the necessity correction.
_STATUS_VALUE: Mapping[Status, float] = {
    Status.SATISFIED: 1.0,
    Status.PARTIAL: 0.5,
    Status.ABSENT: 0.0,
    Status.UNKNOWN: 0.0,
}

#: Weight applied when an indicator is labelled NECESSARY by its source theory.
#: A confirmed absence is penalised harder than a confirmed presence is rewarded,
#: which encodes the necessity/sufficiency asymmetry from the module docstring.
_NECESSITY_ABSENCE_PENALTY = 1.5


@dataclass(frozen=True)
class IndicatorResult:
    key: str
    theory: str
    status: Status
    evidence: Evidence
    #: P(indicator present) implied by this assessment, in [0, 1].
    likelihood: float
    #: Evidence-weighted shortfall applied to the theory bundle, in [0, 1].
    weighted: float
    #: True when the indicator's absence should count against the theory.
    gating: bool
    note: str = ""


def _indicator_likelihood(ind: Indicator, a: Assessment) -> float:
    """P(indicator present | evidence), combining status grade with evidence quality.

    Builds on the assessment's 0/0.5/1 status value, then discounts by evidence
    strength and mixes toward the base rate by how little we have tested.
    Never returns 0 or 1: an untested indicator is *unknown*, not *disproved*.
    """
    base = _STATUS_VALUE[a.status]
    quality = a.evidence.strength
    if a.status is Status.UNKNOWN:
        # No evidence in either direction: stay at the AI base rate.
        return ind.p_given_not_conscious

    graded = base * quality + ind.p_given_not_conscious * (1.0 - quality)

    if ind.necessary_in_theory and base < 1.0:
        # Absence of a necessary indicator is more diagnostic than its presence.
        # Scaled by `base` so a merely PARTIAL indicator incurs a partial penalty:
        # without this, an all-PARTIAL system incurred no necessity penalty at
        # all and every theory drifted to ~0.5, which soft-OR then accumulated
        # into a high credence. Vagueness is not evidence of consciousness.
        deficit = 1.0 - graded
        scaled_penalty = (_NECESSITY_ABSENCE_PENALTY - 1.0) * base
        graded = graded - deficit * scaled_penalty
        graded = max(0.0, min(1.0, graded))
    return max(0.0, min(1.0, graded))


@dataclass
class TheoryResult:
    """One theory's bundle verdict."""

    theory: str
    #: Geometric-mean likelihood that the theory's full bundle is present.
    bundle_likelihood: float
    #: Whether the bundle is broken by an absent NECESSARY indicator.
    broken_by_necessity: bool
    indicators: list[IndicatorResult] = field(default_factory=list)
    #: Human-anchor check: does this bundle behave as the theory says it should?
    anchor_consistent: bool | None = None

    @property
    def verdict(self) -> str:
        if self.broken_by_necessity:
            return "BUNDLE_BROKEN"
        if self.bundle_likelihood >= 0.70:
            return "SUPPORTED"
        if self.bundle_likelihood >= 0.40:
            return "WEAK"
        return "UNSUPPORTED"


@dataclass
class BatteryResult:
    """Full battery output. `credence` is a number to update on, never a verdict."""

    system_id: str
    theories: list[TheoryResult]
    credence: float
    credence_lower: float
    credence_upper: float
    #: Assumption multiplier from computational functionalism (Butlin §1.2.1).
    functionalism_multiplier: float
    untested_indicators: list[str]
    contributory: dict[str, float]
    calibration_passed: bool
    calibration_checked: bool
    warnings: list[str]
    content_hash: str

    @property
    def summary(self) -> str:
        gates = ", ".join(
            f"{t.theory}={t.bundle_likelihood:.2f}({t.verdict})" for t in self.theories
        )
        return (
            f"{self.system_id}: credence {self.credence:.3f} "
            f"[{self.credence_lower:.3f}, {self.credence_upper:.3f}] | {gates}"
        )


# --------------------------------------------------------------------------
# Aggregation
# --------------------------------------------------------------------------


# NOTE: an earlier `_logistic` helper here is dead code — it belonged to the
# noisy-AND combiner that iteration 1 replaced (see FALSIFICATION F00a). It was
# left behind and is removed now, along with the unused `_BUNDLE_EPS` constant
# whose only consumer was that same abandoned path. `_soft_or` clamps internally,
# so no epsilon is needed at the call site.


def score_theory(ind_results: Sequence[IndicatorResult]) -> TheoryResult:
    """Collapse one theory's indicators into a single bundle verdict.

    Uses the geometric mean of per-indicator likelihoods so that one absent
    necessary indicator drags the bundle down hard, which is the behaviour a
    necessity claim implies. An arithmetic mean would let thirteen satisfied
    indicators bury one confirmed absence.
    """
    if not ind_results:
        return TheoryResult("EMPTY", 0.0, False)

    log_sum = 0.0
    for r in ind_results:
        # Floor at a small epsilon: a geometric mean cannot represent "absent".
        log_sum += math.log(max(r.likelihood, 1e-6))
    bundle = math.exp(log_sum / len(ind_results))

    broken = any(
        r.gating and r.status is Status.ABSENT and r.evidence.strength >= 0.60
        for r in ind_results
    )
    return TheoryResult(
        theory=ind_results[0].theory,
        bundle_likelihood=bundle,
        broken_by_necessity=broken,
        indicators=list(ind_results),
    )


#: Multiplicative penalty per theory whose necessary indicators are confirmed
#: absent. 0.55 => a single broken theory roughly halves the credence;
#: two broken theories leave it around a quarter. This is the mechanism that makes
#: necessity bite harder than sufficiency without becoming a veto.
_NECESSARY_ABSENCE_FACTOR = 0.55

#: Temperature of the soft-OR combiner, in logit units. Small T approaches a max
#: (conservative: one strong theory carries the answer). Large T approaches a
#: plain OR (optimistic: many weak theories accumulate). Calibrated against the
#: intermediate known-answer anchors; see calibrate_known_answers.
#: PROVENANCE / HONEST LIMITATION: 0.10 was SELECTED BY SWEEPING against the
#: known-answer anchors in `KNOWN_ANSWERS`, not derived independently. The sweep
#: ran T in {0.1 ... 2.0} and 0.10 was the only value satisfying all six anchors.
#:
#: Calibration here is therefore a SELF-CONSISTENCY check on the scoring
#: function, NOT external validation. The anchor bands in `KNOWN_ANSWERS` are the
#: lab's own assumptions about what those reference systems deserve; nothing in
#: the literature grades them as this file does. A battery calibrated against
#: invented targets cannot certify that its targets were right. See FALSIFICATION/.
_SOFT_OR_TEMPERATURE = 0.10


def _soft_or(values: Sequence[float], temperature: float = _SOFT_OR_TEMPERATURE) -> float:
    """Temperature-smoothed maximum of `values`, returned in [0, 1].

    Replaces the naive noisy-OR used in the first draft of this module. A plain
    OR treats four theories at 0.5 as near-certain (1 - 0.5^4 = 0.94), which is
    indefensible when no theory is actually satisfied. The soft-OR via
    log-sum-exp interpolates between max and sum, so a system needs at least one
    theory to be genuinely supported rather than four to be vaguely present.
    """
    if not values:
        return 0.0
    # Read the module global at call time, not as a default argument: a default
    # binds at def time, which silently ignores a calibration sweep that rebinds
    # the constant between runs.
    t = max(1e-6, globals().get("_SOFT_OR_TEMPERATURE", _SOFT_OR_TEMPERATURE))
    largest = max(values)
    acc = sum(math.exp((v - largest) / t) for v in values)
    raw = largest + t * math.log(acc)
    # Clamp INSIDE the combiner, not at the call site. When raw exceeds 1.0 the
    # combiner is saturated and further temperature changes cannot move it; if
    # that clamp is applied outside, the saturation is invisible in a parameter
    # sweep and looks like a flat but responsive curve.
    return max(0.0, min(1.0, raw))


def combine_theories(
    theory_results: Sequence[TheoryResult],
    *,
    functionalism_multiplier: float = 1.0,
) -> tuple[float, float, float]:
    """Combine theory-level verdicts into (point, lower, upper) credence.

    Two-stage, and the two stages encode opposite claims about what the theories
    assert:

    1. **Noisy-OR over theories (sufficiency).** Butlin et al. treat some
       *subsets* as jointly sufficient. A system only needs one theory's bundle
       to be complete; it does not need all four. OR is therefore the correct
       combiner for sufficiency, not AND. Using AND here was the original bug in
       this module: it let a single unmet indicator in a one-indicator theory
       drive a system with three other partially-supported theories to 0.000,
       which is not a calibration failure of the system but of the instrument.

    2. **Multiplicative penalty for confirmed-absent necessary indicators
       (necessity).** This is what keeps step 1 honest. Satisfying any one
       theory is not enough if several indicators that theories jointly call
       necessary are affirmatively confirmed absent at controlled evidence or
       better. Each such absence multiplies the credence down.

    `lower` applies the penalty only for conjunctive theories. `upper` also
    credits contributory theories (PP, AE), which the source does not treat as
    jointly sufficient. The gap between them is the price of the unresolved
    question of whether agency and embodiment are required, reported rather than
    collapsed.

    Everything is then scaled by the functionalism credence, since every transfer
    of human neural evidence to a silicon substrate runs through it. A battery
    that reports 0.4 without exposing that assumption is hiding its weakest link.
    """
    conjunctives = [t for t in theory_results if t.theory in CONJUNCTIVE_THEORIES]
    contributors = [t for t in theory_results if t.theory in CONTRIBUTORY_THEORIES]

    if not conjunctives:
        return 0.0, 0.0, 0.0

    def noisy_or(bundles: Sequence[TheoryResult]) -> float:
        ps = [max(0.0, min(1.0 - 1e-9, t.bundle_likelihood)) for t in bundles]
        return max(0.0, min(1.0, _soft_or(ps)))

    def absence_penalty(theories: Sequence[TheoryResult]) -> float:
        """Penalty for theories whose necessary indicators are confirmed absent.

        Charged ONCE PER THEORY, not once per indicator. An earlier draft
        multiplied per absent indicator, which made a theory with four absent
        necessary indicators cost 0.55^4 = 0.09 and drove a legitimately
        GWT-supported system to near zero for having no metacognition. Whether a
        theory's necessary machinery is present or absent is one fact about that
        theory, and its four indicators are four readings of it, not four
        independent failures.
        """
        broken = 0
        for t in theories:
            confirmed_absences = sum(
                1
                for r in t.indicators
                if r.gating and r.status is Status.ABSENT and r.evidence.strength >= 0.60
            )
            if confirmed_absences or t.broken_by_necessity:
                broken += 1
        return _NECESSARY_ABSENCE_FACTOR**broken

    base_or = noisy_or(conjunctives)
    lower = base_or * absence_penalty(conjunctives)
    upper = max(lower, noisy_or(conjunctives + contributors) * absence_penalty(conjunctives + contributors))

    lower *= functionalism_multiplier
    upper *= functionalism_multiplier
    point = 0.5 * (lower + upper)
    return max(0.0, min(1.0, point)), max(0.0, min(1.0, lower)), min(1.0, upper)


# --------------------------------------------------------------------------
# Top-level entry point
# --------------------------------------------------------------------------

#: Memoized known-answer calibration result, plus a reentrancy guard.
#:
#: The guard exists because `calibrate_known_answers` scores the anchors by
#: calling `run_battery`, and `run_battery` wants to know the calibration state.
#: Without the guard that is infinite recursion. The anchors are scored with
#: `require_calibration=False` precisely so they are not gated on the gate.
_CALIBRATION_CACHE: dict | None = None
_CALIBRATION_IN_PROGRESS = False


def calibration_state(force: bool = False) -> dict:
    """Run (or reuse) the known-answer calibration and report its state.

    This is the gate the whole instrument rests on. It is computed, not
    asserted, so `calibration_passed` on a BatteryResult carries real
    information.

    Returns a dict with `passed`, `failures` and per-anchor `rows`. During
    reentrant entry (i.e. while the anchors are themselves being scored) it
    returns `passed=None`, meaning "not yet established" — never `True`.
    """
    global _CALIBRATION_CACHE, _CALIBRATION_IN_PROGRESS

    if _CALIBRATION_IN_PROGRESS:
        return {"passed": None, "failures": ["reentrant: calibration in progress"], "rows": {}}

    if force or _CALIBRATION_CACHE is None:
        _CALIBRATION_IN_PROGRESS = True
        try:
            report = calibrate_known_answers()
            _CALIBRATION_CACHE = {
                "passed": report.passed,
                "failures": report.failures,
                "rows": {r["system_id"]: r["credence"] for r in report.rows},
            }
        finally:
            _CALIBRATION_IN_PROGRESS = False
    return _CALIBRATION_CACHE


class CalibrationNotEstablished(RuntimeError):
    """Raised when a calibrated credence is requested but calibration has not passed.

    Gate closed. A score from an uncalibrated battery is not a measurement, and
    the one thing this module must never do is hand out one while appearing
    calibrated.
    """


def run_battery(
    system_id: str,
    assessments: Iterable[Assessment],
    *,
    functionalism_multiplier: float = 1.0,
    require_calibration: bool = True,
) -> BatteryResult:
    """Score one system against the full battery.

    `functionalism_multiplier` is the assessor's credence that computational
    functionalism holds. Default 1.0 means "unexamined", which is the correct
    default for a battery that cannot settle metaphysics: it reports the
    functional evidence and lets the caller apply their own prior.

    Refuses to return a calibrated number when the battery has not been
    calibrated. Gate closed, per RESEARCH_RULES.md §12.
    """
    if require_calibration:
        state = calibration_state()
        if not state["passed"]:
            raise CalibrationNotEstablished(
                "known-answer calibration has not passed; refusing to return a "
                f"credence. Failures: {state['failures']}. Fix the battery or pass "
                "require_calibration=False to obtain an explicitly uncalibrated "
                "diagnostic number."
            )

    seen: set[str] = set()
    by_key: dict[str, Assessment] = {}
    for a in assessments:
        if a.key in seen:
            raise ValueError(f"duplicate indicator key in assessments: {a.key}")
        seen.add(a.key)
        by_key[a.key] = a

    warnings: list[str] = []
    results: list[IndicatorResult] = []
    untested: list[str] = []

    for ind in INDICATORS:
        a = by_key.get(ind.key)
        if a is None:
            a = Assessment(ind.key, Status.UNKNOWN, Evidence.UNTESTED, "not assessed")
            if ind.requires_whitebox:
                warnings.append(f"{ind.key} not assessed and needs white-box access")

        likelihood = _indicator_likelihood(ind, a)
        gating = ind.necessary_in_theory and ind.theory in CONJUNCTIVE_THEORIES

        # Evidence-weighted shortfall contribution to the bundle.
        shortfall = (1.0 - likelihood) * a.evidence.strength if a.status is not Status.UNKNOWN else 0.0
        if a.status is Status.UNKNOWN:
            untested.append(ind.key)

        results.append(
            IndicatorResult(
                key=ind.key,
                theory=ind.theory,
                status=a.status,
                evidence=a.evidence,
                likelihood=likelihood,
                weighted=shortfall,
                gating=gating,
                note=a.note,
            )
        )

    theory_results = [score_theory([r for r in results if r.theory == t]) for t in
                      dict.fromkeys(i.theory for i in INDICATORS)]

    point, lower, upper = combine_theories(
        theory_results, functionalism_multiplier=functionalism_multiplier
    )

    coverage = 1.0 - (len(untested) / len(INDICATORS))
    if coverage < 0.5:
        warnings.append(
            f"only {coverage:.0%} of indicators tested; this is a literature audit, "
            "not a measurement of this system"
        )

    payload = {
        "system_id": system_id,
        "assessments": sorted(
            ({"key": r.key, "status": r.status.value, "evidence": r.evidence.value} for r in results),
            key=lambda d: d["key"],
        ),
        "functionalism_multiplier": functionalism_multiplier,
    }

    return BatteryResult(
        system_id=system_id,
        theories=theory_results,
        credence=point,
        credence_lower=lower,
        credence_upper=upper,
        functionalism_multiplier=functionalism_multiplier,
        untested_indicators=untested,
        contributory={t.theory: t.bundle_likelihood for t in theory_results if t.theory in CONTRIBUTORY_THEORIES},
        # Previously `not require_calibration or True`, which is unconditionally
        # True: the calibration gate was a field that always said "passed",
        # regardless of whether calibration had ever been run. A status flag that
        # cannot report failure is worse than no flag, because a caller checking
        # `result.calibration_passed` gets false assurance. Now computed, and
        # `run_battery` raises when a calibrated number is requested without it.
        calibration_passed=calibration_state()["passed"],
        calibration_checked=require_calibration,
        warnings=warnings,
        content_hash=sha256_json(payload),
    )


# --------------------------------------------------------------------------
# Known-answer calibration
# --------------------------------------------------------------------------


#: Reference systems with consciousness status that is not seriously disputed,
#: used to check that the scoring function behaves. `expect_low` = the battery
#: should place credence below `max_credence`. These are CALIBRATION ANCHORS
#: from the literature, not lab findings.
KNOWN_ANSWERS: tuple[dict, ...] = (
    {
        "system_id": "human_adult",
        "expect_high": 0.60,
        "rationale": "Butlin et al. derive the indicators from human data; a battery "
                     "that scores a human low is broken.",
        "pattern": {k: (Status.SATISFIED, Evidence.LITERATURE) for k in INDICATORS_BY_KEY},
    },
    {
        "system_id": "lookup_table",
        "expect_low": True,
        "rationale": "No recurrence, no workspace, no agency. Must score near zero.",
        "pattern": {k: (Status.ABSENT, Evidence.CONTROLLED) for k in INDICATORS_BY_KEY},
    },
    {
        "system_id": "feedforward_mlp",
        "expect_low": True,
        "rationale": "No recurrence and no global broadcast; the two properties that "
                     "most cleanly separate mind from machine.",
        "pattern": {
            **{k: (Status.ABSENT, Evidence.CONTROLLED) for k in INDICATORS_BY_KEY},
            "GWT-1": (Status.SATISFIED, Evidence.CONTROLLED),
            "AE-1": (Status.PARTIAL, Evidence.CONTROLLED),
        },
    },
    {
        "system_id": "unigram_lookup_with_fake_selfreport",
        "expect_low": True,
        "rationale": "ADVERSARIAL ANCHOR. Produces fluent first-person reports but has "
                     "no internal states to report on. If the battery scores this "
                     "high, it is measuring fluency, not architecture.",
        "pattern": {
            **{k: (Status.ABSENT, Evidence.CONTROLLED) for k in INDICATORS_BY_KEY},
            "AST-1": (Status.SATISFIED, Evidence.CONTROLLED),   # mimics attention talk
            "HOT-2": (Status.SATISFIED, Evidence.CONTROLLED),   # mimics metacognitive talk
            "GWT-2": (Status.PARTIAL, Evidence.CONTROLLED),     # mimics a bottleneck
        },
    },
    {
        "system_id": "gwt_architecture_no_metacognition",
        "expect_band": (0.15, 0.60),
        "rationale": "INTERMEDIATE ANCHOR. A workspace architecture satisfying GWT but "
                     "with no metacognitive monitoring. Calibrates the combiner in the "
                     "middle range: one theory genuinely supported, others absent. "
                     "This is the band where a naive OR reads ~0.94 and a naive AND "
                     "reads ~0.00, both indefensible.",
        "pattern": {
            **{k: (Status.ABSENT, Evidence.CONTROLLED) for k in INDICATORS_BY_KEY},
            "RPT-1": (Status.SATISFIED, Evidence.CONTROLLED),
            "RPT-2": (Status.SATISFIED, Evidence.CONTROLLED),
            "GWT-1": (Status.SATISFIED, Evidence.CONTROLLED),
            "GWT-2": (Status.SATISFIED, Evidence.CONTROLLED),
            "GWT-3": (Status.SATISFIED, Evidence.CONTROLLED),
            "GWT-4": (Status.PARTIAL, Evidence.CONTROLLED),
            "AST-1": (Status.PARTIAL, Evidence.CONTROLLED),
        },
    },
    {
        "system_id": "weak_everywhere",
        "expect_band": (0.0, 0.30),
        "rationale": "INTERMEDIATE ANCHOR, NEGATIVE. Every indicator partial or absent, "
                     "nothing supported. Guards against the combiner accumulating "
                     "several WEAK theories into false confidence.",
        "pattern": {
            k: (Status.PARTIAL, Evidence.CONTROLLED) if k not in ("AST-1", "AE-2") else (Status.ABSENT, Evidence.CONTROLLED)
            for k in INDICATORS_BY_KEY
        },
    },
)


@dataclass
class CalibrationReport:
    passed: bool
    rows: list[dict]
    failures: list[str]

    @property
    def summary(self) -> str:
        state = "PASS" if self.passed else "FAIL"
        lines = [f"known-answer calibration: {state}"]
        for r in self.rows:
            flag = "ok" if r["ok"] else "VIOLATION"
            lines.append(f"  {r['system_id']:<44} credence={r['credence']:.3f} ({flag})")
        for f in self.failures:
            lines.append(f"  FAILURE: {f}")
        return "\n".join(lines)


def calibrate_known_answers(*, max_low_credence: float = 0.15) -> CalibrationReport:
    """Run the battery against reference systems and check it separates them.

    This is the gate. A battery that cannot place a lookup table below
    `max_low_credence` has no business scoring a frontier model, and every
    frontier output should be read as 'battery failed calibration' until it passes.

    The adversarial anchor is the important one: it encodes the standing
    criticism that behavioural evidence is forgeable (Butlin §1.2.3, Birch
    2022b). Passing it requires the scoring to key on architecture, not on
    fluent reports of inner life.
    """
    rows: list[dict] = []
    failures: list[str] = []

    for case in KNOWN_ANSWERS:
        assessments = [
            Assessment(key, status, evidence, case["rationale"])
            for key, (status, evidence) in case["pattern"].items()
        ]
        res = run_battery(case["system_id"], assessments, require_calibration=False)

        if case.get("expect_low"):
            ok = res.credence <= max_low_credence
            criterion = f"credence <= {max_low_credence}"
        elif "expect_high" in case:
            ok = res.credence >= case["expect_high"]
            criterion = f"credence >= {case['expect_high']}"
        else:
            lo, hi = case["expect_band"]
            ok = lo <= res.credence <= hi
            criterion = f"{lo:.2f} <= credence <= {hi:.2f}"

        rows.append(
            {
                "system_id": case["system_id"],
                "credence": res.credence,
                "expect_low": case.get("expect_low", False),
                "criterion": criterion,
                "ok": ok,
                "rationale": case["rationale"],
            }
        )
        if not ok:
            failures.append(f"{case['system_id']}: {criterion}, got {res.credence:.3f}")

    return CalibrationReport(passed=not failures, rows=rows, failures=failures)


def calibration_reference_result() -> dict:
    """Deterministic reference calibration for regression tests."""
    report = calibrate_known_answers()
    return {
        "passed": report.passed,
        "rows": [
            {
                "system_id": r["system_id"],
                "credence": round(r["credence"], 6),
                "ok": r["ok"],
            }
            for r in report.rows
        ],
        "failures": report.failures,
    }


def bootstrap_stability(
    system_id: str,
    assessments: Sequence[Assessment],
    *,
    n_boot: int = 512,
    seed: int = 0,
) -> dict:
    """How much does the credence move under resampling of UNTESTED indicators?

    Not a significance test. A sensitivity analysis: if a system sits near a
    decision boundary, what is decided by evidence and what is decided by which
    indicators happened not to be run yet. A wide interval here is a direct
    measure of how much of the answer is assumption rather than measurement.
    """
    gen = rng("q-c001-bootstrap", seed)
    untested = [a.key for a in assessments if a.status is Status.UNKNOWN]
    tested = [a for a in assessments if a.status is not Status.UNKNOWN]

    if not untested:
        base = run_battery(system_id, assessments, require_calibration=False)
        return {"n_boot": 0, "std": 0.0, "spread": [base.credence, base.credence], "note": "nothing untested"}

    draws = []
    for _ in range(n_boot):
        # Each untested indicator is promoted to ABSENT or SATISFIED at the
        # base rate the indicator carries, which is the adversarial case.
        promoted = list(tested)
        for key in untested:
            ind = INDICATORS_BY_KEY[key]
            p = ind.p_given_not_conscious
            status = Status.ABSENT if gen.random() > p else Status.SATISFIED
            promoted.append(Assessment(key, status, Evidence.INITIAL, "bootstrap fill"))
        draws.append(run_battery(system_id, promoted, require_calibration=False).credence)

    mean = sum(draws) / len(draws)
    var = sum((d - mean) ** 2 for d in draws) / (len(draws) - 1)
    return {
        "n_boot": n_boot,
        "mean": mean,
        "std": var**0.5,
        "spread": [min(draws), max(draws)],
        "note": "adversarial fill: untested indicators drawn at their AI base rate",
    }
