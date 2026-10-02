"""Navigation System.

16 nav sections with active state management and breadcrumb navigation.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

NAV_SECTIONS = [
    "Dashboard",
    "Plants",
    "Compounds",
    "Molecules",
    "Virtual Mixer",
    "Reactions",
    "Targets",
    "Docking",
    "Molecular Dynamics",
    "Quantum",
    "Literature",
    "Experiments",
    "Hypotheses",
    "Knowledge Graph",
    "Novelty",
    "Statistics",
    "Research Swarm",
    "Reports",
    "Settings",
]


class NavItem:
    def __init__(self, label: str, section: str, icon: str = "", route: str = ""):
        self.label = label
        self.section = section
        self.icon = icon
        self.route = route
        self.active = False

    def activate(self) -> None:
        self.active = True

    def deactivate(self) -> None:
        self.active = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "section": self.section,
            "icon": self.icon,
            "route": self.route,
            "active": self.active,
        }


class Breadcrumb:
    def __init__(self, label: str, route: str = ""):
        self.label = label
        self.route = route
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {"label": self.label, "route": self.route, "timestamp": self.timestamp}


class Navigation:
    """Navigation system with active state and breadcrumbs."""

    def __init__(self):
        self.items: Dict[str, NavItem] = {}
        self.breadcrumbs: List[Breadcrumb] = []
        self.current_section: Optional[str] = None
        self._init_sections()

    def _init_sections(self) -> None:
        for i, section in enumerate(NAV_SECTIONS):
            self.items[section] = NavItem(
                label=section,
                section=section,
                icon=f"icon_{i}",
                route=f"/{section.lower().replace(' ', '-')}",
            )

    def navigate(self, section: str, breadcrumb_labels: List[str] = None) -> bool:
        if section not in self.items:
            return False

        for item in self.items.values():
            item.deactivate()
        self.items[section].activate()
        self.current_section = section

        if breadcrumb_labels:
            self.breadcrumbs = [
                Breadcrumb(label, route=f"/{label.lower().replace(' ', '-')}")
                for label in breadcrumb_labels
            ]
        else:
            self.breadcrumbs = [Breadcrumb(section)]

        return True

    def get_current(self) -> Optional[NavItem]:
        if self.current_section:
            return self.items.get(self.current_section)
        return None

    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        return [b.to_dict() for b in self.breadcrumbs]

    def get_all_sections(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self.items.values()]

    def get_active_section(self) -> Optional[str]:
        return self.current_section

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_section": self.current_section,
            "sections": self.get_all_sections(),
            "breadcrumbs": self.get_breadcrumbs(),
            "total_sections": len(self.items),
        }


def get_nav_sections() -> List[str]:
    """Return all 16+ nav section names."""
    return NAV_SECTIONS.copy()


__all__ = [
    "NAV_SECTIONS",
    "NavItem",
    "Breadcrumb",
    "Navigation",
    "get_nav_sections",
]
