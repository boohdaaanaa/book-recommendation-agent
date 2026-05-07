from agents.input_parser import parse_user_input, build_search_query
from agents.search_agent import search_books
from agents.ranking_agent import rank_books
from agents.explainer_agent import explain_all
from agents.memory_agent import load_past_preferences, save_current_session


def display_recommendations(recommendations: list[dict], user_input: str) -> None:
    print("\n" + "=" * 60)
    print("BOOKMATCH RECOMMENDATIONS")
    print("=" * 60)
    print(f"Based on: \"{user_input}\"\n")

    for i, book in enumerate(recommendations, 1):
        print(f"{'Top 1:' if i == 1 else 'Book:'} #{i}: {book['title']}")
        print(f"   Author: {book['author']}")
        print(f"   Year:   {book.get('year', 'Unknown')}")
        print(f"   Score:  {book.get('match_score', 0)}/100")
        print(f"   Why:    {book.get('explanation', '')}")
        print()

    print("=" * 60)


def validate_input(user_input: str) -> bool:
    if not user_input or len(user_input.strip()) < 5:
        print("Please describe what you are looking for in more detail.")
        return False
    return True


def run():
    print("=" * 60)
    print("Welcome to BookMatch — AI book recommendation assistant")
    print("=" * 60)
    print("Describe the kind of book you want to read.")
    print("Example: 'something like Gone Girl but set in Asia'\n")

    user_input = input("Your request: ").strip()

    if not validate_input(user_input):
        return

    print("\nStep 1: Loading your preference history...")
    past_preferences = load_past_preferences()

    print("\nStep 2: Parsing your request with AI...")
    preferences = parse_user_input(user_input, past_preferences)
    query = build_search_query(preferences)
    print(f"  Detected: genres={preferences.get('genres')}, themes={preferences.get('themes')}, mood={preferences.get('mood')}")

    print("\nStep 3: Searching book databases...")
    candidates = search_books(query)

    if not candidates:
        print("No books found. Please try a different description.")
        return

    print("\nStep 4: Ranking candidates...")
    top_books = rank_books(candidates, preferences)

    print("\nStep 5: Generating explanations...")
    final_recommendations = explain_all(top_books, preferences, user_input)

    print("\nStep 6: Saving session...")
    save_current_session(preferences, final_recommendations)

    display_recommendations(final_recommendations, user_input)


if __name__ == "__main__":
    run()