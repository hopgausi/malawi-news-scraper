#!/usr/bin/env python3
"""
Test script to verify PIJ HTML scraping functionality
"""
import sys
import time
from src.scrapers.pij import PijParser


def main():
    print("=" * 60)
    print("Testing PIJ HTML Scraper")
    print("=" * 60)

    parser = PijParser()

    print("\n📰 Fetching articles from https://www.pijmalawi.org/all-stories...")
    print(f"⏱️  Timeout: {parser.timeout} seconds")

    start_time = time.time()

    try:
        result = parser.scrape_news()
        elapsed = time.time() - start_time

        articles = result.get("data", [])
        source = result.get("source", {})

        print(f"\n✅ Success! Fetched in {elapsed:.2f} seconds")
        print(f"\n📊 Results:")
        print(f"   - Total articles: {len(articles)}")
        print(f"   - Source: {source.get('name', 'Unknown')}")
        print(f"   - URL: {source.get('url', 'Unknown')}")

        if articles:
            print(f"\n📄 First 5 articles:")
            for i, article in enumerate(articles[:5], 1):
                print(f"\n   {i}. {article.get('title', 'No title')}")
                print(f"      Link: {article.get('link', 'No link')}")
                print(f"      Author: {article.get('author', 'Unknown')}")
                print(f"      Date: {article.get('published_date', 'Unknown')}")
                if article.get("cover_image"):
                    print(f"      Image: {article.get('cover_image')[:60]}...")

            # Check for duplicate links (the original problem)
            links = [a.get("link") for a in articles if a.get("link")]
            unique_links = set(links)

            print(f"\n🔍 Link Analysis:")
            print(f"   - Total links: {len(links)}")
            print(f"   - Unique links: {len(unique_links)}")

            if len(unique_links) < len(links) * 0.8:
                print("   ⚠️  Warning: Many duplicate links detected")
            else:
                print("   ✅ Links appear to be unique (problem fixed!)")
        else:
            print("\n⚠️  No articles found. HTML structure may have changed.")
            print("   Run with verbose mode to inspect HTML structure.")

        return 0

    except TimeoutError as e:
        elapsed = time.time() - start_time
        print(f"\n⏱️  Timeout after {elapsed:.2f} seconds: {e}")
        return 1

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ Error after {elapsed:.2f} seconds: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
