from typing import Dict, List, Any, Optional
from src.reaction.engine import analyze_reaction, validate_smiles
from src.plant.engine import decompose_plant_ingredients, constituent_placeholder
from src.utils.validator import validate_smiles as _validate_smiles


INTERACTION_CLASSES = [
    "KNOWN REACTION",
    "PREDICTED REACTION",
    "NO KNOWN REACTION",
    "INSUFFICIENT DATA",
    "POTENTIAL INTERACTION",
]


def classify_interaction(compound_a_smiles: str, compound_b_smiles: str, conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    a_result = _validate_smiles(compound_a_smiles)
    b_result = _validate_smiles(compound_b_smiles)

    if not a_result["valid"] or not b_result["valid"]:
        return {
            "classification": "INSUFFICIENT DATA",
            "compound_a_valid": a_result["valid"],
            "compound_b_valid": b_result["valid"],
            "evidence_level": "E0",
            "note": "One or more compounds could not be validated.",
        }

    analysis = analyze_reaction(compound_a_smiles, compound_b_smiles, conditions)
    reaction_class = analysis["reaction_class"]

    if reaction_class == "SIMILAR_STRUCTURES":
        return {
            "classification": "INSUFFICIENT DATA",
            "analyzer_classification": reaction_class,
            "similarity": analysis.get("similarity"),
            "evidence_level": "E0",
            "note": "Structural similarity alone does not predict a reaction or physical interaction.",
        }
    elif reaction_class == "NO KNOWN REACTION":
        return {
            "classification": "INSUFFICIENT DATA",
            "analyzer_classification": reaction_class,
            "evidence_level": "E0",
            "note": "The current analyzer has no reaction rules; this is not evidence that no reaction exists.",
        }
    elif reaction_class == "INVALID_INPUT":
        return {
            "classification": "INSUFFICIENT DATA",
            "analyzer_classification": reaction_class,
            "evidence_level": "E0",
            "note": "Invalid input structures.",
        }
    else:
        return {
            "classification": "INSUFFICIENT DATA",
            "analyzer_classification": reaction_class,
            "evidence_level": "E0",
            "note": "No established reaction rule supports an interaction prediction.",
        }


def decompose_ingredients(ingredients: List[str]) -> List[Dict[str, Any]]:
    """Decompose a list of ingredient SMILES/names into known compounds."""
    results = []
    for ingredient in ingredients:
        result = _validate_smiles(ingredient)
        if result["valid"]:
            results.append({
                "input": ingredient,
                "smiles": ingredient,
                "valid": True,
                "type": "known_compound",
            })
        else:
            results.append({
                "input": ingredient,
                "smiles": None,
                "valid": False,
                "type": "unknown",
                "note": "Could not validate as known compound.",
            })
    return results


class VirtualMixer:
    def __init__(self):
        self.ingredients: List[str] = []
        self.conditions: Dict[str, Any] = {}

    def add_ingredient(self, ingredient: str) -> None:
        self.ingredients.append(ingredient)

    def set_condition(self, key: str, value: Any) -> None:
        self.conditions[key] = value

    def get_ingredients(self) -> List[str]:
        return self.ingredients

    def get_conditions(self) -> Dict[str, Any]:
        return self.conditions

    def mix(self) -> Dict[str, Any]:
        interactions = []
        for i, a in enumerate(self.ingredients):
            for b in self.ingredients[i+1:]:
                result = classify_interaction(a, b, self.conditions)
                interactions.append({
                    "pair": [a, b],
                    "classification": result["classification"],
                    "evidence_level": result["evidence_level"],
                })

        return {
            "ingredients": self.ingredients,
            "conditions": self.conditions,
            "interactions": interactions,
            "summary": {
                "total_pairs": len(interactions),
                "known_reactions": sum(1 for i in interactions if i["classification"] == "KNOWN REACTION"),
                "predicted_reactions": sum(1 for i in interactions if i["classification"] == "PREDICTED REACTION"),
                "no_known_reaction": sum(1 for i in interactions if i["classification"] == "NO KNOWN REACTION"),
                "insufficient_data": sum(1 for i in interactions if i["classification"] == "INSUFFICIENT DATA"),
                "potential_interactions": sum(1 for i in interactions if i["classification"] == "POTENTIAL INTERACTION"),
            },
            "caveat": "Virtual Mixer does not simulate physical mixture behavior. All interactions are classified and evidence-tracked.",
        }


__all__ = [
    "VirtualMixer",
    "classify_interaction",
    "decompose_ingredients",
    "INTERACTION_CLASSES",
]
