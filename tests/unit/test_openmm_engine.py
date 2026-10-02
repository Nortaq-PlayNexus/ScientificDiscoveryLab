from src.simulation.openmm_adapter import OpenMMEngine
from src.simulation.base import SimulationResult

def test_openmm_capabilities():
    engine = OpenMMEngine()
    caps = engine.get_capabilities()
    assert "molecular_dynamics" in caps
    assert "energy_minimization" in caps

def test_openmm_metadata():
    engine = OpenMMEngine()
    meta = engine.get_metadata()
    assert meta.engine_name == "OpenMM"
    assert meta.engine_version == "8.6.1"

def test_openmm_md_mock():
    engine = OpenMMEngine()
    result = engine.run(
        {"smiles": "CCO"},
        {"operation": "md", "steps": 100, "temperature": 300, "seed": 42},
    )
    assert result.success is True
    output = result.output
    assert "rmsd" in output
    assert "rmsf" in output
    assert "energy" in output
    assert len(output["rmsd"]) == 100

def test_openmm_invalid_smiles():
    engine = OpenMMEngine()
    result = engine.run(
        {"smiles": "INVALID"},
        {"operation": "md"},
    )
    assert result.success is False

def test_openmm_validate_inputs():
    engine = OpenMMEngine()
    assert engine.validate_inputs({"smiles": "CCO"}) is True
    assert engine.validate_inputs({"smiles": "INVALID"}) is False

def test_openmm_default_params():
    engine = OpenMMEngine()
    meta = engine.get_metadata()
    assert meta.parameters["default_temperature"] == 300.0
    assert meta.parameters["default_timestep"] == 0.002
