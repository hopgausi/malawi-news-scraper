#!/usr/bin/env python3
"""
Example script demonstrating how to use the Malawi News Scraper

This script shows different ways to use the scrapers to collect news
from Malawian news sources.
"""

from scrapers import (
    MalawiVoiceParser,
    Malawi24Parser,
    MaraviPostParser,
    MwNationParser,
    PijParser,
)


def scrape_single_source():
    """Example: Scraping from a single news source"""
    print("=" * 60)
    print("Example 1: Scraping from a single news source")
    print("=" * 60)

    # Define available sources
    sources = {
        "1": ("Malawi Voice", MalawiVoiceParser),
        "2": ("Malawi24", Malawi24Parser),
        "3": ("Maravi Post", MaraviPostParser),
        "4": ("MW Nation", MwNationParser),
        "5": ("PIJ", PijParser),
    }

    # Display available sources
    print("\nAvailable news sources:")
    for key, (name, _) in sources.items():
        print(f"  {key}. {name}")

    # Get user choice
    print(
        "\nEnter the number of the source to scrape (or press Enter for Malawi Voice): ",
        end="",
    )
    try:
        choice = input().strip() or "1"
    except (EOFError, KeyboardInterrupt):
        print("\nUsing default: Malawi Voice")
        choice = "1"

    # Validate choice
    if choice not in sources:
        print(f"\n⚠️  Invalid choice '{choice}'. Using Malawi Voice instead.")
        choice = "1"

    source_name, ParserClass = sources[choice]
    print(f"\n→ Selected: {source_name}")
    print("-" * 60)

    try:
        parser = ParserClass()
        news_data = parser.scrape_news()

        # Display source information
        source = news_data["source"]
        print(f"\nSource: {source['name']}")
        print(f"URL: {source['url']}")
        print(f"Mission: {source['mission_statement']}")

        # Display warnings if any
        if "warnings" in news_data and news_data["warnings"].get("broken_links"):
            print(f"\n⚠️  WARNING: {news_data['warnings']['message']}")
            print(f"   Articles will link to: {news_data['warnings']['fallback_url']}")

        # Display first 3 articles
        articles = news_data["data"]
        print(f"\nFound {len(articles)} articles")
        print("\nFirst 3 articles:")
        for i, article in enumerate(articles[:3], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Author: {article['author']}")
            print(f"   Date: {article['published_date']}")
            print(f"   Link: {article['link']}")
            # Show if link is from broken feed
            if article.get("link_status") == "broken_feed":
                print(f"   ⚠️  (Using fallback URL - feed has broken links)")
            if article["cover_image"]:
                print(f"   Image: {article['cover_image'][:60]}...")
    except TimeoutError:
        print(f"\n⏱ Request timed out after 10 seconds")
        print("   Continuing with other examples...")
    except Exception as e:
        print(f"\n❌ Failed to scrape {source_name}: {str(e)}")
        print("   Continuing with other examples...")


def scrape_all_sources():
    """Example: Scraping from all news sources"""
    print("\n\n" + "=" * 60)
    print("Example 2: Scraping from all sources")
    print("=" * 60)

    parsers = [
        ("Malawi Voice", MalawiVoiceParser()),
        ("Malawi24", Malawi24Parser()),
        ("Maravi Post", MaraviPostParser()),
        ("MW Nation", MwNationParser()),
        ("PIJ", PijParser()),
    ]

    total_articles = 0
    successful = 0
    failed = 0
    print()
    for name, parser in parsers:
        try:
            news_data = parser.scrape_news()
            article_count = len(news_data["data"])
            total_articles += article_count
            successful += 1
            print(f"✓ {name:20} - {article_count:3} articles")
        except TimeoutError as e:
            failed += 1
            print(f"⏱ {name:20} - TIMEOUT (>10s)")
        except Exception as e:
            failed += 1
            error_msg = str(e)[:40]
            print(f"✗ {name:20} - FAILED ({error_msg}...)")

    print(f"\nTotal articles scraped: {total_articles}")
    print(f"Successful sources: {successful}/{len(parsers)}")
    if failed > 0:
        print(f"Failed/Timeout sources: {failed}/{len(parsers)}")


def collect_all_articles():
    """Example: Collecting all articles into a single list"""
    print("\n\n" + "=" * 60)
    print("Example 3: Collecting all articles")
    print("=" * 60)

    parsers = [
        ("Malawi Voice", MalawiVoiceParser()),
        ("Malawi24", Malawi24Parser()),
        ("Maravi Post", MaraviPostParser()),
        ("MW Nation", MwNationParser()),
        ("PIJ", PijParser()),
    ]

    all_articles = []
    successful_sources = []
    failed_sources = []

    for name, parser in parsers:
        try:
            news_data = parser.scrape_news()
            # Add source name to each article
            source_name = news_data["source"]["name"] or name
            for article in news_data["data"]:
                article["source_name"] = source_name
                all_articles.append(article)
            successful_sources.append(name)
        except TimeoutError:
            failed_sources.append((name, "Timeout (>10s)"))
            print(f"⏱  Skipping {name}: Request timed out after 10 seconds")
        except Exception as e:
            failed_sources.append((name, str(e)[:50]))
            print(f"⚠️  Skipping {name}: {str(e)[:50]}...")

    print(
        f"\nCollected {len(all_articles)} articles from {len(successful_sources)} sources"
    )

    if failed_sources:
        print(f"Failed to scrape {len(failed_sources)} source(s):")
        for name, error in failed_sources:
            print(f"  - {name}")

    if all_articles:
        print("\nMost recent articles across all sources:")
        # Sort by date (descending) and show top 5
        # Note: In production, you'd want to parse the dates properly
        for i, article in enumerate(all_articles[:5], 1):
            print(f"\n{i}. [{article['source_name']}] {article['title']}")
            print(f"   {article['published_date']}")
    else:
        print("\n⚠️  No articles collected from any source.")


def scrape_with_summaries():
    """Example: Scraping articles with automatic summarization"""
    print("\n\n" + "=" * 60)
    print("Example 4: Article Summarization (2 types)")
    print("=" * 60)
    print("\nThis example fetches full article content and generates:")
    print("  1. Short teaser (~150 chars) for introducing the article")
    print("  2. Full overview (3-4 sentences) for complete picture")
    print("\nNote: Requires 'summarizer' dependencies. Install with:")
    print("  pip install -e '.[summarizer]'")
    print("-" * 60)

    # Use PIJ as example (HTML scraping, reliable links)
    print("\n→ Scraping PIJ articles with summaries...")

    try:
        parser = PijParser()
        news_data = parser.scrape_news()

        print(f"✓ Found {len(news_data['data'])} articles")
        print("→ Generating summaries (this may take a moment)...\n")

        # Add summaries to first 3 articles (to keep it fast)
        news_data = parser.add_summaries(news_data, max_articles=3)

        # Check if summarization worked
        if "summary_error" in news_data:
            print(f"⚠️  {news_data['summary_error']}")
            return

        # Display summary stats
        stats = news_data.get("summary_stats", {})
        print(f"✓ Successfully summarized: {stats.get('summarized', 0)}")
        print(f"✗ Failed: {stats.get('failed', 0)}")

        # Display articles with summaries
        print("\n" + "=" * 60)
        for i, article in enumerate(news_data["data"][:3], 1):
            print(f"\n📰 Article {i}: {article['title'][:50]}...")
            print(f"   Author: {article['author']}")
            print(f"   Date: {article['published_date']}")
            print(f"   URL: {article['link'][:60]}...")

            # Show short teaser
            if article.get("summary_short"):
                print(f"\n   💡 SHORT TEASER:")
                print(f"   {'-' * 55}")
                print(f"   {article['summary_short']}")
                print(f"   {'-' * 55}")

            # Show full overview
            if article.get("summary_long"):
                print(f"\n   📝 FULL OVERVIEW:")
                print(f"   {'-' * 55}")
                print(f"   {article['summary_long']}")
                print(f"   {'-' * 55}")

            if article.get("summary_error"):
                print(f"\n   ⚠️  Summary not available: {article['summary_error']}")

    except TimeoutError:
        print(f"⏱  Request timed out after 10 seconds")
    except Exception as e:
        print(f"❌ Failed to scrape: {str(e)}")


def main():
    """Run all examples"""
    print("\n🗞️  Malawi News Scraper - Examples\n")

    # Example 1: Single source
    scrape_single_source()

    # Example 2: All sources summary
    scrape_all_sources()

    # Example 3: Collect all articles
    collect_all_articles()

    # Example 4: Article summarization
    scrape_with_summaries()

    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)
    print("\nNote: Some sources may fail due to network issues,")
    print("site maintenance, or changes in RSS feed structure.")
    print()

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
