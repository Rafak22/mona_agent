import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
print("🔑 Testing OpenAI Key:", "set" if bool(key) else "missing")

url = "https://api.openai.com/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "user", "content": "What are effective marketing strategies for Ramadan campaigns?"}
    ],
    "temperature": 0.7
}

res = requests.post(url, headers=headers, json=payload)

print("✅ Status Code:", res.status_code)
try:
    print("🧠 Mona says:\n", res.json()["choices"][0]["message"]["content"])
except Exception:
    print("❌ Error parsing response:")
    print(res.text)