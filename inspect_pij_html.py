#!/usr/bin/env python3
"""
Inspect PIJ HTML structure to improve parsing
"""
import urllib.request
import socket
from bs4 import BeautifulSoup

url = "https://www.pijmalawi.org/all-stories"

socket.setdefaulttimeout(10)
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

with urllib.request.urlopen(req) as response:
    html = response.read().decode("utf-8")

soup = BeautifulSoup(html, "html.parser")

# Save a sample of the HTML for inspection
with open("/tmp/pij_sample.html", "w") as f:
    f.write(soup.prettify()[:10000])  # First 10k chars

print("HTML sample saved to /tmp/pij_sample.html")
print("\nLooking for article containers...")

# Try different selectors
selectors = [
    ("article", None),
    ("div", "post"),
    ("div", "story"),
    ("div", "article"),
    ("div", "item"),
    ("div", "card"),
]

for tag, class_pattern in selectors:
    if class_pattern:
        elements = soup.find_all(
            tag, class_=lambda x: x and class_pattern in str(x).lower()
        )
        if elements:
            print(
                f"\n✓ Found {len(elements)} elements: <{tag} class=*{class_pattern}*>"
            )
            if elements:
                print(f"  Sample HTML:\n{elements[0].prettify()[:500]}")
    else:
        elements = soup.find_all(tag)
        if elements:
            print(f"\n✓ Found {len(elements)} <{tag}> elements")
            if elements:
                print(f"  Sample HTML:\n{elements[0].prettify()[:500]}")

# Look for links to /show-story/
story_links = soup.find_all("a", href=lambda x: x and "/show-story/" in x)
print(f"\n✓ Found {len(story_links)} links to /show-story/")
if story_links:
    for i, link in enumerate(story_links[:3]):
        print(f"\n  {i+1}. {link.get('href')}")
        print(f"     Text: {link.get_text(strip=True)[:60]}")
        print(f"     Parent: {link.parent.name}")
