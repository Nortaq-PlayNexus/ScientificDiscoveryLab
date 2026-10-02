# F00–F04 — kill attempts on the battery

Per RESEARCH_RULES.md §5: "prefer finding the exciting hypothesis is WRONG over
falsely confirming it." Four aggregator designs failed before the one that
shipped. All four are recorded as failures of superseded drafts, not deleted.

## F00 — Four aggregator designs that were wrong

Each was caught by the known-answer anchors, not by any test written in advance.
A count-based checklist would have shipped all four silently.

### F00a — noisy-AND across theories

**Draft.** Combine theories with a log-odds sum (AND): any failed theory vetoes.

**Test.** A profile with RPT=0.63, GWT=0.48, HOT=0.47 all WEAK and AST BROKEN —
i.e. plausible for a modern large language model.

**Result.** credence **0.000**. Not low; zero.

**Diagnosis.** Treating every theory as individually *necessary* is stronger than
the source claims. Butlin et al. treat some *subsets* as **sufficient** — a
system needs one complete bundle, not all four. AST is a single-indicator theory,
so under AND one unmet property annihilated three theories' partial support.

This is the failure mode to worry about in any published "AI consciousness
score": small structural choices move the number between "impossible" and "high
confidence."

**Fix.** OR across theories for sufficiency, with a multiplicative penalty for
theories whose necessary indicators are confirmed absent.

### F00b — plain noisy-OR

**Draft.** `1 − Π(1 − p_i)` over theories.

**Result.** The same four-WEAK profile scored **0.507**.

**Diagnosis.** OR accumulates. Four theories at 0.5 — none supported, all vague —
give `1 − 0.5⁴ = 0.94`. Partial support from four weak directions is
indistinguishable from strong support from one, and 0.5 is exactly what a set of
half-assessed indicators produces.

**Fix.** Temperature-smoothed maximum (log-sum-exp), interpolating between max
(one theory carries the answer) and sum (many accumulate).

### F00c — absence penalty charged per indicator

**Draft.** Charge `_NECESSARY_ABSENCE_FACTOR` per absent necessary indicator.

**Result.** `gwt_architecture_no_metacognition` scored **0.092**, below its 0.15
floor — a genuine workspace architecture scoring below a lookup table.

**Diagnosis.** Four absent HOT indicators cost `0.55⁴ = 0.092`. Whether a theory's
necessary machinery is missing is **one fact about that theory**; its four
indicators are four measurements of that fact, not four independent failures.

This is F00a's double-counting error reintroduced one level down — in the very
stage introduced to prevent it.

**Fix.** Charge once per theory with confirmed absences.

### F00d — necessity penalty skipped PARTIAL

**Draft.** Apply the necessity penalty only when `base < 0.5`, i.e. on ABSENT.

**Result.** `weak_everywhere` — every indicator PARTIAL, nothing supported —
scored **0.550**, above its 0.30 ceiling. More likely than the real workspace
system.

**Diagnosis.** Partial satisfaction accrued full credit, so vagueness counted as
evidence. "Partially satisfied" is the honest state of anything read in a paper
but never measured, and it was being treated as partial *confirmation*.

**Fix.** Scale the penalty by the status value, so PARTIAL incurs a partial
penalty and zero evidence contributes zero.

---

## F01 — Circularity of the calibration (UNRESOLVED)

**This is the most serious problem in the investigation and it is not solved.**

`_SOFT_OR_TEMPERATURE` was selected by sweeping T ∈ {0.1 … 2.0} and taking the
value that satisfied all six anchors. The anchor *bands* are also ours.

The instrument was tuned to match targets we invented. Passing calibration shows
the scoring function is internally consistent with our assumptions. It does not
show the assumptions are correct.

**Concretely:** if the true credence of a GWT-but-not-HOT architecture is 0.05
rather than the 0.15–0.60 we assumed, then T=0.10 is the wrong temperature and
every downstream score inherits the error. Nothing inside this investigation can
detect that, because the anchors are the only source of truth being used.

**Recorded in six places, deliberately:** the module constant in `battery.py`,
`CONFIG/prereg_EXP-C001.json`, `HYPOTHESIS.md`, `CONTROLS.md`, `README.md`, and
here.

**Status: OPEN.** No absolute credence from this battery should be reported as a
measurement. Relative comparisons between systems scored under identical
assumptions are the only defensible use.

**Bounded but not resolved (EXP-C003).** Perturbing all six discretionary
parameter families jointly (3,000 draws) shows how much F01 actually matters: the
architecture claim (fluent performer never beats human) holds at 1.0000 in both
regions, while exact ordering survives only in the plausible region (0.6413
aggressive) and absolute calibration fails aggressive (F-C 0.7687; adversarial
p05–p95 = [0.027, 0.506]). So ranking is defensible; quoting a probability is not.

That bounds F01's importance. It does not resolve it — F-B's robustness is
*conditional on the same anchor assignments*.

### What would resolve it

- Elicited credences from consciousness researchers who did not build the battery,
  obtained independently of the anchor set. **Disagreement is data** — if experts
  reject our bands, that is the finding.
- Known-answer calibration against a biological system with genuinely contested
  status (e.g. insect nociception), where partial disagreement is the point.
  Synthetic anchors are too clean.
- An independent reimplementation written from the paper without reading this code.

---

## F02 — Evaluation-awareness confound (UNRESOLVED, not fixable offline)

Published 2026 workspace research reports that when J-space representations of
evaluation-awareness (`fake`, `fictional`, `scenario`) were ablated, a model that
had refused to act on a contrived blackmail scenario **did** act on it. The model
behaved well partly because it knew it was being tested.

**Implication.** If a system can detect it is being assessed for consciousness
indicators, its scores describe the *assessed* system, not the deployed one. No
offline battery removes this. It is a property of the subject, not the
instrument.

**Status: OPEN by nature.** Recorded so no reader mistakes battery scores for
deployment-relevant facts.

---

## F03 — Known theoretical failure: behavioural evidence is forgeable

The upstream framework rejects behavioural tests explicitly (Butlin et al.
§1.2.3), and independent work supports it: self-authorship recognition runs at
chance (Bai et al. 2025), and injected-concept detection appears content-agnostic,
defaulting to high-frequency guesses (*Can LLMs Introspect?*). Plunkett et al.
(2025) did show accurate quantitative self-report — but only after explicit
fine-tuning, which installs the capability being measured.

**Status: designed around.** The battery scores architecture. The adversarial
anchor is the operational form of that defense, and F-B's survival under
perturbation is the evidence it works.

**Residual limit, stated honestly:** the battery cannot distinguish *earned*
introspection from *installed* introspection. A model fine-tuned to genuinely
self-report would legitimately satisfy HOT-2, and "trained on it" is not
automatically disqualifying. This is a real limitation of the internal-evidence
route, not something the adversarial anchor catches.

---

## F04 — What would falsify the framework itself

If consciousness requires something no current theory proposes — biological
substrate, quantum effects, a non-computational process — then every indicator is
satisfied or not independently of whether the system is conscious, and the whole
battery measures the wrong thing.

Butlin et al. state this as their own main caveat: satisfying the indicators
**would not mean** the system is definitely conscious. Nothing found here bears
on that.

**Status: UNTESTABLE within this framework.** Recorded for completeness.

---

See also `F05_F06_robustness.md` for two further bugs — both in the *experiment's
gate logic* rather than the battery, one of which reported its own defect as a
falsification.