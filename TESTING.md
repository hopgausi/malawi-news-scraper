# Testing Guide

## Setup Testing Environment

### 1. Install Development Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e '.[dev]'
```

This installs:

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `isort` - Import sorting
- `bumpver` - Version bumping

### 2. Verify Installation

```bash
pytest --version
```

## Running Tests

### Quick Start

Use the test runner script:

```bash
# Run unit tests (default, fast, no network calls)
python run_tests.py

# Run with coverage report
python run_tests.py coverage

# Run integration tests (makes real network calls)
python run_tests.py integration

# Run all tests
python run_tests.py all

# Quick run (stop at first failure)
python run_tests.py quick
```

### Using pytest Directly

```bash
# Run all unit tests (skips integration)
pytest -v tests/

# Run specific test file
pytest -v tests/test_base_feed_scraper.py

# Run specific test
pytest -v tests/test_parsers.py::TestMalawiVoiceParser::test_get_link

# Run with coverage
pytest --cov=scrapers --cov-report=term-missing

# Run integration tests
pytest --run-integration --run-slow

# Run tests matching a pattern
pytest -k "test_get_link"

# Stop at first failure
pytest -x
```

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_base_feed_scraper.py # Unit tests for BaseFeedScraper
├── test_parsers.py          # Unit tests for parser classes
└── test_integration.py      # Integration tests (network calls)
```

## Test Types

### Unit Tests

- **Fast** - No network calls
- **Isolated** - Test individual components
- **Default** - Run by default with `pytest`

Files:

- `test_base_feed_scraper.py`
- `test_parsers.py`

### Integration Tests

- **Slow** - Makes real network requests
- **End-to-end** - Tests actual RSS feed scraping
- **Manual** - Requires `--run-integration` flag

File:

- `test_integration.py`

## Coverage Reports

Generate coverage report:

```bash
# Terminal report
pytest --cov=scrapers --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=scrapers --cov-report=html
open htmlcov/index.html  # On macOS
xdg-open htmlcov/index.html  # On Linux
```

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Run unit tests only (fast)
pytest -v tests/ -m "not integration and not slow"

# Run all tests (slower)
pytest -v tests/ --run-integration --run-slow
```

## Writing New Tests

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test

```python
import pytest
from scrapers import MalawiVoiceParser

class TestMalawiVoice:
    """Test suite for Malawi Voice scraper"""

    def test_parser_initialization(self):
        """Test that parser initializes correctly"""
        parser = MalawiVoiceParser()
        assert parser.link is not None

    @pytest.mark.slow
    def test_scrape_real_feed(self):
        """Test scraping real RSS feed"""
        parser = MalawiVoiceParser()
        result = parser.scrape_news()
        assert len(result['data']) > 0
```

### Using Markers

```python
# Mark as integration test
@pytest.mark.integration
def test_with_network():
    pass

# Mark as slow test
@pytest.mark.slow
def test_slow_operation():
    pass
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed:

```bash
pip install -e .
```

### Network Errors in Integration Tests

Integration tests require internet connection and may fail if:

- News sites are down
- Network is unavailable
- RSS feeds have changed structure

Run without integration tests:

```bash
pytest -v tests/ -m "not integration"
```

### Coverage Not Working

Install coverage:

```bash
pip install pytest-cov
```

## Best Practices

1. **Run unit tests frequently** during development
2. **Run integration tests** before commits/PRs
3. **Check coverage** to ensure good test coverage
4. **Keep tests fast** - use mocks for external dependencies
5. **Keep integration tests separate** - mark with `@pytest.mark.integration`

## Common Commands Cheat Sheet

```bash
# Quick test
pytest

# Verbose output
pytest -v

# Stop at first failure
pytest -x

# Run specific test
pytest tests/test_parsers.py::TestMalawiVoiceParser

# Run tests matching pattern
pytest -k "voice"

# Show print statements
pytest -s

# Run only integration tests
pytest --run-integration

# Coverage report
pytest --cov=scrapers --cov-report=html
```
