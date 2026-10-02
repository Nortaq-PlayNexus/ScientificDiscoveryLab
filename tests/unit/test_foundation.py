from src.utils.validator import validate_smiles

def test_validate_valid_smiles():
    result = validate_smiles("CCO")
    assert result["valid"] is True
    assert result["molecule"] is not None

def test_validate_invalid_smiles():
    result = validate_smiles("INVALID")
    assert result["valid"] is False
    assert result["molecule"] is None

def test_get_molecule_descriptors():
    result = validate_smiles("c1ccccc1")
    assert result["valid"] is True
    mol = result["molecule"]
    from src.utils.validator import get_molecule_descriptors
    desc = get_molecule_descriptors(mol)
    assert "molecular_weight" in desc
    assert desc["molecular_weight"] > 0
    assert "logp" in desc
    assert "tpsa" in desc

def test_smiles_to_inchi():
    inchi = validate_smiles("CCO")
    from src.utils.validator import smiles_to_inchi
    result = smiles_to_inchi("CCO")
    assert result is not None

def test_smiles_to_inchikey():
    from src.utils.validator import smiles_to_inchikey
    result = smiles_to_inchikey("CCO")
    assert result is not None
    assert len(result) == 27

def test_canonicalize_smiles():
    from src.utils.validator import canonicalize_smiles
    result = canonicalize_smiles("CCO")
    assert result is not None

def test_tanimoto_similarity():
    from src.utils.validator import tanimoto_similarity
    sim = tanimoto_similarity("c1ccccc1", "c1ccc(O)cc1")
    assert sim is not None
    assert 0.0 <= sim <= 1.0

def test_evidence_level_e0_is_computational():
    from src.evidence import EvidenceLevel
    assert EvidenceLevel.E0.is_computational() is True
    assert EvidenceLevel.E0.is_fact() is False

def test_evidence_level_e6_is_validated():
    from src.evidence import EvidenceLevel
    assert EvidenceLevel.E6.is_validated() is True
    assert EvidenceLevel.E6.is_computational() is False

def test_evidence_e3_not_displayed_as_fact():
    from src.evidence import EvidenceLevel
    assert EvidenceLevel.E3.is_fact() is False
