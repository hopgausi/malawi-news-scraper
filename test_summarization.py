#!/usr/bin/env python3
"""Test article summarization feature"""

import sys

sys.path.insert(0, "src")

from scrapers.pij import PijParser

print("Testing Article Summarization")
print("=" * 70)
print("\n→ Scraping PIJ articles...")

try:
    parser = PijParser()
    news_data = parser.scrape_news()

    article_count = len(news_data.get("data", []))
    print(f"✓ Found {article_count} articles")

    if article_count == 0:
        print("⚠️  No articles to summarize")
        sys.exit(0)

    print("\n→ Generating summaries for first 2 articles...")
    print("   (Fetching full content from URLs...)\n")

    # Add summaries
    news_data = parser.add_summaries(news_data, max_articles=2)

    # Check for errors
    if "summary_error" in news_data:
        print(f"❌ {news_data['summary_error']}")
        sys.exit(1)

    # Display stats
    stats = news_data.get("summary_stats", {})
    print("-" * 70)
    print(f"Summary Statistics:")
    print(f"  ✓ Successfully summarized: {stats.get('summarized', 0)}")
    print(f"  ✗ Failed: {stats.get('failed', 0)}")
    print("-" * 70)

    # Display first summarized article
    for i, article in enumerate(news_data["data"][:2], 1):
        print(f"\n📰 Article {i}:")
        print(f"   Title: {article['title'][:70]}...")
        print(f"   Author: {article.get('author', 'N/A')}")
        print(f"   URL: {article['link'][:70]}...")

        # Display both summary types
        if article.get("summary_short"):
            print(f"\n   💡 SHORT TEASER (for introducing):")
            print("   " + "─" * 66)
            print(f"   {article['summary_short']}")
            print("   " + "─" * 66)

        if article.get("summary_long"):
            print(f"\n   📝 FULL OVERVIEW (complete picture):")
            print("   " + "─" * 66)
            print(f"   {article['summary_long']}")
            print("   " + "─" * 66)

        if article.get("summary_error"):
            print(f"\n   ⚠️  Error: {article['summary_error']}")

        print()

    print("\n✅ Summarization test complete!")

except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
