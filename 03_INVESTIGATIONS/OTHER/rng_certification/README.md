# INVESTIGATION — Lab RNG statistical certification (Q-I004 / HYP-003 / EXP-0004)

Does the lab's sha256-derived numpy Generator (`engine.utilities.core.rng`) pass a
standard, lightweight statistical PRNG battery at lab scales, so anomalies in any
future experiment can be attributed to science and not to the RNG?

The lab depends on `rng(label, seed)` everywhere (seed from
`sha256(label:seed)`). This investigation certifies that dependency with a
reproducible battery and validates the battery itself against known-good
generators so that "passes" and "fails" are both meaningful.

## Map

| File | Purpose |
|---|---|
| QUESTION.md | the question, what is known, pitfalls |
| LITERATURE.md | references (NIST SP 800-22, Knuth, Marsaglia); honest scope note |
| HYPOTHESIS.md | HYP-003, frozen statements |
| PREDICTIONS.md | numeric expectations + pass/fail bands |
| CONTROLS.md | C1-C8 and the kill-the-hypothesis battery |
| EXPERIMENT_PLAN.md | protocol, test formulas, decision rules |
| CODE/run_rng_cert.py | the certification run |
| CODE/plot_battery.py | p-value distribution figures |
| REPLICATION/independent_check.py | independent battery re-implementation |
| FALSIFICATION/planning_checks.md | disclosed pre-design sanity checks |
| RESULTS/, FIGURES/, REPORT/ | outputs |
| CONFIG/ | frozen preregistration, experiment.json, registry.jsonl |

## Run

    python CODE/run_rng_cert.py
    python REPLICATION/independent_check.py
    python CODE/plot_battery.py

(Add `04_SHARED_ENGINE` to PYTHONPATH automatically; scripts handle it.)

## Status

See the lab EXPERIMENT_REGISTRY.md and REPORT/ for the outcome.