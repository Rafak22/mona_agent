from datetime import datetime
from .supabase_client import supabase

def fetch_posts_summary() -> str:
    """
    Fetches the latest 5 social media posts from Supabase and formats them for display.
    """
    try:
        result = supabase.table("posts") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "📱 لم يتم العثور على أي منشورات حديثة."

        posts = result.data
        summary_parts = ["📲 آخر تحليل للمنشورات الاجتماعية (Ayrshare):\n"]

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
        print(f"Error fetching posts: {e}")
        return "⚠️ عذراً، حدث خطأ أثناء جلب بيانات المنشورات الاجتماعية."