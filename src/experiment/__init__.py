"""Experiment Manager.

Manages immutable experiment records (EXP-######).
Every experiment stores: question, hypothesis, inputs, parameters,
versions, seeds, methods, outputs, logs, evidence, criticism.

Experiments are immutable once created. Clone/modify creates a new record.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.utils.id_gen import generate_stable_id, timestamp_now


class ExperimentStatus(str):
    PROPOSED = "PROPOSED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    REPRODUCING = "REPRODUCING"


class Experiment:
    def __init__(
        self,
        experiment_id: str,
        question: str,
        hypothesis: str = "",
        inputs: Dict[str, Any] = None,
        parameters: Dict[str, Any] = None,
        software_versions: Dict[str, str] = None,
        random_seeds: Dict[str, int] = None,
        methods: List[str] = None,
        outputs: Dict[str, Any] = None,
        logs: List[str] = None,
        evidence: List[Dict[str, Any]] = None,
        interpretation: str = "",
        criticism: str = "",
        reproduction_status: str = "",
        created_at: str = None,
        immutable: bool = True,
    ):
        self.id = experiment_id
        self.question = question
        self.hypothesis = hypothesis
        self.inputs = inputs or {}
        self.parameters = parameters or {}
        self.software_versions = software_versions or {}
        self.random_seeds = random_seeds or {}
        self.methods = methods or []
        self.outputs = outputs or {}
        self.logs = logs or []
        self.evidence = evidence or []
        self.interpretation = interpretation
        self.criticism = criticism
        self.reproduction_status = reproduction_status
        self.created_at = created_at or timestamp_now()
        self.immutable = immutable
        self.status = ExperimentStatus.PROPOSED

    def mark_running(self) -> None:
        if self.immutable and self.status != ExperimentStatus.PROPOSED:
            raise RuntimeError(f"Cannot change status of immutable experiment {self.id}")
        self.status = ExperimentStatus.RUNNING

    def mark_completed(self) -> None:
        self.status = ExperimentStatus.COMPLETED

    def mark_failed(self) -> None:
        self.status = ExperimentStatus.FAILED

    def mark_cancelled(self) -> None:
        self.status = ExperimentStatus.CANCELLED

    def is_immutable(self) -> bool:
        return self.immutable

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "question": self.question,
            "hypothesis": self.hypothesis,
            "inputs": self.inputs,
            "parameters": self.parameters,
            "software_versions": self.software_versions,
            "random_seeds": self.random_seeds,
            "methods": self.methods,
            "outputs": self.outputs,
            "logs": self.logs,
            "evidence": self.evidence,
            "interpretation": self.interpretation,
            "criticism": self.criticism,
            "reproduction_status": self.reproduction_status,
            "status": self.status,
            "created_at": self.created_at,
            "immutable": self.immutable,
        }


class ExperimentManager:
    """Manages the lifecycle of experiments."""

    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self._counter = 0

    def create(
        self,
        question: str,
        hypothesis: str = "",
        inputs: Dict[str, Any] = None,
        parameters: Dict[str, Any] = None,
        software_versions: Dict[str, str] = None,
        random_seeds: Dict[str, int] = None,
        methods: List[str] = None,
    ) -> Experiment:
        self._counter += 1
        exp_id = generate_stable_id("EXP", self._counter)
        exp = Experiment(
            experiment_id=exp_id,
            question=question,
            hypothesis=hypothesis,
            inputs=inputs,
            parameters=parameters,
            software_versions=software_versions,
            random_seeds=random_seeds,
            methods=methods,
        )
        self.experiments[exp_id] = exp
        return exp

    def get(self, exp_id: str) -> Optional[Experiment]:
        return self.experiments.get(exp_id)

    def list_all(self) -> List[Experiment]:
        return list(self.experiments.values())

    def list_by_status(self, status: str) -> List[Experiment]:
        return [e for e in self.experiments.values() if e.status == status]

    def count(self) -> int:
        return len(self.experiments)

    def clone(self, exp_id: str, new_question: str = "") -> Experiment:
        """Clone an experiment. Creates a NEW immutable record.
        
        Original is never modified.
        """
        original = self.get(exp_id)
        if original is None:
            raise ValueError(f"Experiment {exp_id} not found")

        self._counter += 1
        new_id = generate_stable_id("EXP", self._counter)

        cloned = Experiment(
            experiment_id=new_id,
            question=new_question or f"Clone of {exp_id}: {original.question}",
            hypothesis=original.hypothesis,
            inputs=original.inputs.copy(),
            parameters=original.parameters.copy(),
            software_versions=original.software_versions.copy(),
            random_seeds=original.random_seeds.copy(),
            methods=original.methods.copy(),
        )
        self.experiments[new_id] = cloned
        return cloned

    def compare(self, exp_id_a: str, exp_id_b: str) -> Dict[str, Any]:
        """Compare two experiments."""
        a = self.get(exp_id_a)
        b = self.get(exp_id_b)
        if a is None or b is None:
            raise ValueError("One or both experiments not found")

        diffs = {}
        for key in ["question", "hypothesis", "inputs", "parameters", "methods"]:
            val_a = getattr(a, key)
            val_b = getattr(b, key)
            if val_a != val_b:
                diffs[key] = {"a": val_a, "b": val_b}

        return {
            "experiment_a": exp_id_a,
            "experiment_b": exp_id_b,
            "differences": diffs,
            "same": len(diffs) == 0,
        }

    def branch(self, exp_id: str, branch_name: str) -> Experiment:
        """Create a branch from an experiment (variant)."""
        return self.clone(exp_id, new_question=f"Branch '{branch_name}' of {exp_id}")

    def merge(self, exp_id_a: str, exp_id_b: str, merged_question: str = "") -> Experiment:
        """Merge two experiments into a new record."""
        a = self.get(exp_id_a)
        b = self.get(exp_id_b)
        if a is None or b is None:
            raise ValueError("One or both experiments not found")

        merged_inputs = {**a.inputs, **b.inputs}
        merged_params = {**a.parameters, **b.parameters}

        return self.create(
            question=merged_question or f"Merge: {a.question} + {b.question}",
            hypothesis=f"Combined hypothesis from {a.id} and {b.id}",
            inputs=merged_inputs,
            parameters=merged_params,
            software_versions={**a.software_versions, **b.software_versions},
            random_seeds={**a.random_seeds, **b.random_seeds},
            methods=a.methods + b.methods,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": len(self.experiments),
            "by_status": {
                s: [e.id for e in self.list_by_status(s)]
                for s in ExperimentStatus.__dict__.values()
                if isinstance(s, str)
            },
            "experiments": [e.to_dict() for e in self.list_all()],
        }


__all__ = [
    "ExperimentStatus",
    "Experiment",
    "ExperimentManager",
]
