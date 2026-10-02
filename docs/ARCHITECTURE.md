# ARCHITECTURE

SOVEREIGN BIOCHEMICAL DISCOVERY LAB — System Architecture

Date: 2026-09-20
Status: COMPLETE

---

## 1. High-Level Architecture

```
                     SOVEREIGN ORCHESTRATOR
                              |
               +--------------+--------------+
               |                             |
         RESEARCH SWARM                EXPERIMENT ENGINE
               |                             |
               +--------------+--------------+
                              |
                      KNOWLEDGE GRAPH
                              |
         +--------------------+--------------------+
         |                    |                    |
    PLANT DATABASE      CHEMICAL DATABASE    LITERATURE DB
         |                    |                    |
         +--------------------+--------------------+
                              |
                     MOLECULAR ENGINE
                              |
               +--------------+--------------+
               |              |              |
           REACTIONS       DOCKING           MD
               |              |              |
               +--------------+--------------+
                              |
                        QM ENGINE
                              |
                     ANALYSIS ENGINE
                              |
                   STATISTICS ENGINE
                              |
                      NOVELTY ENGINE
                              |
                     REPORT GENERATOR
```

---

## 2. System Components

### 2.1 Sovereign Orchestrator

The central command layer. Responsibilities:
- Parse user requests and route to appropriate engine
- Manage evidence classification (E0-E6) for ALL outputs
- Coordinate Research Swarm and Experiment Engine
- Enforce safety boundaries (no medical claims, no hallucinated data)
- Maintain global provenance registry
- Manage compute budget and job scheduling

### 2.2 Research Swarm

Specialized AI agents communicating through structured experiment records:
- **Researcher** — literature search, paper extraction, citation verification
- **Chemist** — molecule design, SMILES generation, structure validation
- **Cheminformatician** — fingerprints, descriptors, similarity, substructure search
- **Reaction Analyst** — reaction prediction, SMARTS matching, feasibility scoring
- **Molecular Simulation Specialist** — MD, docking, QM orchestration
- **Literature Analyst** — claim extraction, evidence grading, contradiction detection
- **Biology Analyst** — target-pathway-biological process linking
- **Statistics Analyst** — null models, multiple testing, effect sizes, CIs
- **Novelty Analyst** — database searching, prior-art checking
- **Adversarial Scientist** — disproof attempts, artifact detection
- **Reproducibility Scientist** — experiment replay, independent verification
- **Report Writer** — scientific report generation

Communication: All inter-agent communication via immutable experiment records. NO uncontrolled prose.

### 2.3 Experiment Engine

Manages the lifecycle of every computational experiment:
- Create immutable experiment record (EXP-######)
- Store: question, hypothesis, inputs, parameters, software versions, random seeds, methods, outputs, plots, logs, evidence, interpretation, criticism, reproduction status
- Clone, modify, re-run, compare, branch, merge operations
- Failure recovery (preserve logs, mark failed, diagnose, retry)
- Reproducibility: exact reconstruction via manifest

### 2.4 Knowledge Graph

Graph database linking all entities:
```
Compound → Target → Pathway → Biological Process → Literature Evidence
Plant → Species → Extract → Compound → Molecule
Reaction → Reactants → Products → Conditions → Literature
```

Implementation: NetworkX graph + SQLite backing store.

### 2.5 Plant Database

Structured plant/natural-product representation:
```
Plant
 ├── Taxonomy (kingdom → species)
 ├── Common names
 ├── Scientific name
 ├── Plant parts (leaves, roots, bark, etc.)
 ├── Known constituents (Compound references)
 ├── Concentration ranges (with uncertainty)
 ├── Extraction method
 ├── Literature (reference IDs)
 └── Evidence (classification, provenance)
```

Supported types: berries, fruits, vegetables, herbs, spices, roots, bark, leaves, flowers, seeds, fungi, algae, food ingredients.

**CRITICAL**: Never invent chemical constituents. Missing data = "UNKNOWN".

### 2.6 Chemical Database

All chemical entities with full metadata:
```
Compound
 ├── Molecule (structure, SMILES, InChI, InChIKey)
 ├── Molecular descriptors (MW, LogP, TPSA, HBD, HBA, etc.)
 ├── Fingerprints (Morgan, MACCS, etc.)
 ├── Sources (database references)
 ├── Evidence level (E0-E6)
 └── Validation status (valid/invalid/unknown)
```

### 2.7 Molecular Engine

Core chemistry operations:
- **SMILES parsing/validation/generation**
- **InChI/InChIKey computation**
- **Canonicalization**
- **Stereochemistry analysis**
- **Fingerprint computation** (Morgan, MACCS, structural)
- **Molecular descriptors** (MW, LogP, TPSA, HBD, HBA, rotatable bonds, etc.)
- **Substructure search**
- **Similarity search** (Tanimoto, Dice, etc.)
- **Functional group identification**
- **Salt handling**
- **Tautomer handling**
- **Duplicate detection**
- **Structure validation**

Implementation: RDKit primary; Open Babel for format conversion.

### 2.8 Virtual Mixer

Centerpiece module for ingredient interaction analysis:
- User selects: Plant A, Plant B, Plant C, Ingredient D, Compound E, Extract F
- Configure: Temperature, pH, Solvent, Concentration, Time, Oxygen, Light, Water, Enzyme, Reaction environment
- Decomposes ingredients into known compounds
- Classifies each interaction:
  - **KNOWN REACTION** — documented reaction exists
  - **PREDICTED REACTION** — plausible based on reaction rules
  - **NO KNOWN REACTION** — no pathway found
  - **INSUFFICIENT DATA** — missing information
  - **POTENTIAL INTERACTION** — possible but unverified

**CRITICAL**: Never simulate arbitrary physical mixture perfectly. All interactions are classified and evidence-tracked.

### 2.9 Reaction Engine

Reaction analysis pipeline:
- **Inputs**: Compound A, Compound B, Conditions
- **Outputs**: Possible reaction, reaction SMARTS, products, reactants, reaction class, feasibility estimate, known literature, confidence, evidence level
- Uses known reaction rules (RDKit reaction SMARTS)
- LLMs may propose hypotheses; computational engines MUST validate structures
- Never fabricate reaction equations

### 2.10 Reaction Discovery (Hypothesis Generator)

Combinatorial hypothesis generation with explosion protection:
- Evaluate combinations: A+B, A+C, A+D, B+C, etc.
- **Combatorial explosion protections**:
  - Similarity filtering
  - Functional-group filtering
  - Known reaction class filtering
  - Reaction likelihood scoring
  - Evidence filtering
  - User-defined limits
  - Beam search
  - Priority queues
  - Active-learning exploration
- Every candidate must be reproducible (seed, parameters recorded)

### 2.11 Simulation Engine (Abstraction Layer)

Adapter pattern for multiple simulation backends:
```
SimulationEngine
 ├── RDKitEngine (property prediction, similarity, descriptors)
 ├── OpenMMEngine (molecular dynamics)
 ├── Psi4Engine (quantum chemistry — deferred)
 ├── PySCFEngine (quantum chemistry — deferred)
 └── DockingEngine (ligand-target docking)
```

Interface supports: Docking, Molecular Dynamics, Quantum Chemistry, Property Prediction, Reaction Modeling.

### 2.12 Docking Module

Ligand-target evaluation:
- Display: Target, Ligand, Binding pose, Docking score, Pose visualization, Interactions (H-bonds, hydrophobic)
- **CRITICAL DISCLAIMER**: "DOCKING IS A COMPUTATIONAL HYPOTHESIS, NOT CLINICAL EVIDENCE."
- Never equate docking score with medical efficacy

### 2.13 Molecular Dynamics Module

OpenMM-based MD with metadata tracking:
- Inputs: Protein, ligand, solvent, ions, temperature, simulation time, force field, seed
- Outputs: RMSD, RMSF, radius of gyration, hydrogen bonds, interaction persistence, energy, trajectory
- Trajectory visualization (via Plotly)
- Complete simulation metadata stored

### 2.14 QM Engine

Quantum chemistry abstraction (deferred):
- Geometry optimization, energy, dipole moment, orbital information, charge distribution, reaction energetics
- CPU-friendly calculations for development
- GPU/advanced compute allowed later
- Approximations must NEVER be presented as experimental precision

### 2.15 Biological Knowledge Engine

Knowledge graph linking:
```
Compound → Target → Pathway → Biological Process → Literature Evidence
```

Each node has stable ID, evidence classification, provenance.

### 2.16 Literature Research Agent

For each hypothesis:
1. Search literature (PubMed, arXiv, Semantic Scholar)
2. Identify relevant papers
3. Extract claims, conditions, compounds, targets
4. Extract contradictions, replications, evidence gaps
5. Link papers to database entities

Storage: DOI, PMID, authors, year, journal, title, abstract, claims, experimental evidence, limitations.

**CRITICAL**: Abstract alone is never complete evidence.

### 2.17 Novelty Engine

For every candidate:
- Search: PubChem, ChEBI, ChEMBL, literature, reaction databases, publications
- Determine: Known molecule? Known reaction? Known plant source? Known target? Known activity? Previously reported combination?
- **NEVER claim**: "This is the first discovery in history."
- **INSTEAD**: "No matching record was found in the searched sources as of YYYY-MM-DD."

### 2.18 Hypothesis Engine

Structured hypothesis management:
- Rationale, assumptions, predictions, tests, falsification criteria, evidence, confidence, status
- Statuses: PROPOSED, TESTING, SUPPORTED, WEAKENED, REFUTED, INCONCLUSIVE, REPRODUCED
- Every hypothesis actively seeks evidence against it (Phase 43)

### 2.19 Statistical Validation Engine

- Random controls, null models, bootstrap, permutation tests
- Effect sizes, confidence intervals, multiple-testing correction
- Sensitivity analysis, parameter sweeps, ablation tests, reproducibility tests
- Never rely on one interesting simulation

### 2.20 Dashboard & Visual Lab UI

Dark scientific interface:
- Dark background, subtle grid, neon accents
- Molecular visualizations, animated but restrained
- High information density, professional dashboard
- Responsive layout

Navigation: Dashboard, Plants, Compounds, Molecules, Virtual Mixer, Reactions, Targets, Docking, Molecular Dynamics, Quantum, Literature, Experiments, Hypotheses, Knowledge Graph, Novelty, Statistics, Research Swarm, Reports, Settings.

---

## 3. Database Schema

### 3.1 Primary Storage: SQLite (local-first)

All entities with stable IDs:

```sql
CREATE TABLE Plant (
    id TEXT PRIMARY KEY,        -- PLANT-000001
    scientific_name TEXT,
    common_names TEXT,          -- JSON array
    taxonomy TEXT,              -- JSON object
    plant_parts TEXT,           -- JSON array
    known_constituents TEXT,    -- JSON array of CMP-IDs
    concentration_ranges TEXT,  -- JSON object
    extraction_method TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE Compound (
    id TEXT PRIMARY KEY,        -- CMP-000001
    smiles TEXT,
    inchi TEXT,
    inchikey TEXT,
    molecular_formula TEXT,
    molecular_weight REAL,
    canonical_name TEXT,
    sources TEXT,               -- JSON array
    evidence_level TEXT,        -- E0-E6
    validation_status TEXT,     -- valid/invalid/unknown
    created_at TEXT
);

CREATE Molecule (
    id TEXT PRIMARY KEY,        -- MOL-000001
    compound_id TEXT REFERENCES Compound(id),
    structure BLOB,             -- SDF or PNG
    descriptors TEXT,           -- JSON: MW, LogP, TPSA, etc.
    fingerprints TEXT,          -- JSON: Morgan, MACCS
    stereochemistry TEXT,
    functional_groups TEXT,
    created_at TEXT
);

CREATE TABLE Experiment (
    id TEXT PRIMARY KEY,        -- EXP-000001
    question TEXT,
    hypothesis TEXT,
    inputs TEXT,                -- JSON
    parameters TEXT,            -- JSON
    software_versions TEXT,     -- JSON
    random_seeds TEXT,          -- JSON
    methods TEXT,
    outputs TEXT,               -- JSON
    logs TEXT,                  -- JSON
    evidence TEXT,              -- JSON
    interpretation TEXT,
    criticism TEXT,
    reproduction_status TEXT,   -- REPRODUCED/PARTIAL/FAILED
    created_at TEXT,
    immutable INTEGER DEFAULT 1
);

CREATE TABLE Evidence (
    id TEXT PRIMARY KEY,
    entity_id TEXT,             -- Any entity ID
    entity_type TEXT,           -- Compound/Plant/Reaction/etc.
    evidence_level TEXT,        -- E0-E6
    source TEXT,
    source_type TEXT,           -- Database/Literature/Computational/AI
    timestamp TEXT,
    software_version TEXT,
    model_version TEXT,
    parameters TEXT,
    random_seed TEXT,
    input_structures TEXT,
    output TEXT,
    uncertainty TEXT,
    reproducibility_info TEXT
);
```

### 3.2 ID Convention

```
PLANT-000001
SPECIES-000001
PLANTPART-000001
EXTRACT-000001
COMPOUND-000001 (CMP-000001)
MOLECULE-000001 (MOL-000001)
REACTION-000001 (RXN-000001)
REACTIONCONDITION-000001
TARGET-000001
PROTEIN-000001
GENE-000001
DISEASE-000001
BIOLOGICALEFFECT-000001
EXPERIMENT-000001 (EXP-000001)
SIMULATION-000001 (SIM-000001)
LITERATURESOURCE-000001
DATASET-000001
HYPOTHESIS-000001 (HYP-000001)
PREDICTION-000001
EVIDENCE-000001
RESULT-000001
```

### 3.3 Migration Path

SQLite → PostgreSQL: SQLAlchemy ORM abstracts the difference. Replace connection string only.

---

## 4. Evidence Classification System

```
E0 = AI-generated hypothesis          (never displayed as fact)
E1 = database-derived fact            (sourced, timestamped)
E2 = literature-supported observation (with citation)
E3 = computational prediction         (labeled as prediction)
E4 = molecular simulation result      (with method details)
E5 = independently reproduced         (minimum 2 independent impls)
E6 = experimentally validated         (gold standard)
```

**Rule**: E0/E3/E4 must NEVER be displayed as experimentally confirmed.

Every result stores: source, timestamp, software version, model version, parameters, random seed, input structures, input concentrations, assumptions, computational method, output, uncertainty, evidence level, reproducibility info.

---

## 5. Key Design Principles

1. **Local-first**: Core functionality works without internet. APIs degrade gracefully.
2. **Evidence-first**: Every claim has an evidence level. No unclassified data.
3. **Immutable experiments**: Once created, experiment records cannot be modified.
4. **Reproducibility**: Every result reconstructible via manifest (inputs, params, versions, seeds).
5. **Adversarial by design**: Every result must survive disproof attempts.
6. **No fabricated data**: LLMs cannot insert fake molecules, SMILES, reactions, citations, or results. All structures validated computationally.
7. **Conflict detection**: Disagreements between sources are flagged, never auto-resolved.
8. **Provenance**: Every fact traceable to source with retrieval timestamp.
9. **Falsification**: System actively seeks evidence against hypotheses.
10. **Safety boundaries**: No medical claims, no dosages, no unsafe procedures, no clinical recommendations.

---

## 6. Data Flow

```
User Request
     ↓
Orchestrator (validate, classify intent)
     ↓
Research Swarm (agents propose approaches)
     ↓
Experiment Engine (create EXP record)
     ↓
Molecular Engine (validate structures)
     ↓
Relevant Engines (reactions, docking, MD, etc.)
     ↓
Analysis Engine (statistics, novelty, adversarial)
     ↓
Evidence System (classify E0-E6)
     ↓
Knowledge Graph (update)
     ↓
Report Generator (produce report)
     ↓
User (display with caveats)
```

---

## 7. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Core Chemistry | RDKit | Molecular operations |
| Format Conversion | Open Babel | Format handling |
| Molecular Dynamics | OpenMM | MD simulations |
| Quantum Chemistry | Psi4/PySCF (deferred) | QM calculations |
| Database | SQLite + SQLAlchemy | Data persistence |
| Knowledge Graph | NetworkX | Graph relationships |
| Statistics | scipy, numpy, scikit-learn | Statistical analysis |
| Biological Data | Biopython | Sequence/structure handling |
| Database Access | pubchempy | PubChem API |
| Backend API | FastAPI | Web API layer |
| Dashboard | Dash + Plotly | Interactive UI |
| Desktop GUI | PySide6 | Native interface |
| Visualization | matplotlib, Plotly | Charts, structures |
| HTTP | requests, httpx | API communication |

---

## 8. Project Directory Structure

```
SovereignBioLab/
├── README.md
├── LICENSE
├── CITATION.cff
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
│
├── src/
│   ├── core/              # Orchestrator, Experiment Manager
│   ├── molecular/         # Molecular Engine, RDKit adapter
│   ├── plant/             # Plant/Natural-Product Engine
│   ├── reaction/          # Reaction Engine, Discovery
│   ├── simulation/        # Simulation Engine, Docking, MD, QM
│   ├── knowledge/         # Knowledge Graph, Biological Engine
│   ├── literature/        # Literature Agent
│   ├── novelty/           # Novelty Engine
│   ├── hypothesis/        # Hypothesis Engine
│   ├── adversarial/       # Adversarial Scientist
│   ├── statistics/        # Statistical Validation
│   ├── swarm/             # Research Swarm agents
│   ├── experiment/        # Experiment Manager, Scheduler
│   ├── evidence/          # Evidence classification system
│   ├── database/          # Database models, migrations
│   ├── ui/                # Dashboard, Visual Lab
│   └── utils/             # Utilities, logging, validation
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── scientific/
│   ├── reproducibility/
│   ├── data/
│   ├── security/
│   └── ui/
│
├── benchmarks/
│   ├── BENCH-001          # Molecule descriptor calculation
│   ├── BENCH-002          # Known reaction
│   ├── BENCH-003          # Known ligand-target interaction
│   ├── BENCH-004          # Known MD trajectory property
│   ├── BENCH-005          # Known quantum calculation
│   └── BENCH-006          # Known literature relationship
│
├── examples/
│   └── (example queries, sample data)
│
├── scripts/
│   └── (automation, setup)
│
├── data/
│   └── (cached datasets, seed data)
│
├── docs/
│   ├── RESEARCH_RECONNAISSANCE.md
│   ├── ARCHITECTURE.md
│   ├── scientific-methodology.md
│   ├── evidence-model.md
│   ├── provenance.md
│   ├── simulations.md
│   ├── reactions.md
│   ├── molecular-dynamics.md
│   ├── quantum.md
│   ├── literature.md
│   ├── novelty.md
│   ├── reproducibility.md
│   ├── datasets.md
│   ├── installation.md
│   ├── development.md
│   └── limitations.md
│
├── experiments/
│   └── (immutable experiment records)
│
├── reports/
│   └── (generated reports)
│
├── experiments/
│   └── (experiment data)
│
└── requirements.txt
```

---

## 9. Abstraction Layers

### 9.1 Simulation Engine Interface

```python
class SimulationEngine(ABC):
    @abstractmethod
    def run(self, inputs: dict, parameters: dict) -> SimulationResult: ...
    
    @abstractmethod
    def validate_inputs(self, inputs: dict) -> ValidationResult: ...
    
    @abstractmethod
    def get_metadata(self) -> EngineMetadata: ...
```

### 9.2 Database Interface

```python
class Database(ABC):
    @abstractmethod
    def save(self, entity: Entity) -> str: ...
    
    @abstractmethod
    def get(self, entity_id: str) -> Entity: ...
    
    @abstractmethod
    def query(self, filters: dict) -> List[Entity]: ...
    
    @abstractmethod
    def migrate(self, target: str) -> None: ...
```

### 9.3 Agent Interface

```python
class ResearchAgent(ABC):
    @abstractmethod
    def execute(self, task: Task) -> AgentResult: ...
    
    @abstractmethod
    def get_capabilities(self) -> List[str]: ...
    
    @abstractmethod
    def get_evidence(self, result: AgentResult) -> EvidenceRecord: ...
```

All adapters/swaps go through these interfaces. No hard-coding against specific engines.
