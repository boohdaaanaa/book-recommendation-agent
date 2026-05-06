import requests

"""
    Search OpenLibrary for books matching the query.

    Args:
        query: Search string built from user preferences
        max_results: Maximum number of books to return

    Returns:
        List of book dictionaries with title, author, subjects, year
"""

def search_openlibrary(query: str, max_results: int = 10) -> list[dict]:


    url = "https://openlibrary.org/search.json"
    params = {"q": query, "limit": max_results, "fields": "title,author_name,subject,first_publish_year,ratings_average"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        books = []
        for doc in data.get("docs", []):
            books.append({
                "title": doc.get("title", "Unknown"),
                "author": doc.get("author_name", ["Unknown"])[0] if doc.get("author_name") else "Unknown",
                "subjects": doc.get("subject", [])[:5],
                "year": doc.get("first_publish_year", None),
                "rating": doc.get("ratings_average", 0.0),
                "source": "OpenLibrary"
            })
        return books

    except requests.exceptions.Timeout:
        print("OpenLibrary request timed out.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"OpenLibrary API error: {e}")
        return []