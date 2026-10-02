"""Observation System / Monitors.

System Monitor, Simulation Monitor, Agent Monitor,
Database Monitor, Compute Monitor, Error Monitor,
Action trace logging (timestamped, agent-attributed).
"""

import psutil
import threading
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

from src.utils.id_gen import timestamp_now


class MonitorType(str, Enum):
    SYSTEM = "system"
    SIMULATION = "simulation"
    AGENT = "agent"
    DATABASE = "database"
    COMPUTE = "compute"
    ERROR = "error"
    ACTION = "action"


class MonitorEntry:
    def __init__(
        self,
        monitor_type: str,
        entity_id: str,
        metric: str,
        value: Any,
        unit: str = "",
        timestamp: str = None,
        agent: str = "",
    ):
        self.monitor_type = monitor_type
        self.entity_id = entity_id
        self.metric = metric
        self.value = value
        self.unit = unit
        self.timestamp = timestamp or timestamp_now()
        self.agent = agent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.monitor_type,
            "entity_id": self.entity_id,
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
            "agent": self.agent,
        }


class SystemMonitor:
    """Monitors system resources (CPU, RAM, disk)."""

    def __init__(self):
        self.entries: List[MonitorEntry] = []

    def snapshot(self, agent: str = "") -> Dict[str, Any]:
        """Take a system resource snapshot."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        snapshot = {
            "cpu_percent": cpu_percent,
            "ram_total_gb": round(ram.total / (1024**3), 2),
            "ram_used_gb": round(ram.used / (1024**3), 2),
            "ram_available_gb": round(ram.available / (1024**3), 2),
            "ram_percent": ram.percent,
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_percent": disk.percent,
            "timestamp": timestamp_now(),
        }

        entry = MonitorEntry(
            monitor_type=MonitorType.SYSTEM.value,
            entity_id="SYSTEM",
            metric="snapshot",
            value=snapshot,
            agent=agent,
        )
        self.entries.append(entry)
        return snapshot


class SimulationMonitor:
    """Monitors simulation progress and metrics."""

    def __init__(self):
        self.entries: List[MonitorEntry] = []
        self._current_sim: Optional[str] = None

    def start_simulation(self, sim_id: str, agent: str = "") -> None:
        entry = MonitorEntry(
            monitor_type=MonitorType.SIMULATION.value,
            entity_id=sim_id,
            metric="START",
            value="Simulation started",
            agent=agent,
        )
        self.entries.append(entry)
        self._current_sim = sim_id

    def update_step(self, sim_id: str, step: int, total_steps: int, agent: str = "") -> None:
        progress = (step / total_steps * 100) if total_steps > 0 else 0
        entry = MonitorEntry(
            monitor_type=MonitorType.SIMULATION.value,
            entity_id=sim_id,
            metric="STEP",
            value={"step": step, "total": total_steps, "progress_percent": round(progress, 1)},
            agent=agent,
        )
        self.entries.append(entry)

    def complete_simulation(self, sim_id: str, agent: str = "") -> None:
        entry = MonitorEntry(
            monitor_type=MonitorType.SIMULATION.value,
            entity_id=sim_id,
            metric="COMPLETE",
            value="Simulation completed",
            agent=agent,
        )
        self.entries.append(entry)


class AgentMonitor:
    """Monitors agent activity."""

    def __init__(self):
        self.entries: List[MonitorEntry] = []

    def record_action(self, agent_name: str, action: str, detail: str = "", result: str = "") -> None:
        entry = MonitorEntry(
            monitor_type=MonitorType.AGENT.value,
            entity_id=agent_name,
            metric=action,
            value={"detail": detail, "result": result},
            agent=agent_name,
        )
        self.entries.append(entry)

    def get_agent_actions(self, agent_name: str) -> List[MonitorEntry]:
        return [e for e in self.entries if e.entity_id == agent_name]


class DatabaseMonitor:
    """Monitors database operations."""

    def __init__(self):
        self.entries: List[MonitorEntry] = []
        self._query_count = 0

    def record_query(self, query_type: str, table: str, rows_affected: int = 0, agent: str = "", duration_ms: float = 0.0) -> None:
        self._query_count += 1
        entry = MonitorEntry(
            monitor_type=MonitorType.DATABASE.value,
            entity_id=f"{table}:{self._query_count}",
            metric=query_type,
            value={"rows": rows_affected, "duration_ms": duration_ms},
            agent=agent,
        )
        self.entries.append(entry)

    def get_query_count(self) -> int:
        return self._query_count


class ComputeMonitor:
    """Monitors compute resources and job execution."""

    def __init__(self):
        self.entries: List[MonitorEntry] = []
        self._job_count = 0

    def record_job(self, job_id: str, status: str, compute_gb: float = 0.0, cpu_cores: int = 1, agent: str = "") -> None:
        self._job_count += 1
        entry = MonitorEntry(
            monitor_type=MonitorType.COMPUTE.value,
            entity_id=job_id,
            metric=status,
            value={"compute_gb": compute_gb, "cpu_cores": cpu_cores},
            agent=agent,
        )
        self.entries.append(entry)


class ErrorMonitor:
    """Monitors errors and exceptions."""

    def __init__(self):
        self.entries: List[MonitorEntry] = []
        self._error_count = 0

    def record_error(self, error_type: str, message: str, entity_id: str = "UNKNOWN", agent: str = "", severity: str = "medium") -> None:
        self._error_count += 1
        entry = MonitorEntry(
            monitor_type=MonitorType.ERROR.value,
            entity_id=entity_id,
            metric=f"{severity}:{error_type}",
            value={"message": message, "severity": severity},
            agent=agent,
        )
        self.entries.append(entry)

    def get_error_count(self) -> int:
        return self._error_count

    def get_errors_by_severity(self, severity: str) -> List[MonitorEntry]:
        return [e for e in self.entries if severity in e.metric]


class ObservationSystem:
    """Central observation system aggregating all monitors."""

    def __init__(self):
        self.system = SystemMonitor()
        self.simulation = SimulationMonitor()
        self.agent = AgentMonitor()
        self.database = DatabaseMonitor()
        self.compute = ComputeMonitor()
        self.errors = ErrorMonitor()
        self.action_log: List[Dict[str, Any]] = []

    def log_action(
        self,
        agent: str,
        action: str,
        target: str = "",
        details: Dict[str, Any] = None,
    ) -> None:
        entry = {
            "timestamp": timestamp_now(),
            "agent": agent,
            "action": action,
            "target": target,
            "details": details or {},
        }
        self.action_log.append(entry)
        self.agent.record_action(agent, action, detail=target, result="ok")

    def snapshot_system(self, agent: str = "") -> Dict[str, Any]:
        return self.system.snapshot(agent=agent)

    def start_simulation(self, sim_id: str, agent: str = "") -> None:
        self.simulation.start_simulation(sim_id, agent=agent)
        self.log_action(agent, "START_SIMULATION", target=sim_id)

    def complete_simulation(self, sim_id: str, agent: str = "") -> None:
        self.simulation.complete_simulation(sim_id, agent=agent)
        self.log_action(agent, "COMPLETE_SIMULATION", target=sim_id)

    def get_all_entries(self) -> Dict[str, List[MonitorEntry]]:
        return {
            "system": self.system.entries,
            "simulation": self.simulation.entries,
            "agent": self.agent.entries,
            "database": self.database.entries,
            "compute": self.compute.entries,
            "error": self.errors.entries,
        }

    def get_action_log(self) -> List[Dict[str, Any]]:
        return self.action_log.copy()

    def get_summary(self) -> Dict[str, Any]:
        return {
            "system_snapshots": len(self.system.entries),
            "simulation_entries": len(self.simulation.entries),
            "agent_actions": len(self.agent.entries),
            "database_queries": self.database.get_query_count(),
            "compute_jobs": self.compute._job_count,
            "errors": self.errors.get_error_count(),
            "total_actions": len(self.action_log),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.get_summary(),
            "entries": {k: [e.to_dict() for e in v] for k, v in self.get_all_entries().items()},
            "action_log": self.get_action_log(),
        }


__all__ = [
    "MonitorType",
    "MonitorEntry",
    "SystemMonitor",
    "SimulationMonitor",
    "AgentMonitor",
    "DatabaseMonitor",
    "ComputeMonitor",
    "ErrorMonitor",
    "ObservationSystem",
]
