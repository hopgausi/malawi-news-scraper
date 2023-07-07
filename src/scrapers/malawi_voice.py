import scrapers
from base_parser import BaseParser

class MalawiVoiceParser(BaseParser):
    def get_link(self):
        return scrapers.MALAWI_VOICE_URL
    
print(MalawiVoiceParser().scrape_news())