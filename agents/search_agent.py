from tools.openlibrary_tool import search_openlibrary
from tools.googlebooks_tool import search_google_books
from tools.scoring_tool import deduplicate_books
from config import MAX_CANDIDATES

"""
    Search both OpenLibrary and Google Books APIs and merge results.

    Args:
        query: Search string built from user preferences

    Returns:
        Deduplicated list of candidate book dictionaries
"""

def search_books(query: str) -> list[dict]:

    print(f"  Searching OpenLibrary...")
    openlibrary_results = search_openlibrary(query, max_results=MAX_CANDIDATES // 2)

    print(f"  Searching Google Books...")
    google_results = search_google_books(query, max_results=MAX_CANDIDATES // 2)

    combined = openlibrary_results + google_results
    unique = deduplicate_books(combined)

    print(f"  Found {len(unique)} unique candidates.")
    return unique