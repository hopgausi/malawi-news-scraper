#!/usr/bin/env python3
"""Quick test to see if Chrome works with the new flags."""

import sys

sys.path.insert(0, "src")

from scrapers.maravi_post import MaraviPostParser

print("Testing Maravi Post with updated Chrome flags...")
print("=" * 60)

parser = MaraviPostParser()
try:
    result = parser.scrape_news()
    articles = result.get("data", [])
    warning = result.get("warning")

    print(f"\n✅ Chrome launched successfully!")
    print(f"   Retrieved {len(articles)} articles")

    if warning:
        print(f"   Warning: {warning}")

    if articles:
        print("\nFirst article:")
        print(f"  Title: {articles[0].get('title', 'N/A')[:60]}...")
        print(f"  Link: {articles[0].get('link', 'N/A')[:60]}...")
    else:
        print("  (No articles found - likely still CAPTCHA blocked)")
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
print("\n" + "=" * 60)
