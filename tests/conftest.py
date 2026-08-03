"""Test configuration and fixtures."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        yield db_path
