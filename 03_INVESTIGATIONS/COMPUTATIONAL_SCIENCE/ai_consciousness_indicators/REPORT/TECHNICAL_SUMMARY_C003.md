# TECHNICAL SUMMARY — EXP-C003 (robustness arm of Q-C001)

## Question

F01 is the worst problem in this investigation: the aggregation temperature and
every prior were chosen so that six reference anchors — whose bands we also
invented — came out right. Perturbing the temperature alone does not address
that. Temperature is one of dozens of discretionary choices.

**How much of the battery's output survives the arbitrariness, if every
discretionary choice is perturbed jointly?**

## Method

Six parameter families perturbed simultaneously per draw:

| | Parameter | Plausible range | Aggressive range |
|---|---|---|---|
| P1 | `_SOFT_OR_TEMPERATURE` | 0.05–0.60 (log-uniform) | 0.02–3.0 (log-uniform) |
| P2 | evidence quality multiplier | 0.80–1.25 | 0.35–1.6 |
| P3 | `p_given_not_conscious` shift | ±0.15 | ±0.35 |
| P4 | `p_given_conscious` shift | −0.12…+0.08 | −0.30…+0.15 |
| P5 | `_NECESSARY_ABSENCE_FACTOR` | 0.45–0.70 | 0.30–0.85 |
| P6 | `_NECESSITY_ABSENCE_PENALTY` | 1.2–1.8 | 1.0–2.2 |

P2 is drawn **per evidence state**, so a sample can make `CONTROLLED` stronger
than `REPLICATED` — inverting the intended ordering. That is deliberate: it
exposes assumptions the original design never questioned.

**Held fixed:** anchor *assignments* and calibration bands. These are the source
claims under test, not parameters. Perturbing them would make every sample
trivially "fail" and measure nothing.

1500 draws per region, seed 0, all randomness via the lab's sha256-derived
`rng(label, seed)`.

## Results

### Plausible region (±~40% on most parameters)

| Gate | Hold rate | Threshold |
|---|---|---|
| F-A full canonical order exact | **1.0000** | ≥ 0.90 |
| F-B adversarial < human | **1.0000** | ≥ 0.95 |
| F-C adversarial < 0.30 | 0.9753 | ≥ 0.95 |
| F-D human > 0.50 | **1.0000** | ≥ 0.95 |

All pass.

### Aggressive region (evidence scales can invert; penalties 0.30–0.85)

| Gate | Hold rate |
|---|---|
| F-A exact order | **0.6413** |
| F-B adversarial < human | **1.0000** |
| F-C adversarial < 0.30 | **0.7687** |
| F-D human > 0.50 | **1.0000** |

Absolute calibration does not hold.

### The asymmetry that matters

| Anchor | plausible mean | aggressive mean | aggressive p05–p95 |
|---|---|---|---|
| `human_adult` | 0.998 | 0.969 | 0.781–1.000 |
| `gwt_architecture_no_metacognition` | 0.492 | 0.505 | 0.261–0.797 |
| `weak_everywhere` | 0.346 | 0.393 | 0.144–0.781 |
| `unigram_lookup_with_fake_selfreport` | 0.148 | 0.191 | 0.027–**0.506** |
| `feedforward_mlp` | 0.052 | 0.093 | 0.004–0.368 |
| `lookup_table` | 0.051 | 0.092 | 0.004–0.368 |

Absolute credences move substantially: the adversarial anchor's 5th–95th
percentile spans 0.027–0.506 in the aggressive region, wide enough to cross the
0.30 ceiling entirely.

**F-B never fails.** Across 3000 draws spanning temperatures 0.02–3.0, evidence
scales that invert the intended ordering, and penalties from 0.30 to 0.85, no
sample let a system that merely produces fluent first-person inner-life talk
outscore the human. 1.0000 in both regions.

## Interpretation

**Ranking is robust; absolute probabilities are not.**

This is the strongest result available without independent expert elicitation,
and it is a genuine partial answer to F01. It does not resolve F01 — it bounds
how much F01 matters.

**Authorised:** comparing systems scored under identical assumptions. Ordering
holds at 1.0000 in the plausible region, and the architectural claim (F-B) holds
everywhere tried, including regions chosen to break it.

**Not authorised:** quoting an absolute probability that any system is conscious.
In the aggressive region the same system lands anywhere in 0.027–0.506 depending
on constants nobody derived from evidence.

## Two gate bugs found

Both fixed, both recorded in `FALSIFICATION/F05_F06_robustness.md`.

- **F05:** `EXPECTED_ORDER` omitted `feedforward_mlp`, so F-A compared a sorted
  six-element list against a five-element tuple and read **0.0000** — reporting
  its own defect as a falsification. Now raises on partial orders; regression
  tested.
- **F06:** `all_gates_pass` drove the verdict, discarding F-B = 1.0000 because
  the fragile calibration gate F-C failed. Verdict now computed from the
  load-bearing gate, with calibration gates reported separately. Reported
  conclusion changed; measurements did not.

## Limitations

1. **Conditional on anchor assignments.** F-B holds *given* that we assigned
   `human_adult` every indicator satisfied and the adversarial anchor three
   mimicked properties. Those assignments remain lab assumptions. F01 stands.
2. **Ranges are judgement calls.** The "aggressive" range was chosen to be
   hostile, not estimated. A wider one might break F-B.
3. **No white-box evidence.** Nothing here was measured on a real model.
4. **Uniform independence.** Priors perturbed independently; correlated
   miscalibration is not sampled and could be worse.
5. **`all_gates_pass` is still exposed** in the output and still keys on all four
   gates. Deliberate — it is the stricter reading. Consumers should read
   `verdict_detail`, not `all_gates_pass`.

## Reproduction

```powershell
cd <repo-root>
python -m pytest 03_INVESTIGATIONS/COMPUTATIONAL_SCIENCE/ai_consciousness_indicators/TESTS -q
```

30 tests pass (19 instrument + 11 robustness).

`result_hash`: `b96aaef11ef49e7b…` (`RESULTS/experiment_C003.json`).

## Claim layer

**L2 (statistical) for the robustness claim.** "No parameter setting tried lets
the fluent-liar anchor outscore the human" is a statistical claim about a sampled
region, and is falsifiable by finding a counterexample.

**No claim about any AI system.** No model was scored.