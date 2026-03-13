# Timeout & Error Handling Guide

## Overview

The Malawi News Scraper includes robust timeout and error handling to ensure reliability when scraping news from multiple sources.

**Important:** The timeout is enforced at the **socket level**, which means network operations will be interrupted after exactly 10 seconds, preventing hanging connections even on slow or unresponsive servers.

## How It Works

The scraper uses **socket-level timeout** via `socket.setdefaulttimeout()`:

1. Before making a request, the socket timeout is set to 10 seconds
2. If the server doesn't respond within 10 seconds, the connection is terminated
3. A `TimeoutError` is raised, allowing the scraper to continue with other sources
4. The original timeout is restored after the request completes

This is more reliable than application-level timeouts because it interrupts the actual network operations.

## Features

### ⏱️ Automatic Timeout (10 seconds)

Every request to a news source automatically times out after **10 seconds**. This prevents:

- Hanging connections
- Slow/unresponsive servers blocking your application
- Indefinite waiting

### 🛡️ Graceful Error Handling

If one source fails:

- ✅ The scraper marks it as failed
- ✅ Continues with remaining sources
- ✅ Returns data from successful sources
- ✅ Your application doesn't crash

## Usage Examples

### Single Source with Timeout Handling

```python
from scrapers import MalawiVoiceParser

parser = MalawiVoiceParser()

try:
    news_data = parser.scrape_news()
    articles = news_data['data']
    print(f"✓ Scraped {len(articles)} articles")

except TimeoutError:
    print("⏱ Request timed out after 10 seconds")
    print("   The server may be slow or unreachable")

except Exception as e:
    print(f"✗ Failed to scrape: {e}")
```

### Multiple Sources with Error Handling

```python
from scrapers import (
    MalawiVoiceParser,
    Malawi24Parser,
    MaraviPostParser,
    MwNationParser,
    PijParser
)

parsers = [
    ("Malawi Voice", MalawiVoiceParser()),
    ("Malawi24", Malawi24Parser()),
    ("Maravi Post", MaraviPostParser()),
    ("MW Nation", MwNationParser()),
    ("PIJ", PijParser())
]

successful = []
failed = []
timeout = []

for name, parser in parsers:
    try:
        news = parser.scrape_news()
        successful.append((name, len(news['data'])))
        print(f"✓ {name}: {len(news['data'])} articles")

    except TimeoutError:
        timeout.append(name)
        print(f"⏱ {name}: Timeout (>10s)")

    except Exception as e:
        failed.append((name, str(e)))
        print(f"✗ {name}: {type(e).__name__}")

print(f"\nResults: {len(successful)} successful, {len(timeout)} timeout, {len(failed)} failed")
```

## Error Types

### TimeoutError

**Cause**: Request took longer than 10 seconds  
**Action**: The source may be slow or down. Continue with other sources.

```python
except TimeoutError:
    print("Source is taking too long, skipping...")
```

### Connection Errors

**Cause**: Network issues, DNS problems, server down  
**Action**: Log the error and continue with other sources.

```python
except Exception as e:
    print(f"Connection error: {type(e).__name__}")
```

### Feed Parsing Errors

**Cause**: Invalid RSS/XML format, unexpected structure  
**Action**: Log the error, notify about the source issue.

## Customizing Timeout

You can customize the timeout if needed:

```python
from scrapers import MalawiVoiceParser

parser = MalawiVoiceParser()
parser.timeout = 15  # Set to 15 seconds

news = parser.scrape_news()
```

## Best Practices

### 1. Always Handle TimeoutError Separately

```python
try:
    news = parser.scrape_news()
except TimeoutError:
    # Specific handling for timeouts
    log_timeout(source_name)
except Exception as e:
    # Handle other errors
    log_error(source_name, e)
```

### 2. Use Progress Indicators

```python
for name, parser in parsers:
    print(f"⏳ Fetching {name}...", end="", flush=True)
    try:
        news = parser.scrape_news()
        print(f"\r✓ {name}: {len(news['data'])} articles")
    except TimeoutError:
        print(f"\r⏱ {name}: Timeout")
```

### 3. Collect Partial Results

```python
all_articles = []
for parser in parsers:
    try:
        news = parser.scrape_news()
        all_articles.extend(news['data'])
    except (TimeoutError, Exception):
        pass  # Continue collecting from other sources

print(f"Collected {len(all_articles)} articles total")
```

### 4. Log Failures for Monitoring

```python
import logging

for name, parser in parsers:
    try:
        news = parser.scrape_news()
    except TimeoutError:
        logging.warning(f"{name} timed out after 10 seconds")
    except Exception as e:
        logging.error(f"{name} failed: {e}")
```

## Testing Timeout Behavior

Run the demo script to see timeout handling in action:

```bash
python demo_timeout.py
```

This demonstrates:

- ✅ Successful scrapes
- ⏱️ Timeout handling
- ❌ Error handling
- 📊 Summary statistics

## Production Considerations

### 1. Implement Retry Logic

```python
def scrape_with_retry(parser, max_retries=2):
    for attempt in range(max_retries):
        try:
            return parser.scrape_news()
        except TimeoutError:
            if attempt < max_retries - 1:
                time.sleep(2)  # Wait before retry
                continue
            raise
```

### 2. Monitor Timeout Rates

Track which sources frequently timeout to identify issues:

```python
timeout_counts = {}
for name, parser in parsers:
    try:
        parser.scrape_news()
    except TimeoutError:
        timeout_counts[name] = timeout_counts.get(name, 0) + 1
```

### 3. Adjust Timeout Based on Source

```python
# Some sources may need longer timeouts
slow_sources = ["MW Nation"]
for name, parser in parsers:
    if name in slow_sources:
        parser.timeout = 20
```

## Verifying Timeout Behavior

### Quick Verification Test

Run the timeout verification script to test a specific slow source:

```bash
python test_timeout_verify.py
```

This tests Maravi Post (which was previously taking 71 seconds before timing out) and verifies it now times out at ~10 seconds.

**Expected Output:**

```
✓ Timeout working correctly: 10.7s ≤ 12s
  (10s timeout + ~0.7s overhead)
```

### Full Demo

Run the complete demo to see timeout handling across all sources:

```bash
python demo_timeout.py
```

This shows:

- ✓ Successful scrapes with timing
- ⏱ Timeouts (sources that took >10s)
- ✗ Failed sources (connection errors, etc.)

### Expected Behavior

When a source times out:

- **Actual timeout**: ~10-11 seconds (10s + small overhead)
- **Error type**: `TimeoutError`
- **Scraper behavior**: Marks as timeout, continues with next source
- **No hanging**: Process never waits more than ~11 seconds per source

## FAQ

**Q: Why 10 seconds?**  
A: 10 seconds is typically enough for RSS feeds but prevents hanging on slow/dead servers. Testing shows this works well in practice.

**Q: How is the timeout enforced?**  
A: At the **socket level** using `socket.setdefaulttimeout()`. This interrupts network operations directly, unlike application-level timeouts that only wait but don't stop the underlying request.

**Q: Can I disable timeout?**  
A: Not recommended, but you can set a very high value: `parser.timeout = 9999`

**Q: What if all sources timeout?**  
A: Check your internet connection or the news sites may be experiencing issues. Run `python test_timeout_verify.py` to diagnose specific sources.

**Q: Does timeout affect cached results?**  
A: No, cached results (from `@cache` decorator) return immediately without network calls.

**Q: Why does timeout show as 10.7s instead of exactly 10s?**  
A: The 10s is the network socket timeout. The extra ~0.7s is Python overhead (function calls, exception handling, etc.). This is normal and acceptable.

## Related

- See [examples.py](examples.py) for basic usage
- See [demo_timeout.py](demo_timeout.py) for timeout demo
- See [TESTING.md](TESTING.md) for testing documentation
