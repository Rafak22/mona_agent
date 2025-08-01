from tools.perplexity_tool import fetch_perplexity_insight
from tools.almarai_mentions_tool import fetch_mentions_summary
from tools.almarai_seo_tool import fetch_seo_signals_summary
from tools.almarai_posts_tool import fetch_posts_summary
from schema import UserProfile
import re

def is_arabic(text: str) -> bool:
    """Quick check: does the string contain Arabic letters?"""
    return bool(re.search(r'[\u0600-\u06FF]', text))

def route_almarai_query(message: str) -> str | None:
    """
    Routes Almarai-related queries to the appropriate Supabase tool based on keywords.
    Returns None if no matching tool is found.
    """
    message = message.lower().strip()
    
    # Brand mentions and reputation
    if any(kw in message for kw in ["براند", "السمعة", "brand mentions", "ذكر", "سمعة", "reputation"]):
        return fetch_mentions_summary()
    
    # Social media and content
    if any(kw in message for kw in ["social", "منشور", "محتوى", "وسائل التواصل", "تفاعل", "engagement"]):
        return fetch_posts_summary()
    
    # SEO and search rankings
    if any(kw in message for kw in ["seo", "keywords", "تحسين", "ترتيب", "محركات البحث", "كلمات"]):
        return fetch_seo_signals_summary()
    
    return None

def run_agent(user_id: str, message: str, profile: UserProfile) -> str:
    """
    Simple routing logic: try Supabase tools first, then fallback to Perplexity.
    """
    # Try Supabase tools first
    almarai_reply = route_almarai_query(message)
    if almarai_reply:
        return almarai_reply

    # Fallback to Perplexity
    try:
        prompt = f"""
You are MORVO, Almarai's marketing assistant. The user asked: "{message}"

Focus on marketing insights related to:
- Brand reputation and mentions
- Social media performance
- SEO and search visibility

Keep your response short, clear, and data-focused.
"""
        return fetch_perplexity_insight.invoke(prompt)
    except Exception as e:
        print(f"Error: {e}")
        return (
            "عذراً، حدث خطأ. هل يمكنك إعادة صياغة سؤالك؟"
            if is_arabic(message) else
            "Sorry, there was an error. Could you rephrase your question?"
        )