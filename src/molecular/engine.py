from io import BytesIO

from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, rdDepictor, FunctionalGroups
from rdkit.Chem.Draw import MolToImage
from typing import Optional, Dict, List, Any
import json

from src.utils.validator import (
    validate_smiles,
    get_molecule_descriptors as _desc,
    canonicalize_smiles,
    smiles_to_inchi,
    smiles_to_inchikey,
    tanimoto_similarity as _tanimoto,
)


class MoleculeInspector:
    """Displays comprehensive molecular information."""

    def __init__(self, smiles: str):
        self.smiles = smiles
        self.validation = validate_smiles(smiles)
        self.mol = self.validation["molecule"]
        self.is_valid = self.validation["valid"]

    def get_2d_structure(self, width: int = 300, height: int = 300) -> Optional[bytes]:
        """Return a PNG depiction, or ``None`` for an invalid structure."""
        if not self.is_valid:
            return None
        if width <= 0 or height <= 0:
            raise ValueError("Depiction width and height must be positive")
        rdDepictor.Compute2DCoords(self.mol)
        image = MolToImage(self.mol, size=(width, height))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def get_smiles(self) -> Optional[str]:
        if not self.is_valid:
            return None
        return canonicalize_smiles(self.smiles)

    def get_inchi(self) -> Optional[str]:
        return smiles_to_inchi(self.smiles)

    def get_inchikey(self) -> Optional[str]:
        return smiles_to_inchikey(self.smiles)

    def get_formula(self) -> Optional[str]:
        if not self.is_valid:
            return None
        return rdMolDescriptors.CalcMolFormula(self.mol)

    def get_mw(self) -> Optional[float]:
        if not self.is_valid:
            return None
        return round(Descriptors.MolWt(self.mol), 4)

    def get_logp(self) -> Optional[float]:
        if not self.is_valid:
            return None
        return round(Descriptors.MolLogP(self.mol), 4)

    def get_tpsa(self) -> Optional[float]:
        if not self.is_valid:
            return None
        return round(Descriptors.TPSA(self.mol), 4)

    def get_hbd(self) -> Optional[int]:
        if not self.is_valid:
            return None
        return Descriptors.NumHDonors(self.mol)

    def get_hba(self) -> Optional[int]:
        if not self.is_valid:
            return None
        return Descriptors.NumHAcceptors(self.mol)

    def get_rotatable_bonds(self) -> Optional[int]:
        if not self.is_valid:
            return None
        return Descriptors.NumRotatableBonds(self.mol)

    def get_formal_charge(self) -> Optional[int]:
        """Return the molecule's net formal charge (not a partial charge)."""
        if not self.is_valid:
            return None
        return int(Chem.GetFormalCharge(self.mol))

    def get_max_abs_partial_charge(self) -> Optional[float]:
        """Return RDKit's maximum absolute Gasteiger partial charge."""
        if not self.is_valid:
            return None
        try:
            return float(Descriptors.MaxAbsPartialCharge(self.mol))
        except Exception:
            return None

    def get_stereocenters(self) -> Optional[int]:
        if not self.is_valid:
            return None
        return Descriptors.NumAtomStereoCenters(self.mol)

    def get_functional_groups(self) -> List[str]:
        if not self.is_valid:
            return []
        try:
            fp = FunctionalGroups.CreateMolFingerprint(self.mol)
            return [str(fp)] if fp else []
        except Exception:
            return []

    def get_all_descriptors(self) -> Dict[str, Any]:
        if not self.is_valid:
            return {"valid": False, "smiles": self.smiles, "error": "Invalid SMILES"}
        return {
            "valid": True,
            "smiles": self.get_smiles(),
            "inchi": self.get_inchi(),
            "inchikey": self.get_inchikey(),
            "formula": self.get_formula(),
            "mw": self.get_mw(),
            "logp": self.get_logp(),
            "tpsa": self.get_tpsa(),
            "hbd": self.get_hbd(),
            "hba": self.get_hba(),
            "rotatable_bonds": self.get_rotatable_bonds(),
            "formal_charge": self.get_formal_charge(),
            "max_abs_partial_charge": self.get_max_abs_partial_charge(),
            "stereocenters": self.get_stereocenters(),
            "functional_groups": self.get_functional_groups(),
            "fingerprint": self.get_fingerprints(),
        }

    def get_fingerprints(self, radius: int = 2) -> Optional[Dict]:
        if not self.is_valid:
            return None
        fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(self.mol, radius)
        return {
            "radius": radius,
            "bit_string": fp.ToBitString(),
            "on_bits": len(fp.GetOnBits()),
        }

    def get_stereochemistry(self) -> Dict[str, Any]:
        if not self.is_valid:
            return {"valid": False}
        return {
            "valid": True,
            "num_stereocenters": Descriptors.NumAtomStereoCenters(self.mol),
            "num_unspecified": Descriptors.NumUnspecifiedAtomStereoCenters(self.mol),
            "has_chiral_centers": Descriptors.NumAtomStereoCenters(self.mol) > 0,
        }

    def is_valid_structure(self) -> bool:
        return self.is_valid


def get_molecule_descriptors(mol) -> dict:
    return _desc(mol)


def tanimoto_similarity(smiles1: str, smiles2: str) -> Optional[float]:
    return _tanimoto(smiles1, smiles2)


def get_fingerprints(mol, radius: int = 2) -> Optional[Dict]:
    if mol is None:
        return None
    fp = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius)
    return {
        "radius": radius,
        "bit_string": fp.ToBitString(),
        "on_bits": len(fp.GetOnBits()),
    }


def get_functional_groups(mol) -> List[str]:
    if mol is None:
        return []
    try:
        fp = FunctionalGroups.CreateMolFingerprint(mol)
        return [str(fp)] if fp else []
    except Exception:
        return []


def get_stereochemistry(mol) -> Dict[str, Any]:
    if mol is None:
        return {"valid": False}
    return {
        "valid": True,
        "num_stereocenters": Descriptors.NumAtomStereoCenters(mol),
        "num_unspecified": Descriptors.NumUnspecifiedAtomStereoCenters(mol),
        "has_chiral_centers": Descriptors.NumAtomStereoCenters(mol) > 0,
    }


def is_duplicate(smiles1: str, smiles2: str) -> Optional[bool]:
    c1 = canonicalize_smiles(smiles1)
    c2 = canonicalize_smiles(smiles2)
    if c1 is None or c2 is None:
        return None
    return c1 == c2


def is_valid_structure(smiles: str) -> bool:
    return validate_smiles(smiles)["valid"]


def get_known_reaction_types() -> List[str]:
    return [
        "Oxidation",
        "Reduction",
        "Hydrolysis",
        "Esterification",
        "Amidation",
        "Substitution (SN1/SN2)",
        "Elimination",
        "Addition",
        "Rearrangement",
        "Polymerization",
        "Condensation",
        "Dehydration",
        "Halogenation",
        "Nitration",
        "Sulfonation",
        "Friedel-Crafts",
        "Grignard",
        "Aldol",
        "Diels-Alder",
        "Cylization",
    ]


def classify_reaction(reactants: List[str], products: List[str]) -> Dict[str, Any]:
    return {
        "reactants": reactants,
        "products": products,
        "classification": "UNKNOWN",
        "confidence": 0.0,
        "evidence_level": "E0",
        "note": "Manual classification required until automated reaction SMARTS matching is implemented.",
    }


def reaction_feasibility(reactants: List[str], conditions: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "reactants": reactants,
        "conditions": conditions,
        "feasibility": "UNKNOWN",
        "confidence": 0.0,
        "evidence_level": "E0",
        "note": "Feasibility assessment requires known reaction rules or experimental data.",
    }


def analyze_reaction(compound_a: str, compound_b: str, conditions: Optional[Dict] = None) -> Dict[str, Any]:
    result_a = validate_smiles(compound_a)
    result_b = validate_smiles(compound_b)
    return {
        "compound_a": compound_a,
        "compound_a_valid": result_a["valid"],
        "compound_b": compound_b,
        "compound_b_valid": result_b["valid"],
        "possible_products": [],
        "reaction_smarts": None,
        "reaction_class": "UNKNOWN",
        "estimated_feasibility": "UNKNOWN",
        "known_literature": [],
        "confidence": 0.0,
        "evidence_level": "E0",
        "caveats": [
            "No reaction prediction without established reaction rules.",
            "All structures must be computationally validated before further analysis.",
            "This is a computational hypothesis, not experimental fact.",
        ],
    }


__all__ = [
    "MoleculeInspector",
    "get_molecule_descriptors",
    "validate_smiles",
    "smiles_to_inchi",
    "smiles_to_inchikey",
    "canonicalize_smiles",
    "tanimoto_similarity",
    "get_fingerprints",
    "get_functional_groups",
    "get_stereochemistry",
    "is_duplicate",
    "is_valid_structure",
    "get_known_reaction_types",
    "classify_reaction",
    "reaction_feasibility",
    "analyze_reaction",
]
