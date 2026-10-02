# REVISED DOSSIER: Shared Computational Engine

**Revised by:** Forensic Audit, 2026-09-23
**Original**: 04_SHARED_ENGINE/
**Changes**: Documented separately; original preserved

---

## 1. Purpose

The shared computational engine provides validated core functionality for all experiments:
- RNG (sha256-derived PCG64)
- BH-FDR statistical testing
- Surrogate generation
- Template system
- Infrastructure validation

## 2. Engine Modules

| Module | File | Size | Purpose |
|---|---|---|---|
| engine.__init__ | engine/__init__.py | 824 B | Core interface |
| datasets | engine/datasets/manifest.py | 965 B | Dataset manifest |
| hypothesis_testing | engine/hypothesis_testing/prereg.py | 1,937 B | Pre-registration |
| reproducibility | engine/reproducibility/experiments.py | 2,681 B | Experiment reproducibility |
| simulation | engine/simulation/controls.py | 2,618 B | Simulation controls |
| statistics | engine/statistics/testers.py | 3,347 B | Statistical tests |
| utilities | engine/utilities/core.py | 3,001 B | RNG core |
| validation | engine/validation/rng_battery.py | 14,604 B | RNG battery |
| visualization | engine/visualization/plots.py | 1,248 B | Plot utilities |

## 3. Tests

| File | Size | Content |
|---|---|---|
| tests/run_infra_validation.py | 6,192 B | Infrastructure validation |
| tests/infra_validation_results.json | 1,601 B | Validation results (14/14) |

## 4. Known Bugs (Fixed)

| Bug | Description | Status |
|---|---|---|
| BH-FDR indexing | Step-up indexing flagged ALL cells as significant | Fixed, regression-tested, experiment re-run |

## 5. Key Features

- **Deterministic RNG**: sha256-derived Generator, independent of Python's hash() salt
- **Verified stable**: Across fresh processes
- **BH-FDR**: Full implementation with bug tracking
- **Experiment template**: Standardized experiment structure

## 6. Reproduction

```bash
cd 04_SHARED_ENGINE
python -m engine.tests.run_infra_validation
# Expected: 14/14 checks PASS
```

## 7. Dependencies

Per REPRODUCIBILITY.md: numpy, scipy, matplotlib, scikit-image, scikit-learn, sympy. pandas NOT installed; shared code avoids it.

## 8. Recommended Wording

> The shared computational engine provides validated RNG (sha256-derived PCG64), BH-FDR statistical testing, and infrastructure validation. All 14 validation checks pass. A BH-FDR indexing bug was found, fixed, regression-tested, and the affected experiment was re-run with both results preserved in the registry.
