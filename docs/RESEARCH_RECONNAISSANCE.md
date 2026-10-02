# RESEARCH RECONNAISSANCE

SOVEREIGN BIOCHEMICAL DISCOVERY LAB — Phase 0 Technical/Scientific Reconnaissance

Date: 2026-09-20
Status: COMPLETE

---

## 0. Environment Summary

| Property | Value |
|---|---|
| OS | Windows 10 Home |
| Python | 3.14.7 (global), pip 26.2.1 |
| CPU | Intel Core i7-8700 @ 3.20GHz (6C/12T) |
| RAM | 24 GB (2×8 GB) |
| GPU | NVIDIA GTX 1080 (8 GB) — CUDA available but no nvidia-smi in PATH |
| CUDA | Libraries NOT found via ctypes; GTX 1080 present but status UNKNOWN |
| C/C++ compiler | NONE (cl.exe not in PATH) |
| Conda | NOT installed |
| pip | 26.2.1 (global Python 3.14) |
| wheel | NOT installed |

---

## 1. Scientific Scope

### CAN simulate (with appropriate libraries):

- Molecular structures (SMILES, InChI, 2D/3D representations)
- Molecular similarity and fingerprints
- Molecular descriptors (MW, LogP, TPSA, HBD, HBA, etc.)
- Canonicalization and stereochemistry analysis
- Known reaction types (via reaction SMARTS, RDKit)
- Computational reaction hypotheses (constrained by known rules)
- Molecular interactions (hydrogen bonds, hydrophobic, etc.)
- Docking hypotheses (via AutoDock or custom scoring)
- Molecular dynamics (OpenMM, CPU mode)
- Some quantum chemical calculations (Psi4, PySCF — small molecules, CPU)
- Physicochemical properties (RDKit descriptors)
- Statistical comparisons (scipy, numpy)
- Literature relationships (database/APIs)
- Database relationships (SQLite local, REST APIs)
- Hypothesis generation (structured, evidence-tracked)
- Plant/natural-product representation (custom schema)
- Concentration range tracking (with provenance)

### CANNOT reliably simulate:

- That a compound cures a disease
- That a predicted reaction actually occurs experimentally
- Human safety or toxicity
- Clinical efficacy
- Pharmacological effectiveness
- Real concentrations inside plants (database-derived only)
- Real-world pharmacokinetics
- Real biological outcomes
- Quantum chemical results for large molecules (>100 atoms on CPU)
- Molecular dynamics beyond nanosecond timescales (CPU)
- Experimental confirmation of any computational prediction

This distinction is FUNDAMENTAL to the architecture — see Evidence Classification below.

---

## 2. Dependency Audit

### 2.1 RDKit (Cheminformatics Core)

| Property | Value |
|---|---|
| What it does | Cheminformatics toolkit: SMILES parsing, fingerprints, descriptors, reactions, substructure search, molecular visualization |
| Open source | Yes |
| License | BSD-3-Clause |
| Python compatibility | 3.14 ✅ (rdkit 2026.3.6 has cp314 wheel) |
| Windows compatibility | ✅ (win_amd64 wheel available) |
| CPU/GPU requirements | CPU only; optional CUDA for some features |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A (local) |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed (BSD-3-Clause) |
| Scientific limitations | Predictions are computational only; not experimental validation |
| Reproducibility limitations | Deterministic given same version and input |
| Installation complexity | LOW — pip install rdkit (prebuilt wheel) |
| Install status (2026-09-20) | **VERIFIED AVAILABLE**: rdkit-2026.3.6 cp314 win_amd64 wheel found via dry-run |

**Critical role**: Core molecular engine. REQUIRED for all chemistry operations.

### 2.2 Open Babel

| Property | Value |
|---|---|
| What it does | Chemical toolbox: format conversion, 2D/3D rendering, file I/O, molecule operations |
| Open source | Yes |
| License | GPL-2.0 (with exceptions) |
| Python compatibility | 3.14 ✅ (openbabel 3.2.1 has cp314 wheel) |
| Windows compatibility | ✅ (win_amd64 wheel available) |
| CPU/GPU requirements | CPU only |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A (local) |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ⚠️ GPL — may be problematic for commercial products |
| Scientific limitations | Format conversion utility; computational predictions are approximate |
| Reproducibility limitations | Deterministic for conversions |
| Installation complexity | MEDIUM — GPL license consideration; pip install openbabel |
| Install status (2026-09-20) | **VERIFIED AVAILABLE**: openbabel-3.2.1 cp314 win_amd64 wheel found |

**Critical role**: Format converter and supplementary molecule operations. OPTIONAL.

### 2.3 OpenMM (Molecular Dynamics)

| Property | Value |
|---|---|
| What it does | Molecular dynamics simulation engine; GPU-accelerated |
| Open source | Yes |
| License | LGPL (custom) |
| Python compatibility | 3.14 ✅ (openmm 8.6.1 has cp314 wheel) |
| Windows compatibility | ✅ (win_amd64 wheel available) |
| CPU/GPU requirements | CPU ✅, GPU optional (CUDA/ROCm/Metal) |
| NVIDIA/CUDA requirements | Optional — CUDA enables GPU acceleration |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A (local) |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed (LGPL) |
| Scientific limitations | Classical mechanics only; force field accuracy depends on parameterization |
| Reproducibility limitations | Deterministic given same seed, platform, and version |
| Installation complexity | LOW-MEDIUM — pip install openmm (prebuilt wheel); CUDA optional |
| Install status (2026-09-20) | **VERIFIED AVAILABLE**: openmm-8.6.1 cp314 win_amd64 wheel found |

**Critical role**: Molecular dynamics engine (Phase 12). REQUIRED for MD module.

### 2.4 Psi4 (Quantum Chemistry)

| Property | Value |
|---|---|
| What it does | Ab initio quantum chemistry: HF, DFT, post-HF methods, excited states |
| Open source | Yes |
| License | LGPL |
| Python compatibility | ⚠️ UNCERTAIN — PySCF distribution; Python 3.14 support unknown |
| Windows compatibility | ⚠️ PROBLEMATIC — typically requires compilation; no prebuilt wheel found |
| CPU/GPU requirements | CPU ✅, GPU optional (CUDA) |
| NVIDIA/CUDA requirements | Optional |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A (local) |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed (LGPL) |
| Scientific limitations | Basis set dependence; correlation energy truncated |
| Reproducibility limitations | Platform-dependent floating point; must record hardware |
| Installation complexity | **HIGH** — no prebuilt Python 3.14 wheel; source compilation requires C/C++ compiler (absent) |
| Install status (2026-09-20) | **BLOCKED**: No Python 3.14 prebuilt wheel; no C/C++ compiler; cannot compile from source |

**Mitigation**: Use PySCF (which has better packaging) or restrict QC to small molecules via RDKit descriptors. Install via conda if available later.

### 2.5 PySCF (Quantum Chemistry)

| Property | Value |
|---|---|
| What it does | Python Simulations of Chemistry Framework; DFT, HF, post-HF, TDDFT |
| Open source | Yes |
| License | Apache-2.0 |
| Python compatibility | ⚠️ PySCF 2.14.0 is sdist (tar.gz); Python 3.14 support UNVERIFIED |
| Windows compatibility | ⚠️ PROBLEMATIC — source distribution; requires compilation |
| CPU/GPU requirements | CPU ✅, GPU optional (CUDA, requires PySCF CUDA build) |
| NVIDIA/CUDA requirements | Optional (requires CUDA toolkit + PySCF CUDA variant) |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A (local) |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed (Apache-2.0) |
| Scientific limitations | Basis set dependence; active space limitations for multi-reference |
| Reproducibility limitations | Platform-dependent; must record hardware + library versions |
| Installation complexity | **HIGH** — source build required; needs h5py, psutil, C/Fortran compilers |
| Install status (2026-09-20) | **BLOCKED**: No prebuilt Python 3.14 wheel; source build requires compilers absent from system |

**Mitigation**: Defer QC module until compiler toolchain installed OR use RDKit descriptor-based approximations. Alternatively, install via conda-forge if conda added later.

### 2.6 Biopython

| Property | Value |
|---|---|
| What it does | Biological computation: sequence analysis, structure parsing, database access |
| Open source | Yes |
| License | Biopython License (similar to MIT/BSD) |
| Python compatibility | 3.14 ✅ (biopython 1.88 has cp314 wheel) |
| Windows compatibility | ✅ (win_amd64 wheel available) |
| CPU/GPU requirements | CPU only |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes (local operations); ⚠️ Requires internet for PDB/UniProt/NCBI fetchers |
| Requires API | No (local); Optional: NCBI E-utilities, RCSB PDB REST |
| API free | N/A (local); Web APIs are free |
| Rate limits | NCBI: 3 requests/sec (with email); RCSB: rate-limited |
| Dataset licensing | Varies by database (public) |
| Commercial use | ✅ Allowed |
| Scientific limitations | Database access layer only; data accuracy depends on source |
| Reproducibility limitations | Deterministic for local ops; web data changes over time |
| Installation complexity | LOW — pip install biopython (prebuilt wheel) |
| Install status (2026-09-20) | **VERIFIED AVAILABLE**: biopython-1.88 cp314 win_amd64 wheel found |

**Critical role**: Protein/nucleic acid sequence handling, PDB parsing for docking targets. REQUIRED for biological knowledge engine (Phase 14).

### 2.7 PubChemPy (Database Access)

| Property | Value |
|---|---|
| What it does | Python wrapper for PubChem REST API: compound search, property retrieval |
| Open source | Yes |
| License | MIT |
| Python compatibility | 3.14 ✅ (pure Python, PubChemPy 1.0.5) |
| Windows compatibility | ✅ (pure Python) |
| CPU/GPU requirements | N/A (network I/O) |
| NVIDIA/CUDA requirements | No |
| Works offline | ❌ No — requires PubChem REST API |
| Requires API | Yes — PubChem PUG-REST |
| API free | ✅ Yes |
| Rate limits | PubChem recommends ≤ 3 requests/sec |
| Dataset licensing | Public domain (PubChem data) |
| Commercial use | ✅ Allowed |
| Scientific limitations | Only covers PubChem-catalogued compounds |
| Reproducibility limitations | Data changes over time; must cache and timestamp |
| Installation complexity | VERY LOW — pip install pubchempy (pure Python) |
| Install status (2026-09-20) | **VERIFIED AVAILABLE**: PubChemPy-1.0.5 pure Python wheel found |

**Critical role**: Novelty checker, compound lookup (Phase 16). REQUIRED.

### 2.8 NetworkX (Knowledge Graph)

| Property | Value |
|---|---|
| What it does | Graph/network analysis and visualization |
| Open source | Yes |
| License | BSD-3-Clause |
| Python compatibility | 3.14 ✅ (networkx 3.6.1 installed) |
| Windows compatibility | ✅ |
| CPU/GPU requirements | CPU only |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A (local) |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed |
| Scientific limitations | Graph algorithms are exact; knowledge graph completeness depends on data |
| Reproducibility limitations | Deterministic |
| Installation complexity | NONE — already installed (3.6.1) |
| Install status (2026-09-20) | **INSTALLED**: 3.6.1 ✅ |

**Critical role**: Knowledge graph backbone (Phase 14). REQUIRED.

### 2.9 NumPy / SciPy / Pandas (Numerical Core)

| Property | Value |
|---|---|
| What they do | Numerical computation, scientific computing, data manipulation |
| Open source | Yes (BSD / BSD / BSD) |
| License | BSD-3-Clause / BSD / BSD |
| Python compatibility | 3.14 ✅ (installed) |
| Windows compatibility | ✅ |
| CPU/GPU requirements | CPU (numpy/scipy); optional GPU (CuPy alternative not installed) |
| NVIDIA/CUDA requirements | No (unless using CuPy) |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed |
| Scientific limitations | Floating-point precision limits; algorithm-specific |
| Reproducibility limitations | Deterministic given version + platform + seed |
| Installation complexity | NONE — installed |
| Install status (2026-09-20) | **INSTALLED**: numpy 2.5.3, scipy 1.18.1, pandas 3.0.6 ✅ |

### 2.10 Matplotlib / Plotly (Visualization)

| Property | Value |
|---|---|
| What they do | 2D/3D plotting, molecular visualization, dashboard charts |
| Open source | Yes |
| License | matplotlib: PSF-like; Plotly: MIT |
| Python compatibility | 3.14 ✅ |
| Windows compatibility | ✅ |
| CPU/GPU requirements | CPU only |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed |
| Scientific limitations | Rendering quality varies by backend; 2D only for matplotlib |
| Reproducibility limitations | Deterministic for data; rendering may vary by backend |
| Installation complexity | NONE (matplotlib) / LOW (plotly) |
| Install status (2026-09-20) | matplotlib INSTALLED 3.11.2 ✅; plotly AVAILABLE (would install 7.1.0) |

### 2.11 scikit-learn / scikit-image (Statistics/Image Analysis)

| Property | Value |
|---|---|
| What they do | Machine learning, statistical analysis, image processing |
| Open source | Yes |
| License | BSD-3-Clause |
| Python compatibility | 3.14 ✅ |
| Windows compatibility | ✅ |
| CPU/GPU requirements | CPU only |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed |
| Scientific limitations | Model accuracy depends on training data; not a substitute for domain expertise |
| Reproducibility limitations | Deterministic given seed and version |
| Installation complexity | NONE — installed |
| Install status (2026-09-20) | **INSTALLED**: scikit-learn 1.9.1, scikit-image 0.26.0 ✅ |

### 2.12 PyTorch (Deep Learning / Property Prediction)

| Property | Value |
|---|---|
| What it does | Deep learning framework; molecular property prediction models |
| Open source | Yes |
| License | BSD |
| Python compatibility | 3.14 ✅ (torch 2.14.0+cpu installed) |
| Windows compatibility | ✅ |
| CPU/GPU requirements | CPU ✅ (installed as +cpu); GPU ❌ (no CUDA wheel installed) |
| NVIDIA/CUDA requirements | Requires CUDA toolkit + cuDNN for GPU (GTX 1080 supports up to CUDA 12.x) |
| Works offline | ✅ Yes (inference); training benefits from GPU |
| Requires API | No |
| API free | N/A |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed (BSD) |
| Scientific limitations | Model predictions are approximate; generalization not guaranteed |
| Reproducibility limitations | Deterministic on CPU; GPU may have minor float non-determinism |
| Installation complexity | NONE — installed (CPU version) |
| Install status (2026-09-20) | **INSTALLED**: torch 2.14.0+cpu, torchvision 0.29.0+cpu ✅ |

### 2.13 FastAPI (Web Backend)

| Property | Value |
|---|---|
| What it does | Async web framework for API endpoints (UI backend, agent communication) |
| Open source | Yes |
| License | MIT |
| Python compatibility | 3.14 ✅ (fastapi 0.141.1 available) |
| Windows compatibility | ✅ |
| CPU/GPU requirements | CPU only |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes (local server) |
| Requires API | No (local server) |
| API free | N/A |
| Rate limits | N/A (local) |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed |
| Scientific limitations | N/A (infrastructure, not scientific) |
| Reproducibility limitations | N/A |
| Installation complexity | LOW — pip install fastapi (available; would also need uvicorn) |
| Install status (2026-09-20) | **AVAILABLE**: Would install fastapi 0.141.1 + starlette 1.6.0 |

### 2.14 SQLAlchemy (Database ORM)

| Property | Value |
|---|---|
| What it does | Database ORM; abstracts SQLite/PostgreSQL |
| Open source | Yes |
| License | MIT |
| Python compatibility | 3.14 ✅ (SQLAlchemy 2.0.54 available) |
| Windows compatibility | ✅ |
| CPU/GPU requirements | CPU only |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes (local SQLite) |
| Requires API | No |
| API free | N/A |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed |
| Scientific limitations | N/A |
| Reproducibility limitations | N/A |
| Installation complexity | LOW — pip install sqlalchemy |
| Install status (2026-09-20) | **AVAILABLE**: Would install SQLAlchemy 2.0.54 |

### 2.15 Dash / Streamlit (Dashboard UI)

| Property | Value (Dash) | Value (Streamlit) |
|---|---|---|
| What it does | Interactive web dashboard | Interactive web dashboard |
| Open source | Yes | Yes |
| License | MIT | Apache-2.0 |
| Python compatibility | 3.14 ✅ (4.4.1) | 3.14 ✅ (1.64.0) |
| Windows compatibility | ✅ | ✅ |
| CPU/GPU requirements | CPU only | CPU only |
| NVIDIA/CUDA requirements | No | No |
| Works offline | ✅ Yes | ✅ Yes |
| Requires API | No | No |
| API free | N/A | N/A |
| Rate limits | N/A | N/A |
| Dataset licensing | N/A | N/A |
| Commercial use | ✅ Allowed | ✅ Allowed |
| Scientific limitations | N/A | N/A |
| Reproducibility limitations | N/A | N/A |
| Installation complexity | LOW (includes plotly) | MEDIUM (many deps: altair, pyarrow, etc.) |
| Install status (2026-09-20) | DASH AVAILABLE; STREAMlit AVAILABLE |

**Recommendation**: Use **Dash** — lighter dependency tree, better for embedding Plotly charts which are needed for molecular visualization.

### 2.16 SymPy (Symbolic Mathematics)

| Property | Value |
|---|---|
| What it does | Symbolic math: equation solving, calculus, algebra |
| Open source | Yes |
| License | BSD |
| Python compatibility | 3.14 ✅ (sympy 1.14.0 installed) |
| Windows compatibility | ✅ |
| CPU/GPU requirements | CPU only |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | ✅ Allowed |
| Scientific limitations | Symbolic, not numerical; performance limits on complex expressions |
| Reproducibility limitations | Deterministic |
| Installation complexity | NONE — installed |
| Install status (2026-09-20) | **INSTALLED**: sympy 1.14.0 ✅ |

### 2.17 PyQt5 / PySide6 (GUI)

| Property | Value |
|---|---|
| What they do | Desktop GUI framework |
| Open source | Yes |
| License | PyQt5: GPL/COMmercial; PySide6: LGPL |
| Python compatibility | 3.14 ✅ (both installed) |
| Windows compatibility | ✅ |
| CPU/GPU requirements | CPU only |
| NVIDIA/CUDA requirements | No |
| Works offline | ✅ Yes |
| Requires API | No |
| API free | N/A |
| Rate limits | N/A |
| Dataset licensing | N/A |
| Commercial use | PyQt5: ⚠️ GPL; PySide6: ✅ LGPL |
| Scientific limitations | N/A |
| Reproducibility limitations | N/A |
| Installation complexity | NONE — both installed |
| Install status (2026-09-20) | **INSTALLED**: PyQt5 5.15.11, PySide6 6.11.2 ✅ |

**Recommendation**: Use **PySide6** (LGPL) over PyQt5 (GPL) for commercial-friendly licensing.

---

## 3. Blocked / Problematic Dependencies

| Dependency | Issue | Mitigation |
|---|---|---|
| **Psi4** | No Python 3.14 wheel; requires compilation; no C/C++ compiler | Defer QC module; use RDKit descriptors as proxy; install conda later if needed |
| **PySCF** | Source distribution only; requires Fortran/C compilers | Same as Psi4; or install via conda-forge |
| **wheel** | Not installed in global Python | Install: `pip install wheel` |
| **CUDA toolkit** | GTX 1080 present but toolkit not verified in PATH | GPU acceleration deferred until confirmed; CPU mode is primary |
| **conda** | Not installed | Consider Miniconda for PySCF/Psi4 if needed |

---

## 4. Local vs Cloud Capabilities

### CAN run 100% locally:
- Molecular structure handling (RDKit)
- Molecular descriptors, fingerprints, similarity (RDKit)
- Reaction SMARTS and known reaction rules (RDKit)
- Molecular dynamics on CPU (OpenMM)
- Knowledge graph (NetworkX + SQLite)
- Database operations (SQLite via SQLAlchemy)
- Statistical analysis (scipy, numpy, scikit-learn)
- Dashboard (Dash + Plotly)
- Literature/database lookups via REST API (pubchempy, biopython) — requires internet but is API-based
- Plant/natural product database (custom SQLite)
- Evidence tracking system (custom)
- Report generation (custom + markdown)
- Statistical validation (scipy, numpy)

### REQUIRES internet (APIs):
- PubChem compound lookups (pubchempy → PUG-REST)
- RCSB PDB structure fetch (biopython → REST)
- ChEBI/ChEMBL lookups (REST APIs, free)
- NCBI literature search (biopython → E-utilities, free, rate-limited)
- Semantic Scholar (REST API, free)
- CrossRef/arXiv metadata (free APIs)

### CANNOT run locally (blocked):
- Psi4 quantum chemistry (no compiler, no wheel)
- PySCF quantum chemistry (no compiler, no wheel)
- GPU-accelerated MD/DL (no CUDA toolkit confirmed)
- Large-scale molecular dynamics (>100ns on CPU)

---

## 5. Dataset Assessment

| Dataset | Access | License | Free? | Local? | Notes |
|---|---|---|---|---|---|
| PubChem | REST API | Public Domain | ✅ | ❌ API | Primary compound source |
| ChEBI | REST API | CC BY-SA 4.0 | ✅ | ❌ API | Small molecule ontology |
| ChEMBL | REST API | CC BY-SA 3.0 | ✅ | ❌ API | Bioactivity data |
| DrugBank | REST API | CC BY-NC 4.0 | ⚠️ Non-commercial | ❌ API | Drug-focused |
| RCSB PDB | REST API | Open Access | ✅ | ❌ API | Protein structures |
| NCBI/PubMed | REST API | Public | ✅ | ❌ API | Literature |
| UniProt | REST API | Open Access | ✅ | ❌ API | Protein sequences |
| KEGG | REST API | ❌ Restricted | ❌ | ❌ API | Commercial license required |
| USDA FoodData Central | REST API | Public | ✅ | ❌ API | Food composition |
| Wikipedia/Wikidata | REST API | CC BY-SA 3.0 | ✅ | ❌ API | General knowledge |
| Local SQLite | N/A | N/A | N/A | ✅ | Primary storage |

---

## 6. Risk Assessment

| Risk | Severity | Probability | Mitigation |
|---|---|---|---|
| Python 3.14 compatibility gaps | HIGH | MEDIUM | All critical packages (RDKit, OpenMM, Bio) verified; QC deferred |
| No C/C++ compiler | HIGH | CERTAIN | QC module deferred; document as Phase 2 capability |
| CUDA toolkit unavailable | MEDIUM | HIGH | CPU mode primary; GPU optional |
| REST API rate limiting | MEDIUM | HIGH | Implement caching layer with timestamps; respect rate limits |
| PySide6 LGPL compliance | LOW | LOW | Maintain license notice in about dialog |
| Data drift in API-sourced data | MEDIUM | HIGH | Cache + timestamp all external data; never treat as current |
| RDKit version pinning | MEDIUM | MEDIUM | Pin version in requirements; test on upgrades |
| pandas 3.x breaking changes | LOW | MEDIUM | Test migration; code defensively |
| Network dependency for core features | HIGH | MEDIUM | All features designed to degrade gracefully offline |
| GPT hallucination of chemical data | CRITICAL | HIGH | Evidence classification (E0-E6); structural validation; provenance tracking |

---

## 7. Implementation Roadmap

### Phase A: Foundation (Week 1)
- [ ] Install verified packages: rdkit, openmm, openbabel, biopython, pubchempy, h5py, psutil, wheel
- [ ] Verify RDKit import and basic molecule operations
- [ ] Verify OpenMM import and basic simulation
- [ ] Set up SQLite database schema (Phase 4 entities)
- [ ] Implement evidence classification system (E0-E6)

### Phase B: Core Engines (Week 2-3)
- [ ] Build Molecular Engine (Phase 6): SMILES, InChI, descriptors, fingerprints
- [ ] Build Plant/Natural-Product Engine (Phase 5): taxonomy, constituents, evidence
- [ ] Build Reaction Engine (Phase 8): reaction SMARTS, products, feasibility
- [ ] Build Virtual Mixer (Phase 7): ingredient decomposition, interaction classification

### Phase C: Simulation Layer (Week 4)
- [ ] Build Simulation Engine abstraction (Phase 10)
- [ ] Implement RDKitAdapter (property prediction, similarity)
- [ ] Implement OpenMMAdapter (molecular dynamics)
- [ ] Build Docking module (Phase 11)
- [ ] Build Molecular Dynamics module (Phase 12)

### Phase D: AI & Intelligence (Week 5-6)
- [ ] Build Novelty Engine (Phase 16): PubChem/ChEBI/ChEMBL lookups
- [ ] Build Hypothesis Engine (Phase 17): structured hypothesis generation
- [ ] Build Adversarial Scientist (Phase 18): disproof agent
- [ ] Build Literature Research Agent (Phase 15): search, extract, link
- [ ] Build Statistical Validation (Phase 19)

### Phase E: Infrastructure (Week 7)
- [ ] Build Experiment Manager (Phase 20): immutable records, clone, replay
- [ ] Build Compute Scheduler (Phase 31): job queue, priorities
- [ ] Build Failure Recovery (Phase 32)
- [ ] Build Observation/Monitoring (Phase 47)

### Phase F: UI (Week 8-9)
- [ ] Build Dashboard UI (Phase 22)
- [ ] Build Visual Lab UI (Phase 21): dark theme, molecular viz
- [ ] Build Nav navigation for all 16 sections
- [ ] Build Experiment Replay UI (Phase 23)

### Phase G: Validation (Week 10)
- [ ] Red-team testing (Phase 35)
- [ ] Scientific test suite (Phase 34)
- [ ] Unit/integration tests (Phase 33)
- [ ] Final audit (Phase 48)

### Phase H: Polish & Deliver (Week 11-12)
- [ ] Documentation (Phase 39)
- [ ] Report generation (Phase 36)
- [ ] Export system (Phase 37)
- [ ] GitHub quality (Phase 38)
- [ ] Final deliverable (Phase 49)

---

## 8. Recommendations

1. **Start with RDKit** — it is the highest-value, lowest-risk dependency. Verified installable on Python 3.14 Windows.
2. **Defer quantum chemistry** — Psi4/PySCF blocked by compiler absence. Design the QM engine interface now; implement later when toolchain available.
3. **Use SQLite first** — local-first, zero-config, migratable to PostgreSQL later.
4. **Cache all external data** — API responses must be timestamped and cached locally to ensure reproducibility and offline operation.
5. **Implement evidence classification first** — E0-E6 must be the backbone of every data structure before any scientific code is written.
6. **Pin all versions** — create requirements.txt immediately after verified installs.
7. **CPU-first design** — GTX 1080 CUDA status unknown; design for CPU and add GPU as optional acceleration.
