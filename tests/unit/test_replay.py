# tests/unit/test_replay.py
from src.replay import ReplayEngine, ReplayResult, ExperimentManager, Experiment, ExperimentStatus

def test_reproduce_exact():
    mgr = ExperimentManager()
    exp = mgr.create("Q?", hypothesis="H1", inputs={"a": 1}, parameters={"b": 2})

    engine = ReplayEngine(mgr)
    result = engine.reproduce(exp.id)

    assert result.status == "REPRODUCED"
    assert result.match_score == 1.0
    assert result.differences == []

def test_reproduce_with_diff():
    mgr = ExperimentManager()
    exp = mgr.create("Q?", hypothesis="H1", inputs={"a": 1})

    engine = ReplayEngine(mgr)
    result = engine.reproduce(exp.id, inputs={"a": 99})

    assert result.status == "PARTIALLY_REPRODUCED"
    assert result.match_score < 1.0
    assert len(result.differences) > 0

def test_reproduce_many_diffs():
    mgr = ExperimentManager()
    exp = mgr.create("Q?", hypothesis="H1")

    engine = ReplayEngine(mgr)
    result = engine.reproduce(exp.id, inputs={"x": 1}, parameters={"y": 2})

    assert result.status in ("PARTIALLY_REPRODUCED", "FAILED_REPRODUCTION")

def test_reproduce_experiment_not_found():
    engine = ReplayEngine()
    try:
        engine.reproduce("EXP-999999")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

def test_replay_to_dict():
    mgr = ExperimentManager()
    exp = mgr.create("Q?")
    engine = ReplayEngine(mgr)
    result = engine.reproduce(exp.id)
    d = result.to_dict()
    assert d["replay_id"] == "RPL-000001"
    assert d["experiment_id"] == exp.id
    assert d["status"] == "REPRODUCED"

def test_replay_get_by_id():
    mgr = ExperimentManager()
    exp = mgr.create("Q?")
    engine = ReplayEngine(mgr)
    result = engine.reproduce(exp.id)
    retrieved = engine.get_replay(result.replay_id)
    assert retrieved is not None
    assert retrieved.replay_id == result.replay_id

def test_replay_get_by_experiment():
    mgr = ExperimentManager()
    exp = mgr.create("Q?")
    engine = ReplayEngine(mgr)
    engine.reproduce(exp.id)
    engine.reproduce(exp.id)
    replays = engine.get_by_experiment(exp.id)
    assert len(replays) == 2

def test_replay_count():
    mgr = ExperimentManager()
    exp = mgr.create("Q?")
    engine = ReplayEngine(mgr)
    assert engine.count() == 0
    engine.reproduce(exp.id)
    assert engine.count() == 1

def test_replay_different_inputs():
    """Different inputs produce different replay results."""
    mgr = ExperimentManager()
    exp = mgr.create("Q?", inputs={"a": 1})
    engine = ReplayEngine(mgr)
    r1 = engine.reproduce(exp.id, inputs={"a": 1})
    r2 = engine.reproduce(exp.id, inputs={"a": 2})
    assert r1.status == "REPRODUCED"
    assert r2.status != "REPRODUCED"
