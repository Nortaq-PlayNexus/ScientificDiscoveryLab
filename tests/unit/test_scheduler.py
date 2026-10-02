# tests/unit/test_scheduler.py
from src.scheduler import ComputeScheduler, Job, JobStatus, JobPriority

def test_job_creation():
    job = Job(job_id="JOB-000001", name="Test job")
    assert job.id == "JOB-000001"
    assert job.name == "Test job"
    assert job.status == JobStatus.QUEUED
    assert job.priority == JobPriority.NORMAL

def test_job_to_dict():
    job = Job(job_id="JOB-000001", name="Test")
    d = job.to_dict()
    assert d["id"] == "JOB-000001"
    assert d["status"] == "QUEUED"

def test_scheduler_submit():
    sched = ComputeScheduler()
    job = sched.submit("Test job")
    assert job.id == "JOB-000001"
    assert sched.count() == 1

def test_scheduler_get():
    sched = ComputeScheduler()
    sched.submit("Test")
    job = sched.get("JOB-000001")
    assert job is not None

def test_scheduler_get_none():
    sched = ComputeScheduler()
    assert sched.get("JOB-999999") is None

def test_scheduler_pending_count():
    sched = ComputeScheduler()
    sched.submit("J1")
    sched.submit("J2")
    assert sched.pending_count() == 2

def test_scheduler_get_by_status():
    sched = ComputeScheduler()
    sched.submit("J1")
    sched.submit("J2")
    queued = sched.get_by_status("QUEUED")
    assert len(queued) == 2

def test_scheduler_run_next():
    sched = ComputeScheduler()
    job = sched.submit("Test job", func=lambda: {"result": 42})
    result_job = sched.run_next()
    assert result_job is not None
    assert result_job.status == JobStatus.COMPLETED
    assert result_job.result == {"result": 42}

def test_scheduler_run_all():
    sched = ComputeScheduler()
    for i in range(3):
        sched.submit(f"Job {i}", func=lambda i=i: {"val": i})
    results = sched.run_all()
    assert len(results) == 3
    assert all(j.status == JobStatus.COMPLETED for j in results)

def test_scheduler_cancel():
    sched = ComputeScheduler()
    job = sched.submit("Test")
    assert sched.cancel(job.id) is True
    assert job.status == JobStatus.CANCELLED

def test_scheduler_cancel_running():
    sched = ComputeScheduler()
    job = sched.submit("Test")
    sched.run_next()  # Start the job
    assert sched.cancel(job.id) is False  # Cannot cancel running

def test_scheduler_dependencies():
    sched = ComputeScheduler()
    j1 = sched.submit("First")
    j2 = sched.submit("Second", dependencies=[j1.id])
    assert sched.can_run(j1.id) is True
    assert sched.can_run(j2.id) is False  # Dependency not met

    sched.run_next()  # Run j1
    assert sched.can_run(j2.id) is True  # Now dependency met

def test_scheduler_priority():
    sched = ComputeScheduler()
    low = sched.submit("Low", priority=JobPriority.LOW)
    high = sched.submit("High", priority=JobPriority.HIGH)
    normal = sched.submit("Normal", priority=JobPriority.NORMAL)

    first = sched.run_next()
    assert first.id == high.id  # Highest priority runs first

def test_scheduler_estimate_resources():
    sched = ComputeScheduler()
    sched.submit("J1", estimated_ram_gb=2.0, estimated_cpu_cores=4, estimated_gpu=True)
    sched.submit("J2", estimated_ram_gb=1.0, estimated_cpu_cores=2)
    estimate = sched.estimate_resources()
    assert estimate["queued_jobs"] == 2
    assert estimate["total_ram_gb"] == 3.0
    assert estimate["total_cpu_cores"] == 6
    assert estimate["gpu_jobs"] == 1

def test_scheduler_job_to_dict():
    job = Job(job_id="JOB-000001", name="Test", priority=JobPriority.HIGH)
    d = job.to_dict()
    assert d["priority"] == "HIGH"

def test_scheduler_run_failing_job():
    sched = ComputeScheduler()
    job = sched.submit("Failing", func=lambda: 1/0)
    result = sched.run_next()
    assert result.status == JobStatus.FAILED
    assert result.error is not None
