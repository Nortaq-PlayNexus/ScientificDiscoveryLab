# IMPLEMENTATION ROADMAP

SOVEREIGN BIOCHEMICAL DISCOVERY LAB — Development Phases

Date: 2026-09-20

---

## Phase 0: Pre-Development (Current)

**Status**: ✅ COMPLETE

- [x] Technical reconnaissance (RESEARCH_RECONNAISSANCE.md)
- [x] System architecture design (ARCHITECTURE.md)
- [x] Dependency matrix (DEPENDENCY_MATRIX.md)
- [x] Risk register (RISK_REGISTER.md)
- [x] This roadmap

**Deliverables**: All docs in `docs/`

---

## Phase 1: Foundation (Week 1)

**Goal**: Core infrastructure ready for scientific code

### 1.1 Environment Setup
- [ ] Install verified packages (rdkit, openmm, openbabel, biopython, pubchempy, h5py, psutil)
- [ ] Install wheel (prerequisite for compilation packages)
- [ ] Verify RDKit: create molecule from SMILES, compute descriptors, fingerprints
- [ ] Verify OpenMM: create simple system, run 100-step simulation
- [ ] Create requirements.txt with pinned versions
- [ ] Set up project directory structure per ARCHITECTURE.md

### 1.2 Evidence System
- [ ] Implement E0-E6 classification enum
- [ ] Create Evidence model (source, timestamp, version, parameters, seed, method, output, uncertainty, level)
- [ ] Implement evidence validation rules

### 1.3 Database
- [ ] Set up SQLite via SQLAlchemy
- [ ] Implement all Phase 4 entities (Plant, Compound, Molecule, Reaction, Experiment, Evidence, etc.)
- [ ] Implement stable ID generation (PLANT-000001, CMP-000001, etc.)
- [ ] Write initial migration
- [ ] Test CRUD operations

### 1.4 Validation Layer
- [ ] SMILES validator (via RDKit)
- [ ] Structure validator (valence, stereochemistry, etc.)
- [ ] Reaction SMARTS validator

**Exit Criteria**: Database stores all entity types; evidence classification working; SMILES validation working

---

## Phase 2: Core Chemistry (Week 2-3)

**Goal**: Molecular and plant engines operational

### 2.1 Molecular Engine (Phase 6)
- [ ] SMILES ↔ InChI ↔ InChIKey conversion
- [ ] Molecular formula, molecular weight
- [ ] Canonicalization
- [ ] Stereochemistry (R/S, E/Z, tetrahedral, cis/trans)
- [ ] Fingerprints (Morgan, MACCS, structural)
- [ ] Descriptors (LogP, TPSA, HBD, HBA, rotatable bonds, formal charge, stereocenters)
- [ ] Functional group identification
- [ ] Salt and tautomer handling
- [ ] Duplicate detection
- [ ] Substructure search
- [ ] Similarity search (Tanimoto, Dice)
- [ ] Molecule Inspector (2D structure, all descriptors, known sources, evidence)

### 2.2 Plant Engine (Phase 5)
- [ ] Plant schema (taxonomy, names, parts, constituents, concentrations, extracts, literature, evidence)
- [ ] Plant part types (berries, fruits, herbs, roots, etc.)
- [ ] UNKNOWN placeholder for missing data (no invention)
- [ ] Concentration range tracking with uncertainty
- [ ] Plant database CRUD
- [ ] Plant → Compound relationship management

### 2.3 Reaction Engine (Phase 8)
- [ ] Reaction SMARTS parsing
- [ ] Product prediction from reactants + SMARTS
- [ ] Reaction classification
- [ ] Feasibility estimation (from known rules)
- [ ] Literature reference linking
- [ ] Confidence scoring
- [ ] Evidence level assignment

### 2.4 Virtual Mixer (Phase 7)
- [ ] Ingredient selection interface (Plant, Compound, Extract, Ingredient)
- [ ] Condition configuration (Temperature, pH, Solvent, Concentration, Time, Oxygen, Light, Water, Enzyme, Environment)
- [ ] Ingredient decomposition into known compounds
- [ ] Interaction classification (KNOWN, PREDICTED, NO KNOWN, INSUFFICIENT DATA, POTENTIAL)
- [ ] Mixture analysis with evidence tracking

**Exit Criteria**: Molecule Inspector fully functional; Plant database populated with test data; Virtual Mixer classifies interactions; Reaction Engine predicts products for known reactions

---

## Phase 3: Simulation Layer (Week 4)

**Goal**: Abstract simulation engine with first adapters

### 3.1 Simulation Engine Interface
- [ ] Abstract SimulationEngine class
- [ ] Common interface: Docking, MD, QC, Property Prediction, Reaction Modeling

### 3.2 RDKit Adapter
- [ ] Property prediction
- [ ] Similarity calculations
- [ ] Descriptor computation
- [ ] Fingerprint comparison

### 3.3 OpenMM Adapter
- [ ] Molecular dynamics setup
- [ ] Force field application
- [ ] Trajectory generation
- [ ] Analysis (RMSD, RMSF, radius of gyration, H-bonds, energy)
- [ ] Trajectory visualization

### 3.4 Docking Module (Phase 11)
- [ ] Target loading (PDB via Biopython)
- [ ] Ligand preparation (RDKit)
- [ ] Docking execution (or scoring function)
- [ ] Result display: pose, score, interactions
- [ ] Disclaimer: "DOCKING IS A COMPUTATIONAL HYPOTHESIS, NOT CLINICAL EVIDENCE"

**Exit Criteria**: OpenMM runs 100-step simulation of small molecule in water; Docking scores computed with proper caveats

---

## Phase 4: AI & Intelligence (Week 5-6)

**Goal**: Hypothesis generation, novelty, adversarial testing

### 4.1 Literature Research Agent (Phase 15)
- [ ] PubMed search interface
- [ ] Semantic Scholar search interface
- [ ] Claim extraction
- [ ] Compound/target extraction
- [ ] Contradiction detection
- [ ] Citation validation (check DOI resolves)
- [ ] Literature source database

### 4.2 Novelty Engine (Phase 16)
- [ ] PubChem search
- [ ] ChEBI search
- [ ] ChEMBL search
- [ ] Reaction database search
- [ ] Known molecule/reaction/plant/source determination
- [ ] Output: "No matching record found in searched sources as of [DATE]" (never "first discovery")

### 4.3 Hypothesis Engine (Phase 17)
- [ ] Structured hypothesis creation
- [ ] Rationale, assumptions, predictions, tests, falsification criteria
- [ ] Status management (PROPOSED → TESTING → SUPPORTED/REFUTED/INCONCLUSIVE)
- [ ] Confidence tracking
- [ ] Evidence linking

### 4.4 Adversarial Scientist (Phase 18)
- [ ] Artifact detection checklist
- [ ] Alternative explanation generation
- [ ] Parameter sensitivity analysis
- [ ] Method comparison
- [ ] Authority to reject findings

### 4.5 Statistical Validation (Phase 19)
- [ ] Null models
- [ ] Bootstrap
- [ ] Permutation tests
- [ ] Effect sizes and CIs
- [ ] Multiple-testing correction (BH-FDR)
- [ ] Sensitivity analysis
- [ ] Reproducibility tests

**Exit Criteria**: End-to-end flow: hypothesis generated → novelty checked → adversarial tested → statistics computed → evidence classified

---

## Phase 5: Infrastructure (Week 7)

**Goal**: Experiment management, scheduling, monitoring

### 5.1 Experiment Manager (Phase 20)
- [ ] Immutable experiment records (EXP-######)
- [ ] Clone/modify/re-run/compare/branch/merge operations
- [ ] Complete metadata storage (question, hypothesis, inputs, params, versions, seeds, methods, outputs, logs, evidence, criticism)
- [ ] Experiment browser UI

### 5.2 Compute Scheduler (Phase 31)
- [ ] Job queue with priorities
- [ ] Resource estimation (compute, RAM, GPU, CPU)
- [ ] Job statuses (QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED, RETRYING)
- [ ] Parallel execution when resources permit
- [ ] Dependency tracking between jobs

### 5.3 Failure Recovery (Phase 32)
- [ ] Error capture
- [ ] Log preservation
- [ ] Experiment marked failed (immutable)
- [ ] Diagnosis suggestions
- [ ] Safe retry mechanism
- [ ] Original results never overwritten

### 5.4 Observation System (Phase 47)
- [ ] System Monitor
- [ ] Simulation Monitor
- [ ] Agent Monitor
- [ ] Database Monitor
- [ ] Compute Monitor
- [ ] Error Monitor
- [ ] Action trace logging (timestamped, agent-attributed)

**Exit Criteria**: Full experiment lifecycle tested; scheduler runs multiple jobs; failure recovery tested; monitoring operational

---

## Phase 6: UI (Week 8-9)

**Goal**: Complete user interface

### 6.1 Visual Lab UI (Phase 21)
- [ ] Dark background theme
- [ ] Subtle scientific grid
- [ ] Neon laboratory accents
- [ ] Molecular visualizations (Plotly)
- [ ] Animated but restrained
- [ ] High information density
- [ ] Professional scientific dashboard
- [ ] Responsive layout

### 6.2 Dashboard (Phase 22)
- [ ] Active Experiments display
- [ ] Running Simulations
- [ ] Hypotheses status
- [ ] Candidate Molecules
- [ ] Potential Reactions
- [ ] Literature Sources
- [ ] Reproduced/Refuted Results
- [ ] Evidence Distribution chart (E0-E6)
- [ ] Compute Usage

### 6.3 Navigation
- [ ] All 16 nav sections: Dashboard, Plants, Compounds, Molecules, Virtual Mixer, Reactions, Targets, Docking, MD, Quantum, Literature, Experiments, Hypotheses, Knowledge Graph, Novelty, Statistics, Research Swarm, Reports, Settings
- [ ] Active state management
- [ ] Breadcrumb navigation

### 6.4 Experiment Replay (Phase 23)
- [ ] REPRODUCE button per experiment
- [ ] Reconstruct: exact inputs, parameters, environment, seeds, versions
- [ ] Compare original vs reproduction
- [ ] Output: REPRODUCED / PARTIALLY REPRODUCED / FAILED REPRODUCTION

**Exit Criteria**: Full dark UI with all sections navigable; dashboard populated with data; experiment replay functional

---

## Phase 7: Advanced Features (Week 10)

**Goal**: Biological, quantum, and advanced analysis

### 7.1 Biological Knowledge Engine (Phase 14)
- [ ] Compound → Target → Pathway → Biological Process graph
- [ ] Literature evidence linking
- [ ] Knowledge graph visualization
- [ ] Pathway enrichment analysis

### 7.2 QM Engine (Phase 13)
- [ ] Geometry optimization interface (deferred — requires compiler)
- [ ] Energy, dipole moment, orbital info placeholders
- [ ] CPU-friendly defaults
- [ ] Clear labeling of approximation level
- [ ] Note: blocked until compiler/Conda available

### 7.3 Report Generator (Phase 36)
- [ ] Report template (title, question, background, hypothesis, methods, datasets, environment, results, statistics, figures, tables, uncertainty, alternatives, negative results, adversarial, reproducibility, limitations, conclusion, references, manifest)
- [ ] Markdown export
- [ ] JSON export
- [ ] CSV export
- [ ] HTML export
- [ ] PDF export (via external tool)

### 7.4 Export System (Phase 37)
- [ ] Experiment bundle export (manifest.json, parameters.json, inputs/, outputs/, structures/, trajectories/, figures/, logs/, report.md, provenance.json)

**Exit Criteria**: Knowledge graph populated; reports generated; data exported correctly

---

## Phase 8: Validation & Quality (Week 11)

**Goal**: Comprehensive testing and validation

### 8.1 Testing (Phase 33)
- [ ] Unit tests (molecule validation, reaction generation, duplicate handling, stereochemistry)
- [ ] Integration tests (database integrity, pipeline flow)
- [ ] Scientific tests (descriptor accuracy, reaction feasibility)
- [ ] Reproducibility tests (re-run same experiment, compare results)
- [ ] Data tests (malformed data handling, missing fields)
- [ ] Security tests (arbitrary code execution prevention, input sanitization)
- [ ] UI tests (navigation, rendering)

### 8.2 Scientific Test Suite (Phase 34)
- [ ] BENCH-001: Known molecule descriptor calculation
- [ ] BENCH-002: Known reaction
- [ ] BENCH-003: Known ligand-target interaction
- [ ] BENCH-004: Known MD trajectory property
- [ ] BENCH-005: Known quantum calculation (deferred)
- [ ] BENCH-006: Known literature relationship

### 8.3 Red Team (Phase 35)
- [ ] Invalid SMILES rejection test
- [ ] Impossible structure detection
- [ ] Duplicate compound handling
- [ ] Fake citation detection
- [ ] Missing metadata flagging
- [ ] Contradictory source detection
- [ ] Absurd concentration rejection
- [ ] Invalid pH rejection
- [ ] Negative concentration rejection
- [ ] Impossible temperature rejection
- [ ] Corrupted dataset detection

**Exit Criteria**: All tests passing; benchmark experiments within expected ranges; red-team inputs all rejected/flagged

---

## Phase 9: Polish & Deliverable (Week 12)

**Goal**: Production-ready deliverable

### 9.1 Documentation (Phase 39)
- [ ] docs/architecture.md ✅
- [ ] docs/scientific-methodology.md
- [ ] docs/evidence-model.md
- [ ] docs/provenance.md
- [ ] docs/simulations.md
- [ ] docs/reactions.md
- [ ] docs/molecular-dynamics.md
- [ ] docs/quantum.md
- [ ] docs/literature.md
- [ ] docs/novelty.md
- [ ] docs/reproducibility.md
- [ ] docs/datasets.md
- [ ] docs/installation.md
- [ ] docs/development.md
- [ ] docs/limitations.md

### 9.2 GitHub Quality (Phase 38)
- [ ] README.md (overview, scope, architecture, screenshots, installation, quick start, examples, engines, limitations, reproducibility, citation, contribution)
- [ ] LICENSE (MIT or Apache-2.0)
- [ ] CONTRIBUTING.md
- [ ] SECURITY.md
- [ ] CITATION.cff
- [ ] CHANGELOG.md
- [ ] CODE_OF_CONDUCT.md
- [ ] .gitignore
- [ ] Pyproject.toml or requirements.txt

### 9.3 Final Audit (Phase 48)
- [ ] Data: Are sources real? Citations real? Structures valid?
- [ ] Chemistry: Generated molecules valid? Reactions structurally valid?
- [ ] Simulation: Executing? Parameters recorded?
- [ ] Statistics: Null models? Multiple comparisons handled?
- [ ] Reproducibility: Can experiments rerun?
- [ ] AI: Can agents hallucinate? Fabricate citations? Bypass evidence?
- [ ] Security: Arbitrary code execution? Malformed data compromise?
- [ ] Scientific integrity: Prediction→fact? Association→causation? Docking→treatment?

### 9.4 Final Deliverable (Phase 49)
- [ ] FINAL_AUDIT.md
- [ ] SCIENTIFIC_VALIDATION.md
- [ ] KNOWN_LIMITATIONS.md
- [ ] REPRODUCIBILITY_REPORT.md
- [ ] Complete directory structure per Phase 49 spec

**Exit Criteria**: All docs present; all tests passing; audit complete; deliverable packaged

---

## Timeline Summary

| Week | Phase | Focus |
|---|---|---|
| 1 | Phase 1 | Foundation (env setup, evidence system, database, validation) |
| 2-3 | Phase 2 | Core Chemistry (molecular, plant, reaction, mixer) |
| 4 | Phase 3 | Simulation (RDKit, OpenMM, Docking) |
| 5-6 | Phase 4 | AI & Intelligence (literature, novelty, hypothesis, adversarial, statistics) |
| 7 | Phase 5 | Infrastructure (experiments, scheduler, failure recovery, monitoring) |
| 8-9 | Phase 6 | UI (dark theme, dashboard, navigation, replay) |
| 10 | Phase 7 | Advanced Features (biology, QC, reports, export) |
| 11 | Phase 8 | Validation (tests, benchmarks, red team) |
| 12 | Phase 9 | Polish & Deliverable (docs, GitHub quality, audit, package) |

---

## Dependencies Between Phases

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
  │                          │          │          │
  ▼                          ▼          ▼          ▼
 Evidence DB              RDKit     OpenMM     Agent comms
 SMILES engine            Molecule  MD Engine  via Experiment
 DB schema                Inspector Records   record
  │                          │          │          │
  └──────────────────────────┴──────────┴──────────┘
                           ▼
                    Phase 6 (UI)
                     │          │
                     ▼          ▼
              Phase 7       Phase 8
            (Features)    (Validation)
                     │          │
                     └────┬─────┘
                          ▼
                    Phase 9 (Deliverable)
```

---

## Success Criteria

The platform is complete when:
1. Every scientific claim has an E0-E6 evidence level
2. Every experiment is replayable
3. Every result has full provenance
4. The adversarial scientist can challenge every finding
5. The system degrades gracefully without internet
6. No LLM can insert fabricated chemical data without validation
7. All tests pass including red-team
8. Documentation is complete and accurate
9. The platform NEVER makes medical claims
10. Reproducibility is guaranteed (given same inputs, params, versions, seeds)
