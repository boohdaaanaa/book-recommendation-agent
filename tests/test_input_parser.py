import pytest
from datetime import datetime
from agents.input_parser import (
    detect_year_filter,
    detect_author,
    keyword_fallback_parser,
    build_search_query
)

CURRENT_YEAR = datetime.now().year


class TestYearDetection:
    """Tests for the detect_year_filter function."""

    def test_last_5_years(self):
        assert detect_year_filter("published in last 5 years") == CURRENT_YEAR - 5

    def test_last_3_years(self):
        assert detect_year_filter("book from last 3 years") == CURRENT_YEAR - 3

    def test_last_10_years(self):
        assert detect_year_filter("last 10 years") == CURRENT_YEAR - 10

    def test_5_years_ago(self):
        assert detect_year_filter("published 5 years ago") == CURRENT_YEAR - 5

    def test_since_year(self):
        assert detect_year_filter("since 2020") == 2020

    def test_after_year(self):
        assert detect_year_filter("after 2018") == 2018

    def test_no_year_returns_none(self):
        assert detect_year_filter("book about magic and dragons") is None

    def test_recent_keyword(self):
        result = detect_year_filter("recent books about romance")
        assert result == CURRENT_YEAR - 3

    def test_last_year(self):
        assert detect_year_filter("published last year") == CURRENT_YEAR - 1


class TestAuthorDetection:
    """Tests for the detect_author function."""

    def test_by_author(self):
        result = detect_author("something romantic by Colleen Hoover")
        assert result == "Colleen Hoover"

    def test_author_is(self):
        result = detect_author("I want a book, author is Stephen King")
        assert result is not None
        assert "Stephen" in result

    def test_written_by(self):
        result = detect_author("written by Jane Austen")
        assert result is not None
        assert "Austen" in result

    def test_no_author_returns_none(self):
        result = detect_author("book about dragons and magic")
        assert result is None


class TestKeywordFallbackParser:
    """Tests for the keyword-based fallback parser."""

    def test_romance_detected(self):
        result = keyword_fallback_parser("book about love and heartbreak")
        assert "romance" in result["genres"]

    def test_fantasy_detected(self):
        result = keyword_fallback_parser("story about dragons and magic")
        assert "fantasy" in result["genres"]

    def test_sad_mood_detected(self):
        result = keyword_fallback_parser("something with bad ending and tears")
        assert result["mood"] == "sad"

    def test_tragic_love_theme(self):
        result = keyword_fallback_parser("love story with heartbreak and bad ending")
        assert "tragic love" in result["themes"]

    def test_year_filter_in_result(self):
        result = keyword_fallback_parser("fantasy published in last 5 years")
        assert result["year_from"] == CURRENT_YEAR - 5

    def test_author_in_result(self):
        result = keyword_fallback_parser("romance by Colleen Hoover")
        assert result["author"] == "Colleen Hoover"

    def test_empty_input_returns_defaults(self):
        result = keyword_fallback_parser("")
        assert isinstance(result["genres"], list)
        assert isinstance(result["themes"], list)
        assert result["mood"] is not None

    def test_result_has_all_keys(self):
        result = keyword_fallback_parser("fantasy adventure")
        required_keys = ["genres", "themes", "mood", "era", "year_from", "author", "reference_books", "exclusions"]
        for key in required_keys:
            assert key in result


class TestBuildSearchQuery:
    """Tests for the build_search_query function."""

    def test_uses_reference_book(self):
        prefs = {"genres": ["thriller"], "themes": [], "reference_books": ["Gone Girl"]}
        query = build_search_query(prefs)
        assert "Gone Girl" in query

    def test_uses_genres_when_no_reference(self):
        prefs = {"genres": ["fantasy"], "themes": ["magic"], "reference_books": []}
        query = build_search_query(prefs)
        assert "fantasy" in query

    def test_no_duplicates_in_query(self):
        prefs = {"genres": ["romance"], "themes": ["romance", "tragic love"], "reference_books": []}
        query = build_search_query(prefs)
        assert query.count("romance") == 1

    def test_empty_preferences_returns_default(self):
        query = build_search_query({})
        assert query == "fiction"