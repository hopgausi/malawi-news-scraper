from scrapers.base_feed_scraper import BaseFeedScraper

class BaseParser(BaseFeedScraper):
    def get_link(self):
        raise NotImplementedError("Subclasses must implement get_link()")

    def scrape_news(self) -> dict:
        self.link = self.get_link()
        return super().scrape_news()
