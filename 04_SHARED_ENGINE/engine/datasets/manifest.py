"""datasets.manifest — dataset provenance (sha256 manifests for 05_DATA)."""

from __future__ import annotations

import json
import os

from ..utilities.core import sha256_file


def manifest_directory(root: str, out_path: str | None = None) -> dict:
    """Hash every file under root (recursive), write/sha the manifest.

    Raw data is immutable; this manifest is how the lab proves its inputs
    did not change (REPRODUCIBILITY.md / RESEARCH_RULES.md section 11).
    """
    root = os.path.abspath(root)
    entries = {}
    for dirpath, _, files in os.walk(root):
        for name in sorted(files):
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            entries[rel] = sha256_file(path)
    manifest = {"root": root, "entries": entries}
    if out_path is not None:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, sort_keys=True)
    return manifest