#!/bin/bash
# Setup script for test environment

echo "================================================"
echo "Malawi News Scraper - Test Environment Setup"
echo "================================================"
echo ""

# Check if Python 3.11+ is available
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $python_version"

# Check if we're in a virtual environment
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo ""
    echo "⚠️  Warning: Not in a virtual environment"
    echo "   It's recommended to use a virtual environment"
    echo ""
    read -p "   Create virtual environment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
        echo "   Activating virtual environment..."
        source venv/bin/activate
        echo "   ✅ Virtual environment created and activated"
    fi
fi

echo ""
echo "📦 Installing package in development mode..."
pip install -e '.[dev]'

if [ $? -eq 0 ]; then
    echo "   ✅ Installation successful"
else
    echo "   ❌ Installation failed"
    exit 1
fi

echo ""
echo "🧪 Running quick test to verify setup..."
python -c "
import sys
try:
    import scrapers
    import pytest
    print('   ✅ All imports successful')
    sys.exit(0)
except ImportError as e:
    print(f'   ❌ Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "✅ Test environment setup complete!"
    echo "================================================"
    echo ""
    echo "Quick Start:"
    echo "  • Run unit tests:        python run_tests.py"
    echo "  • Run with coverage:     python run_tests.py coverage"
    echo "  • Run integration tests: python run_tests.py integration"
    echo "  • Get help:              python run_tests.py --help"
    echo ""
    echo "Or use pytest directly:"
    echo "  • pytest -v tests/"
    echo "  • pytest --run-integration"
    echo ""
    echo "See TESTING.md for detailed documentation"
    echo ""
else
    echo ""
    echo "❌ Setup verification failed"
    exit 1
fi
