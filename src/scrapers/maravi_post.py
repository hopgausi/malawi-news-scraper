import scrapers
from scrapers.base_parser import BaseParser
from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import socket
from datetime import datetime


class MaraviPostParser(BaseParser):
    def get_link(self):
        return scrapers.MARAVI_POST_URL

    def scrape_news(self) -> dict:
        """
        Custom scraper for Maravi Post since their RSS feed is malformed.

        Note: The site uses CAPTCHA protection which may prevent scraping.
        If CAPTCHA is encountered, returns empty article list.
        """
        # Try the main page for latest articles
        html_url = "https://www.maravipost.com/"

        old_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(self.timeout)

            # Fetch HTML page with browser-like headers
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }

            req = urllib.request.Request(html_url, headers=headers)
            with urllib.request.urlopen(req) as response:
                # Check if we hit CAPTCHA
                if "SG-Captcha" in str(response.headers):
                    # CAPTCHA detected - return empty results
                    return {
                        "data": [],
                        "source": {
                            "name": "Maravi Post",
                            "url": "https://www.maravipost.com",
                            "mission_statement": "News from Malawi",
                        },
                        "warning": "Site is protected by CAPTCHA - unable to scrape",
                    }

                html_content = response.read().decode("utf-8")

            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")
            articles = self._parse_maravi_html(soup, html_url)

            return {
                "data": articles,
                "source": {
                    "name": "Maravi Post",
                    "url": "https://www.maravipost.com",
                    "mission_statement": "News from Malawi",
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

    def _parse_maravi_html(self, soup: BeautifulSoup, base_url: str) -> list:
        """Parse Maravi Post HTML page and extract article information"""
        articles = []

        # Try to find article containers
        # Common WordPress patterns: article tags, .post, .entry
        selectors = [
            ("article", None),
            ("div", "post"),
            ("div", "entry"),
            ("div", "item"),
        ]

        article_elements = []
        for tag, class_pattern in selectors:
            if class_pattern:
                elements = soup.find_all(
                    tag, class_=lambda x: x and class_pattern in str(x).lower()
                )
            else:
                elements = soup.find_all(tag)

            if elements:
                article_elements = elements
                break

        for element in article_elements[:20]:  # Limit to first 20
            try:
                article_data = self._extract_article_data(element, base_url)
                if article_data and article_data["title"] and article_data["link"]:
                    articles.append(article_data)
            except Exception:
                continue  # Skip problematic articles

        return articles

    def _extract_article_data(self, element, base_url: str) -> dict:
        """Extract article data from an HTML element"""
        title = ""
        link = ""
        author = "Maravi Post"
        published_date = ""
        cover_image = ""

        # Try to find title
        title_elem = element.find(["h1", "h2", "h3", "h4"])
        if title_elem:
            title = title_elem.get_text(strip=True)

        # Try to find link
        link_elem = element.find("a", href=True)
        if link_elem and link_elem.get("href"):
            link = link_elem["href"]
            if link and not link.startswith("http"):
                link = f"https://www.maravipost.com{link}"
            # Also get title from link if not found
            if not title:
                title = link_elem.get_text(strip=True)

        # Try to find image
        img_elem = element.find("img")
        if img_elem:
            cover_image = img_elem.get("src", "") or img_elem.get("data-src", "")
            if cover_image and not cover_image.startswith("http"):
                cover_image = f"https://www.maravipost.com{cover_image}"

        # Try to find date
        date_elem = element.find(
            ["time", "span"], class_=lambda x: x and "date" in str(x).lower()
        )
        if date_elem:
            datetime_attr = date_elem.get("datetime")
            if datetime_attr:
                published_date = datetime_attr
            else:
                published_date = date_elem.get_text(strip=True)

        return {
            "title": title,
            "link": link,
            "author": author,
            "published_date": published_date or datetime.now().strftime("%Y-%m-%d"),
            "cover_image": cover_image,
        }
