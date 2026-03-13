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
echo "   Installing with dev and selenium dependencies..."
pip install -e '.[dev,selenium]'

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
    import selenium
    from webdriver_manager.firefox import GeckoDriverManager
    print('   ✅ All imports successful (including selenium)')
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
    echo "📦 Installed packages:"
    echo "  • Core dependencies (feedparser, beautifulsoup4, etc.)"
    echo "  • Dev dependencies (pytest, coverage, etc.)"
    echo "  • Selenium dependencies (for Maravi Post scraping)"
    echo ""
    echo "⚠️  Note: Chrome/Chromium or Firefox browser required for Selenium"
    echo "   Chrome (recommended): sudo apt-get install chromium-browser"
    echo "   Firefox (fallback): sudo apt-get install firefox"
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
    echo "See README.md for documentation"
    echo ""
else
    echo ""
    echo "❌ Setup verification failed"
    exit 1
fi
