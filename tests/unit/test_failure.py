# tests/unit/test_failure.py
from src.failure import FailureRecovery, FailureRecord, FailureType

def test_failure_record_creation():
    rec = FailureRecord(
        failure_id="FAIL-000001",
        experiment_id="EXP-000001",
        error_message="Test error",
        failure_type=FailureType.RUNTIME_ERROR,
    )
    assert rec.id == "FAIL-000001"
    assert rec.experiment_id == "EXP-000001"
    assert rec.resolved is False
    assert rec.original_results_preserved is True

def test_failure_record_to_dict():
    rec = FailureRecord("FAIL-000001", "EXP-000001", "Error")
    d = rec.to_dict()
    assert d["id"] == "FAIL-000001"
    assert d["error_message"] == "Error"

def test_recovery_capture():
    rec = FailureRecovery()
    failure = rec.capture("EXP-000001", ValueError("Test error"), FailureType.VALIDATION_ERROR)
    assert failure is not None
    assert failure.experiment_id == "EXP-000001"
    assert "Test error" in failure.error_message

def test_recovery_get():
    rec = FailureRecovery()
    failure = rec.capture("EXP-000001", ValueError("Error"))
    retrieved = rec.get_failure(failure.id)
    assert retrieved is not None
    assert retrieved.id == failure.id

def test_recovery_get_none():
    rec = FailureRecovery()
    assert rec.get_failure("FAIL-999999") is None

def test_recovery_get_by_experiment():
    rec = FailureRecovery()
    rec.capture("EXP-000001", ValueError("Error 1"))
    rec.capture("EXP-000002", ValueError("Error 2"))
    rec.capture("EXP-000001", ValueError("Error 3"))
    failures = rec.get_by_experiment("EXP-000001")
    assert len(failures) == 2

def test_recovery_mark_resolved():
    rec = FailureRecovery()
    failure = rec.capture("EXP-000001", ValueError("Error"))
    assert rec.mark_resolved(failure.id) is True
    assert failure.resolved is True

def test_recovery_mark_resolved_none():
    rec = FailureRecovery()
    assert rec.mark_resolved("FAIL-999999") is False

def test_recovery_get_unresolved():
    rec = FailureRecovery()
    f1 = rec.capture("EXP-000001", ValueError("Error 1"))
    f2 = rec.capture("EXP-000001", ValueError("Error 2"))
    rec.mark_resolved(f1.id)
    unresolved = rec.get_unresolved()
    assert len(unresolved) == 1
    assert unresolved[0].id == f2.id

def test_recovery_safe_retry_success():
    rec = FailureRecovery()
    success, result, failure = rec.safe_retry(
        "EXP-000001", lambda: 42, max_retries=2
    )
    assert success is True
    assert result == 42
    assert failure is None

def test_recovery_safe_retry_failure():
    rec = FailureRecovery()
    call_count = [0]
    def fail_func():
        call_count[0] += 1
        raise RuntimeError("Always fails")

    success, result, failure = rec.safe_retry(
        "EXP-000001", fail_func, max_retries=2
    )
    assert success is False
    assert result is None
    assert failure is not None
    assert call_count[0] == 3  # 1 initial + 2 retries

def test_recovery_diagnosis():
    rec = FailureRecovery()
    failure = rec.capture("EXP-000001", ValueError("Invalid SMILES"), FailureType.VALIDATION_ERROR)
    assert "SMILES" in failure.diagnosis

def test_recovery_preserve_original_results():
    rec = FailureRecovery()
    rec.capture("EXP-000001", ValueError("Error"))
    assert rec.preserve_original_results("EXP-000001") is True

def test_recovery_summary():
    rec = FailureRecovery()
    rec.capture("EXP-000001", ValueError("E1"), FailureType.VALIDATION_ERROR)
    rec.capture("EXP-000001", RuntimeError("E2"), FailureType.RUNTIME_ERROR)
    summary = rec.get_summary()
    assert summary["total_failures"] == 2
    assert summary["unresolved"] == 2
    assert "VALIDATION_ERROR" in summary["by_type"]

def test_recovery_to_dict():
    rec = FailureRecovery()
    rec.capture("EXP-000001", ValueError("Error"))
    d = rec.to_dict()
    assert d["summary"]["total_failures"] == 1
    assert len(d["failures"]) == 1
