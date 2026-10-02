# tests/unit/test_simulation_module.py
from src.simulation import RDKitEngine, OpenMMEngine, DockingModule, SimulationEngine

def test_rdkit_is_simulation_engine():
    engine = RDKitEngine()
    assert isinstance(engine, SimulationEngine)

def test_openmm_is_simulation_engine():
    engine = OpenMMEngine()
    assert isinstance(engine, SimulationEngine)

def test_docking_is_simulation_engine():
    engine = DockingModule()
    assert isinstance(engine, SimulationEngine)

def test_all_engines_have_metadata():
    for engine_class in [RDKitEngine, OpenMMEngine, DockingModule]:
        engine = engine_class()
        meta = engine.get_metadata()
        assert meta.engine_name is not None
        assert meta.engine_version is not None

def test_all_engines_have_capabilities():
    for engine_class in [RDKitEngine, OpenMMEngine, DockingModule]:
        engine = engine_class()
        caps = engine.get_capabilities()
        assert len(caps) > 0
