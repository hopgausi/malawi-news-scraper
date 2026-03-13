"""Pytest configuration and fixtures"""

import pytest


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (makes real network calls)",
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running (fetches live data)"
    )


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="run integration tests that make real network calls",
    )
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="run slow tests that fetch live data",
    )


def pytest_collection_modifyitems(config, items):
    """Skip integration and slow tests unless explicitly requested"""
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(
            reason="need --run-integration option to run"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
