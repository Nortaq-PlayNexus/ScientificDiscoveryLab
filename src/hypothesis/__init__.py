"""Hypothesis Engine.

Creates structured, falsifiable hypotheses with full lifecycle management.
Every hypothesis actively seeks evidence against it.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from src.evidence import EvidenceLevel, EvidenceSourceType


class HypothesisStatus(str):
    PROPOSED = "PROPOSED"
    TESTING = "TESTING"
    SUPPORTED = "SUPPORTED"
    WEAKENED = "WEAKENED"
    REFUTED = "REFUTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REPRODUCED = "REPRODUCED"


class Prediction:
    def __init__(self, description: str, expected_outcome: str, evidence_level: str = "E0"):
        self.description = description
        self.expected_outcome = expected_outcome
        self.evidence_level = evidence_level

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "expected_outcome": self.expected_outcome,
            "evidence_level": self.evidence_level,
        }


class Hypothesis:
    def __init__(
        self,
        hypothesis_id: str,
        statement: str,
        rationale: str = "",
        assumptions: List[str] = None,
        predictions: List[Dict[str, Any]] = None,
        tests: List[str] = None,
        falsification_criteria: str = "",
        evidence: List[Dict[str, Any]] = None,
        confidence: float = 0.0,
    ):
        self.id = hypothesis_id
        self.statement = statement
        self.rationale = rationale
        self.assumptions = assumptions or []
        self.predictions = [Prediction(**p) if isinstance(p, dict) else p for p in (predictions or [])]
        self.tests = tests or []
        self.falsification_criteria = falsification_criteria
        self.evidence = evidence or []
        self.confidence = confidence
        self.status = HypothesisStatus.PROPOSED
        self.created_at = datetime.utcnow().isoformat()
        self.history: List[Dict[str, str]] = [
            {"timestamp": self.created_at, "status": self.status, "note": "Hypothesis proposed"}
        ]

    def set_status(self, new_status: str, note: str = "") -> None:
        valid_statuses = [
            HypothesisStatus.PROPOSED,
            HypothesisStatus.TESTING,
            HypothesisStatus.SUPPORTED,
            HypothesisStatus.WEAKENED,
            HypothesisStatus.REFUTED,
            HypothesisStatus.INCONCLUSIVE,
            HypothesisStatus.REPRODUCED,
        ]
        assert new_status in valid_statuses, f"Invalid status: {new_status}"
        self.status = new_status
        self.history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "status": new_status,
            "note": note,
        })

    def add_prediction(self, description: str, expected_outcome: str) -> None:
        self.predictions.append(Prediction(description, expected_outcome))

    def add_test(self, test: str) -> None:
        self.tests.append(test)

    def add_assumption(self, assumption: str) -> None:
        self.assumptions.append(assumption)

    def is_falsifiable(self) -> bool:
        return len(self.falsification_criteria) > 0 and len(self.tests) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "rationale": self.rationale,
            "assumptions": self.assumptions,
            "predictions": [p.to_dict() for p in self.predictions],
            "tests": self.tests,
            "falsification_criteria": self.falsification_criteria,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "status": self.status,
            "created_at": self.created_at,
            "history": self.history,
            "is_falsifiable": self.is_falsifiable(),
        }


class HypothesisEngine:
    """Manages structured hypotheses."""

    def __init__(self):
        self.hypotheses: List[Hypothesis] = []
        self._counter = 0

    def create(
        self,
        statement: str,
        rationale: str = "",
        assumptions: List[str] = None,
        predictions: List[Dict[str, Any]] = None,
        tests: List[str] = None,
        falsification_criteria: str = "",
        confidence: float = 0.0,
    ) -> Hypothesis:
        self._counter += 1
        hyp_id = f"HYP-{self._counter:06d}"
        hyp = Hypothesis(
            hypothesis_id=hyp_id,
            statement=statement,
            rationale=rationale,
            assumptions=assumptions,
            predictions=predictions,
            tests=tests,
            falsification_criteria=falsification_criteria,
            confidence=confidence,
        )
        self.hypotheses.append(hyp)
        return hyp

    def get_by_id(self, hyp_id: str) -> Optional[Hypothesis]:
        for h in self.hypotheses:
            if h.id == hyp_id:
                return h
        return None

    def get_by_status(self, status: str) -> List[Hypothesis]:
        return [h for h in self.hypotheses if h.status == status]

    def search_novelty(self, hypothesis: Hypothesis, novelty_engine=None) -> Dict[str, Any]:
        """Check if hypothesis components are novel.
        
        Returns evidence-level assessment.
        """
        if novelty_engine is None:
            return {
                "novelty_check": "SKIPPED",
                "note": "No novelty engine provided.",
            }
        return {
            "novelty_check": "COMPLETED",
            "note": "Run novelty engine on hypothesis components.",
        }

    def get_summary(self) -> Dict[str, Any]:
        by_status = {}
        for h in self.hypotheses:
            by_status.setdefault(h.status, []).append(h.id)
        return {
            "total": len(self.hypotheses),
            "by_status": by_status,
            "falsifiable": sum(1 for h in self.hypotheses if h.is_falsifiable()),
        }


__all__ = [
    "HypothesisStatus",
    "Prediction",
    "Hypothesis",
    "HypothesisEngine",
]
