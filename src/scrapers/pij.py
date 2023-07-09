import scrapers
from scrapers.base_parser import BaseParser

class PijParser(BaseParser):
    def get_link(self):
        return scrapers.PIJ_URL