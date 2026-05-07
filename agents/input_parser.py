import json
import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

"""
    Parse raw user input into structured book preferences using Claude.

    Args:
        user_input: Raw natural language input from the user
        past_preferences: Optional list of past preference profiles

    Returns:
        Dictionary with keys: genres, themes, mood, era, reference_books, exclusions
"""

def parse_user_input(user_input: str, past_preferences: list[dict] = None) -> dict:

    history_context = ""
    if past_preferences:
        history_context = f"\nThe user has previously enjoyed: {json.dumps(past_preferences)}"

    prompt = f"""You are a book preference extraction assistant.
Extract structured reading preferences from the user's input.{history_context}

User input: "{user_input}"

Respond ONLY with a valid JSON object and nothing else. No explanation, no markdown.
Use this exact structure:
{{
  "genres": ["list of genres"],
  "themes": ["list of themes"],
  "mood": "overall mood or tone",
  "era": "classic or modern or contemporary or null",
  "reference_books": ["books mentioned by user"],
  "exclusions": ["anything user wants to avoid"]
}}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = response.content[0].text.strip()
        return json.loads(raw)

    except json.JSONDecodeError:
        print("Could not parse Claude response as JSON, using defaults.")
        return {
            "genres": [], "themes": [], "mood": "unknown",
            "era": None, "reference_books": [], "exclusions": []
        }
    except Exception as e:
        print(f"InputParserAgent error: {e}")
        return {
            "genres": [], "themes": [], "mood": "unknown",
            "era": None, "reference_books": [], "exclusions": []
        }

"""
    Convert structured preferences into a search query string.

    Args:
        preferences: Structured preference dictionary

    Returns:
        Search query string for API tools
"""

def build_search_query(preferences: dict) -> str:

    parts = preferences.get("genres", []) + preferences.get("themes", [])
    if preferences.get("reference_books"):
        parts.append(preferences["reference_books"][0])
    return " ".join(parts[:5]) if parts else "popular fiction"