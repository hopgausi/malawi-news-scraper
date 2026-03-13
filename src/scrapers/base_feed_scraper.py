import feedparser
from bs4 import BeautifulSoup
from functools import cache
import socket
import urllib.request
import urllib.error


class BaseFeedScraper:
    def __init__(self):
        self.link = self.get_link()
        self.timeout = 10  # Default timeout in seconds

    def get_link(self):
        return None

    def scrape_news(self) -> dict:
        """Scrape the news feed, and return a list of news articles and source details."""
        parsed_xml_news = self._get_xml_news()
        return self._sanitize_news(parsed_xml_news)

    @cache
    def _get_xml_news(self) -> dict:
        """Return an object of parsed xml news feed with timeout handling"""
        # Set socket timeout to enforce actual timeout at network level
        old_timeout = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(self.timeout)
            result = feedparser.parse(self.link)

            # Check if feedparser encountered an error (like timeout)
            if hasattr(result, "bozo") and result.bozo:
                if isinstance(
                    result.bozo_exception, (socket.timeout, urllib.error.URLError)
                ):
                    raise TimeoutError(
                        f"Request timed out after {self.timeout} seconds"
                    )

            return result
        except (socket.timeout, TimeoutError) as e:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds")
        except urllib.error.URLError as e:
            if isinstance(e.reason, socket.timeout):
                raise TimeoutError(f"Request timed out after {self.timeout} seconds")
            raise
        finally:
            # Always restore the original timeout
            socket.setdefaulttimeout(old_timeout)

    def _sanitize_news(self, parsed_xml_news: dict) -> dict:
        """Satinize news parsed from xml"""
        sanitized_news = []
        news_list = parsed_xml_news.entries

        # Get source name early to use as fallback for missing author
        source_details = self._get_source_details(parsed_xml_news.feed)
        source_name = source_details.get("name", "Unknown")

        # Detect broken feed (all entries have the same link)
        links = [news.get("link", "") for news in news_list if news.get("link")]
        has_broken_links = False
        broken_link_replacement = ""

        if links and len(set(links)) == 1 and len(links) > 5:
            # All entries have the same link - broken RSS feed
            has_broken_links = True
            # Get the base URL from the feed
            feed_link = parsed_xml_news.feed.get("link", "")
            broken_link_replacement = feed_link if feed_link else links[0]

        for news in news_list:
            # Use .get() to handle missing fields gracefully
            title = news.get("title", "No title")
            link = news.get("link", "")
            # Use source name if author is missing
            author = news.get("author", source_name)
            published_date = news.get("published", "")
            content = (
                news["content"][0]["value"] if len(news.get("content", [])) > 0 else ""
            )
            cover_image = self._get_image_url(content)

            # Handle broken links
            article_data = {
                "title": title,
                "link": link,
                "author": author,
                "published_date": published_date,
                "cover_image": cover_image,
            }

            # Add broken link indicator if detected
            if has_broken_links:
                article_data["link_status"] = "broken_feed"
                article_data["link"] = broken_link_replacement
                article_data["original_broken_link"] = link

            sanitized_news.append(article_data)

        result = {
            "data": sanitized_news,
            "source": source_details,
            "broken_links": True,
            "message": "This feed has broken article links. All articles point to the same URL. Using main website instead.",
            "fallback_url": broken_link_replacement,
        }

        return result

    def _get_image_url(self, content: str) -> str:
        """Returns the image url for the given content news feed"""
        soup = BeautifulSoup(content, "html.parser")
        img_tag = soup.find_all("img")
        img = img_tag[0]["src"] if len(img_tag) > 0 else ""
        return img

    def _get_source_details(self, feed: dict) -> dict:
        """Returns the source details for the news, that is, the site the feed is being scraped from"""
        name = feed.get("title", "")
        link = feed.get("link", "")
        subtitle = feed.get("subtitle", "")

        if len(name) == 0:
            name = self._get_source_name(link)
        source_details = {
            "name": name,
            "url": link,
            "mission_statement": (
                subtitle if len(subtitle) > 0 else self._get_mission_statement(name)
            ),
        }
        return source_details

    def _get_source_name(self, link):
        """Returns source name of the news based on link provided should the feed have no defined source name"""
        name = ""
        if "pijmalawi" in link:
            name = "Platform For Investigative Journalism"
        return name

    def _get_mission_statement(self, source_name):
        """Returns source mission statement of the news based on source name provided should the feed have no defined source statement"""
        statement = ""
        if source_name == "Platform For Investigative Journalism":
            statement = "Digging Truth. Lighting Democracy"
        return statement
