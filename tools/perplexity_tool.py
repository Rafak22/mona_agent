import requests
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()
PERPLEXITY_KEY = os.getenv("PERPLEXITY_API_KEY")

@tool
def fetch_perplexity_insight(query: str) -> str:
    """Fetches real-time marketing insight from Perplexity."""
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "user", "content": query}
        ],
        "temperature": 0.7
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("🛑 Perplexity fetch error:", e)
        return "⚠️ Mona had trouble fetching insights. Please try again later." 