"""Pytest configuration and fixtures."""

import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator

import pytest


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def sample_diff() -> str:
    """Return a sample git diff for testing."""
    return """diff --git a/README.md b/README.md
index 1234567..89abcde 100644
--- a/README.md
+++ b/README.md
@@ -1,5 +1,8 @@
 # Project
 
+## New Feature
+Added a new feature to the project.
+
 ## Installation
 Run `pip install -e .`
 """


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create and cleanup a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Return a sample configuration dictionary."""
    return {
        "ai": {
            "model_name": "gpt-4-turbo-preview",
            "temperature": 0.3,
            "max_tokens": 500,
        },
        "commit": {
            "require_ticket": True,
            "default_commit_type": "IMPROVE",
            "default_severity": "MEDIUM",
            "max_line_length": 72,
        },
    }
