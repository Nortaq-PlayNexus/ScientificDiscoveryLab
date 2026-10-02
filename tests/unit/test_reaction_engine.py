# tests/unit/test_reaction_engine.py
from src.reaction.engine import (
    analyze_reaction, classify_reaction, get_known_reaction_types,
    reaction_feasibility,
)
from src.reaction.mixer import (
    VirtualMixer, classify_interaction, decompose_ingredients,
)

ETHANOL = "CCO"
BENZENE = "c1ccccc1"
INVALID = "INVALID"

def test_analyze_reaction_valid():
    result = analyze_reaction(BENZENE, ETHANOL)
    assert result["compound_a_valid"] is True
    assert result["compound_b_valid"] is True
    assert "caveats" in result

def test_analyze_reaction_invalid():
    result = analyze_reaction(INVALID, ETHANOL)
    assert result["compound_a_valid"] is False

def test_get_known_reaction_types():
    types = get_known_reaction_types()
    assert len(types) >= 10

def test_classify_reaction_basic():
    result = classify_reaction([ETHANOL], [BENZENE])
    assert "reaction_class" in result
    assert "confidence" in result
    assert "evidence_level" in result

def test_reaction_feasibility_basic():
    result = reaction_feasibility([ETHANOL, BENZENE], {"temperature": 100})
    assert "feasibility" in result
    assert result["confidence"] == 0.0
    assert result["evidence_level"] == "E0"

def test_mixer_add_ingredients():
    m = VirtualMixer()
    m.add_ingredient(BENZENE)
    m.add_ingredient(ETHANOL)
    assert len(m.get_ingredients()) == 2

def test_mixer_mix():
    m = VirtualMixer()
    m.add_ingredient(BENZENE)
    m.add_ingredient(ETHANOL)
    m.add_ingredient(INVALID)
    result = m.mix()
    assert "interactions" in result
    assert "summary" in result
    assert result["summary"]["total_pairs"] == 3
    assert result["summary"]["potential_interactions"] == 0
    assert "caveat" in result

def test_mixer_classify_interaction():
    result = classify_interaction(BENZENE, ETHANOL)
    assert result["classification"] == "INSUFFICIENT DATA"
    assert result["analyzer_classification"] == "NO_KNOWN_REACTION"
    assert result["evidence_level"] == "E0"

def test_mixer_classify_interaction_invalid():
    result = classify_interaction(INVALID, ETHANOL)
    assert result["classification"] == "INSUFFICIENT DATA"

def test_decompose_ingredients():
    ingredients = decompose_ingredients([BENZENE, ETHANOL])
    assert len(ingredients) == 2
    assert ingredients[0]["valid"] is True

def test_classify_interaction_similar():
    result = classify_interaction("CCCCCCCCCC", "CCCCCCCCCCC")
    assert result["analyzer_classification"] == "SIMILAR_STRUCTURES"
    assert result["classification"] == "INSUFFICIENT DATA"
    assert result["evidence_level"] == "E0"
    assert result["similarity"] > 0.8
