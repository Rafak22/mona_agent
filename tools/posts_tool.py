from datetime import datetime
from .supabase_client import supabase

def fetch_posts_summary() -> str:
    """
    Fetches latest social media posts from the posts table.
    Schema:
    - content: string
    - platform: string
    - hashtags: array/string
    - reach: int
    - ctr: float
    - published_date: date
    """
    try:
        result = supabase.table("posts") \
            .select("content,platform,hashtags,reach,ctr,published_date") \
            .order("published_date", desc=True) \
            .limit(5) \
            .execute()

        if not result.data:
            return "لم يتم العثور على أي منشورات حديثة."

        posts = result.data
        summary_parts = ["📱 آخر تحليل للمنشورات على وسائل التواصل:\n"]

        platform_icons = {
            "instagram": "📸",
            "tiktok": "🎵",
            "twitter": "🐦",
            "facebook": "👥",
            "linkedin": "💼"
        }

        for post in posts:
            date = datetime.fromisoformat(post["published_date"]).strftime("%Y-%m-%d")
            platform = platform_icons.get(post["platform"].lower(), "🌐")
            hashtags = post["hashtags"] if isinstance(post["hashtags"], list) else \
                      post["hashtags"].split(",") if post["hashtags"] else []
            
            summary_parts.append(
                f"• {date} | {platform} {post['platform']}\n"
                f"  - المحتوى: {post['content'][:100]}...\n"
                f"  - الوسوم: {' '.join(['#' + tag.strip() for tag in hashtags[:3]])}...\n"
                f"  - الوصول: {post['reach']} 👀\n"
                f"  - نسبة النقر: {post['ctr']:.1f}% 🎯\n"
            )

        return "\n".join(summary_parts)

    except Exception as e:
        print(f"Error fetching posts: {e}")
        return "عذراً، حدث خطأ أثناء جلب بيانات المنشورات."