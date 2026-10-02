"""Root pytest configuration.

The Zenodo deposit under ``zenodo/package/`` ships byte-copies of the
laboratory's test files so that a reader can inspect exactly what was run.
Those copies are **reference material, not runnable tests**: they import from
laboratory-relative paths that do not exist inside the packaged deposit, so
collection of them always fails.

``norecursedirs`` in ``pytest.ini`` did not reliably exclude them, so the
exclusion is stated here in pytest's explicit collect-ignore mechanism instead.
The authoritative tests remain the ones under the investigation directories and
``tests/``; the packaged copies are hash-checked by
``zenodo/verify_historical_integrity.py`` against the originals.
"""
from __future__ import annotations

collect_ignore_glob = [
    "zenodo/*",
    "zenodo/**",
    "*/__pycache__/*",
    "**/package/tests_reference/*",
]
