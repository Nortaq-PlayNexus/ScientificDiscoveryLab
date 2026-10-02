"""Pytest process isolation for persistent laboratory services."""

import atexit
import os
import shutil
import tempfile
from pathlib import Path

_TEST_STATE = Path(tempfile.mkdtemp(prefix="scientific-discovery-lab-pytest-"))
_TEST_DB = _TEST_STATE / f"pytest_science_{os.getpid()}.db"
_PREVIOUS_DATABASE_URL = os.environ.get("SOVEREIGN_BIOLAB_DATABASE_URL")

# This assignment happens during conftest import, before test modules import the
# database layer. Tests therefore cannot touch the laboratory's persistent DB.
os.environ["SOVEREIGN_BIOLAB_DATABASE_URL"] = f"sqlite:///{_TEST_DB.as_posix()}"


def _cleanup() -> None:
    if _PREVIOUS_DATABASE_URL is None:
        os.environ.pop("SOVEREIGN_BIOLAB_DATABASE_URL", None)
    else:
        os.environ["SOVEREIGN_BIOLAB_DATABASE_URL"] = _PREVIOUS_DATABASE_URL
    shutil.rmtree(_TEST_STATE, ignore_errors=True)


atexit.register(_cleanup)
