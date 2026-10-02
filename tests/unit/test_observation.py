# tests/unit/test_observation.py
from src.observation import (
    ObservationSystem, SystemMonitor, SimulationMonitor, AgentMonitor,
    DatabaseMonitor, ComputeMonitor, ErrorMonitor, MonitorEntry, MonitorType,
)
import psutil

def test_system_monitor_snapshot():
    mon = SystemMonitor()
    snapshot = mon.snapshot()
    assert "cpu_percent" in snapshot
    assert "ram_total_gb" in snapshot
    assert "disk_percent" in snapshot
    assert len(mon.entries) == 1

def test_simulation_monitor():
    mon = SimulationMonitor()
    mon.start_simulation("SIM-000001")
    mon.update_step("SIM-000001", step=50, total_steps=100)
    mon.complete_simulation("SIM-000001")
    assert len(mon.entries) == 3

def test_agent_monitor():
    mon = AgentMonitor()
    mon.record_action("Researcher", "SEARCH", detail="PubMed", result="3 papers")
    actions = mon.get_agent_actions("Researcher")
    assert len(actions) == 1
    assert actions[0].metric == "SEARCH"

def test_database_monitor():
    mon = DatabaseMonitor()
    mon.record_query("SELECT", "plants", rows_affected=10, duration_ms=5.0)
    assert mon.get_query_count() == 1

def test_compute_monitor():
    mon = ComputeMonitor()
    mon.record_job("JOB-000001", "COMPLETED", compute_gb=2.0, cpu_cores=4)
    assert mon._job_count == 1

def test_error_monitor():
    mon = ErrorMonitor()
    mon.record_error("VALIDATION", "Bad SMILES", entity_id="CMP-000001", severity="high")
    assert mon.get_error_count() == 1
    errors = mon.get_errors_by_severity("high")
    assert len(errors) == 1

def test_observation_system():
    obs = ObservationSystem()
    # System
    snap = obs.snapshot_system(agent="TestAgent")
    assert "cpu_percent" in snap

    # Simulation
    obs.start_simulation("SIM-001", agent="TestAgent")
    obs.complete_simulation("SIM-001", agent="TestAgent")

    # Agent action
    obs.log_action("TestAgent", "CREATE", target="EXP-000001", details={"q": "test"})

    # Error
    obs.errors.record_error("TEST", "Error msg", agent="TestAgent")

    summary = obs.get_summary()
    assert summary["system_snapshots"] == 1
    assert summary["simulation_entries"] == 2
    assert summary["total_actions"] >= 1

def test_observation_system_action_log():
    obs = ObservationSystem()
    obs.log_action("Agent1", "ACTION_A", target="T1")
    obs.log_action("Agent2", "ACTION_B", target="T2")
    log = obs.get_action_log()
    assert len(log) == 2
    assert log[0]["agent"] == "Agent1"
    assert log[1]["agent"] == "Agent2"
    assert "timestamp" in log[0]

def test_observation_system_to_dict():
    obs = ObservationSystem()
    obs.snapshot_system(agent="A")
    obs.log_action("A", "TEST", target="T")
    d = obs.to_dict()
    assert "summary" in d
    assert "entries" in d
    assert "action_log" in d

def test_monitor_entry_to_dict():
    entry = MonitorEntry(
        monitor_type=MonitorType.SYSTEM.value,
        entity_id="SYS",
        metric="cpu",
        value=50.0,
        unit="%",
        agent="TestAgent",
    )
    d = entry.to_dict()
    assert d["metric"] == "cpu"
    assert d["value"] == 50.0
    assert d["agent"] == "TestAgent"

def test_observation_system_summary_keys():
    obs = ObservationSystem()
    summary = obs.get_summary()
    expected_keys = [
        "system_snapshots", "simulation_entries", "agent_actions",
        "database_queries", "compute_jobs", "errors", "total_actions",
    ]
    for key in expected_keys:
        assert key in summary
