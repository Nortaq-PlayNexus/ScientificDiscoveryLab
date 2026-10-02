# tests/unit/test_adversarial.py
from src.adversarial import AdversarialScientist, CheckCategory

def test_agent_init():
    agent = AdversarialScientist()
    assert len(agent.findings) == 0
    assert agent.checks_performed == 0

def test_check_artifact():
    agent = AdversarialScientist()
    result = agent.check_artifact({"key": "value"}, context={"param": 1})
    assert result.category == CheckCategory.ARTIFACT
    assert "artifact" in result.question.lower()

def test_check_database_error():
    agent = AdversarialScientist()
    result = agent.check_database_error("some result")
    assert result.category == CheckCategory.DATABASE_ERROR

def test_check_stereochemistry():
    agent = AdversarialScientist()
    result = agent.check_stereochemistry("some result")
    assert result.category == CheckCategory.STEREOCHEMISTRY

def test_check_parameter():
    agent = AdversarialScientist()
    result = agent.check_parameter("result", parameters={"temp": 300, "pH": 7.0})
    assert result.category == CheckCategory.PARAMETER
    assert "temp" in result.result

def test_check_numerical():
    agent = AdversarialScientist()
    result = agent.check_numerical("result")
    assert result.category == CheckCategory.NUMERICAL

def test_check_docking_bias():
    agent = AdversarialScientist()
    result = agent.check_docking_bias("score")
    assert result.category == CheckCategory.DOCKING_BIAS
    assert "CLINICAL EVIDENCE" in result.result or "efficacy" in result.result.lower()

def test_check_overfitting():
    agent = AdversarialScientist()
    result = agent.check_overfitting("result", n_features=10, n_samples=100)
    assert result.category == CheckCategory.OVERFITTING
    assert "100/10" in result.result

def test_check_multiple_testing():
    agent = AdversarialScientist()
    result = agent.check_multiple_testing(n_tests=20)
    assert result.category == CheckCategory.MULTIPLE_TESTING
    assert "20" in result.result

def test_check_selection_bias():
    agent = AdversarialScientist()
    result = agent.check_selection_bias()
    assert result.category == CheckCategory.SELECTION_BIAS

def test_check_alternative_method():
    agent = AdversarialScientist()
    result = agent.check_alternative_method("result")
    assert result.category == CheckCategory.ALTERNATIVE_METHOD

def test_check_alternative_explanation():
    agent = AdversarialScientist()
    result = agent.check_alternative_explanation("result")
    assert result.category == CheckCategory.GENERAL

def test_run_full_adversarial():
    agent = AdversarialScientist()
    result = agent.run_full_adversarial({"data": "test"})
    assert result["checks_performed"] >= 6
    assert "recommendation" in result

def test_adversarial_can_reject():
    agent = AdversarialScientist()
    # Run with high-severity checks
    agent.check_parameter("result", parameters={"x": 1})
    assert agent.can_reject() is True  # high severity

def test_adversarial_finding_to_dict():
    agent = AdversarialScientist()
    finding = agent.check_artifact("result")
    d = finding.to_dict()
    assert "category" in d
    assert "question" in d
    assert "severity" in d
