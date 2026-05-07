from tools.scoring_tool import score_books
from config import TOP_RESULTS

"""
    Score all candidate books and return the top matches.

    Args:
        candidates: List of candidate books from SearchAgent
        preferences: Structured user preferences from InputParserAgent
        top_n: Number of top results to return

    Returns:
        Top N ranked books with match_score field added
"""

def rank_books(candidates: list[dict], preferences: dict, top_n: int = TOP_RESULTS) -> list[dict]:

    if not candidates:
        return []

    print(f"  Scoring {len(candidates)} candidates...")
    ranked = score_books(candidates, preferences)
    top = ranked[:top_n]

    print(f"  Top match: '{top[0]['title']}' with score {top[0]['match_score']}/100")
    return top