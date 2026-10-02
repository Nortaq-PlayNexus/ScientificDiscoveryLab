# tests/unit/test_hypothesis.py
from src.hypothesis import Hypothesis, HypothesisEngine, HypothesisStatus, Prediction

def test_hypothesis_creation():
    h = Hypothesis("HYP-000001", "Test hypothesis")
    assert h.id == "HYP-000001"
    assert h.statement == "Test hypothesis"
    assert h.status == HypothesisStatus.PROPOSED
    assert len(h.history) == 1

def test_hypothesis_status_change():
    h = Hypothesis("HYP-000001", "Test")
    h.set_status(HypothesisStatus.TESTING, "Started testing")
    assert h.status == HypothesisStatus.TESTING
    assert len(h.history) == 2

def test_hypothesis_is_falsifiable():
    h = Hypothesis("HYP-000001", "Test", tests=["T1", "T2"], falsification_criteria="If X fails")
    assert h.is_falsifiable() is True

def test_hypothesis_not_falsifiable():
    h = Hypothesis("HYP-000001", "Test")
    assert h.is_falsifiable() is False

def test_hypothesis_add_prediction():
    h = Hypothesis("HYP-000001", "Test")
    h.add_prediction("P1", "Expected outcome 1")
    assert len(h.predictions) == 1
    assert h.predictions[0].description == "P1"

def test_hypothesis_add_test():
    h = Hypothesis("HYP-000001", "Test")
    h.add_test("T1")
    assert "T1" in h.tests

def test_hypothesis_to_dict():
    h = Hypothesis("HYP-000001", "Test", confidence=0.8)
    d = h.to_dict()
    assert d["id"] == "HYP-000001"
    assert d["confidence"] == 0.8
    assert d["status"] == "PROPOSED"
    assert d["is_falsifiable"] is False

def test_hypothesis_engine_create():
    eng = HypothesisEngine()
    h = eng.create("Test hypothesis", tests=["T1"], falsification_criteria="If X")
    assert h.id == "HYP-000001"
    assert len(eng.hypotheses) == 1

def test_hypothesis_engine_get_by_id():
    eng = HypothesisEngine()
    eng.create("Test")
    h = eng.get_by_id("HYP-000001")
    assert h is not None
    assert h.statement == "Test"

def test_hypothesis_engine_get_by_status():
    eng = HypothesisEngine()
    eng.create("H1")
    h2 = eng.create("H2")
    h2.set_status(HypothesisStatus.REFUTED)
    proposed = eng.get_by_status(HypothesisStatus.PROPOSED)
    assert len(proposed) == 1

def test_hypothesis_engine_summary():
    eng = HypothesisEngine()
    eng.create("H1", tests=["T1"], falsification_criteria="C1")
    eng.create("H2")
    summary = eng.get_summary()
    assert summary["total"] == 2
    assert summary["falsifiable"] == 1
