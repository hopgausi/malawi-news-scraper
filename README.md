# Malawi News Scraper

A Python library for scraping news articles from major Malawian news outlets. Get the latest news from multiple sources with a simple API, built-in timeout handling, and robust error management.

## What is this?

This library allows you to programmatically fetch news articles from 5 major Malawian news sources. Whether you're building a news aggregator, conducting media analysis, or just want to stay informed about Malawi, this scraper makes it easy to collect news data from multiple sources.

## Features

- 📰 **5 News Sources** - Scrapes from Malawi Voice, Malawi24, Maravi Post, MW Nation, and PIJ
- 🚀 **Simple API** - Just import a parser and call `scrape_news()`
- ⏱️ **Smart Timeouts** - 10-second timeout per source prevents hanging
- 🛡️ **Error Handling** - Gracefully handles network errors, timeouts, and malformed feeds
- 🔄 **Continues on Failure** - One failed source won't stop the others
- 📊 **Structured Data** - Returns clean, structured article data (title, author, date, link, image)

## Supported News Sources

| Source           | URL             | Notes                             |
| ---------------- | --------------- | --------------------------------- |
| **Malawi Voice** | malawivoice.com | RSS feed                          |
| **Malawi24**     | malawi24.com    | RSS feed                          |
| **Maravi Post**  | maravipost.com  | HTML scraping (CAPTCHA protected) |
| **MW Nation**    | mwnation.com    | RSS feed                          |
| **PIJ**          | pijmalawi.org   | HTML scraping                     |

**Note:** Maravi Post's website uses CAPTCHA protection which may prevent scraping. When CAPTCHA is encountered, the scraper returns an empty list with a warning message.

## Installation

```bash
pip install malawi-news-scraper
```

Or install from source:

```bash
git clone https://github.com/hopgausi/malawi-news-scraper
cd malawi-news-scraper
pip install -e .
```

## Quick Start

### Scrape from a Single Source

```python
from scrapers import MalawiVoiceParser

# Create parser instance
parser = MalawiVoiceParser()

# Scrape news
try:
    result = parser.scrape_news()

    # Access articles
    articles = result['data']
    source_info = result['source']

    print(f"Source: {source_info['name']}")
    print(f"Found {len(articles)} articles\n")

    # Display first article
    article = articles[0]
    print(f"Title: {article['title']}")
    print(f"Author: {article['author']}")
    print(f"Date: {article['published_date']}")
    print(f"Link: {article['link']}")

except TimeoutError:
    print("Request timed out after 10 seconds")
except Exception as e:
    print(f"Error: {e}")
```

### Scrape from All Sources

```python
from scrapers import (
    MalawiVoiceParser,
    Malawi24Parser,
    MaraviPostParser,
    MwNationParser,
    PijParser
)

# Create all parsers
parsers = {
    'Malawi Voice': MalawiVoiceParser(),
    'Malawi24': Malawi24Parser(),
    'Maravi Post': MaraviPostParser(),
    'MW Nation': MwNationParser(),
    'PIJ': PijParser()
}

# Scrape all sources
all_articles = []

for name, parser in parsers.items():
    try:
        result = parser.scrape_news()
        articles = result['data']

        print(f"✓ {name}: {len(articles)} articles")
        all_articles.extend(articles)

    except TimeoutError:
        print(f"⏱ {name}: Timeout")
    except Exception as e:
        print(f"✗ {name}: {e}")

print(f"\nTotal articles collected: {len(all_articles)}")
```

## Usage Examples

### Get Article Details

Each article contains:

```python
article = {
    'title': 'Article headline',
    'author': 'Author name or source name',
    'published_date': 'Publication date',
    'link': 'Full article URL',
    'cover_image': 'Cover image URL (if available)'
}
```

### Filter Recent Articles

```python
from datetime import datetime, timedelta

parser = MalawiVoiceParser()
result = parser.scrape_news()

# Filter articles from last 24 hours
yesterday = datetime.now() - timedelta(days=1)

for article in result['data']:
    pub_date = article['published_date']
    # Add your date parsing logic here
    print(f"{article['title']} - {pub_date}")
```

### Custom Timeout

```python
from scrapers import MalawiVoiceParser

# Default timeout is 10 seconds
parser = MalawiVoiceParser()

# Set custom timeout (in seconds)
parser.timeout = 20

result = parser.scrape_news()
```

## Error Handling

The scraper handles common issues automatically:

- **Timeouts**: Requests that take longer than 10 seconds are automatically cancelled
- **Network Errors**: Connection failures are caught and reported as exceptions
- **Invalid Data**: Missing or malformed fields won't crash the scraper
- **Dead Links**: Some sources are detected and handled gracefully

### Recommended Error Handling Pattern

```python
from scrapers import MalawiVoiceParser

parser = MalawiVoiceParser()

try:
    result = parser.scrape_news()
    # Process articles...

except TimeoutError:
    print("The request took too long (>10 seconds)")

except ConnectionError:
    print("Could not connect to the news source")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## Interactive Demo

Try the interactive examples script:

```bash
python examples.py
```

This will let you:

1. Choose a specific news source to scrape
2. See all sources scraped at once
3. View the most recent articles across all sources

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/hopgausi/malawi-news-scraper
cd malawi-news-scraper

# Install in development mode
pip install -e '.[dev]'
```

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run with coverage report
python run_tests.py coverage
```

### Project Structure

```
malawi-news-scraper/
├── src/scrapers/          # Main package
│   ├── base_feed_scraper.py    # Base RSS scraper
│   ├── base_parser.py          # Abstract parser class
│   ├── malawi_voice.py         # Malawi Voice parser
│   ├── malawi24.py             # Malawi24 parser
│   ├── maravi_post.py          # Maravi Post parser
│   ├── mwnation.py             # MW Nation parser
│   ├── pij.py                  # PIJ parser (HTML)
│   └── config.toml             # RSS feed URLs
├── tests/                 # Unit tests
├── examples.py            # Interactive demo
└── run_tests.py          # Test runner
```

## Requirements

- Python 3.11+
- feedparser
- beautifulsoup4
- html2text

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

**Issue**: All sources timeout  
**Solution**: Check your internet connection. Some sources may be temporarily down.

**Issue**: Maravi Post returns no articles with CAPTCHA warning  
**Solution**: The Maravi Post website uses CAPTCHA protection to prevent automated scraping. This is a site-level restriction and cannot be bypassed by the scraper. The scraper will detect this and return an empty list with a warning message.

**Issue**: PIJ returns no articles  
**Solution**: The PIJ website structure may have changed. The scraper uses HTML parsing which depends on the site's structure.

**Issue**: Articles have "Unknown" author  
**Solution**: Some sources don't include author information in their feeds. The scraper defaults to "Unknown" in these cases.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/hopgausi/malawi-news-scraper).
