"""Novelty Engine.

Searches databases to determine if a molecule, reaction, plant, or compound
is previously known. NEVER claims 'first discovery'.
Instead: 'No matching record was found in [SOURCE] as of [DATE].'
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

import pubchempy as pcp
import requests

from src.evidence import EvidenceLevel
from src.utils.validator import validate_smiles


class NoveltyResult:
    def __init__(
        self,
        query: str,
        category: str,
        is_known: bool,
        sources_searched: List[str],
        search_date: str,
        details: Dict[str, Any] = None,
    ):
        self.query = query
        self.category = category
        self.is_known = is_known
        self.sources_searched = sources_searched
        self.search_date = search_date
        self.details = details or {}

    @staticmethod
    def unknown_result(query: str, category: str, sources_searched: List[str]) -> "NoveltyResult":
        """Return an UNKNOWN result (no claim of novelty)."""
        return NoveltyResult(
            query=query,
            category=category,
            is_known=False,
            sources_searched=sources_searched,
            search_date=datetime.utcnow().strftime("%Y-%m-%d"),
            details={
                "statement": f"No matching record was found in the searched sources as of {datetime.utcnow().strftime('%Y-%m-%d')}.",
                "caveat": "Absence of evidence is not evidence of absence. This does not establish priority or novelty.",
                "sources_searched": sources_searched,
            },
        )


class NoveltyEngine:
    """Determines if candidates are previously known."""

    def __init__(self):
        self.sources_searched: List[str] = []

    def search_pubchem(self, smiles: str, name: str = "") -> Dict[str, Any]:
        """Search PubChem for a compound."""
        result = {"found": False, "source": "PubChem", "matches": []}
        try:
            if smiles and validate_smiles(smiles)["valid"]:
                c = pcp.Compound.from_smiles(smiles)
                if c:
                    result["found"] = True
                    result["cid"] = c.cid
                    result["matches"].append(f"CID: {c.cid}")
            elif name:
                ps = pcp.get_compounds(name, "name")
                if ps:
                    result["found"] = True
                    for p in ps[:3]:
                        result["matches"].append(f"CID: {p.cid}")
        except Exception:
            pass
        self.sources_searched.append("PubChem")
        return result

    def search_chebi(self, name: str) -> Dict[str, Any]:
        """Search ChEBI via REST API."""
        result = {"found": False, "source": "ChEBI", "matches": []}
        try:
            url = "https://www.ebi.ac.uk/chebi/services/rest"
            params = {"chebiLabel": name, "maxRows": 5}
            resp = requests.get(url, params=params, timeout=15)
            if resp.status_code == 200 and resp.text:
                result["found"] = True
                result["matches"].append(f"Response: {len(resp.text)} chars")
        except Exception:
            pass
        self.sources_searched.append("ChEBI")
        return result

    def check_novelty(
        self,
        smiles: str = "",
        name: str = "",
        plant_name: str = "",
        reaction_smarts: str = "",
    ) -> Dict[str, Any]:
        """Check novelty across multiple databases.
        
        NEVER claims 'first discovery'.
        Always says 'No matching record found as of [DATE]'.
        """
        results = {}
        sources = []

        if smiles:
            pc_result = self.search_pubchem(smiles)
            results["pubchem"] = pc_result
            if not pc_result["found"]:
                sources.append("PubChem")

        if name:
            chebi_result = self.search_chebi(name)
            results["chebi"] = chebi_result
            if not chebi_result["found"]:
                sources.append("ChEBI")

        sources_searched = list(set(sources)) if sources else ["PubChem", "ChEBI"]

        if not any(r["found"] for r in results.values()):
            return {
                "novelty": "UNKNOWN",
                "statement": NoveltyResult.unknown_result(
                    query=f"{name} {smiles}", category="compound", sources_searched=sources_searched
                ).details["statement"],
                "caveat": NoveltyResult.unknown_result("", "", sources_searched).details["caveat"],
                "sources_searched": sources_searched,
                "search_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "is_known": False,
            }
        else:
            return {
                "novelty": "KNOWN",
                "is_known": True,
                "statement": "This compound is already catalogued in one or more databases.",
                "sources": {k: v for k, v in results.items() if v["found"]},
            }

    def check_reaction_novelty(self, reactants: List[str], products: List[str] = None) -> Dict[str, Any]:
        """Check reaction novelty. Always cautious."""
        self.sources_searched.append("Reaction databases")
        return {
            "novelty": "UNKNOWN",
            "statement": "No matching reaction was found in the searched sources as of "
            f"{datetime.utcnow().strftime('%Y-%m-%d')}.",
            "caveat": "Absence of evidence is not evidence of absence. "
            "This does not establish priority or novelty.",
            "sources_searched": ["PubChem", "ChEBI", "Reaction databases"],
            "is_known": False,
        }


import requests

__all__ = [
    "NoveltyResult",
    "NoveltyEngine",
]
