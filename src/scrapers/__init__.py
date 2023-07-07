from importlib import resources
import tomllib

# Version of the malawi news scraper
__version__ = "1.1.1"


_cfg = tomllib.loads(resources.read_text("scrapers", "config.toml"))
MALAWI_VOICE_URL = _cfg["scraper_urls"]["malawi_voice"]
MARAVI_POST_URL = _cfg["scraper_urls"]["maravi_post"]