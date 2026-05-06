import json
import os
from datetime import datetime

HISTORY_FILE = "data/user_history.json"

"""
    Save current session preferences and recommendations to history file.

    Args:
        preferences: Structured user preferences from InputParserAgent
        recommendations: Final ranked book recommendations
"""

def save_session(preferences: dict, recommendations: list[dict]) -> None:

    os.makedirs("data", exist_ok=True)

    session = {
        "timestamp": datetime.now().isoformat(),
        "preferences": preferences,
        "recommendations": [
            {"title": b["title"], "author": b["author"]} for b in recommendations
        ]
    }

    history = load_history()
    history.append(session)

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Could not save session: {e}")

"""
    Load past session history from JSON file.

    Returns:
        List of past session dictionaries, empty list if file doesn't exist
"""

def load_history() -> list[dict]:

    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return []

"""
    Retrieve the most recent user preference profiles.

    Args:
        limit: Number of recent sessions to return

    Returns:
        List of recent preference dictionaries
"""

def get_past_preferences(limit: int = 3) -> list[dict]:

    history = load_history()
    return [s["preferences"] for s in history[-limit:]]