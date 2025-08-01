from tools.mentions_tool import fetch_mentions_summary
from tools.posts_tool import fetch_posts_summary
from tools.seo_tool import fetch_seo_signals_summary
from schema import UserProfile
import re

def is_arabic(text: str) -> bool:
    """Quick check: does the string contain Arabic letters?"""
    return bool(re.search(r'[\u0600-\u06FF]', text))

def route_query(message: str) -> str | None:
    """
    Routes queries to appropriate Supabase tools based on keywords.
    Returns None if no match is found.
    """
    message = message.lower().strip()

    # Brand mentions and sentiment
    mentions_keywords = [
        "وش الناس يقولون", "سمعة", "يقولون عن", "ذكر", "انطباع",
        "brand mentions", "reputation", "sentiment"
    ]
    if any(kw in message for kw in mentions_keywords):
        return fetch_mentions_summary()

    # Social media posts
    posts_keywords = [
        "بوست", "منشور", "تفاعل", "وسائل التواصل", "السوشيال",
        "post", "social media", "engagement", "content"
    ]
    if any(kw in message for kw in posts_keywords):
        return fetch_posts_summary()

    # SEO and keywords
    seo_keywords = [
        "كلمات مفتاحية", "تتصدر", "محركات البحث", "ترتيب",
        "seo", "keywords", "ranking", "search"
    ]
    if any(kw in message for kw in seo_keywords):
        return fetch_seo_signals_summary()

    return None

def run_agent(user_id: str, message: str, profile: UserProfile) -> str:
    """
    Simple routing: try Supabase tools first, Perplexity temporarily disabled.
    """
    # Try Supabase tools first
    tool_response = route_query(message)
    if tool_response:
        return tool_response

    # Perplexity temporarily disabled
    return (
        "⚠️ عذراً، لا يمكنني الإجابة على هذا السؤال حالياً. الرجاء السؤال عن:\n"
        "• ذكر العلامة التجارية والسمعة\n"
        "• المنشورات ووسائل التواصل\n"
        "• تحليلات SEO والكلمات المفتاحية"
        if is_arabic(message) else
        "⚠️ Sorry, I can only answer questions about:\n"
        "• Brand mentions and reputation\n"
        "• Social media posts and engagement\n"
        "• SEO and keyword analytics"
    )