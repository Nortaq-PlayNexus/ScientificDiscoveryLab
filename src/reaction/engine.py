from typing import Dict, List, Any, Optional
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from src.utils.validator import validate_smiles, canonicalize_smiles


REACTION_CLASSIFICATION_RULES = {
    "Oxidation": ["oxidation", "oxidize", "dioxygen", "peroxide"],
    "Reduction": ["reduction", "reduce", "hydrogenation", "H2"],
    "Hydrolysis": ["hydrolysis", "water", "H2O"],
    "Esterification": ["ester", "esterification", "acid + alcohol"],
    "Amidation": ["amide", "amidation", "amine + acid"],
    "Substitution": ["substitution", "SN1", "SN2", "halide", "nucleophilic"],
    "Elimination": ["elimination", "E1", "E2", "dehydration"],
    "Addition": ["addition", "alkene", "alkyne", "double bond"],
    "Rearrangement": ["rearrangement", "rearrange", "Wagner", "pinacol"],
    "Polymerization": ["polymer", "polymerization", "oligomer"],
    "Condensation": ["condensation", "condense"],
}


def get_known_reaction_types() -> List[str]:
    return list(REACTION_CLASSIFICATION_RULES.keys())


def classify_reaction(reactants: List[str], products: List[str], conditions: Optional[Dict] = None) -> Dict[str, Any]:
    smiles_list = list(reactants) + list(products)
    for smiles in smiles_list:
        result = validate_smiles(smiles)
        if not result["valid"]:
            return {
                "classification": "INVALID_STRUCTURE",
                "confidence": 0.0,
                "evidence_level": "E0",
                "error": f"Invalid SMILES: {smiles}",
            }

    conditions_text = ""
    if conditions:
        conditions_text = " ".join(str(v) for v in conditions.values()).lower()

    best_match = "UNKNOWN"
    best_score = 0
    for rclass, keywords in REACTION_CLASSIFICATION_RULES.items():
        score = sum(1 for kw in keywords if kw in conditions_text)
        if score > best_score:
            best_score = score
            best_match = rclass

    return {
        "reactants": reactants,
        "products": products,
        "reaction_class": best_match,
        "confidence": min(best_score / 3.0, 1.0) if best_score > 0 else 0.0,
        "evidence_level": "E0" if best_score == 0 else "E3",
        "caveat": "Classification based on condition keywords only. No SMARTS matching yet.",
    }


def reaction_feasibility(reactants: List[str], conditions: Optional[Dict] = None) -> Dict[str, Any]:
    for smiles in reactants:
        result = validate_smiles(smiles)
        if not result["valid"]:
            return {
                "feasibility": "INVALID_INPUT",
                "confidence": 0.0,
                "evidence_level": "E0",
                "error": f"Invalid SMILES: {smiles}",
            }

    return {
        "reactants": reactants,
        "conditions": conditions or {},
        "feasibility": "UNKNOWN",
        "confidence": 0.0,
        "evidence_level": "E0",
        "caveat": "Feasibility cannot be determined without known reaction rules or experimental data.",
    }


def analyze_reaction(compound_a: str, compound_b: str, conditions: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    result_a = validate_smiles(compound_a)
    result_b = validate_smiles(compound_b)
    a_valid = result_a["valid"]
    b_valid = result_b["valid"]

    products = []
    reaction_smarts = None
    reaction_class = "UNKNOWN"
    similarity = None

    if a_valid and b_valid:
        mol_a = result_a["molecule"]
        mol_b = result_b["molecule"]
        fingerprint_match = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol_a, 2)
        fp_b = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol_b, 2)
        from rdkit import DataStructs
        similarity = DataStructs.TanimotoSimilarity(fingerprint_match, fp_b)
        if similarity > 0.8:
            reaction_class = "SIMILAR_STRUCTURES"
        else:
            reaction_class = "NO_KNOWN_REACTION"
    elif a_valid:
        reaction_class = "SINGLE_COMPOUND"
    else:
        reaction_class = "INVALID_INPUT"

    return {
        "compound_a": compound_a,
        "compound_a_valid": a_valid,
        "compound_b": compound_b,
        "compound_b_valid": b_valid,
        "possible_products": products,
        "reaction_smarts": reaction_smarts,
        "reaction_class": reaction_class,
        "similarity": similarity,
        "estimated_feasibility": "UNKNOWN",
        "known_literature": [],
        "confidence": 0.0,
        "evidence_level": "E0",
        "caveats": [
            "No automated reaction prediction without established reaction SMARTS rules.",
            "All structures must be computationally validated before further analysis.",
            "This is a computational hypothesis, not experimental fact.",
        ],
    }


__all__ = [
    "analyze_reaction",
    "classify_reaction",
    "get_known_reaction_types",
    "reaction_feasibility",
]
