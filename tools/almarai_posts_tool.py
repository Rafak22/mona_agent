from datetime import datetime
from .supabase_client import supabase

def fetch_posts_summary() -> str:
    """
    Fetches and summarizes the latest Almarai social media posts from Supabase.
    """
    try:
        result = supabase.table("almarai_posts") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "📱 لم يتم العثور على أي منشورات حديثة للمراعي."

        posts = result.data
        summary_parts = ["📲 آخر تحليل لمنشورات المراعي على وسائل التواصل:\n"]

        platform_icons = {
            "instagram": "📸",
            "tiktok": "🎵",
            "twitter": "🐦",
            "facebook": "👥",
            "linkedin": "💼"
        }

        for post in posts:
            date = datetime.fromisoformat(post["created_at"]).strftime("%Y-%m-%d")
            platforms = [f"{platform_icons.get(p, '🌐')} {p}" for p in post["platforms"]]
            
            summary_parts.append(
                f"• {date} | {', '.join(platforms)}\n"
                f"  - المحتوى: {post['content'][:100]}...\n"
                f"  - التفاعل: {post['engagement']} 👥\n"
                f"  - الوصول: {post['reach']} 👀\n"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        print(f"Error fetching Almarai posts: {e}")
        return "⚠️ عذراً، حدث خطأ أثناء جلب بيانات المنشورات."