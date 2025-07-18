import requests
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("PERPLEXITY_API_KEY")
print("🔑 Testing Key:", key)

url = "https://api.perplexity.ai/chat/completions"

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

payload = {
    "model": "sonar-pro",  # ✅ Valid model
    "messages": [
        {"role": "user", "content": "What are effective marketing strategies for Ramadan campaigns?"}
    ],
    "temperature": 0.7
}

res = requests.post(url, headers=headers, json=payload)

print("✅ Status Code:", res.status_code)
try:
    print("🧠 Mona says:\n", res.json()["choices"][0]["message"]["content"])
except Exception as e:
    print("❌ Error parsing response:")
    print(res.text) 