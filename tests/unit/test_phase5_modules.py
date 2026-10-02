# tests/unit/test_phase5_modules.py
from src.experiment import ExperimentManager, Experiment, ExperimentStatus
from src.scheduler import ComputeScheduler, Job, JobStatus, JobPriority
from src.failure import FailureRecovery, FailureType
from src.observation import ObservationSystem

def test_experiment_manager_full_lifecycle():
    mgr = ExperimentManager()
    exp = mgr.create("Q?", hypothesis="H1", inputs={"x": 1})
    exp.mark_running()
    exp.mark_completed()
    assert exp.status == ExperimentStatus.COMPLETED
    assert mgr.count() == 1

def test_experiment_clone_keeps_original():
    mgr = ExperimentManager()
    orig = mgr.create("Original Q", inputs={"a": 1})
    clone = mgr.clone(orig.id)
    assert orig.id != clone.id
    assert orig.question == "Original Q"
    assert clone.question != orig.question

def test_scheduler_run_job():
    sched = ComputeScheduler()
    job = sched.submit("Test", func=lambda: 1+1)
    sched.run_next()
    assert job.status == JobStatus.COMPLETED
    assert job.result == 2

def test_scheduler_dependencies():
    sched = ComputeScheduler()
    j1 = sched.submit("First")
    j2 = sched.submit("Second", dependencies=[j1.id])
    sched.run_next()  # j1
    sched.run_next()  # j2 (dep now met)
    assert j1.status == JobStatus.COMPLETED
    assert j2.status == JobStatus.COMPLETED

def test_failure_capture():
    rec = FailureRecovery()
    f = rec.capture("EXP-000001", ValueError("test"), FailureType.VALIDATION_ERROR)
    assert f is not None
    assert "test" in f.error_message

def test_failure_safe_retry_success():
    rec = FailureRecovery()
    ok, result, fail = rec.safe_retry("EXP-000001", lambda: "ok", max_retries=1)
    assert ok is True
    assert result == "ok"

def test_failure_safe_retry_failure():
    rec = FailureRecovery()
    ok, result, fail = rec.safe_retry(
        "EXP-000001", lambda: 1/0, max_retries=1
    )
    assert ok is False
    assert fail is not None

def test_observation_system_integration():
    obs = ObservationSystem()
    obs.snapshot_system(agent="test")
    obs.log_action("agent", "action", target="exp-1")
    summary = obs.get_summary()
    assert summary["total_actions"] >= 1

def test_scheduler_cancel():
    sched = ComputeScheduler()
    job = sched.submit("Cancel me")
    assert sched.cancel(job.id) is True
    assert job.status == JobStatus.CANCELLED

def test_experiment_compare():
    mgr = ExperimentManager()
    e1 = mgr.create("Q1", hypothesis="H1")
    e2 = mgr.create("Q2", hypothesis="H2")
    result = mgr.compare(e1.id, e2.id)
    assert result["same"] is False
    assert "hypothesis" in result["differences"]

def test_experiment_merge():
    mgr = ExperimentManager()
    e1 = mgr.create("Q1", inputs={"a": 1})
    e2 = mgr.create("Q2", inputs={"b": 2})
    merged = mgr.merge(e1.id, e2.id)
    assert merged.inputs == {"a": 1, "b": 2}
