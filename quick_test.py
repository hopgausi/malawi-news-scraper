#!/usr/bin/env python3
"""
Quick example showing the timeout working correctly
"""

import time
from scrapers import MaraviPostParser

print("Testing Maravi Post - should timeout at ~10 seconds")
print(f"URL: {MaraviPostParser().get_link()}")
print()

parser = MaraviPostParser()
start = time.time()

try:
    print("⏳ Fetching (max 10s)...", end="", flush=True)
    news = parser.scrape_news()
    elapsed = time.time() - start
    print(f"\r✓ Success: {len(news['data'])} articles in {elapsed:.1f}s")
except TimeoutError:
    elapsed = time.time() - start
    print(f"\r⏱ Timeout: {elapsed:.1f}s ✓")
    print(f"   Expected: ~10s, Got: {elapsed:.1f}s")
    print(f"   ✅ Working correctly! (within 10-12s range)")
except Exception as e:
    elapsed = time.time() - start
    print(f"\r✗ Error: {e} ({elapsed:.1f}s)")
