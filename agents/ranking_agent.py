"""
RankingAgent — scores and ranks candidate books against user preferences.
Uses the weighted scoring calculator tool.
"""
from tools.scoring_tool import score_books
from config import TOP_RESULTS

MIN_SCORE = 20.0  # reject books below this score


def rank_books(candidates: list[dict], preferences: dict, top_n: int = TOP_RESULTS) -> list[dict]:
    """
    Score all candidate books and return the top matches.
    Filters out books below minimum relevance threshold.

    Args:
        candidates: List of candidate books from SearchAgent
        preferences: Structured user preferences from InputParserAgent
        top_n: Number of top results to return

    Returns:
        Top N ranked books with match_score field added
    """
    if not candidates:
        return []

    print(f"  Scoring {len(candidates)} candidates...")
    ranked = score_books(candidates, preferences)

    # Filter out clearly irrelevant results
    relevant = [b for b in ranked if b["match_score"] >= MIN_SCORE]

    if not relevant:
        print(f"  No books above minimum score {MIN_SCORE}, returning best available.")
        relevant = ranked[:top_n]

    top = relevant[:top_n]
    print(f"  Top match: '{top[0]['title']}' with score {top[0]['match_score']}/100")
    return top