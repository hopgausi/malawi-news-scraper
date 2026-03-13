"""
Article Summarizer Module

Fetches full article content from URLs and generates 2-3 paragraph summaries.
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
            text = "\n\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

            # Clean up extra whitespace
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\n\s*\n", "\n\n", text)

            socket.setdefaulttimeout(old_timeout)

            if not text or len(text) < 50:
                return {"content": None, "error": "Article text too short or empty"}

            return {"content": text, "error": None}

        except socket.timeout:
            return {"content": None, "error": "Timeout fetching article"}
        except urllib.error.URLError as e:
            return {"content": None, "error": f"URL error: {str(e)[:50]}"}
        except Exception as e:
            return {"content": None, "error": f"Error: {str(e)[:50]}"}
        finally:
            socket.setdefaulttimeout(old_timeout)

    def summarize_text(self, text: str, num_sentences: int = 5) -> str:
        """
        Summarize text into specified number of sentences.

        Args:
            text: The full article text
            num_sentences: Number of sentences in summary (default 5 for ~2-3 paragraphs)

        Returns:
            Summary text or original text if summarization fails
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

                summary_sentences = summarizer(parser.document, num_sentences)
                summary = " ".join([str(sentence) for sentence in summary_sentences])

                # Format into paragraphs (2-3 sentences per paragraph)
                sentences = summary.split(". ")
                paragraphs = []
                current_para = []

                for i, sent in enumerate(sentences):
                    current_para.append(sent if sent.endswith(".") else sent + ".")
                    # Create paragraph every 2-3 sentences
                    if len(current_para) >= 2 and (i == len(sentences) - 1 or len(current_para) >= 3):
                        paragraphs.append(" ".join(current_para))
                        current_para = []

                # Add remaining sentences
                if current_para:
                    paragraphs.append(" ".join(current_para))

                return "\n\n".join(paragraphs)

            except Exception as e:
                # Fall back to simple extraction
                pass

        # Simple fallback: extract first few sentences
        sentences = re.split(r"(?<=[.!?])\s+", text)
        summary_sentences = sentences[: min(num_sentences, len(sentences))]
        summary = " ".join(summary_sentences)

        # Format into 2-3 paragraphs
        words = summary.split()
        third = len(words) // 3
        if third > 0 and len(words) > 20:
            para1 = " ".join(words[:third])
            para2 = " ".join(words[third : third * 2])
            para3 = " ".join(words[third * 2 :])
            return f"{para1}\n\n{para2}\n\n{para3}"
        elif len(words) > 10:
            # Split into 2 paragraphs
            half = len(words) // 2
            para1 = " ".join(words[:half])
            para2 = " ".join(words[half:])
            return f"{para1}\n\n{para2}"
        else:
            return summary

    def get_article_summary(self, url: str, num_sentences: int = 5) -> dict:
        """
        Fetch article and generate summary.

        Args:
            url: Article URL
            num_sentences: Number of sentences in summary

        Returns:
            dict with 'summary', 'error', and 'full_content'
        """
        # Fetch content
        result = self.fetch_article_content(url)

        if result["error"]:
            return {"summary": None, "error": result["error"], "full_content": None}

        content = result["content"]

        # Generate summary
        summary = self.summarize_text(content, num_sentences)

        return {"summary": summary, "error": None, "full_content": content}
