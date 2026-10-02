# Contributing

## Read this first

`AUDIT/DO_NOT_CLAIM.md` and `CURRENT_STATUS.md` exist because this laboratory has
produced results that are easy to misread. **No physics discovery is claimed
anywhere.** Several experiments failed, and those failures are documented as
findings rather than deleted. If you are about to write a summary, read those two
files before you do.

## What this repository is

The full laboratory record: code, preregistrations, results, reports, audit
trails and registries across seven investigation areas. `zenodo-deposit/` is a
preserved curated subset; it is a different scope, not an older draft.

## The rules that are not negotiable

These come from `RESEARCH_RULES.md` and are load-bearing, not decorative.

1. **Claim layers.** Every result sits at one of four layers (instrument →
   statistical → physical claim → novelty). Never describe a result one layer
   above what the evidence supports.
2. **Preregister before running.** Freeze the decision rule in `CONFIG/` first.
   If you change it afterwards, log it as a hypothesis change, not silently.
3. **Raw data is read-only.** Fix a bug in code; never edit a recorded result.
4. **Nulls are results.** A failed replication gets recorded with the same care
   as a success.
5. **Controls are mandatory.** Every experiment implements the control suite in
   `RESEARCH_RULES.md` §3. A result that disappears under a control is recorded
   as having disappeared.
6. **No baseline refreshes.** An immutable audit baseline may not be regenerated
   to make a failing test pass. This is the exact defect the
   `AUDIT_REPAIR_N04…` investigation exists to prevent.

## Known gaps in a clean checkout

Raw simulation data (`.npz`, `.sqlite3` — 377 MB, regenerable from the seeds
recorded in each preregistration) is excluded from the published tree, and the
read-only audit suite reads some of it. Those tests **fail closed** here with
`required historical evidence is missing`. That is correct behaviour: the audit
refuses to run without the exact bytes it was audited against. CI asserts that
every failure carries that cause and nothing else.

- Laboratory with full data: **543 passed, 0 failed**
- Published tree: fewer, and the difference is accounted for by cause

## A floating-point trap you will hit

Several historical tests assert exact float equality between a value recomputed
from stored cells and the same value as persisted JSON. **That cannot hold.** A
JSON round-trip plus resummation over a 24 960-row table differs in the last few
digits. See `CHANGELOG_TEST_TOLERANCE_REPAIR.md` (N-29) for the seven repaired
assertions and the two that were genuine findings rather than tolerance issues.

When you write a tolerance, separate two questions:

1. *Did the quantity change?* — bounded tolerance, chosen from what was observed
2. *Does the conclusion still hold?* — asserted independently and exactly

Asserting only (1) with `== 0.0` produces a test that rejects correct answers
and invites someone to loosen a number which should stay tight.

## What would help

- **An independent implementation** of any published estimator. Several results
  currently rely on the same stream; `SAME_STREAM_IMPLEMENTATION_CHECK` marks
  where that is the case and it is not a validation.
- **The 3D percolation run** (`Q-P008`), currently INPROGRESS and unvalidated.
- **A genuinely independent audit** of the audit controls.
- **Regenerating the excluded data** from recorded seeds, so the full suite runs
  from a clean checkout.

## What would not help

- Retuning a preregistered threshold to make a result land inside its band.
- Re-freezing an audit baseline.
- Summarising this work as a physics discovery.

## Running it

```bash
pip install -r requirements.txt
python -m pytest -q
```

Roughly one minute. No GPU.