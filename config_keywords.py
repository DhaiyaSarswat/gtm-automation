import os
from dotenv import load_dotenv
from typing import List

load_dotenv()

# --- Configuration ---
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", 0.5))
API_RATE_LIMIT_DELAY = int(os.getenv("API_RATE_LIMIT_DELAY", 3))

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

DESIRED_SHEET_HEADERS = [
    "Keyword", "Title", "Link", "Author", "Subreddit", "Timestamp",
    "Relevance", "Intent", "Sentiment", "Summary", "Engagement Suggestion", "Feedback"
]

# --- Keyword Loading ---
def load_keywords(filepath: str = "keywords.txt") -> List[str]:
    try:
        with open(filepath, 'r') as f:
            keywords = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        if not keywords:
            raise ValueError("Keywords file is empty or contains no valid keywords.")
        return keywords
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: Keywords file not found at '{filepath}'")

KEYWORDS = load_keywords()
