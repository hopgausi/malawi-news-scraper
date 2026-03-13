import scrapers
from scrapers.base_parser import BaseParser
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import socket
from datetime import datetime


class PijParser(BaseParser):
    def get_link(self):
        return scrapers.PIJ_URL

    def scrape_news(self) -> dict:
        """
        Custom scraper for PIJ since their RSS feed has broken links.
        Uses HTML page scraping instead.
        """
        # Use the all-stories page instead of RSS feed
        html_url = "https://www.pijmalawi.org/all-stories"

        old_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(self.timeout)

            # Fetch HTML page
            req = urllib.request.Request(
                html_url, headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req) as response:
                html_content = response.read().decode("utf-8")

            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")
            articles = self._parse_pij_html(soup, html_url)

            return {
                "data": articles,
                "source": {
                    "name": "Platform For Investigative Journalism",
                    "url": "https://www.pijmalawi.org",
                    "mission_statement": "Digging Truth. Lighting Democracy",
                },
            }

        except (socket.timeout, urllib.error.URLError) as e:
            if isinstance(e, socket.timeout) or (
                isinstance(e, urllib.error.URLError)
                and isinstance(e.reason, socket.timeout)
            ):
                raise TimeoutError(f"Request timed out after {self.timeout} seconds")
            raise
        finally:
            socket.setdefaulttimeout(old_timeout)

    def _parse_pij_html(self, soup: BeautifulSoup, base_url: str) -> list:
        """Parse PIJ HTML page and extract article information"""
        articles = []

        # Find article containers - PIJ uses <article class="story-card">
        article_elements = soup.find_all("article", class_="story-card")

        for element in article_elements:
            try:
                article_data = self._extract_article_data(element, base_url)
                if article_data and article_data["title"] and article_data["link"]:
                    # Skip if link is just a hash (navigation elements)
                    if article_data["link"].endswith("#"):
                        continue
                    articles.append(article_data)
            except Exception:
                continue  # Skip problematic articles

        return articles

    def _extract_article_data(self, element, base_url: str) -> dict:
        """Extract article data from an HTML element"""
        title = ""
        link = ""
        author = "Platform For Investigative Journalism"
        published_date = ""
        cover_image = ""

        # Find title from image alt text or h3
        img_elem = element.find("img", class_="story-image")
        if img_elem and img_elem.get("alt"):
            title = img_elem["alt"]
            cover_image = img_elem.get("src", "")
            if cover_image and not cover_image.startswith("http"):
                cover_image = f"https://www.pijmalawi.org{cover_image}"

        # Find link from h3 > a
        h3_elem = element.find("h3", class_="story-title")
        if h3_elem:
            link_elem = h3_elem.find("a")
            if link_elem and link_elem.get("href"):
                link = link_elem["href"]
                if not link.startswith("http"):
                    link = f"https://www.pijmalawi.org{link}"
                # Also get title from link text if not found in image
                if not title:
                    title = link_elem.get_text(strip=True)

        # Try to find date
        date_elem = element.find(
            "span", class_=lambda x: x and "date" in str(x).lower()
        )
        if date_elem:
            published_date = date_elem.get_text(strip=True)

        return {
            "title": title,
            "link": link,
            "author": author,
            "published_date": published_date or datetime.now().strftime("%Y-%m-%d"),
            "cover_image": cover_image,
        }
