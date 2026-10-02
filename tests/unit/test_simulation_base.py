# tests/unit/test_simulation_base.py
from src.simulation.base import (
    SimulationEngine, SimulationResult, SimulationMetadata,
    DockingResult, DockingPose, MolecularDynamicsResult,
    PropertyPredictionResult, ReactionModelingResult,
)

def test_metadata_to_dict():
    meta = SimulationMetadata("Test", "1.0", "1.0", {"key": "val"}, random_seed=42)
    d = meta.to_dict()
    assert d["engine_name"] == "Test"
    assert d["parameters"]["key"] == "val"
    assert d["random_seed"] == 42
    assert d["timestamp"] is not None

def test_simulation_result_to_dict():
    meta = SimulationMetadata("Test", "1.0", "1.0", {})
    result = SimulationResult(
        success=True,
        output={"key": "value"},
        metadata=meta,
        evidence_level="E3",
    )
    d = result.to_dict()
    assert d["success"] is True
    assert d["output"]["key"] == "value"
    assert d["evidence_level"] == "E3"

def test_simulation_result_error():
    meta = SimulationMetadata("Test", "1.0", "1.0", {})
    result = SimulationResult(
        success=False,
        output={"error": "fail"},
        metadata=meta,
        error="Detailed error",
    )
    assert result.success is False
    assert result.error == "Detailed error"

def test_docking_pose():
    pose = DockingPose("CCO", [1, 2, 3], [1, 0, 0, 0])
    assert pose.ligand_smiles == "CCO"
    assert pose.position == [1, 2, 3]

def test_docking_result_to_dict():
    meta = SimulationMetadata("Test", "1.0", "1.0", {})
    result = DockingResult(
        target_name="Target",
        ligand_smiles="CCO",
        score=-5.0,
        pose=None,
        interactions={},
        caveats=["test"],
        evidence_level="E3",
    )
    d = result.to_dict()
    assert d["target_name"] == "Target"
    assert d["score"] == -5.0
    assert d["pose"] is None

def test_md_result_to_dict():
    meta = SimulationMetadata("Test", "1.0", "1.0", {})
    result = MolecularDynamicsResult(
        rmsd=[1, 2, 3],
        rmsf=[0.1, 0.2],
        radius_of_gyration=[15, 16],
        hydrogen_bonds=5,
        energy=-100,
        trajectory=[{"frame": 1}],
        metadata=meta,
    )
    d = result.to_dict()
    assert d["rmsd"] == [1, 2, 3]
    assert d["energy"] == -100

def test_property_prediction_result():
    meta = SimulationMetadata("Test", "1.0", "1.0", {})
    result = PropertyPredictionResult(
        properties={"mw": 78.11},
        metadata=meta,
        evidence_level="E3",
    )
    assert result.properties["mw"] == 78.11

def test_reaction_modeling_result():
    meta = SimulationMetadata("Test", "1.0", "1.0", {})
    result = ReactionModelingResult(
        reactants=["A"],
        products=["B"],
        reaction_smarts="[A:1]>>[B:1]",
        confidence=0.8,
        evidence_level="E3",
        metadata=meta,
    )
    assert result.confidence == 0.8
