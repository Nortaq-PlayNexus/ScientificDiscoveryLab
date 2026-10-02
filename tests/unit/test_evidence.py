# tests/unit/test_evidence.py
import time
from src.evidence import Evidence, EvidenceLevel, EvidenceSourceType

def test_e0_is_ai_hypothesis():
    assert EvidenceLevel.E0.value == "E0"
    assert EvidenceLevel.E0.is_computational() is True
    assert EvidenceLevel.E0.is_fact() is False

def test_e1_is_database_fact():
    assert EvidenceLevel.E1.value == "E1"
    assert EvidenceLevel.E1.is_fact() is True
    assert EvidenceLevel.E1.is_computational() is False

def test_e3_is_computational_prediction():
    assert EvidenceLevel.E3.is_computational() is True
    assert EvidenceLevel.E3.is_fact() is False
    assert EvidenceLevel.E3.is_validated() is False

def test_e6_is_gold_standard():
    assert EvidenceLevel.E6.is_validated() is True
    assert EvidenceLevel.E6.is_fact() is True

def test_evidence_creation_all_fields():
    ev = Evidence(
        entity_id="CMP-000001",
        entity_type="Compound",
        level=EvidenceLevel.E3,
        source="RDKit",
        source_type=EvidenceSourceType.COMPUTATIONAL,
        timestamp="2026-09-20T08:00:00",
        software_version="rdkit-2026.3.6",
        model_version=None,
        parameters={"key": "value"},
        random_seed=42,
        input_structures=["SMILES:CCO"],
        input_concentrations={"ethanol": 0.1},
        assumptions=["assumption1"],
        computational_method="MolLogP",
        output={"logp": -0.001},
        uncertainty="±0.1",
        reproducibility_info="deterministic",
    )
    d = ev.to_dict()
    assert d["entity_id"] == "CMP-000001"
    assert d["parameters"]["key"] == "value"
    assert d["random_seed"] == 42
    assert d["uncertainty"] == "±0.1"

def test_evidence_from_dict():
    ev = Evidence(
        entity_id="EXP-0001",
        entity_type="Experiment",
        level=EvidenceLevel.E1,
        source="PubChem",
        source_type=EvidenceSourceType.DATABASE,
    )
    d = ev.to_dict()
    ev2 = Evidence.from_dict(d)
    assert ev2.level == EvidenceLevel.E1
    assert ev2.source == "PubChem"

def test_evidence_timestamp_auto():
    ev = Evidence(
        entity_id="TEST",
        entity_type="Test",
        level=EvidenceLevel.E0,
        source="AI-generated",
        source_type=EvidenceSourceType.AI,
    )
    assert ev.timestamp is not None
    assert "T" in ev.timestamp
