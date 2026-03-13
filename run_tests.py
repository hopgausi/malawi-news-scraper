#!/usr/bin/env python3
"""
Test runner script for malawi-news-scraper

This script provides a simple interface to run different test suites.
"""
import sys
import subprocess
from pathlib import Path


def run_tests(test_type="unit"):
    """Run tests based on specified type"""

    # Ensure we're in the project root
    project_root = Path(__file__).parent

    test_commands = {
        "unit": ["pytest", "-v", "tests/", "-m", "not integration and not slow"],
        "integration": ["pytest", "-v", "tests/", "--run-integration", "--run-slow"],
        "all": ["pytest", "-v", "tests/", "--run-integration", "--run-slow"],
        "coverage": [
            "pytest",
            "-v",
            "tests/",
            "-m",
            "not integration and not slow",
            "--cov=scrapers",
            "--cov-report=term-missing",
            "--cov-report=html",
        ],
        "quick": [
            "pytest",
            "-v",
            "tests/",
            "-m",
            "not integration and not slow",
            "-x",  # Stop at first failure
        ],
    }

    if test_type not in test_commands:
        print(f"❌ Unknown test type: {test_type}")
        print(f"Available types: {', '.join(test_commands.keys())}")
        return 1

    print(f"🧪 Running {test_type} tests...\n")

    try:
        result = subprocess.run(test_commands[test_type], cwd=project_root, check=False)
        return result.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Install dev dependencies:")
        print("   pip install -e '.[dev]'")
        return 1


def main():
    """Main entry point"""
    test_type = sys.argv[1] if len(sys.argv) > 1 else "unit"

    print("=" * 60)
    print("Malawi News Scraper - Test Runner")
    print("=" * 60)
    print()

    if test_type in ["-h", "--help", "help"]:
        print("Usage: python run_tests.py [test_type]")
        print()
        print("Test types:")
        print("  unit         - Run unit tests only (default)")
        print("  integration  - Run integration tests (makes network calls)")
        print("  all          - Run all tests")
        print("  coverage     - Run unit tests with coverage report")
        print("  quick        - Run unit tests, stop at first failure")
        print()
        print("Examples:")
        print("  python run_tests.py")
        print("  python run_tests.py integration")
        print("  python run_tests.py coverage")
        return 0

    exit_code = run_tests(test_type)

    print()
    print("=" * 60)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 60)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
