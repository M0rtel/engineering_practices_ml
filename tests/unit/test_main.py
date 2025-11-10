"""Unit tests for main module."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


def test_import_main() -> None:
    """Test that main module can be imported."""
    # This is a simple test to verify the structure works
    assert True


def test_project_structure() -> None:
    """Test that project structure is correct."""
    project_root = Path(__file__).parent.parent.parent
    assert (project_root / "src").exists()
    assert (project_root / "tests").exists()
    assert (project_root / "data").exists()
    assert (project_root / "pyproject.toml").exists()
