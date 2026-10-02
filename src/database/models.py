from datetime import datetime
import os
from typing import Optional
from sqlalchemy import (
    Column, String, Text, JSON, Float, Integer, Boolean, DateTime, ForeignKey,
)
from sqlalchemy.orm import declarative_base, relationship, Session
from sqlalchemy import create_engine as sa_create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


def generate_id(prefix: str) -> str:
    """Generate a stable ID like PLANT-000001."""
    return f"{prefix}-000001"


class Plant(Base):
    __tablename__ = "plants"
    id = Column(String, primary_key=True)
    scientific_name = Column(String)
    common_names = Column(JSON)
    taxonomy = Column(JSON)
    plant_parts = Column(JSON)
    known_constituents = Column(JSON)
    concentration_ranges = Column(JSON)
    extraction_method = Column(String)
    created_at = Column(String, default=datetime.utcnow().isoformat)
    updated_at = Column(String, default=datetime.utcnow().isoformat)


class Species(Base):
    __tablename__ = "species"
    id = Column(String, primary_key=True)
    scientific_name = Column(String)
    common_name = Column(String)
    taxonomy = Column(JSON)
    plant_id = Column(String, ForeignKey("plants.id"))
    created_at = Column(String, default=datetime.utcnow().isoformat)


class PlantPart(Base):
    __tablename__ = "plant_parts"
    id = Column(String, primary_key=True)
    name = Column(String)
    part_type = Column(String)
    plant_id = Column(String, ForeignKey("plants.id"))
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Extract(Base):
    __tablename__ = "extracts"
    id = Column(String, primary_key=True)
    name = Column(String)
    method = Column(String)
    plant_id = Column(String, ForeignKey("plants.id"))
    compound_ids = Column(JSON)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Compound(Base):
    __tablename__ = "compounds"
    id = Column(String, primary_key=True)
    smiles = Column(String)
    inchi = Column(String)
    inchikey = Column(String)
    molecular_formula = Column(String)
    molecular_weight = Column(Float)
    canonical_name = Column(String)
    sources = Column(JSON)
    evidence_level = Column(String)
    validation_status = Column(String, default="unknown")
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Molecule(Base):
    __tablename__ = "molecules"
    id = Column(String, primary_key=True)
    compound_id = Column(String, ForeignKey("compounds.id"))
    structure = Column(Text)
    descriptors = Column(JSON)
    fingerprints = Column(JSON)
    stereochemistry = Column(JSON)
    functional_groups = Column(JSON)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Reaction(Base):
    __tablename__ = "reactions"
    id = Column(String, primary_key=True)
    reactants = Column(JSON)
    products = Column(JSON)
    reaction_smarts = Column(String)
    reaction_class = Column(String)
    conditions = Column(JSON)
    confidence = Column(Float)
    evidence_level = Column(String)
    known_literature = Column(JSON)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class ReactionCondition(Base):
    __tablename__ = "reaction_conditions"
    id = Column(String, primary_key=True)
    reaction_id = Column(String, ForeignKey("reactions.id"))
    temperature = Column(Float)
    ph = Column(Float)
    solvent = Column(String)
    concentration = Column(Float)
    time = Column(String)
    oxygen = Column(String)
    light = Column(String)
    water_content = Column(String)
    enzyme = Column(String)
    environment = Column(String)


class Target(Base):
    __tablename__ = "targets"
    id = Column(String, primary_key=True)
    name = Column(String)
    protein_id = Column(String)
    organism = Column(String)
    evidence_level = Column(String)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Protein(Base):
    __tablename__ = "proteins"
    id = Column(String, primary_key=True)
    name = Column(String)
    sequence = Column(Text)
    structure_pdb = Column(String)
    organism = Column(String)
    target_id = Column(String, ForeignKey("targets.id"))
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Gene(Base):
    __tablename__ = "genes"
    id = Column(String, primary_key=True)
    name = Column(String)
    sequence = Column(Text)
    organism = Column(String)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Disease(Base):
    __tablename__ = "diseases"
    id = Column(String, primary_key=True)
    name = Column(String)
    icd_code = Column(String)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class BiologicalEffect(Base):
    __tablename__ = "biological_effects"
    id = Column(String, primary_key=True)
    description = Column(String)
    compound_id = Column(String, ForeignKey("compounds.id"))
    target_id = Column(String, ForeignKey("targets.id"))
    evidence_level = Column(String)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(String, primary_key=True)
    question = Column(Text)
    hypothesis = Column(Text)
    inputs = Column(JSON)
    parameters = Column(JSON)
    software_versions = Column(JSON)
    random_seeds = Column(JSON)
    methods = Column(Text)
    outputs = Column(JSON)
    logs = Column(JSON)
    evidence = Column(JSON)
    interpretation = Column(Text)
    criticism = Column(Text)
    reproduction_status = Column(String)
    created_at = Column(String, default=datetime.utcnow().isoformat)
    immutable = Column(Boolean, default=True)


class Simulation(Base):
    __tablename__ = "simulations"
    id = Column(String, primary_key=True)
    experiment_id = Column(String, ForeignKey("experiments.id"))
    engine = Column(String)
    engine_version = Column(String)
    inputs = Column(JSON)
    parameters = Column(JSON)
    results = Column(JSON)
    status = Column(String)
    error = Column(Text)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class LiteratureSource(Base):
    __tablename__ = "literature_sources"
    id = Column(String, primary_key=True)
    doi = Column(String)
    pmid = Column(String)
    authors = Column(JSON)
    year = Column(Integer)
    journal = Column(String)
    title = Column(String)
    abstract = Column(Text)
    claims = Column(JSON)
    experimental_evidence = Column(JSON)
    limitations = Column(JSON)
    url = Column(String)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(Text)
    source = Column(String)
    license = Column(String)
    size = Column(Integer)
    cached = Column(Boolean, default=False)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Hypothesis(Base):
    __tablename__ = "hypotheses"
    id = Column(String, primary_key=True)
    statement = Column(Text)
    rationale = Column(Text)
    assumptions = Column(JSON)
    predictions = Column(JSON)
    tests = Column(JSON)
    falsification_criteria = Column(Text)
    evidence = Column(JSON)
    confidence = Column(Float)
    status = Column(String, default="PROPOSED")
    created_at = Column(String, default=datetime.utcnow().isoformat)


class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(String, primary_key=True)
    hypothesis_id = Column(String, ForeignKey("hypotheses.id"))
    description = Column(Text)
    expected_outcome = Column(Text)
    evidence_level = Column(String)
    created_at = Column(String, default=datetime.utcnow().isoformat)


class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    id = Column(String, primary_key=True)
    entity_id = Column(String)
    entity_type = Column(String)
    level = Column(String)
    source = Column(String)
    source_type = Column(String)
    timestamp = Column(String)
    software_version = Column(String)
    model_version = Column(String)
    parameters = Column(JSON)
    random_seed = Column(Integer)
    input_structures = Column(JSON)
    input_concentrations = Column(JSON)
    assumptions = Column(JSON)
    computational_method = Column(String)
    output = Column(JSON)
    uncertainty = Column(String)
    reproducibility_info = Column(String)


class Result(Base):
    __tablename__ = "results"
    id = Column(String, primary_key=True)
    experiment_id = Column(String, ForeignKey("experiments.id"))
    simulation_id = Column(String, ForeignKey("simulations.id"))
    value = Column(JSON)
    uncertainty = Column(String)
    evidence_level = Column(String)
    created_at = Column(String, default=datetime.utcnow().isoformat)


DATABASE_URL = os.environ.get(
    "SOVEREIGN_BIOLAB_DATABASE_URL",
    "sqlite:///sovereign_biolab.db",
)

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = sa_create_engine(DATABASE_URL, echo=False)
    return _engine


def get_session() -> Session:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


__all__ = [
    "Base",
    "generate_id",
    "Plant",
    "Species",
    "PlantPart",
    "Extract",
    "Compound",
    "Molecule",
    "Reaction",
    "ReactionCondition",
    "Target",
    "Protein",
    "Gene",
    "Disease",
    "BiologicalEffect",
    "Experiment",
    "Simulation",
    "LiteratureSource",
    "Dataset",
    "Hypothesis",
    "Prediction",
    "EvidenceRecord",
    "Result",
    "get_engine",
    "get_session",
    "init_db",
]
