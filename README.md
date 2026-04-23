# book-recommendation-agent

# BookMatch – AI-powered book recommendation assistant

## System description and goal
BookMatch is an AI-powered reading assistant that helps users 
discover books based on their mood and preferences using 
natural language input.

## Agent-based approach
The system uses a multi-agent pipeline with 5 agents:
- InputParserAgent – parses user preferences
- SearchAgent – queries book APIs
- RankingAgent – scores and filters results
- ExplainerAgent – explains why each book matches
- MemoryAgent – saves user history

## Tools used:
1. OpenLibrary API – search books by genre and subject
2. Google Books API – fetch descriptions and metadata
3. Web Search Tool – retrieve reviews and ratings
4. Scoring Calculator – weighted ranking of candidates
5. File Tool - save user preference history

## Programming concepts used
- Multi-agent architecture
- REST API calls with requests library
- LLM integration via Anthropic API
- Weighted scoring algorithm
- JSON file handling
