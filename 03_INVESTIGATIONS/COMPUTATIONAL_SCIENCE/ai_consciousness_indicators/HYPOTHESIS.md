# HYPOTHESIS

## HYP-C001

**Statement.** A scoring function over the 14 Butlin et al. (2023) indicator
properties, aggregating by theory rather than by count, can be constructed such
that it (a) ranks a human adult above a lookup table, (b) is not materially
raised by a system that merely produces fluent first-person reports, and (c)
produces a bounded credence with a decomposable interval — and that these
properties are *measurable* against reference systems before the battery is
applied to any frontier model.

**Type.** Instrument claim. About the measurement apparatus, not about
consciousness in any system.

**Not claimed.** That this battery determines whether any AI system is conscious.
That any system scored here is or is not conscious. That the aggregator's
structure is the correct way to combine neuroscientific indicator evidence — only
that this particular aggregator is internally coherent and correctly ordered on
reference systems.

## Why "not claimed" is written this way

The obvious failure mode for a project like this is to end up with a confident
number about AI consciousness that nobody earned. Three specific commitments
prevent it here:

1. **No boolean output.** `run_battery` returns a credence, an interval, a
   per-theory decomposition, and the list of untested indicators. There is no
   function that returns `is_conscious`.

2. **UNTESTED cannot masquerade as SATISFIED.** The `Assessment` dataclass
   raises `ValueError` if a satisfied or partial claim carries no evidence, and
   raises again if an untested claim claims non-untested evidence.

3. **The gate is calibration, not the score.** If the battery fails its
   known-answer calibration, its frontier scores mean nothing — regardless of
   how low or high they are. The gate is checked before use, not after.

## Falsification conditions

HYP-C001 is **falsified** if any of the following is observed:

- **F1.** A system with all indicators ABSENT scores credence ≥ 0.15.
- **F2.** A system with all indicators SATISFIED scores credence < 0.60.
- **F3.** The adversarial anchor (fluent self-reports, no internal states)
  exceeds 0.15 credence. *This is the load-bearing one.* Failing it would mean
  the battery measures fluency rather than architecture.
- **F4.** Removing a theory's indicators changes its bundle verdict not at all
  (aggregation ignoring its own inputs).
- **F5.** Credence falls outside [0, 1] for any input.
- **F6.** The same inputs produce different credences across runs
  (non-determinism).

## Status

`SURVIVED_CONTROLS` for the instrument claim: F1–F6 checked in
`TESTS/test_battery.py` (19 tests, all passing), plus the six-anchor calibration
gate in `calibrate_known_answers`.

**Held at Layer 1** (RESEARCH_RULES.md §1). No claim about any AI system.

## Known limitation, stated up front

The soft-OR temperature `_SOFT_OR_TEMPERATURE = 0.10` was **chosen by sweeping**
against the lab's own anchor set. The anchor bands are the lab's own assumptions.
So the calibration is a self-consistency check, not external validation — see
`FALSIFICATION/F00_F01_F02_F03_F04_kill_attempts.md` (entry F01). Passing F1–F6
means the instrument is internally coherent. It does not mean the anchors were
right.