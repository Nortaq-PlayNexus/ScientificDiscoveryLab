"""Compute Scheduler.

Job queue with priorities, resource estimation, status tracking,
parallel execution, and dependency management.
"""

import heapq
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Set

from src.utils.id_gen import generate_stable_id, timestamp_now


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"


class JobPriority(int, Enum):
    LOW = 10
    NORMAL = 20
    HIGH = 30
    CRITICAL = 40


class Job:
    def __init__(
        self,
        job_id: str,
        name: str,
        func: Callable = None,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        priority: JobPriority = JobPriority.NORMAL,
        estimated_compute: str = "unknown",
        estimated_ram_gb: float = 1.0,
        estimated_gpu: bool = False,
        estimated_cpu_cores: int = 1,
        dependencies: List[str] = None,
        max_retries: int = 0,
        retry_count: int = 0,
    ):
        self.id = job_id
        self.name = name
        self.func = func
        self.args = args or []
        self.kwargs = kwargs or {}
        self.priority = priority
        self.estimated_compute = estimated_compute
        self.estimated_ram_gb = estimated_ram_gb
        self.estimated_gpu = estimated_gpu
        self.estimated_cpu_cores = estimated_cpu_cores
        self.dependencies = dependencies or []
        self.max_retries = max_retries
        self.retry_count = retry_count
        self.status = JobStatus.QUEUED
        self.result = None
        self.error = None
        self.created_at = timestamp_now()
        self.started_at = None
        self.completed_at = None
        self.lock = threading.Lock()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority.name,
            "status": self.status.value,
            "estimated_compute": self.estimated_compute,
            "estimated_ram_gb": self.estimated_ram_gb,
            "estimated_gpu": self.estimated_gpu,
            "estimated_cpu_cores": self.estimated_cpu_cores,
            "dependencies": self.dependencies,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class ComputeScheduler:
    """Job queue with priorities and dependency tracking."""

    def __init__(self, max_workers: int = 1):
        self.jobs: Dict[str, Job] = {}
        self.queue: List[tuple] = []  # (priority, counter, job_id)
        self._counter = 0
        self._lock = threading.Lock()
        self._max_workers = max_workers
        self._running: Dict[str, Job] = {}
        self._completed: List[str] = []
        self._action_log: List[Dict[str, str]] = []

    def submit(
        self,
        name: str,
        func: Callable = None,
        priority: JobPriority = JobPriority.NORMAL,
        estimated_compute: str = "unknown",
        estimated_ram_gb: float = 1.0,
        estimated_gpu: bool = False,
        estimated_cpu_cores: int = 1,
        dependencies: List[str] = None,
        max_retries: int = 0,
    ) -> Job:
        self._counter += 1
        job_id = generate_stable_id("JOB", self._counter)
        job = Job(
            job_id=job_id,
            name=name,
            func=func,
            priority=priority,
            estimated_compute=estimated_compute,
            estimated_ram_gb=estimated_ram_gb,
            estimated_gpu=estimated_gpu,
            estimated_cpu_cores=estimated_cpu_cores,
            dependencies=dependencies or [],
            max_retries=max_retries,
        )
        self.jobs[job_id] = job
        with self._lock:
            heapq.heappush(self.queue, (-priority.value, self._counter, job_id))
        self._log_action("SUBMIT", job_id, name)
        return job

    def _log_action(self, action: str, job_id: str, detail: str = "") -> None:
        self._action_log.append({
            "timestamp": timestamp_now(),
            "action": action,
            "job_id": job_id,
            "detail": detail,
        })

    def get(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    def count(self) -> int:
        return len(self.jobs)

    def pending_count(self) -> int:
        return len(self.queue)

    def get_by_status(self, status: str) -> List[Job]:
        return [j for j in self.jobs.values() if j.status.value == status]

    def get_dependencies(self, job_id: str) -> List[str]:
        job = self.jobs.get(job_id)
        if job is None:
            return []
        return job.dependencies

    def can_run(self, job_id: str) -> bool:
        """Check if all dependencies are completed."""
        job = self.jobs.get(job_id)
        if job is None:
            return False
        for dep_id in job.dependencies:
            dep = self.jobs.get(dep_id)
            if dep is None or dep.status != JobStatus.COMPLETED:
                return False
        return True

    def run_next(self) -> Optional[Job]:
        """Run the highest priority job that has its dependencies met."""
        with self._lock:
            while self.queue:
                neg_priority, _, job_id = heapq.heappop(self.queue)
                job = self.jobs.get(job_id)
                if job is None:
                    continue
                if job.status != JobStatus.QUEUED:
                    continue
                if not self.can_run(job_id):
                    continue
                break
            else:
                return None

            job.status = JobStatus.RUNNING
            job.started_at = timestamp_now()
            self._running[job_id] = job
            self._log_action("START", job_id, job.name)

        try:
            if job.func:
                result = job.func(*job.args, **job.kwargs)
            else:
                result = {"status": "completed", "job_id": job_id}
            job.result = result
            job.status = JobStatus.COMPLETED
            job.completed_at = timestamp_now()
            self._completed.append(job_id)
            self._log_action("COMPLETE", job_id, f"result={type(result).__name__}")
        except Exception as e:
            job.error = str(e)
            if job.retry_count < job.max_retries:
                job.retry_count += 1
                job.status = JobStatus.RETRYING
                self._log_action("RETRY", job_id, f"attempt {job.retry_count}")
                with self._lock:
                    heapq.heappush(self.queue, (-job.priority.value, self._counter, job_id))
            else:
                job.status = JobStatus.FAILED
                self._log_action("FAIL", job_id, str(e))
        finally:
            with self._lock:
                if job_id in self._running:
                    del self._running[job_id]

        return job

    def run_all(self, max_jobs: int = None) -> List[Job]:
        """Run all jobs in priority order."""
        results = []
        count = 0
        max_jobs = max_jobs or self.pending_count()
        while count < max_jobs:
            job = self.run_next()
            if job is None:
                break
            results.append(job)
            count += 1
        return results

    def cancel(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if job is None or job.status in (JobStatus.RUNNING, JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            return False
        job.status = JobStatus.CANCELLED
        self._log_action("CANCEL", job_id, job.name)
        return True

    def estimate_resources(self) -> Dict[str, Any]:
        """Estimate total resources for queued jobs."""
        total_ram = 0.0
        total_cpu = 0
        gpu_count = 0
        queued = 0
        for job in self.jobs.values():
            if job.status == JobStatus.QUEUED:
                total_ram += job.estimated_ram_gb
                total_cpu += job.estimated_cpu_cores
                if job.estimated_gpu:
                    gpu_count += 1
                queued += 1
        return {
            "queued_jobs": queued,
            "total_ram_gb": round(total_ram, 2),
            "total_cpu_cores": total_cpu,
            "gpu_jobs": gpu_count,
        }

    def get_action_log(self) -> List[Dict[str, str]]:
        return self._action_log.copy()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_jobs": len(self.jobs),
            "by_status": {s.value: [j.id for j in self.get_by_status(s.value)] for s in JobStatus},
            "resource_estimate": self.estimate_resources(),
            "action_log_length": len(self._action_log),
        }


__all__ = [
    "JobStatus",
    "JobPriority",
    "Job",
    "ComputeScheduler",
]
