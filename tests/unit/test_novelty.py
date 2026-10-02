# tests/unit/test_novelty.py
from src.novelty import NoveltyResult, NoveltyEngine

def test_novelty_result_unknown():
    result = NoveltyResult.unknown_result("Test", "compound", ["PubChem", "ChEBI"])
    assert result.is_known is False
    assert "No matching record was found" in result.details["statement"]
    assert "does not establish priority" in result.details["caveat"]
    assert "2026" in result.details["statement"]  # current year

def test_engine_init():
    engine = NoveltyEngine()
    assert len(engine.sources_searched) == 0

def test_pubchem_search_invalid():
    """Search with invalid SMILES should return no matches."""
    engine = NoveltyEngine()
    result = engine.search_pubchem("INVALID")
    assert result["found"] is False
    assert result["source"] == "PubChem"

def test_check_novelty_returns_unknown_format():
    """Check that novelty check never claims 'first discovery'."""
    engine = NoveltyEngine()
    result = engine.check_novelty(smiles="CCO")
    assert "first discovery" not in str(result).lower()
    assert "No matching record was found" in result.get("statement", "") or result["novelty"] == "KNOWN"

def test_check_reaction_novelty():
    engine = NoveltyEngine()
    result = engine.check_reaction_novelty(["CCO"], ["CCO"])
    assert "No matching reaction was found" in result["statement"]
    assert "does not establish priority" in result["caveat"]
    assert result["is_known"] is False

def test_novelty_never_claims_first():
    """CRITICAL: Never claim 'first discovery'."""
    engine = NoveltyEngine()
    # Try various scenarios
    for smiles in ["CCO", "c1ccccc1", "INVALID"]:
        result = engine.check_novelty(smiles=smiles)
        statement = result.get("statement", "")
        assert "first discovery" not in statement.lower(), \
            f"Novelty check should never claim 'first discovery' for {smiles}"
        assert "No matching record was found" in statement or result["novelty"] == "KNOWN"
