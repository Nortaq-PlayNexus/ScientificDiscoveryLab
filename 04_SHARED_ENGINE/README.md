# SHARED ENGINE (04_SHARED_ENGINE)

Reusable machinery for every investigation. Python code lives in the importable
package `engine/`; the sibling folders (datasets/, simulation/, statistics/,
visualization/, hypothesis_testing/, reproducibility/, utilities/) hold the
narrative specs + templates that describe how each engine module must be used.

## Python package

```python
import sys
sys.path.insert(0, r"C:\Users\natha\ScientificDiscoveryLab\04_SHARED_ENGINE")
import engine
from engine.utilities.core import rng, make_experiment_json
from engine.statistics.testers import bh_fdr, summarize
```

| Folder | Module | Purpose |
|---|---|---|
| utilities/ | `engine/utilities/core.py` | deterministic RNG (sha256), hashing, experiment.json builder |
| statistics/ | `engine/statistics/testers.py` | BH-FDR 0.01, Welch t, Cohen's d, bootstrap CI, binomial bands |
| hypothesis_testing/ | `engine/hypothesis_testing/prereg.py` | freeze prereg config, append-only change log |
| simulation/ | `engine/simulation/controls.py` | null fields, matched-spectrum surrogates, resolution/seed ladders |
| reproducibility/ | `engine/reproducibility/experiments.py` | universal template scaffold, append-only registry |
| datasets/ | `engine/datasets/manifest.py` | sha256 provenance manifests |
| visualization/ | `engine/visualization/plots.py` | deterministic figure saving |

## Templates and specs (narrative)

- `experiment_template.md` — the universal investigation folder layout.
- Each sibling folder's README documents the corresponding control/analysis law
  (they reference RESEARCH_RULES.md at the lab root).

## Rules

- Never import pandas (not installed); keep engine dependency-light (numpy/scipy/
  matplotlib only) so investigations can run on the plain lab Python 3.14.7.
- Test: `python tests/run_infra_validation.py` (from `04_SHARED_ENGINE`).