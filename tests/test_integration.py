"""Integration tests for scraping live RSS feeds"""

import pytest
from scrapers import (
    MalawiVoiceParser,
    Malawi24Parser,
    MaraviPostParser,
    MwNationParser,
    PijParser,
)


# Mark integration tests to be run separately
pytestmark = pytest.mark.integration


class TestLiveFeeds:
    """Integration tests that fetch real RSS feeds"""

    @pytest.mark.slow
    def test_malawi_voice_scrape_news(self):
        """Test scraping live news from Malawi Voice"""
        parser = MalawiVoiceParser()
        result = parser.scrape_news()

        assert "data" in result
        assert "source" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

        # Check article structure
        article = result["data"][0]
        assert "title" in article
        assert "link" in article
        assert "author" in article
        assert "published_date" in article
        assert "cover_image" in article

        # Check source structure
        source = result["source"]
        assert "name" in source
        assert "url" in source
        assert "mission_statement" in source

    @pytest.mark.slow
    def test_malawi24_scrape_news(self):
        """Test scraping live news from Malawi24"""
        parser = Malawi24Parser()
        result = parser.scrape_news()

        assert "data" in result
        assert "source" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

    @pytest.mark.slow
    def test_maravi_post_scrape_news(self):
        """Test scraping live news from Maravi Post"""
        parser = MaraviPostParser()
        result = parser.scrape_news()

        assert "data" in result
        assert "source" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

    @pytest.mark.slow
    def test_mwnation_scrape_news(self):
        """Test scraping live news from MW Nation"""
        parser = MwNationParser()
        result = parser.scrape_news()

        assert "data" in result
        assert "source" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

    @pytest.mark.slow
    def test_pij_scrape_news(self):
        """Test scraping live news from PIJ"""
        parser = PijParser()
        result = parser.scrape_news()

        assert "data" in result
        assert "source" in result
        assert isinstance(result["data"], list)
        assert len(result["data"]) > 0

    @pytest.mark.slow
    def test_all_parsers(self):
        """Test that all parsers can scrape successfully"""
        parsers = [
            MalawiVoiceParser(),
            Malawi24Parser(),
            MaraviPostParser(),
            MwNationParser(),
            PijParser(),
        ]

        all_articles = []
        for parser in parsers:
            result = parser.scrape_news()
            assert len(result["data"]) > 0
            all_articles.extend(result["data"])

        assert len(all_articles) > 0
        print(f"\nTotal articles scraped from all sources: {len(all_articles)}")
