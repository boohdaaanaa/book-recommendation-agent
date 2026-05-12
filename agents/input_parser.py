"""
InputParserAgent — extracts structured preferences from raw user input.
Uses Groq API (free) with keyword-based fallback.
"""
import re
import json
from datetime import datetime
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

CURRENT_YEAR = datetime.now().year

GENRE_KEYWORDS = {
    "fantasy": ["dragon", "magic", "wizard", "quest", "elf", "fairy", "princess", "kingdom", "spell", "enchanted"],
    "thriller": ["thriller", "suspense", "murder", "crime", "detective", "mystery", "killer"],
    "romance": ["romance", "love", "relationship", "wedding", "heart", "tears", "cry", "sad", "tragic"],
    "sci-fi": ["space", "robot", "future", "alien", "galaxy", "science fiction", "dystopia"],
    "horror": ["horror", "scary", "haunted", "ghost", "vampire", "demon"],
    "historical": ["historical", "war", "medieval", "ancient", "century", "empire"],
    "adventure": ["adventure", "journey", "expedition", "survival", "explore"],
}

MOOD_KEYWORDS = {
    "sad": ["sad", "tears", "cry", "tragic", "tragedy", "heartbreak", "bad ending", "death"],
    "dark": ["dark", "darker", "grim", "gritty", "depressing", "bleak"],
    "light": ["light", "fun", "funny", "cozy", "feel-good", "happy", "fairy", "princess"],
    "tense": ["tense", "gripping", "suspenseful", "intense"],
    "epic": ["epic", "grand", "massive"],
}

THEME_KEYWORDS = {
    "tragic love": ["bad ending", "sad ending", "heartbreak", "tragic love", "unrequited"],
    "loss": ["loss", "grief", "death", "dies", "missing"],
    "fairy tale": ["fairy", "princess", "enchanted", "magic", "castle"],
    "blood": ["blood", "bloody", "gore"],
}

ERA_KEYWORDS = {
    "classic": ["classic", "old", "vintage", "19th", "18th"],
    "modern": ["modern", "contemporary", "recent", "new", "latest"],
}

# Year pattern map — maps phrases to years_back
YEAR_PATTERNS = [
    (r"last\s+(\d+)\s+years?", lambda m: CURRENT_YEAR - int(m.group(1))),
    (r"past\s+(\d+)\s+years?", lambda m: CURRENT_YEAR - int(m.group(1))),
    (r"(\d+)\s+years?\s+ago", lambda m: CURRENT_YEAR - int(m.group(1))),
    (r"published\s+in\s+(\d{4})", lambda m: int(m.group(1))),
    (r"since\s+(\d{4})", lambda m: int(m.group(1))),
    (r"after\s+(\d{4})", lambda m: int(m.group(1))),
    (r"last\s+year", lambda m: CURRENT_YEAR - 1),
    (r"this\s+year", lambda m: CURRENT_YEAR),
    (r"recent(ly)?", lambda m: CURRENT_YEAR - 3),
]


def detect_year_filter(user_input: str) -> int | None:
    """
    Detect if user wants books from a specific recent time period.
    Handles: 'last 5 years', 'past 3 years', '5 years ago', 'since 2020', etc.

    Returns:
        Year as integer (books published FROM this year) or None
    """
    text = user_input.lower()
    for pattern, year_func in YEAR_PATTERNS:
        match = re.search(pattern, text)
        if match:
            year = year_func(match)
            print(f"  Detected year filter: published after {year}")
            return year
    return None


def detect_author(user_input: str) -> str | None:
    """
    Detect author name from user input.
    Handles: 'by X', 'author is X', 'written by X', 'from author X'

    Returns:
        Author name string or None
    """
    text = user_input.lower()
    patterns = [
        r"by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
        r"author\s+is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
        r"written\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
        r"from\s+author\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
    ]
    for pattern in patterns:
        match = re.search(pattern, user_input)
        if match:
            author = match.group(1).strip()
            print(f"  Detected author: '{author}'")
            return author
    return None


def keyword_fallback_parser(user_input: str) -> dict:
    """Rule-based fallback parser when AI API is unavailable."""
    text = user_input.lower()

    detected_genres = []
    for genre, keywords in GENRE_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            detected_genres.append(genre)

    detected_mood = "neutral"
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            detected_mood = mood
            break

    detected_themes = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            detected_themes.append(theme)

    detected_era = None
    for era, keywords in ERA_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            detected_era = era
            break

    year_from = detect_year_filter(user_input)
    author = detect_author(user_input)
    all_themes = list(set(detected_genres + detected_themes))

    print(f"  [Fallback] genres={detected_genres}, mood={detected_mood}, themes={all_themes}, author={author}, year_from={year_from}")

    return {
        "genres": detected_genres if detected_genres else ["fiction"],
        "themes": all_themes,
        "mood": detected_mood,
        "era": detected_era,
        "year_from": year_from,
        "author": author,
        "reference_books": [],
        "exclusions": []
    }


def parse_user_input(user_input: str, past_preferences: list[dict] = None) -> dict:
    """Parse raw user input using Groq AI, with keyword fallback."""
    history_context = ""
    if past_preferences:
        history_context = f"\nUser previously enjoyed: {json.dumps(past_preferences)}"

    prompt = f"""Extract book preferences from this input as JSON only. No explanation.

Input: "{user_input}"
Current year: {CURRENT_YEAR}

Return this exact JSON structure:
{{
  "genres": ["genres like romance, fantasy, thriller, sci-fi, horror, historical"],
  "themes": ["themes like tragic love, loss, fairy tale, magic, crime"],
  "mood": "one of: sad, dark, light, tense, epic, neutral",
  "era": "one of: classic, modern, contemporary, or null",
  "author": "author name if mentioned or null",
  "year_from": null or integer year (e.g. if user says 'last 5 years' return {CURRENT_YEAR - 5}, 'last 3 years' return {CURRENT_YEAR - 3}, '5 years ago' return {CURRENT_YEAR - 5}),
  "reference_books": ["book titles mentioned as examples"],
  "exclusions": ["things to avoid"]
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.1
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)

        # Always run our own detectors as backup — more reliable than LLM for these
        if not result.get("year_from"):
            result["year_from"] = detect_year_filter(user_input)
        if not result.get("author"):
            result["author"] = detect_author(user_input)

        return result

    except json.JSONDecodeError:
        print("  Could not parse Groq response, using keyword fallback.")
        return keyword_fallback_parser(user_input)
    except Exception as e:
        print(f"  Groq unavailable ({type(e).__name__}), using keyword fallback.")
        return keyword_fallback_parser(user_input)


def build_search_query(preferences: dict) -> str:
    """Convert structured preferences into a focused search query string."""
    parts = []

    # Add reference books — strongest signal
    if preferences.get("reference_books"):
        parts.append(preferences["reference_books"][0])

    # Add genres (max 2)
    for g in preferences.get("genres", [])[:2]:
        if g and g not in " ".join(parts):
            parts.append(g)

    # Add themes (max 2)
    for t in preferences.get("themes", [])[:2]:
        if t and t not in " ".join(parts):
            parts.append(t)

    query = " ".join(parts[:4]) if parts else "fiction"
    print(f"  Search query: '{query}'")
    return query