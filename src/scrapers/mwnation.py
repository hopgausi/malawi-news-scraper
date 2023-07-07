import scrapers
from scrapers.base_parser import BaseParser

class MwNationParser(BaseParser):
    def get_link(self):
        return scrapers.MWNATION_URL