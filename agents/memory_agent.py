from tools.file_tool import save_session, get_past_preferences

"""
    Load recent user preference profiles from history.

    Returns:
        List of recent preference dictionaries
"""

def load_past_preferences() -> list[dict]:

    past = get_past_preferences(limit=3)
    if past:
        print(f"  Loaded {len(past)} past preference profiles.")
    return past

"""
    Save the current session to history file.

    Args:
        preferences: Structured preferences from this session
        recommendations: Final recommendations from this session
"""

def save_current_session(preferences: dict, recommendations: list[dict]) -> None:

    save_session(preferences, recommendations)
    print("  Session saved to history.")