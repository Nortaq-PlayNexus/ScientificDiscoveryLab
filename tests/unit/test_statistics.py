# tests/unit/test_statistics.py
import numpy as np
from src.statistics import (
    BHFDRCorrection, Bootstrap, PermutationTest, EffectSize, NullModel, StatisticalValidation,
)

def test_bhfdr_empty():
    result = BHFDRCorrection.correct([])
    assert result["adjusted"] == []
    assert result["significant"] == []

def test_bhfdr_simple():
    pvals = [0.001, 0.01, 0.05, 0.1, 0.5]
    result = BHFDRCorrection.correct(pvals, alpha=0.05)
    assert len(result["adjusted"]) == 5
    assert sum(result["significant"]) > 0
    # Adjusted p-values should be >= original p-values
    for adj, orig in zip(result["adjusted"], pvals):
        assert adj >= orig - 1e-10

def test_bootstrap_ci():
    data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    result = Bootstrap.ci(data, confidence=0.95, n_bootstrap=500, seed=42)
    assert result["mean"] == 3.0
    assert result["ci_lower"] <= 3.0 <= result["ci_upper"]
    assert result["n_bootstrap"] == 500

def test_bootstrap_mean_ci_contains_mean():
    rng = np.random.default_rng(42)
    data = rng.normal(10, 2, 100)
    result = Bootstrap.ci(data, confidence=0.95, n_bootstrap=500, seed=42)
    assert result["ci_lower"] <= 10 <= result["ci_upper"]

def test_permutation_test():
    a = np.array([1, 2, 3, 4, 5])
    b = np.array([6, 7, 8, 9, 10])
    result = PermutationTest.test(a, b, n_permutations=1000, seed=42)
    assert result["observed_difference"] == 5.0
    assert result["p_value"] <= 0.05  # very different groups
    assert result["significant"] is True

def test_permutation_test_identical():
    rng = np.random.default_rng(42)
    a = rng.normal(5, 1, 50)
    b = rng.normal(5, 1, 50)
    result = PermutationTest.test(a, b, n_permutations=1000, seed=42)
    assert result["significant"] is False  # identical distributions

def test_cohens_d():
    rng = np.random.default_rng(42)
    a = rng.normal(10, 2, 50)
    b = rng.normal(12, 2, 50)
    result = EffectSize.cohens_d(a, b)
    assert "cohens_d" in result
    assert "interpretation" in result
    assert abs(result["cohens_d"]) > 0

def test_effect_size_identical():
    a = np.array([1, 2, 3])
    b = np.array([1, 2, 3])
    result = EffectSize.cohens_d(a, b)
    assert result["cohens_d"] == 0.0

def test_null_model_shuffle():
    data = np.array([1, 2, 3, 4, 5])
    null_dist = NullModel.random_shuffle(data, n_permutations=100, seed=42)
    assert len(null_dist) == 100
    assert np.mean(null_dist) > 0

def test_null_model_matched():
    data = np.array([1.0, 2.0, 3.0])
    control = NullModel.matched_control(data, n_controls=50, seed=42)
    assert len(control) == 50

def test_statistical_validation():
    rng = np.random.default_rng(42)
    data = rng.normal(5, 1, 50)
    control = rng.normal(6, 1, 50)
    sv = StatisticalValidation()
    result = sv.validate(data, control=control, n_bootstrap=100, n_permutations=500)
    assert "bootstrap" in result
    assert "effect_size" in result
    assert "permutation" in result
    assert result["n_observations"] == 50

def test_bhfdr_all_significant():
    pvals = [0.001, 0.002, 0.003]
    result = BHFDRCorrection.correct(pvals, alpha=0.01)
    assert all(result["significant"])

def test_bhfdr_none_significant():
    pvals = [0.5, 0.6, 0.7]
    result = BHFDRCorrection.correct(pvals, alpha=0.05)
    assert not any(result["significant"])
