# agent.py
import os, requests
from typing import Optional, Dict, Any, List
from openai import OpenAI

# ---- OpenAI (GPT-4 family) ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # or "gpt-4.1"
_oai = OpenAI(api_key=OPENAI_API_KEY)

def answer_with_openai(user_text: str, *, system_text: str, history: List[Dict[str, str]] = None) -> str:
    messages = [{"role": "system", "content": system_text}]
    
    # Add conversation history if provided
    if history:
        messages.extend(history)
    
    # Add current user message
    messages.append({"role": "user", "content": user_text})
    
    resp = _oai.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=700,
    )
    return resp.choices[0].message.content.strip()

# ---- Java routes (keywords) ----
JAVA_API_BASE = os.getenv("JAVA_API_BASE", "https://sweet-stillness-production.up.railway.app/api")

ROUTE_KEYWORDS = {
    "mentions": ["mentions", "سمعة", "آراء", "وش يقولون", "الناس تقول", "براند"],
    "posts":    ["posts", "بوستات", "منشورات", "سوشيال"],
    "seo":      ["seo", "سيو", "ترتيب", "بحث", "كلمات", "باكلينك"],
}

def _java_get(path: str) -> Optional[str]:
    """
    Only return a NON-empty string on success.
    Return None on:
      - HTTP error
      - empty body
      - 'null', '[]', '{}' (common placeholders)
    """
    try:
        r = requests.get(f"{JAVA_API_BASE}{path}", timeout=20)
        r.raise_for_status()
        body = (r.text or "").strip()
        if not body:
            return None
        if body in ("null", "[]", "{}", "\"\""):
            return None
        return body
    except Exception as e:
        print(f"[route_query] Java call failed {path}: {e}")
        return None

def route_query(message: str) -> Optional[str]:
    """
    Return:
      - string (the Java response) ONLY when a keyword matched AND the call succeeded with content
      - None otherwise → caller should fall back to OpenAI
    """
    txt = (message or "").lower()
    path = None
    if any(k in txt for k in ROUTE_KEYWORDS["mentions"]):
        path = "/mentions"
    elif any(k in txt for k in ROUTE_KEYWORDS["posts"]):
        path = "/posts"
    elif any(k in txt for k in ROUTE_KEYWORDS["seo"]):
        path = "/seo"

    if not path:
        return None

    return _java_get(path)

def run_agent(user_id: str, message: str, profile, history: List[Dict[str, str]] = None) -> str:
    """
    Main agent function that routes queries and generates responses.
    """
    # Try Java routes first
    java_response = route_query(message)
    if java_response:
        return java_response
    
    # Fall back to OpenAI with context
    system_prompt = """أنت مورفو، وكيل تسويقي ذكي متخصص في تحليل بيانات المراعي. 
    أجب باللغة العربية بطريقة ودية ومهنية. ركز على التسويق والتحليل."""
    
    # Call answer_with_openai with conversation history
    return answer_with_openai(message, system_text=system_prompt, history=history)