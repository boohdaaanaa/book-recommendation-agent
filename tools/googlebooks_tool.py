"""
Google Books API tool.
Searches books with retry logic and author/year filtering.
"""
import time
import requests
from config import GOOGLE_BOOKS_API_KEY


def search_google_books(query: str, max_results: int = 10,
                        year_from: int = None, author: str = None) -> list[dict]:
    """
    Search Google Books for books matching the query.

    Args:
        query: Search string
        max_results: Maximum number of books to return
        year_from: Only return books published after this year
        author: Filter by author name

    Returns:
        List of book dictionaries
    """
    # Build query — inauthor: works well in Google Books
    if author:
        search_query = f'inauthor:"{author}"'
        if query and query != "fiction":
            search_query += f" {query}"
    else:
        search_query = query

    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": search_query,
        "maxResults": max_results,
        "printType": "books",
        "langRestrict": "en",
        "orderBy": "relevance"
    }

    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY

    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code in [500, 502, 503]:
                print(f"  Google Books temporarily unavailable, retrying ({attempt + 1}/3)...")
                time.sleep(3)
                continue

            if response.status_code == 429:
                print("  Google Books rate limited, skipping.")
                return []

            response.raise_for_status()
            data = response.json()

            books = []
            for item in data.get("items", []):
                info = item.get("volumeInfo", {})

                # Parse publication year correctly
                year = parse_year(info.get("publishedDate", ""))

                # Apply year filter
                if year_from and year and year < year_from:
                    continue

                description = info.get("description", "")
                if description:
                    description = description[:300].strip()

                books.append({
                    "title": info.get("title", "Unknown"),
                    "author": info.get("authors", ["Unknown"])[0] if info.get("authors") else "Unknown",
                    "subjects": info.get("categories", []),
                    "year": year,
                    "rating": info.get("averageRating", 0.0) or 0.0,
                    "description": description,
                    "source": "GoogleBooks"
                })

            return books

        except requests.exceptions.Timeout:
            print(f"  Google Books timed out (attempt {attempt + 1}/3).")
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"  Google Books API error: {e}")
            return []

    print("  Google Books unavailable after 3 attempts, skipping.")
    return []


def parse_year(date_str: str) -> int | None:
    """
    Safely parse year from Google Books date string.
    Handles formats: '2019', '2019-05', '2019-05-21'

    Args:
        date_str: Raw date string from API

    Returns:
        Year as integer or None
    """
    if not date_str:
        return None
    try:
        return int(date_str[:4])
    except (ValueError, IndexError):
        return None