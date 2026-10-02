from enum import Enum
from datetime import datetime
from typing import Optional


class EvidenceLevel(str, Enum):
    E0 = "E0"
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"
    E4 = "E4"
    E5 = "E5"
    E6 = "E6"

    def is_computational(self) -> bool:
        return self in (EvidenceLevel.E0, EvidenceLevel.E3, EvidenceLevel.E4)

    def is_fact(self) -> bool:
        return self in (EvidenceLevel.E1, EvidenceLevel.E2, EvidenceLevel.E5, EvidenceLevel.E6)

    def is_validated(self) -> bool:
        return self == EvidenceLevel.E6


class EvidenceSourceType(str, Enum):
    DATABASE = "database"
    LITERATURE = "literature"
    COMPUTATIONAL = "computational"
    AI = "ai"
    EXPERIMENTAL = "experimental"
    REPRODUCED = "reproduced"


class Evidence:
    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        level: EvidenceLevel,
        source: str,
        source_type: EvidenceSourceType,
        timestamp: Optional[str] = None,
        software_version: Optional[str] = None,
        model_version: Optional[str] = None,
        parameters: Optional[dict] = None,
        random_seed: Optional[int] = None,
        input_structures: Optional[list] = None,
        input_concentrations: Optional[dict] = None,
        assumptions: Optional[list] = None,
        computational_method: Optional[str] = None,
        output: Optional[dict] = None,
        uncertainty: Optional[str] = None,
        reproducibility_info: Optional[str] = None,
    ):
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.level = level
        self.source = source
        self.source_type = source_type
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.software_version = software_version
        self.model_version = model_version
        self.parameters = parameters or {}
        self.random_seed = random_seed
        self.input_structures = input_structures or []
        self.input_concentrations = input_concentrations or {}
        self.assumptions = assumptions or []
        self.computational_method = computational_method
        self.output = output or {}
        self.uncertainty = uncertainty
        self.reproducibility_info = reproducibility_info

    def is_computational(self) -> bool:
        return self.level.is_computational()

    def is_fact(self) -> bool:
        return self.level.is_fact()

    def is_validated(self) -> bool:
        return self.level.is_validated()

    def to_dict(self) -> dict:
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "level": self.level.value,
            "source": self.source,
            "source_type": self.source_type.value,
            "timestamp": self.timestamp,
            "software_version": self.software_version,
            "model_version": self.model_version,
            "parameters": self.parameters,
            "random_seed": self.random_seed,
            "input_structures": self.input_structures,
            "input_concentrations": self.input_concentrations,
            "assumptions": self.assumptions,
            "computational_method": self.computational_method,
            "output": self.output,
            "uncertainty": self.uncertainty,
            "reproducibility_info": self.reproducibility_info,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Evidence":
        data["level"] = EvidenceLevel(data["level"])
        data["source_type"] = EvidenceSourceType(data["source_type"])
        return cls(**data)

    def __repr__(self) -> str:
        return f"Evidence({self.entity_id}, {self.level.value}, {self.source})"


__all__ = [
    "EvidenceLevel",
    "EvidenceSourceType",
    "Evidence",
]
