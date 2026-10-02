# Press release

## Short version (60 words)

An open-source research project built a calibrated instrument for assessing AI
consciousness, then found and fixed four wrong ways of combining its inputs and
six defects in its own verification, three of them found in a final pre-release review. It proved the ordering of systems is robust to
arbitrary parameter choices while absolute probabilities are not, scored zero AI
systems, and publishes its unresolved problems as the main result.

## Headline options

- "Ranking survives, absolute probabilities don't: what a consciousness test for AI revealed when it was stress-tested"
- "We built four ways to measure AI consciousness. Three were wrong. The fourth can't be validated."
- "A consciousness detector that tells you exactly what it can't tell you"

## Key facts

- **What it is.** An instrument for scoring how likely an AI system is to be
  phenomenally conscious, built from 14 indicator properties in Butlin, Long et
  al. (2023), arXiv:2308.08708 — a 19-author paper including Yoshua Bengio and
  David Chalmers, restated in *Trends in Cognitive Sciences* in 2026.

- **No AI systems were scored.** No claim is made about whether any AI system is
  conscious, including the model that assisted with the work.

- **Four aggregators, three wrong.** A counting-based approach was rejected on
  theoretical grounds. Of the implementations that replaced it, three produced
  a plausible profile scoring 0.000, 0.507 and 0.092 respectively. All three
  failures landed in the middle of the range the instrument exists to measure.

- **Six defects in the verification, not the instrument.** Including a test that
  reported its own coding bug as a falsification of the battery.

- **The robustness result.** Across 3,000 joint perturbations of all six
  discretionary parameters — including settings that invert the intended
  evidence-quality ordering — no configuration ever let a system that merely
  *performs* introspection outscore a human. 1.0000 in both perturbation
  regions. By contrast, absolute credence for that same system spans
  [0.027, 0.506] and genuinely crosses its calibration ceiling.

- **The unresolved problem, stated plainly.** The aggregation constant was
  chosen by sweeping against six reference anchors whose bands the authors also
  invented. Passing calibration shows internal consistency, not correctness.
  This is documented in the source code, the preregistration file, and the
  limitations section. It is not resolved.

- **The adversarial control.** A deliberately trivial system trained to emit
  fluent first-person sentences about its inner life, with no internal states
  behind them, scores 0.107 against a 0.15 ceiling. This is the battery's
  central check on the standing objection that such work measures eloquence
  rather than architecture.

- **Reproducibility.** 48 tests, ~5 seconds, three dependencies (numpy, scipy,
  pytest). No GPU, no network, no model weights. Results carry SHA-256 hashes
  over a canonical JSON encoding, with a verifier that detects post-hoc edits —
  itself covered by a test.

- **License.** MIT. The upstream indicator paper is CC BY-NC-SA 4.0. This is an
  independent implementation, not affiliated with or endorsed by the original
  authors.

## Quotes available on request

> "We set out to build a consciousness detector and spent most of the effort
> proving that our own detector was broken. The four ways it failed are more
> informative than the version that worked."

> "The honest headline isn't a number. It's that ranking systems survives every
> parameter choice we made, while quoting a probability does not. That
> distinction is the whole result."

> "The circularity is in the source code, not buried in a footnote. Passing our
> own calibration shows our instrument is consistent with our assumptions. It
> does not show our assumptions were right, and nothing inside the experiment
> can tell us."

## What we are asking for

Not code. **Calibration anchors from consciousness researchers who did not
build this instrument** — including researchers who think the approach is
wrong. If expert credences disagree with our bands, that disagreement is the
result.

Also welcome: an independent reimplementation written from the paper without
reading the existing code.

Explicitly not welcome: scores for specific frontier models absent white-box
evidence; re-tuned constants swept against the same anchors; speculation about
whether AI is conscious.

## Boilerplate

A research project built to a preregistered laboratory standard — claim
layering, mandatory controls, adversarial falsification, evidence grading,
append-only registries, null results recorded rather than deleted. The
investigation publishes four superseded aggregator designs, five verification
bugs, and two unresolved confounds in full.

The instrument reports a calibrated credence with a decomposable interval and a
per-theory breakdown. There is no function that returns a boolean, and a
`SATISFIED` finding cannot be recorded without evidence attached.

## Risk / accuracy notes for editors

If covering this, the following are accurate and the following are not:

- **Accurate:** "No AI system was scored." "No claim is made about AI
  consciousness." "The calibration is circular and unresolved." "Ranking is
  robust; absolute probabilities are not."
- **Not accurate:** "The project determined whether AI is conscious." "The
  project proved AI is not conscious." "Scientists now have a reliable measure of
  AI consciousness." "The instrument is validated."

The project produced a measurement tool and an honest account of that tool's
limits. It did not produce an answer about any system.

## Sources

- Butlin, P., Long, R., Elmoznino, E., Bengio, Y., et al. (2023).
  *Consciousness in Artificial Intelligence: Insights from the Science of
  Consciousness.* arXiv:2308.08708.
- Butlin, P., Long, R., Bayne, T., Bengio, Y., et al. (2026). *Identifying
  indicators of consciousness in AI systems.* Trends in Cognitive Sciences,
  30(6), 488–501. https://doi.org/10.1016/j.tics.2025.10.011
- Long, R., Sebo, J., Butlin, P., et al. (2026). *Studying AI Welfare Empirically.*
  https://nonhumanminds.org/studying-ai-welfare-empirically
- Gurnee, B., Sofroniew, N., Lindsey, J., et al. (2026). *Verbalizable
  Representations Form a Global Workspace in Language Models.*
  https://transformer-circuits.pub/2026/workspace

Repository: `github.com/Nortaq-PlayNexus/consciousness-indicator-battery`


