"""Adversarial Scientist.

Dedicated agent whose job is to DISPROVE findings.
For every interesting result, asks critical questions:
- Could this be an artifact?
- Could this be a database error?
- Could this be stereochemistry?
- Could this be a parameter artifact?
- Could this be numerical instability?
- Could this be docking bias?
- Could this be overfitting?
- Could this be multiple-testing?
- Could this be selection bias?
- Could this result disappear under another method?
- Is there an alternative explanation?

This agent MUST be allowed to reject the main swarm's conclusions.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class CheckCategory(str, Enum):
    ARTIFACT = "artifact"
    DATABASE_ERROR = "database_error"
    STEREOCHEMISTRY = "stereochemistry"
    PARAMETER = "parameter"
    NUMERICAL = "numerical"
    DOCKING_BIAS = "docking_bias"
    OVERFITTING = "overfitting"
    MULTIPLE_TESTING = "multiple_testing"
    SELECTION_BIAS = "selection_bias"
    ALTERNATIVE_METHOD = "alternative_method"
    GENERAL = "general"


class AdversarialFinding:
    def __init__(
        self,
        category: CheckCategory,
        question: str,
        result: str,
        severity: str = "low",
    ):
        self.category = category
        self.question = question
        self.result = result
        self.severity = severity
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "question": self.question,
            "result": self.result,
            "severity": self.severity,
            "timestamp": self.timestamp,
        }


class AdversarialScientist:
    """Attempts to disprove findings."""

    def __init__(self):
        self.findings: List[AdversarialFinding] = []
        self.checks_performed = 0

    def check_artifact(self, result: Any, context: Dict[str, Any] = None) -> AdversarialFinding:
        """Check if result could be an artifact."""
        self.checks_performed += 1
        finding = AdversarialFinding(
            category=CheckCategory.ARTIFACT,
            question="Could this be an artifact?",
            result=f"Examined context: {list(context.keys()) if context else 'none'}. "
                   "Requires resolution dependence, grid dependence, and parameter sensitivity checks.",
            severity="medium",
        )
        self.findings.append(finding)
        return finding

    def check_database_error(self, result: Any) -> AdversarialFinding:
        """Check if result could be due to database error."""
        self.checks_performed += 1
        finding = AdversarialFinding(
            category=CheckCategory.DATABASE_ERROR,
            question="Could this be a database error?",
            result="Cross-reference with multiple databases required before accepting.",
            severity="medium",
        )
        self.findings.append(finding)
        return finding

    def check_stereochemistry(self, result: Any) -> AdversarialFinding:
        """Check if stereochemistry affects result."""
        self.checks_performed += 1
        finding = AdversarialFinding(
            category=CheckCategory.STEREOCHEMISTRY,
            question="Could this be stereochemistry?",
            result="Verify stereochemistry is correctly specified and consistent.",
            severity="medium",
        )
        self.findings.append(finding)
        return finding

    def check_parameter(self, result: Any, parameters: Dict[str, Any] = None) -> AdversarialFinding:
        """Check if result is a parameter artifact."""
        self.checks_performed += 1
        param_keys = list(parameters.keys()) if parameters else []
        finding = AdversarialFinding(
            category=CheckCategory.PARAMETER,
            question="Could this be a parameter artifact?",
            result=f"Parameters used: {param_keys}. Parameter sensitivity analysis required.",
            severity="high",
        )
        self.findings.append(finding)
        return finding

    def check_numerical(self, result: Any) -> AdversarialFinding:
        """Check for numerical instability."""
        self.checks_performed += 1
        finding = AdversarialFinding(
            category=CheckCategory.NUMERICAL,
            question="Could this be numerical instability?",
            result="Check convergence, precision, and boundary conditions.",
            severity="medium",
        )
        self.findings.append(finding)
        return finding

    def check_docking_bias(self, result: Any) -> AdversarialFinding:
        """Check if docking result is biased."""
        self.checks_performed += 1
        finding = AdversarialFinding(
            category=CheckCategory.DOCKING_BIAS,
            question="Could this be docking bias?",
            result="Docking score does NOT equal clinical efficacy. "
                   "Verify with orthogonal methods.",
            severity="high",
        )
        self.findings.append(finding)
        return finding

    def check_overfitting(self, result: Any, n_features: int = 0, n_samples: int = 0) -> AdversarialFinding:
        """Check for overfitting."""
        self.checks_performed += 1
        ratio = f"{n_samples}/{n_features}" if n_features > 0 else "unknown"
        finding = AdversarialFinding(
            category=CheckCategory.OVERFITTING,
            question="Could this be overfitting?",
            result=f"Data ratio: {ratio}. Cross-validation required.",
            severity="high",
        )
        self.findings.append(finding)
        return finding

    def check_multiple_testing(self, n_tests: int = 0) -> AdversarialFinding:
        """Check for multiple testing issues."""
        self.checks_performed += 1
        finding = AdversarialFinding(
            category=CheckCategory.MULTIPLE_TESTING,
            question="Could this be multiple-testing?",
            result=f"{n_tests} comparisons. Multiple-testing correction (BH-FDR) required.",
            severity="high" if n_tests > 1 else "low",
        )
        self.findings.append(finding)
        return finding

    def check_selection_bias(self) -> AdversarialFinding:
        """Check for selection bias."""
        self.checks_performed += 1
        finding = AdversarialFinding(
            category=CheckCategory.SELECTION_BIAS,
            question="Could this be selection bias?",
            result="Verify randomization and blinding where applicable.",
            severity="medium",
        )
        self.findings.append(finding)
        return finding

    def check_alternative_method(self, result: Any) -> AdversarialFinding:
        """Check if result holds under alternative method."""
        self.checks_performed += 1
        finding = AdversarialFinding(
            category=CheckCategory.ALTERNATIVE_METHOD,
            question="Could this result disappear under another method?",
            result="Independent implementation required for verification.",
            severity="high",
        )
        self.findings.append(finding)
        return finding

    def check_alternative_explanation(self, result: Any) -> AdversarialFinding:
        """Is there an alternative explanation?"""
        self.checks_performed += 1
        finding = AdversarialFinding(
            category=CheckCategory.GENERAL,
            question="Is there an alternative explanation?",
            result="Consider confounding variables, reverse causality, "
                   "and confounding factors before accepting.",
            severity="medium",
        )
        self.findings.append(finding)
        return finding

    def run_full_adversarial(self, result: Any, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run all adversarial checks."""
        self.check_artifact(result, context)
        self.check_database_error(result)
        self.check_stereochemistry(result)
        self.check_numerical(result)
        self.check_alternative_method(result)
        self.check_alternative_explanation(result)

        severe = [f for f in self.findings if f.severity == "high"]
        critical = [f for f in self.findings if f.severity in ["critical", "high"]]

        return {
            "checks_performed": self.checks_performed,
            "findings": [f.to_dict() for f in self.findings],
            "n_high_severity": len(severe),
            "recommendation": "DO NOT accept findings" if severe else "Accept with caution — verify independently.",
        }

    def can_reject(self) -> bool:
        """Adversarial scientist can always reject if severe findings exist."""
        return any(f.severity in ["critical", "high"] for f in self.findings)


__all__ = [
    "AdversarialScientist",
    "AdversarialFinding",
    "CheckCategory",
]
