import scrapers
from scrapers.base_parser import BaseParser

class MaraviPostParser(BaseParser):
    def get_link(self):
        return scrapers.MARAVI_POST_URL