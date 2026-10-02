# LITERATURE — Q-C001

## Primary source: the indicator framework

**Butlin, P., Long, R., Elmoznino, E., Bengio, Y., Birch, J., Constant, A.,
Deane, G., Fleming, S. M., Frith, C., Ji, X., Kanai, R., Klein, C., Lindsay, G.,
Michel, M., Mudrik, L., Peters, M. A. K., Schwitzgebel, E., Simon, J., &
VanRullen, R. (2023).** *Consciousness in Artificial Intelligence: Insights from
the Science of Consciousness.* arXiv:2308.08708.
https://arxiv.org/abs/2308.08708

19 authors. The canonical indicator list. Key claims used here:

- Adopts **computational functionalism** as a working hypothesis (§1.2.1). This is
  the load-bearing assumption of the entire transfer from human evidence to silicon.
- Rejects the behavioural route: AI systems "can be trained to mimic human
  behaviours while working in very different ways" (§1.2.3).
- **Explicitly excludes IIT** — not compatible with computational functionalism
  (§Executive Summary). Any Φ-based score is outside this framework by construction.
- Table 1 gives 14 indicators; §2.5 says some *subsets* are jointly sufficient.
  This is why a count is wrong.
- Verdict on current systems: "no current AI systems are conscious," with the
  footnote that satisfying indicators **would not mean** the system is definitely
  conscious.
- Published correction worth noting: an earlier version of that sentence said "no
  obvious barriers to building conscious AI systems"; it was amended to say only
  that building systems satisfying the indicators is feasible. The distinction
  matters and is preserved in the source.

**Butlin, P., Long, R., Bayne, T., Bengio, Y., Birch, J., Chalmers, D., Constant,
A., Deane, G., Elmoznino, E., Fleming, S. M., Ji, X., Kanai, R., Klein, C.,
Lindsay, G., Michel, M., Mudrik, L., Peters, M. A. K., Schwitzgebel, E., Simon, J.,
& VanRullen, R. (2026).** *Identifying indicators of consciousness in AI systems.*
**Trends in Cognitive Sciences** 30(6), 488–501.
DOI: [10.1016/j.tics.2025.10.011](https://doi.org/10.1016/j.tics.2025.10.011) · PMID 41219038

The peer-reviewed restatement. Same 14 indicators, plus four methodological
guidelines for deriving them. Confirms the 2023 verdict.

## Methodology source

**Long, R., Sebo, J., Butlin, P., Plunkett, D., Campbell, R., Beasley, C.,
Saad, B., & Sims, T. (2026).** *Studying AI Welfare Empirically.* NYU Center for
Mind, Ethics, and Policy & Eleos AI Research.
https://nonhumanminds.org/studying-ai-welfare-empirically

Supplies the three-axis structure this investigation adopts for *what* is being
assessed: the question asked, the entity assessed (model vs. instance vs.
persona), and the evidence type (**behavioural / internal / developmental**).

Their field principles are adopted nearly verbatim as lab rules here:
probabilistic, pluralistic, thoughtfully targeted, ethically conducted,
transparently reported, and **informed by research independent of AI companies**.

One of their claims is directly load-bearing for the adversarial anchor below:
prior work establishing that models have welfare-relevant states is weak, and
that even where introspection exists, self-reports may not be produced by
introspection. That is the "fluent liar" failure mode `KNOWN_ANSWERS` encodes.

## Empirical findings that constrain what the battery can claim

**Gurnee, B., Sofroniew, N., Lindsey, J., et al. (2026).** *Verbalizable
Representations Form a Global Workspace in Language Models.* Transformer Circuits.
https://transformer-circuits.pub/2026/workspace
Code: https://github.com/anthropics/jacobian-lens (Apache-2.0)

The most important empirical result for this investigation. Findings used:

- An emergent "J-space" of ~25 concurrently active vectors, <10% of activation.
- Causal tests: swapping a J-space direction changes output (the spider→ant swap
  changes an answer from 8 to 6). So it is read out, not merely mirrored.
- Ablating J-space destroys multi-step reasoning (→ near zero) while leaving
  fluency, sentiment classification, and factual recall intact.
- J-space patterns have ~100× denser connectivity than ordinary representations.
- The structure is **not designed** — it emerged during training.
- Authors' own conclusion, quoted: evidence bears on **access** consciousness,
  and "it remains a contested philosophical question whether or not access
  consciousness *implies* phenomenal consciousness."

This is exactly the split the battery's output format enforces. It reports what
is measurable and refuses to convert access into experience.

**Sofroniew, N., Kauvar, I., Saunders, W., et al. (2026).** *Emotion Concepts and
their Function in a Large Language Model.* Transformer Circuits.
https://transformer-circuits.pub/2026/emotions · arXiv:2604.07729

Relevant because valenced representations were found to exist **before**
post-training RLHF. Bears on HOT-2/metacognition and AE-1: valence structure in
a model is not automatically evidence of sentience, and its presence pre-dates
the training stage usually blamed for it.

**Skeptical counterweight.** *Can LLMs Introspect? A Reality Check.*
(arXiv:2605.26242) argues detection of injected concepts is **content-agnostic**:
models notice *an* anomaly but cannot reliably identify *which* concept, and
default to high-frequency guesses. Bai et al. (2025) found self-authorship
recognition at chance.

This is why the battery keys on architecture rather than self-report, and why
HOT-2 is scored from internal evidence only.

## Explicitly excluded

**Integrated Information Theory (Tononi).** Excluded by Butlin et al. because it
is incompatible with computational functionalism. Independently contested: a
2023 open letter characterised it as unfalsifiable pseudoscience, with a
documented critique that Φ applied to simple systems returns large values for
structures (XOR grids, single photodiodes) nobody would call conscious
(https://pmc.ncbi.nlm.nih.gov/articles/PMC4574706).

Φ is therefore **not computed** in this battery. Computing it would produce a
number with no agreed interpretation, which is worse than not computing it.

## Priority statement (RESEARCH_RULES.md §7)

No matching study was found that implements a *calibrated, known-answer-gated
aggregator* over the Butlin indicator set. Individual indicators and the
Jacobian-lens method are all prior art. This does not establish priority.