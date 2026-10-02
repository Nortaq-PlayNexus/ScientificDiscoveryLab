"""Dashboard System.

Aggregates all dashboard sections into a unified view.
"""

import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.experiment import ExperimentManager
from src.hypothesis import HypothesisEngine
from src.scheduler import ComputeScheduler
from src.observation import ObservationSystem
from src.novelty import NoveltyEngine
from src.ui import VisualizationFactory, DarkTheme, THEME


class DashboardSection:
    def __init__(self, name: str, title: str, data: Dict[str, Any] = None):
        self.name = name
        self.title = title
        self.data = data or {}
        self.last_updated: Optional[str] = None

    def update(self, data: Dict[str, Any]) -> None:
        self.data = data
        self.last_updated = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "title": self.title,
            "data": self.data,
            "last_updated": self.last_updated,
        }


class Dashboard:
    """Scientific lab dashboard aggregating all system data."""

    SECTION_ORDER = [
        "active_experiments",
        "running_simulations",
        "hypotheses",
        "candidate_molecules",
        "potential_reactions",
        "literature_sources",
        "results",
        "evidence_distribution",
        "compute_usage",
    ]

    def __init__(
        self,
        experiment_manager: ExperimentManager = None,
        hypothesis_engine: HypothesisEngine = None,
        scheduler: ComputeScheduler = None,
        observation: ObservationSystem = None,
        novelty_engine: NoveltyEngine = None,
    ):
        self.experiment_manager = experiment_manager or ExperimentManager()
        self.hypothesis_engine = hypothesis_engine or HypothesisEngine()
        self.scheduler = scheduler or ComputeScheduler()
        self.observation = observation or ObservationSystem()
        self.novelty_engine = novelty_engine or NoveltyEngine()
        self.sections: Dict[str, DashboardSection] = {}
        self._build_sections()

    def _build_sections(self) -> None:
        self.sections["active_experiments"] = DashboardSection(
            "active_experiments", "Active Experiments"
        )
        self.sections["running_simulations"] = DashboardSection(
            "running_simulations", "Running Simulations"
        )
        self.sections["hypotheses"] = DashboardSection(
            "hypotheses", "Hypotheses"
        )
        self.sections["candidate_molecules"] = DashboardSection(
            "candidate_molecules", "Candidate Molecules"
        )
        self.sections["potential_reactions"] = DashboardSection(
            "potential_reactions", "Potential Reactions"
        )
        self.sections["literature_sources"] = DashboardSection(
            "literature_sources", "Literature Sources"
        )
        self.sections["results"] = DashboardSection(
            "results", "Reproduced / Refuted Results"
        )
        self.sections["evidence_distribution"] = DashboardSection(
            "evidence_distribution", "Evidence Distribution (E0-E6)"
        )
        self.sections["compute_usage"] = DashboardSection(
            "compute_usage", "Compute Usage"
        )

    def refresh(self) -> Dict[str, Any]:
        """Refresh all dashboard sections with current data."""
        self._refresh_active_experiments()
        self._refresh_running_simulations()
        self._refresh_hypotheses()
        self._refresh_evidence_distribution()
        self._refresh_compute_usage()

        return {section.name: section.to_dict() for section in self.sections.values()}

    def _refresh_active_experiments(self) -> None:
        experiments = self.experiment_manager.list_all()
        active = [e.to_dict() for e in experiments if e.status not in ("COMPLETED", "FAILED", "CANCELLED")]
        self.sections["active_experiments"].update({
            "count": len(active),
            "experiments": active,
        })

    def _refresh_running_simulations(self) -> None:
        running = self.scheduler.get_by_status("RUNNING")
        self.sections["running_simulations"].update({
            "count": len(running),
            "jobs": [j.to_dict() for j in running],
        })

    def _refresh_hypotheses(self) -> None:
        summary = self.hypothesis_engine.get_summary()
        self.sections["hypotheses"].update(summary)

    def _refresh_evidence_distribution(self) -> None:
        evidence_counts = {"E0": 0, "E1": 0, "E2": 0, "E3": 0, "E4": 0, "E5": 0, "E6": 0}
        for exp in self.experiment_manager.list_all():
            for ev in exp.evidence:
                level = ev.get("evidence_level", "E0") if isinstance(ev, dict) else "E0"
                if level in evidence_counts:
                    evidence_counts[level] += 1
        self.sections["evidence_distribution"].update({
            "chart": VisualizationFactory.evidence_distribution(evidence_counts),
            "counts": evidence_counts,
        })

    def _refresh_compute_usage(self) -> None:
        snapshot = self.observation.system.snapshot()
        self.sections["compute_usage"].update({
            "snapshot": snapshot,
            "gauge": VisualizationFactory.compute_usage(
                snapshot["cpu_percent"],
                snapshot["ram_used_gb"],
                snapshot["ram_total_gb"],
            ),
            "scheduler_estimate": self.scheduler.estimate_resources(),
        })

    def get_section(self, name: str) -> Optional[DashboardSection]:
        return self.sections.get(name)

    def get_section_data(self, name: str) -> Dict[str, Any]:
        section = self.sections.get(name)
        return section.data if section else {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sections": {name: s.to_dict() for name, s in self.sections.items()},
            "section_order": self.SECTION_ORDER,
        }

    def widget_count(self) -> int:
        return len(self.sections)


__all__ = [
    "DashboardSection",
    "Dashboard",
]
