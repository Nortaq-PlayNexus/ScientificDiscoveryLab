# RISK REGISTER

SOVEREIGN BIOCHEMICAL DISCOVERY LAB — Risk Assessment

Date: 2026-09-20

---

## Critical Risks

| ID | Risk | Severity | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R-001 | LLM hallucinates chemical structures, SMILES, or citations | CRITICAL | HIGH | Catastrophic | Evidence classification (E0-E6); all structures computationally validated; provenance tracking; no LLM insertion of scientific facts | Orchestrator |
| R-002 | Python 3.14 package incompatibility | HIGH | MEDIUM | High | All critical packages (RDKit, OpenMM, Bio) verified on 3.14; QC deferred; monitor for updates | Dev |
| R-003 | No C/C++ compiler blocks quantum chemistry | HIGH | CERTAIN | High | QC module deferred; design interface now; install Miniconda later if needed | Dev |
| R-004 | CUDA toolkit unavailable/broken | HIGH | HIGH | Medium | CPU mode as primary; GPU as optional enhancement; document GPU requirements | Dev |
| R-005 | REST API rate limiting breaks data acquisition | MEDIUM | HIGH | Medium | Implement request caching with timestamps; respect rate limits (PubChem: 3/s, NCBI: 3/s); exponential backoff | Dev |
| R-006 | Data drift — external databases change over time | MEDIUM | HIGH | Medium | Cache all external data locally with retrieval timestamp; record source version; never treat cached data as current | Dev |

## High Risks

| ID | Risk | Severity | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R-007 | PySide6 LGPL compliance violation | LOW | LOW | Medium | Maintain license notice; document use; review on distribution | Dev |
| R-008 | pandas 3.x breaking changes | MEDIUM | MEDIUM | Medium | Test migration; code defensively; pin versions | Dev |
| R-009 | Network dependency for core features | HIGH | MEDIUM | High | All features designed to degrade gracefully offline; cache aggressively | Dev |
| R-010 | RDKit version pinning issues | MEDIUM | MEDIUM | Medium | Pin exact versions in requirements.txt; test on upgrades in staging | Dev |
| R-011 | Docking score misinterpretation as medical evidence | CRITICAL | MEDIUM | Catastrophic | Display disclaimer prominently: "DOCKING IS A COMPUTATIONAL HYPOTHESIS, NOT CLINICAL EVIDENCE" | Orchestrator |
| R-012 | Simulation result presented as experimental fact | CRITICAL | MEDIUM | Catastrophic | Evidence classification enforced at ALL display layers; E3/E4 results labeled as "computational prediction" | Orchestrator |

## Medium Risks

| ID | Risk | Severity | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R-013 | Combinatorial explosion in reaction discovery | HIGH | CERTAIN | Medium | Beam search, similarity filtering, priority queues, user-defined limits | Reaction Engine |
| R-014 | Reproducibility failures across machines | HIGH | MEDIUM | High | Record: OS, Python version, package versions, CPU type, random seeds, exact methods | Experiment Engine |
| R-015 | Adversarial agent fails to catch errors | MEDIUM | MEDIUM | High | Multiple adversarial strategies; rotate strategies; periodic external review | Adversarial Scientist |
| R-016 | Database schema migration issues | MEDIUM | MEDIUM | High | SQLAlchemy ORM abstraction; test migrations on copies; version schema | Database |
| R-017 | Git history bloating from large binary files | MEDIUM | HIGH | Low | .gitignore for binaries; git-lfs for structures/trajectories; separate data repository | Dev |
| R-018 | Open Babel GPL contamination | LOW | LOW | Medium | Use only for format conversion; document GPL dependency; consider commercial license if needed | Dev |

## Low Risks

| ID | Risk | Severity | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R-019 | Plotly rendering issues on Windows | LOW | MEDIUM | Low | Test on Windows; fallback to matplotlib | UI |
| R-020 | FastAPI async issues on Windows | LOW | MEDIUM | Low | Use uvicorn; test async endpoints; Windows asyncio considerations | Backend |
| R-021 | PyTorch CPU performance limitations | MEDIUM | HIGH | Low | CPU-only by design; GPU optional; use scipy/numpy where sufficient | ML |
| R-022 | wheel not installed | LOW | CERTAIN | Low | Install wheel before any package requiring compilation | Dev |
| R-023 | OpenMM force field parameter availability | MEDIUM | MEDIUM | Medium | Use AMBER/GROMOS force fields; document parameter sources; validate against known systems | MD |

---

## Risk Summary

| Severity | Count |
|---|---|
| CRITICAL | 3 |
| HIGH | 5 |
| MEDIUM | 7 |
| LOW | 5 |

## Risk Mitigation Priority

1. **Immediate**: R-001 (hallucination prevention), R-011 (docking misinterpretation), R-012 (simulation as fact)
2. **High Priority**: R-002 (Python 3.14 compat), R-004 (CUDA), R-005 (API limits), R-013 (combinatorial explosion)
3. **Medium Priority**: R-006 (data drift), R-014 (reproducibility), R-015 (adversarial gaps), R-016 (migration)
4. **Ongoing**: All others monitored
