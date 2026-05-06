import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
MAX_CANDIDATES = 20
TOP_RESULTS = 3

# Scoring weights used by RankingAgent
SCORING_WEIGHTS = {
    "genre_match": 0.35,
    "theme_overlap": 0.30,
    "rating": 0.20,
    "era_relevance": 0.15
}