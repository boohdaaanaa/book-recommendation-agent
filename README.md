# book-recommendation-agent

# BookMatch – AI-powered book recommendation assistant

## System Description & Goal

BookMatch is an AI-powered book recommendation assistant that helps users find their next favorite book through natural language input. The system solves the problem of generic recommendations that ignore mood, themes, and personal taste — something platforms like Goodreads and Amazon fail to address well. Users simply describe what they are looking for in plain language, for example *"something like Gone Girl but darker and set in Asia"*, and the system intelligently searches, ranks, and explains matching books. The primary beneficiaries are casual readers, students, and picky readers who know how they feel but do not know what to search for. The expected outcome is a ranked list of personalized book recommendations, each with a clear AI-generated explanation of why it matches the user's request.


## AI & Agent-Based Approach

BookMatch addresses the core problem that platforms like Goodreads and Amazon fail to solve — recommending books based on mood, themes, and personal taste rather than purchase history — and its multi-agent pipeline is the architectural reason why this is possible where a simple script would fail. A basic script could never interpret a request like *"something like Gone Girl but darker and set in Asia with a strong female lead"* because it lacks semantic understanding, contextual reasoning, and the ability to coordinate multiple external tools in sequence. The AI fills this gap by acting as both the interpreter of human intent and the generator of human-readable explanations — the two capabilities that transform a search engine into a genuine recommendation assistant.

The central controller in `main.py` orchestrates the five agents sequentially, passing structured data from one stage to the next like a pipeline. It begins by calling the **InputParserAgent**, which uses the Groq LLM to convert the raw user request into a structured preference profile containing genre, mood, themes, era, author, and reference books. This profile is passed to the **SearchAgent**, which uses it to query the OpenLibrary API and Google Books API in parallel and returns a merged pool of candidate books. The **RankingAgent** then receives both the candidates and the preference profile, scoring each book using a weighted calculator tool where genre match contributes 35%, thematic similarity 30%, user ratings 20%, and era relevance 15%, returning only the top results above a minimum relevance threshold. The **ExplainerAgent** takes each top-ranked book and uses the LLM again to generate a personalized explanation of why it matches the specific user request — delivering on BookMatch's promise of recommendations with clear AI-generated reasoning. Finally the **MemoryAgent** saves the session preferences and results to a local JSON file, allowing the system to load past preferences at the start of future sessions and refine recommendations over time

## Tools used:
1. **OpenLibrary API** receives structured search parameters extracted from the user's input — such as genre, themes, author, and year filter — and returns a list of matching books with metadata including title, author, subject tags, and publication year. This tool serves as the primary book database that the SearchAgent queries to build the initial candidate pool.

2. **Google Books API** receives the same structured search parameters as a secondary source and returns additional book metadata including descriptions, cover information, and reader ratings. It is used alongside OpenLibrary to broaden the candidate pool and fill in missing details such as book descriptions that OpenLibrary may not provide.

3. **Groq API (LLM — llama-3.1-8b-instant)** receives natural language text from the user and returns structured preference data such as genre, mood, themes, era, author, and reference books that the agents can work with. It is called twice in the pipeline — first by the InputParserAgent to parse user input into structured JSON, and second by the ExplainerAgent to generate human-readable explanations for each recommended book. Groq is used because it provides a generous free tier with no daily quota issues.

4. **Weighted Scoring Calculator** is a custom Python tool that receives a list of candidate books and the user's structured preference profile and returns a ranked list of books with numerical match scores. It calculates each score using four weighted criteria: genre match 35%, theme overlap 30%, user rating 20%, and era relevance 15%. Books below a minimum score threshold of 20/100 are filtered out as irrelevant.

5. **File Reader/Writer Tool** is a custom Python tool that receives session data including user preferences and recommendations and saves them to a local JSON file under `data/user_history.json`. On subsequent runs it reads that file and returns past preference history to the MemoryAgent, allowing BookMatch to improve recommendations over time for returning users.


## Programming concepts used
**Multi-agent architecture** is the core design pattern of the system. Five specialized agents — InputParserAgent, SearchAgent, RankingAgent, ExplainerAgent, and MemoryAgent — each handle one clearly defined responsibility. The main controller passes structured data between them sequentially, ensuring modularity and separation of concerns.

**REST API integration** is used to communicate with OpenLibrary and Google Books. The `requests` library sends HTTP GET requests with query parameters and parses the JSON responses into normalized Python dictionaries that all agents can work with uniformly.

**LLM integration via Groq API** demonstrates how large language models can be called programmatically from Python. The system sends structured prompts and parses the JSON responses, using the model for natural language understanding and text generation rather than rule-based logic.

**Weighted scoring algorithm** implements a custom ranking function that combines multiple numerical signals — genre match, theme overlap, rating, and era relevance — into a single comparable score using configurable weights defined in `config.py`.

**JSON file handling** is used by the MemoryAgent to persist user preference history across sessions. The file tool reads and writes structured data using Python's built-in `json` module, implementing a simple form of cross-session memory.

**Error handling and fallback logic** ensures the system remains functional even when external APIs fail. Every API call is wrapped in try/except blocks with meaningful fallback behaviour — for example, when the Groq API is unavailable the InputParserAgent falls back to a keyword-based parser that still extracts genres, mood, themes, author, and year filter from the raw input using regex and keyword matching.

**Regular expressions** are used in the year detection and author detection functions to reliably extract structured information from free-form user input, handling patterns like "last 5 years", "published after 2020", and "by Colleen Hoover".

**Modular project structure** separates the codebase into `agents/`, `tools/`, `tests/`, and `data/` directories. Each module has a single clear purpose and can be tested, replaced, or extended independently.


## Testing Process

Testing was performed alongside implementation — each agent and tool was tested independently before being integrated into the full pipeline. Tests are written using `pytest` and cover four categories: functional correctness, API tool connectivity, error handling, and input validation.

### How to Run Tests

```bash
py -m pytest tests/ -v
```

### Test Scenarios

| Test File | Test | What It Verifies |
|---|---|---|
| `test_input_parser.py` | `test_last_5_years` | "last 5 years" maps to correct year |
| `test_input_parser.py` | `test_5_years_ago` | "5 years ago" maps to correct year |
| `test_input_parser.py` | `test_since_year` | "since 2020" maps to year 2020 |
| `test_input_parser.py` | `test_after_year` | "after 2018" maps to year 2018 |
| `test_input_parser.py` | `test_no_year_returns_none` | No year phrase returns None |
| `test_input_parser.py` | `test_by_author` | "by Colleen Hoover" extracts author |
| `test_input_parser.py` | `test_no_author_returns_none` | No author phrase returns None |
| `test_input_parser.py` | `test_romance_detected` | Genre correctly identified |
| `test_input_parser.py` | `test_sad_mood_detected` | Mood correctly identified |
| `test_input_parser.py` | `test_tragic_love_theme` | Theme correctly identified |
| `test_input_parser.py` | `test_result_has_all_keys` | Fallback returns complete profile |
| `test_input_parser.py` | `test_no_duplicates_in_query` | Search query has no duplicate terms |
| `test_googlebooks_tool.py` | `test_parse_year_full_date` | "2019-05-21" parses to 2019 |
| `test_googlebooks_tool.py` | `test_parse_year_invalid_string` | Invalid date returns None |
| `test_googlebooks_tool.py` | `test_year_filter_excludes_old_books` | API results filtered by year |
| `test_googlebooks_tool.py` | `test_author_filter_in_query` | Author filter applied to query |
| `test_openlibrary_tool.py` | `test_basic_search_returns_results` | API returns non-empty results |
| `test_openlibrary_tool.py` | `test_search_returns_correct_fields` | All required fields present |
| `test_openlibrary_tool.py` | `test_max_results_respected` | Result count does not exceed limit |
| `test_ranking_agent.py` | `test_romance_book_ranks_higher` | Relevant books score higher |
| `test_ranking_agent.py` | `test_rank_adds_match_score` | Score field added to every book |
| `test_ranking_agent.py` | `test_empty_candidates_returns_empty` | Empty input handled gracefully |
| `test_memory_agent.py` | `test_save_and_load_roundtrip` | Session saves and loads correctly |
| `test_memory_agent.py` | `test_load_respects_limit` | History limit parameter works |

### Final Testing Results
50 passed, 0 failed in ~24s


## Deployment Preparation

### Requirements

- Python 3.11 or higher
- Groq API key — free at [console.groq.com](https://console.groq.com)
- Google Books API key — free at [console.cloud.google.com](https://console.cloud.google.com)

### Setup & Run

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/bookmatch-ai.git
cd bookmatch-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Open .env and add your API keys:
# GROQ_API_KEY=your_groq_key_here
# GOOGLE_BOOKS_API_KEY=your_google_books_key_here

# 4. Run the assistant
python main.py

# 5. Run tests
py -m pytest tests/ -v
```

### Dependencies
groq
requests
python-dotenv
pytest


## Data Transformation

The system performs five data transformation steps as information flows through the agent pipeline:

**1. Natural language → structured JSON preferences** — The InputParserAgent sends the raw user input to the Groq LLM which returns a structured JSON object containing genre, mood, themes, era, author, year filter, reference books, and exclusions. If the LLM is unavailable, the keyword fallback parser performs the same transformation using regex and keyword matching.

**2. Structured preferences → search query string** — The `build_search_query` function in InputParserAgent converts the structured preference profile into a compact search string for the API tools, combining genres, themes, and reference books while removing duplicates.

**3. Raw API responses → normalized book dictionaries** — Both API tools convert the different response formats from OpenLibrary and Google Books into a common normalized schema with consistent field names (title, author, year, rating, subjects, description, source), making them interchangeable for downstream agents.

**4. Candidate books + preferences → scored and ranked list** — The RankingAgent passes the normalized book list through the weighted scoring calculator which adds a numerical `match_score` field to each book and returns them sorted by relevance, with irrelevant results filtered out.

**5. Session data → persisted JSON file** — The MemoryAgent serializes the current session's preferences and recommendations into a JSON object with a timestamp and appends it to the local history file, transforming in-memory runtime data into persistent cross-session storage.


## Deployment Strategy

The current version runs as a local command-line application, which is appropriate for a development and demonstration context. For production deployment the system could be extended in the following way: the agent pipeline would be wrapped in a **FastAPI** backend exposing a `POST /recommend` endpoint that accepts a user query and returns structured recommendations as JSON. A **React** frontend would provide a browser-based interface for entering requests and displaying recommendation cards with book descriptions and AI-generated explanations. The application could then be containerized using **Docker** for environment consistency and deployed to a cloud platform such as **Railway** or **Render**, both of which offer free tiers suitable for a project of this scale.