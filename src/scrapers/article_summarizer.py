"""
Article Summarizer Module

Fetches full article content from URLs and generates two types of summaries:
1. Short teaser (~150 chars) for introducing the article
2. Longer overview (3-4 sentences) for getting the full picture
"""

import urllib.request
import urllib.error
import socket
from bs4 import BeautifulSoup
import re

# Try to import sumy (optional dependency for better summarization)
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    from sumy.nlp.stemmers import Stemmer
    from sumy.utils import get_stop_words

    SUMY_AVAILABLE = True
except ImportError:
    SUMY_AVAILABLE = False


class ArticleSummarizer:
    """Fetches and summarizes news articles"""

    def __init__(self, timeout=10):
        """
        Initialize the article summarizer.

        Args:
            timeout: Timeout in seconds for fetching articles
        """
        self.timeout = timeout

    def fetch_article_content(self, url: str) -> dict:
        """
        Fetch full article content from a URL.

        Args:
            url: The article URL

        Returns:
            dict with 'content' (str) and 'error' (str or None)
        """
        if not url or url == "":
            return {"content": None, "error": "No URL provided"}

        try:
            # Set timeout
            old_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(self.timeout)

            # Fetch the page
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                },
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html = response.read()

            # Parse HTML
            soup = BeautifulSoup(html, "html.parser")

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()

            # Try to find main content area (common HTML5 patterns)
            article_content = None

            # Try common article containers
            for selector in [
                "article",
                '[role="main"]',
                ".post-content",
                ".article-content",
                ".entry-content",
                ".story-body",
                '[itemprop="articleBody"]',
            ]:
                content = soup.select_one(selector)
                if content:
                    article_content = content
                    break

            # Fallback to body if no article container found
            if not article_content:
                article_content = soup.find("body")

            if not article_content:
                return {"content": None, "error": "Could not extract article content"}

            # Extract text from paragraphs
            paragraphs = article_content.find_all("p")
            text = "\n\n".join(
                [p.get_text().strip() for p in paragraphs if p.get_text().strip()]
            )

            # Clean up extra whitespace
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\n\s*\n", "\n\n", text)

            # Extract author if present (common byline patterns)
            # Handles single or multiple authors with various separators:
            # - BY AUTHOR NAME
            # - BY AUTHOR1 AND AUTHOR2
            # - BY AUTHOR1 & AUTHOR2
            # - BY AUTHOR1, AUTHOR2 AND AUTHOR3
            # - BY AUTHOR1, AUTHOR2, AND AUTHOR3 (Oxford comma)
            author = None

            # Try all-caps pattern first (most common in news):
            # BY [CAPS NAME] (comma/AND/&) [CAPS NAME] ...
            # Matches everything from BY until we hit a sentence start (capital followed by lowercase)
            author_match = re.search(
                r"BY\s+((?:[A-Z\u00c0-\u017f\'\u2019\-]+\s+(?:,\s*|AND\s+|&\s+)?)+[A-Z\u00c0-\u017f\'\u2019\-]+)(?=\s+[A-Z][a-z]|\s+The|\s*$)",
                text,
            )

            if not author_match:
                # Try mixed-case pattern: BY [Name Name] (comma/and/&) [Name Name]
                author_match = re.search(
                    r"BY\s+((?:[A-Z][a-z\u00c0-\u017f\'\u2019\-]+\s+(?:,\s*|and\s+|&\s+)?)+[A-Z][a-zA-Z\u00c0-\u017f\'\u2019\-]+)(?=\s+[a-z]|\s+[A-Z][a-z]|\s*$)",
                    text,
                    re.IGNORECASE,
                )

            if author_match:
                author = author_match.group(1).strip()
                # Clean up extra spaces around separators
                author = re.sub(r"\s+", " ", author)
                author = re.sub(r"\s*,\s*", ", ", author)  # Normalize comma spacing

            # Clean bylines from text before summarization
            # Remove entire byline including multiple authors with comma/AND/&
            text = re.sub(
                r"BY\s+(?:[A-Z\u00c0-\u017f\'\u2019\-]+\s+(?:,\s*|AND\s+|&\s+)?)+[A-Z\u00c0-\u017f\'\u2019\-]+\s*",
                "",
                text,
            )
            text = re.sub(
                r"BY\s+(?:[A-Z][a-z\u00c0-\u017f\'\u2019\-]+\s+(?:,\s*|and\s+|&\s+)?)+[A-Z][a-zA-Z\u00c0-\u017f\'\u2019\-]+\s*",
                "",
                text,
                flags=re.IGNORECASE,
            )
            text = re.sub(r"\s+", " ", text).strip()

            socket.setdefaulttimeout(old_timeout)

            if not text or len(text) < 50:
                return {"content": None, "error": "Article text too short or empty"}

            return {"content": text, "author": author, "error": None}

        except socket.timeout:
            return {"content": None, "error": "Timeout fetching article"}
        except urllib.error.URLError as e:
            return {"content": None, "error": f"URL error: {str(e)[:50]}"}
        except Exception as e:
            return {"content": None, "error": f"Error: {str(e)[:50]}"}
        finally:
            socket.setdefaulttimeout(old_timeout)

    def summarize_text(
        self, text: str, num_sentences: int = 2, short: bool = False
    ) -> str:
        """
        Summarize text into a single catchy paragraph.

        Args:
            text: The full article text
            num_sentences: Number of sentences in summary
            short: If True, generate a very short teaser (under 150 chars)

        Returns:
            Summary text as a single engaging paragraph
        """
        if not text:
            return ""

        # If sumy is available, use LSA summarization
        if SUMY_AVAILABLE:
            try:
                parser = PlaintextParser.from_string(text, Tokenizer("english"))
                stemmer = Stemmer("english")
                summarizer = LsaSummarizer(stemmer)
                summarizer.stop_words = get_stop_words("english")

                # Generate based on type requested
                if short:
                    # Very short teaser - just key phrase or half sentence
                    summary_sentences = summarizer(parser.document, 1)
                    sentences_list = [
                        str(sentence).strip() for sentence in summary_sentences
                    ]
                    summary = sentences_list[0] if sentences_list else ""

                    # Trim to under 150 chars at natural break
                    if len(summary) > 150:
                        for break_char in [",", ";", "—", " - ", " and ", " but "]:
                            truncate_at = summary[:147].rfind(break_char)
                            if truncate_at > 50:
                                summary = summary[:truncate_at] + "..."
                                break
                        else:
                            truncate_at = summary[:147].rfind(" ")
                            summary = (
                                summary[:truncate_at] + "..."
                                if truncate_at > 50
                                else summary[:147] + "..."
                            )
                else:
                    # Longer overview - 3-4 sentences
                    summary_sentences = summarizer(parser.document, 4)
                    sentences_list = [
                        str(sentence).strip() for sentence in summary_sentences
                    ]
                    summary = " ".join(sentences_list)

                # Ensure proper sentence endings
                summary = re.sub(r"\s+", " ", summary).strip()
                if not summary.endswith((".", "!", "?", "...")):
                    summary += "."

                return summary

            except Exception as e:
                # Fall back to simple extraction
                pass

        # Simple fallback: extract sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)

        # Clean and filter sentences (remove very short ones)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if not sentences:
            return text[:200] + "..." if len(text) > 200 else text

        if short:
            # Very short teaser - first sentence trimmed to under 150 chars
            summary = sentences[0]

            if len(summary) > 150:
                # Try to find a natural break
                for break_char in [",", ";", "—", " - ", " and ", " but "]:
                    truncate_at = summary[:147].rfind(break_char)
                    if truncate_at > 50:
                        summary = summary[:truncate_at] + "..."
                        break
                else:
                    truncate_at = summary[:147].rfind(" ")
                    summary = (
                        summary[:truncate_at] + "..."
                        if truncate_at > 50
                        else summary[:147] + "..."
                    )
        else:
            # Longer overview - first 3-4 sentences
            num_to_use = min(4, len(sentences))
            summary = " ".join(sentences[:num_to_use])

        # Clean up and ensure proper ending
        summary = re.sub(r"\s+", " ", summary).strip()
        if not summary.endswith((".", "!", "?", "...")):
            summary += "."

        return summary

    def get_article_summary(self, url: str) -> dict:
        """
        Fetch article and generate both short teaser and longer overview summaries.

        Args:
            url: Article URL

        Returns:
            dict with 'summary_short' (teaser), 'summary_long' (overview),
            'author' (extracted from content if present), 'error', and 'full_content'
        """
        # Fetch content
        result = self.fetch_article_content(url)

        if result["error"]:
            return {
                "summary_short": None,
                "summary_long": None,
                "author": None,
                "error": result["error"],
                "full_content": None,
            }

        content = result["content"]
        author = result.get("author")

        # Generate both types of summaries
        try:
            summary_short = self.summarize_text(content, num_sentences=1, short=True)
            summary_long = self.summarize_text(content, num_sentences=4, short=False)
        except Exception as e:
            return {
                "summary_short": None,
                "summary_long": None,
                "author": author,
                "error": f"Summarization failed: {str(e)[:50]}",
                "full_content": content,
            }

        return {
            "summary_short": summary_short,
            "summary_long": summary_long,
            "author": author,
            "error": None,
            "full_content": content,
        }
