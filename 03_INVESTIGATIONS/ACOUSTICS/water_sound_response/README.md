# Investigation: Water acoustic response simulator certification (Q-AC001 / HYP-AC001 / EXP-0015)

Can one physically-parameterised simulator reproduce, simultaneously and within
preregistered tolerances, the established quantitative laws that govern how water
responds to sound and vibration — the speed of sound, bounded-column resonance,
frequency-dependent absorption, pressure-node patterning of suspended particles,
bubble (Minnaert/cavitation) response, and the Faraday surface-wave threshold and
wavelength selection?

This is the lab's **first acoustics investigation** and the first to certify a
multi-module *physics simulator* rather than a single estimator. Each of the six
modules is gated against its own published anchor, carries a resolution ladder, and
is re-implemented by an independent route in `REPLICATION/`.

Honest framing (mandatory, see `REPORT/`): every target law is established
textbook physics (Minnaert 1933, Faraday 1831, Benjamin & Ursell 1954, UNESCO
1983, Gorkov 1962, Nye/Berry-era material). **No novelty is claimed or implied.**
The deliverable is a certified instrument plus an honest failure-zone map.

## Map

| File | Purpose |
|---|---|
| QUESTION.md | Q-AC001 — the question, what is known, pitfalls |
| LITERATURE.md | references; honest "sources searched" note |
| HYPOTHESIS.md | HYP-AC001, frozen statements |
| PREDICTIONS.md | numeric predictions + frozen test grid |
| CONTROLS.md | C1–C12 and the kill-the-hypothesis battery |
| EXPERIMENT_PLAN.md | protocol, decision rules, physics appendices |
| CODE/water_acoustics_engine.py | the six-module simulator |
| CODE/run_exp0015.py | the experiment (prereg, cells, gates, FDR, outputs) |
| CODE/make_figures.py | figures |
| REPLICATION/independent_check.py | independent re-implementation (C12) |
| FALSIFICATION/planning_checks.md | disclosed pre-design sanity checks |
| RESULTS/, FIGURES/, REPORT/ | outputs |
| CONFIG/ | frozen preregistration, experiment.json, registry.jsonl, changelog.jsonl |

## The six modules

| # | Module | Established anchor tested |
|---|---|---|
| S1 | Speed of sound c(T,P) | UNESCO (Chen–Millero / Wong–Zhu) vs Mackenzie (1981); published c anchors |
| S2 | Bounded-column resonance | f_n = n·c/2L (rigid–rigid), (2n−1)c/4L (rigid–free) |
| S3 | Absorption vs frequency | α = 2.50×10⁻¹⁴ f² Np/m (fresh water, 20 °C); classical theory gives only 1.1×10⁻¹⁴ |
| S4 | Radiation-force patterning | Gorkov force → particles at pressure nodes, spacing λ/2; φ>0 vs φ<0 |
| S5 | Bubble response / cavitation | Minnaert f₀R₀ ≈ 3 Hz·m, f₀ ∝ R₀⁻¹; cavitation onset ≈ P₀ |
| S6 | Faraday surface response | ω₀²=(gk+σk³/ρ)tanh(kh); subharmonic ω/2; Γ_c ≈ 4μ/ω₀ |

## Run

    python CODE/run_exp0015.py
    python REPLICATION/independent_check.py
    python CODE/make_figures.py

(Scripts add `04_SHARED_ENGINE` to `sys.path` themselves.)

## Status

See the lab `EXPERIMENT_REGISTRY.md` and `REPORT/` for the outcome.
