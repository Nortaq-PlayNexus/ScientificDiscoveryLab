# tests/unit/test_plant_engine.py
from src.plant.engine import (
    PlantProfile, get_plant_template, constituent_placeholder,
    concentration_range_placeholder, decompose_plant_ingredients,
    CONSTITUENT_UNKNOWN, CONCENTRATION_UNKNOWN,
)

def test_plant_template_unknown():
    template = get_plant_template()
    assert template["scientific_name"] == CONSTITUENT_UNKNOWN
    assert template["common_names"] == []
    assert template["plant_parts"] == []
    assert template["constituents"] == []

def test_constituent_placeholder():
    c = constituent_placeholder("Quercetin")
    assert c["name"] == "Quercetin"
    assert c["smiles"] == CONSTITUENT_UNKNOWN
    assert c["evidence_level"] == "E0"

def test_concentration_range_placeholder():
    cr = concentration_range_placeholder()
    assert cr["low"] is None
    assert cr["high"] is None
    assert cr["unit"] == "unknown"

def test_plant_profile_unknown():
    p = PlantProfile()
    assert p.is_known() is False
    assert p.get_scientific_name() == CONSTITUENT_UNKNOWN

def test_plant_profile_known():
    data = {
        "id": "PLANT-000001",
        "scientific_name": "Quercus robur",
        "common_names": ["English Oak", "Pedunculate Oak"],
        "plant_parts": ["bark", "leaves", "acorns"],
        "constituents": [],
        "concentration_ranges": {},
    }
    p = PlantProfile(data)
    assert p.is_known() is True
    assert p.get_scientific_name() == "Quercus robur"
    assert "English Oak" in p.get_common_names()

def test_decompose_plant_ingredients_empty():
    ingredients = decompose_plant_ingredients({"constituents": []})
    assert len(ingredients) == 1
    assert ingredients[0]["name"] == "Plant"
    assert ingredients[0]["smiles"] == CONSTITUENT_UNKNOWN
    assert ingredients[0]["evidence_level"] == "E0"

def test_decompose_plant_ingredients_with_constituents():
    data = {
        "scientific_name": "Test Plant",
        "constituents": [
            {"name": "Compound A", "smiles": "CCO", "concentration": 0.05},
            {"name": "Compound B", "smiles": "Cc1ccccc1", "concentration": 0.02},
        ],
    }
    ingredients = decompose_plant_ingredients(data)
    assert len(ingredients) == 2
    assert ingredients[0]["name"] == "Compound A"
    assert ingredients[1]["smiles"] == "Cc1ccccc1"

def test_plant_profile_constituent_smiles():
    data = {
        "scientific_name": "Test",
        "constituents": [
            {"name": "A", "smiles": "CCO"},
            {"name": "B", "smiles": "CCC"},
        ],
    }
    p = PlantProfile(data)
    smiles = p.constituent_smiles()
    assert "CCO" in smiles
    assert "CCC" in smiles

def test_plant_profile_to_dict():
    p = PlantProfile()
    d = p.to_dict()
    assert isinstance(d, dict)
    assert "scientific_name" in d
