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
    Simple routing: try Supabase tools first, then OpenAI fallback.
    """
    # Try Supabase tools first
    tool_response = route_query(message)
    if tool_response:
        return tool_response
    
    # OpenAI fallback for general questions
    try:
        # Import OpenAI here
        import openai
        import os
        
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت مورفو، وكيلة تسويق ذكية متخصصة في تحليل بيانات المراعي. أجب باللغة العربية بطريقة ودودة ومفيدة."},
                {"role": "user", "content": message}
            ],
            max_tokens=150
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI error: {e}")
        # Fallback response
        return (
            f"مرحباً! شكراً لسؤالك '{message}'. أنا مورفو، وكيلتك التسويقية الذكية. "
            "يمكنني مساعدتك في تحليل البيانات التسويقية للمراعي!"
            if is_arabic(message) else
            f"Hello! Thanks for your question '{message}'. I'm MORVO, your smart marketing agent. "
            "I can help you analyze Almarai's marketing data!"
        )