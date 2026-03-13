"""Tests for BaseFeedScraper class"""

import pytest
from scrapers.base_feed_scraper import BaseFeedScraper


class TestBaseFeedScraper:
    """Test suite for BaseFeedScraper"""

    def test_initialization(self):
        """Test that BaseFeedScraper can be initialized"""
        scraper = BaseFeedScraper()
        assert scraper.link is None
        assert scraper.timeout == 10  # Default timeout

    def test_custom_timeout(self):
        """Test that timeout can be customized"""
        scraper = BaseFeedScraper()
        scraper.timeout = 5
        assert scraper.timeout == 5

    def test_get_link_returns_none(self):
        """Test that get_link returns None by default"""
        scraper = BaseFeedScraper()
        assert scraper.get_link() is None

    def test_get_image_url_with_image(self):
        """Test extracting image URL from HTML content"""
        scraper = BaseFeedScraper()
        html_content = (
            '<p>Some text</p><img src="https://example.com/image.jpg" alt="test"/>'
        )
        image_url = scraper._get_image_url(html_content)
        assert image_url == "https://example.com/image.jpg"

    def test_get_image_url_without_image(self):
        """Test extracting image URL from HTML without images"""
        scraper = BaseFeedScraper()
        html_content = "<p>Some text without images</p>"
        image_url = scraper._get_image_url(html_content)
        assert image_url == ""

    def test_get_image_url_with_multiple_images(self):
        """Test that only first image is extracted"""
        scraper = BaseFeedScraper()
        html_content = """
        <img src="https://example.com/first.jpg" alt="first"/>
        <img src="https://example.com/second.jpg" alt="second"/>
        """
        image_url = scraper._get_image_url(html_content)
        assert image_url == "https://example.com/first.jpg"

    def test_get_source_name_for_pij_old(self):
        """Test getting source name for PIJ old URL doesn't match"""
        scraper = BaseFeedScraper()
        link = "https://www.investigativeplatform-mw.org/feed/"
        name = scraper._get_source_name(link)
        # Old URL no longer has special handling
        assert name == ""

    def test_get_source_name_for_pij_new(self):
        """Test getting source name for Platform for Investigative Journalism (new URL)"""
        scraper = BaseFeedScraper()
        link = "https://www.pijmalawi.org/feed/"
        name = scraper._get_source_name(link)
        assert name == "Platform For Investigative Journalism"

    def test_get_source_name_for_unknown(self):
        """Test getting source name for unknown source"""
        scraper = BaseFeedScraper()
        link = "https://example.com/feed/"
        name = scraper._get_source_name(link)
        assert name == ""

    def test_get_mission_statement_for_pij(self):
        """Test getting mission statement for PIJ"""
        scraper = BaseFeedScraper()
        statement = scraper._get_mission_statement(
            "Platform For Investigative Journalism"
        )
        assert statement == "Digging Truth. Lighting Democracy"

    def test_get_mission_statement_for_unknown(self):
        """Test getting mission statement for unknown source"""
        scraper = BaseFeedScraper()
        statement = scraper._get_mission_statement("Unknown Source")
        assert statement == ""

    def test_get_source_details(self):
        """Test getting source details from feed"""
        scraper = BaseFeedScraper()
        mock_feed = {
            "title": "Test News",
            "link": "https://example.com",
            "subtitle": "Test mission statement",
        }
        details = scraper._get_source_details(mock_feed)
        assert details["name"] == "Test News"
        assert details["url"] == "https://example.com"
        assert details["mission_statement"] == "Test mission statement"

    def test_get_source_details_with_empty_title_old_pij(self):
        """Test getting source details when feed has no title (old PIJ URL has no special handling)"""
        scraper = BaseFeedScraper()
        mock_feed = {
            "title": "",
            "link": "https://www.investigativeplatform-mw.org/feed/",
            "subtitle": "",
        }
        details = scraper._get_source_details(mock_feed)
        # Old URL no longer has special handling
        assert details["name"] == ""

    def test_get_source_details_with_empty_title_new_url(self):
        """Test getting source details when feed has no title (new PIJ URL)"""
        scraper = BaseFeedScraper()
        mock_feed = {
            "title": "",
            "link": "https://www.pijmalawi.org/feed/",
            "subtitle": "",
        }
        details = scraper._get_source_details(mock_feed)
        # New URL matches special case for PIJ
        assert details["name"] == "Platform For Investigative Journalism"
        assert details["mission_statement"] == "Digging Truth. Lighting Democracy"

    def test_sanitize_news_with_missing_fields(self):
        """Test that _sanitize_news handles missing fields gracefully"""
        scraper = BaseFeedScraper()

        # Mock parsed feed with missing fields
        mock_parsed = type(
            "obj",
            (object,),
            {
                "entries": [
                    {
                        "title": "Test Article",
                        "link": "https://example.com/article1",
                        # author is missing
                        # published is missing
                    },
                    {
                        # title is missing
                        "link": "https://example.com/article2",
                        "author": "Test Author",
                        "published": "2026-03-13",
                    },
                ],
                "feed": {
                    "title": "Test Feed",
                    "link": "https://example.com",
                    "subtitle": "Test Description",
                },
            },
        )()

        result = scraper._sanitize_news(mock_parsed)

        # Check first article (missing author and published)
        # Author should fallback to source name
        assert result["data"][0]["title"] == "Test Article"
        assert result["data"][0]["link"] == "https://example.com/article1"
        assert result["data"][0]["author"] == "Test Feed"  # Falls back to source name
        assert result["data"][0]["published_date"] == ""

        # Check second article (missing title)
        assert result["data"][1]["title"] == "No title"
        assert result["data"][1]["link"] == "https://example.com/article2"
        assert result["data"][1]["author"] == "Test Author"
        assert result["data"][1]["published_date"] == "2026-03-13"

    def test_get_source_details_with_missing_fields(self):
        """Test that _get_source_details handles missing fields gracefully"""
        scraper = BaseFeedScraper()

        # Mock feed with all fields missing
        mock_feed = {}
        details = scraper._get_source_details(mock_feed)

        assert details["name"] == ""
        assert details["url"] == ""
        assert details["mission_statement"] == ""
