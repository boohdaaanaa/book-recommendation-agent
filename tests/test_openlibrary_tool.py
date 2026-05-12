import pytest
from tools.openlibrary_tool import search_openlibrary, fetch_openlibrary_description


def test_basic_search_returns_results():
    """Basic search should return a non-empty list of books."""
    results = search_openlibrary("fantasy magic", max_results=5)
    assert isinstance(results, list)
    assert len(results) > 0


def test_search_returns_correct_fields():
    """Each book should have all required fields."""
    results = search_openlibrary("romance", max_results=3)
    for book in results:
        assert "title" in book
        assert "author" in book
        assert "year" in book
        assert "rating" in book
        assert "source" in book
        assert book["source"] == "OpenLibrary"


def test_author_filter_returns_correct_author():
    """Author filter should only return books by that author."""
    results = search_openlibrary("romance", max_results=5, author="Colleen Hoover")
    for book in results:
        assert "Hoover" in book["author"] or "Colleen" in book["author"]


def test_year_filter_excludes_old_books():
    """Year filter should exclude books published before the threshold."""
    year_threshold = 2015
    results = search_openlibrary("thriller", max_results=10, year_from=year_threshold)
    for book in results:
        if book["year"] is not None:
            assert book["year"] >= year_threshold


def test_empty_query_does_not_crash():
    """Empty query should return empty list without crashing."""
    results = search_openlibrary("", max_results=5)
    assert isinstance(results, list)


def test_max_results_respected():
    """Result count should not exceed max_results."""
    results = search_openlibrary("fiction", max_results=4)
    assert len(results) <= 4