"""
ExplainerAgent — generates human-readable explanations for each recommendation.
Uses Groq API (free, fast, no daily quota issues).
"""
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)


def explain_recommendation(book: dict, preferences: dict, user_input: str) -> str:
    """Generate a human-readable explanation of why a book matches the user's request."""
    prompt = f"""You are a friendly book recommendation assistant.
Explain in 2-3 sentences why this book matches the user's request.
Be specific and mention the mood and themes they asked for.

User requested: "{user_input}"
User mood: {preferences.get('mood')}
User themes: {preferences.get('themes')}

Book: "{book['title']}" by {book['author']}
Published: {book.get('year', 'unknown')}
Subjects: {book.get('subjects', [])}

Write only the explanation, nothing else."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  ExplainerAgent error: {e}")
        mood = preferences.get('mood', '')
        themes = ', '.join(preferences.get('themes', ['this genre']))
        return f"This book matches your interest in {themes} with a {mood} tone."


def explain_all(top_books: list[dict], preferences: dict, user_input: str) -> list[dict]:
    """Add explanations to all top recommended books."""
    for book in top_books:
        print(f"  Generating explanation for '{book['title']}'...")
        book["explanation"] = explain_recommendation(book, preferences, user_input)
    return top_books