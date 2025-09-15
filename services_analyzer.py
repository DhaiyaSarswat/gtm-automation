import praw
import gspread
import requests
import json
from oauth2client.service_account import ServiceAccountCredentials
from config_keywords import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SHEET_NAME,
    GROQ_API_KEY, GROQ_API_URL, GROQ_MODEL,
    SLACK_WEBHOOK_URL, KEYWORDS
)
from typing import Dict, Union

class ServiceManager:
    """Manages all external API interactions."""
    def __init__(self):
        self.reddit = self._init_reddit()
        self.sheets = self._init_sheets()
        self.groq = self._init_groq()
        self.slack = self._init_slack()

    def _init_reddit(self):
        return praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

    def _init_sheets(self):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SERVICE_ACCOUNT_FILE, scope)
        client = gspread.authorize(creds)
        return client.open(GOOGLE_SHEET_NAME).sheet1

    def _init_groq(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set.")
        return {"headers": {"Authorization": f"Bearer {GROQ_API_KEY}"}}

    def _init_slack(self):
        if not SLACK_WEBHOOK_URL:
            raise ValueError("SLACK_WEBHOOK_URL is not set.")
        return {"webhook": SLACK_WEBHOOK_URL}

class PostAnalyzer:
    """Analyzes a post's content using the Groq API."""
    @staticmethod
    def get_analysis(text: str, service_manager: ServiceManager) -> Union[Dict, None]:
        system_prompt = f"""
        You are an expert GTM analyst. Analyze a social media post and provide JSON:
        1. "relevance": 0.0-1.0 relevant to keywords: {', '.join(KEYWORDS)}
        2. "intent": "question", "complaint", "vendor search", "general chatter"
        3. "sentiment": "positive", "negative", "neutral"
        4. "summary": concise one-sentence summary
        5. "suggestion": short engagement suggestion
        Response must be a single valid JSON object.
        """
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze the following post:\n\nTEXT: {text}"}
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }
        try:
            response = requests.post(GROQ_API_URL, headers=service_manager.groq["headers"], json=payload)
            response.raise_for_status()
            return json.loads(response.json()['choices'][0]['message']['content'])
        except Exception as e:
            print(f"Groq inference failed: {e}")
            return None
