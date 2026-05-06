from config import SCORING_WEIGHTS

"""
    Score and rank candidate books against user preferences.

    Scoring weights:
        genre_match:   35%
        theme_overlap: 30%
        rating:        20%
        era_relevance: 15%

    Args:
        candidates: List of book dictionaries from APIs
        preferences: Structured preferences from InputParserAgent

    Returns:
        Sorted list of books with added match_score field
"""

def score_books(candidates: list[dict], preferences: dict) -> list[dict]:

    preferred_genres = [g.lower() for g in preferences.get("genres", [])]
    preferred_themes = [t.lower() for t in preferences.get("themes", [])]
    preferred_era = preferences.get("era", None)

    scored = []
    for book in candidates:
        subjects = [s.lower() for s in book.get("subjects", [])]

        # Genre match score
        genre_hits = sum(1 for g in preferred_genres if any(g in s for s in subjects))
        genre_score = min(genre_hits / max(len(preferred_genres), 1), 1.0)

        # Theme overlap score
        theme_hits = sum(1 for t in preferred_themes if any(t in s for s in subjects))
        theme_score = min(theme_hits / max(len(preferred_themes), 1), 1.0)

        # Rating score (normalize from 0-5 to 0-1)
        raw_rating = book.get("rating", 0.0) or 0.0
        rating_score = min(raw_rating / 5.0, 1.0)

        # Era relevance score
        era_score = 0.5
        if preferred_era and book.get("year"):
            era_ranges = {
                "classic": (1800, 1970),
                "modern": (1970, 2010),
                "contemporary": (2010, 2025)
            }
            if preferred_era.lower() in era_ranges:
                start, end = era_ranges[preferred_era.lower()]
                era_score = 1.0 if start <= book["year"] <= end else 0.0

        # Final weighted score
        final_score = (
            genre_score * SCORING_WEIGHTS["genre_match"] +
            theme_score * SCORING_WEIGHTS["theme_overlap"] +
            rating_score * SCORING_WEIGHTS["rating"] +
            era_score * SCORING_WEIGHTS["era_relevance"]
        )

        book["match_score"] = round(final_score * 100, 1)
        scored.append(book)

    return sorted(scored, key=lambda x: x["match_score"], reverse=True)


def deduplicate_books(books: list[dict]) -> list[dict]:
    """Remove duplicate books by title and author."""
    seen = set()
    unique = []
    for book in books:
        key = (book["title"].lower(), book["author"].lower())
        if key not in seen:
            seen.add(key)
            unique.append(book)
    return unique