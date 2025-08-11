import requests
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

@tool
def fetch_perplexity_insight(query: str) -> str:
    """Fetches real-time marketing insight using OpenAI Chat Completions."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
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
        print("🛑 OpenAI fetch error:", e)
        return "⚠️ Mona had trouble fetching insights. Please try again later." 