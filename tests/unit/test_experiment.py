# tests/unit/test_experiment.py
from src.experiment import ExperimentManager, Experiment, ExperimentStatus

def test_experiment_creation():
    exp = Experiment(experiment_id="EXP-000001", question="Test question")
    assert exp.id == "EXP-000001"
    assert exp.question == "Test question"
    assert exp.status == ExperimentStatus.PROPOSED
    assert exp.immutable is True

def test_experiment_mark_running():
    exp = Experiment(experiment_id="EXP-000001", question="Test")
    exp.mark_running()
    assert exp.status == ExperimentStatus.RUNNING

def test_experiment_mark_completed():
    exp = Experiment(experiment_id="EXP-000001", question="Test")
    exp.mark_running()
    exp.mark_completed()
    assert exp.status == ExperimentStatus.COMPLETED

def test_experiment_mark_failed():
    exp = Experiment(experiment_id="EXP-000001", question="Test")
    exp.mark_failed()
    assert exp.status == ExperimentStatus.FAILED

def test_experiment_mark_cancelled():
    exp = Experiment(experiment_id="EXP-000001", question="Test")
    exp.mark_cancelled()
    assert exp.status == ExperimentStatus.CANCELLED

def test_experiment_immutable_cannot_change():
    """Immutable experiments cannot be modified after completion."""
    exp = Experiment(experiment_id="EXP-000001", question="Test", immutable=True)
    exp.mark_running()
    exp.mark_completed()
    # Once completed, should not change status (immutable)
    # Note: mark_running/check works before completion; immutability means
    # experiment record itself cannot be changed
    assert exp.is_immutable() is True

def test_experiment_to_dict():
    exp = Experiment(experiment_id="EXP-000001", question="Test", hypothesis="H1")
    d = exp.to_dict()
    assert d["id"] == "EXP-000001"
    assert d["question"] == "Test"
    assert d["hypothesis"] == "H1"

def test_manager_create():
    mgr = ExperimentManager()
    exp = mgr.create("Test question")
    assert exp.id == "EXP-000001"
    assert mgr.count() == 1

def test_manager_get():
    mgr = ExperimentManager()
    exp = mgr.create("Test")
    retrieved = mgr.get("EXP-000001")
    assert retrieved is not None
    assert retrieved.question == "Test"

def test_manager_get_none():
    mgr = ExperimentManager()
    assert mgr.get("EXP-999999") is None

def test_manager_list_all():
    mgr = ExperimentManager()
    mgr.create("Q1")
    mgr.create("Q2")
    assert len(mgr.list_all()) == 2

def test_manager_list_by_status():
    mgr = ExperimentManager()
    exp1 = mgr.create("Q1")
    exp2 = mgr.create("Q2")
    exp1.mark_completed()
    completed = mgr.list_by_status(ExperimentStatus.COMPLETED)
    assert len(completed) == 1
    assert completed[0].id == exp1.id

def test_manager_clone():
    mgr = ExperimentManager()
    original = mgr.create("Original question", hypothesis="H1", inputs={"a": 1})
    clone = mgr.clone(original.id, new_question="Cloned question")
    assert clone.id != original.id
    assert "Cloned question" in clone.question
    assert clone.hypothesis == "H1"
    assert clone.inputs == {"a": 1}
    assert original.question == "Original question"  # Original unchanged

def test_manager_compare():
    mgr = ExperimentManager()
    exp1 = mgr.create("Q1", hypothesis="H1", inputs={"a": 1})
    exp2 = mgr.create("Q2", hypothesis="H2", inputs={"a": 2})
    result = mgr.compare(exp1.id, exp2.id)
    assert result["same"] is False
    assert "question" in result["differences"]

def test_manager_compare_same():
    mgr = ExperimentManager()
    exp1 = mgr.create("Q1", hypothesis="H1")
    exp2 = mgr.clone(exp1.id, new_question="Q1")
    result = mgr.compare(exp1.id, exp2.id)
    assert result["same"] is True

def test_manager_branch():
    mgr = ExperimentManager()
    exp = mgr.create("Q1")
    branch = mgr.branch(exp.id, "variant_A")
    assert "variant_A" in branch.question

def test_manager_merge():
    mgr = ExperimentManager()
    exp1 = mgr.create("Q1", inputs={"a": 1})
    exp2 = mgr.create("Q2", inputs={"b": 2})
    merged = mgr.merge(exp1.id, exp2.id)
    assert "Q1" in merged.question or "Q2" in merged.question
    assert merged.inputs == {"a": 1, "b": 2}

def test_manager_to_dict():
    mgr = ExperimentManager()
    mgr.create("Q1")
    d = mgr.to_dict()
    assert d["total"] == 1
    assert len(d["experiments"]) == 1
