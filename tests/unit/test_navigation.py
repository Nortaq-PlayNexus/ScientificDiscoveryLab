# tests/unit/test_navigation.py
from src.navigation import (
    Navigation, NavItem, Breadcrumb, get_nav_sections, NAV_SECTIONS,
)

def test_nav_sections():
    sections = get_nav_sections()
    assert len(sections) == 19  # All sections including Research Swarm, Reports, Settings

def test_navigation_init():
    nav = Navigation()
    assert nav.current_section is None
    assert len(nav.items) == 19

def test_navigation_navigate():
    nav = Navigation()
    result = nav.navigate("Dashboard")
    assert result is True
    assert nav.current_section == "Dashboard"
    current = nav.get_current()
    assert current is not None
    assert current.label == "Dashboard"
    assert current.active is True

def test_navigation_navigate_invalid():
    nav = Navigation()
    result = nav.navigate("Nonexistent")
    assert result is False

def test_navigation_breadcrumbs():
    nav = Navigation()
    nav.navigate("Molecules", breadcrumb_labels=["Dashboard", "Compounds", "Molecules"])
    crumbs = nav.get_breadcrumbs()
    assert len(crumbs) == 3
    assert crumbs[0]["label"] == "Dashboard"
    assert crumbs[2]["label"] == "Molecules"

def test_navigation_switch_section():
    nav = Navigation()
    nav.navigate("Dashboard")
    nav.navigate("Hypotheses")
    assert nav.current_section == "Hypotheses"
    dashboard = nav.items.get("Dashboard")
    assert dashboard.active is False
    hypotheses = nav.items.get("Hypotheses")
    assert hypotheses.active is True

def test_navigation_get_all_sections():
    nav = Navigation()
    sections = nav.get_all_sections()
    assert len(sections) == 19
    assert all("label" in s for s in sections)
    assert all("active" in s for s in sections)

def test_navigation_to_dict():
    nav = Navigation()
    nav.navigate("Dashboard")
    d = nav.to_dict()
    assert d["current_section"] == "Dashboard"
    assert d["total_sections"] == 19
    assert len(d["breadcrumbs"]) >= 1

def test_nav_item_activation():
    item = NavItem("Test", "section", icon="icon_test")
    assert item.active is False
    item.activate()
    assert item.active is True
    item.deactivate()
    assert item.active is False

def test_breadcrumb_to_dict():
    b = Breadcrumb("Test", route="/test")
    d = b.to_dict()
    assert d["label"] == "Test"
    assert d["route"] == "/test"
    assert "timestamp" in d
