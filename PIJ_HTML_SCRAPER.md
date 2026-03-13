# PIJ HTML Scraper Implementation

## Problem Statement

The PIJ RSS feed had broken links - all 309 articles pointed to the same URL (`https://www.pijmalawi.org/blog`), which returned a 404 error. This made the articles unusable even though the scraper could fetch them.

## Solution

Replaced the RSS feed parsing approach with custom HTML scraping for PIJ only.

### What Changed

**File:** `src/scrapers/pij.py`

The `PijParser` class now:

1. **Overrides `scrape_news()`** - Instead of using the RSS feed, it fetches the HTML page from `https://www.pijmalawi.org/all-stories`

2. **Uses BeautifulSoup** - Parses the HTML to extract article information directly from the page structure

3. **Targets specific elements** - Looks for `<article class="story-card">` elements which contain real articles

4. **Extracts article data** from:
   - Title: From `<img class="story-image">` alt text
   - Link: From `<h3 class="story-title"> > <a>` href attribute
   - Image: From `<img class="story-image">` src attribute
   - Date: From `<span class="*date*">` elements
   - Author: Defaults to "Platform For Investigative Journalism"

5. **Filters out navigation elements** - Skips links ending with `#` which are navigation items

### Results

Before:

- ❌ 309 articles
- ❌ All articles had the same link
- ❌ Links returned 404 errors

After:

- ✅ 12 unique articles
- ✅ All links are unique (100% unique)
- ✅ All links work and point to real articles
- ✅ Articles include titles, dates, images, and proper URLs

### Performance

- Fetch time: ~1.6-4.2 seconds (much faster than timeout)
- Timeout: 10 seconds (enforced at socket level)
- Articles per request: 12 working articles vs 309 broken ones

### Code Structure

```python
class PijParser(BaseParser):
    def get_link(self):
        """Still returns RSS URL for backwards compatibility"""
        return scrapers.PIJ_URL

    def scrape_news(self) -> dict:
        """Custom HTML scraper for PIJ"""
        # 1. Fetch HTML from all-stories page
        # 2. Parse with BeautifulSoup
        # 3. Extract articles
        # 4. Return standardized format

    def _parse_pij_html(self, soup, base_url) -> list:
        """Find article containers and extract data"""

    def _extract_article_data(self, element, base_url) -> dict:
        """Extract title, link, image, date from article element"""
```

### Testing

Test PIJ scraping using the examples script:

```bash
python examples.py
# Select option 5 (PIJ) to test PIJ specifically
# Or wait for Example 2/3 which scrape all sources including PIJ
```

### Future Maintenance

If the PIJ website structure changes, you may need to update:

1. **URL**: Change `html_url` in `scrape_news()` if the all-stories page moves
2. **Selectors**: Update `find_all('article', class_='story-card')` if the HTML class names change
3. **Field extraction**: Update `_extract_article_data()` if the article structure changes

To diagnose structure changes, you can:

- Manually inspect the page source at https://www.pijmalawi.org/all-stories
- Use browser developer tools to inspect article elements
- Test with `python examples.py` and select PIJ to see if articles are still being extracted correctly

### Dependencies

- **beautifulsoup4**: Already a project dependency, used for HTML parsing
- **urllib.request**: Python standard library, used for HTTP requests
- **socket**: Python standard library, used for timeout enforcement

No new dependencies were added.
