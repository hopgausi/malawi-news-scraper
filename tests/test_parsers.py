"""Tests for news source parsers"""

import pytest
from scrapers import (
    MalawiVoiceParser,
    Malawi24Parser,
    MaraviPostParser,
    MwNationParser,
    PijParser,
    MALAWI_VOICE_URL,
    MALAWI24_URL,
    MARAVI_POST_URL,
    MWNATION_URL,
    PIJ_URL,
)


class TestMalawiVoiceParser:
    """Test suite for MalawiVoiceParser"""

    def test_get_link(self):
        """Test that MalawiVoiceParser returns correct URL"""
        parser = MalawiVoiceParser()
        assert parser.get_link() == MALAWI_VOICE_URL
        assert "malawivoice.com" in parser.get_link()

    def test_initialization(self):
        """Test that MalawiVoiceParser initializes correctly"""
        parser = MalawiVoiceParser()
        assert parser.link == MALAWI_VOICE_URL


class TestMalawi24Parser:
    """Test suite for Malawi24Parser"""

    def test_get_link(self):
        """Test that Malawi24Parser returns correct URL"""
        parser = Malawi24Parser()
        assert parser.get_link() == MALAWI24_URL
        assert "malawi24.com" in parser.get_link()


class TestMaraviPostParser:
    """Test suite for MaraviPostParser"""

    def test_get_link(self):
        """Test that MaraviPostParser returns correct URL"""
        parser = MaraviPostParser()
        assert parser.get_link() == MARAVI_POST_URL
        assert "maravipost.com" in parser.get_link()


class TestMwNationParser:
    """Test suite for MwNationParser"""

    def test_get_link(self):
        """Test that MwNationParser returns correct URL"""
        parser = MwNationParser()
        assert parser.get_link() == MWNATION_URL
        assert "mwnation.com" in parser.get_link()


class TestPijParser:
    """Test suite for PijParser"""

    def test_get_link(self):
        """Test that PijParser returns correct URL"""
        parser = PijParser()
        assert parser.get_link() == PIJ_URL
        assert (
            "pijmalawi.org" in parser.get_link()
            or "investigativeplatform-mw" in parser.get_link()
        )
