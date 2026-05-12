import pytest
from agents.ranking_agent import rank_books

SAMPLE_CANDIDATES = [
    {
        "title": "The Midnight Library",
        "author": "Matt Haig",
        "subjects": ["fiction", "fantasy", "magic", "life choices"],
        "year": 2020,
        "rating": 4.2,
        "source": "GoogleBooks"
    },
    {
        "title": "Twilight",
        "author": "Stephenie Meyer",
        "subjects": ["romance", "vampire", "fantasy", "young adult"],
        "year": 2005,
        "rating": 3.8,
        "source": "OpenLibrary"
    },
    {
        "title": "It Ends with Us",
        "author": "Colleen Hoover",
        "subjects": ["romance", "tragic love", "emotional", "contemporary"],
        "year": 2016,
        "rating": 4.4,
        "source": "GoogleBooks"
    }
]

ROMANCE_PREFERENCES = {
    "genres": ["romance"],
    "themes": ["tragic love"],
    "mood": "sad",
    "era": "contemporary"
}


def test_rank_returns_list():
    """rank_books should always return a list."""
    result = rank_books(SAMPLE_CANDIDATES, ROMANCE_PREFERENCES)
    assert isinstance(result, list)


def test_rank_returns_top_n(self=None):
    """rank_books should return at most top_n results."""
    result = rank_books(SAMPLE_CANDIDATES, ROMANCE_PREFERENCES, top_n=2)
    assert len(result) <= 2


def test_rank_adds_match_score():
    """Every ranked book should have a match_score field."""
    result = rank_books(SAMPLE_CANDIDATES, ROMANCE_PREFERENCES)
    for book in result:
        assert "match_score" in book
        assert 0 <= book["match_score"] <= 100


def test_romance_book_ranks_higher():
    """Romance book should rank higher than unrelated book for romance preferences."""
    result = rank_books(SAMPLE_CANDIDATES, ROMANCE_PREFERENCES)
    titles = [b["title"] for b in result]
    romance_idx = titles.index("It Ends with Us") if "It Ends with Us" in titles else 99
    library_idx = titles.index("The Midnight Library") if "The Midnight Library" in titles else 99
    assert romance_idx <= library_idx


def test_empty_candidates_returns_empty():
    """Empty candidates list should return empty list."""
    result = rank_books([], ROMANCE_PREFERENCES)
    assert result == []


def test_rank_with_empty_preferences():
    """Should handle empty preferences without crashing."""
    result = rank_books(SAMPLE_CANDIDATES, {})
    assert isinstance(result, list)