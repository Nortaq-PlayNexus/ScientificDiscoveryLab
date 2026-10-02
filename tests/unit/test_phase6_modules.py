# tests/unit/test_phase6_modules.py
from src.ui import THEME, DarkTheme, MolecularVisualization, VisualizationFactory, DashboardWidget
from src.dashboard import Dashboard
from src.navigation import Navigation, get_nav_sections
from src.replay import ReplayEngine, ReplayResult
from src.experiment import ExperimentManager

def test_dashboard_with_experiment():
    mgr = ExperimentManager()
    mgr.create("Q?", hypothesis="H1")
    dash = Dashboard(experiment_manager=mgr)
    dash.refresh()
    data = dash.get_section_data("active_experiments")
    assert data["count"] == 1

def test_navigation_full_flow():
    nav = Navigation()
    nav.navigate("Dashboard", ["Home", "Dashboard"])
    nav.navigate("Molecules", ["Dashboard", "Compounds", "Molecules"])
    assert nav.current_section == "Molecules"
    crumbs = nav.get_breadcrumbs()
    assert len(crumbs) == 3

def test_replay_integration():
    mgr = ExperimentManager()
    exp = mgr.create("Q?", inputs={"a": 1}, parameters={"b": 2})
    engine = ReplayEngine(mgr)
    result = engine.reproduce(exp.id)
    assert result.status == "REPRODUCED"
    assert result.match_score == 1.0

def test_visualization_factory():
    chart = VisualizationFactory.evidence_distribution({"E0": 1, "E1": 2})
    assert chart["labels"] == ["E0", "E1"]
    gauge = VisualizationFactory.compute_usage(75.0, 12.0, 16.0)
    assert gauge["cpu_percent"] == 75.0

def test_dark_theme_applies():
    kwargs = DarkTheme.figure_kwargs()
    assert kwargs["paper_bgcolor"] == "#0a0e17"
