# tests/unit/test_ui.py
from src.ui import (
    THEME, MolecularVisualization, VisualizationFactory,
    DashboardWidget, DarkTheme,
)

def test_theme_has_keys():
    assert "background" in THEME
    assert "accent_neon" in THEME
    assert THEME["background"] == "#0a0e17"

def test_molecular_viz_2d():
    viz = MolecularVisualization("MOL-000001")
    d = viz.to_2d_plotly()
    assert d["type"] == "molecule_2d"
    assert d["dark_theme"] is True

def test_molecular_viz_3d():
    viz = MolecularVisualization("MOL-000001")
    d = viz.to_3d_plotly()
    assert d["type"] == "molecule_3d"

def test_molecular_viz_to_dict():
    viz = MolecularVisualization("MOL-000001", structure_data={"atoms": 5})
    d = viz.to_dict()
    assert d["molecule_id"] == "MOL-000001"

def test_evidence_distribution():
    chart = VisualizationFactory.evidence_distribution({"E0": 3, "E3": 5})
    assert chart["type"] == "bar"
    assert chart["labels"] == ["E0", "E3"]

def test_compute_usage():
    gauge = VisualizationFactory.compute_usage(50.0, 8.0, 16.0)
    assert gauge["cpu_percent"] == 50.0
    assert gauge["ram_percent"] == 50.0

def test_dashboard_widget():
    w = DashboardWidget("W1", "chart", {"data": [1,2,3]})
    d = w.to_dict()
    assert d["widget_id"] == "W1"
    w.hide()
    assert w.visible is False
    w.show()
    assert w.visible is True

def test_dark_theme():
    kwargs = DarkTheme.figure_kwargs()
    assert "paper_bgcolor" in kwargs
    assert kwargs["paper_bgcolor"] == THEME["background"]
