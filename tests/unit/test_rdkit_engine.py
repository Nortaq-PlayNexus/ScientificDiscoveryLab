from src.simulation.rdkit_adapter import RDKitEngine
from src.simulation.base import SimulationResult

def test_rdkit_capabilities():
    engine = RDKitEngine()
    caps = engine.get_capabilities()
    assert "property_prediction" in caps
    assert "similarity" in caps

def test_rdkit_metadata():
    engine = RDKitEngine()
    meta = engine.get_metadata()
    assert meta.engine_name == "RDKit"
    assert meta.engine_version == "2026.3.6"

def test_rdkit_property_prediction():
    engine = RDKitEngine()
    result = engine.run(
        {"smiles": "c1ccccc1"},
        {"operation": "property_prediction"},
    )
    assert result.success is True
    assert "properties" in result.output
    props = result.output["properties"]
    assert props["molecular_weight"] > 75.0

def test_rdkit_similarity():
    engine = RDKitEngine()
    result = engine.run(
        {"smiles_a": "c1ccccc1", "smiles_b": "c1ccc(O)cc1"},
        {"operation": "similarity"},
    )
    assert result.success is True
    sim = result.output["similarity"]
    assert 0.0 <= sim <= 1.0

def test_rdkit_descriptors():
    engine = RDKitEngine()
    result = engine.run(
        {"smiles": "CCO"},
        {"operation": "descriptors"},
    )
    assert result.success is True
    desc = result.output["descriptors"]
    assert "molecular_weight" in desc
    assert desc["molecular_weight"] > 0

def test_rdkit_validate():
    engine = RDKitEngine()
    result = engine.run(
        {"smiles": "CCO"},
        {"operation": "validate"},
    )
    assert result.success is True
    assert result.output["valid"] is True

def test_rdkit_invalid():
    engine = RDKitEngine()
    result = engine.run(
        {"smiles": "INVALID"},
        {"operation": "property_prediction"},
    )
    assert result.success is False

def test_rdkit_validate_inputs():
    engine = RDKitEngine()
    assert engine.validate_inputs({"smiles": "CCO"}) is True
    assert engine.validate_inputs({"smiles": "INVALID"}) is False
