from typing import Dict, Any, Optional, List
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, rdDepictor
from rdkit import DataStructs

from src.simulation.base import (
    SimulationEngine, SimulationResult, SimulationMetadata,
    PropertyPredictionResult,
)
from src.utils.validator import (
    validate_smiles, get_molecule_descriptors, canonicalize_smiles,
    smiles_to_inchi, smiles_to_inchikey, tanimoto_similarity,
)


class RDKitEngine(SimulationEngine):
    """RDKit-based engine for property prediction, similarity, and descriptors."""

    def __init__(self):
        self._metadata = SimulationMetadata(
            engine_name="RDKit",
            engine_version="2026.3.6",
            software_version="rdkit-2026.3.6",
            parameters={},
        )
        self._capabilities = [
            "property_prediction",
            "similarity",
            "descriptors",
            "fingerprints",
            "stereochemistry",
            "functional_groups",
            "structure_validation",
            "smiles_canonicalization",
            "inchi_conversion",
            "duplicate_detection",
        ]

    def run(self, inputs: Dict[str, Any], parameters: Dict[str, Any]) -> SimulationResult:
        operation = parameters.get("operation", "property_prediction")

        try:
            if operation == "property_prediction":
                return self._predict_properties(inputs)
            elif operation == "similarity":
                return self._compute_similarity(inputs)
            elif operation == "descriptors":
                return self._compute_descriptors(inputs)
            elif operation == "validate":
                return self._validate_structure(inputs)
            else:
                return SimulationResult(
                    success=False,
                    output={"error": f"Unknown operation: {operation}"},
                    metadata=self._metadata,
                    evidence_level="E0",
                )
        except Exception as e:
            return SimulationResult(
                success=False,
                output={"error": str(e)},
                metadata=self._metadata,
                evidence_level="E3",
            )

    def _predict_properties(self, inputs: Dict[str, Any]) -> SimulationResult:
        smiles = inputs.get("smiles", "")
        result = validate_smiles(smiles)
        if not result["valid"]:
            return SimulationResult(
                success=False,
                output={"error": "Invalid SMILES"},
                metadata=self._metadata,
                evidence_level="E3",
            )
        desc = get_molecule_descriptors(result["molecule"])
        return SimulationResult(
            success=True,
            output={"properties": desc},
            metadata=self._metadata,
            evidence_level="E3",
        )

    def _compute_similarity(self, inputs: Dict[str, Any]) -> SimulationResult:
        smi1 = inputs.get("smiles_a", "")
        smi2 = inputs.get("smiles_b", "")
        sim = tanimoto_similarity(smi1, smi2)
        if sim is None:
            return SimulationResult(
                success=False,
                output={"error": "Could not compute similarity"},
                metadata=self._metadata,
                evidence_level="E3",
            )
        return SimulationResult(
            success=True,
            output={"similarity": sim, "method": "Tanimoto", "radius": 2},
            metadata=self._metadata,
            evidence_level="E3",
        )

    def _compute_descriptors(self, inputs: Dict[str, Any]) -> SimulationResult:
        smiles = inputs.get("smiles", "")
        result = validate_smiles(smiles)
        if not result["valid"]:
            return SimulationResult(
                success=False,
                output={"error": "Invalid SMILES"},
                metadata=self._metadata,
                evidence_level="E3",
            )
        desc = get_molecule_descriptors(result["molecule"])
        return SimulationResult(
            success=True,
            output={"descriptors": desc},
            metadata=self._metadata,
            evidence_level="E3",
        )

    def _validate_structure(self, inputs: Dict[str, Any]) -> SimulationResult:
        smiles = inputs.get("smiles", "")
        valid = validate_smiles(smiles)["valid"]
        return SimulationResult(
            success=True,
            output={"smiles": smiles, "valid": valid},
            metadata=self._metadata,
            evidence_level="E3",
        )

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        smiles = inputs.get("smiles", inputs.get("smiles_a", ""))
        if smiles:
            return validate_smiles(smiles)["valid"]
        return False

    def get_metadata(self) -> SimulationMetadata:
        return self._metadata

    def get_capabilities(self) -> List[str]:
        return self._capabilities


__all__ = ["RDKitEngine"]
