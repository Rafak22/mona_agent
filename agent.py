# agent.py
import os
import requests
from typing import Optional, Dict, Any, List

# --- OpenAI (GPT-4 family) ---
from openai import OpenAI

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # or "gpt-4.1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
_oai = OpenAI(api_key=OPENAI_API_KEY)

def answer_with_openai(user_text: str, *, system_text: str) -> str:
    """Fallback LLM answer using GPT-4 family with your system prompt."""
    resp = _oai.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_text},
            {"role": "user", "content": user_text}
        ],
        temperature=0.3,
        max_tokens=700,
    )
    return resp.choices[0].message.content.strip()

# --- Java “tables” service passthrough (leave their service untouched) ---
JAVA_API_BASE = os.getenv(
    "JAVA_API_BASE",
    "https://sweet-stillness-production.up.railway.app/api"
)

ROUTE_KEYWORDS = {
    "mentions": ["mentions", "سمعة", "آراء", "وش يقولون", "الناس تقول", "براند"],
    "posts":    ["posts", "بوستات", "منشورات", "سوشيال"],
    "seo":      ["seo", "سيو", "ترتيب", "بحث", "كلمات", "باكلينك"],
}

def _java_get(path: str) -> Optional[str]:
    try:
        r = requests.get(f"{JAVA_API_BASE}{path}", timeout=20)
        r.raise_for_status()
        return r.text  # return raw text; FE will render the "reply" string
    except Exception as e:
        print(f"[route_query] Java call failed {path}: {e}")
        return None

def route_query(message: str) -> Optional[str]:
    """Route certain keywords to the Java API; return None to fall back to OpenAI."""
    txt = (message or "").lower()
    if any(k in txt for k in ROUTE_KEYWORDS["mentions"]):
        return _java_get("/mentions")
    if any(k in txt for k in ROUTE_KEYWORDS["posts"]):
        return _java_get("/posts")
    if any(k in txt for k in ROUTE_KEYWORDS["seo"]):
        return _java_get("/seo")
    return None

# --- Supabase profile helpers (for conditioning the system prompt) ---
try:
    from supabase import create_client, Client  # supabase-py v2
except Exception:
    create_client = None
    Client = None  # type: ignore

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Use SERVICE KEY on backend if possible; falls back to anon for read-only cases
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")

_sb: Optional["Client"] = None
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        _sb = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[supabase] init failed: {e}")
        _sb = None

def get_profile(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch one row from profiles by user_id."""
    if not _sb:
        return None
    res = _sb.table("profiles").select("*").eq("user_id", user_id).limit(1).execute()
    items: List[Dict[str, Any]] = getattr(res, "data", None) or res._dict_.get("data", []) or []
    return items[0] if items else None

def build_system_prompt(profile: Optional[Dict[str, Any]]) -> str:
    """Builds a compact system prompt using stored profile fields (if any)."""
    base = (
        "You are MORVO, a helpful bilingual (Arabic/English) marketing strategist. "
        "Be concise and ROI-focused. Ask ONE clarifying question only if essential."
    )
    if not profile:
        return base

    parts = []
    if profile.get("user_name"):     parts.append(f"User name: {profile['user_name']}")
    if profile.get("user_role"):     parts.append(f"Role: {profile['user_role']}")
    if profile.get("industry"):      parts.append(f"Industry: {profile['industry']}")
    if profile.get("company_size"):  parts.append(f"Company size: {profile['company_size']}")
    if profile.get("primary_goals"):
        goals = profile["primary_goals"]
        if isinstance(goals, list):
            parts.append(f"Goals: {', '.join(map(str, goals))}")
        else:
            parts.append(f"Goals: {goals}")
    if profile.get("budget_range"):  parts.append(f"Budget: {profile['budget_range']}")
    if profile.get("website_status"):parts.append(f"Website: {profile['website_status']}")
    if profile.get("website_url"):   parts.append(f"URL: {profile['website_url']}")

    return base + ("\n\n" + " • ".join(parts) if parts else "")