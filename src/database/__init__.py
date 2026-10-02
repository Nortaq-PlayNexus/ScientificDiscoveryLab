from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from contextlib import contextmanager

from src.database.models import (
    Base, init_db, get_engine, get_session,
    Plant, Species, PlantPart, Extract,
    Compound, Molecule, Reaction, ReactionCondition,
    Target, Protein, Gene, Disease, BiologicalEffect,
    Experiment, Simulation, LiteratureSource, Dataset,
    Hypothesis, Prediction, EvidenceRecord, Result,
)
from src.evidence import Evidence, EvidenceLevel, EvidenceSourceType

__all__ = [
    "init_db",
    "get_session",
    "Base",
    "Evidence",
    "EvidenceLevel",
    "EvidenceSourceType",
    "Plant",
    "Compound",
    "Molecule",
    "Reaction",
    "Experiment",
    "Hypothesis",
]
