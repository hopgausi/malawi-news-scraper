# malawi-news-scraper

Scrape news from known news outlets in Malawi with built-in timeout and error handling.

## Features

- ✅ Scrapes from 5 major Malawi news sources
- ⏱️ 10-second timeout per source (prevents hanging)
- 🛡️ Graceful error handling (one failure won't crash the scraper)
- 📊 Support for multiple parsers
- 🔄 Continues with other sources if one fails

## Supported News Sources

- Malawi Voice
- Malawi24
- Maravi Post
- MW Nation
- Platform for Investigative Journalism (PIJ)

**Note:** PIJ uses custom HTML scraping instead of RSS feed parsing due to broken links in their RSS feed. See [PIJ_HTML_SCRAPER.md](PIJ_HTML_SCRAPER.md) for details.

## Installation

```bash
pip install malawi-news-scraper
```

Or from source:

```bash
git clone https://github.com/hopgausi/malawi-news-scraper
cd malawi-news-scraper
pip install -e .
```

## Quick Start

```python
from scrapers import MalawiVoiceParser

# Scrape from a single source
parser = MalawiVoiceParser()
try:
    news_data = parser.scrape_news()
    print(f"Found {len(news_data['data'])} articles")
except TimeoutError:
    print("Request timed out after 10 seconds")
except Exception as e:
    print(f"Error: {e}")
```

## Timeout & Error Handling

The scraper automatically handles:

- **Timeouts**: Each request has a 10-second timeout enforced at the **socket level**
- **Connection errors**: Network issues are caught and reported
- **Invalid feeds**: Malformed RSS feeds won't crash the scraper
- **Graceful degradation**: If one source fails, others continue

**Socket-Level Timeout:** The timeout is enforced at the network socket level, which means slow servers are interrupted after exactly 10 seconds and won't hang your application.

### Verification

Test the timeout with a slow source:

```bash
python test_timeout_verify.py
```

Expected: ~10.7 seconds (10s timeout + 0.7s overhead)

```python
from scrapers import (
    MalawiVoiceParser,
    Malawi24Parser,
    MaraviPostParser
)

parsers = [MalawiVoiceParser(), Malawi24Parser(), MaraviPostParser()]

for parser in parsers:
    try:
        news = parser.scrape_news()
        print(f"✓ Scraped {len(news['data'])} articles")
    except TimeoutError:
        print("⏱ Timeout - took too long")
    except Exception as e:
        print(f"✗ Failed: {e}")
```

## Examples

See the examples:

```bash
# Basic usage examples
python examples.py

# Timeout and error handling demo
python demo_timeout.py
```

## Development

```bash
# Install dev dependencies
pip install -e '.[dev]'

# Run tests
python run_tests.py

# Run with coverage
python run_tests.py coverage
```

See [TESTING.md](TESTING.md) for detailed testing documentation.
