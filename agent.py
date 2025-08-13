 # agent.py
import os, requests, json
from typing import Optional, Dict, Any, List
from openai import OpenAI
from tools.supabase_client import supabase as _sb

# ---- OpenAI (GPT-4 family) ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # or "gpt-4.1"
_oai = OpenAI(api_key=OPENAI_API_KEY)

MORVO_SYSTEM_PROMPT = (
    "You are MORVO, an intelligent Arabic/English marketing strategist.\n"
    "Core behavior:\n"
    "1) First try to answer from three data domains: mentions (brand sentiment), posts (social content performance), and seo (search signals). If the user asks about any of these, craft a short clean summary from the data without exposing raw field names.\n"
    "2) Otherwise, answer using expert marketing knowledge with practical, ROI-focused advice.\n"
    "Tone:\n"
    "- Arabic: warm, friendly, natural. Avoid markdown symbols and quotes. Use occasional emojis like 💡📈🤝 when helpful.\n"
    "- English: confident, concise, professional.\n"
    "Formatting:\n"
    "- Output plain text only. No **bold**, quotes, or asterisks.\n"
    "- Prefer a short paragraph. Use numbered bullets only when clearly helpful and keep them succinct.\n"
    "- Make answers readable and appealing; add relevant emojis sparingly.\n"
    "- Personalize if profile info is known (role, industry, size, website, goals, budget).\n"
)

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

# ---- Routing keywords (Arabic + English synonyms) ----
ROUTE_KEYWORDS = {
    "mentions": [
        "mentions", "mention", "سمعة", "السمعة", "ذكر", "الذكر", "آراء", "تعليقات",
        "مراجعات", "وش يقولون", "الناس تقول", "حديث الناس", "البراند", "براند", "سمعة العلامة",
        "مشاعر", "sentiment"
    ],
    "posts": [
        "posts", "post", "بوست", "بوستات", "منشور", "منشورات", "سوشيال", "سوشيال ميديا",
        "تغريدات", "تويتر", "اكس", "انستقرام", "تيك توك", "يوتيوب", "reach", "engagement"
    ],
    "seo": [
        "seo", "سيو", "تحسين محركات", "تحسين محركات البحث", "بحث", "نتائج البحث", "ترتيب",
        "الترتيب", "كلمات", "كلمات مفتاحية", "باكلينك", "باك لينك", "جوجل", "google"
    ],
}

# ---- Supabase routing helpers ----
def _format_rows_for_text(table: str, rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "لا توجد بيانات متاحة حالياً."
    snippets: List[str] = []
    for row in rows:
        # Prefer common fields if present
        parts: List[str] = []
        for key in ("title", "keyword", "content", "text", "summary", "source", "platform", "sentiment"):
            if key in row and row[key]:
                val = str(row[key])
                if len(val) > 140:
                    val = val[:137] + "..."
                parts.append(val)
        # Fallback to first 3 items
        if not parts:
            for k, v in list(row.items())[:3]:
                parts.append(f"{k}: {v}")
        snippet = " — ".join(parts)
        snippets.append(snippet)
        if len(snippets) >= 5:
            break
    table_name_ar = {
        "mentions": "السمعة والذكور",
        "posts": "منشورات السوشيال",
        "seo": "إشارات SEO",
    }.get(table, table)
    return f"ملخص سريع من {table_name_ar}: " + "; ".join(snippets)

def _sb_fetch_table(table: str) -> Optional[str]:
    if not _sb:
        return None
    try:
        q = _sb.table(table).select("*")
        # try to order by created_at if present
        try:
            q = q.order("created_at", desc=True)
        except Exception:
            pass
        res = q.limit(5).execute()
        rows = res.data or []
        if not rows:
            return None
        return _format_rows_for_text(table, rows)
    except Exception as e:
        print(f"[supabase] fetch failed for {table}: {e}")
        return None

def route_query(message: str) -> Optional[str]:
    """
    Route to Supabase-backed data answers for mentions/posts/seo when keywords match.
    Returns a non-empty string on success; otherwise None so caller can fall back to OpenAI.
    """
    txt = (message or "").lower()
    table: Optional[str] = None
    if any(k in txt for k in ROUTE_KEYWORDS["mentions"]):
        table = "mentions"
    elif any(k in txt for k in ROUTE_KEYWORDS["posts"]):
        table = "posts"
    elif any(k in txt for k in ROUTE_KEYWORDS["seo"]):
        table = "seo"

    if not table:
        return None
    return _sb_fetch_table(table)

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