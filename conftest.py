"""Root pytest configuration.

The Zenodo deposits ship byte-copies of the laboratory's test files so that a
reader can inspect exactly what was run. Those copies are **reference material,
not runnable tests**: they import from laboratory-relative paths that do not exist
inside the packaged form, so collecting them always fails.

There are two deposits and both must be excluded:

  ``zenodo/``          the laboratory's own staging copy
  ``zenodo-deposit/``  the curated v1.0.0 deposit preserved at the repository root

``norecursedirs`` in ``pytest.ini`` is *not* sufficient on its own here, and this
file already said so before ``zenodo-deposit/`` existed. Both mechanisms are kept:
``norecursedirs`` covers the directory walk, and this ``collect_ignore_glob``
covers pytest's explicit collection path. Dropping either one lets four
collection errors back in, which is how the omission was found -- on CI, not
locally, because the laboratory tree has no ``zenodo-deposit/`` directory.

The authoritative tests remain the ones under the investigation directories and
``tests/``; the packaged copies are hash-checked by
``tools/verify_deposit_manifest.py`` and ``zenodo/verify_historical_integrity.py``
against the originals.
"""
from __future__ import annotations

collect_ignore_glob = [
    "zenodo/*",
    "zenodo/**",
    "zenodo-deposit/*",
    "zenodo-deposit/**",
    "*/__pycache__/*",
    "**/package/tests_reference/*",
]