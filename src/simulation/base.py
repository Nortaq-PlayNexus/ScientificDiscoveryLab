from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List
from datetime import datetime


class SimulationMetadata:
    def __init__(
        self,
        engine_name: str,
        engine_version: str,
        software_version: str,
        parameters: Dict[str, Any],
        random_seed: Optional[int] = None,
        timestamp: Optional[str] = None,
    ):
        self.engine_name = engine_name
        self.engine_version = engine_version
        self.software_version = software_version
        self.parameters = parameters
        self.random_seed = random_seed
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "software_version": self.software_version,
            "parameters": self.parameters,
            "random_seed": self.random_seed,
            "timestamp": self.timestamp,
        }


class SimulationResult:
    def __init__(
        self,
        success: bool,
        output: Dict[str, Any],
        metadata: SimulationMetadata,
        error: Optional[str] = None,
        evidence_level: str = "E3",
    ):
        self.success = success
        self.output = output
        self.metadata = metadata
        self.error = error
        self.evidence_level = evidence_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "metadata": self.metadata.to_dict(),
            "error": self.error,
            "evidence_level": self.evidence_level,
        }


class DockingPose:
    def __init__(self, ligand_smiles: str, position: List[float], orientation: List[float]):
        self.ligand_smiles = ligand_smiles
        self.position = position
        self.orientation = orientation


class DockingResult:
    def __init__(
        self,
        target_name: str,
        ligand_smiles: str,
        score: Optional[float],
        pose: Optional[DockingPose],
        interactions: Dict[str, Any],
        caveats: List[str],
        evidence_level: str,
    ):
        self.target_name = target_name
        self.ligand_smiles = ligand_smiles
        self.score = score
        self.pose = pose
        self.interactions = interactions
        self.caveats = caveats
        self.evidence_level = evidence_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_name": self.target_name,
            "ligand_smiles": self.ligand_smiles,
            "score": self.score,
            "pose": self.pose.__dict__ if self.pose else None,
            "interactions": self.interactions,
            "caveats": self.caveats,
            "evidence_level": self.evidence_level,
        }


class MolecularDynamicsResult:
    def __init__(
        self,
        rmsd: Optional[List[float]],
        rmsf: Optional[List[float]],
        radius_of_gyration: Optional[List[float]],
        hydrogen_bonds: Optional[int],
        energy: Optional[float],
        trajectory: Optional[List[Dict]],
        metadata: SimulationMetadata,
    ):
        self.rmsd = rmsd
        self.rmsf = rmsf
        self.radius_of_gyration = radius_of_gyration
        self.hydrogen_bonds = hydrogen_bonds
        self.energy = energy
        self.trajectory = trajectory
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rmsd": self.rmsd,
            "rmsf": self.rmsf,
            "radius_of_gyration": self.radius_of_gyration,
            "hydrogen_bonds": self.hydrogen_bonds,
            "energy": self.energy,
            "trajectory": self.trajectory,
            "metadata": self.metadata.to_dict(),
        }


class PropertyPredictionResult:
    def __init__(
        self,
        properties: Dict[str, Any],
        metadata: SimulationMetadata,
        evidence_level: str = "E3",
    ):
        self.properties = properties
        self.metadata = metadata
        self.evidence_level = evidence_level


class ReactionModelingResult:
    def __init__(
        self,
        reactants: List[str],
        products: List[str],
        reaction_smarts: Optional[str],
        confidence: float,
        evidence_level: str,
        metadata: SimulationMetadata,
    ):
        self.reactants = reactants
        self.products = products
        self.reaction_smarts = reaction_smarts
        self.confidence = confidence
        self.evidence_level = evidence_level
        self.metadata = metadata


class SimulationEngine(ABC):
    """Abstract base class for all simulation engines."""

    @abstractmethod
    def run(self, inputs: Dict[str, Any], parameters: Dict[str, Any]) -> SimulationResult:
        """Run a simulation with given inputs and parameters."""
        pass

    @abstractmethod
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate that inputs are suitable for this engine."""
        pass

    @abstractmethod
    def get_metadata(self) -> SimulationMetadata:
        """Get metadata about this engine."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """List capabilities of this engine (e.g., 'property_prediction', 'docking', 'md')."""
        pass


__all__ = [
    "SimulationEngine",
    "SimulationResult",
    "SimulationMetadata",
    "DockingResult",
    "DockingPose",
    "MolecularDynamicsResult",
    "PropertyPredictionResult",
    "ReactionModelingResult",
]
