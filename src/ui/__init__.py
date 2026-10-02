"""Visual Lab UI Components.

Dark background theme, subtle scientific grid, neon laboratory accents,
molecular visualizations, professional scientific dashboard.
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

import plotly.graph_objects as go
import plotly.express as px


THEME = {
    "background": "#0a0e17",
    "surface": "#111827",
    "grid": "#1f2937",
    "accent_neon": "#00ff9d",
    "accent_cyan": "#00d4ff",
    "accent_purple": "#a855f7",
    "accent_orange": "#f97316",
    "accent_red": "#ef4444",
    "text_primary": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "font": "JetBrains Mono, monospace",
}


class MolecularVisualization:
    def __init__(self, molecule_id: str, structure_data: Dict[str, Any] = None):
        self.molecule_id = molecule_id
        self.structure_data = structure_data or {}
        self.created_at = datetime.utcnow().isoformat()

    def to_2d_plotly(self) -> Dict[str, Any]:
        """Generate 2D molecular visualization config."""
        return {
            "type": "molecule_2d",
            "molecule_id": self.molecule_id,
            "colorscale": [
                [0, THEME["accent_neon"]],
                [1, THEME["accent_cyan"]],
            ],
            "show_legend": False,
            "dark_theme": True,
        }

    def to_3d_plotly(self) -> Dict[str, Any]:
        """Generate 3D molecular visualization config."""
        return {
            "type": "molecule_3d",
            "molecule_id": self.molecule_id,
            "colorscale": "Viridis",
            "dark_theme": True,
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "molecule_id": self.molecule_id,
            "structure_data": self.structure_data,
            "created_at": self.created_at,
            "viz_2d": self.to_2d_plotly(),
            "viz_3d": self.to_3d_plotly(),
        }


class VisualizationFactory:
    """Creates visualizations for various data types."""

    @staticmethod
    def evidence_distribution(evidence_counts: Dict[str, int]) -> Dict[str, Any]:
        """Create evidence distribution chart config."""
        levels = list(evidence_counts.keys())
        counts = list(evidence_counts.values())
        return {
            "type": "bar",
            "labels": levels,
            "values": counts,
            "title": "Evidence Distribution (E0-E6)",
            "dark_theme": True,
            "colors": [THEME["accent_neon"], THEME["accent_cyan"], THEME["accent_purple"],
                        THEME["accent_orange"], THEME["accent_red"], "#22d3ee", "#a3e635"],
        }

    @staticmethod
    def compute_usage(cpu_percent: float, ram_used_gb: float, ram_total_gb: float) -> Dict[str, Any]:
        """Create compute usage gauge config."""
        return {
            "type": "gauge",
            "cpu_percent": cpu_percent,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
            "ram_percent": round(ram_used_gb / ram_total_gb * 100, 1) if ram_total_gb > 0 else 0,
            "dark_theme": True,
        }

    @staticmethod
    def timeline(events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create timeline visualization."""
        return {
            "type": "timeline",
            "events": events,
            "dark_theme": True,
        }

    @staticmethod
    def hypothesis_status(hypotheses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create hypothesis status donut chart config."""
        status_counts: Dict[str, int] = {}
        for h in hypotheses:
            status = h.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
        return {
            "type": "donut",
            "labels": list(status_counts.keys()),
            "values": list(status_counts.values()),
            "title": "Hypothesis Status",
            "dark_theme": True,
        }


class DashboardWidget:
    def __init__(self, widget_id: str, widget_type: str, config: Dict[str, Any] = None):
        self.widget_id = widget_id
        self.widget_type = widget_type
        self.config = config or {}
        self.visible = True
        self.created_at = datetime.utcnow().isoformat()

    def hide(self) -> None:
        self.visible = False

    def show(self) -> None:
        self.visible = True

    def update_config(self, new_config: Dict[str, Any]) -> None:
        self.config.update(new_config)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "widget_id": self.widget_id,
            "widget_type": self.widget_type,
            "config": self.config,
            "visible": self.visible,
            "created_at": self.created_at,
        }


class DarkTheme:
    """Dark scientific theme constants and helpers."""

    @staticmethod
    def colors() -> Dict[str, str]:
        return THEME.copy()

    @staticmethod
    def figure_kwargs() -> Dict[str, Any]:
        return {
            "paper_bgcolor": THEME["background"],
            "plot_bgcolor": THEME["surface"],
            "font": {"color": THEME["text_primary"], "family": THEME["font"]},
        }

    @staticmethod
    def apply_to_figure(fig: Any) -> Any:
        """Apply dark theme to a plotly figure."""
        if fig is not None:
            fig.update_layout(**DarkTheme.figure_kwargs())
        return fig


__all__ = [
    "THEME",
    "MolecularVisualization",
    "VisualizationFactory",
    "DashboardWidget",
    "DarkTheme",
]
