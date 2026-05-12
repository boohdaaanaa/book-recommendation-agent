"""
OpenLibrary API tool.
Searches books by query and optional author/year filters.
"""
import requests


def search_openlibrary(query: str, max_results: int = 10,
                       year_from: int = None, author: str = None) -> list[dict]:
    """
    Search OpenLibrary for books matching the query.

    Args:
        query: Search string
        max_results: Maximum number of books to return
        year_from: Only return books published after this year
        author: Filter by author name

    Returns:
        List of book dictionaries
    """
    url = "https://openlibrary.org/search.json"

    params = {
        "limit": max_results * 3,
        "fields": "title,author_name,subject,first_publish_year,ratings_average,edition_count,isbn"
    }

    if author:
        params["author"] = author
        params["q"] = query if query and query != "fiction" else "novel"
    else:
        params["q"] = query

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        books = []
        for doc in data.get("docs", []):
            # Use first_publish_year — this is the ORIGINAL publication year
            year = doc.get("first_publish_year")

            # Skip if year filter is set and book is too old
            if year_from and year and year < year_from:
                continue

            # Fetch description from works API if available
            description = ""
            work_key = doc.get("key", "")
            if work_key:
                description = fetch_openlibrary_description(work_key)

            books.append({
                "title": doc.get("title", "Unknown"),
                "author": doc.get("author_name", ["Unknown"])[0] if doc.get("author_name") else "Unknown",
                "subjects": doc.get("subject", [])[:5],
                "year": year,
                "rating": round(doc.get("ratings_average", 0.0) or 0.0, 1),
                "description": description,
                "source": "OpenLibrary"
            })

            if len(books) >= max_results:
                break

        return books

    except requests.exceptions.Timeout:
        print("  OpenLibrary request timed out.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"  OpenLibrary API error: {e}")
        return []


def fetch_openlibrary_description(work_key: str) -> str:
    """
    Fetch book description from OpenLibrary works API.

    Args:
        work_key: OpenLibrary work key e.g. /works/OL123W

    Returns:
        Short description string or empty string
    """
    try:
        url = f"https://openlibrary.org{work_key}.json"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        desc = data.get("description", "")
        if isinstance(desc, dict):
            desc = desc.get("value", "")
        if desc:
            return desc[:300].strip()
        return ""
    except Exception:
        return ""