from importlib import resources
import tomllib
from .malawi_voice import MalawiVoiceParser
from .maravi_post import MaraviPostParser
from .mwnation import MwNationParser
from .pij import PijParser

# Version of the malawi news scraper
__version__ = "1.1.1"

_cfg = tomllib.loads(resources.read_text("scrapers", "config.toml"))
MALAWI_VOICE_URL = _cfg["scraper_urls"]["malawi_voice"]
MARAVI_POST_URL = _cfg["scraper_urls"]["maravi_post"]
MWNATION_URL = _cfg["scraper_urls"]["mwnation"]
PIJ_URL = _cfg["scraper_urls"]["pij"]