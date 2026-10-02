from src.literature import LiteratureAgent
from src.novelty import NoveltyEngine
from src.hypothesis import HypothesisEngine, HypothesisStatus
from src.adversarial import AdversarialScientist
from src.statistics import StatisticalValidation, BHFDRCorrection, Bootstrap, PermutationTest, EffectSize, NullModel

# Literature
def test_literature_agent():
    agent = LiteratureAgent()
    assert agent is not None

# Novelty
def test_novelty_engine():
    engine = NoveltyEngine()
    assert engine is not None

# Hypothesis
def test_hypothesis_engine():
    engine = HypothesisEngine()
    h = engine.create("Test", tests=["T1"], falsification_criteria="C1")
    assert h.status == HypothesisStatus.PROPOSED

# Adversarial
def test_adversarial_scientist():
    agent = AdversarialScientist()
    result = agent.run_full_adversarial({"data": "test"})
    assert result["checks_performed"] >= 6

# Statistics
def test_bhfdr():
    result = BHFDRCorrection.correct([0.001, 0.05, 0.5], alpha=0.05)
    assert len(result["adjusted"]) == 3

def test_bootstrap():
    import numpy as np
    data = np.array([1.0, 2.0, 3.0])
    result = Bootstrap.ci(data, n_bootstrap=100, seed=42)
    assert "mean" in result

def test_permutation():
    import numpy as np
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    result = PermutationTest.test(a, b, n_permutations=100, seed=42)
    assert "p_value" in result

def test_effect_size():
    import numpy as np
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    result = EffectSize.cohens_d(a, b)
    assert "cohens_d" in result

def test_null_model():
    import numpy as np
    data = np.array([1.0, 2.0, 3.0])
    null = NullModel.random_shuffle(data, n_permutations=50, seed=42)
    assert len(null) == 50

def test_statistical_validation():
    import numpy as np
    sv = StatisticalValidation()
    data = np.array([1.0, 2.0, 3.0])
    result = sv.validate(data, n_bootstrap=50, n_permutations=50)
    assert "bootstrap" in result
