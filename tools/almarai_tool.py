from tools.mentions_tool import fetch_mentions_summary
from tools.posts_tool import fetch_posts_summary
from tools.seo_tool import fetch_seo_signals_summary
from langchain.tools import tool

@tool
def almarai_tool(message: str) -> str:
    """
    Route user message to the correct Almarai-related tool based on comprehensive keyword lists.
    Returns data about Almarai's brand mentions, social media posts, or SEO performance.
    """
    message = message.lower().strip()

    # كلمات مفتاحية لل mentions
    mentions_keywords = [
        "براند", "السمعة", "ذكر", "brand mentions", "reputation", "brand24"
    ]

    # كلمات مفتاحية لل posts
    posts_keywords = [
        "منشور", "المنشورات", "السوشيال", "وسائل التواصل", "نشر", "محتوى", "ayrshare", "post", "social media"
    ]

    # كلمات مفتاحية لل seo
    seo_keywords = [
        "تحسين محركات", "seo", "تحليل الكلمات", "ترتيب", "تصدر", "البحث", "موقع", "se ranking", "keyword ranking"
    ]

    if any(kw in message for kw in mentions_keywords):
        return fetch_mentions_summary()

    elif any(kw in message for kw in posts_keywords):
        return fetch_posts_summary()

    elif any(kw in message for kw in seo_keywords):
        return fetch_seo_signals_summary()

    return "❓ لم أفهم سؤالك بدقة، هل يمكنك توضيح ما تريد عن المراعي؟ (مثلاً: المنشورات، السمعة، ترتيب الكلمات؟)"