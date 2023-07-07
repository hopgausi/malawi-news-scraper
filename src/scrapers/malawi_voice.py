import feedparser
from bs4 import BeautifulSoup
import scrapers
from functools import cache

class MalawiVoiceScraper:
    def __init__(self):
        self.link = scrapers.MALAWI_VOICE_URL
    
    def scrape_news(self)-> dict:
        """ Scrape the news feed, and return a list of news articles and source details."""
        parsed_xml_news = self.get_xml_news()
        return self._sanitize_news(parsed_xml_news)
    
    @cache
    def get_xml_news(self)-> dict:
        """ Return an object of parsed xml news feed"""
        return feedparser.parse(self.link)

    def _sanitize_news(self, parsed_xml_news: dict) -> dict:
        """ Satinize news parsed from xml"""
        sanitized_news = []
        news_list = parsed_xml_news.entries
        for news in news_list:
            title = news['title']
            link = news['link']
            author = news['author']
            published_date = news['published']
            cover_image = self._get_image_url(news['content'][0]['value'])
            sanitized_news.append({
                'title': title,
                'link': link,
                'author': author,
                'published_date': published_date,
                'cover_image': cover_image,
            })
        return {
            'data': sanitized_news,
            'source': self._get_source_details(parsed_xml_news.feed)
        }
            
    def _get_image_url(self, content: str)->str:
        """Returns the image url for the given content news feed"""
        soup = BeautifulSoup(content, 'html.parser')
        img_tag = soup.find('figure').find('img')
        return img_tag['src']
    
    def _get_source_details(self, feed: dict) -> dict:
        """Returns the source details for the news, that is, the site the feed is being scraped from"""
        source_details = {
            'name': feed['title'],
            'url': feed['link'],
            'mission_statement': feed['subtitle'],
        }
        return source_details