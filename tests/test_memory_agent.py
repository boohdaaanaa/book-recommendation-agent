import os
import pytest
from agents.memory_agent import save_current_session, load_past_preferences
from tools.file_tool import save_session, get_past_preferences

SAMPLE_PREFERENCES = {
    "genres": ["romance"],
    "themes": ["tragic love"],
    "mood": "sad",
    "era": "modern",
    "author": "Colleen Hoover",
    "year_from": 2019
}

SAMPLE_RECOMMENDATIONS = [
    {"title": "It Ends with Us", "author": "Colleen Hoover"},
    {"title": "Verity", "author": "Colleen Hoover"}
]


@pytest.fixture(autouse=True)
def cleanup_history():
    """Remove history file before and after each test."""
    path = "data/user_history.json"
    if os.path.exists(path):
        os.remove(path)
    yield
    if os.path.exists(path):
        os.remove(path)


def test_save_creates_file():
    """Saving a session should create the history file."""
    save_current_session(SAMPLE_PREFERENCES, SAMPLE_RECOMMENDATIONS)
    assert os.path.exists("data/user_history.json")


def test_load_returns_empty_when_no_history():
    """Loading with no history file should return empty list."""
    result = load_past_preferences()
    assert result == []


def test_save_and_load_roundtrip():
    """Saved preferences should be retrievable."""
    save_current_session(SAMPLE_PREFERENCES, SAMPLE_RECOMMENDATIONS)
    result = load_past_preferences()
    assert len(result) > 0
    assert result[0]["genres"] == ["romance"]



def test_load_past_preferences(limit: int = 3) -> list[dict]:
    """
    Load recent user preference profiles from history.

    Args:
        limit: Number of recent sessions to return

    Returns:
        List of recent preference dictionaries
    """
    past = get_past_preferences(limit=limit)
    if past:
        print(f"  Loaded {len(past)} past preference profiles.")
    return past


def save_current_session(preferences: dict, recommendations: list[dict]) -> None:
    """
    Save the current session to history file.

    Args:
        preferences: Structured preferences from this session
        recommendations: Final recommendations from this session
    """
    save_session(preferences, recommendations)
    print("  Session saved to history.")
