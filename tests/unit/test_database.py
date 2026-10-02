from hashlib import sha256
from pathlib import Path

from sqlalchemy import create_engine
from src.database.models import Base, init_db, get_session, Compound, Experiment
from src.evidence import Evidence, EvidenceLevel, EvidenceSourceType

def test_database_init():
    root_db = Path(__file__).resolve().parents[2] / "sovereign_biolab.db"
    before = sha256(root_db.read_bytes()).hexdigest() if root_db.exists() else None
    engine = init_db()
    after = sha256(root_db.read_bytes()).hexdigest() if root_db.exists() else None
    assert engine is not None
    assert Path(engine.url.database).resolve() != root_db.resolve()
    assert before == after

def test_compound_crud():
    engine = init_db()
    session = get_session()
    cmp = Compound(
        id="CMP-000001",
        smiles="CCO",
        inchi="InChI=1S/C2H6O",
        inchikey="LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
        molecular_formula="C2H6O",
        molecular_weight=46.07,
        canonical_name="Ethanol",
        sources=[{"database": "PubChem", "id": "702"}],
        evidence_level="E1",
        validation_status="valid",
    )
    session.add(cmp)
    session.commit()
    retrieved = session.query(Compound).filter_by(id="CMP-000001").first()
    assert retrieved is not None
    assert retrieved.smiles == "CCO"
    session.delete(cmp)
    session.commit()
    session.close()

def test_evidence_creation():
    ev = Evidence(
        entity_id="CMP-000001",
        entity_type="Compound",
        level=EvidenceLevel.E3,
        source="RDKit descriptor calculation",
        source_type=EvidenceSourceType.COMPUTATIONAL,
        software_version="rdkit-2026.3.6",
        parameters={"method": "MolLogP"},
        computational_method="RDKit Descriptors.MolLogP",
        output={"logp": -0.0014},
        uncertainty="±0.1",
    )
    assert ev.level == EvidenceLevel.E3
    assert ev.is_computational() is True
    assert ev.is_fact() is False
    assert ev.is_validated() is False
    d = ev.to_dict()
    assert d["entity_id"] == "CMP-000001"
    ev2 = Evidence.from_dict(d)
    assert ev2.level == EvidenceLevel.E3

def test_experiment_immutable():
    engine = init_db()
    session = get_session()
    exp = Experiment(
        id="EXP-000001",
        question="Test question",
        hypothesis="Test hypothesis",
        inputs={},
        parameters={},
        software_versions={"rdkit": "2026.3.6"},
        random_seeds=[42],
        methods="test",
        outputs={},
        logs={},
        evidence=[],
        interpretation="test",
        criticism="none",
        reproduction_status="REPRODUCED",
    )
    session.add(exp)
    session.commit()
    retrieved = session.query(Experiment).filter_by(id="EXP-000001").first()
    assert retrieved is not None
    assert retrieved.immutable is True
    session.delete(exp)
    session.commit()
    session.close()
