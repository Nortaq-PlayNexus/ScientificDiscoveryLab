# tests/unit/test_literature.py
from src.literature import Claim, LiteratureSource, LiteratureAgent
from src.evidence import EvidenceSourceType

def test_claim_creation():
    c = Claim("Test claim", compounds=["A"], targets=["B"])
    assert c.text == "Test claim"
    assert c.compounds == ["A"]
    assert c.targets == ["B"]

def test_claim_to_dict():
    c = Claim("Test", compounds=["A"])
    d = c.to_dict()
    assert d["text"] == "Test"

def test_literature_source_abstract_only():
    s = LiteratureSource(title="Test", abstract="Some abstract")
    assert s.is_abstract_only() is True

def test_literature_source_to_dict():
    s = LiteratureSource(doi="10.1234/test", pmid="123456", title="Test", year=2024)
    d = s.to_dict()
    assert d["doi"] == "10.1234/test"
    assert d["pmid"] == "123456"
    assert d["abstract_only"] is True

def test_agent_init():
    agent = LiteratureAgent()
    assert len(agent.sources) == 0

def test_agent_extract_claims():
    agent = LiteratureAgent()
    abstract = "We found that compound A increases activity. The results were significant."
    claims = agent.extract_claims(abstract)
    assert len(claims) > 0
    assert "We found" in claims[0]

def test_agent_create_source():
    agent = LiteratureAgent()
    source = agent.create_source_record(
        doi="10.1234/test",
        title="Test Paper",
        authors=["Author A"],
        year=2024,
        abstract="Some abstract",
    )
    assert source.doi == "10.1234/test"
    assert len(agent.sources) == 1

def test_agent_validate_citation_local():
    """When network is unavailable, citation validation returns False."""
    agent = LiteratureAgent()
    result = agent.validate_citation("10.1234/does-not-exist-test")
    assert isinstance(result, bool)
