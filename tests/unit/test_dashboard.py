# tests/unit/test_dashboard.py
from src.dashboard import Dashboard, DashboardSection
from src.experiment import ExperimentManager, Experiment, ExperimentStatus
from src.hypothesis import HypothesisEngine
from src.scheduler import ComputeScheduler
from src.observation import ObservationSystem

def test_dashboard_creation():
    dash = Dashboard()
    assert dash.widget_count() == 9
    assert "active_experiments" in dash.sections

def test_dashboard_section():
    dash = Dashboard()
    section = dash.get_section("active_experiments")
    assert section is not None
    assert section.title == "Active Experiments"

def test_dashboard_refresh():
    dash = Dashboard()
    result = dash.refresh()
    assert "active_experiments" in result
    assert "compute_usage" in result

def test_dashboard_refresh_empty():
    """Dashboard works with no data."""
    dash = Dashboard()
    dash.refresh()
    exp_section = dash.get_section_data("active_experiments")
    assert exp_section["count"] == 0

def test_dashboard_with_data():
    """Dashboard works with actual data."""
    mgr = ExperimentManager()
    exp = mgr.create("Q?", hypothesis="H1", inputs={"a": 1})
    exp.mark_running()

    dash = Dashboard(experiment_manager=mgr)
    dash.refresh()
    data = dash.get_section_data("active_experiments")
    assert data["count"] == 1

def test_dashboard_to_dict():
    dash = Dashboard()
    d = dash.to_dict()
    assert "sections" in d
    assert "section_order" in d

def test_dashboard_section_data():
    dash = Dashboard()
    data = dash.get_section_data("nonexistent")
    assert data == {}

def test_dashboard_evidence_distribution():
    dash = Dashboard()
    dash.refresh()
    ev_data = dash.get_section_data("evidence_distribution")
    assert "chart" in ev_data
    assert "counts" in ev_data
    assert ev_data["counts"]["E0"] == 0
