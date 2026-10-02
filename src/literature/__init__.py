"""Literature Research Agent.

Searches scientific literature, extracts claims, validates citations,
and links papers to database entities.

CRITICAL: Never treats an abstract alone as complete evidence.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import requests

from src.evidence import Evidence, EvidenceLevel, EvidenceSourceType


class Claim:
    def __init__(
        self,
        text: str,
        compounds: List[str] = None,
        targets: List[str] = None,
        experimental_evidence: List[str] = None,
        limitations: List[str] = None,
    ):
        self.text = text
        self.compounds = compounds or []
        self.targets = targets or []
        self.experimental_evidence = experimental_evidence or []
        self.limitations = limitations or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "compounds": self.compounds,
            "targets": self.targets,
            "experimental_evidence": self.experimental_evidence,
            "limitations": self.limitations,
        }


class LiteratureSource:
    def __init__(
        self,
        doi: Optional[str] = None,
        pmid: Optional[str] = None,
        title: Optional[str] = None,
        authors: List[str] = None,
        year: Optional[int] = None,
        journal: Optional[str] = None,
        abstract: Optional[str] = None,
        claims: List[Dict[str, Any]] = None,
        experimental_evidence: List[str] = None,
        limitations: List[str] = None,
        url: Optional[str] = None,
    ):
        self.doi = doi
        self.pmid = pmid
        self.title = title
        self.authors = authors or []
        self.year = year
        self.journal = journal
        self.abstract = abstract
        self.claims = claims or []
        self.experimental_evidence = experimental_evidence or []
        self.limitations = limitations or []
        self.url = url
        self.retrieved_at = datetime.utcnow().isoformat()

    def is_abstract_only(self) -> bool:
        """Check if this source is only supported by abstract (not full text)."""
        return True  # All literature sources start as abstract-only

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doi": self.doi,
            "pmid": self.pmid,
            "title": self.title,
            "authors": self.authors,
            "year": self.year,
            "journal": self.journal,
            "abstract": self.abstract,
            "claims": [c.to_dict() if isinstance(c, Claim) else c for c in self.claims],
            "experimental_evidence": self.experimental_evidence,
            "limitations": self.limitations,
            "url": self.url,
            "retrieved_at": self.retrieved_at,
            "abstract_only": self.is_abstract_only(),
        }


class LiteratureAgent:
    """Searches literature and extracts structured information."""

    def __init__(self):
        self.sources: List[LiteratureSource] = []

    def search_pubmed(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search PubMed via E-utilities API."""
        results = []
        try:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
            search_url = f"{base_url}/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
            }
            resp = requests.get(search_url, params=params, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                id_list = data.get("esearchresult", {}).get("idlist", [])
                for pmid in id_list:
                    summary = self._fetch_pubmed_summary(pmid)
                    if summary:
                        results.append(summary)
        except Exception as e:
            pass
        return results

    def _fetch_pubmed_summary(self, pmid: str) -> Optional[Dict[str, Any]]:
        """Fetch PubMed article summary."""
        try:
            base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
            url = f"{base_url}/efetch.fcgi"
            params = {"db": "pubmed", "id": pmid, "retmode": "xml"}
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                return {"pmid": pmid, "raw_xml": resp.text[:10000]}
        except Exception:
            pass
        return None

    def search_arxiv(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search arXiv API."""
        results = []
        try:
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": max_results,
            }
            resp = requests.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(resp.text)
                for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                    title_el = entry.find("{http://www.w3.org/2005/Atom}title")
                    id_el = entry.find("{http://www.w3.org/2005/Atom}id")
                    summary_el = entry.find("{http://www.w3.org/2005/Atom}summary")
                    if id_el is not None:
                        results.append({
                            "id": id_el.text,
                            "title": title_el.text.strip() if title_el is not None else "",
                            "abstract": summary_el.text.strip() if summary_el is not None else "",
                            "source": "arxiv",
                        })
        except Exception:
            pass
        return results

    def validate_citation(self, doi: str) -> bool:
        """Check if a DOI resolves."""
        try:
            url = f"https://doi.org/{doi}"
            headers = {"Accept": "application/json"}
            resp = requests.head(url, headers=headers, timeout=15, allow_redirects=True)
            return resp.status_code == 200
        except Exception:
            return False

    def extract_claims(self, abstract: str) -> List[str]:
        """Extract claims from abstract text (heuristic-based)."""
        claims = []
        sentences = abstract.replace(".", ".\n").split("\n")
        for sent in sentences:
            sent = sent.strip()
            if not sent:
                continue
            lower = sent.lower()
            if any(kw in lower for kw in ["we found", "we observed", "we demonstrate", "our results show",
                                            "we report", "we show", "it was found", "it was observed"]):
                claims.append(sent)
        return claims

    def search_and_extract(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search PubMed and extract claims."""
        papers = self.search_pubmed(query, max_results)
        results = []
        for paper in papers:
            pmid = paper.get("pmid", "")
            raw = paper.get("raw_xml", "")
            if raw:
                claims = self.extract_claims(raw[:3000])
                results.append({
                    "pmid": pmid,
                    "claims_count": len(claims),
                    "claims": claims[:5],
                    "evidence_level": "E2",
                    "note": "Abstract-level evidence only. Full text needed for E3+.",
                })
        return results

    def create_source_record(
        self,
        doi: Optional[str] = None,
        pmid: Optional[str] = None,
        title: Optional[str] = None,
        authors: List[str] = None,
        year: Optional[int] = None,
        journal: Optional[str] = None,
        abstract: Optional[str] = None,
        url: Optional[str] = None,
    ) -> LiteratureSource:
        """Create a structured literature source record."""
        source = LiteratureSource(
            doi=doi,
            pmid=pmid,
            title=title,
            authors=authors,
            year=year,
            journal=journal,
            abstract=abstract,
            url=url,
        )
        self.sources.append(source)
        return source


__all__ = [
    "Claim",
    "LiteratureSource",
    "LiteratureAgent",
]
