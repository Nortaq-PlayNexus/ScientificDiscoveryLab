# Investigation: Vortex density in random wave fields (Q-O002 / HYP-002 / EXP-0003)

Does a discrete winding-number counter reproduce the Kac-Rice / Nye-Berry
phase-singularity density n = <|dE/dx|^2> / (2*pi*<|E|^2>) for isotropic complex
Gaussian random fields - and in which regime does it fail?

This is the lab's first optics investigation that directly inherits a lesson from the
predecessor project `coherent-optical-ai-sandbox`, whose winding counter was found to
be grid-locked. A half-pixel shift-invariance test is a first-class control here.

## Map

| File | Purpose |
|---|---|
| QUESTION.md | the question, what is known, pitfalls |
| LITERATURE.md | references; honest "sources searched" note |
| HYPOTHESIS.md | HYP-002, frozen statements |
| PREDICTIONS.md | numeric predictions + test grid |
| CONTROLS.md | C1-C10 and the kill-the-hypothesis battery |
| EXPERIMENT_PLAN.md | protocol, decision rules, Appendix A derivation |
| CODE/run_vortex_density.py | the experiment |
| CODE/make_figure.py | figure |
| REPLICATION/independent_check.py | plane-wave sum, independent detector |
| FALSIFICATION/planning_checks.md | disclosed pre-design sanity checks |
| RESULTS/, FIGURES/, REPORT/ | outputs |
| CONFIG/ | frozen preregistration, experiment.json, registry.jsonl |

## Run

    python CODE/run_vortex_density.py
    python REPLICATION/independent_check.py
    python CODE/make_figure.py

(Add `04_SHARED_ENGINE` to PYTHONPATH automatically; scripts handle it.)

## Status

See the lab EXPERIMENT_REGISTRY.md and REPORT/ for the outcome.
