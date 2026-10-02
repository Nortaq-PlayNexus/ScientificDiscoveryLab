from src.simulation.docking import DockingModule, DOCKING_CAVEATS
from src.simulation.base import DockingResult

def test_docking_caveats_present():
    assert any("CLINICAL EVIDENCE" in c for c in DOCKING_CAVEATS)

def test_docking_module_capabilities():
    engine = DockingModule()
    caps = engine.get_capabilities()
    assert "docking" in caps
    assert "scoring" in caps

def test_docking_metadata():
    engine = DockingModule()
    meta = engine.get_metadata()
    assert meta.engine_name == "DockingModule"

def test_dock_valid_ligand():
    engine = DockingModule()
    result = engine.run(
        {"ligand_smiles": "CCO", "target_name": "TestTarget"},
        {"operation": "dock", "score": -8.5},
    )
    assert result.success is True
    docking = result.output["docking"]
    assert docking["target_name"] == "TestTarget"
    assert docking["ligand_smiles"] == "CCO"
    assert docking["score"] == -8.5
    assert "caveats" in docking
    assert len(docking["caveats"]) > 0

def test_dock_invalid_ligand():
    engine = DockingModule()
    result = engine.run(
        {"ligand_smiles": "INVALID", "target_name": "TestTarget"},
        {"operation": "dock"},
    )
    assert result.success is False

def test_dock_with_pose():
    engine = DockingModule()
    result = engine.run(
        {"ligand_smiles": "CCO", "target_name": "Target"},
        {
            "operation": "dock",
            "score": -5.0,
            "pose": {
                "position": [1, 2, 3],
                "orientation": [1, 0, 0, 0],
            },
        },
    )
    assert result.success is True
    docking = result.output["docking"]
    assert docking["pose"] is not None
    assert docking["pose"]["position"] == [1, 2, 3]

def test_dock_score():
    engine = DockingModule()
    result = engine.run(
        {"ligand_smiles": "c1ccccc1", "target_name": "Test"},
        {"operation": "score", "score": -7.2},
    )
    assert result.success is True
    assert result.output["score"] == -7.2
    assert "caveats" in result.output

def test_dock_validate_inputs():
    engine = DockingModule()
    assert engine.validate_inputs({"ligand_smiles": "CCO"}) is True
    assert engine.validate_inputs({"ligand_smiles": "INVALID"}) is False
