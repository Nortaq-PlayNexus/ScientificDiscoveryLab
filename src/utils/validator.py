from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from typing import Optional
import json


def validate_smiles(smiles: str) -> dict:
    """Validate a SMILES string. Returns dict with valid flag and molecule."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"valid": False, "smiles": smiles, "error": "Invalid SMILES", "molecule": None}
    return {"valid": True, "smiles": smiles, "molecule": mol, "error": None}


def get_molecule_descriptors(mol) -> dict:
    """Compute all molecular descriptors for a valid RDKit molecule."""
    if mol is None:
        return {}
    return {
        "molecular_formula": rdMolDescriptors.CalcMolFormula(mol),
        "molecular_weight": round(Descriptors.MolWt(mol), 4),
        "exact_molecular_weight": round(Descriptors.ExactMolWt(mol), 4),
        "logp": round(Descriptors.MolLogP(mol), 4),
        "tpsa": round(Descriptors.TPSA(mol), 4),
        "num_h_donors": Descriptors.NumHDonors(mol),
        "num_h_acceptors": Descriptors.NumHAcceptors(mol),
        "num_rotatable_bonds": Descriptors.NumRotatableBonds(mol),
        "num_rings": Descriptors.RingCount(mol),
        "num_atoms": mol.GetNumAtoms(),
        "num_bonds": mol.GetNumBonds(),
        "num_stereocenters": Descriptors.NumAtomStereoCenters(mol),
        "num_unspecified_stereocenters": Descriptors.NumUnspecifiedAtomStereoCenters(mol),
        "num_aromatic_rings": Descriptors.NumAromaticRings(mol),
        "num_aromatic_carbocycles": Descriptors.NumAromaticCarbocycles(mol),
        "max_abs_partial_charge": round(Descriptors.MaxAbsPartialCharge(mol), 4),
        "heavy_atom_count": Descriptors.HeavyAtomCount(mol),
    }


def get_molecular_formula(smiles: str) -> Optional[str]:
    """Get molecular formula from SMILES."""
    result = validate_smiles(smiles)
    if not result["valid"]:
        return None
    return rdMolDescriptors.CalcMolFormula(result["molecule"])


def compute_fingerprints(mol, radius: int = 2) -> dict:
    """Compute molecular fingerprints."""
    if mol is None:
        return {}
    from rdkit import DataStructs
    morgan = rdMolDescriptors.GetMorganFingerprintAsBitVect(mol, radius)
    return {
        "morgan_radius_2": morgan.ToBitString(),
        "morgan_on_bits": len(morgan.GetOnBits()),
    }


def smiles_to_inchi(smiles: str) -> Optional[str]:
    """Convert SMILES to InChI."""
    result = validate_smiles(smiles)
    if not result["valid"]:
        return None
    return Chem.MolToInchi(result["molecule"])


def smiles_to_inchikey(smiles: str) -> Optional[str]:
    """Convert SMILES to InChIKey."""
    result = validate_smiles(smiles)
    if not result["valid"]:
        return None
    inchi = Chem.MolToInchi(result["molecule"])
    if inchi:
        return Chem.InchiToInchiKey(inchi)
    return None


def canonicalize_smiles(smiles: str) -> Optional[str]:
    """Canonicalize a SMILES string."""
    result = validate_smiles(smiles)
    if not result["valid"]:
        return None
    return Chem.MolToSmiles(result["molecule"], canonical=True)


def are_isomers(smiles1: str, smiles2: str) -> Optional[bool]:
    """Check if two SMILES are isomers (same formula, different structure)."""
    m1 = validate_smiles(smiles1)["molecule"]
    m2 = validate_smiles(smiles2)["molecule"]
    if m1 is None or m2 is None:
        return None
    f1 = rdMolDescriptors.CalcMolFormula(m1)
    f2 = rdMolDescriptors.CalcMolFormula(m2)
    return f1 == f2 and m1.GetSmiles() != m2.GetSmiles()


def tanimoto_similarity(smiles1: str, smiles2: str) -> Optional[float]:
    """Compute Tanimoto similarity between two molecules."""
    m1 = validate_smiles(smiles1)["molecule"]
    m2 = validate_smiles(smiles2)["molecule"]
    if m1 is None or m2 is None:
        return None
    fp1 = rdMolDescriptors.GetMorganFingerprintAsBitVect(m1, 2)
    fp2 = rdMolDescriptors.GetMorganFingerprintAsBitVect(m2, 2)
    from rdkit import DataStructs
    return DataStructs.TanimotoSimilarity(fp1, fp2)


__all__ = [
    "validate_smiles",
    "get_molecule_descriptors",
    "get_molecular_formula",
    "compute_fingerprints",
    "smiles_to_inchi",
    "smiles_to_inchikey",
    "canonicalize_smiles",
    "are_isomers",
    "tanimoto_similarity",
]
