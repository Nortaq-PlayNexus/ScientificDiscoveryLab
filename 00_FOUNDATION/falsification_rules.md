# Falsification Rules

The lab's most important engine: actively trying to destroy interesting results.

## Purpose

Any result that survives this engine is worth a second look. Any result that dies is
logged as falsified — equally valuable, and recorded with the same dignity.

## Automatic questions for every interesting result

1. Is this **numerical error**? (repeat with higher precision / different dtype)
2. Is this **sampling**? (shuffle/repartition the data)
3. Is this **aliasing**? (change resolution/grid; does it move?)
4. Is this **floating-point behaviour**? (tiny differences at 1e-16 scale are noise)
5. Is this a **visualization artifact**? (replot from raw numbers, no smoothing)
6. Is this a **boundary artifact**? (pad the region; does the effect stay interior?)
7. Is this caused by **parameter selection**? (sweep the parameter honestly)
8. Is this caused by **overfitting**? (frozen holdout / fresh data)
9. Is this **multiple testing**? (apply BH-FDR across all comparisons)
10. Is this a **known physical phenomenon**? (search literature for the effect)
11. Is this caused by the **simulation method**? (try a second independent algorithm)
12. Does changing **algorithms** remove it?
13. Does changing **resolution** remove it?
14. Does changing **random seeds** remove it?
15. Does **independently generated data** reproduce it?
16. Does a **simpler model** explain it? (Occam: a 1-line rule beating your 50-line
    model is a falsification, not a compliment)

## Orders of suspiciousness

Patterns that are MORE suspicious, not less:

- Appears at exactly one grid size / seed / parameter value
- Depends on a detector that counts things (e.g., peak-counting) tuned by hand
- Magnitude shrinks as resolution increases
- Only visible in a processed metric, not in raw data
- Only visible after several layers of processing
- Matches the hypothesis's shape "a bit too closely"
- Even slightly sensitive to boundary padding

## The rule of the engine

> The system actively prefers discovering that an exciting hypothesis is WRONG
> over falsely confirming it.

A rejected hypothesis gets a clean entry in `06_RESULTS/falsified/` plus a line in
the registry. The lab is proud of its falsifications.

## Escalation gate

A result may be logged as an **anomaly** (`ANOM-####`) only after:

- baseline defined
- difference quantified (effect size)
- relevant controls survived
- alternative explanations attempted
- replication attempted (multiple seeds)
- independent method attempted where practical
- literature-checked

It is escalated to "flag for human scientific review" only after: matched controls,
parameter changes, independent seeds, independent implementations, literature
checking, and — where possible — external replication. That is the highest state
this lab can reach alone.