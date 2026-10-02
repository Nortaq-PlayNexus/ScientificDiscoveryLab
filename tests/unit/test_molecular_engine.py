# tests/unit/test_molecular_engine.py
from src.molecular.engine import (
    MoleculeInspector, get_molecule_descriptors, validate_smiles,
    smiles_to_inchi, smiles_to_inchikey, canonicalize_smiles,
    tanimoto_similarity, get_fingerprints, get_functional_groups,
    get_stereochemistry, is_duplicate, is_valid_structure,
    analyze_reaction, classify_reaction, get_known_reaction_types,
)

ETHANOL = "CCO"
BENZENE = "c1ccccc1"
PHENOL = "c1ccc(O)cc1"
INVALID = "INVALID"

def test_inspector_valid():
    insp = MoleculeInspector(ETHANOL)
    assert insp.is_valid is True

def test_inspector_invalid():
    insp = MoleculeInspector(INVALID)
    assert insp.is_valid is False

def test_inspector_all_descriptors():
    insp = MoleculeInspector(BENZENE)
    d = insp.get_all_descriptors()
    assert d["valid"] is True
    assert "mw" in d
    assert "inchi" in d
    assert "inchikey" in d
    assert "formula" in d
    assert "logp" in d
    assert d["smiles"] is not None

def test_inspector_formal_charge_is_net_integer_charge():
    assert MoleculeInspector(ETHANOL).get_formal_charge() == 0
    assert MoleculeInspector("CC(=O)[O-]").get_formal_charge() == -1
    assert MoleculeInspector("C[NH3+]").get_formal_charge() == 1


def test_inspector_partial_charge_has_separate_field():
    inspector = MoleculeInspector(ETHANOL)
    descriptors = inspector.get_all_descriptors()
    assert descriptors["formal_charge"] == 0
    assert descriptors["max_abs_partial_charge"] > 0
    assert descriptors["max_abs_partial_charge"] != descriptors["formal_charge"]


def test_inspector_2d_structure_returns_png_bytes():
    image = MoleculeInspector(BENZENE).get_2d_structure(width=240, height=180)
    assert isinstance(image, bytes)
    assert image.startswith(b"\x89PNG\r\n\x1a\n")
    assert MoleculeInspector(INVALID).get_2d_structure() is None


def test_inspector_functional_groups():
    insp = MoleculeInspector(ETHANOL)
    groups = insp.get_functional_groups()
    assert isinstance(groups, list)

def test_inspector_stereochemistry():
    insp = MoleculeInspector(BENZENE)
    stereo = insp.get_stereochemistry()
    assert stereo["valid"] is True

def test_inspector_fingerprints():
    insp = MoleculeInspector(BENZENE)
    fp = insp.get_fingerprints()
    assert fp is not None
    assert "bit_string" in fp
    assert fp["on_bits"] > 0

def test_get_molecule_descriptors_benzene():
    from rdkit import Chem
    mol = Chem.MolFromSmiles(BENZENE)
    desc = get_molecule_descriptors(mol)
    assert desc["molecular_weight"] > 75.0

def test_validate_smiles_valid():
    assert validate_smiles(ETHANOL)["valid"] is True

def test_validate_smiles_invalid():
    assert validate_smiles(INVALID)["valid"] is False

def test_smiles_to_inchi():
    inchi = smiles_to_inchi(ETHANOL)
    assert inchi is not None

def test_smiles_to_inchikey():
    ik = smiles_to_inchikey(ETHANOL)
    assert ik is not None
    assert len(ik) == 27

def test_canonicalize():
    c = canonicalize_smiles(ETHANOL)
    assert c is not None

def test_tanimoto_self():
    assert tanimoto_similarity(BENZENE, BENZENE) == 1.0

def test_tanimoto_different():
    sim = tanimoto_similarity(BENZENE, PHENOL)
    assert 0.0 < sim < 1.0

def test_get_fingerprints():
    from rdkit import Chem
    mol = Chem.MolFromSmiles(BENZENE)
    fp = get_fingerprints(mol)
    assert fp["on_bits"] > 0

def test_get_known_reaction_types():
    types = get_known_reaction_types()
    assert len(types) > 0
    assert "Oxidation" in types

def test_analyze_reaction():
    result = analyze_reaction(BENZENE, PHENOL)
    assert result["compound_a_valid"] is True
    assert result["compound_b_valid"] is True
    assert "caveats" in result

def test_classify_reaction():
    result = classify_reaction([ETHANOL], [BENZENE])
    assert "classification" in result
    assert "evidence_level" in result

def test_is_duplicate_same():
    assert is_duplicate(ETHANOL, "CCO") is True

def test_is_duplicate_different():
    assert is_duplicate(BENZENE, PHENOL) is False

def test_is_valid_structure():
    assert is_valid_structure(ETHANOL) is True
    assert is_valid_structure(INVALID) is False
