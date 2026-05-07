import anthropic
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

""" Generate a human-readable explanation of why a book matches the user's request.

    Args:
        book: Book dictionary with title, author, subjects, score
        preferences: Structured user preferences
        user_input: Original raw user input for context

    Returns:
        Human-readable explanation string
"""

def explain_recommendation(book: dict, preferences: dict, user_input: str) -> str:
    
    prompt = f"""You are a friendly book recommendation assistant.
Explain in 2-3 sentences why this book is a great match for the user.
Be specific and reference their actual request. Be warm and conversational.

User requested: "{user_input}"
User preferences: genres={preferences.get('genres')}, themes={preferences.get('themes')}, mood={preferences.get('mood')}

Book: "{book['title']}" by {book['author']}
Subjects: {book.get('subjects', [])}
Match score: {book.get('match_score')}/100

Write only the explanation, nothing else."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

    except Exception as e:
        print(f"ExplainerAgent error: {e}")
        return f"This book matches your interest in {', '.join(preferences.get('themes', ['this genre']))}."

"""
    Add explanations to all top recommended books.

    Args:
        top_books: Ranked list of top books from RankingAgent
        preferences: Structured user preferences
        user_input: Original raw user input

    Returns:
        Books list with added explanation field
"""

def explain_all(top_books: list[dict], preferences: dict, user_input: str) -> list[dict]:

    for book in top_books:
        print(f"  Generating explanation for '{book['title']}'...")
        book["explanation"] = explain_recommendation(book, preferences, user_input)
    return top_books