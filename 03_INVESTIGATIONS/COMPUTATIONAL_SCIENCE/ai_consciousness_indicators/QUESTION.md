# Q-C001 — Can an indicator battery bound AI consciousness credence?

**Status:** `INVESTIGATING` (instrument built and calibrated; no system scored as a finding)

## The question

Can a preregistered, falsifiable battery derived from neuroscientific theories of
consciousness produce a *defensible number* for how likely a given AI system is to
be phenomenally conscious — and can that battery be shown to behave correctly
before it is pointed at a frontier model?

This splits into two questions, deliberately:

- **Q-C001a (instrument).** Does the scoring function separate reference systems
  whose consciousness status is not in dispute? An instrument that cannot place a
  lookup table below a human is not measuring anything.
- **Q-C001b (application).** What does the battery say about specific systems?

## Why this is not a checklist

The obvious approach scores 14 indicators and counts the satisfied ones. That is
wrong in a way that inflates results, and this investigation refuses to do it.

Butlin et al. do not claim "N of 14 satisfied ⇒ conscious". They claim some
*subsets* are jointly sufficient, and that each indicator is necessary *according
to at least one theory*. A count cannot handle three things:

1. **Intra-theory correlation.** RPT-1 and RPT-2 come from one theory about one
   mechanism. Counting them twice double-counts evidence.
2. **Inter-theory non-independence.** Theories are not independent hypotheses.
   Satisfying GWT-2 typically yields GWT-3 nearly free.
3. **Necessity ≠ sufficiency.** Failing one indicator of a theory that treats it as
   necessary is far more informative than satisfying the other thirteen.

So aggregation runs in two stages: collapse indicators within a theory, then
combine theory-level verdicts. See `CODE/battery.py` module docstring.

## What the battery outputs

A **credence with an interval**, a decomposition by theory, an untested-indicator
list, and warnings. Never a boolean. A verdict computed from UNTESTED evidence is
returned as UNTESTED — the `Assessment` dataclass raises rather than let an
untested indicator claim to be satisfied.

## Layer discipline (RESEARCH_RULES.md §1)

Per RESEARCH_RULES §1, everything produced here is **Layer 1 (instrument/measurement
result)** at most. This investigation has produced:

- a working, tested, calibrated scoring function — Layer 1
- the finding that three plausible aggregator designs were wrong — Layer 1/2 about
  *the instrument*, not about consciousness

It has produced **no** Layer 3 physical/scientific claim about whether any AI system
is conscious. Doing so would require Layer 2 statistics on real systems, which
requires white-box access the lab does not have.

## Current state

See `REPORT/TECHNICAL_SUMMARY.md` for the aggregator bugs found and fixed, and
`REPORT/PLAIN_ENGLISH_SUMMARY.md` for the short version.

`CONFIG/prereg_EXP-C001.json` freezes the calibration result that was measured
before any system was scored.