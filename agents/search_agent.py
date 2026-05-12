"""
SearchAgent — queries book APIs using structured preferences.
Combines results from OpenLibrary and Google Books.
"""
from tools.openlibrary_tool import search_openlibrary
from tools.googlebooks_tool import search_google_books
from tools.scoring_tool import deduplicate_books
from config import MAX_CANDIDATES


def search_books(query: str, year_from: int = None, author: str = None) -> list[dict]:
    """
    Search both APIs and merge results.

    Args:
        query: Search string
        year_from: Only return books published after this year
        author: Filter by author name

    Returns:
        Deduplicated list of candidate books
    """
    half = MAX_CANDIDATES // 2

    print(f"  Searching OpenLibrary...")
    openlibrary_results = search_openlibrary(
        query, max_results=half, year_from=year_from, author=author
    )

    print(f"  Searching Google Books...")
    google_results = search_google_books(
        query, max_results=half, year_from=year_from, author=author
    )

    combined = openlibrary_results + google_results
    unique = deduplicate_books(combined)
    print(f"  Found {len(unique)} unique candidates.")
    return unique