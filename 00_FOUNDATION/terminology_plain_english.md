# Terminology in Plain English

Glossary of terms used in this lab, written without jargon. When a report uses a
term, this file explains it.

| Term | Plain meaning |
|---|---|
| **Baseline** | What happens in the plain/default case, with nothing special on top. |
| **Control** | A run that is the same as the experiment except the thing you are testing is neutralised/removed/shuffled. If the experiment still "works" without the thing, the thing was not the cause. |
| **Null hypothesis** | The boring, default claim: "nothing special is going on; the numbers are just ordinary variation." |
| **Alternative hypothesis** | These numbers are different from ordinary variation in a specific way. |
| **p-value** | How surprised you should be if the boring claim were true and you still saw numbers this extreme. Tiny p => very surprised. Surprise is not proof. |
| **Effect size** | How big the difference actually is, in plain units or relative to noise. Bigger than "significant" — a difference can be significant and still trivial. |
| **Falsify** | Show that a claim is wrong, or at least that its expected signature is absent. |
| **Replication** | Rerun the same thing (new seeds) and get the same answer. |
| **Independent implementation** | A second person/process writes their own version of the code and gets the same answer. Much stronger than rerunning the same code. |
| **Anomaly** | A number or pattern that looks surprising before controls have been done. An anomaly is a question, not an answer. |
| **Aliasing / sampling artifact** | A fake pattern caused by the grid being too coarse — real signal folded onto itself. Often appears/disappears when resolution changes. |
| **Boundary artifact** | A fake pattern caused by the edge of the simulation region, not the physics. Tested by padding the edges and watching if the effect follows. |
| **Numerical error** | The numbers drift because of floating-point behaviour / method; the pattern is in the arithmetic, not the physics. |
| **Seed** | The starting number for a random-number generator. Same seed => same "random" data; different seeds => independent random realisations. |
| **Multiple testing / FDR** | If you test 1000 things for "significance", you will find ~10 "significant" by luck alone. FDR correction knocks back the false claims. |
| **Pre-registration** | Writing down the exact plan (test, data, alpha, controls) BEFORE looking at results, so you cannot quietly change the plan to get a nice answer. |
| **Holdout** | Data kept untouched and unseen until the very end, used to check the final model did not just memorise the search data. |
| **Evidence state** | Where a result sits on the honesty ladder: UNTESTED -> INITIAL RESULT -> CONTROLLED -> REPLICATED -> INDEPENDENTLY REPRODUCED -> LITERATURE-CHECKED -> EXTERNALLY VALIDATED. |
| **Model** | A simplified computer version of something, used for experiments that are too expensive/dangerous/hard to do for real. A model always leaves things out. |
| **Conservation law** | A quantity (energy, mass, charge) that should stay constant over time. A cross-check that a simulator is not secretly losing/creating stuff. |

## The three forbidden phrases

1. **"God/universe revealed it"** — not an explanation we can test.
2. **"This proves new physics"** — nothing here without external replication + review.
3. **"Nobody has done this before"** — only ever: "no matching study found in the
   sources searched; this does not establish priority."