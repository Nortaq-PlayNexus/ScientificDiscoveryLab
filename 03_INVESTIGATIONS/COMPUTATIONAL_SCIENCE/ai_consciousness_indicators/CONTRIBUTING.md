# Contributing

Thanks for looking. This project is deliberately narrow, and contributions that
respect that narrowness are the useful ones.

## What this project is

A measurement instrument for AI consciousness assessment, plus a robustness
analysis of that instrument. It scores **no AI systems** and claims nothing about
whether any system is conscious.

## What would genuinely help

Ordered by how much it would improve the work.

### 1. Independent calibration anchors

**This is the single most valuable contribution available.**

The project's central unresolved problem is that `_SOFT_OR_TEMPERATURE` was
chosen by sweeping against reference anchors whose bands the authors also
invented. Passing calibration is self-consistency, not correctness. Nobody
outside this project can currently check whether the anchors are right.

Useful forms:

- **Elicited credences.** Ask consciousness researchers who did not build this
  battery to place credences on the six anchors in `battery.KNOWN_ANSWERS`,
  independently. Even a small sample would be worth more than any further
  parameter tuning.
- **Disagreement is data.** If experts disagree with the bands, that disagreement
  is the finding. Please report spread, not a consensus.
- **Biological anchors with contested status.** Running the battery against
  systems where partial disagreement is the point would test it harder than any
  synthetic anchor.

### 2. An independent reimplementation

`REPLICATION` and `INDEPENDENT METHOD` in the lab protocol are explicitly not
reached — there is exactly one scoring implementation. A second implementation
written from the paper rather than from this code would be a genuine test.

If you write one, please do **not** look at `battery.py` first. The value is in
implementing from the description.

### 3. Alternative aggregators

The four aggregators in `CHANGELOG.md` are the ones we happened to try. Others
exist. In particular:

- **Dirichlet perturbation** over all indicator weights simultaneously, rather
  than the uniform shifts in `perturbation.py`. The current version perturbs
  priors independently and so cannot sample *correlated* miscalibration, which may
  be the worse failure mode.
- **Interval-valued indicators.** Currently `PARTIAL` is a fixed 0.5. Real
  partial satisfaction is probably graded.
- **Explicit model of theory dependence.** The current soft-OR treats theories as
  peers with a tunable temperature. `Bayne et al.` and the IIT controversy suggest
  the right weighting is not flat and not a single scalar.

### 4. Extending the adversarial anchors

The most valuable control in the suite is the fluent-liar anchor. More variants
would test the battery harder:

- A system trained (via fine-tuning) to *genuinely* self-report accurately. This
  is the sharp case — the battery currently cannot distinguish *earned*
  introspection from *installed* introspection, and that limit is real.
- A system that reports inner states in a non-linguistic format, to test whether
  the battery's textual bias matters.

## What would not help

- **Scores for specific frontier models.** Not without white-box evidence. A
  number produced from literature summaries is a number about the literature.
- **A different weighting constant, re-swept against our anchors.** This tightens
  the circularity rather than loosening it.
- **Speculation about whether AI is conscious.** The project is built to make
  that question tractable, not to answer it by assertion.
- **Turing-test variants.** The upstream framework rejects that route explicitly,
  for good reason.

## Ground rules

These come from the laboratory protocol this was built under, and they are load-
bearing rather than ceremonial:

1. **Report failures, including your own.** Every broken aggregator and every
   broken test in this repo is documented in `FALSIFICATION/` and `CHANGELOG.md`
   rather than deleted. Please match that.
2. **Preregister before running.** If you add an experiment, freeze the decision
   rule first (`CONFIG/`).
3. **Never promote a claim a layer.** An instrument result is not a finding about
   the world. See `RESEARCH_RULES.md` §1 in the parent lab, or the summary in
   `EXPERIMENT_PLAN.md`.
4. **Label untested things as untested.** `battery.Assessment` raises if you try
   to record `SATISFIED` with no evidence. Please don't route around it.
5. **Determinism.** All randomness goes through `rng(label, seed)`. Never use
   Python's `hash()`, which is salted per process.

## Dev setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

48 tests, ~5 seconds. No GPU, no network.

## A note on tone

This project touches a question people have strong feelings about, and a fair
amount of writing about it is either promotional or dismissive. The standard here
is different: **state what was measured, state what survived the controls, state
what is assumed, and refuse to state a verdict.** The limitation sections are not
hedging — they are the result.

If you find something wrong, say so plainly. That is the whole point of shipping
the falsification log.

## License

MIT. See `LICENSE`. The upstream indicator paper is CC BY-NC-SA 4.0; please cite
it and do not reproduce its text beyond attributed quotation for identification.