# tests/unit/test_molecular.py
from src.utils.validator import (
    validate_smiles, get_molecule_descriptors, canonicalize_smiles,
    smiles_to_inchi, smiles_to_inchikey, tanimoto_similarity,
)

# Test data
ETHANOL_SMILES = "CCO"
BENZENE_SMILES = "c1ccccc1"
PHENOL_SMILES = "c1ccc(O)cc1"
INVALID_SMILES = "INVALID"

def test_smiles_validation_valid():
    result = validate_smiles(ETHANOL_SMILES)
    assert result["valid"] is True
    assert result["molecule"] is not None

def test_smiles_validation_invalid():
    result = validate_smiles(INVALID_SMILES)
    assert result["valid"] is False
    assert result["molecule"] is None
    assert "error" in result

def test_molecule_descriptors_ethanol():
    mol = validate_smiles(ETHANOL_SMILES)["molecule"]
    desc = get_molecule_descriptors(mol)
    assert desc["molecular_weight"] > 0
    assert desc["num_atoms"] > 0
    assert "logp" in desc
    assert "tpsa" in desc
    assert desc["num_h_donors"] == 1
    assert desc["num_h_acceptors"] == 1

def test_molecule_descriptors_benzene():
    mol = validate_smiles(BENZENE_SMILES)["molecule"]
    desc = get_molecule_descriptors(mol)
    assert desc["molecular_weight"] > 75.0
    assert desc["molecular_weight"] < 80.0
    assert desc["num_aromatic_rings"] == 1

def test_inchi_conversion():
    inchi = smiles_to_inchi(ETHANOL_SMILES)
    assert inchi is not None
    assert "InChI" in inchi

def test_inchikey_length():
    inchikey = smiles_to_inchikey(ETHANOL_SMILES)
    assert inchikey is not None
    assert len(inchikey) == 27

def test_canonicalize():
    canonical = canonicalize_smiles(ETHANOL_SMILES)
    assert canonical is not None
    assert "C" in canonical

def test_tanimoto_similarity_range():
    sim = tanimoto_similarity(BENZENE_SMILES, PHENOL_SMILES)
    assert sim is not None
    assert 0.0 <= sim <= 1.0

def test_similarity_self():
    sim = tanimoto_similarity(BENZENE_SMILES, BENZENE_SMILES)
    assert sim == 1.0

def test_similarity_different():
    sim1 = tanimoto_similarity(BENZENE_SMILES, PHENOL_SMILES)
    assert sim1 < 1.0
    assert sim1 > 0.0

def test_formula():
    from src.utils.validator import get_molecular_formula
    formula = get_molecular_formula(ETHANOL_SMILES)
    assert formula == "C2H6O"
