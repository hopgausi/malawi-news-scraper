import scrapers
from scrapers.base_parser import BaseParser
from bs4 import BeautifulSoup
from datetime import datetime
import signal

# Try to import Selenium (optional dependency)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.webdriver.firefox.service import Service as FirefoxService
    from webdriver_manager.chrome import ChromeDriverManager
    from webdriver_manager.firefox import GeckoDriverManager
    from selenium.common.exceptions import (
        WebDriverException,
        TimeoutException as SeleniumTimeout,
    )

    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class MaraviPostParser(BaseParser):
    def get_link(self):
        return scrapers.MARAVI_POST_URL

    def scrape_news(self) -> dict:
        """
        Custom scraper for Maravi Post.

        Tries Selenium (if available) to bypass CAPTCHA, otherwise returns empty results.
        The site uses CAPTCHA protection which prevents simple HTTP scraping.
        """
        if SELENIUM_AVAILABLE:
            try:
                return self._scrape_with_selenium()
            except Exception as e:
                # Selenium failed, return empty with warning
                return {
                    "data": [],
                    "source": {
                        "name": "Maravi Post",
                        "url": "https://www.maravipost.com",
                        "mission_statement": "News from Malawi",
                    },
                    "warning": f"Selenium scraping failed: {str(e)[:100]}",
                }
        else:
            # Selenium not available
            return {
                "data": [],
                "source": {
                    "name": "Maravi Post",
                    "url": "https://www.maravipost.com",
                    "mission_statement": "News from Malawi",
                },
                "warning": "Site protected by CAPTCHA - install selenium and webdriver-manager: pip install selenium webdriver-manager",
            }

    def _scrape_with_selenium(self) -> dict:
        """Use Selenium to scrape Maravi Post (attempts CAPTCHA bypass)"""
        html_url = "https://www.maravipost.com/"

        # Try Chrome first, then Firefox
        driver = None
        browser_used = None

        # Timeout handler for Chrome initialization
        def timeout_handler(signum, frame):
            raise TimeoutError("Chrome initialization timed out")

        try:
            # Try Chrome/Chromium first
            try:
                chrome_options = ChromeOptions()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--disable-software-rasterizer")
                chrome_options.add_argument("--disable-background-networking")
                chrome_options.add_argument("--disable-sync")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-default-apps")
                chrome_options.add_argument("--no-first-run")
                chrome_options.add_argument("--mute-audio")
                chrome_options.add_argument("--disable-breakpad")
                chrome_options.add_argument(
                    "--disable-blink-features=AutomationControlled"
                )
                chrome_options.add_experimental_option(
                    "excludeSwitches", ["enable-automation", "enable-logging"]
                )
                chrome_options.add_experimental_option("useAutomationExtension", False)
                chrome_options.add_argument(
                    "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                chrome_options.page_load_strategy = "normal"

                # Set 15 second timeout for Chrome initialization
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(15)

                try:
                    service = ChromeService(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    browser_used = "Chrome"
                finally:
                    signal.alarm(0)  # Cancel alarm

            except Exception as chrome_error:
                # Chrome failed, try Firefox
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--headless")
                firefox_options.set_preference(
                    "general.useragent.override",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
                )
                firefox_options.set_preference("dom.webdriver.enabled", False)
                firefox_options.set_preference("useAutomationExtension", False)
                firefox_options.page_load_strategy = "normal"

                service = FirefoxService(GeckoDriverManager().install())
                driver = webdriver.Firefox(service=service, options=firefox_options)
                browser_used = "Firefox"

            # Set timeout
            driver.set_page_load_timeout(self.timeout)

            # Load page
            driver.get(html_url)

            # Wait for content
            driver.implicitly_wait(2)

            # Get page source
            html_content = driver.page_source

            # Check if still has CAPTCHA
            if (
                "sgcaptcha" in html_content.lower()
                or "captcha" in driver.current_url.lower()
            ):
                return {
                    "data": [],
                    "source": {
                        "name": "Maravi Post",
                        "url": "https://www.maravipost.com",
                        "mission_statement": "News from Malawi",
                    },
                    "warning": f"Site protected by CAPTCHA - {browser_used} also blocked",
                }

            # Parse HTML
            soup = BeautifulSoup(html_content, "html.parser")
            articles = self._parse_maravi_html(soup, html_url)

            return {
                "data": articles,
                "source": {
                    "name": "Maravi Post",
                    "url": "https://www.maravipost.com",
                    "mission_statement": "News from Malawi",
                },
            }

        except SeleniumTimeout:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

    def _parse_maravi_html(self, soup: BeautifulSoup, base_url: str) -> list:
        """Parse Maravi Post HTML page and extract article information"""
        articles = []

        # Try to find article containers
        selectors = [
            ("article", None),
            ("div", "post"),
            ("div", "entry"),
            ("div", "item"),
        ]

        article_elements = []
        for tag, class_pattern in selectors:
            if class_pattern:
                elements = soup.find_all(
                    tag, class_=lambda x: x and class_pattern in str(x).lower()
                )
            else:
                elements = soup.find_all(tag)

            if elements:
                article_elements = elements
                break

        for element in article_elements[:20]:
            try:
                article_data = self._extract_article_data(element, base_url)
                if article_data and article_data["title"] and article_data["link"]:
                    articles.append(article_data)
            except Exception:
                continue

        return articles

    def _extract_article_data(self, element, base_url: str) -> dict:
        """Extract article data from an HTML element"""
        title = ""
        link = ""
        author = "Maravi Post"
        published_date = ""
        cover_image = ""

        # Try to find title
        title_elem = element.find(["h1", "h2", "h3", "h4"])
        if title_elem:
            title = title_elem.get_text(strip=True)

        # Try to find link
        link_elem = element.find("a", href=True)
        if link_elem and link_elem.get("href"):
            link = link_elem["href"]
            if link and not link.startswith("http"):
                link = f"https://www.maravipost.com{link}"
            if not title:
                title = link_elem.get_text(strip=True)

        # Try to find image
        img_elem = element.find("img")
        if img_elem:
            cover_image = img_elem.get("src", "") or img_elem.get("data-src", "")
            if cover_image and not cover_image.startswith("http"):
                cover_image = f"https://www.maravipost.com{cover_image}"

        # Try to find date
        date_elem = element.find(
            ["time", "span"], class_=lambda x: x and "date" in str(x).lower()
        )
        if date_elem:
            datetime_attr = date_elem.get("datetime")
            if datetime_attr:
                published_date = datetime_attr
            else:
                published_date = date_elem.get_text(strip=True)

        return {
            "title": title,
            "link": link,
            "author": author,
            "published_date": published_date or datetime.now().strftime("%Y-%m-%d"),
            "cover_image": cover_image,
        }
