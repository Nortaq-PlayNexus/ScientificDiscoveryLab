# REPOSITORY COMPARISON — ScientificDiscoveryLab vs string-theory-questions

**Audit date:** 2026-09-23
**Primary source:** `C:\Users\natha\ScientificDiscoveryLab` (per instruction document)
**Secondary source:** `C:\Users\natha\code\string-theory-questions`
**Auditor:** Automated forensic inventory (Phase 5 of 20)

---

## 1. Scope

The instruction document on the Desktop (last read 2026-09-23) specifies:

> Treat `C:\Users\natha\ScientificDiscoveryLab` as the PRIMARY SOURCE OF TRUTH.
> Do NOT assume the smaller string-theory-questions repository contains everything.

This document compares the two repositories to determine:
- What exists only in ScientificDiscoveryLab
- What exists only in string-theory-questions
- What overlaps (and whether it's consistent)
- Whether the string-theory-questions content should be considered part of this audit

## 2. Repository Overview

| Property | ScientificDiscoveryLab | string-theory-questions |
|---|---|---|
| **Primary domain** | Multi-disciplinary scientific lab (optics, physics, math, etc.) | String theory computational program |
| **Total files** | ~416 | ~300+ (estimated from prior audit) |
| **Core investigations** | 5 active (optics, percolation, math, acoustics, RNG) | 12 Q-series experiments |
| **Shared engine** | Yes (04_SHARED_ENGINE) | No (separate implementations) |
| **Experiment registry** | EXPERIMENT_REGISTRY.md (14 experiments) | No centralized registry |
| **Pre-registration** | Yes (prereg_*.json, frozen) | Partial (some prereg files exist) |
| **Independent replication** | Yes (independent_check.* for all major experiments) | Limited (3 agents found, not 62+) |
| **Categorized results** | Yes (06_RESULTS/{confirmed,anomalies,falsified,inconclusive}) | No |
| **External dossier** | Yes (05_EXTERNAL_RESEARCHER_DOSSIER, 9 documents) | No |
| **Falsification framework** | Yes (RESEARCH_RULES.md, falsification_rules.md, FALSIFICATION/planning_checks.md) | Partial |

## 3. Overlap Analysis

### 3.1 Content Overlap

**No direct content overlap was found** between the two repositories. They address completely different scientific domains:

- ScientificDiscoveryLab: coherent scalar optics, percolation, prime gaps, Feigenbaum constants, RNG certification, acoustics
- string-theory-questions: WGC, de Sitter swampland, islands, holography, inflation, moduli, SUSY, landscape, testability, swampland catalog

### 3.2 Methodological Overlap

Both repositories share some **methodological patterns** (likely from the same lab philosophy):

| Pattern | ScientificDiscoveryLab | string-theory-questions |
|---|---|---|
| Pre-registration | Full (prereg_*.json, frozen) | Partial |
| Independent replication | Full (independent_check.*) | Limited (3 agents) |
| BH-FDR statistics | Yes | Yes (from prior audit) |
| Controls framework | Full (C1–C10) | Partial |
| Honest framing | Yes (PLAIN_*.md, what it does NOT prove) | Yes (PLAIN section in some) |
| Claim registers | No (this audit adds one) | Yes (AUDIT/CLAIM_REGISTER.md) |

### 3.3 Priority Determination

Per the instruction document:

> "Treat C:\Users\natha\ScientificDiscoveryLab as the PRIMARY SOURCE OF TRUTH."
> "Do NOT assume the smaller string-theory-questions repository contains everything."

**Decision:** All 20 audit phases in this audit are performed on ScientificDiscoveryLab. The string-theory-questions repository is treated as a **secondary source** for context only. Findings from prior audits of string-theory-questions (AUDIT/ directory at `code/string-theory-questions/AUDIT/`) are referenced but NOT included in this audit's output.

## 4. What string-theory-questions Has That ScientificDiscoveryLab Does Not

Per prior audit work, the string-theory-questions repository contains:

| Content | Description |
|---|---|
| Q1–Q12 dossiers | 12 detailed experimental dossiers on string theory topics |
| Theory documents | 8 theory documents (WGC, de Sitter, islands, etc.) |
| ~32 simulation scripts | String-theory-specific computations |
| 19 JSON data files | String-theory-specific datasets |
| AUDIT/ directory | 7 prior audit documents (from earlier phase) |

**Assessment:** These are **not relevant** to the current audit, which focuses on ScientificDiscoveryLab per the instruction document.

## 5. What ScientificDiscoveryLab Has That string-theory-questions Does Not

| Content | Description |
|---|---|
| 04_SHARED_ENGINE | Shared computational engine with validated RNG, BH-FDR, surrogate generation |
| 05_EXTERNAL_RESEARCHER_DOSSIER | 9 external review documents (Professor Swartzlander dossier) |
| 06_RESULTS/ categorized | Formal result categorization (confirmed/anomalies/falsified/inconclusive) |
| 08_REPLICATION/ | Structured replication directory |
| RESEARCH_RULES.md | Formal rules of conduct with 5-layer claim hierarchy |
| REPRODUCIBILITY.md | Full reproducibility specification |
| EXPERIMENT_REGISTRY.md | Centralized experiment registry (14 experiments) |
| src/ packages | 17 modular source packages |
| tests/ unit tests | 17 unit test files |
| sovereign_biolab.db | 184 KB database (unexamined) |

## 6. Cross-Referencing

### 6.1 Shared Personnel
Both repositories appear to be from the same research group (Nathan/DJ PhantomTape). The Professor Swartzlander correspondence in ScientificDiscoveryLab may relate to external collaboration.

### 6.2 Shared Methodological DNA
Both repositories reflect the same research philosophy:
- Pre-registration before running
- Independent implementation replication
- Honest negative results
- BH-FDR for multiple comparisons
- "What does this NOT prove?" sections

### 6.3 No Code Sharing
No Python files were found to be shared or copied between the two repositories. Each has its own implementations.

## 7. Recommendation

**For this audit:** All 20 phases focus exclusively on ScientificDiscoveryLab. The string-theory-questions repository is:
1. **NOT** included in the audit scope
2. **NOT** modified or overwritten
3. **NOT** treated as authoritative for any finding
4. Referenced ONLY when providing context about shared methodology or research group practices

## 8. Data Integrity Statement

The prior audit work at `code/string-theory-questions/AUDIT/` (7 documents from Phases 0–7) remains intact and unmodified. It is NOT part of this audit's output. Any references to string theory content in this audit are for contextual comparison only.
