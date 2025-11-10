"""Main entry point for the data science project."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def main() -> None:
    """Main function."""
    print("Engineering Practices ML Project")
    print("Data Science project with modern engineering practices")


if __name__ == "__main__":
    main()
