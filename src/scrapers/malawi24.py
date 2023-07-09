import scrapers
from scrapers.base_parser import BaseParser

class Malawi24Parser(BaseParser):
    def get_link(self):
        return scrapers.MALAWI24_URL