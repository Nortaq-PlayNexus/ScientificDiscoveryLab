from typing import Dict, List, Any, Optional
from datetime import datetime


CONSTITUENT_UNKNOWN = "UNKNOWN"
CONCENTRATION_UNKNOWN = "UNKNOWN"


def get_plant_template() -> Dict[str, Any]:
    return {
        "id": None,
        "scientific_name": CONSTITUENT_UNKNOWN,
        "common_names": [],
        "taxonomy": {
            "kingdom": CONSTITUENT_UNKNOWN,
            "phylum": CONSTITUENT_UNKNOWN,
            "class": CONSTITUENT_UNKNOWN,
            "order": CONSTITUENT_UNKNOWN,
            "family": CONSTITUENT_UNKNOWN,
            "genus": CONSTITUENT_UNKNOWN,
            "species": CONSTITUENT_UNKNOWN,
        },
        "plant_parts": [],
        "constituents": [],
        "concentration_ranges": {},
        "extraction_method": CONSTITUENT_UNKNOWN,
        "literature": [],
        "evidence": {
            "level": "E0",
            "source": "User-provided or database-derived",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


def constituent_placeholder(name: str = "Component") -> Dict[str, str]:
    return {
        "name": name,
        "smiles": CONSTITUENT_UNKNOWN,
        "inchi": CONSTITUENT_UNKNOWN,
        "concentration": CONCENTRATION_UNKNOWN,
        "concentration_unit": CONSTITUENT_UNKNOWN,
        "evidence_level": "E0",
        "source": CONSTITUENT_UNKNOWN,
    }


def concentration_range_placeholder(low: Optional[float] = None, high: Optional[float] = None, unit: str = "unknown") -> Dict[str, Any]:
    return {
        "low": low,
        "high": high,
        "unit": unit,
        "note": CONSTITUENT_UNKNOWN if (low is None and high is None) else f"Range {low}-{high} {unit}",
    }


def decompose_plant_ingredients(plant_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    ingredients = []
    constituents = plant_data.get("constituents", [])
    if not constituents or constituents == [CONSTITUENT_UNKNOWN]:
        return [constituent_placeholder(plant_data.get("scientific_name", "Plant"))]

    for c in constituents:
        if isinstance(c, dict):
            ingredients.append({
                "name": c.get("name", CONSTITUENT_UNKNOWN),
                "smiles": c.get("smiles", CONSTITUENT_UNKNOWN),
                "inchi": c.get("inchi", CONSTITUENT_UNKNOWN),
                "concentration": c.get("concentration", CONCENTRATION_UNKNOWN),
                "concentration_unit": c.get("concentration_unit", CONSTITUENT_UNKNOWN),
                "evidence_level": c.get("evidence_level", "E0"),
                "source": c.get("source", CONSTITUENT_UNKNOWN),
            })
        else:
            ingredients.append(constituent_placeholder(str(c)))
    return ingredients


class PlantProfile:
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self.data = data or get_plant_template()

    def get_id(self) -> Optional[str]:
        return self.data.get("id")

    def get_scientific_name(self) -> str:
        return self.data.get("scientific_name", CONSTITUENT_UNKNOWN)

    def get_common_names(self) -> List[str]:
        return self.data.get("common_names", [])

    def get_plant_parts(self) -> List[str]:
        return self.data.get("plant_parts", [])

    def get_constituents(self) -> List[Dict[str, Any]]:
        return self.data.get("constituents", [])

    def get_concentration_ranges(self) -> Dict[str, Any]:
        return self.data.get("concentration_ranges", {})

    def get_evidence(self) -> Dict[str, Any]:
        return self.data.get("evidence", {})

    def is_known(self) -> bool:
        return self.get_scientific_name() != CONSTITUENT_UNKNOWN

    def to_dict(self) -> Dict[str, Any]:
        return self.data

    def constituent_smiles(self) -> List[str]:
        return [c.get("smiles", CONSTITUENT_UNKNOWN) for c in self.get_constituents()]


__all__ = [
    "PlantProfile",
    "get_plant_template",
    "constituent_placeholder",
    "concentration_range_placeholder",
    "decompose_plant_ingredients",
    "CONSTITUENT_UNKNOWN",
    "CONCENTRATION_UNKNOWN",
]
