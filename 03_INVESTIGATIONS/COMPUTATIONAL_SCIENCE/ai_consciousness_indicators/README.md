# A calibrated indicator battery for AI consciousness

**And what survives perturbing every discretionary choice in it.**

![Calibration](https://img.shields.io/badge/calibration-6%2F6%20anchors%20PASS-brightgreen)
![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.XXXXXXX-lightgrey)
![Robustness](https://img.shields.io/badge/robustness-3000%20joint%20perturbations-blue)
![Tests](https://img.shields.io/badge/tests-38%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Systems scored](https://img.shields.io/badge/AI%20systems%20scored-zero-lightgrey)
![Claim layer](https://img.shields.io/badge/claim%20layer-L1%20instrument-lightgrey)

A measurement instrument for asking *"how likely is this AI system to be
phenomenally conscious?"* — built from the 14 indicator properties derived from
neuroscience by [Butlin, Long et al. (2023)](https://arxiv.org/abs/2308.08708),
then stress-tested to find out how much of its output is real and how much is
tuning.

> **This is not a test that says whether an AI is conscious.**
> No AI system was scored. No claim is made about whether any system — human,
> animal, or machine — is conscious. What follows is a working instrument and a
> report on its own failure modes.

---

## Why this exists

In 2023, nineteen researchers including Yoshua Bengio and David Chalmers took the
leading neuroscientific theories of consciousness — global workspace, recurrent
processing, higher-order, predictive processing, attention schema — and converted
each into concrete, checkable properties a computer might have. Fourteen
"indicator properties" in total. It became the reference framework for the field
(peer-reviewed in *Trends in Cognitive Sciences* 30(6), 2026).

The obvious thing to do is score 14 indicators and count the ticks.

**That is wrong**, and this project exists to show why, with executable evidence.

---

## The core design decision

Butlin et al. do not claim "N of 14 satisfied ⇒ conscious." They claim some
*subsets* are jointly **sufficient**, and that each indicator is necessary
*according to at least one theory*. A count cannot handle three consequences:

1. **Intra-theory correlation.** `RPT-1` and `RPT-2` come from one theory about
   one mechanism. Counting them twice is double-counting evidence.
2. **Inter-theory non-independence.** Theories aren't independent hypotheses.
   Satisfying `GWT-2` typically yields `GWT-3` nearly free.
3. **Necessity ≠ sufficiency.** Failing one indicator a theory calls necessary is
   far more informative than satisfying the other thirteen.

So aggregation runs in two stages:

```
14 indicators  ──►  collapse WITHIN each theory  ──►  6 theory verdicts
                                                          │
                                     combine across theories (soft-OR)
                                                          ▼
                                    credence + interval + decomposition
```

Output is a **credence with an interval**, a per-theory breakdown, and an explicit
list of untested indicators. There is no function that returns
`is_conscious`, and an `UNTESTED` indicator cannot be recorded as `SATISFIED` —
the dataclass raises.

---

## The interesting part: what broke

We built four aggregators. **Three of them were wrong**, and the calibration
anchors caught all three:

| Design | Symptom | Why it was wrong |
|---|---|---|
| noisy-AND across theories | plausible modern AI scored **0.000** | Source says *sufficient* subsets, not necessary ones — one unmet indicator shouldn't veto everything |
| plain noisy-OR | system with nothing established scored **0.507** | `1 − 0.5⁴ = 0.94`. Vagueness accumulates into false confidence |
| penalty per indicator | valid workspace architecture scored **0.092** | `0.55⁴` treats four readings of *one fact* as four independent failures |
| necessity penalty on ABSENT only | all-PARTIAL system scored **0.550** | Partial support accrued full credit — vagueness looked like evidence |

Every failure landed **in the middle of the range the battery exists to measure**.
A counting checklist would have shipped all four silently.

We also found **five gate-logic bugs** — in the *tests*, not the battery:

- a per-indicator penalty, a default argument binding at def-time, an
  `if "key" in dict` where truthiness was meant
- an `EXPECTED_ORDER` missing one anchor, so the ordering gate compared a
  six-element list to a five-element tuple and reported **0.0000** — its own bug,
  reported as a falsification
- a verdict keyed on `all_gates_pass`, which discarded a robust result because a
  fragile one failed

That last pattern matters more than any single bug: **we have no systematic way to
check that our gates themselves run.** Both experiments now assert it.

---

## Known-answer calibration (the gate)

A battery nobody calibrated isn't an instrument. Before scoring anything, the
scoring function must separate reference systems whose status isn't disputed:

| Anchor | Expected | Why it's in the set |
|---|---|---|
| `human_adult` | ≥ 0.60 | The indicators come from human data. Scoring a human low means the battery is broken. |
| `lookup_table` | ≤ 0.15 | No recurrence, no workspace, no agency. |
| `feedforward_mlp` | ≤ 0.15 | No recurrence, no broadcast. |
| **`unigram_lookup_with_fake_selfreport`** | **≤ 0.15** | **Adversarial.** Fluent first-person inner-life talk, zero internal states. |
| `gwt_architecture_no_metacognition` | 0.15–0.60 | Calibrates the mid-range, where naive OR *and* naive AND both fail. |
| `weak_everywhere` | 0.00–0.30 | Guards against weak theories accumulating into confidence. |

**All six pass.** The adversarial anchor is the load-bearing one: if a system can
score well merely by *talking* about inner life, every downstream conclusion is
void.

---

## Robustness: ranking survives, absolute numbers don't

F01 was the worst problem with this work — the aggregation temperature was chosen
by sweeping against the same six anchors we then validated against, whose bands
we ourselves invented. Passing calibration was therefore **self-consistency, not
correctness**.

So we perturbed **all six** discretionary parameter families jointly (3,000
draws, two regions, including temperature 0.02–3.0 and evidence-quality scales
that *invert* the intended `CONTROLLED > REPLICATED` ordering):

| Gate | Plausible region | Aggressive region |
|---|---|---|
| exact ordering holds | **1.0000** | 0.6680 |
| **fluent-liar never beats human** | **1.0000** | **1.0000** |
| absolute 0.30 ceiling holds | 0.9753 | 0.7907 |

**The asymmetry is the result.**

*Ranking is robust. Absolute probabilities are not.* In the aggressive region the
adversarial anchor's 5th–95th percentile is **[0.025, 0.491]** — it genuinely
crosses its ceiling. So "fluent systems stay below 0.15" is **not** safe.

But across every parameter setting tried, **no sample ever let a system that
merely performs introspection outscore the human.** That is the claim the battery
exists to make, and it survived everything we threw at it.

**What this authorises:** ranking systems scored under identical assumptions.
**What it does not:** quoting an absolute probability that anything is conscious.

---

## Honest limitations

These are load-bearing, not disclaimers.

1. **The calibration is circular.** The temperature was picked to satisfy our own
   invented anchors. Passing proves internal consistency, *not* correctness.
   Nothing inside this experiment can detect it, because those assumptions are
   the only source of truth in use. **This is unsolved** — see
   [`FALSIFICATION/F00_F01_F02_F03_F04_kill_attempts.md`](FALSIFICATION/F00_F01_F02_F03_F04_kill_attempts.md).
2. **The robustness result is conditional** on the same anchor assignments. It
   bounds how much the circularity matters; it does not resolve it.
3. **Evaluation-awareness is unfixable offline.** Work published in 2026 found
   that ablating representations of *"this is a fake scenario"* caused a model to
   act on a test it otherwise refused. If a system detects it's being assessed,
   the score describes the *assessed* system, not the deployed one.
4. **Nothing here is white-box evidence.** The strongest relevant result in the
   literature — the "J-space" workspace finding — was read, not reproduced. No
   model internals were measured.
5. **Phenomenal experience is out of reach by construction.** The battery reports
   evidence about *access* consciousness. Whether access implies experience is
   contested philosophy, not a measurement.
6. **Single implementation.** `REPLICATION` and `INDEPENDENT METHOD` are
   explicitly not reached.
7. **Priors are estimates.** Every `p_given_conscious` and `p_given_not_conscious`
   was assigned by hand from the literature narrative.

The original authors state the core caveat themselves: satisfying all 14
indicators **would still not mean** a system is definitely conscious.

---

## Install & run

```bash
git clone https://github.com/Nortaq-PlayNexus/consciousness-indicator-battery.git
cd consciousness-indicator-battery
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest -q          # 48 tests, ~5s
```

No GPU. No network. No model weights. Python 3.11+.

Reproduce the headline numbers:

```python
from battery import calibrate_known_answers
from perturbation import compare_regions

print(calibrate_known_answers().summary)

result = compare_regions(seed=0)
print(result["verdict"])
print(result["verdict_detail"]["load_claim_FB_holds_both"])  # -> True
```

Everything is deterministic: all randomness flows through a sha256-derived
`numpy.Generator` keyed on `(label, seed)`, never Python's salted builtin `hash`.

---

## Repository layout

```
battery.py                    scoring, two-stage aggregation, calibration gate
perturbation.py               EXP-C003: joint robustness sweep
_rng.py                       deterministic RNG (standalone fallback)
test_battery.py               19 instrument tests: validation, calibration,
                              falsification, symmetry, determinism
test_perturbation.py          11 robustness tests for EXP-C003
test_calibration_gate.py      10 regression tests for F08-F10
test_standalone.py            8 tests: clean-install parity, hash integrity
experiment_verify.py          SHA-256 verifier for RESULTS/*.json
tools/regenerate_results.py   rebuild RESULTS/*.json after a code change
RESULTS/experiment.json       EXP-C001 result + canonical-JSON SHA-256
RESULTS/experiment_C003.json  EXP-C003 result + SHA-256
CONFIG/prereg_EXP-C001.json   constants frozen before scoring, incl. the
                              known circularity recorded up front
FALSIFICATION/                4 broken aggregator designs, 7 verifier
                              defects (F08-F11 in a separate file),
                              2 unresolved confounds
REPORT/                       technical + plain-English summaries
```

## Relationship to the source lab

These files are a self-contained copy. When the same code runs inside a larger
laboratory checkout, it prefers that checkout's shared RNG engine and falls back
to `_rng.py` here. `test_standalone.py` asserts the two produce **bit-identical**
streams, so a recorded hash does not depend on which implementation ran.

---

## Reproducibility

Every run records seed, parameters, software versions, machine info, and a
SHA-256 over a canonical JSON encoding of the result. The hash scope is declared
explicitly so an in-memory hash can't be confused with a formatted artifact hash.

Verify the whole thing reproduces with no dependency on any outside library:

```bash
python verify_clean_room.py    # copies to a temp dir, re-runs tests + hashes
python experiment_verify.py RESULTS/experiment.json RESULTS/experiment_C003.json
```

The Zenodo deposit archive is byte-reproducible — rebuilding on an unchanged tree
yields an identical SHA-256, so the checksum recorded in `RELEASE.md` stays
valid:

```bash
python zenodo/build_zenodo_package.py   # stages, verifies, builds, prints ARCHIVE VERIFIED
```

Programmatic use:

```python
from experiment_verify import verify_experiment_result_hash
```

## Methodology

Built to a preregistered laboratory standard (claim layering, mandatory controls,
kill-the-hypothesis, evidence grading, append-only registries, nulls recorded not
deleted). The full protocol and every failure are in `CHANGELOG.md`,
`EXPERIMENT_PLAN.md`, and `FALSIFICATION/`.

## Citation

See [`CITATION.cff`](CITATION.cff). Please cite both this work and the indicator
framework. This is an independent implementation and is **not** affiliated with or
endorsed by the original authors.

## License

MIT — see [`LICENSE`](LICENSE). The upstream indicator paper is CC BY-NC-SA 4.0;
this repository contains no copied text from it beyond citation and short
attributed quotations used for identification.

## The honest one-paragraph version

We built a rigorous, gated instrument for measuring AI consciousness, then
admitted the instrument's own calibration is circular. We found and fixed five
bugs in the *instrument* and five in our *tests*. We proved the ordering of
systems is robust to arbitrary parameter choices while absolute probabilities are
not. We scored no AI systems and claim nothing about whether any of them is
conscious. The next real step is not more code — it is getting calibration
anchors from researchers who didn't build this thing.