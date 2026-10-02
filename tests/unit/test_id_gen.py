# tests/unit/test_id_gen.py
from src.utils.id_gen import generate_stable_id, timestamp_now

def test_generate_stable_id_format():
    uid = generate_stable_id("PLANT", 1)
    assert uid == "PLANT-000001"

def test_generate_stable_id_zero():
    uid = generate_stable_id("CMP", 0)
    assert uid == "CMP-000000"

def test_generate_stable_id_large():
    uid = generate_stable_id("EXP", 999999)
    assert uid == "EXP-999999"

def test_generate_stable_id_custom_prefix():
    uid = generate_stable_id("RXN", 42)
    assert uid == "RXN-000042"

def test_timestamp_format():
    ts = timestamp_now()
    assert ts is not None
    assert "T" in ts or "-" in ts
