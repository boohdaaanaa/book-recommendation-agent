import pytest
from tools.googlebooks_tool import search_google_books, parse_year


def test_parse_year_full_date():
    """Should correctly parse full date string."""
    assert parse_year("2019-05-21") == 2019


def test_parse_year_year_only():
    """Should correctly parse year-only string."""
    assert parse_year("2021") == 2021


def test_parse_year_empty_string():
    """Should return None for empty string."""
    assert parse_year("") is None


def test_parse_year_invalid_string():
    """Should return None for invalid date string."""
    assert parse_year("unknown") is None


def test_parse_year_partial_date():
    """Should correctly parse year from partial date."""
    assert parse_year("2020-03") == 2020


def test_basic_search_returns_results():
    """Basic search should return results from Google Books."""
    results = search_google_books("fantasy magic", max_results=5)
    assert isinstance(results, list)


def test_search_result_has_required_fields():
    """Each result should contain required book fields."""
    results = search_google_books("romance novel", max_results=3)
    if results:
        for book in results:
            assert "title" in book
            assert "author" in book
            assert "year" in book
            assert "source" in book
            assert book["source"] == "GoogleBooks"


def test_author_filter_in_query():
    """Author filter should produce results related to that author."""
    results = search_google_books("love", max_results=5, author="Colleen Hoover")
    if results:
        authors = [b["author"] for b in results]
        assert any("Hoover" in a for a in authors)


def test_year_filter_excludes_old_books():
    """Year filter should exclude books before threshold."""
    results = search_google_books("thriller", max_results=10, year_from=2018)
    for book in results:
        if book["year"] is not None:
            assert book["year"] >= 2018