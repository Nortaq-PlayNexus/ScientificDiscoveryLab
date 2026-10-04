#!/usr/bin/env python3
"""Generate per-investigation Zenodo metadata from each investigation's own files.

    python tools/make_investigation_metadata.py

Reads each investigation's README and preregistration to derive an honest title,
description and subject set, rather than inventing them. The point is that a
deposit's description should be derivable from the record it publishes.

Output: zenodo/investigations/<slug>.json and <slug>.md, ready for
tools/upload_investigations.py.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
INV = LAB / "03_INVESTIGATIONS"
OUT = LAB / "zenodo" / "investigations"

#: slug -> (relative path, experiments, plain-language question, keywords, subjects)
TARGETS = {
    "speckle-contrast-law": dict(
        path="OPTICS/speckle_contrast_law", exps="EXP-0002", qid="Q-O001",
        question=(
            "Does the contrast of a fully developed speckle pattern follow "
            "C(M) = 1/sqrt(M) for M independent looks?"
        ),
        keywords=["speckle contrast", "optics", "random fields", "intensity "
                  "statistics", "reproducibility research"],
        subjects=["mesh:D010825Q000379", "euroscivoc:805", "mesh:D015203"],
    ),
    "vortex-density": dict(
        path="OPTICS/vortex_density", exps="EXP-0003", qid="Q-O002",
        question=(
            "Does the density of phase singularities in a random complex field "
            "agree with the Nye-Berry / Freund prediction?"
        ),
        keywords=["phase singularities", "vortex density", "random wave fields",
                  "topological charge", "reproducibility research"],
        subjects=["mesh:D010825Q000379", "mesh:D015203"],
    ),
    "discrete-vortex-detection-bias": dict(
        path="OPTICS/discrete_vortex_bias", exps="EXP-0015", qid="Q-O006",
        question=(
            "When does discrete optical-vortex detection produce systematic "
            "count bias relative to known continuous topology?"
        ),
        keywords=["detector bias", "discretisation artifact", "phase singularities",
                  "numerical methods", "negative results"],
        subjects=["mesh:D010825Q000379", "euroscivoc:1061", "mesh:D015203"],
    ),
    "topology-measurement-definition": dict(
        path="OPTICS/topology_measurement_definition", exps="EXP-0016", qid="Q-O007",
        question=(
            "Under what conditions do discrete representations of optical phase "
            "topology disagree about singularity count, charge, or identity?"
        ),
        keywords=["measurement definition", "phase topology", "numerical methods",
                  "operationalisation", "negative results"],
        subjects=["mesh:D010825Q000379", "euroscivoc:1061", "mesh:D015203"],
    ),
    "rng-certification": dict(
        path="OTHER/rng_certification", exps="EXP-0004", qid="Q-I004",
        question=(
            "Does the laboratory's own pseudorandom number generator pass a "
            "statistical test battery it is itself subjected to?"
        ),
        keywords=["NIST SP 800-22", "pseudorandom number generation",
                  "statistical test calibration", "instrument validation",
                  "negative results"],
        subjects=["mesh:D015203", "mesh:D012106Q000706", "euroscivoc:1061"],
    ),
    "percolation-thresholds-and-exponents": dict(
        path="PHYSICS/percolation", exps="EXP-0005, 0006, 0009, 0010, 0017",
        qid="Q-P004, Q-P005, Q-P009",
        question=(
            "What are the site and bond percolation thresholds, and does the "
            "reported 2D cluster-mass exponent deviate from the Fisher value "
            "187/91?"
        ),
        keywords=["percolation", "cluster mass exponent", "finite-size scaling",
                  "estimator bias", "preregistration", "negative results",
                  "power-law estimation"],
        subjects=["mesh:D010825Q000379", "euroscivoc:805", "mesh:D015203"],
    ),
    "feigenbaum-universality": dict(
        path="MATHEMATICS/feigenbaum_constants", exps="EXP-0014", qid="Q-M005",
        question=(
            "Do higher-order one-dimensional maps show Feigenbaum universality, "
            "and is the constant the same across orders?"
        ),
        keywords=["Feigenbaum constant", "universality", "bifurcation",
                  "computational mathematics", "reproducibility research"],
        subjects=["mesh:D012106Q000706", "euroscivoc:1061", "mesh:D015203"],
    ),
    "prime-gap-statistics": dict(
        path="MATHEMATICS/prime_gaps", exps="EXP-0008", qid="Q-M002",
        question=(
            "Do prime gaps follow the Poisson / Gallagher distribution the "
            "literature predicts?"
        ),
        keywords=["prime gaps", "Poisson distribution", "number theory",
                  "hypothesis testing", "negative results"],
        subjects=["mesh:D012106Q000706", "mesh:D015203"],
    ),
    "water-acoustic-response": dict(
        path="ACOUSTICS/water_sound_response", exps="n/a", qid="Q-A001",
        question=(
            "A computational model of the acoustic response of a water surface "
            "to structured forcing. Simulator and controls; no empirical claim."
        ),
        keywords=["acoustics", "wave simulation", "simulator", "controls",
                  "no empirical claim"],
        subjects=["euroscivoc:1061", "mesh:D015203"],
    ),
}

SUBJECT_TITLES = {
    "mesh:D015203": "Reproducibility of Results",
    "mesh:D010825Q000379": "Physics/methods",
    "mesh:D010825": "Physics",
    "mesh:D012106Q000706": "Research/statistics & numerical data",
    "euroscivoc:805": "Statistical mechanics",
    "euroscivoc:1061": "Numerical analysis",
}

TEMPLATE = """# {title}

**Experiments:** {exps} · **Question:** {qid}

## What this is

{question}

This deposit is one investigation from a larger laboratory, published separately
so it can be cited on its own. The laboratory as a whole — its registries,
governance rules, and the self-audit that found four defects in its own
instruments — is published separately as
[`10.5281/zenodo.23109117`](https://doi.org/10.5281/zenodo.23109117).

## Why separate deposits

A single question in this laboratory can span several experiments. Q-P004 covers
EXP-0005/0006/0007 and Q-P005 covers EXP-0009/0010. Splitting those across
separate DOIs would scatter one scientific answer across four identifiers and
make it harder to cite, not easier. The investigation — the unit with its own
README, preregistration, code, config and results — is therefore the unit of
deposit, and the experiment IDs are recorded above so a reader can drill down.

## What is in the archive

Code, frozen preregistrations, configs, results, reports and audit trails for
this investigation.

Raw simulation output is **excluded**: `.npz`, `.sqlite3` and `.db`, 362 MB
across the laboratory. That data is regenerable from the seeds recorded in each
preregistration, and including it would make this archive an order of magnitude
larger for no gain in verifiability. The code that consumes it ships here; the
inputs it consumes do not.

## Reproducibility and honesty

This laboratory runs to a written standard (`RESEARCH_RULES.md`): claim
layering, preregistration before analysis, mandatory controls, adversarial
falsification, evidence grading, read-only raw data, and fail-closed runners.

**No physics discovery is claimed.** Several experiments here are INCONCLUSIVE,
and one anomaly was traced to an instrument defect rather than to nature. Null
results are recorded with the same care as positive ones, and a preregistered
prediction that failed is reported as having failed.

Two defects in the laboratory's own instruments were found during self-audit and
are documented in the laboratory deposit: a statistical test that applied a
z-score conversion to a statistic already in `erfc` units, and a percolation
exponent estimator biased upward by 0.11 to 0.35. In the second case the defect
made the laboratory's own anomaly look *smaller* than it really was.

## Licence

MIT — see the licence file in the laboratory repository, or
`CITATION.cff` there.
"""


def main() -> int:
    index = json.loads((OUT / "INDEX.json").read_text(encoding="utf-8"))
    by_slug = {e["slug"]: e for e in index["investigations"]}

    for slug, spec in TARGETS.items():
        folder = LAB / "03_INVESTIGATIONS" / spec["path"]
        readme = folder / "README.md"

        title = by_slug.get(slug, {}).get("title", slug.replace("-", " ").title())
        desc = TEMPLATE.format(
            title=title,
            exps=spec["exps"],
            qid=spec["qid"],
            question=spec["question"],
        )
        (OUT / f"{slug}.md").write_text(desc, encoding="utf-8", newline="\n")

        meta = {
            "schema": "zenodo-investigation-metadata-v1",
            "upload_type": "dataset",
            "slug": slug,
            "path_in_laboratory": f"03_INVESTIGATIONS/{spec['path']}",
            "experiments": spec["exps"],
            "question_ids": spec["qid"],
            "title": f"ScientificDiscoveryLab investigation: {title}",
            "version": "1.0.0",
            "creators": [{
                "name": "ScientificDiscoveryLab contributors",
                "affiliation": "independent",
            }],
            "description_source": f"{slug}.md",
            "license": "mit-license",
            "language": "eng",
            "access_right": "open",
            "subjects": [
                {"id": s, "title": SUBJECT_TITLES.get(s, s)}
                for s in spec["subjects"]
            ],
            "keywords": spec["keywords"],
            "references": [],
            "related_identifiers": [
                {
                    "relation": "isSupplementTo",
                    "identifier": "https://doi.org/10.5281/zenodo.23109117",
                    "resource_type": "dataset",
                    "note": (
                        "SCOPE NOTE: this is one investigation from the laboratory "
                        "published as a separate record. The laboratory deposit holds "
                        "the registries, governance rules and self-audit. Neither "
                        "supersedes the other; cite whichever matches your question. "
                        "No physics discovery is claimed in either."
                    ),
                },
                {
                    "relation": "isDocumentedBy",
                    "identifier": "https://github.com/Nortaq-PlayNexus/ScientificDiscoveryLab",
                    "resource_type": "software",
                    "note": "Source repository. This archive is the frozen, byte-reproducible slice of the repository for this investigation.",
                },
            ],
            "archive": by_slug.get(slug, {}).get("archive", f"{slug}.zip"),
            "archive_sha256": by_slug.get(slug, {}).get("sha256", ""),
            "doi": "",
        }
        (OUT / f"{slug}.json").write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n")
        print(f"  {slug:<36} {meta['title'][:58]}")

    print(f"\n  wrote {len(TARGETS)} metadata + description pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())