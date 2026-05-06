import requests
from config import GOOGLE_BOOKS_API_KEY

"""
    Search Google Books for books matching the query.

    Args:
        query: Search string built from user preferences
        max_results: Maximum number of books to return

    Returns:
        List of book dictionaries with title, author, description, rating
"""

def search_google_books(query: str, max_results: int = 10) -> list[dict]:
 
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results,
        "key": GOOGLE_BOOKS_API_KEY,
        "printType": "books",
        "langRestrict": "en"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        books = []
        for item in data.get("items", []):
            info = item.get("volumeInfo", {})
            books.append({
                "title": info.get("title", "Unknown"),
                "author": info.get("authors", ["Unknown"])[0] if info.get("authors") else "Unknown",
                "subjects": info.get("categories", []),
                "year": int(info.get("publishedDate", "0")[:4]) if info.get("publishedDate") else None,
                "rating": info.get("averageRating", 0.0),
                "description": info.get("description", "")[:300],
                "source": "GoogleBooks"
            })
        return books

    except requests.exceptions.Timeout:
        print("Google Books request timed out.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"Google Books API error: {e}")
        return []