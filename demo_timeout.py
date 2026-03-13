#!/usr/bin/env python3
"""
Quick demo showing timeout and error handling features

This script demonstrates how the scraper handles:
1. Timeouts (URLs that take >10 seconds)
2. Connection errors
3. Invalid feeds
4. Successful scrapes

All errors are handled gracefully and don't crash the application.
"""

from scrapers import (
    MalawiVoiceParser,
    Malawi24Parser,
    MaraviPostParser,
    MwNationParser,
    PijParser,
)
import time


def demo_timeout_handling():
    """Demonstrate timeout and error handling"""
    print("=" * 70)
    print("Malawi News Scraper - Timeout & Error Handling Demo")
    print("=" * 70)
    print("\nThis demo shows how the scraper handles various failure scenarios:")
    print("• Timeouts (>10 seconds)")
    print("• Connection errors")
    print("• Invalid feeds")
    print("• Successful scrapes")
    print("\n" + "-" * 70)

    parsers = [
        ("Malawi Voice", MalawiVoiceParser()),
        ("Malawi24", Malawi24Parser()),
        ("Maravi Post", MaraviPostParser()),
        ("MW Nation", MwNationParser()),
        ("PIJ", PijParser()),
    ]

    results = {"successful": [], "timeout": [], "failed": []}

    print("\nScraping from all sources (10-second timeout per source)...\n")

    for name, parser in parsers:
        start_time = time.time()
        status = "⏳"
        print(f"{status} {name:20} - Fetching...", end="", flush=True)

        try:
            news_data = parser.scrape_news()
            elapsed = time.time() - start_time
            article_count = len(news_data["data"])
            results["successful"].append(
                {"name": name, "count": article_count, "time": elapsed}
            )
            print(f"\r✓ {name:20} - {article_count:3} articles ({elapsed:.1f}s)")

        except TimeoutError:
            elapsed = time.time() - start_time
            results["timeout"].append(name)
            print(f"\r⏱ {name:20} - TIMEOUT (>{elapsed:.0f}s)")

        except Exception as e:
            elapsed = time.time() - start_time
            error_type = type(e).__name__
            results["failed"].append(
                {"name": name, "error": error_type, "time": elapsed}
            )
            print(f"\r✗ {name:20} - FAILED: {error_type} ({elapsed:.1f}s)")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total = len(parsers)
    successful = len(results["successful"])
    timeout = len(results["timeout"])
    failed = len(results["failed"])

    print(f"\n📊 Results:")
    print(f"   Total sources:     {total}")
    print(f"   ✓ Successful:      {successful} ({successful/total*100:.0f}%)")
    print(f"   ⏱ Timeouts:        {timeout} ({timeout/total*100:.0f}%)")
    print(f"   ✗ Failed:          {failed} ({failed/total*100:.0f}%)")

    if results["successful"]:
        total_articles = sum(r["count"] for r in results["successful"])
        avg_time = sum(r["time"] for r in results["successful"]) / len(
            results["successful"]
        )
        print(f"\n📰 Articles collected: {total_articles}")
        print(f"⏱  Average fetch time: {avg_time:.1f}s")

    if results["timeout"]:
        print(f"\n⚠️  Timeout sources (took >10s):")
        for name in results["timeout"]:
            print(f"   - {name}")
        print(f"\n💡 These sources may be slow or unreachable.")
        print(f"   Consider increasing timeout or checking their status.")

    if results["failed"]:
        print(f"\n❌ Failed sources:")
        for item in results["failed"]:
            print(f"   - {item['name']}: {item['error']}")

    print("\n" + "=" * 70)
    print("✓ Demo completed - All errors handled gracefully!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    demo_timeout_handling()
