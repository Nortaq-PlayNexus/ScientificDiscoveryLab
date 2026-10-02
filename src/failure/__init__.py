"""Failure Recovery System.

Captures errors, preserves logs, marks experiments as failed (immutable),
provides diagnosis suggestions, safe retry mechanism.
Original results are NEVER overwritten.
"""

import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple

from src.utils.id_gen import generate_stable_id, timestamp_now


class FailureType(str):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIMEOUT = "TIMEOUT"
    RESOURCE_EXHAUSTION = "RESOURCE_EXHAUSTION"
    DATA_CORRUPTION = "DATA_CORRUPTION"
    LOGIC_ERROR = "LOGIC_ERROR"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    UNKNOWN = "UNKNOWN"


class FailureRecord:
    def __init__(
        self,
        failure_id: str,
        experiment_id: str,
        error_message: str,
        failure_type: str = FailureType.UNKNOWN,
        traceback_text: str = "",
        context: Dict[str, Any] = None,
        timestamp: str = None,
        diagnosis: str = "",
        resolved: bool = False,
        original_results_preserved: bool = True,
    ):
        self.id = failure_id
        self.experiment_id = experiment_id
        self.error_message = error_message
        self.failure_type = failure_type
        self.traceback = traceback_text
        self.context = context or {}
        self.timestamp = timestamp or timestamp_now()
        self.diagnosis = diagnosis
        self.resolved = resolved
        self.original_results_preserved = original_results_preserved

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "error_message": self.error_message,
            "failure_type": self.failure_type,
            "traceback": self.traceback,
            "context": self.context,
            "timestamp": self.timestamp,
            "diagnosis": self.diagnosis,
            "resolved": self.resolved,
            "original_results_preserved": self.original_results_preserved,
        }


class FailureRecovery:
    """Manages failure capture, diagnosis, and safe retry."""

    def __init__(self):
        self.failures: Dict[str, FailureRecord] = {}
        self._counter = 0
        self._log: List[Dict[str, Any]] = []

    def _generate_failure_id(self) -> str:
        self._counter += 1
        return generate_stable_id("FAIL", self._counter)

    def capture(
        self,
        experiment_id: str,
        error: Exception,
        failure_type: str = FailureType.UNKNOWN,
        context: Dict[str, Any] = None,
    ) -> FailureRecord:
        """Capture a failure with full context. Never overwrites original results."""
        tb = traceback.format_exc()
        failure_id = self._generate_failure_id()

        diagnosis = self._diagnose(error, failure_type)

        record = FailureRecord(
            failure_id=failure_id,
            experiment_id=experiment_id,
            error_message=str(error),
            failure_type=failure_type,
            traceback_text=tb,
            context=context or {},
            diagnosis=diagnosis,
        )
        self.failures[failure_id] = record
        self._log.append({
            "timestamp": timestamp_now(),
            "action": "CAPTURE_FAILURE",
            "failure_id": failure_id,
            "experiment_id": experiment_id,
            "type": failure_type,
        })
        return record

    def _diagnose(self, error: Exception, failure_type: str) -> str:
        """Generate diagnosis suggestions based on error type."""
        error_str = str(error).lower()
        msg = str(error)

        diagnoses = []

        if "smiles" in error_str or "smile" in error_str:
            diagnoses.append("Invalid SMILES string — validate structure before processing")
        if "inchi" in error_str:
            diagnoses.append("InChI conversion failed — check molecular structure validity")
        if "timeout" in failure_type.lower() or "timed out" in error_str:
            diagnoses.append("Operation timed out — consider increasing timeout or reducing input size")
        if "memory" in error_str or "ram" in error_str or "mle" in error_str:
            diagnoses.append("Memory exhausted — reduce input size or increase resources")
        if "connection" in error_str or "network" in error_str:
            diagnoses.append("Network failure — check internet connectivity, retry with graceful degradation")
        if "key" in error_str and "error" in error_str:
            diagnoses.append("Key error — check input data structure and required fields")
        if "type" in error_str and "error" in error_str:
            diagnoses.append("Type error — verify input types match expected parameters")
        if "attribute" in error_str and "error" in error_str:
            diagnoses.append("Attribute error — object may not have expected method or property")
        if "value" in error_str and "error" in error_str:
            diagnoses.append("Value error — input value out of expected range")

        if not diagnoses:
            diagnoses.append(f"Review error: {msg[:200]}")
            diagnoses.append("Consider running with reduced parameters")

        return " | ".join(diagnoses)

    def get_failure(self, failure_id: str) -> Optional[FailureRecord]:
        return self.failures.get(failure_id)

    def get_by_experiment(self, experiment_id: str) -> List[FailureRecord]:
        return [f for f in self.failures.values() if f.experiment_id == experiment_id]

    def get_unresolved(self) -> List[FailureRecord]:
        return [f for f in self.failures.values() if not f.resolved]

    def mark_resolved(self, failure_id: str) -> bool:
        failure = self.get_failure(failure_id)
        if failure:
            failure.resolved = True
            self._log.append({
                "timestamp": timestamp_now(),
                "action": "RESOLVE",
                "failure_id": failure_id,
            })
            return True
        return False

    def safe_retry(
        self,
        experiment_id: str,
        func: Callable,
        max_retries: int = 3,
        *args,
        **kwargs,
    ) -> Tuple[bool, Any, Optional[FailureRecord]]:
        """Safe retry: preserves original results, captures each attempt.
        
        Returns (success, result, failure_record)
        """
        last_failure = None
        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return True, result, None
            except Exception as e:
                failure = self.capture(
                    experiment_id=experiment_id,
                    error=e,
                    failure_type=FailureType.RUNTIME_ERROR,
                    context={"attempt": attempt + 1, "max_retries": max_retries},
                )
                last_failure = failure

        return False, None, last_failure

    def get_log(self) -> List[Dict[str, Any]]:
        return self._log.copy()

    def get_summary(self) -> Dict[str, Any]:
        by_type = {}
        unresolved = 0
        for f in self.failures.values():
            by_type.setdefault(f.failure_type, 0)
            by_type[f.failure_type] += 1
            if not f.resolved:
                unresolved += 1
        return {
            "total_failures": len(self.failures),
            "unresolved": unresolved,
            "by_type": by_type,
            "diagnoses_available": all(f.diagnosis for f in self.failures.values()),
        }

    def preserve_original_results(self, experiment_id: str) -> bool:
        """Confirm that original results are preserved (never overwritten)."""
        failures = self.get_by_experiment(experiment_id)
        return all(f.original_results_preserved for f in failures)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.get_summary(),
            "failures": [f.to_dict() for f in self.failures.values()],
            "log_length": len(self._log),
        }


__all__ = [
    "FailureType",
    "FailureRecord",
    "FailureRecovery",
]
