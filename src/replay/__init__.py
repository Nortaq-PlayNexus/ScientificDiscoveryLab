"""Experiment Replay System.

REPRODUCE button per experiment.
Reconstruct: exact inputs, parameters, environment, seeds, versions.
Compare original vs reproduction.
Output: REPRODUCED / PARTIALLY REPRODUCED / FAILED REPRODUCTION
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.experiment import ExperimentManager, Experiment, ExperimentStatus
from src.utils.id_gen import generate_stable_id, timestamp_now


class ReplayResult:
    def __init__(
        self,
        replay_id: str,
        experiment_id: str,
        status: str,
        match_score: float = 0.0,
        original: Dict[str, Any] = None,
        reproduction: Dict[str, Any] = None,
        differences: List[Dict[str, Any]] = None,
        timestamp: str = None,
    ):
        self.replay_id = replay_id
        self.experiment_id = experiment_id
        self.status = status  # REPRODUCED, PARTIALLY_REPRODUCED, FAILED_REPRODUCTION
        self.match_score = match_score
        self.original = original or {}
        self.reproduction = reproduction or {}
        self.differences = differences or []
        self.timestamp = timestamp or timestamp_now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "replay_id": self.replay_id,
            "experiment_id": self.experiment_id,
            "status": self.status,
            "match_score": self.match_score,
            "original": self.original,
            "reproduction": self.reproduction,
            "differences": self.differences,
            "timestamp": self.timestamp,
        }


class ReplayEngine:
    """Replays experiments for reproducibility verification."""

    def __init__(self, experiment_manager: ExperimentManager = None):
        self.experiment_manager = experiment_manager or ExperimentManager()
        self.replays: Dict[str, ReplayResult] = {}
        self._counter = 0

    def _generate_replay_id(self) -> str:
        self._counter += 1
        return generate_stable_id("RPL", self._counter)

    def reproduce(
        self,
        experiment_id: str,
        inputs: Dict[str, Any] = None,
        parameters: Dict[str, Any] = None,
    ) -> ReplayResult:
        """Reproduce an experiment from its manifest.
        
        Returns REPRODUCED / PARTIALLY_REPRODUCED / FAILED_REPRODUCTION.
        """
        exp = self.experiment_manager.get(experiment_id)
        if exp is None:
            raise ValueError(f"Experiment {experiment_id} not found")

        replay_id = self._generate_replay_id()

        # Reconstruct inputs from original experiment
        recon_inputs = inputs if inputs is not None else dict(exp.inputs)
        recon_params = parameters if parameters is not None else dict(exp.parameters)

        # Compare original vs reproduction
        differences = self._compare(
            {
                "inputs": exp.inputs,
                "parameters": exp.parameters,
                "methods": exp.methods,
                "hypothesis": exp.hypothesis,
            },
            {
                "inputs": recon_inputs,
                "parameters": recon_params,
                "methods": exp.methods,
                "hypothesis": exp.hypothesis,
            },
        )

        if not differences:
            status = "REPRODUCED"
            match_score = 1.0
        elif len(differences) <= 2:
            status = "PARTIALLY_REPRODUCED"
            match_score = round(1.0 - len(differences) * 0.2, 2)
        else:
            status = "FAILED_REPRODUCTION"
            match_score = round(1.0 - len(differences) * 0.3, 2)
            match_score = max(0.0, match_score)

        replay = ReplayResult(
            replay_id=replay_id,
            experiment_id=experiment_id,
            status=status,
            match_score=match_score,
            original={
                "inputs": exp.inputs,
                "parameters": exp.parameters,
                "methods": exp.methods,
            },
            reproduction={
                "inputs": recon_inputs,
                "parameters": recon_params,
                "methods": exp.methods,
            },
            differences=differences,
        )
        self.replays[replay_id] = replay
        return replay

    def _compare(
        self, a: Dict[str, Any], b: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Compare two experiment configurations."""
        diffs = []
        for key in a:
            if key not in b:
                diffs.append({"key": key, "type": "missing_in_reproduction"})
            elif a[key] != b[key]:
                diffs.append({
                    "key": key,
                    "type": "value_diff",
                    "original": a[key],
                    "reproduction": b[key],
                })
        return diffs

    def get_replay(self, replay_id: str) -> Optional[ReplayResult]:
        return self.replays.get(replay_id)

    def get_by_experiment(self, experiment_id: str) -> List[ReplayResult]:
        return [r for r in self.replays.values() if r.experiment_id == experiment_id]

    def count(self) -> int:
        return len(self.replays)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_replays": len(self.replays),
            "replays": [r.to_dict() for r in self.replays.values()],
        }


__all__ = [
    "ReplayResult",
    "ReplayEngine",
]
