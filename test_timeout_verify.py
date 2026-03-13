#!/usr/bin/env python3
"""
Quick test to verify 10-second timeout is working

This script specifically tests the Maravi Post URL that was previously
taking 71 seconds to timeout.
"""

import time
from scrapers import MaraviPostParser


def test_maravi_post_timeout():
    """Test that Maravi Post times out within 10-12 seconds"""
    print("Testing Maravi Post timeout...")
    print("Expected: ~10 seconds")
    print("Previous behavior: 71 seconds")
    print()

    parser = MaraviPostParser()
    start_time = time.time()

    try:
        print("⏳ Starting request to Maravi Post...")
        news_data = parser.scrape_news()
        elapsed = time.time() - start_time
        print(f"✓ Success! Scraped {len(news_data['data'])} articles in {elapsed:.1f}s")
        return "success", elapsed

    except TimeoutError as e:
        elapsed = time.time() - start_time
        print(f"⏱ Timeout after {elapsed:.1f}s (expected ~10s)")

        if elapsed <= 12:  # Allow 2s buffer for overhead
            print(f"✅ PASS: Timeout occurred within acceptable range ({elapsed:.1f}s)")
            return "timeout-ok", elapsed
        else:
            print(f"❌ FAIL: Timeout took too long ({elapsed:.1f}s > 12s)")
            return "timeout-slow", elapsed

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ Failed with {type(e).__name__}: {e}")
        print(f"   Time elapsed: {elapsed:.1f}s")
        return "error", elapsed


if __name__ == "__main__":
    print("=" * 70)
    print("Maravi Post Timeout Verification Test")
    print("=" * 70)
    print()

    result, elapsed = test_maravi_post_timeout()

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    if result == "success":
        print(f"✓ Server responded successfully in {elapsed:.1f}s")
    elif result == "timeout-ok":
        print(f"✓ Timeout working correctly: {elapsed:.1f}s ≤ 12s")
        print(f"  (10s timeout + ~{elapsed-10:.1f}s overhead)")
    elif result == "timeout-slow":
        print(f"✗ Timeout too slow: {elapsed:.1f}s > 12s")
        print(f"  Expected: ~10s, Got: {elapsed:.1f}s")
    else:
        print(f"? Unexpected error after {elapsed:.1f}s")

    print("=" * 70)
